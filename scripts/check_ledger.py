#!/usr/bin/env python3
"""Ledger integrity check for research/CLAIMS.md.

Enforces, as a hook rather than a convention (research/README.md rule 3):

  (a) monotonicity  - a claim's tier rank may not exceed the minimum tier rank
                       of its dependencies
  (b) acyclicity    - the `depends` graph must be a DAG
  (c) no orphans    - every `depends` reference must point at an entry that exists
  (d) referee gate  - tier E2 or above requires a non-"none" `referee:` field
  (e) history gate  - a `tier:` change must be accompanied by a new `history:` line,
                       checked against the last committed version when available

Stdlib only, no dependencies. Exit 0 on a clean ledger, exit 1 with all violations
printed to stderr otherwise.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

LEDGER_PATH = Path("research/CLAIMS.md")

# Monotonicity order. EX (refuted) is deliberately excluded: nothing may depend on a
# refuted claim, regardless of ranking.
TIER_RANK = {"E0": 0, "E1": 1, "E2": 2, "E4": 3, "E3": 4}

ENTRY_HEADER_RE = re.compile(r"^##\s+(RC-\d+)\s*$")
FIELD_RE = re.compile(r"^(statement|tier|depends|proof|target_checker|referee|history):\s*(.*)$")
DEPENDS_ID_RE = re.compile(r"RC-\d+")
HISTORY_ITEM_RE = re.compile(r"^\s*-\s+.+$")


class LedgerError(Exception):
    pass


def parse_ledger(text: str) -> dict[str, dict]:
    """Parse research/CLAIMS.md into {id: {tier, depends, referee, history, ...}}."""
    entries: dict[str, dict] = {}
    current_id = None
    current_field = None
    lines = text.splitlines()

    for raw_line in lines:
        header_match = ENTRY_HEADER_RE.match(raw_line)
        if header_match:
            current_id = header_match.group(1)
            if current_id in entries:
                raise LedgerError(f"duplicate entry id {current_id}")
            entries[current_id] = {
                "statement": "",
                "tier": None,
                "depends": [],
                "proof": "",
                "target_checker": "",
                "referee": None,
                "history": [],
            }
            current_field = None
            continue

        if current_id is None:
            continue  # preamble / schema doc before the first entry

        field_match = FIELD_RE.match(raw_line)
        if field_match:
            current_field = field_match.group(1)
            value = field_match.group(2).strip()
            entry = entries[current_id]
            if current_field == "tier":
                entry["tier"] = value
            elif current_field == "depends":
                entry["depends"] = DEPENDS_ID_RE.findall(value)
            elif current_field == "referee":
                entry["referee"] = value
            elif current_field == "history":
                if value:
                    entry["history"].append(value)
            else:
                entry[current_field] = value
            continue

        if current_field == "history" and HISTORY_ITEM_RE.match(raw_line):
            entries[current_id]["history"].append(raw_line.strip())
            continue

        if current_field == "statement" and raw_line.strip():
            entries[current_id]["statement"] += " " + raw_line.strip()

    return entries


def check_monotonicity(entries: dict[str, dict]) -> list[str]:
    errors = []
    for entry_id, entry in entries.items():
        tier = entry["tier"]
        if tier == "EX" or tier is None:
            continue
        if tier not in TIER_RANK:
            errors.append(f"{entry_id}: unknown tier {tier!r}")
            continue
        for dep_id in entry["depends"]:
            dep = entries.get(dep_id)
            if dep is None:
                continue  # reported by check_orphans
            dep_tier = dep["tier"]
            if dep_tier == "EX":
                errors.append(
                    f"{entry_id}: depends on refuted claim {dep_id} (tier EX) "
                    f"-- a claim may not depend on a refuted result"
                )
                continue
            if dep_tier not in TIER_RANK:
                continue  # reported separately
            if TIER_RANK[tier] > TIER_RANK[dep_tier]:
                errors.append(
                    f"{entry_id}: tier {tier} exceeds dependency {dep_id}'s tier "
                    f"{dep_tier} -- monotonicity violation "
                    f"(research/README.md 'The monotonicity rule')"
                )
    return errors


def check_orphans(entries: dict[str, dict]) -> list[str]:
    errors = []
    for entry_id, entry in entries.items():
        for dep_id in entry["depends"]:
            if dep_id not in entries:
                errors.append(f"{entry_id}: depends on nonexistent entry {dep_id}")
    return errors


def check_acyclic(entries: dict[str, dict]) -> list[str]:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {entry_id: WHITE for entry_id in entries}
    errors = []

    def visit(node: str, stack: list[str]) -> None:
        color[node] = GRAY
        stack.append(node)
        for dep_id in entries[node]["depends"]:
            if dep_id not in entries:
                continue  # reported by check_orphans
            if color[dep_id] == GRAY:
                cycle = " -> ".join([*stack[stack.index(dep_id) :], dep_id])
                errors.append(f"dependency cycle: {cycle}")
            elif color[dep_id] == WHITE:
                visit(dep_id, stack)
        stack.pop()
        color[node] = BLACK

    for entry_id in entries:
        if color[entry_id] == WHITE:
            visit(entry_id, [])
    return errors


def check_referee_gate(entries: dict[str, dict]) -> list[str]:
    errors = []
    for entry_id, entry in entries.items():
        tier = entry["tier"]
        if tier in ("E2", "E3") and (entry["referee"] in (None, "none", "")):
            errors.append(f"{entry_id}: tier {tier} requires a non-'none' referee: field")
    return errors


def previous_ledger_text() -> str | None:
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{LEDGER_PATH.as_posix()}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError:
        return None  # git not available
    if result.returncode != 0:
        return None  # no HEAD, or file not tracked yet
    return result.stdout


def check_history_gate(entries: dict[str, dict]) -> list[str]:
    old_text = previous_ledger_text()
    if old_text is None:
        return []  # nothing to diff against yet (first commit) -- not an error
    old_entries = parse_ledger(old_text)
    errors = []
    for entry_id, entry in entries.items():
        old_entry = old_entries.get(entry_id)
        if old_entry is None:
            continue  # brand-new entry, no prior tier to compare
        if entry["tier"] != old_entry["tier"] and len(entry["history"]) <= len(
            old_entry["history"]
        ):
            errors.append(
                f"{entry_id}: tier changed ({old_entry['tier']} -> "
                f"{entry['tier']}) without an appended history: line"
            )
    return errors


def main() -> int:
    if not LEDGER_PATH.exists():
        print(f"check_ledger: {LEDGER_PATH} not found, nothing to check")
        return 0

    text = LEDGER_PATH.read_text(encoding="utf-8")
    try:
        entries = parse_ledger(text)
    except LedgerError as exc:
        print(f"check_ledger: parse error: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    errors += check_orphans(entries)
    errors += check_acyclic(entries)
    errors += check_monotonicity(entries)
    errors += check_referee_gate(entries)
    errors += check_history_gate(entries)

    if errors:
        print(f"check_ledger: {len(errors)} violation(s) in {LEDGER_PATH}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"check_ledger: {LEDGER_PATH} OK ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
