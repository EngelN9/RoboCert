"""Research checker implementations behind the trusted checking boundary.

Contains a generic exact-rational evaluator for Claim predicates/formulas (no
domain-specific math -- reusable by any future "exists a witness" checker family)
and a research checker for the planar-2R exact-witness family built by
`robocert.kinematics2r`. No checker in this module is currently registered for
production; tests install the research checker explicitly when auditing it.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction

from robocert.certificates import Certificate, CertificateConclusion
from robocert.checking import CheckerDecision
from robocert.errors import ValidationError
from robocert.specification import (
    Claim,
    Formula,
    FormulaKind,
    Polynomial,
    QuantifierKind,
    Rational,
    Relation,
)

_RELATION_OPS: Mapping[Relation, object] = {
    Relation.EQ: lambda a, b: a == b,
    Relation.GT: lambda a, b: a > b,
    Relation.GE: lambda a, b: a >= b,
    Relation.LT: lambda a, b: a < b,
    Relation.LE: lambda a, b: a <= b,
}


def _to_fraction(value: Rational) -> Fraction:
    return Fraction(value.numerator, value.denominator)


def evaluate_polynomial(polynomial: Polynomial, bindings: Mapping[str, Fraction]) -> Fraction:
    """Sum of coefficient * product(variable ** exponent) over exact Fractions."""
    total = Fraction(0)
    for term in polynomial.terms:
        value = _to_fraction(term.coefficient)
        for power in term.powers:
            value *= bindings[power.variable_id] ** power.exponent
        total += value
    return total


def evaluate_predicate(claim: Claim, predicate_id: str, bindings: Mapping[str, Fraction]) -> bool:
    predicate = next(p for p in claim.predicates if p.predicate_id == predicate_id)
    left = evaluate_polynomial(predicate.left, bindings)
    right = evaluate_polynomial(predicate.right, bindings)
    return bool(_RELATION_OPS[predicate.relation](left, right))  # type: ignore[operator]


def evaluate_formula(claim: Claim, formula: Formula, bindings: Mapping[str, Fraction]) -> bool:
    if formula.kind is FormulaKind.PREDICATE:
        assert formula.predicate_id is not None
        return evaluate_predicate(claim, formula.predicate_id, bindings)
    if formula.kind is FormulaKind.AND:
        return all(evaluate_formula(claim, operand, bindings) for operand in formula.operands)
    if formula.kind is FormulaKind.OR:
        return any(evaluate_formula(claim, operand, bindings) for operand in formula.operands)
    return not evaluate_formula(claim, formula.operands[0], bindings)


def _parse_witness(payload: Mapping[str, object]) -> dict[str, Fraction]:
    witness = payload.get("witness")
    if not isinstance(witness, Mapping):
        raise ValidationError("certificate payload must contain a 'witness' object")
    parsed: dict[str, Fraction] = {}
    for variable_id, raw in witness.items():
        rational = Rational.from_dict(raw)
        parsed[variable_id] = _to_fraction(rational)
    return parsed


class ExactWitnessChecker:
    """Generic exists-witness checker: accepts iff the payload's witness lies in
    every quantified variable's declared domain and the claim's formula evaluates
    to True there, using exact Fraction arithmetic throughout. No domain-specific
    (2R, obstacle, etc.) logic lives here -- that meaning is entirely in the Claim's
    predicates, so this class is directly reusable by future exact-witness families.
    """

    def __init__(self, checker_id: str, checker_version: str, certificate_family: str) -> None:
        self.checker_id = checker_id
        self.checker_version = checker_version
        self.certificate_family = certificate_family
        self.arithmetic_mode = "exact-rational"

    def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
        if certificate.conclusion is not CertificateConclusion.FEASIBLE:
            return CheckerDecision(
                False, ("an exact-witness certificate can only conclude 'feasible'",)
            )
        try:
            witness = _parse_witness(certificate.payload)
        except ValidationError as exc:
            return CheckerDecision(False, (f"malformed witness payload: {exc}",))

        # Fail closed on any quantifier this checker cannot honour. A single
        # witness point can only ever establish an existential claim; evaluating
        # the formula at one point of a FORALL block would accept a claim that is
        # false almost everywhere in that block. Silently filtering non-EXISTS
        # blocks (rather than rejecting) is unsound the moment a claim carries
        # one, so reject rather than ignore -- the ROADMAP target theorem is
        # `forall theta, forall x, exists q`, and that must reach a checker built
        # to discharge it, not this one.
        if any(block.kind is not QuantifierKind.EXISTS for block in claim.quantifiers):
            return CheckerDecision(
                False,
                (
                    "exact-witness checker supports purely existential claims only; "
                    "this claim carries a non-existential quantifier block",
                ),
            )

        exists_blocks = [q for q in claim.quantifiers if q.kind is QuantifierKind.EXISTS]
        domains_by_id = {domain.domain_id: domain for domain in claim.domains}
        diagnostics: list[str] = []
        for block in exists_blocks:
            domain = domains_by_id[block.domain_id]
            for component in domain.components:
                value = witness.get(component.variable_id)
                if value is None:
                    diagnostics.append(f"witness is missing value for {component.variable_id!r}")
                    continue
                lower = _to_fraction(component.lower)
                upper = _to_fraction(component.upper)
                lower_ok = value > lower or (component.lower_closed and value == lower)
                upper_ok = value < upper or (component.upper_closed and value == upper)
                if not (lower_ok and upper_ok):
                    diagnostics.append(
                        f"witness value for {component.variable_id!r} is outside its domain"
                    )
        if diagnostics:
            return CheckerDecision(False, tuple(diagnostics))

        try:
            holds = evaluate_formula(claim, claim.formula, witness)
        except (KeyError, ZeroDivisionError, ArithmeticError) as exc:
            return CheckerDecision(False, (f"witness evaluation failed: {exc}",))
        if not holds:
            return CheckerDecision(False, ("witness does not satisfy the claim's formula",))
        return CheckerDecision(True)


PLANAR2R_EXACT_WITNESS_FAMILY = "planar2r.exact_witness"

planar2r_exact_witness_checker = ExactWitnessChecker(
    checker_id="robocert.planar2r_exact_witness",
    checker_version="0.1.0",
    certificate_family=PLANAR2R_EXACT_WITNESS_FAMILY,
)

# evaluate_formula / evaluate_predicate / evaluate_polynomial are deliberately
# NOT exported. A sub-formula of a claim generally carries no meaning on its own:
# for the planar-2R family, proof P2 Proposition 9.4(3) and Remark 9.5 show the
# segment-2 clearance predicate evaluates TRUE at every t1 where Sigma^(2) = 0,
# regardless of the true distance -- it is sound only inside the full conjunction,
# which supplies the forward-kinematics conjunct that rules that locus out.
# Remark 9.5 asks specifically that it never be exposed as a pruning filter, an
# independently reported clearance certificate, or a lemma quoted elsewhere.
# They remain importable by name for tests; keeping them out of __all__ marks
# them as internal rather than part of the supported surface.
__all__ = [
    "PLANAR2R_EXACT_WITNESS_FAMILY",
    "ExactWitnessChecker",
    "planar2r_exact_witness_checker",
]
