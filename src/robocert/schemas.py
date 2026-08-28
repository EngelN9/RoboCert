"""Read-only access to the versioned JSON Schema documents."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

from robocert.errors import ValidationError

SCHEMA_NAMES = frozenset(
    {
        "certificate.schema.json",
        "claim.schema.json",
        "problem.schema.json",
        "result.schema.json",
    }
)


def _schema_text(name: str) -> str:
    if name not in SCHEMA_NAMES:
        raise ValidationError(f"unknown RoboCert schema: {name!r}")
    packaged = files("robocert").joinpath("schemas", name)
    if packaged.is_file():
        return packaged.read_text(encoding="utf-8")

    # Editable installs map the Python package directly to src/robocert while
    # Hatch's force-included wheel resources remain at the repository root.
    repository_copy = Path(__file__).parents[2] / "schemas" / name
    if repository_copy.is_file():
        return repository_copy.read_text(encoding="utf-8")
    raise ValidationError(f"RoboCert schema resource is unavailable: {name!r}")


def schema_document(name: str) -> dict[str, Any]:
    """Load a fresh mutable copy of a supported versioned schema."""

    value = json.loads(_schema_text(name))
    if not isinstance(value, dict):
        raise ValidationError(f"RoboCert schema resource is not a JSON object: {name!r}")
    return cast(dict[str, Any], value)


__all__ = ["SCHEMA_NAMES", "schema_document"]
