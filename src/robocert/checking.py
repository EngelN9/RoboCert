"""Deterministic certificate-checker boundary and fail-closed promotion gate."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol

from robocert.artifacts import ArtifactDigest
from robocert.certificates import Certificate
from robocert.errors import ValidationError
from robocert.specification import Claim


class Checker(Protocol):
    """Interface implemented by deterministic certificate checkers."""

    checker_id: str
    checker_version: str
    certificate_family: str
    arithmetic_mode: str

    def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
        """Return a deterministic decision for the serialized certificate."""
        ...


@dataclass(frozen=True, slots=True)
class CheckerDecision:
    accepted: bool
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.accepted) is not bool:
            raise ValidationError("checker decision accepted flag must be boolean")
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        if any(not isinstance(item, str) or not item for item in self.diagnostics):
            raise ValidationError("checker diagnostics must be non-empty strings")


_CHECKED_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class CheckedCertificate:
    """A certificate accepted through RoboCert's checker gate."""

    certificate: Certificate

    def __init__(self, certificate: Certificate, *, _token: object) -> None:
        if _token is not _CHECKED_TOKEN:
            raise TypeError("CheckedCertificate values can only be created by verify_certificate")
        object.__setattr__(self, "certificate", certificate)


@dataclass(frozen=True, slots=True)
class CheckReport:
    accepted: bool
    claim_hash: ArtifactDigest
    model_hash: ArtifactDigest
    diagnostics: tuple[str, ...]
    checked_certificate: CheckedCertificate | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        if not isinstance(self.claim_hash, ArtifactDigest) or not isinstance(
            self.model_hash, ArtifactDigest
        ):
            raise ValidationError("check report hashes must be ArtifactDigest values")
        if self.accepted != (self.checked_certificate is not None):
            raise ValidationError(
                "accepted check reports must contain exactly one checked certificate"
            )


# Production registration is an evidence-gated code change (see
# research/README.md and docs/architecture/trusted-computing-base.md).  Keep the
# registry empty until every research claim supporting a certificate family has
# reached E2 and its implementation correspondence has been checked.  Checker
# implementations may exist as research artifacts without being trusted here.
_PRODUCTION_CHECKERS: Mapping[str, Checker] = MappingProxyType({})


def production_checker_families() -> tuple[str, ...]:
    """Return the immutable set of evidence-approved production families."""

    return tuple(sorted(_PRODUCTION_CHECKERS))


def _rejection(
    claim_hash: ArtifactDigest,
    model_hash: ArtifactDigest,
    diagnostics: list[str] | tuple[str, ...],
) -> CheckReport:
    return CheckReport(False, claim_hash, model_hash, tuple(diagnostics), None)


def _run_checker(
    claim: Claim,
    model_hash: ArtifactDigest,
    certificate: Certificate,
    checker: Checker,
) -> CheckReport:
    claim_hash = claim.digest()
    diagnostics: list[str] = []
    try:
        checker_family = checker.certificate_family
        checker_id = checker.checker_id
        checker_version = checker.checker_version
        checker_arithmetic_mode = checker.arithmetic_mode
    except Exception as exc:
        return _rejection(
            claim_hash,
            model_hash,
            (f"checker metadata raised {type(exc).__name__}: {exc}",),
        )
    if certificate.claim_hash != claim_hash:
        diagnostics.append("certificate claim hash does not match the supplied claim")
    if certificate.model_hash != model_hash:
        diagnostics.append("certificate model hash does not match the supplied model hash")
    expected_assumptions = tuple(item.assumption_id for item in claim.assumptions)
    if certificate.assumption_ids != expected_assumptions:
        diagnostics.append("certificate assumptions do not match the supplied claim")
    if certificate.provenance != claim.provenance:
        diagnostics.append("certificate provenance does not match the supplied claim")
    if certificate.family != checker_family:
        diagnostics.append("certificate family does not match checker family")
    if certificate.checker_id != checker_id:
        diagnostics.append("certificate checker_id does not match checker identity")
    if certificate.checker_version != checker_version:
        diagnostics.append("certificate checker_version does not match checker version")
    if certificate.arithmetic_mode != checker_arithmetic_mode:
        diagnostics.append("certificate arithmetic_mode does not match checker arithmetic mode")
    if diagnostics:
        return _rejection(claim_hash, model_hash, diagnostics)

    try:
        decision = checker.check(claim, certificate)
    except Exception as exc:  # fail closed at the trusted checker boundary
        return _rejection(
            claim_hash,
            model_hash,
            (f"checker raised {type(exc).__name__}: {exc}",),
        )
    if not isinstance(decision, CheckerDecision):
        return _rejection(claim_hash, model_hash, ("checker returned an invalid decision type",))
    if not decision.accepted:
        diagnostics = list(decision.diagnostics) or ["checker rejected certificate"]
        return _rejection(claim_hash, model_hash, diagnostics)
    checked = CheckedCertificate(certificate, _token=_CHECKED_TOKEN)
    return CheckReport(True, claim_hash, model_hash, tuple(decision.diagnostics), checked)


def verify_certificate(
    claim: Claim,
    model_hash: ArtifactDigest,
    certificate: Certificate,
) -> CheckReport:
    """Verify with a library-registered production checker, failing closed if none exists."""

    checker = _PRODUCTION_CHECKERS.get(certificate.family)
    if checker is None:
        return _rejection(
            claim.digest(),
            model_hash,
            (f"no production checker is registered for family {certificate.family!r}",),
        )
    return _run_checker(claim, model_hash, certificate, checker)


__all__ = [
    "CheckReport",
    "CheckedCertificate",
    "Checker",
    "CheckerDecision",
    "production_checker_families",
    "verify_certificate",
]
