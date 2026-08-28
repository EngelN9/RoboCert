from __future__ import annotations

import pytest

from robocert.artifacts import canonical_json_bytes, digest_json
from robocert.specification import ValidationError


def test_canonical_json_is_independent_of_mapping_order() -> None:
    left = {"b": [2, 3], "a": {"z": True, "x": "value"}}
    right = {"a": {"x": "value", "z": True}, "b": [2, 3]}

    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert digest_json(left) == digest_json(right)


@pytest.mark.parametrize("value", [0.0, float("inf"), float("nan")])
def test_canonical_json_rejects_all_floats(value: float) -> None:
    with pytest.raises(ValidationError, match="floating-point"):
        canonical_json_bytes({"value": value})


def test_digest_has_explicit_algorithm_prefix() -> None:
    digest = digest_json({"artifact": "fixture"})
    assert str(digest).startswith("sha256:")
    assert len(str(digest)) == len("sha256:") + 64


def test_canonical_digest_has_cross_platform_golden_value() -> None:
    assert str(digest_json({"a": [1, "μ"], "b": True})) == (
        "sha256:207d8fbd51c71ae3e029e988c13d112ffa6a5f07fde19a2e99639ca8e6f4c3ca"
    )
