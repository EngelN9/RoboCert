"""Regression tests for the research-ledger validator (`scripts/check_ledger.py`).

Two properties are load-bearing for the ledger rules in `research/README.md`:

* The fatal-objection procedure relies on demotion cascading. Demoting a claim must make every
  dependent that now outranks it fail the monotonicity check, so an objection to one claim
  cannot leave its dependents quietly standing.
* The history gate counts `history:` lines. Bullets that belong to another field must never be
  counted as history, or a tier change could appear to carry a justification it does not have.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
LEDGER_SCRIPT = ROOT / "scripts" / "check_ledger.py"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_ledger", LEDGER_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator()


def _entry(entry_id: str, tier: str, *, depends: str = "[]", extra: str = "") -> str:
    referee = "research/reports/fixture-referee.md" if tier in ("E2", "E3") else "none"
    return (
        f"## {entry_id}\n"
        f"statement: fixture claim {entry_id}\n"
        f"tier: {tier}\n"
        f"depends: {depends}\n"
        f"proof: none\n"
        f"target_checker: not yet implemented\n"
        f"referee: {referee}\n"
        f"history:\n"
        f"  - 2026-09-11 created\n"
        f"{extra}"
    )


def test_the_real_ledger_passes() -> None:
    completed = subprocess.run(
        [sys.executable, str(LEDGER_SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_demoting_a_claim_forces_its_dependents_down() -> None:
    """The fatal-objection procedure (research/README.md rule 5) depends on this cascade."""

    before = _entry("RC-900", "E2") + _entry("RC-901", "E2", depends="[RC-900]")
    assert VALIDATOR.check_monotonicity(VALIDATOR.parse_ledger(before)) == []

    demoted = _entry("RC-900", "E1") + _entry("RC-901", "E2", depends="[RC-900]")
    errors = VALIDATOR.check_monotonicity(VALIDATOR.parse_ledger(demoted))
    assert len(errors) == 1
    assert "RC-901" in errors[0] and "RC-900" in errors[0]

    cascaded = _entry("RC-900", "E1") + _entry("RC-901", "E1", depends="[RC-900]")
    assert VALIDATOR.check_monotonicity(VALIDATOR.parse_ledger(cascaded)) == []


def test_refuting_a_claim_blocks_every_dependent() -> None:
    refuted = _entry("RC-900", "EX") + _entry("RC-901", "E0", depends="[RC-900]")
    errors = VALIDATOR.check_monotonicity(VALIDATOR.parse_ledger(refuted))
    assert errors and "refuted" in errors[0]


def test_mechanized_bullets_are_not_counted_as_history() -> None:
    """A bullet under a later field must not pad the history gate."""

    text = _entry(
        "RC-900",
        "E0",
        extra=(
            "mechanized:\n"
            "  - lean4: formal/RoboCert/Fixture.lean fixture_theorem\n"
            "  - rocq: formal/rocq/RoboCert/Fixture.v fixture_lemma\n"
            "fidelity: not independently checked against statement\n"
        ),
    )
    entry = VALIDATOR.parse_ledger(text)["RC-900"]
    assert entry["history"] == ["- 2026-09-11 created"]
    assert entry["mechanized"] == [
        "- lean4: formal/RoboCert/Fixture.lean fixture_theorem",
        "- rocq: formal/rocq/RoboCert/Fixture.v fixture_lemma",
    ]
    assert entry["fidelity"] == "not independently checked against statement"


def test_mechanization_without_a_fidelity_statement_is_rejected() -> None:
    """Recording kernel support without saying whether the formal statement was compared
    with the intended one is exactly the omission the fidelity field exists to prevent."""

    text = _entry(
        "RC-900",
        "E0",
        extra="mechanized:\n  - lean4: formal/RoboCert/Fixture.lean fixture_theorem\n",
    )
    errors = VALIDATOR.check_fidelity_declared(VALIDATOR.parse_ledger(text))
    assert len(errors) == 1 and "fidelity" in errors[0]


def test_an_entry_without_mechanization_needs_no_fidelity_field() -> None:
    text = _entry("RC-900", "E0")
    assert VALIDATOR.check_fidelity_declared(VALIDATOR.parse_ledger(text)) == []
