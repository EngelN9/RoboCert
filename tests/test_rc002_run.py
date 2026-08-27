"""Regression gates for frozen and newly prepared RC-002 verification runs."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "benchmarks" / "proof-verification"
RUN_ID = "RCMPVB-20260821-CROSS-X-RUN001"
RUN001 = BENCHMARK_ROOT / "runs" / RUN_ID
CHECK_SCRIPT = BENCHMARK_ROOT / "scripts" / "check_rc002_run.py"
PREPARE_SCRIPT = BENCHMARK_ROOT / "scripts" / "prepare_rc002_run.py"


def _run(script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _snapshot(directory: Path) -> dict[str, tuple[str, int]]:
    return {
        path.relative_to(directory).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            path.stat().st_mtime_ns,
        )
        for path in directory.rglob("*")
        if path.is_file()
    }


def test_rc002_run_artifacts_validate_without_writes() -> None:
    before = _snapshot(RUN001)
    commands = (
        (),
        ("--run-id", RUN_ID, "--run-dir", str(RUN001)),
        ("--all-runs",),
    )
    for arguments in commands:
        completed = _run(CHECK_SCRIPT, *arguments)
        assert completed.returncode == 0, completed.stdout + completed.stderr
    assert _snapshot(RUN001) == before


def test_prepare_help_is_side_effect_free(tmp_path: Path) -> None:
    run_dir = tmp_path / "SHOULD-NOT-EXIST"
    private_map = tmp_path / "private" / "map.json"
    completed = _run(
        PREPARE_SCRIPT,
        "--run-dir",
        str(run_dir),
        "--private-map",
        str(private_map),
        "--help",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert not run_dir.exists()
    assert not private_map.exists()


def test_prepare_custom_run_is_idempotent_and_refuses_overwrite(tmp_path: Path) -> None:
    run_id = "RCMPVB-TEST-CROSS-X-RUN999"
    run_dir = tmp_path / run_id
    private_map = tmp_path / "private" / f"{run_id}-blinding-map.json"
    prepare_arguments = (
        "--repo-root",
        str(ROOT),
        "--run-id",
        run_id,
        "--run-dir",
        str(run_dir),
        "--private-map",
        str(private_map),
    )

    first = _run(PREPARE_SCRIPT, *prepare_arguments)
    assert first.returncode == 0, first.stdout + first.stderr
    assert private_map.is_file()

    manifest = _run(
        CHECK_SCRIPT,
        "--run-id",
        run_id,
        "--run-dir",
        str(run_dir),
        "--write-manifest",
    )
    assert manifest.returncode == 0, manifest.stdout + manifest.stderr
    before = _snapshot(run_dir)

    second = _run(PREPARE_SCRIPT, *prepare_arguments)
    assert second.returncode == 0, second.stdout + second.stderr
    assert _snapshot(run_dir) == before

    readme_path = run_dir / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8") + "mutation\n",
        encoding="utf-8",
    )
    refused = _run(PREPARE_SCRIPT, *prepare_arguments)
    assert refused.returncode != 0
    assert "refusing to overwrite differing artifact" in refused.stderr


def test_stopped_run_manifest_rewrite_is_refused() -> None:
    manifest_path = RUN001 / "manifest.sha256"
    before = (manifest_path.read_bytes(), manifest_path.stat().st_mtime_ns)
    completed = _run(CHECK_SCRIPT, "--write-manifest")
    assert completed.returncode != 0
    assert "refusing to rewrite manifest for stopped run" in completed.stdout
    assert (manifest_path.read_bytes(), manifest_path.stat().st_mtime_ns) == before
