"""Exact refutation of universal claims, and every way it must refuse.

`COUNTEREXAMPLE` is the one status besides `CERTIFIED_*` that asserts a mathematical fact, so
the negative cases here matter more than the positive one. Each corresponds to a guard in
`robocert.refutation`: a prefix a point cannot refute, a point outside the domain, a
malformed assignment, and a point that simply does not violate the formula.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import pytest

from robocert.artifacts import digest_json
from robocert.errors import ValidationError
from robocert.refutation import CheckedCounterexample, refute
from robocert.results import (
    CertificationResult,
    ResultStatus,
    counterexample_result,
    unknown_from_refutation,
)
from robocert.specification import (
    BoxDomain,
    Claim,
    Formula,
    QuantifierBlock,
    QuantifierKind,
    Rational,
)

MODEL_HASH = digest_json({"model": "refutation-fixture"})


def test_a_violating_point_refutes_the_claim(make_universal_claim: Callable[..., Claim]) -> None:
    claim = make_universal_claim()
    report = refute(claim, MODEL_HASH, {"q": Rational(3, 4)})
    assert report.accepted
    assert report.diagnostics == ()
    counterexample = report.checked_counterexample
    assert counterexample is not None
    assert counterexample.assignment == (("q", Rational(3, 4)),)
    assert counterexample.claim_hash == claim.digest()
    assert counterexample.arithmetic_mode == "exact-rational"


def test_a_satisfying_point_is_not_a_counterexample(
    make_universal_claim: Callable[..., Claim],
) -> None:
    report = refute(make_universal_claim(), MODEL_HASH, {"q": Rational(1, 4)})
    assert not report.accepted
    assert report.checked_counterexample is None
    assert "not a counterexample" in report.diagnostics[0]


def test_the_boundary_point_satisfies_a_weak_inequality(
    make_universal_claim: Callable[..., Claim],
) -> None:
    """`q <= 1/2` holds AT one half. Strict versus weak must not blur (AGENTS.md SS5)."""

    assert not refute(make_universal_claim(), MODEL_HASH, {"q": Rational(1, 2)}).accepted


@pytest.mark.parametrize("kind", [QuantifierKind.EXISTS])
def test_a_non_universal_prefix_is_refused(
    kind: QuantifierKind, make_universal_claim: Callable[..., Claim]
) -> None:
    report = refute(make_universal_claim(kind=kind), MODEL_HASH, {"q": Rational(3, 4)})
    assert not report.accepted
    assert "purely universal" in report.diagnostics[0]


def test_a_point_outside_the_domain_refutes_nothing(
    make_universal_claim: Callable[..., Claim],
) -> None:
    report = refute(make_universal_claim(), MODEL_HASH, {"q": Rational(5)})
    assert not report.accepted
    assert "outside domain" in report.diagnostics[0]


def test_an_open_endpoint_excludes_its_own_value(
    make_universal_claim: Callable[..., Claim],
) -> None:
    claim = make_universal_claim(upper_closed=False)
    assert not refute(claim, MODEL_HASH, {"q": Rational(1)}).accepted
    assert refute(claim, MODEL_HASH, {"q": Rational(3, 4)}).accepted


def test_a_closed_endpoint_includes_its_own_value(
    make_universal_claim: Callable[..., Claim],
) -> None:
    assert refute(make_universal_claim(), MODEL_HASH, {"q": Rational(1)}).accepted


@pytest.mark.parametrize(
    "assignment",
    [{}, {"q": Rational(3, 4), "extra": Rational(1)}, {"wrong": Rational(3, 4)}],
)
def test_a_malformed_assignment_is_refused(
    assignment: dict[str, Rational], make_universal_claim: Callable[..., Claim]
) -> None:
    assert not refute(make_universal_claim(), MODEL_HASH, assignment).accepted


def test_inexact_values_are_refused(make_universal_claim: Callable[..., Claim]) -> None:
    report = refute(make_universal_claim(), MODEL_HASH, {"q": 0.75})  # type: ignore[dict-item]
    assert not report.accepted
    assert "exact Rational" in report.diagnostics[0]


def test_serialized_rational_objects_are_not_mistaken_for_checked_values(
    make_universal_claim: Callable[..., Claim],
) -> None:
    report = refute(
        make_universal_claim(),
        MODEL_HASH,
        {"q": {"numerator": 3, "denominator": 4}},  # type: ignore[dict-item]
    )
    assert not report.accepted
    assert "exact Rational" in report.diagnostics[0]


def test_malformed_model_hash_cannot_produce_evidence(
    make_universal_claim: Callable[..., Claim],
) -> None:
    with pytest.raises(ValidationError, match="hashes"):
        refute(
            make_universal_claim(),
            "sha256:not-a-digest",  # type: ignore[arg-type]
            {"q": Rational(3, 4)},
        )


def test_hash_validation_precedes_evidence_construction(
    make_universal_claim: Callable[..., Claim],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("evidence construction reached before hash validation")

    monkeypatch.setattr("robocert.refutation.CheckedCounterexample", forbidden)
    with pytest.raises(ValidationError):
        refute(make_universal_claim(), "bad", {"q": Rational(3, 4)})  # type: ignore[arg-type]


def test_multiple_universal_blocks_are_refuted_by_one_complete_assignment(
    make_universal_claim: Callable[..., Claim],
) -> None:
    claim = make_universal_claim(variable_ids=("q1", "q2"))
    q1, q2 = claim.domains[0].components
    claim = replace(
        claim,
        domains=(BoxDomain("Q1", (q1,)), BoxDomain("Q2", (q2,))),
        quantifiers=(
            QuantifierBlock(QuantifierKind.FORALL, ("q1",), "Q1"),
            QuantifierBlock(QuantifierKind.FORALL, ("q2",), "Q2"),
        ),
    )

    report = refute(claim, MODEL_HASH, {"q1": Rational(3, 4), "q2": Rational(0)})
    assert report.accepted


def test_refutation_evaluates_the_complete_boolean_formula(
    make_universal_claim: Callable[..., Claim],
) -> None:
    claim = make_universal_claim()
    atom = Formula.predicate("first_below_half")
    tautology = Formula.any(atom, Formula.negate(atom))
    claim = replace(claim, formula=Formula.all(tautology, atom))

    assert refute(claim, MODEL_HASH, {"q": Rational(3, 4)}).accepted
    assert not refute(claim, MODEL_HASH, {"q": Rational(1, 4)}).accepted


def test_a_checked_counterexample_cannot_be_forged(
    make_universal_claim: Callable[..., Claim],
) -> None:
    claim = make_universal_claim()
    with pytest.raises(TypeError):
        CheckedCounterexample(  # type: ignore[call-arg]
            claim_id=claim.claim_id,
            claim_hash=claim.digest(),
            model_hash=MODEL_HASH,
            assignment=(("q", Rational(3, 4)),),
            assumption_ids=(),
        )


def test_promotion_requires_a_checked_counterexample() -> None:
    with pytest.raises(TypeError):
        counterexample_result({"q": Rational(3, 4)})  # type: ignore[arg-type]


def test_a_refuted_claim_promotes_to_counterexample(
    make_universal_claim: Callable[..., Claim],
) -> None:
    claim = make_universal_claim()
    report = refute(claim, MODEL_HASH, {"q": Rational(3, 4)})
    assert report.checked_counterexample is not None

    result = counterexample_result(report.checked_counterexample)
    assert result.status is ResultStatus.COUNTEREXAMPLE
    assert result.claim_hash == claim.digest()
    assert result.model_hash == MODEL_HASH
    assert result.checked_certificate is None
    assert result.to_dict()["counterexample"] is not None


def test_a_failed_refutation_becomes_unknown_not_feasible(
    make_universal_claim: Callable[..., Claim],
) -> None:
    report = refute(make_universal_claim(), MODEL_HASH, {"q": Rational(1, 4)})
    result = unknown_from_refutation(report)
    assert result.status is ResultStatus.UNKNOWN
    assert result.checked_counterexample is None


def test_an_accepted_refutation_cannot_be_downgraded_to_unknown(
    make_universal_claim: Callable[..., Claim],
) -> None:
    report = refute(make_universal_claim(), MODEL_HASH, {"q": Rational(3, 4)})
    with pytest.raises(ValueError, match="counterexample_result"):
        unknown_from_refutation(report)


def test_other_statuses_may_not_carry_a_counterexample(
    make_universal_claim: Callable[..., Claim],
) -> None:
    """The paired invariant, from both sides."""

    report = refute(make_universal_claim(), MODEL_HASH, {"q": Rational(3, 4)})
    assert report.checked_counterexample is not None

    with pytest.raises(ValidationError, match="counterexample"):
        CertificationResult(
            status=ResultStatus.UNKNOWN,
            claim_hash=report.claim_hash,
            model_hash=report.model_hash,
            checked_counterexample=report.checked_counterexample,
            _token=_result_token(),
        )
    with pytest.raises(ValidationError, match="counterexample"):
        CertificationResult(
            status=ResultStatus.COUNTEREXAMPLE,
            claim_hash=report.claim_hash,
            model_hash=report.model_hash,
            _token=_result_token(),
        )


def _result_token() -> object:
    """Reach past the factory gate deliberately, to test the invariant underneath it."""

    from robocert import results

    return results._RESULT_TOKEN
