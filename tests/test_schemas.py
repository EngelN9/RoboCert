from __future__ import annotations

import json
from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as SchemaValidationError

from robocert import checking
from robocert.certificates import Certificate
from robocert.checking import CheckerDecision, verify_certificate
from robocert.results import certified_result, unknown_result
from robocert.schemas import SCHEMA_NAMES, schema_document
from robocert.specification import Claim, Unit

ROOT = Path(__file__).parents[1]


def load_schema(name: str) -> dict[str, object]:
    with (ROOT / "schemas" / name).open(encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return schema


def test_packaged_schema_loader_matches_repository_contracts() -> None:
    assert (
        frozenset(
            {
                "claim.schema.json",
                "certificate.schema.json",
                "problem.schema.json",
                "result.schema.json",
            }
        )
        == SCHEMA_NAMES
    )
    for name in SCHEMA_NAMES:
        assert schema_document(name) == load_schema(name)


def test_claim_matches_versioned_schema(sample_claim: Claim) -> None:
    Draft202012Validator(load_schema("claim.schema.json")).validate(sample_claim.to_dict())


def test_claim_schema_accepts_squared_length_jacobian_margin(sample_claim: Claim) -> None:
    squared_margin = replace(sample_claim.margins[0], unit=Unit.SQUARE_METRE)
    claim = replace(sample_claim, margins=(squared_margin,))

    Draft202012Validator(load_schema("claim.schema.json")).validate(claim.to_dict())


def test_certificate_matches_versioned_schema(
    make_certificate: Callable[..., Certificate],
) -> None:
    certificate = make_certificate()
    Draft202012Validator(load_schema("certificate.schema.json")).validate(certificate.to_dict())
    assert Certificate.from_dict(certificate.to_dict()) == certificate


def test_result_matches_versioned_schema(sample_claim: Claim) -> None:
    result = unknown_result(sample_claim.digest(), sample_claim.digest(), ("fixture",))
    Draft202012Validator(load_schema("result.schema.json")).validate(result.to_dict())


@pytest.mark.parametrize("mutation", ["version", "extra", "float"])
def test_claim_schema_rejects_noncanonical_artifacts(sample_claim: Claim, mutation: str) -> None:
    artifact = deepcopy(sample_claim.to_dict())
    if mutation == "version":
        artifact["schema_version"] = "9.0.0"
    elif mutation == "extra":
        artifact["unexpected"] = True
    else:
        artifact["margins"][0]["bound"] = {"numerator": 0.5, "denominator": 1}  # type: ignore[index]

    with pytest.raises(SchemaValidationError):
        Draft202012Validator(load_schema("claim.schema.json")).validate(artifact)


def test_result_schema_rejects_status_conclusion_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    sample_claim: Claim,
    make_certificate: Callable[..., Certificate],
) -> None:
    class AcceptingChecker:
        checker_id = "fixture-checker"
        checker_version = "1.0.0"
        certificate_family = "fixture.exact"
        arithmetic_mode = "exact-rational"

        def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
            del claim, certificate
            return CheckerDecision(True)

    certificate = make_certificate()
    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {"fixture.exact": AcceptingChecker()},
    )
    report = verify_certificate(sample_claim, certificate.model_hash, certificate)
    assert report.checked_certificate is not None
    mismatched = deepcopy(certified_result(report.checked_certificate).to_dict())
    mismatched["checked_certificate"]["conclusion"] = "infeasible"  # type: ignore[index]

    with pytest.raises(SchemaValidationError):
        Draft202012Validator(load_schema("result.schema.json")).validate(mismatched)
