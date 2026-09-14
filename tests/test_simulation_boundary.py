"""The certification boundary, checked mechanically rather than trusted to prose.

`docs/architecture/backends.md` states that no simulation output may cross into
certification. A statement in a document can be forgotten during a refactor; an import
cannot. These tests are the enforcement.

Only executable lines are inspected. The docstrings in this subpackage deliberately name the
symbols the layer may not use, in order to say that it may not use them; blanking docstrings
first is what keeps that prose legal while the code stays constrained.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

import robocert.simulation
from robocert.checking import production_checker_families

SIMULATION_DIR = Path(robocert.simulation.__file__).parent
SIMULATION_SOURCES = sorted(SIMULATION_DIR.glob("*.py"))

# Symbols that could promote a result, and modules only the trusted core should reach.
FORBIDDEN_SYMBOLS = (
    "CERTIFIED_",
    "CheckedCertificate",
    "CheckedCounterexample",
    "counterexample_result",
    "refute",
    "CheckerDecision",
    "ResultStatus",
    "certified_result",
    "numerical_result",
    "verify_certificate",
    "robocert.certificates",
    "robocert.checkers",
    "robocert.checking",
    "robocert.results",
    "robocert.refutation",
)


def executable_source(text: str) -> str:
    """Blank out docstrings and comments, leaving only lines that can run."""

    tree = ast.parse(text)
    lines = text.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if ast.get_docstring(node, clean=False) is None:
            continue
        first = node.body[0]
        assert first.end_lineno is not None
        for index in range(first.lineno - 1, first.end_lineno):
            lines[index] = ""
    return "\n".join(line for line in lines if not line.lstrip().startswith("#"))


def test_the_subpackage_has_sources_to_check() -> None:
    assert {path.name for path in SIMULATION_SOURCES} >= {
        "__init__.py",
        "backend.py",
        "falsification.py",
        "mujoco_backend.py",
    }


@pytest.mark.parametrize("source", SIMULATION_SOURCES, ids=lambda path: path.name)
def test_simulation_code_never_touches_the_certification_core(source: Path) -> None:
    code = executable_source(source.read_text(encoding="utf-8"))
    for symbol in FORBIDDEN_SYMBOLS:
        assert symbol not in code, f"{source.name} uses {symbol} in executable code"


def test_the_guard_would_catch_a_real_violation() -> None:
    """A negative control: the stripper must not blank out actual code."""

    offending = '"""A docstring naming ResultStatus is fine."""\nx = ResultStatus.UNKNOWN\n'
    code = executable_source(offending)
    assert "ResultStatus" in code


@pytest.mark.parametrize("symbol", ["refute", "CheckedCounterexample", "counterexample_result"])
def test_guard_detects_refutation_imports(symbol: str) -> None:
    code = executable_source(f"from robocert import {symbol}\n")
    assert any(forbidden in code for forbidden in FORBIDDEN_SYMBOLS)


def test_importing_robocert_does_not_import_mujoco() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import robocert, sys; print('mujoco' in sys.modules)"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == "False"


def test_importing_the_simulation_subpackage_does_not_import_mujoco() -> None:
    """`robocert.simulation` is usable without the extra; only `mujoco_backend` needs it."""

    completed = subprocess.run(
        [sys.executable, "-c", "import robocert.simulation, sys; print('mujoco' in sys.modules)"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == "False"


def test_production_checker_registry_is_unaffected() -> None:
    """Adding a simulation backend registers no checker and opens no certification path."""

    assert production_checker_families() == ()
