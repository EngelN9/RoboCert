"""Regression gate for the frozen RC-002 cross-verification run."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_rc002_run_artifacts_validate() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "benchmarks" / "proof-verification" / "scripts" / "check_rc002_run.py"),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
