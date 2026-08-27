#!/usr/bin/env python3
"""Guard against overclaiming language in research/reports/.

Blocks a write/edit under research/reports/ if it introduces certification or
completion language (AGENTS.md §36 "Avoid" list, §66 "No Overclaiming" list, plus
"QED" / "we have proved") in a paragraph that does not also cite a
research/CLAIMS.md entry at tier E2 or above, or a real CheckedCertificate.

Heuristic, not NLP -- false positives are the acceptable failure mode (see
research/reports/README.md and the manuals this project adapts: hooks execute
deterministically and cannot be rationalized around, unlike a written-only rule).

Usable two ways:
  - as a Claude Code PreToolUse hook: reads the hook JSON payload from stdin,
    exits 2 (block) on a violation, 0 otherwise.
  - standalone, for testing: `check_report_language.py <path-to-markdown-file>`,
    same exit codes, human-readable output either way.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CLAIMS_PATH = Path("research/CLAIMS.md")
REPORTS_PREFIX = "research/reports/"

# AGENTS.md §36 "Avoid" -- vague unless qualified.
VAGUE_TERMS = [
    "safe",
    "reachable",
    "singularity-free",
    "exact",
    "verified",
    "robust",
    "guaranteed",
]

# AGENTS.md §66 "No Overclaiming", plus completion phrases from the source manuals.
OVERCLAIM_PHRASES = [
    "100% safe",
    "guaranteed in reality",
    "proof that the robot can never collide",
    "formally verified hardware",
    "certified for all manufacturing errors",
    "qed",
    "we have proved",
    "we have shown",
    "this proves",
]

QUALIFIER_HINT_RE = re.compile(
    r"\bwith clearance\b|\bunder\b.*\btheta\b|\bfor all\b|\bchecker\b|\bcertificate\b",
    re.IGNORECASE,
)
RC_ID_RE = re.compile(r"RC-\d+")
CHECKED_CERT_RE = re.compile(r"CheckedCertificate", re.IGNORECASE)

TIER_RANK = {"E0": 0, "E1": 1, "E2": 2, "E4": 3, "E3": 4}
ENTRY_HEADER_RE = re.compile(r"^##\s+(RC-\d+)\s*$")
TIER_FIELD_RE = re.compile(r"^tier:\s*(\S+)")


def load_claim_tiers() -> dict[str, str]:
    if not CLAIMS_PATH.exists():
        return {}
    tiers: dict[str, str] = {}
    current_id = None
    for line in CLAIMS_PATH.read_text(encoding="utf-8").splitlines():
        header_match = ENTRY_HEADER_RE.match(line)
        if header_match:
            current_id = header_match.group(1)
            continue
        if current_id is not None:
            tier_match = TIER_FIELD_RE.match(line)
            if tier_match:
                tiers[current_id] = tier_match.group(1)
                current_id = None  # only need the first tier: line per entry
    return tiers


def paragraph_has_qualifying_citation(paragraph: str, claim_tiers: dict[str, str]) -> bool:
    if CHECKED_CERT_RE.search(paragraph):
        return True
    for rc_id in RC_ID_RE.findall(paragraph):
        tier = claim_tiers.get(rc_id)
        if tier in TIER_RANK and TIER_RANK[tier] >= TIER_RANK["E2"]:
            return True
    return False


def find_violations(content: str, claim_tiers: dict[str, str]) -> list[str]:
    violations = []
    paragraphs = re.split(r"\n\s*\n", content)
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        lowered = paragraph.lower()

        hit_phrases = [p for p in OVERCLAIM_PHRASES if p in lowered]
        hit_vague = [
            term
            for term in VAGUE_TERMS
            if re.search(rf"\b{re.escape(term)}\b", lowered)
            and not QUALIFIER_HINT_RE.search(paragraph)
        ]
        hits = hit_phrases + hit_vague
        if not hits:
            continue
        if paragraph_has_qualifying_citation(paragraph, claim_tiers):
            continue

        excerpt = paragraph.strip().replace("\n", " ")
        if len(excerpt) > 160:
            excerpt = excerpt[:157] + "..."
        violations.append(
            f"flagged term(s) {hits} with no qualifying RC-xxx (tier E2+) or "
            f'CheckedCertificate citation in paragraph: "{excerpt}"'
        )
    return violations


def extract_hook_payload() -> tuple[str, str] | None:
    """Returns (file_path, new_content) from a Claude Code PreToolUse JSON payload, or None."""
    if sys.stdin.isatty():
        return None
    raw = sys.stdin.read()
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if "content" in tool_input:
        content = tool_input["content"]
    elif "new_string" in tool_input:
        content = tool_input["new_string"]
    else:
        content = ""
    return file_path, content


def main() -> int:
    if len(sys.argv) > 1:
        # Standalone/test mode: never touch stdin, so this can't block waiting
        # for EOF on a stdin that's open but idle (e.g. under a shell harness).
        file_path = sys.argv[1]
        content = Path(file_path).read_text(encoding="utf-8")
    else:
        hook_payload = extract_hook_payload()
        if hook_payload is None:
            print(
                "check_report_language: no input (expected hook JSON on stdin or a file path arg)"
            )
            return 0
        file_path, content = hook_payload

    normalized_path = file_path.replace("\\", "/")
    if REPORTS_PREFIX not in normalized_path:
        return 0  # not a reports/ write, nothing to check

    claim_tiers = load_claim_tiers()
    violations = find_violations(content, claim_tiers)

    if violations:
        print(f"check_report_language: blocked write to {file_path}:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 2  # PreToolUse: exit 2 blocks the tool call in Claude Code

    print(f"check_report_language: {file_path} OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
