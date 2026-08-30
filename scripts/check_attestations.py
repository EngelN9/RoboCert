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

`--require SYSTEM` inverts that for one system: it makes an unavailable toolchain a hard
failure. CI jobs whose entire purpose is to exercise a particular kernel MUST pass it. Without
it a job named after a prover passes green when that prover is absent, which is a worse signal
than a red build -- it is a green one that means nothing. That is not hypothetical: the first
run of the `rocq` job did exactly this, because opam installed Rocq but its PATH never reached
the step that needed it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections.abc import Sequence
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


def _rocq_command() -> list[str] | None:
    """Return the argv prefix that compiles a .v file, across Rocq/Coq naming generations.

    Rocq 9 renamed the compiler entry point: `coqc file.v` became `rocq compile file.v`.
    Some packagings still ship a `rocqc` shim. Probe all three rather than assuming one.
    """
    if shutil.which("rocq") is not None:
        return [shutil.which("rocq") or "rocq", "compile"]
    for legacy in ("rocqc", "coqc"):
        found = shutil.which(legacy)
        if found is not None:
            return [found]
    return None


def _check_rocq(source: Path) -> tuple[bool, str]:
    """Compile the .v file directly. No project-wide build system assumed."""
    command = _rocq_command()
    if command is None:
        return False, "no rocq/rocqc/coqc on PATH"
    argv = [*command, "-Q", str(source.parent), "RoboCert", str(source)]
    code, output = _run(argv, cwd=FORMAL_DIR)
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


def _toolchain_version(system: str) -> str | None:
    """The version string of the binary that just ran.

    This is the one piece of an attestation entry that CANNOT be reconstructed after the fact.
    Digests can be recomputed from committed files at any time; which toolchain actually
    accepted the proof is knowable only on the machine that ran it, which is why the evidence
    file exists at all.
    """
    if system == "rocq":
        command = _rocq_command()
        if command is None:
            return None
        argv = [command[0], "--version"]
    elif system == "isabelle":
        tool = shutil.which("isabelle")
        if tool is None:
            return None
        argv = [tool, "version"]
    else:
        return None
    code, output = _run(argv, cwd=FORMAL_DIR)
    if code != 0:
        return None
    first = output.strip().splitlines()
    return first[0].strip() if first else None


#: What an attestation entry needs that this evidence file does NOT establish. Kept as data so
#: the omission travels with the artifact instead of living only in a docstring.
EVIDENCE_GAPS = (
    "axioms: neither kernel is interrogated for its axiom dependencies here. Rocq would need "
    "`Print Assumptions` per lemma and Isabelle an equivalent; until one exists, the `axioms` "
    "field of an entry cannot be filled from a real run, and writing one anyway is the "
    "fabrication formal/AGENTS.md rule 7 forbids.",
)


def _evidence(
    record: dict[str, Any],
    record_path: Path,
    system: str,
    source: Path,
    detail: str,
) -> dict[str, Any]:
    """Provenance from a kernel run that actually happened. NOT an attestation entry.

    `check_attestations` used to print "record it with kernel_accepted: true" and discard
    everything the promotion would need. This captures it instead. It is deliberately shaped so
    it cannot be mistaken for, or pasted as, an `attestations.entries` element: the field names
    differ, and `not_an_attestation_entry` says why.
    """
    statement = _resolve(record, "statements", system)
    return {
        "not_an_attestation_entry": [
            "Provenance captured from a kernel run that really happened, for a system still "
            "listed under pending_systems. It is NOT an attestation and must not be pasted "
            "into attestations.entries as-is.",
            *EVIDENCE_GAPS,
        ],
        "record": record_path.name,
        "system": system,
        "toolchain": _toolchain_version(system),
        "kernel_result": detail,
        "source_path": str(source.relative_to(REPO_ROOT).as_posix()),
        "artifact_digest": _sha256_file(source),
        "statement_path": (
            str(statement.relative_to(REPO_ROOT).as_posix())
            if statement is not None and statement.is_file()
            else None
        ),
        "statement_digest": (
            _sha256_file(statement) if statement is not None and statement.is_file() else None
        ),
        "certificate": record.get("certificate", {}),
    }


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


def check_record(
    path: Path,
    require_available: Sequence[str] = (),
    evidence_dir: Path | None = None,
) -> list[str]:
    """Return diagnostics for one attestation record; empty means clean.

    `require_available` names systems whose toolchain MUST be present; an absent one
    becomes an error rather than a skip.

    `evidence_dir`, when given, receives one JSON file per pending system whose kernel actually
    ran and passed. Nothing is written for a system that was skipped or failed -- an evidence
    file exists only where a kernel really ran.
    """
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

        if system == "rocq" and _rocq_command() is not None:
            ok, detail = _check_rocq(source)
        elif system == "isabelle" and _tool_available("isabelle"):
            ok, detail = _check_isabelle(source.parent.parent)
        else:
            reason = info.get("reason", "no reason recorded")
            if system in require_available:
                errors.append(
                    f"{path}: {system!r} was REQUIRED to be available here but its toolchain "
                    "is not on PATH. Refusing to report success for a kernel that never ran."
                )
            else:
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
            if evidence_dir is not None:
                evidence = _evidence(record, path, system, source, detail)
                evidence_dir.mkdir(parents=True, exist_ok=True)
                target = evidence_dir / f"{path.stem}.{system}.json"
                target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
                print(
                    f"check_attestations: {path.name}: wrote run evidence for {system!r} to "
                    f"{target} (toolchain {evidence['toolchain']!r}). Still NOT sufficient for "
                    "an entry -- see 'not_an_attestation_entry' in the file."
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="SYSTEM",
        help=(
            "Fail if this proof system's toolchain is not installed. Use in a CI job whose "
            "purpose is to exercise that kernel, so the job cannot pass without it."
        ),
    )
    parser.add_argument(
        "--emit-evidence",
        metavar="DIR",
        help=(
            "Write run provenance here for every pending system whose kernel actually ran and "
            "passed: the toolchain version, which is not reconstructable afterwards, plus the "
            "digests and the certificate binding. Provenance only -- see EVIDENCE_GAPS."
        ),
    )
    args = parser.parse_args(argv)

    if not ATTESTATIONS_DIR.is_dir():
        print(f"check_attestations: no directory at {ATTESTATIONS_DIR}", file=sys.stderr)
        return 2

    records = sorted(ATTESTATIONS_DIR.glob("*.json"))
    if not records:
        print(f"check_attestations: no attestation records found under {ATTESTATIONS_DIR}")
        return 0

    evidence_dir = Path(args.emit_evidence) if args.emit_evidence else None
    all_errors: list[str] = []
    for record_path in records:
        all_errors.extend(
            check_record(
                record_path,
                require_available=args.require,
                evidence_dir=evidence_dir,
            )
        )

    if all_errors:
        for error in all_errors:
            print(f"check_attestations: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
