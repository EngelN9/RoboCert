"""Regression tests for the research-report overclaim guard."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = ROOT / "scripts" / "check_report_language.py"


def _load_guard() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_report_language", GUARD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_existing_reports_pass_language_guard() -> None:
    completed = subprocess.run(
        [sys.executable, str(GUARD_PATH), "research/reports"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_planted_overclaim_is_rejected() -> None:
    guard = _load_guard()
    violations = guard.find_violations(
        "This proves the robot is 100% safe.",
        guard.load_claim_tiers(),
    )
    assert violations
