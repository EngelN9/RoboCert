"""Exact refutation of a universally quantified claim by a single rational point.

This is the mirror image of `checkers.ExactWitnessChecker`, and the asymmetry between them
is the reason this module needs no evidence gate.

    to establish   `exists q in Q: Phi(q)`   exhibit one q and evaluate Phi there
    to establish   `forall q in Q: Phi(q)`   reason over a continuum -- a certificate family
    to REFUTE      `forall q in Q: Phi(q)`   exhibit one q in Q and evaluate Phi there

Refuting a universal claim is therefore as elementary as establishing an existential one:
find a point of the declared domain, evaluate the claim's formula at it in exact rational
arithmetic, and observe that it is false. No relaxation, no degree bound, no research
proposition about a reduction is involved -- which is why this module does not wait on an
`E2` claim the way a production `Checker` does (`research/README.md`,
`docs/architecture/trusted-computing-base.md`). What it establishes is
`not (forall q in Q: Phi(q))` for the claim exactly as serialized, and nothing else.

Three guards carry all of the soundness, and each fails closed:

1. **Purely universal prefix.** A point refutes a `forall` block. It refutes nothing about an
   `exists` block -- for `forall x exists q: Phi(x, q)`, one failing `(x, q)` pair says only
   that this `q` was the wrong choice. Any non-`FORALL` block is rejected outright rather
   than filtered out, exactly as `ExactWitnessChecker` rejects any non-`EXISTS` block.
2. **Domain membership.** A point outside the declared domain refutes nothing, so open and
   closed endpoints are honoured exactly. `AGENTS.md` SS31 clause 1.
3. **Exact evaluation of the WHOLE formula.** Never a sub-formula, and the diagnostics never
   name which conjunct failed: proof P2 Remark 9.5 records that individual conjuncts of the
   planar-2R encoding carry no meaning in isolation and asks that they not be reported as
   standalone findings. A caller who wants to know why has the assignment and the claim, and
   can take responsibility for that reading themselves.

Where the point came from does not matter and is not recorded here. A simulator, an
optimizer, a solver, or a person may propose it; a proposal that survives these three guards
is a counterexample and one that does not is `UNKNOWN`. In particular a rounded or perturbed
proposal is simply a *different* candidate, re-checked from scratch.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction

from robocert.artifacts import ArtifactDigest, JSONValue
from robocert.checkers import evaluate_formula
from robocert.errors import ValidationError
from robocert.specification import Claim, QuantifierKind, Rational

Assignment = Mapping[str, Rational]

_COUNTEREXAMPLE_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class CheckedCounterexample:
    """A rational point shown, by `refute`, to falsify a universally quantified claim.

    Constructible only through `refute`, for the same reason `CheckedCertificate` is
    constructible only through `verify_certificate`: the type is the evidence.
    """

    claim_id: str
    claim_hash: ArtifactDigest
    model_hash: ArtifactDigest
    assignment: tuple[tuple[str, Rational], ...]
    assumption_ids: tuple[str, ...]
    arithmetic_mode: str

    def __init__(
        self,
        *,
        claim_id: str,
        claim_hash: ArtifactDigest,
        model_hash: ArtifactDigest,
        assignment: tuple[tuple[str, Rational], ...],
        assumption_ids: tuple[str, ...],
        _token: object,
    ) -> None:
        if _token is not _COUNTEREXAMPLE_TOKEN:
            raise TypeError("CheckedCounterexample values can only be created by refute")
        object.__setattr__(self, "claim_id", claim_id)
        object.__setattr__(self, "claim_hash", claim_hash)
        object.__setattr__(self, "model_hash", model_hash)
        object.__setattr__(self, "assignment", assignment)
        object.__setattr__(self, "assumption_ids", assumption_ids)
        object.__setattr__(self, "arithmetic_mode", "exact-rational")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "claim_id": self.claim_id,
            "claim_hash": str(self.claim_hash),
            "model_hash": str(self.model_hash),
            "assignment": [
                {"variable_id": variable_id, "value": value.to_dict()}
                for variable_id, value in self.assignment
            ],
            "assumption_ids": list(self.assumption_ids),
            "arithmetic_mode": self.arithmetic_mode,
        }


@dataclass(frozen=True, slots=True)
class RefutationReport:
    """Outcome of one refutation attempt. Mirrors `checking.CheckReport`."""

    accepted: bool
    claim_hash: ArtifactDigest
    model_hash: ArtifactDigest
    diagnostics: tuple[str, ...]
    checked_counterexample: CheckedCounterexample | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        if not isinstance(self.claim_hash, ArtifactDigest) or not isinstance(
            self.model_hash, ArtifactDigest
        ):
            raise ValidationError("refutation report hashes must be ArtifactDigest values")
        if self.accepted != (self.checked_counterexample is not None):
            raise ValidationError(
                "accepted refutation reports must contain exactly one checked counterexample"
            )


def _to_fraction(value: Rational) -> Fraction:
    return Fraction(value.numerator, value.denominator)


def _rejection(
    claim_hash: ArtifactDigest,
    model_hash: ArtifactDigest,
    diagnostics: tuple[str, ...],
) -> RefutationReport:
    return RefutationReport(False, claim_hash, model_hash, diagnostics, None)


def refute(claim: Claim, model_hash: ArtifactDigest, assignment: Assignment) -> RefutationReport:
    """Decide whether `assignment` falsifies `claim`, exactly and deterministically.

    Rejection never means the claim holds. It means this point did not refute it -- because
    the prefix is not purely universal, because the point lies outside the declared domain,
    or because the formula is true there. Callers map a rejection to `UNKNOWN`.
    """

    if not isinstance(model_hash, ArtifactDigest):
        raise ValidationError("refutation hashes must be ArtifactDigest values")
    claim_hash = claim.digest()

    if not isinstance(assignment, Mapping):
        return _rejection(claim_hash, model_hash, ("assignment must be a mapping",))
    if any(not isinstance(value, Rational) for value in assignment.values()):
        return _rejection(
            claim_hash, model_hash, ("assignment values must be exact Rational values",)
        )

    # Guard 1: a point refutes `forall` blocks only. Reject rather than filter -- a claim
    # carrying an `exists` block needs a procedure built to discharge it, not this one.
    if any(block.kind is not QuantifierKind.FORALL for block in claim.quantifiers):
        return _rejection(
            claim_hash,
            model_hash,
            (
                "refutation by a single point supports purely universal claims only; this "
                "claim carries a non-universal quantifier block, and one failing point "
                "does not falsify an existential subclaim",
            ),
        )

    declared = {variable.variable_id for variable in claim.variables}
    supplied = set(assignment)
    diagnostics: list[str] = []
    if missing := sorted(declared - supplied):
        diagnostics.append(f"assignment is missing values for {missing!r}")
    if extra := sorted(supplied - declared):
        diagnostics.append(f"assignment carries values for undeclared variables {extra!r}")
    if diagnostics:
        return _rejection(claim_hash, model_hash, tuple(diagnostics))

    # Guard 2: exact domain membership, strict and weak endpoints preserved (AGENTS.md SS5).
    for domain in claim.domains:
        for component in domain.components:
            value = _to_fraction(assignment[component.variable_id])
            lower = _to_fraction(component.lower)
            upper = _to_fraction(component.upper)
            lower_ok = value > lower or (component.lower_closed and value == lower)
            upper_ok = value < upper or (component.upper_closed and value == upper)
            if not (lower_ok and upper_ok):
                diagnostics.append(
                    f"point value for {component.variable_id!r} lies outside domain "
                    f"{domain.domain_id!r}, so it refutes nothing"
                )
    if diagnostics:
        return _rejection(claim_hash, model_hash, tuple(diagnostics))

    # Guard 3: evaluate the WHOLE formula exactly. Any arithmetic failure is a rejection.
    bindings = {
        variable_id: _to_fraction(value) for variable_id, value in sorted(assignment.items())
    }
    try:
        holds = evaluate_formula(claim, claim.formula, bindings)
    except Exception as exc:  # fail closed at the refutation boundary
        return _rejection(
            claim_hash, model_hash, (f"formula evaluation raised {type(exc).__name__}: {exc}",)
        )
    if holds:
        # Deliberately not reporting which conjunct did what: see the module docstring.
        return _rejection(
            claim_hash,
            model_hash,
            ("the point satisfies the claim's formula, so it is not a counterexample",),
        )

    counterexample = CheckedCounterexample(
        claim_id=claim.claim_id,
        claim_hash=claim_hash,
        model_hash=model_hash,
        assignment=tuple((key, assignment[key]) for key in sorted(assignment)),
        assumption_ids=tuple(item.assumption_id for item in claim.assumptions),
        _token=_COUNTEREXAMPLE_TOKEN,
    )
    return RefutationReport(True, claim_hash, model_hash, (), counterexample)


__all__ = [
    "Assignment",
    "CheckedCounterexample",
    "RefutationReport",
    "refute",
]
