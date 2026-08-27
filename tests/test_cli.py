from __future__ import annotations

import json
from pathlib import Path

import pytest

from robocert import checking, cli
from robocert.cli import EXIT_CERTIFIED, EXIT_ERROR, EXIT_NOT_CERTIFIED, main

_EXAMPLES = Path(__file__).parents[1] / "examples"

# Each example's recorded verdict, so the examples double as end-to-end tests.
_EXPECTED = {
    "reachable": EXIT_NOT_CERTIFIED,
    "obstacle-blocked": EXIT_NOT_CERTIFIED,
    "out-of-reach": EXIT_NOT_CERTIFIED,
}


@pytest.mark.parametrize(("name", "expected"), sorted(_EXPECTED.items()))
def test_examples_produce_their_recorded_verdict(name: str, expected: int, tmp_path: Path) -> None:
    code = main(["certify", str(_EXAMPLES / f"{name}.json"), "-o", str(tmp_path / name)])
    assert code == expected
    assert (tmp_path / name / "result.json").is_file()
    assert (tmp_path / name / "report.md").is_file()


def test_certify_then_check_round_trip(tmp_path: Path) -> None:
    """The public path stays UNKNOWN while the evidence gate is closed."""
    outdir = tmp_path / "run"
    assert main(["certify", str(_EXAMPLES / "reachable.json"), "-o", str(outdir)]) == (
        EXIT_NOT_CERTIFIED
    )
    assert not (outdir / "claim.json").exists()
    assert not (outdir / "certificate.json").exists()
    assert main(["check", str(outdir)]) == EXIT_NOT_CERTIFIED


def test_closed_gate_does_not_enter_legacy_search_or_limit_conversion(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise AssertionError("legacy production path must remain unreachable")

    monkeypatch.setattr(cli, "load_problem", forbidden)
    monkeypatch.setattr(cli, "certify_problem", forbidden)
    monkeypatch.setattr(checking, "_PRODUCTION_CHECKERS", {"unrelated.family": object()})

    assert (
        main(["certify", str(_EXAMPLES / "reachable.json"), "-o", str(tmp_path / "run")])
        == EXIT_NOT_CERTIFIED
    )


def test_check_detects_a_tampered_problem(tmp_path: Path) -> None:
    """Editing the model after certification must invalidate the certificate --
    the model hash binds them."""
    outdir = tmp_path / "run"
    main(["certify", str(_EXAMPLES / "reachable.json"), "-o", str(outdir)])
    problem = outdir / "problem.json"
    problem.write_text(
        problem.read_text(encoding="utf-8").replace('"5", "3"', '"5.0001", "3"'),
        encoding="utf-8",
    )
    assert main(["check", str(outdir)]) == EXIT_NOT_CERTIFIED


def test_check_detects_a_tampered_witness(tmp_path: Path) -> None:
    """Forged artifacts cannot bypass the closed production gate."""
    outdir = tmp_path / "run"
    main(["certify", str(_EXAMPLES / "reachable.json"), "-o", str(outdir)])
    (outdir / "claim.json").write_text("{}", encoding="utf-8")
    (outdir / "certificate.json").write_text("{}", encoding="utf-8")
    assert main(["check", str(outdir)]) == EXIT_NOT_CERTIFIED


def test_check_on_an_uncertified_run_reports_no_certificate(tmp_path: Path) -> None:
    outdir = tmp_path / "run"
    main(["certify", str(_EXAMPLES / "out-of-reach.json"), "-o", str(outdir)])
    assert not (outdir / "certificate.json").exists()
    assert main(["check", str(outdir)]) == EXIT_NOT_CERTIFIED


def test_report_states_that_unknown_is_not_infeasibility(tmp_path: Path) -> None:
    """Proof P2 Warning 11.5. The obvious misreading of exit code 1 is the one
    the mathematics specifically forbids, so the report must say so."""
    outdir = tmp_path / "run"
    main(["certify", str(_EXAMPLES / "out-of-reach.json"), "-o", str(outdir)])
    report = (outdir / "report.md").read_text(encoding="utf-8")
    assert "not infeasibility" in report
    assert "no mathematical" in report


def test_disabled_report_records_that_no_legacy_search_ran(tmp_path: Path) -> None:
    outdir = tmp_path / "run"
    main(["certify", str(_EXAMPLES / "reachable.json"), "-o", str(outdir)])
    report = (outdir / "report.md").read_text(encoding="utf-8")
    assert "No E2-approved production checker" in report
    assert "legacy four-chart search" in report
    assert "radian-to-half-angle conversion" in report


def test_float_literals_in_the_problem_file_are_refused(tmp_path: Path) -> None:
    """A JSON float would silently leave the exact-arithmetic regime."""
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "problem_id": "bad.float",
                "robot": {"kind": "planar_2r", "link_lengths": [5.5, 3]},
                "joint_limits": {"q1": ["-2.5", "2.5"], "q2": ["-2.5", "2.5"]},
                "task": {"target": ["6", "2"]},
                "margins": {"clearance": "0.1", "singularity": "0.5"},
            }
        ),
        encoding="utf-8",
    )
    assert main(["certify", str(bad), "-o", str(tmp_path / "out")]) == EXIT_ERROR


def test_semantically_unreviewed_problem_remains_unknown_while_gate_is_closed(
    tmp_path: Path,
) -> None:
    """The disabled path does not invoke the legacy semantic parser."""
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "problem_id": "bad.margin",
                "robot": {"kind": "planar_2r", "link_lengths": ["5", "3"]},
                "joint_limits": {"q1": ["-2.5", "2.5"], "q2": ["-2.5", "2.5"]},
                "task": {"target": ["6", "2"]},
                "margins": {"clearance": "0.1", "singularity": "999"},
            }
        ),
        encoding="utf-8",
    )
    assert main(["certify", str(bad), "-o", str(tmp_path / "out")]) == EXIT_NOT_CERTIFIED


def test_schema_command_emits_each_packaged_schema(capsys: pytest.CaptureFixture[str]) -> None:
    for name in ("problem.schema.json", "claim.schema.json", "certificate.schema.json"):
        assert main(["schema", name]) == EXIT_CERTIFIED
        assert json.loads(capsys.readouterr().out)["$id"].endswith(name)
