"""Serialized candidate certificates bound to exact claims and models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, cast

from robocert.artifacts import ArtifactDigest, JSONValue, canonical_json_bytes
from robocert.errors import ValidationError
from robocert.specification import SCHEMA_VERSION, ProvenanceEntry


class CertificateConclusion(StrEnum):
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _freeze_json(value: JSONValue) -> JSONValue:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, Sequence) and not isinstance(value, str):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: JSONValue) -> JSONValue:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_thaw_json(item) for item in value]
    return value


def _expect_object(value: object, required: tuple[str, ...], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise ValidationError(f"{label} must be a JSON object")
    if set(value) != set(required):
        raise ValidationError(f"{label} fields do not match the versioned contract")
    return cast(Mapping[str, Any], value)


def _expect_array(value: object, label: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValidationError(f"{label} must be a JSON array")
    return cast(Sequence[object], value)


@dataclass(frozen=True, slots=True)
class Certificate:
    """A candidate proof artifact. Construction does not imply acceptance."""

    certificate_id: str
    family: str
    conclusion: CertificateConclusion
    claim_hash: ArtifactDigest
    model_hash: ArtifactDigest
    assumption_ids: tuple[str, ...]
    checker_id: str
    checker_version: str
    arithmetic_mode: str
    payload: Mapping[str, JSONValue]
    provenance: tuple[ProvenanceEntry, ...]
    schema_version: str = field(default=SCHEMA_VERSION, kw_only=True)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValidationError(
                f"unsupported certificate schema version: {self.schema_version!r}"
            )
        for value, label in (
            (self.certificate_id, "certificate_id"),
            (self.family, "certificate family"),
            (self.checker_id, "checker_id"),
            (self.checker_version, "checker_version"),
            (self.arithmetic_mode, "arithmetic_mode"),
        ):
            _require_identifier(value, label)
        if not isinstance(self.conclusion, CertificateConclusion):
            raise ValidationError("certificate conclusion must be a CertificateConclusion")
        if not isinstance(self.claim_hash, ArtifactDigest) or not isinstance(
            self.model_hash, ArtifactDigest
        ):
            raise ValidationError("certificate claim_hash and model_hash must be ArtifactDigest")
        assumption_ids = tuple(self.assumption_ids)
        if any(not isinstance(item, str) or not item for item in assumption_ids):
            raise ValidationError("certificate assumption_ids must be non-empty strings")
        if len(assumption_ids) != len(set(assumption_ids)):
            raise ValidationError("certificate assumption_ids must be unique")
        object.__setattr__(self, "assumption_ids", assumption_ids)
        if not isinstance(self.payload, Mapping):
            raise ValidationError("certificate payload must be a JSON object")
        mutable_payload = _thaw_json(cast(JSONValue, self.payload))
        canonical_json_bytes(mutable_payload)
        object.__setattr__(self, "payload", _freeze_json(mutable_payload))
        provenance = tuple(self.provenance)
        if any(not isinstance(item, ProvenanceEntry) for item in provenance):
            raise ValidationError("certificate provenance must contain ProvenanceEntry values")
        if len(provenance) != len({item.source_id for item in provenance}):
            raise ValidationError("certificate provenance source identifiers must be unique")
        object.__setattr__(self, "provenance", provenance)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "schema_version": self.schema_version,
            "certificate_id": self.certificate_id,
            "family": self.family,
            "conclusion": self.conclusion.value,
            "claim_hash": str(self.claim_hash),
            "model_hash": str(self.model_hash),
            "assumption_ids": list(self.assumption_ids),
            "checker_id": self.checker_id,
            "checker_version": self.checker_version,
            "arithmetic_mode": self.arithmetic_mode,
            "payload": _thaw_json(cast(JSONValue, self.payload)),
            "provenance": [item.to_dict() for item in self.provenance],
        }

    @classmethod
    def from_dict(cls, value: object) -> Certificate:
        data = _expect_object(
            value,
            (
                "schema_version",
                "certificate_id",
                "family",
                "conclusion",
                "claim_hash",
                "model_hash",
                "assumption_ids",
                "checker_id",
                "checker_version",
                "arithmetic_mode",
                "payload",
                "provenance",
            ),
            "certificate",
        )
        if data["schema_version"] != SCHEMA_VERSION:
            raise ValidationError(
                f"unsupported certificate schema version: {data['schema_version']!r}"
            )
        if not isinstance(data["payload"], Mapping):
            raise ValidationError("certificate payload must be a JSON object")
        try:
            conclusion = CertificateConclusion(data["conclusion"])
        except (TypeError, ValueError) as exc:
            raise ValidationError("unsupported certificate conclusion") from exc
        return cls(
            schema_version=SCHEMA_VERSION,
            certificate_id=_require_identifier(data["certificate_id"], "certificate_id"),
            family=_require_identifier(data["family"], "certificate family"),
            conclusion=conclusion,
            claim_hash=ArtifactDigest.from_json(data["claim_hash"]),
            model_hash=ArtifactDigest.from_json(data["model_hash"]),
            assumption_ids=tuple(
                _require_identifier(item, "assumption_id")
                for item in _expect_array(data["assumption_ids"], "certificate assumption_ids")
            ),
            checker_id=_require_identifier(data["checker_id"], "checker_id"),
            checker_version=_require_identifier(data["checker_version"], "checker_version"),
            arithmetic_mode=_require_identifier(data["arithmetic_mode"], "arithmetic_mode"),
            payload=cast(Mapping[str, JSONValue], data["payload"]),
            provenance=tuple(
                ProvenanceEntry.from_dict(item)
                for item in _expect_array(data["provenance"], "certificate provenance")
            ),
        )


__all__ = ["Certificate", "CertificateConclusion"]
