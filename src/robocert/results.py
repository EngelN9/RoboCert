"""Normative result statuses with checker-gated certified construction."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from robocert.artifacts import ArtifactDigest, JSONValue
from robocert.certificates import CertificateConclusion
from robocert.checking import CheckedCertificate, CheckReport
from robocert.errors import ValidationError
from robocert.specification import SCHEMA_VERSION


class ResultStatus(StrEnum):
    CERTIFIED_FEASIBLE = "CERTIFIED_FEASIBLE"
    CERTIFIED_INFEASIBLE = "CERTIFIED_INFEASIBLE"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    NUMERICALLY_FEASIBLE = "NUMERICALLY_FEASIBLE"
    NUMERICALLY_INFEASIBLE = "NUMERICALLY_INFEASIBLE"
    UNKNOWN = "UNKNOWN"


_RESULT_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class CertificationResult:
    status: ResultStatus
    claim_hash: ArtifactDigest
    model_hash: ArtifactDigest
    diagnostics: tuple[str, ...]
    checked_certificate: CheckedCertificate | None
    schema_version: str

    def __init__(
        self,
        *,
        status: ResultStatus,
        claim_hash: ArtifactDigest,
        model_hash: ArtifactDigest,
        diagnostics: tuple[str, ...] = (),
        checked_certificate: CheckedCertificate | None = None,
        _token: object,
    ) -> None:
        if _token is not _RESULT_TOKEN:
            raise TypeError("CertificationResult values must be created through result factories")
        if not isinstance(status, ResultStatus):
            raise ValidationError("result status must be a ResultStatus")
        if not isinstance(claim_hash, ArtifactDigest) or not isinstance(model_hash, ArtifactDigest):
            raise ValidationError("result hashes must be ArtifactDigest values")
        diagnostics = tuple(diagnostics)
        if any(not isinstance(item, str) or not item for item in diagnostics):
            raise ValidationError("result diagnostics must be non-empty strings")
        is_certified = status in (
            ResultStatus.CERTIFIED_FEASIBLE,
            ResultStatus.CERTIFIED_INFEASIBLE,
        )
        if is_certified != (checked_certificate is not None):
            raise ValidationError("only certified results may contain a checked certificate")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "claim_hash", claim_hash)
        object.__setattr__(self, "model_hash", model_hash)
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(self, "checked_certificate", checked_certificate)
        object.__setattr__(self, "schema_version", SCHEMA_VERSION)

    def to_dict(self) -> dict[str, JSONValue]:
        certificate = (
            None
            if self.checked_certificate is None
            else self.checked_certificate.certificate.to_dict()
        )
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "claim_hash": str(self.claim_hash),
            "model_hash": str(self.model_hash),
            "diagnostics": list(self.diagnostics),
            "checked_certificate": certificate,
        }


def certified_result(checked_certificate: CheckedCertificate) -> CertificationResult:
    if not isinstance(checked_certificate, CheckedCertificate):
        raise TypeError("certified_result requires a CheckedCertificate")
    certificate = checked_certificate.certificate
    status = (
        ResultStatus.CERTIFIED_FEASIBLE
        if certificate.conclusion is CertificateConclusion.FEASIBLE
        else ResultStatus.CERTIFIED_INFEASIBLE
    )
    return CertificationResult(
        status=status,
        claim_hash=certificate.claim_hash,
        model_hash=certificate.model_hash,
        checked_certificate=checked_certificate,
        _token=_RESULT_TOKEN,
    )


def unknown_result(
    claim_hash: ArtifactDigest,
    model_hash: ArtifactDigest,
    diagnostics: tuple[str, ...],
) -> CertificationResult:
    return CertificationResult(
        status=ResultStatus.UNKNOWN,
        claim_hash=claim_hash,
        model_hash=model_hash,
        diagnostics=diagnostics,
        _token=_RESULT_TOKEN,
    )


def unknown_from_check(report: CheckReport) -> CertificationResult:
    if report.accepted:
        raise ValueError("an accepted check report must be promoted with certified_result")
    return unknown_result(report.claim_hash, report.model_hash, report.diagnostics)


def numerical_result(
    status: ResultStatus,
    claim_hash: ArtifactDigest,
    model_hash: ArtifactDigest,
    diagnostics: tuple[str, ...],
) -> CertificationResult:
    if status not in (
        ResultStatus.NUMERICALLY_FEASIBLE,
        ResultStatus.NUMERICALLY_INFEASIBLE,
    ):
        raise ValueError("numerical_result accepts only numerical statuses")
    return CertificationResult(
        status=status,
        claim_hash=claim_hash,
        model_hash=model_hash,
        diagnostics=diagnostics,
        _token=_RESULT_TOKEN,
    )


__all__ = [
    "CertificationResult",
    "ResultStatus",
    "certified_result",
    "numerical_result",
    "unknown_from_check",
    "unknown_result",
]
