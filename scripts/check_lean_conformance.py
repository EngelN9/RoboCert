"""Differential conformance: the Lean checker model must agree with the Python checker.

`formal/RoboCert/Soundness.lean` proves `ExactWitnessChecker.check c cert = true -> c.Semantics`.
That theorem is about `formal/RoboCert/Checker.lean`, a *model* of
`src/robocert/checkers.py::ExactWitnessChecker.check`. Nothing in the repository previously
connected the two, so the model could drift arbitrarily from the shipped code with every gate
still green -- the Lean proof would remain true and remain irrelevant. This script is that
connection.

It builds claim/certificate vectors once, runs each through the real shipped
`planar2r_exact_witness_checker` object, emits a Lean source file carrying one `#guard` per
vector asserting the Lean model returns the same Bool, and runs it through `lake env lean`.
A disagreement fails the build.

Every vector is additionally required to satisfy `Wellformed.lean`'s
`Claim.FormulaVarsQuantified`, which `exactWitness_sound` assumes: without that, a vector could
agree perfectly and still sit outside the theorem's scope.

**What this establishes, and what it does not.** Agreement on a finite vector set is
differential evidence, not a proof of equivalence (`AGENTS.md` SS66). It says nothing about
vectors outside the set, and nothing at all about the parts of the Python path the Lean model
deliberately omits: payload parsing (`checkers.py::_parse_witness`), the metadata and hash
cross-checks in `checking.py::_run_checker`, and `attestation.py::AttestedChecker`. See
`formal/README.md`, "Deliberate divergences". The well-formedness check has its own named
limit: `formula_vars_quantified` is a Python *restatement* of the Lean predicate, checked
against Python `Claim` objects, so it is evidence for `Python validator => FormulaVarsQuantified`
on the vectors -- not the Lean predicate evaluated on the Lean terms.

**A disagreement is a finding, not a bug to paper over.** `formal/AGENTS.md`, "When a model and
the implementation disagree", forbids conforming the model to Python. Report it.

`--require-lean` makes an absent toolchain a hard failure, and CI must pass it. Without it this
script reports "skipped" and exits 0 when `lake` is missing, which is exactly the false green
the `rocq` job shipped on its first run -- a passing job that means nothing.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from robocert.artifacts import digest_json
from robocert.certificates import Certificate, CertificateConclusion
from robocert.checkers import PLANAR2R_EXACT_WITNESS_FAMILY, planar2r_exact_witness_checker
from robocert.kinematics2r import build_planar2r_claim
from robocert.specification import (
    Assumption,
    BoxDomain,
    Claim,
    Formula,
    FormulaKind,
    GeometrySemantics,
    IntervalDomain,
    Margin,
    MonomialPower,
    Polynomial,
    Predicate,
    ProvenanceEntry,
    QuantifierBlock,
    QuantifierKind,
    Rational,
    Relation,
    Term,
    UncertaintySemantics,
    Unit,
    Variable,
)
from robocert.witness_search2r import instance_from_witness

REPO_ROOT = Path(__file__).resolve().parent.parent
FORMAL_DIR = REPO_ROOT / "formal"

# Python enum member -> Lean constructor. Written out rather than derived from the StrEnum
# values, so that renaming either side is a visible edit here instead of a silent mismatch.
# `Unit` is qualified because Lean core has its own `Unit`, which `open RoboCert` does not hide.
_UNIT = {
    Unit.DIMENSIONLESS: "RoboCert.Unit.dimensionless",
    Unit.METRE: "RoboCert.Unit.metre",
    Unit.SQUARE_METRE: "RoboCert.Unit.squareMetre",
    Unit.RADIAN: "RoboCert.Unit.radian",
    Unit.SECOND: "RoboCert.Unit.second",
}
_QUANTIFIER = {
    QuantifierKind.FORALL: "QuantifierKind.forAll",
    QuantifierKind.EXISTS: "QuantifierKind.exists_",
}
_RELATION = {
    Relation.EQ: "Relation.eq",
    Relation.GT: "Relation.gt",
    Relation.GE: "Relation.ge",
    Relation.LT: "Relation.lt",
    Relation.LE: "Relation.le",
}
_UNCERTAINTY = {
    UncertaintySemantics.NONE: "UncertaintySemantics.none",
    UncertaintySemantics.ADJUSTABLE: "UncertaintySemantics.adjustable",
    UncertaintySemantics.STATIC_ROBUST: "UncertaintySemantics.staticRobust",
    UncertaintySemantics.POLICY: "UncertaintySemantics.policy",
}
_GEOMETRY = {
    GeometrySemantics.EXACT: "GeometrySemantics.exact",
    GeometrySemantics.OUTER_CONSERVATIVE: "GeometrySemantics.outerConservative",
    GeometrySemantics.INNER_CONSERVATIVE: "GeometrySemantics.innerConservative",
    GeometrySemantics.NON_CERTIFIED_APPROXIMATION: "GeometrySemantics.nonCertifiedApproximation",
}
_CONCLUSION = {
    CertificateConclusion.FEASIBLE: "Conclusion.feasible",
    CertificateConclusion.INFEASIBLE: "Conclusion.infeasible",
}


# --------------------------------------------------------------------------------------
# Emitter
#
# Every claim is emitted on ONE line. Lean's structure-instance parser is whitespace
# sensitive and rejects a nested `{ ... }` broken across lines at this indentation; a
# generated file has no reason to be pretty, and one line per definition keeps the `#guard`
# line numbers in the compiler's diagnostics mapping cleanly back to a vector.
# --------------------------------------------------------------------------------------


def lean_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lean_rational(value: Rational) -> str:
    """`mkRat` takes an `Int` and a `Nat`; a negative numerator needs its own parentheses."""
    numerator = f"({value.numerator})" if value.numerator < 0 else str(value.numerator)
    return f"(mkRat {numerator} {value.denominator})"


def lean_list(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def lean_variable(variable: Variable) -> str:
    return (
        f"{{ variableId := {lean_string(variable.variable_id)}, unit := {_UNIT[variable.unit]} }}"
    )


def lean_interval(interval: IntervalDomain) -> str:
    return (
        f"{{ domainId := {lean_string(interval.domain_id)}, "
        f"variableId := {lean_string(interval.variable_id)}, "
        f"lower := {lean_rational(interval.lower)}, "
        f"upper := {lean_rational(interval.upper)}, "
        f"unit := {_UNIT[interval.unit]}, "
        f"lowerClosed := {str(interval.lower_closed).lower()}, "
        f"upperClosed := {str(interval.upper_closed).lower()} }}"
    )


def lean_box(domain: BoxDomain) -> str:
    components = lean_list([lean_interval(item) for item in domain.components])
    return f"{{ domainId := {lean_string(domain.domain_id)}, components := {components} }}"


def lean_block(block: QuantifierBlock) -> str:
    variables = lean_list([lean_string(item) for item in block.variable_ids])
    return (
        f"{{ kind := {_QUANTIFIER[block.kind]}, variableIds := {variables}, "
        f"domainId := {lean_string(block.domain_id)} }}"
    )


def lean_power(power: MonomialPower) -> str:
    return f"{{ variableId := {lean_string(power.variable_id)}, exponent := {power.exponent} }}"


def lean_term(term: Term) -> str:
    powers = lean_list([lean_power(item) for item in term.powers])
    return f"{{ coefficient := {lean_rational(term.coefficient)}, powers := {powers} }}"


def lean_polynomial(polynomial: Polynomial) -> str:
    return "{ terms := " + lean_list([lean_term(item) for item in polynomial.terms]) + " }"


def lean_predicate(predicate: Predicate) -> str:
    return (
        f"{{ predicateId := {lean_string(predicate.predicate_id)}, "
        f"left := {lean_polynomial(predicate.left)}, "
        f"relation := {_RELATION[predicate.relation]}, "
        f"right := {lean_polynomial(predicate.right)} }}"
    )


def lean_formula(formula: Formula) -> str:
    """Python's one-element `not` operand list becomes Lean's single `Formula` (divergence 1)."""
    if formula.kind is FormulaKind.PREDICATE:
        assert formula.predicate_id is not None
        return f"(Formula.pred {lean_string(formula.predicate_id)})"
    operands = [lean_formula(item) for item in formula.operands]
    if formula.kind is FormulaKind.NOT:
        return f"(Formula.not {operands[0]})"
    constructor = "Formula.and" if formula.kind is FormulaKind.AND else "Formula.or"
    return f"({constructor} {lean_list(operands)})"


def lean_assumption(assumption: Assumption) -> str:
    return (
        f"{{ assumptionId := {lean_string(assumption.assumption_id)}, "
        f"statement := {lean_string(assumption.statement)}, "
        f"category := {lean_string(assumption.category)} }}"
    )


def lean_margin(margin: Margin) -> str:
    return (
        f"{{ marginId := {lean_string(margin.margin_id)}, "
        f"metric := {lean_string(margin.metric)}, "
        f"relation := {_RELATION[margin.relation]}, "
        f"bound := {lean_rational(margin.bound)}, "
        f"unit := {_UNIT[margin.unit]} }}"
    )


def lean_provenance(entry: ProvenanceEntry) -> str:
    return (
        f"{{ sourceId := {lean_string(entry.source_id)}, "
        f"artifactHash := {lean_string(str(entry.artifact_hash))}, "
        f"description := {lean_string(entry.description)} }}"
    )


def lean_claim(claim: Claim) -> str:
    return (
        "{ claimId := " + lean_string(claim.claim_id) + ", "
        "variables := " + lean_list([lean_variable(item) for item in claim.variables]) + ", "
        "domains := " + lean_list([lean_box(item) for item in claim.domains]) + ", "
        "quantifiers := " + lean_list([lean_block(item) for item in claim.quantifiers]) + ", "
        "predicates := " + lean_list([lean_predicate(item) for item in claim.predicates]) + ", "
        "formula := " + lean_formula(claim.formula) + ", "
        "assumptions := " + lean_list([lean_assumption(item) for item in claim.assumptions]) + ", "
        "margins := " + lean_list([lean_margin(item) for item in claim.margins]) + ", "
        "uncertaintySemantics := " + _UNCERTAINTY[claim.uncertainty_semantics] + ", "
        "geometrySemantics := " + _GEOMETRY[claim.geometry_semantics] + ", "
        "provenance := " + lean_list([lean_provenance(item) for item in claim.provenance]) + " }"
    )


def lean_env(witness: dict[str, Rational]) -> str:
    """Chain `Env.extend` in sorted key order so the emitted file is deterministic."""
    expression = "Env.empty"
    for name in sorted(witness):
        expression = f"({expression}.extend {lean_string(name)} {lean_rational(witness[name])})"
    return expression


# --------------------------------------------------------------------------------------
# Vectors
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Vector:
    """One shared input, with the verdict the real Python checker gave it."""

    name: str
    claim: Claim
    certificate: Certificate
    witness: dict[str, Rational]
    python_accepted: bool


_MODEL_HASH = digest_json({"model": "lean-conformance-vectors"})


def formula_vars_quantified(claim: Claim) -> tuple[bool, list[str]]:
    """Python restatement of `Wellformed.lean::Claim.FormulaVarsQuantified`.

    `exactWitness_sound` takes that predicate as a hypothesis `hwf`, so for a claim not
    satisfying it the soundness theorem says nothing at all. A vector that violated it would
    still be checked for Bool agreement and would still look like conformance, while sitting
    outside the theorem's scope entirely -- so the vector set has to be shown to stay inside it.

    Every unresolvable reference is resolved the way the Lean predicate resolves it, not the
    way Python's validator would: `Formula.Mentions` is `False` for an id `findPredicate`
    misses, so an unknown predicate mentions nothing; `BoundBy` requires `findDomain` to
    succeed, so a block naming an unknown domain binds nothing. Mirroring those choices is the
    point -- a restatement that "helpfully" raised on a missing id would be a different
    predicate.

    Returns the verdict and the variables the formula mentions but no quantifier block binds.
    """
    predicates = {item.predicate_id: item for item in claim.predicates}
    mentioned: set[str] = set()
    for predicate_id in claim.formula.predicate_ids:
        predicate = predicates.get(predicate_id)
        if predicate is not None:
            mentioned |= predicate.variable_ids

    domains = {item.domain_id: item for item in claim.domains}
    bound: set[str] = set()
    for block in claim.quantifiers:
        domain = domains.get(block.domain_id)
        if domain is not None:
            bound |= {component.variable_id for component in domain.components}

    unbound = sorted(mentioned - bound)
    return not unbound, unbound


def _certificate(
    claim: Claim,
    witness: dict[str, Rational],
    conclusion: CertificateConclusion = CertificateConclusion.FEASIBLE,
) -> Certificate:
    return Certificate(
        certificate_id="conformance-vector",
        family=PLANAR2R_EXACT_WITNESS_FAMILY,
        conclusion=conclusion,
        claim_hash=claim.digest(),
        model_hash=_MODEL_HASH,
        assumption_ids=tuple(item.assumption_id for item in claim.assumptions),
        checker_id=planar2r_exact_witness_checker.checker_id,
        checker_version=planar2r_exact_witness_checker.checker_version,
        arithmetic_mode=planar2r_exact_witness_checker.arithmetic_mode,
        payload={
            "witness": {name: value.to_dict() for name, value in witness.items()},
        },
        provenance=claim.provenance,
    )


def _scalar_claim(
    *,
    claim_id: str,
    interval: IntervalDomain,
    predicates: tuple[Predicate, ...],
    formula: Formula,
    kind: QuantifierKind = QuantifierKind.EXISTS,
) -> Claim:
    """A one-variable claim over one interval. Keeps the boundary vectors readable."""
    return Claim(
        claim_id=claim_id,
        variables=(Variable(interval.variable_id, unit=interval.unit),),
        domains=(BoxDomain(interval.domain_id + ".box", components=(interval,)),),
        quantifiers=(QuantifierBlock(kind, (interval.variable_id,), interval.domain_id + ".box"),),
        predicates=predicates,
        formula=formula,
        assumptions=(),
        margins=(),
        uncertainty_semantics=UncertaintySemantics.NONE,
        geometry_semantics=GeometrySemantics.EXACT,
        provenance=(),
    )


def _identity_predicate(predicate_id: str, variable_id: str, bound: Rational, relation: Relation):
    """`variable <relation> bound`, as a Predicate."""
    return Predicate(
        predicate_id=predicate_id,
        left=Polynomial(terms=(Term(Rational(1), powers=(MonomialPower(variable_id, 1),)),)),
        relation=relation,
        right=Polynomial(terms=(Term(bound, powers=()),)) if bound.numerator else Polynomial.zero(),
    )


def _boundary_vectors() -> list[tuple[str, Claim, dict[str, Rational]]]:
    """Witness sitting exactly on an interval endpoint, across all four boundary flags.

    This is where `IntervalDomain.memBool` (Lean) and `checkers.py:135-136` (Python) are most
    likely to drift: the Python form is `value > lower or (lower_closed and value == lower)`,
    the Lean form is `if lowerClosed then lower <= v else lower < v`. Equal by case analysis,
    but written differently enough that a future edit to either could break the equality.
    """
    built: list[tuple[str, Claim, dict[str, Rational]]] = []
    always_true = Predicate(
        predicate_id="trivially_true",
        left=Polynomial.zero(),
        relation=Relation.GE,
        right=Polynomial.zero(),
    )
    for endpoint in ("lower", "upper"):
        for closed in (True, False):
            interval = IntervalDomain(
                domain_id="B",
                variable_id="v",
                lower=Rational(-1),
                upper=Rational(1),
                lower_closed=closed if endpoint == "lower" else True,
                upper_closed=closed if endpoint == "upper" else True,
            )
            claim = _scalar_claim(
                claim_id=f"conformance.boundary.{endpoint}.{'closed' if closed else 'open'}",
                interval=interval,
                predicates=(always_true,),
                formula=Formula.predicate("trivially_true"),
            )
            value = interval.lower if endpoint == "lower" else interval.upper
            label = "closed" if closed else "open"
            built.append((f"boundary_{endpoint}_{label}", claim, {"v": value}))
    return built


def build_vectors() -> list[Vector]:
    """Every shared input, paired with the verdict the shipped Python checker gives it.

    Rejections carry as much weight here as acceptances: a conformance set that only exercises
    the accepting path would agree with a Lean model that returned `true` unconditionally.
    """
    raw: list[tuple[str, Claim, dict[str, Rational], CertificateConclusion]] = []

    def add(
        name: str,
        claim: Claim,
        witness: dict[str, Rational],
        conclusion: CertificateConclusion = CertificateConclusion.FEASIBLE,
    ) -> None:
        raw.append((name, claim, witness, conclusion))

    # 1-4. The flagship worked instance, L1=L2=5, t1=1/2, t2=-1/3 -- the same one
    # tests/test_checkers.py and formal/attestations/planar2r-exact-witness.json use.
    instance = instance_from_witness(Fraction(5), Fraction(5), Fraction(1, 2), Fraction(-1, 3))
    planar = build_planar2r_claim(
        l1=instance.l1,
        l2=instance.l2,
        x=instance.x,
        y=instance.y,
        epsilon=Fraction(10),
        obstacle_center=(Fraction(1000), Fraction(1000)),
        obstacle_radius=Fraction(1),
        clearance_margin=Fraction(1),
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )
    good = {"t1": Rational(1, 2), "t2": Rational(-1, 3)}
    add("planar2r_worked_instance", planar, good)
    add("planar2r_infeasible_conclusion", planar, good, CertificateConclusion.INFEASIBLE)
    add("planar2r_witness_outside_box", planar, {"t1": Rational(2), "t2": Rational(-1, 3)})
    add("planar2r_witness_in_box_formula_false", planar, {"t1": Rational(0), "t2": Rational(0)})
    add("planar2r_witness_missing_binding", planar, {"t1": Rational(1, 2)})
    add(
        "planar2r_witness_extra_binding",
        planar,
        {"t1": Rational(1, 2), "t2": Rational(-1, 3), "unused": Rational(7)},
    )

    # 5. A FORALL block. Both sides must reject: the guard added after the 2026-08-17 audit
    # (RC-002) exists because a single witness point cannot discharge a universal.
    theta = IntervalDomain(
        domain_id="Theta",
        variable_id="theta",
        lower=Rational(9, 10),
        upper=Rational(11, 10),
        unit=Unit.METRE,
    )
    forall_claim = _scalar_claim(
        claim_id="conformance.forall.block",
        interval=theta,
        predicates=(_identity_predicate("positive_theta", "theta", Rational(0), Relation.GT),),
        formula=Formula.predicate("positive_theta"),
        kind=QuantifierKind.FORALL,
    )
    add("forall_block_rejected", forall_claim, {"theta": Rational(1)})

    # 6-9. Interval boundary behaviour across all four open/closed combinations.
    for name, claim, witness in _boundary_vectors():
        add(name, claim, witness)

    # 10. Two existential blocks, exercising prefix iteration order.
    a_axis = IntervalDomain(domain_id="A.a", variable_id="a", lower=Rational(0), upper=Rational(2))
    b_axis = IntervalDomain(domain_id="B.b", variable_id="b", lower=Rational(0), upper=Rational(2))
    sum_predicate = Predicate(
        predicate_id="sum_exceeds",
        left=Polynomial(
            terms=(
                Term(Rational(1), powers=(MonomialPower("a", 1),)),
                Term(Rational(1), powers=(MonomialPower("b", 1),)),
            )
        ),
        relation=Relation.GT,
        right=Polynomial(terms=(Term(Rational(1), powers=()),)),
    )
    two_block = Claim(
        claim_id="conformance.two.blocks",
        variables=(Variable("a"), Variable("b")),
        domains=(BoxDomain("A", components=(a_axis,)), BoxDomain("B", components=(b_axis,))),
        quantifiers=(
            QuantifierBlock(QuantifierKind.EXISTS, ("a",), "A"),
            QuantifierBlock(QuantifierKind.EXISTS, ("b",), "B"),
        ),
        predicates=(sum_predicate,),
        formula=Formula.predicate("sum_exceeds"),
        assumptions=(Assumption("rigid", "Rigid-body model", "model"),),
        margins=(Margin("clearance", "distance", Relation.GE, Rational(1, 1000), Unit.METRE),),
        uncertainty_semantics=UncertaintySemantics.ADJUSTABLE,
        geometry_semantics=GeometrySemantics.OUTER_CONSERVATIVE,
        provenance=(
            ProvenanceEntry("vector-source", digest_json({"source": "conformance"}), "Vector set"),
        ),
    )
    add("two_blocks_satisfied", two_block, {"a": Rational(1), "b": Rational(1)})
    add("two_blocks_unsatisfied", two_block, {"a": Rational(0), "b": Rational(0)})

    # 11-13. Connective shapes: nested negation, a disjunction whose first operand is false
    # (Lean's `decideAny` recurses where Python's `any()` short-circuits), and a failing
    # conjunction.
    low = _identity_predicate("v_small", "v", Rational(-2), Relation.LT)
    high = _identity_predicate("v_large", "v", Rational(0), Relation.GT)
    axis = IntervalDomain(domain_id="V", variable_id="v", lower=Rational(-1), upper=Rational(1))
    small = Formula.predicate("v_small")
    large = Formula.predicate("v_large")
    for label, formula, value in (
        ("nested_not", Formula.negate(Formula.negate(large)), Rational(1, 2)),
        ("or_first_operand_false", Formula.any(small, large), Rational(1, 2)),
        ("and_with_false_operand", Formula.all(small, large), Rational(1, 2)),
        ("not_of_true", Formula.negate(large), Rational(1, 2)),
    ):
        claim = _scalar_claim(
            claim_id=f"conformance.connective.{label}",
            interval=axis,
            predicates=(low, high),
            formula=formula,
        )
        add(label, claim, {"v": value})

    # 14. Exponents above one, a negative coefficient and a large denominator, exercising
    # Lean's hand-written `ratPow` against Python's `**` on Fractions.
    cubic = Predicate(
        predicate_id="cubic_bound",
        left=Polynomial(
            terms=(
                Term(Rational(-3, 7), powers=(MonomialPower("v", 3),)),
                Term(Rational(1234567, 999983), powers=(MonomialPower("v", 1),)),
            )
        ),
        # The bound is TIGHT between exponents 3 and 2 at v = -5/9: the cubic value is
        # -1041667940/1700971083 ~ -0.6124 and the quadratic one -154629110/188996787 ~
        # -0.8182, so `>= -7/10` accepts the first and rejects the second. Chosen that way on
        # purpose -- a slack bound would make the vector agree whatever `ratPow` did, which is
        # a check that does not perform the check it is named for.
        relation=Relation.GE,
        right=Polynomial(terms=(Term(Rational(-7, 10), powers=()),)),
    )
    cubic_claim = _scalar_claim(
        claim_id="conformance.exponents",
        interval=axis,
        predicates=(cubic,),
        formula=Formula.predicate("cubic_bound"),
    )
    add("high_exponent_arithmetic", cubic_claim, {"v": Rational(-5, 9)})

    vectors: list[Vector] = []
    for name, claim, witness, conclusion in raw:
        satisfied, unbound = formula_vars_quantified(claim)
        if not satisfied:
            # Not an assertion: `python -O` would drop it, and this is the guard that keeps the
            # vector set inside the scope of the theorem the whole harness exists to connect.
            raise ValueError(
                f"vector {name!r} does not satisfy Wellformed.lean's FormulaVarsQuantified "
                f"(unbound in the formula: {unbound}). `exactWitness_sound` assumes it, so "
                "agreement on this vector would say nothing about the soundness theorem."
            )
        certificate = _certificate(claim, witness, conclusion)
        decision = planar2r_exact_witness_checker.check(claim, certificate)
        vectors.append(Vector(name, claim, certificate, witness, decision.accepted))
    return vectors


# --------------------------------------------------------------------------------------
# Running Lean
# --------------------------------------------------------------------------------------

_HEADER = """\
-- GENERATED by scripts/check_lean_conformance.py. Not committed; regenerate, never edit.
--
-- One `#guard` per conformance vector. Each asserts that the Lean checker MODEL returns the
-- same Bool the shipped Python checker returned for the same claim and certificate.
import RoboCert.Checker
open RoboCert
"""


def emit_lean_source(vectors: list[Vector]) -> tuple[str, dict[int, str]]:
    """Return the Lean source and a map from `#guard` line number to vector name."""
    lines = _HEADER.splitlines()
    guard_lines: dict[int, str] = {}
    for index, vector in enumerate(vectors):
        lines.append("")
        lines.append(f"-- vector: {vector.name}")
        lines.append(f"def claim{index} : Claim := {lean_claim(vector.claim)}")
        lines.append(f"def witness{index} : Env := {lean_env(vector.witness)}")
        expected = "true" if vector.python_accepted else "false"
        conclusion = _CONCLUSION[vector.certificate.conclusion]
        guard_lines[len(lines) + 1] = vector.name
        lines.append(
            f"#guard ExactWitnessChecker.check claim{index} "
            f"{{ conclusion := {conclusion}, witness := witness{index} }} == {expected}"
        )
    return "\n".join(lines) + "\n", guard_lines


_LEAN_DIAGNOSTIC = re.compile(r"^.*?:(\d+):\d+: (error|warning): ", re.MULTILINE)


def run_lean(source: str, guard_lines: dict[int, str]) -> list[str]:
    """Elaborate the generated file; return one diagnostic per disagreeing vector."""
    with tempfile.TemporaryDirectory(prefix="robocert-conformance-") as directory:
        path = Path(directory) / "Conformance.lean"
        path.write_text(source, encoding="utf-8")
        completed = subprocess.run(
            ["lake", "env", "lean", str(path)],
            cwd=FORMAL_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    output = completed.stdout + completed.stderr
    if completed.returncode == 0:
        return []

    failures: list[str] = []
    for match in _LEAN_DIAGNOSTIC.finditer(output):
        if match.group(2) != "error":
            continue
        line = int(match.group(1))
        name = guard_lines.get(line)
        if name is None:
            continue
        failures.append(
            f"vector {name!r}: the Lean model DISAGREES with the Python checker. "
            "Per formal/AGENTS.md, do not conform the model to Python -- report the "
            "disagreement and record it in formal/README.md."
        )
    if not failures:
        failures.append(
            "the generated Lean file did not elaborate, and no failure mapped to a vector. "
            f"This is an emitter or toolchain defect, not a conformance result:\n{output}"
        )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-lean",
        action="store_true",
        help=(
            "Fail if the Lean toolchain is absent. CI must pass this: without it a missing "
            "toolchain produces a green run that checked nothing."
        ),
    )
    parser.add_argument(
        "--emit-only",
        metavar="PATH",
        help="Write the generated Lean source here and exit, without running it.",
    )
    args = parser.parse_args(argv)

    vectors = build_vectors()
    source, guard_lines = emit_lean_source(vectors)
    accepted = sum(1 for item in vectors if item.python_accepted)
    print(
        f"check_lean_conformance: {len(vectors)} vectors "
        f"({accepted} accepted, {len(vectors) - accepted} rejected by the Python checker)"
    )

    if args.emit_only:
        Path(args.emit_only).write_text(source, encoding="utf-8")
        print(f"check_lean_conformance: wrote {args.emit_only}")
        return 0

    if shutil.which("lake") is None:
        if args.require_lean:
            print(
                "check_lean_conformance: `lake` was REQUIRED here but is not on PATH. Refusing "
                "to report conformance for a model that was never elaborated.",
                file=sys.stderr,
            )
            return 1
        print(
            "check_lean_conformance: `lake` UNAVAILABLE on this machine -- reported, not "
            "treated as a pass. Install the pinned toolchain with elan; see formal/README.md."
        )
        return 0

    failures = run_lean(source, guard_lines)
    if failures:
        for failure in failures:
            print(f"check_lean_conformance: {failure}", file=sys.stderr)
        return 1

    for vector in vectors:
        verdict = "accept" if vector.python_accepted else "reject"
        print(f"check_lean_conformance: {vector.name}: both agree ({verdict})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
