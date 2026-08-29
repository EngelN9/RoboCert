"""The attestation record guard must actually guard.

`scripts/check_attestations.py` previously carried a docstring promising it verified
`artifact_digest` against the proof source; `grep` showed the field appeared *only* in that
docstring. The check did not exist. These tests exist so that regression cannot recur
silently: each one constructs a record that is wrong in exactly one way and asserts the guard
says so.

Records are built in-memory against real repository files, with a deliberately wrong digest --
no repository file is ever mutated by these tests.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "check_attestations.py"

_WRONG_DIGEST = "sha256:" + "0" * 64

# A real, committed file, used so the guard is exercised against genuine content rather than
# a fixture that could drift away from what the script actually reads.
_REAL_SOURCE = "formal/RoboCert/Soundness.lean"
_REAL_STATEMENT = "formal/attestations/statements/lean4.txt"


def _load_script() -> Any:
    spec = importlib.util.spec_from_file_location("check_attestations", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def script() -> Any:
    return _load_script()


def _record(**entry_overrides: object) -> dict[str, Any]:
    """A record whose single lean4 entry is correct unless an override breaks it."""
    import hashlib

    def digest(relative: str) -> str:
        return "sha256:" + hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()

    entry: dict[str, Any] = {
        "system": "lean4",
        "toolchain": "leanprover/lean4:v4.33.1",
        "claim_hash": _WRONG_DIGEST,
        "model_hash": _WRONG_DIGEST,
        "checker_id": "robocert.planar2r_exact_witness.attested",
        "checker_version": "0.1.0",
        "statement_digest": digest(_REAL_STATEMENT),
        "artifact_digest": digest(_REAL_SOURCE),
        "axioms": ["propext", "Classical.choice", "Quot.sound"],
        "kernel_accepted": True,
    }
    entry.update(entry_overrides)
    return {
        "sources": {"lean4": _REAL_SOURCE},
        "statements": {"lean4": _REAL_STATEMENT},
        "attestations": {"format": "robocert.attestation/1", "entries": [entry]},
        "pending_systems": {},
    }


def _run(script: Any, record: dict[str, Any], tmp_path: Path) -> list[str]:
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return list(script.check_record(path))


def test_intact_record_produces_no_digest_errors(script: Any, tmp_path: Path) -> None:
    """Control: with both digests correct, the guard raises nothing about digests."""
    errors = _run(script, _record(), tmp_path)
    assert not [error for error in errors if "STALE" in error]


def test_stale_artifact_digest_is_caught(script: Any, tmp_path: Path) -> None:
    """An attestation must not survive an edit to the proof source it attests to."""
    errors = _run(script, _record(artifact_digest=_WRONG_DIGEST), tmp_path)

    assert any("artifact_digest is STALE" in error for error in errors)


def test_stale_statement_digest_is_caught(script: Any, tmp_path: Path) -> None:
    """Nor an edit to the statement text -- the defense against proving the wrong theorem."""
    errors = _run(script, _record(statement_digest=_WRONG_DIGEST), tmp_path)

    assert any("statement_digest is STALE" in error for error in errors)


def test_attested_system_with_no_declared_source_is_caught(script: Any, tmp_path: Path) -> None:
    """An entry whose files are undeclared cannot be verified, so it must not pass silently."""
    record = _record()
    record["sources"] = {}
    errors = _run(script, record, tmp_path)

    assert any("has no sources" in error for error in errors)


def test_kernel_rejection_in_a_record_is_caught(script: Any, tmp_path: Path) -> None:
    errors = _run(script, _record(kernel_accepted=False), tmp_path)

    assert any("does not claim kernel_accepted=true" in error for error in errors)


def test_stale_entry_also_loses_its_coverage(script: Any, tmp_path: Path) -> None:
    """A stale attestation is not merely an error: it stops counting toward the required set.

    Otherwise a stale entry could still satisfy the policy's coverage requirement while its
    underlying proof had changed out from under it.
    """
    errors = _run(script, _record(artifact_digest=_WRONG_DIGEST), tmp_path)

    assert any("artifact_digest is STALE" in error for error in errors)
    # lean4 must not have been counted as attested, so it is reported missing too.
    assert any("lean4" in error for error in errors)


def test_committed_record_is_clean(script: Any) -> None:
    """The real record in the repository must pass its own guard."""
    errors = list(
        script.check_record(_REPO_ROOT / "formal" / "attestations" / "planar2r-exact-witness.json")
    )

    assert errors == []


def test_require_flag_fails_when_a_toolchain_is_absent(script: Any, tmp_path: Path) -> None:
    """A CI job named after a prover must not pass green when that prover is missing.

    The first real run of the `rocq` CI job did exactly that: opam installed Rocq 9.0.0,
    its PATH never reached the verification step, the script reported UNAVAILABLE, and the
    job went green having verified nothing. `--require` is what makes that impossible.
    """
    record = _record()
    record["pending_systems"] = {"rocq": {"reason": "not installed in this test"}}
    record["sources"]["rocq"] = _REAL_SOURCE  # any real file; it is never compiled here

    without = _run(script, record, tmp_path)
    assert not any("REQUIRED to be available" in error for error in without)

    path = tmp_path / "required.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with_require = list(script.check_record(path, require_available=["rocq"]))

    assert any("REQUIRED to be available" in error for error in with_require)
