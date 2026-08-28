#!/usr/bin/env python3
"""Stop-hook reminder for research/CLAIMS.md.

Unlike check_ledger.py's PostToolUse hook (which blocks a bad edit the moment it
happens, so an invalid ledger state should never actually be reachable at session
end), this is deliberately non-blocking: it re-runs the same checks and prints a
summary, but always exits 0 so it never prevents a session from stopping. Its job is
visibility ("here's what changed and its current state"), not enforcement --
enforcement already happened at edit time.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LEDGER_PATH = Path("research/CLAIMS.md")


def ledger_changed_this_session() -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", LEDGER_PATH.as_posix()],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return bool(result.stdout.strip())


def main() -> int:
    if not LEDGER_PATH.exists() or not ledger_changed_this_session():
        return 0  # nothing to report

    result = subprocess.run(
        [sys.executable, "scripts/check_ledger.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print(f"session reminder: {LEDGER_PATH} changed this session and is valid.")
    else:
        print(
            f"session reminder: {LEDGER_PATH} changed this session. "
            f"(This should be unreachable -- check_ledger.py already blocks invalid "
            f"edits at write time. Reporting anyway, not blocking session end.)"
        )
        print(result.stderr, end="")
    return 0  # always non-blocking


if __name__ == "__main__":
    sys.exit(main())
