"""Fail closed if any audited Lean theorem depends on an unexpected axiom.

`lake build` only *warns* on `sorry`; a warning does not fail CI, and a `sorryAx`
dependency can therefore reach an audited theorem silently. `formal/RoboCert/Audit.lean`
emits `#print axioms` for every theorem the project relies on; this script reads that
output and rejects anything outside the standard three axioms.

This is the Lean-side analogue of the empty production checker registry in
`src/robocert/checking.py` -- a fail-closed gate, not a lint.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

FORMAL_DIR = Path(__file__).resolve().parent.parent / "formal"

# The axioms Lean's own standard library is built on. Anything else -- above all
# `sorryAx` -- means an audited theorem is not actually proved.
ALLOWED_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})

# Every theorem that must remain audited. Deleting a `#print axioms` line from
# Audit.lean is itself a failure, so the gate cannot be silently narrowed.
REQUIRED_DECLARATIONS = (
    "RoboCert.Formula.decideF_iff",
    "RoboCert.Formula.decideF_congr",
    "RoboCert.assignsBox_extendComps",
    "RoboCert.semFrom_of_witness",
    "RoboCert.exactWitness_sound",
)

_AXIOM_LINE = re.compile(r"'([^']+)' depends on axioms: \[([^\]]*)\]")


def audited_axioms(build_output: str) -> dict[str, set[str]]:
    """Map each reported declaration to the axiom set it depends on."""
    found: dict[str, set[str]] = {}
    for match in _AXIOM_LINE.finditer(build_output):
        declaration, raw = match.group(1), match.group(2)
        axioms = {item.strip() for item in raw.split(",") if item.strip()}
        found[declaration] = axioms
    return found


def check(build_output: str) -> list[str]:
    """Return a list of failure diagnostics; empty means the audit passed."""
    found = audited_axioms(build_output)
    errors: list[str] = []

    for declaration in REQUIRED_DECLARATIONS:
        if declaration not in found:
            errors.append(
                f"{declaration}: no '#print axioms' output found. "
                "The audit cannot be narrowed -- restore the line in formal/RoboCert/Audit.lean."
            )

    for declaration, axioms in sorted(found.items()):
        unexpected = axioms - ALLOWED_AXIOMS
        if unexpected:
            detail = ", ".join(sorted(unexpected))
            if "sorryAx" in unexpected:
                errors.append(
                    f"{declaration}: depends on sorryAx -- this theorem is NOT proved. "
                    "`sorry` is permitted only under formal/Statements/."
                )
            else:
                errors.append(
                    f"{declaration}: depends on unexpected axiom(s): {detail}. "
                    "New axioms require a documented change to "
                    "docs/architecture/trusted-computing-base.md."
                )
    return errors


def main() -> int:
    if not FORMAL_DIR.is_dir():
        print(f"check_lean_axioms: no formal/ directory at {FORMAL_DIR}", file=sys.stderr)
        return 2
    try:
        completed = subprocess.run(
            ["lake", "build"],
            cwd=FORMAL_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        print(
            "check_lean_axioms: `lake` not found on PATH. Install the pinned toolchain "
            "with elan; see formal/README.md.",
            file=sys.stderr,
        )
        return 2

    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        print(output, file=sys.stderr)
        print("check_lean_axioms: lake build failed", file=sys.stderr)
        return 1

    errors = check(output)
    if errors:
        for error in errors:
            print(f"check_lean_axioms: {error}", file=sys.stderr)
        return 1

    for declaration in REQUIRED_DECLARATIONS:
        print(f"check_lean_axioms: {declaration} OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
