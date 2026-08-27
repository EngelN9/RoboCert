from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import pytest

from robocert import checking
from robocert.artifacts import ArtifactDigest, digest_json
from robocert.certificates import Certificate, CertificateConclusion
from robocert.checkers import PLANAR2R_EXACT_WITNESS_FAMILY, planar2r_exact_witness_checker
from robocert.checking import verify_certificate
from robocert.kinematics2r import build_planar2r_claim
from robocert.results import ResultStatus, certified_result, unknown_from_check
from robocert.specification import (
    BoxDomain,
    Claim,
    Formula,
    GeometrySemantics,
    IntervalDomain,
    MonomialPower,
    Polynomial,
    Predicate,
    QuantifierBlock,
    QuantifierKind,
    Rational,
    Relation,
    Term,
    UncertaintySemantics,
    Unit,
    Variable,
)
from robocert.witness_search2r import instance_from_witness, witness_payload


@pytest.fixture(autouse=True)
def _enable_research_checker_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Audit checker semantics without granting production registration."""

    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {PLANAR2R_EXACT_WITNESS_FAMILY: planar2r_exact_witness_checker},
    )


# L1=L2=5, t1=1/2, t2=-1/3 -> tool (39/5, 27/5), |det J| = 15 (worked instance).
_INSTANCE = instance_from_witness(Fraction(5), Fraction(5), Fraction(1, 2), Fraction(-1, 3))

# Far from the arm's reach (max 10), so these checker-focused tests don't need to
# reason about obstacle geometry (that's covered in tests/test_kinematics2r.py).
_FAR_OBSTACLE = {
    "obstacle_center": (Fraction(1000), Fraction(1000)),
    "obstacle_radius": Fraction(1),
    "clearance_margin": Fraction(1),
}


def _claim() -> Claim:
    return build_planar2r_claim(
        l1=_INSTANCE.l1,
        l2=_INSTANCE.l2,
        x=_INSTANCE.x,
        y=_INSTANCE.y,
        epsilon=Fraction(10),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )


def _model_hash() -> ArtifactDigest:
    return digest_json({"model": "planar2r-test-fixture"})


def _certificate(claim: Claim, model_hash: ArtifactDigest, **overrides: object) -> Certificate:
    values: dict[str, object] = {
        "certificate_id": "planar2r-worked-instance",
        "family": PLANAR2R_EXACT_WITNESS_FAMILY,
        "conclusion": CertificateConclusion.FEASIBLE,
        "claim_hash": claim.digest(),
        "model_hash": model_hash,
        "assumption_ids": tuple(item.assumption_id for item in claim.assumptions),
        "checker_id": "robocert.planar2r_exact_witness",
        "checker_version": "0.1.0",
        "arithmetic_mode": "exact-rational",
        "payload": witness_payload(_INSTANCE.t1, _INSTANCE.t2),
        "provenance": claim.provenance,
    }
    values.update(overrides)
    return Certificate(**values)  # type: ignore[arg-type]


def test_positive_witness_is_certified_feasible() -> None:
    claim = _claim()
    model_hash = _model_hash()
    report = verify_certificate(claim, model_hash, _certificate(claim, model_hash))

    assert report.accepted is True
    assert report.checked_certificate is not None
    result = certified_result(report.checked_certificate)
    assert result.status is ResultStatus.CERTIFIED_FEASIBLE
    assert result.claim_hash == claim.digest()


def test_fk_violation_is_rejected() -> None:
    claim = _claim()
    model_hash = _model_hash()
    bad_payload = witness_payload(_INSTANCE.t1 + Fraction(1, 1000), _INSTANCE.t2)
    report = verify_certificate(
        claim, model_hash, _certificate(claim, model_hash, payload=bad_payload)
    )

    assert report.accepted is False
    assert any("does not satisfy" in d for d in report.diagnostics)


@pytest.mark.parametrize("bound", ["lower", "upper"])
def test_joint_limit_boundary_is_accepted(bound: str) -> None:
    # t1 in [-1, 1] is a closed interval; the witness sitting exactly at either
    # inclusive endpoint must still be accepted (AGENTS.md SS46 boundary analysis).
    boundary_t1 = Fraction(-1) if bound == "lower" else Fraction(1)
    # t2 = 1/3 (not 0) keeps the arm away from its singularity (t2=0 => det J=0).
    instance = instance_from_witness(Fraction(5), Fraction(5), boundary_t1, Fraction(1, 3))
    claim = build_planar2r_claim(
        l1=instance.l1,
        l2=instance.l2,
        x=instance.x,
        y=instance.y,
        epsilon=Fraction(1, 1000),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )
    model_hash = _model_hash()
    payload = witness_payload(instance.t1, instance.t2)
    report = verify_certificate(claim, model_hash, _certificate(claim, model_hash, payload=payload))
    assert report.accepted is True


def test_joint_limit_violation_is_rejected() -> None:
    claim = _claim()  # t1 domain is [-1, 1]
    model_hash = _model_hash()
    payload = witness_payload(Fraction(2), _INSTANCE.t2)  # outside domain
    report = verify_certificate(claim, model_hash, _certificate(claim, model_hash, payload=payload))
    assert report.accepted is False
    assert any("outside its domain" in d for d in report.diagnostics)


def test_singularity_margin_violation_is_rejected() -> None:
    # True |det J| for this witness is |L1*L2*sin(q2)| = 25*(3/5) = 15.
    # epsilon=20 sits in the SATISFIABLE regime -- proof P2 Corollary 5.4 gives
    # {t2 : G(t2) >= 0} nonempty iff epsilon <= |L1*L2| = 25 -- so the margin
    # constraint is genuinely achievable by some configuration, just not by this
    # witness. That makes the rejection meaningful rather than vacuous; the
    # vacuous regime is now refused at build time -- see
    # test_margin_above_feasibility_threshold_is_refused_at_build_time.
    claim = build_planar2r_claim(
        l1=_INSTANCE.l1,
        l2=_INSTANCE.l2,
        x=_INSTANCE.x,
        y=_INSTANCE.y,
        epsilon=Fraction(20),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )
    model_hash = _model_hash()
    report = verify_certificate(claim, model_hash, _certificate(claim, model_hash))
    assert report.accepted is False
    assert any("does not satisfy" in d for d in report.diagnostics)


def test_infeasible_conclusion_is_rejected() -> None:
    claim = _claim()
    model_hash = _model_hash()
    certificate = _certificate(claim, model_hash, conclusion=CertificateConclusion.INFEASIBLE)
    report = verify_certificate(claim, model_hash, certificate)
    assert report.accepted is False
    assert any("only conclude 'feasible'" in d for d in report.diagnostics)


def test_malformed_payload_missing_witness_key_is_rejected() -> None:
    claim = _claim()
    model_hash = _model_hash()
    report = verify_certificate(
        claim, model_hash, _certificate(claim, model_hash, payload={"not_a_witness": 1})
    )
    assert report.accepted is False
    assert any("witness" in d for d in report.diagnostics)


def test_malformed_payload_non_canonical_rational_is_rejected() -> None:
    claim = _claim()
    model_hash = _model_hash()
    bad_payload = {
        "witness": {
            "t1": {"numerator": 2, "denominator": 4},
            "t2": {"numerator": 0, "denominator": 1},
        }
    }
    report = verify_certificate(
        claim, model_hash, _certificate(claim, model_hash, payload=bad_payload)
    )
    assert report.accepted is False


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("claim_hash", digest_json({"wrong": "claim"})),
        ("model_hash", digest_json({"wrong": "model"})),
        ("assumption_ids", ("different-assumption",)),
        ("family", "different.family"),
        ("checker_id", "different-checker"),
        ("checker_version", "9.9.9"),
        ("arithmetic_mode", "floating-point"),
        ("provenance", ()),
    ],
)
def test_corrupted_certificate_field_is_rejected(field: str, replacement: object) -> None:
    claim = _claim()
    model_hash = _model_hash()
    certificate = replace(_certificate(claim, model_hash), **{field: replacement})
    report = verify_certificate(claim, model_hash, certificate)

    assert report.accepted is False
    assert report.checked_certificate is None
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


def test_forall_quantifier_is_rejected_not_silently_ignored() -> None:
    """Regression: the checker used to filter non-EXISTS quantifier blocks out and
    evaluate the formula at the single witness anyway, which accepts a claim that
    is false almost everywhere in the FORALL block. Reconstructs the auditor's
    counterexample: `forall u in [-10, 10]: u >= 0` is false, and the witness u=3
    must not be able to certify it."""
    u = Variable("u", unit=Unit.DIMENSIONLESS)
    axis = IntervalDomain(
        "U.u", "u", lower=Rational(-10), upper=Rational(10), unit=Unit.DIMENSIONLESS
    )
    predicate = Predicate(
        "u_nonnegative",
        left=Polynomial((Term(Rational(1), (MonomialPower("u", 1),)),)),
        relation=Relation.GE,
        right=Polynomial.zero(),
    )
    false_claim = Claim(
        claim_id="adversarial.forall.probe",
        variables=(u,),
        domains=(BoxDomain("U", components=(axis,)),),
        quantifiers=(QuantifierBlock(QuantifierKind.FORALL, ("u",), "U"),),
        predicates=(predicate,),
        formula=Formula.predicate("u_nonnegative"),
        assumptions=(),
        margins=(),
        uncertainty_semantics=UncertaintySemantics.NONE,
        geometry_semantics=GeometrySemantics.EXACT,
        provenance=(),
    )
    model_hash = _model_hash()
    certificate = Certificate(
        certificate_id="forall-probe",
        family=PLANAR2R_EXACT_WITNESS_FAMILY,
        conclusion=CertificateConclusion.FEASIBLE,
        claim_hash=false_claim.digest(),
        model_hash=model_hash,
        assumption_ids=(),
        checker_id="robocert.planar2r_exact_witness",
        checker_version="0.1.0",
        arithmetic_mode="exact-rational",
        payload={"witness": {"u": {"numerator": 3, "denominator": 1}}},
        provenance=(),
    )
    report = verify_certificate(false_claim, model_hash, certificate)
    assert report.accepted is False
    assert any("existential" in d for d in report.diagnostics)


def test_margin_above_feasibility_threshold_is_refused_at_build_time() -> None:
    """Proof P2 Corollary 5.4: epsilon > |L1*L2| makes the claim unsatisfiable for
    every target and obstacle. Refuse it rather than emit a silently vacuous claim."""
    with pytest.raises(ValueError, match=r"Corollary 5\.4"):
        build_planar2r_claim(
            l1=Fraction(5),
            l2=Fraction(5),  # |L1*L2| = 25
            x=_INSTANCE.x,
            y=_INSTANCE.y,
            epsilon=Fraction(1000),
            **_FAR_OBSTACLE,
            t1_bounds=(Fraction(-1), Fraction(1)),
            t2_bounds=(Fraction(-1), Fraction(1)),
        )


def test_checker_never_raises_past_the_gate() -> None:
    claim = _claim()
    model_hash = _model_hash()
    # A witness value of the wrong shape entirely (not even a rational-shaped
    # object) must fail closed, not raise past verify_certificate.
    bad_payload = {"witness": {"t1": "not-a-rational", "t2": {"numerator": 0, "denominator": 1}}}
    report = verify_certificate(
        claim, model_hash, _certificate(claim, model_hash, payload=bad_payload)
    )
    assert report.accepted is False
    assert report.checked_certificate is None
