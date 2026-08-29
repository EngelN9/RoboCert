"""Re-run every *available* proof-assistant kernel and check it against a committed record.

This is the CI-side complement to `src/robocert/attestation.py`. That module validates an
attestation's *shape* and *bindings*; it never runs a kernel and never touches the filesystem.
This script is what re-derives the kernel result, for whichever systems are installed on the
machine running it. A system that is not installed is reported as unavailable. It is never
treated as passing.

For each record under `formal/attestations/`:

1. **Every attested entry is checked against the files it names.** `artifact_digest` must still
   match the proof source, and `statement_digest` must still match the committed statement
   text. A silent edit to either therefore invalidates the attestation instead of leaving a
   stale one standing. This is the check the module docstring previously *claimed* while the
   code performed only the `kernel_accepted` test -- an overclaim in a guard, fixed here and
   pinned by `tests/test_attestation.py`.
2. **Every pending system with a runnable toolchain is actually compiled**, and its output
   scanned for an admitted/`sorry`-ed proof.
3. **Every pending system without a toolchain is reported and skipped.** Nothing is invented.
4. The record's coverage is compared against the real `AttestationPolicy`, and the resulting
   verdict is printed.

Exit code is nonzero only for an actual defect: a stale digest, a missing named file, a kernel
that now fails, or a malformed record. An honestly incomplete record exits 0 -- "unavailable"
is the state the tightening gate exists to handle, not an error.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from robocert.checkers import PLANAR2R_ATTESTATION_POLICY

REPO_ROOT = Path(__file__).resolve().parent.parent
ATTESTATIONS_DIR = REPO_ROOT / "formal" / "attestations"
FORMAL_DIR = REPO_ROOT / "formal"


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def _run(cmd: list[str], *, cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return completed.returncode, completed.stdout + completed.stderr


def _check_rocq(source: Path) -> tuple[bool, str]:
    """Compile the .v file directly with rocqc/coqc. No project-wide build system assumed."""
    tool = shutil.which("rocqc") or shutil.which("coqc")
    if tool is None:
        return False, "no rocqc/coqc on PATH"
    code, output = _run([tool, "-Q", str(source.parent), "RoboCert", str(source)], cwd=FORMAL_DIR)
    if code != 0:
        return False, f"compilation failed:\n{output}"
    if "admit" in output.lower():
        return False, f"output mentions 'admit' -- treating as an incomplete proof:\n{output}"
    return True, "compiled cleanly"


def _check_isabelle(session_dir: Path) -> tuple[bool, str]:
    tool = shutil.which("isabelle")
    if tool is None:
        return False, "no isabelle on PATH"
    code, output = _run([tool, "build", "-D", str(session_dir), "-v"], cwd=FORMAL_DIR)
    if code != 0:
        return False, f"session build failed:\n{output}"
    if "sorry" in output.lower():
        return False, f"output mentions 'sorry' -- treating as an incomplete proof:\n{output}"
    return True, "session built cleanly"


def _resolve(record: dict[str, Any], section: str, system: str) -> Path | None:
    """Resolve a repo-relative path the record declares for `system`, if it declares one."""
    relative = record.get(section, {}).get(system)
    if not isinstance(relative, str):
        return None
    return REPO_ROOT / relative


def _check_bound_digests(
    path: Path,
    record: dict[str, Any],
    entry: dict[str, Any],
    system: str,
) -> list[str]:
    """Verify an attested entry's digests still match the files the record names.

    Without this, an attestation survives an edit to the very source it attests to.
    """
    errors: list[str] = []
    for section, digest_field, label in (
        ("sources", "artifact_digest", "proof source"),
        ("statements", "statement_digest", "statement text"),
    ):
        target = _resolve(record, section, system)
        if target is None:
            errors.append(
                f"{path}: attested system {system!r} has no {section}[{system!r}] entry, so its "
                f"{digest_field} cannot be verified. Every attested system must name its files."
            )
            continue
        if not target.is_file():
            errors.append(f"{path}: {system!r} {section}[{system!r}] names a missing file {target}")
            continue
        actual = _sha256_file(target)
        recorded = entry.get(digest_field)
        if actual != recorded:
            errors.append(
                f"{path}: {system!r} {digest_field} is STALE -- the {label} at {target} has "
                f"changed since it was attested (recorded {recorded!r}, actual {actual!r}). "
                "Re-run the kernel and re-attest; do not just update the digest."
            )
    return errors


def check_record(path: Path) -> list[str]:
    """Return diagnostics for one attestation record; empty means clean."""
    errors: list[str] = []
    try:
        record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: could not read/parse: {exc}"]

    entries = record.get("attestations", {}).get("entries", [])
    if not isinstance(entries, list):
        return [f"{path}: attestations.entries must be a list"]

    attested_systems: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{path}: attestation entry is not an object")
            continue
        system = entry.get("system")
        if not isinstance(system, str):
            errors.append(f"{path}: attestation entry has no string 'system'")
            continue

        if entry.get("kernel_accepted") is not True:
            errors.append(f"{path}: entry for {system!r} does not claim kernel_accepted=true")
            continue

        digest_errors = _check_bound_digests(path, record, entry, system)
        errors.extend(digest_errors)
        if digest_errors:
            continue

        attested_systems.add(system)
        print(
            f"check_attestations: {path.name}: {system!r} attested "
            "(kernel_accepted=true, artifact and statement digests match)"
        )

    for system, info in record.get("pending_systems", {}).items():
        source = _resolve(record, "sources", system)
        if source is None or not source.is_file():
            errors.append(f"{path}: pending system {system!r} names a missing source {source}")
            continue

        if system == "rocq" and (_tool_available("rocqc") or _tool_available("coqc")):
            ok, detail = _check_rocq(source)
        elif system == "isabelle" and _tool_available("isabelle"):
            ok, detail = _check_isabelle(source.parent.parent)
        else:
            reason = info.get("reason", "no reason recorded")
            print(
                f"check_attestations: {path.name}: {system!r} UNAVAILABLE on this machine "
                f"-- reported, not treated as a pass ({reason})"
            )
            continue

        if ok:
            print(
                f"check_attestations: {path.name}: {system!r} toolchain available and "
                f"{detail} -- record it with `kernel_accepted: true` and move it out of "
                "pending_systems"
            )
        else:
            errors.append(f"{path}: pending system {system!r} is available but failed: {detail}")

    missing = set(PLANAR2R_ATTESTATION_POLICY.required_systems) - attested_systems
    if missing:
        print(
            f"check_attestations: {path.name}: verdict against the real "
            "PLANAR2R_ATTESTATION_POLICY is REJECTED -- required system(s) with no usable "
            f"attestation: {sorted(missing)}. This is the tightening gate working as "
            "designed, not a defect."
        )
    else:
        print(f"check_attestations: {path.name}: all required systems attested")

    return errors


def main() -> int:
    if not ATTESTATIONS_DIR.is_dir():
        print(f"check_attestations: no directory at {ATTESTATIONS_DIR}", file=sys.stderr)
        return 2

    records = sorted(ATTESTATIONS_DIR.glob("*.json"))
    if not records:
        print(f"check_attestations: no attestation records found under {ATTESTATIONS_DIR}")
        return 0

    all_errors: list[str] = []
    for record_path in records:
        all_errors.extend(check_record(record_path))

    if all_errors:
        for error in all_errors:
            print(f"check_attestations: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
