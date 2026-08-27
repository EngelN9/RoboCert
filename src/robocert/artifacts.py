"""Canonical JSON serialization and cryptographic artifact digests."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypeAlias

from robocert.errors import ValidationError

JSONScalar: TypeAlias = bool | int | str | None
JSONValue: TypeAlias = JSONScalar | Mapping[str, "JSONValue"] | Sequence["JSONValue"]

_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ArtifactDigest:
    """A tagged SHA-256 digest bound to a serialized artifact."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or _DIGEST_PATTERN.fullmatch(self.value) is None:
            raise ValueError(
                "artifact digest must be 'sha256:' followed by 64 lowercase hex digits"
            )

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_json(cls, value: object) -> ArtifactDigest:
        if not isinstance(value, str):
            raise ValidationError("artifact digest must be a string")
        try:
            return cls(value)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc


def _validate_json(value: object, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if isinstance(value, float):
        raise ValidationError(f"floating-point values are forbidden in canonical JSON at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValidationError(f"JSON object key at {path} must be a string")
            _validate_json(item, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _validate_json(item, f"{path}[{index}]")
        return
    raise ValidationError(f"unsupported canonical JSON value {type(value).__name__} at {path}")


def canonical_json_bytes(value: JSONValue) -> bytes:
    """Serialize JSON deterministically after rejecting imprecise numbers."""

    _validate_json(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest_json(value: JSONValue) -> ArtifactDigest:
    """Hash canonical JSON with an explicit algorithm tag."""

    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return ArtifactDigest(f"sha256:{digest}")
