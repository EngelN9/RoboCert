from __future__ import annotations

import pytest

from robocert.artifacts import digest_json
from robocert.results import (
    CertificationResult,
    ResultStatus,
    numerical_result,
    unknown_result,
)


def test_certification_result_cannot_be_constructed_directly() -> None:
    with pytest.raises(TypeError):
        CertificationResult(  # type: ignore[call-arg]
            status=ResultStatus.CERTIFIED_FEASIBLE,
            claim_hash=digest_json({"claim": 1}),
            model_hash=digest_json({"model": 1}),
        )


def test_unknown_result_preserves_diagnostics() -> None:
    result = unknown_result(
        digest_json({"claim": 1}),
        digest_json({"model": 1}),
        ("no production checker registered",),
    )
    assert result.status is ResultStatus.UNKNOWN
    assert result.diagnostics == ("no production checker registered",)


@pytest.mark.parametrize(
    "status",
    [ResultStatus.NUMERICALLY_FEASIBLE, ResultStatus.NUMERICALLY_INFEASIBLE],
)
def test_numerical_result_cannot_promote_to_certified(status: ResultStatus) -> None:
    result = numerical_result(
        status,
        digest_json({"claim": 1}),
        digest_json({"model": 1}),
        ("heuristic evidence only",),
    )
    assert result.status is status
    assert result.checked_certificate is None


@pytest.mark.parametrize(
    "status",
    [
        ResultStatus.CERTIFIED_FEASIBLE,
        ResultStatus.CERTIFIED_INFEASIBLE,
        ResultStatus.COUNTEREXAMPLE,
        ResultStatus.UNKNOWN,
    ],
)
def test_numerical_factory_rejects_other_statuses(status: ResultStatus) -> None:
    with pytest.raises(ValueError, match="numerical"):
        numerical_result(
            status,
            digest_json({"claim": 1}),
            digest_json({"model": 1}),
            (),
        )
