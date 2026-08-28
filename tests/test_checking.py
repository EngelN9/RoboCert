from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace

import pytest

from robocert import checking
from robocert.artifacts import ArtifactDigest, digest_json
from robocert.certificates import Certificate, CertificateConclusion
from robocert.checking import CheckedCertificate, CheckerDecision, verify_certificate
from robocert.results import ResultStatus, certified_result, unknown_from_check
from robocert.specification import Claim, ValidationError


class FixtureChecker:
    checker_id = "fixture-checker"
    checker_version = "1.0.0"
    certificate_family = "fixture.exact"
    arithmetic_mode = "exact-rational"

    def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
        del claim
        accepted = (
            certificate.payload.get("proof") == "fixture-ok"
            and certificate.conclusion is CertificateConclusion.FEASIBLE
        )
        return CheckerDecision(accepted, () if accepted else ("fixture proof rejected",))


class ExplodingChecker(FixtureChecker):
    def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
        del claim, certificate
        raise TimeoutError("simulated timeout")


def test_accepted_checker_is_only_certified_promotion_path(
    monkeypatch: pytest.MonkeyPatch,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    make_certificate: Callable[..., Certificate],
) -> None:
    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {"fixture.exact": FixtureChecker()},
    )
    report = verify_certificate(sample_claim, model_hash, make_certificate())

    assert report.accepted is True
    assert report.checked_certificate is not None
    result = certified_result(report.checked_certificate)
    assert result.status is ResultStatus.CERTIFIED_FEASIBLE
    assert result.claim_hash == sample_claim.digest()


def test_checked_certificate_cannot_be_constructed_directly(
    make_certificate: Callable[..., Certificate],
) -> None:
    with pytest.raises(TypeError):
        CheckedCertificate(make_certificate())  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("claim_hash", digest_json({"wrong": "claim"})),
        ("model_hash", digest_json({"wrong": "model"})),
        ("assumption_ids", ("different-assumption",)),
        ("family", "different.family"),
        ("conclusion", CertificateConclusion.INFEASIBLE),
        ("checker_id", "different-checker"),
        ("checker_version", "9.9.9"),
        ("arithmetic_mode", "floating-point"),
        ("payload", {"proof": "corrupted"}),
        ("provenance", ()),
    ],
)
def test_corrupted_certificate_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    replacement: object,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    make_certificate: Callable[..., Certificate],
) -> None:
    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {"fixture.exact": FixtureChecker()},
    )
    certificate = replace(make_certificate(), **{field: replacement})
    report = verify_certificate(sample_claim, model_hash, certificate)

    assert report.accepted is False
    assert report.checked_certificate is None
    assert unknown_from_check(report).status is ResultStatus.UNKNOWN


def test_checker_exception_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    make_certificate: Callable[..., Certificate],
) -> None:
    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {"fixture.exact": ExplodingChecker()},
    )
    report = verify_certificate(sample_claim, model_hash, make_certificate())

    assert report.accepted is False
    assert report.checked_certificate is None
    assert any("TimeoutError" in diagnostic for diagnostic in report.diagnostics)


def test_expected_model_digest_must_be_valid(
    monkeypatch: pytest.MonkeyPatch,
    sample_claim: Claim,
    make_certificate: Callable[..., Certificate],
) -> None:
    with pytest.raises(ValueError):
        ArtifactDigest("sha256:not-a-digest")

    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {"fixture.exact": FixtureChecker()},
    )
    report = verify_certificate(
        sample_claim,
        digest_json({"model": "different"}),
        make_certificate(),
    )
    assert report.accepted is False


def test_phase_zero_has_no_production_checker(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
    make_certificate: Callable[..., Certificate],
) -> None:
    report = verify_certificate(sample_claim, model_hash, make_certificate())
    assert report.accepted is False
    assert report.checked_certificate is None
    assert report.diagnostics == ("no production checker is registered for family 'fixture.exact'",)


def test_unrefereed_planar2r_family_is_not_registered() -> None:
    assert "planar2r.exact_witness" not in checking._PRODUCTION_CHECKERS


def test_production_checker_registry_is_read_only() -> None:
    with pytest.raises(TypeError):
        checking._PRODUCTION_CHECKERS["fixture.exact"] = FixtureChecker()  # type: ignore[index]


def test_certificate_payload_is_deeply_immutable(
    make_certificate: Callable[..., Certificate],
) -> None:
    certificate = make_certificate(payload={"nested": {"value": 1}})
    nested = certificate.payload["nested"]
    assert isinstance(nested, Mapping)
    with pytest.raises(TypeError):
        nested["value"] = 2  # type: ignore[index]


def test_certificate_payload_rejects_floating_point(
    make_certificate: Callable[..., Certificate],
) -> None:
    with pytest.raises(ValidationError, match="floating-point"):
        make_certificate(payload={"bound": 0.5})
