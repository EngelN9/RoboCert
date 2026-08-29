"""Attestation gate: valid, corrupted, mismatched, failed, and unavailable proofs.

Follows the house pattern of `tests/test_checking.py` and `tests/test_checkers.py`:
parametrized single-field corruption, an autouse fixture installing the research checker
without granting it production registration, and identity asserts (`is False`, `is None`).
The claim/certificate fixture is `tests/test_checkers.py`'s worked planar-2R instance,
reused as-is (module-level `_claim`/`_certificate`/`_model_hash`) because it is the one claim
in the test suite the exact-witness family actually accepts -- the shared `sample_claim`
conftest fixture carries a FORALL block that family always rejects (checkers.py:113).

The property under test throughout is that attestations TIGHTEN. They can veto an
acceptance; they can never create one.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from robocert import checking
from robocert.artifacts import ArtifactDigest, digest_json
from robocert.attestation import (
    ATTESTATION_FORMAT,
    ATTESTATION_KEY,
    AttestationPolicy,
    AttestedChecker,
    attestation_block,
    attestation_entry,
)
from robocert.certificates import Certificate, CertificateConclusion
from robocert.checkers import (
    PLANAR2R_ATTESTATION_POLICY,
    PLANAR2R_EXACT_WITNESS_FAMILY,
    planar2r_attested_witness_checker,
)
from robocert.checking import CheckerDecision, verify_certificate
from robocert.errors import ValidationError
from robocert.kinematics2r import build_planar2r_claim
from robocert.results import ResultStatus, unknown_from_check
from robocert.specification import Claim
from robocert.witness_search2r import instance_from_witness, witness_payload

_ZERO_DIGEST = "sha256:" + "0" * 64
_ONE_DIGEST = "sha256:" + "1" * 64

_AXIOMS: Mapping[str, tuple[str, ...]] = {
    "lean4": ("propext", "Classical.choice", "Quot.sound"),
    "rocq": (),
    "isabelle": (),
}

# Same worked instance as tests/test_checkers.py: L1=L2=5, t1=1/2, t2=-1/3.
_INSTANCE = instance_from_witness(Fraction(5), Fraction(5), Fraction(1, 2), Fraction(-1, 3))

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
    return digest_json({"model": "attestation-test-fixture"})


def _certificate(claim: Claim, model_hash: ArtifactDigest, **overrides: object) -> Certificate:
    values: dict[str, object] = {
        "certificate_id": "planar2r-attested-instance",
        "family": PLANAR2R_EXACT_WITNESS_FAMILY,
        "conclusion": CertificateConclusion.FEASIBLE,
        "claim_hash": claim.digest(),
        "model_hash": model_hash,
        "assumption_ids": tuple(item.assumption_id for item in claim.assumptions),
        "checker_id": planar2r_attested_witness_checker.checker_id,
        "checker_version": planar2r_attested_witness_checker.checker_version,
        "arithmetic_mode": "exact-rational",
        "payload": witness_payload(_INSTANCE.t1, _INSTANCE.t2),
        "provenance": claim.provenance,
    }
    values.update(overrides)
    return Certificate(**values)  # type: ignore[arg-type]


@pytest.fixture(autouse=True)
def _enable_attested_research_checker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Audit the attested checker without granting production registration."""
    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {PLANAR2R_EXACT_WITNESS_FAMILY: planar2r_attested_witness_checker},
    )


@pytest.fixture
def sample_claim() -> Claim:
    return _claim()


@pytest.fixture
def model_hash() -> ArtifactDigest:
    return _model_hash()


def _entries(
    claim_hash: str,
    model_hash: str,
    *,
    systems: tuple[str, ...] = ("lean4", "rocq", "isabelle"),
    **overrides: Any,
) -> list[dict[str, object]]:
    built: list[dict[str, object]] = []
    for system in systems:
        entry = attestation_entry(
            system=system,
            toolchain=f"{system} pinned",
            claim_hash=claim_hash,
            model_hash=model_hash,
            checker_id=planar2r_attested_witness_checker.checker_id,
            checker_version=planar2r_attested_witness_checker.checker_version,
            statement_digest=_ZERO_DIGEST,
            artifact_digest=_ONE_DIGEST,
            axioms=_AXIOMS[system],
            kernel_accepted=True,
        )
        entry.update(overrides)
        built.append(entry)
    return built


@pytest.fixture
def attested_certificate(sample_claim: Claim, model_hash: ArtifactDigest) -> Certificate:
    """A certificate whose witness satisfies the claim AND carries complete attestations."""
    claim_hash = str(sample_claim.digest())
    base = _certificate(sample_claim, model_hash)
    payload = dict(base.payload)
    payload[ATTESTATION_KEY] = attestation_block(_entries(claim_hash, str(model_hash)))
    return replace(base, payload=payload)


def _with_attestations(certificate: Certificate, block: object) -> Certificate:
    payload = dict(certificate.payload)
    payload[ATTESTATION_KEY] = block
    return replace(certificate, payload=payload)


# --------------------------------------------------------------------------------------
# The tightening property. This is the whole point of the design.
# --------------------------------------------------------------------------------------


class _RejectingChecker:
    checker_id = "rejecting"
    checker_version = "1.0.0"
    certificate_family = "fixture.exact"
    arithmetic_mode = "exact-rational"

    def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
        del claim, certificate
        return CheckerDecision(False, ("inner checker says no",))


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    payload_block=st.recursive(
        st.none() | st.booleans() | st.integers() | st.text(max_size=8),
        lambda children: (
            st.lists(children, max_size=3)
            | st.dictionaries(st.text(max_size=6), children, max_size=3)
        ),
        max_leaves=8,
    )
)
def test_attestations_can_never_turn_a_rejection_into_an_acceptance(
    payload_block: object,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
) -> None:
    """For ANY attestation payload, an inner rejection stays a rejection.

    `AttestedChecker.check` is `inner.accepted and not violations`, so this is structural --
    but a property test is what makes it stay structural under future edits.
    """
    attested = AttestedChecker(
        _RejectingChecker(), PLANAR2R_ATTESTATION_POLICY, id_suffix=".attested"
    )
    certificate = _with_attestations(_certificate(sample_claim, model_hash), payload_block)
    decision = attested.check(sample_claim, certificate)
    assert decision.accepted is False


def test_attested_checker_identity_differs_from_the_bare_checker() -> None:
    """A certificate built for the bare checker must not be replayable against the attested
    one; `checking._run_checker` compares `checker_id` exactly."""
    from robocert.checkers import planar2r_exact_witness_checker

    assert planar2r_attested_witness_checker.checker_id != (
        planar2r_exact_witness_checker.checker_id
    )
    assert planar2r_attested_witness_checker.checker_id.endswith(".attested")


# --------------------------------------------------------------------------------------
# 1. Valid
# --------------------------------------------------------------------------------------


def test_complete_attestations_do_not_block_acceptance(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    report = verify_certificate(sample_claim, model_hash, attested_certificate)

    assert report.diagnostics == ()
    assert report.accepted is True
    assert report.checked_certificate is not None


def test_policy_reports_no_violations_for_a_complete_block(
    attested_certificate: Certificate,
) -> None:
    assert PLANAR2R_ATTESTATION_POLICY.violations(attested_certificate) == ()


# --------------------------------------------------------------------------------------
# 2. Corrupted
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("label", "block"),
    [
        ("not-an-object", ["lean4"]),
        ("missing-entries", {"format": ATTESTATION_FORMAT}),
        ("extra-block-field", {"format": ATTESTATION_FORMAT, "entries": [], "extra": 1}),
        ("unknown-format", {"format": "robocert.attestation/999", "entries": []}),
        ("entries-not-array", {"format": ATTESTATION_FORMAT, "entries": {"a": 1}}),
        ("entry-not-object", {"format": ATTESTATION_FORMAT, "entries": ["lean4"]}),
    ],
)
def test_corrupted_attestation_block_is_rejected(
    label: str,
    block: object,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    del label
    certificate = _with_attestations(attested_certificate, block)
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert report.checked_certificate is None
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


@pytest.mark.parametrize(
    "field",
    ["system", "toolchain", "statement_digest", "artifact_digest", "axioms", "kernel_accepted"],
)
def test_entry_with_a_missing_field_is_rejected(
    field: str,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    entries = _entries(str(sample_claim.digest()), str(model_hash))
    del entries[0][field]
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert report.checked_certificate is None


@pytest.mark.parametrize("digest_field", ["statement_digest", "artifact_digest"])
def test_malformed_digest_is_rejected(
    digest_field: str,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    entries = _entries(str(sample_claim.digest()), str(model_hash), **{digest_field: "sha256:xyz"})
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert any(digest_field in diagnostic for diagnostic in report.diagnostics)


def test_float_in_an_attestation_is_refused_at_construction(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """Exact-rational semantics: the float ban applies inside attestations too."""
    entries = _entries(str(sample_claim.digest()), str(model_hash))
    entries[0]["toolchain"] = 4.33
    with pytest.raises(ValidationError, match="floating-point"):
        _with_attestations(attested_certificate, attestation_block(entries))


def test_duplicate_system_entries_are_rejected(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    entries = _entries(str(sample_claim.digest()), str(model_hash))
    entries.append(dict(entries[0]))
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert any("duplicate" in diagnostic for diagnostic in report.diagnostics)


def test_unrecognised_proof_system_is_rejected_not_ignored(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """An unknown system has an unknown axiom base; silently ignoring it would be a hole."""
    entries = _entries(str(sample_claim.digest()), str(model_hash))
    entries.append({**entries[0], "system": "some-unreviewed-prover"})
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert any("unrecognised proof system" in diagnostic for diagnostic in report.diagnostics)


# --------------------------------------------------------------------------------------
# 3. Mismatched
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("claim_hash", str(digest_json({"wrong": "claim"}))),
        ("model_hash", str(digest_json({"wrong": "model"}))),
        ("checker_id", "robocert.some_other_checker"),
        ("checker_version", "9.9.9"),
    ],
)
def test_attestation_bound_to_a_different_artifact_is_rejected(
    field: str,
    replacement: str,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """An attestation cannot be moved between claims, models, or checker versions."""
    entries = _entries(str(sample_claim.digest()), str(model_hash))
    entries[0][field] = replacement
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert report.checked_certificate is None
    assert any(field in diagnostic for diagnostic in report.diagnostics)
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


# --------------------------------------------------------------------------------------
# 4. Failed
# --------------------------------------------------------------------------------------


def test_kernel_rejection_vetoes(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    entries = _entries(str(sample_claim.digest()), str(model_hash), kernel_accepted=False)
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert any("did not check" in diagnostic for diagnostic in report.diagnostics)
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


@pytest.mark.parametrize("placeholder", ["sorryAx", "admitted", "sorry", "Skip_axiom"])
def test_placeholder_axiom_vetoes(
    placeholder: str,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """An admitted or incomplete proof must not attest, whatever the assistant calls it."""
    entries = _entries(str(sample_claim.digest()), str(model_hash))
    entries[0]["axioms"] = [*_AXIOMS["lean4"], placeholder]
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert any("allow-list" in diagnostic for diagnostic in report.diagnostics)


def test_non_boolean_kernel_accepted_is_rejected(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """`1` is truthy but is not a kernel verdict."""
    entries = _entries(str(sample_claim.digest()), str(model_hash), kernel_accepted=1)
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False


# --------------------------------------------------------------------------------------
# 5. Unavailable
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("absent", ["lean4", "rocq", "isabelle"])
def test_missing_required_system_is_unavailable_and_vetoes(
    absent: str,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """Unavailable proof checking must yield UNKNOWN, never acceptance."""
    present = tuple(s for s in ("lean4", "rocq", "isabelle") if s != absent)
    entries = _entries(str(sample_claim.digest()), str(model_hash), systems=present)
    certificate = _with_attestations(attested_certificate, attestation_block(entries))
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert report.checked_certificate is None
    assert any(absent in diagnostic for diagnostic in report.diagnostics)
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


def test_absent_attestation_block_vetoes(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
) -> None:
    """A certificate that predates the attestation requirement does not get grandfathered."""
    certificate = _certificate(sample_claim, model_hash)
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert any(ATTESTATION_KEY in diagnostic for diagnostic in report.diagnostics)
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


# --------------------------------------------------------------------------------------
# Policy construction
# --------------------------------------------------------------------------------------


def test_policy_rejects_a_required_system_with_no_axiom_allow_list() -> None:
    with pytest.raises(ValidationError, match="no declared axiom allow-list"):
        AttestationPolicy(required_systems=("lean4",), allowed_axioms={})


def test_policy_rejects_duplicate_required_systems() -> None:
    with pytest.raises(ValidationError, match="unique"):
        AttestationPolicy(
            required_systems=("lean4", "lean4"),
            allowed_axioms={"lean4": frozenset()},
        )


def test_policy_rejects_an_empty_requirement_set() -> None:
    with pytest.raises(ValidationError, match="at least one proof system"):
        AttestationPolicy(required_systems=(), allowed_axioms={})


def test_committed_attestation_record_matches_real_policy_and_is_honestly_incomplete() -> None:
    """Load formal/attestations/planar2r-exact-witness.json and feed its `attestations`
    block through the REAL PLANAR2R_ATTESTATION_POLICY, not a re-description of it.

    This is the permanent form of the manual check run when the record was authored: the
    record's own comment claims that verify_certificate() rejects it because rocq and
    isabelle are unattested. That claim must not silently go stale -- if a future edit to
    the record or the policy makes them agree by accident (e.g. someone adds a rocq entry
    without actually running Rocq), this test is what catches it.
    """
    record_path = (
        Path(__file__).resolve().parent.parent
        / "formal"
        / "attestations"
        / "planar2r-exact-witness.json"
    )
    record = json.loads(record_path.read_text(encoding="utf-8"))
    meta = record["certificate"]

    certificate = Certificate(
        certificate_id=meta["certificate_id"],
        family=meta["family"],
        conclusion=CertificateConclusion.FEASIBLE,
        claim_hash=ArtifactDigest.from_json(meta["claim_hash"]),
        model_hash=ArtifactDigest.from_json(meta["model_hash"]),
        assumption_ids=(),
        checker_id=meta["checker_id"],
        checker_version=meta["checker_version"],
        arithmetic_mode="exact-rational",
        payload={"attestations": record["attestations"]},
        provenance=(),
    )

    violations = PLANAR2R_ATTESTATION_POLICY.violations(certificate)

    assert any("rocq" in v for v in violations)
    assert any("isabelle" in v for v in violations)
    assert not any("lean4" in v for v in violations)


def test_conclusion_still_constrains_the_inner_checker(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    attested_certificate: Certificate,
) -> None:
    """Attestations do not relax the inner family's own semantics."""
    certificate = replace(attested_certificate, conclusion=CertificateConclusion.INFEASIBLE)
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
