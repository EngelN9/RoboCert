"""Prepare the frozen, blinded RC-002 verification-only run.

The source-to-blind-label map is intentionally written outside the repository.
This script never edits either source proof and refuses to overwrite a differing
run artifact.

LIMITATION -- this prepares a TWO-source run only, and a repaired RUN002 needs more.
`source_specs` in `prepare()` names exactly two proofs, `_load_or_create_private_map`
requires the blind-label set to be exactly {"P1", "P2"}, and the label assignment is a
two-way coin flip (`secrets.randbelow(2)`). RC-002's repaired package additionally carries
`research/proofs/rc002-frozen-task-corrigendum-2026-08-24.md`, so it cannot be frozen here
as things stand.

The fix is deliberately NOT written yet, because the blocking question is not mechanical:
does the corrigendum merge into the P1/P2 packets, or take a third blind label? That choice
affects audit validity, and it needs the project owner's read of the corrigendum first --
which per research/CLAIMS.md RC-002 has not happened. Generalizing beforehand would be
scaffolding for a run whose shape is not settled.

Whichever way it goes, note that this tool is frozen on BENCHMARK.md §24 terms: it pins
BENCHMARK_VERSION and RUN001 was prepared at 0.2.0, so changing preparation semantics needs
a version bump and a comparability note, not just an edit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_RUN_ID = "RCMPVB-20260821-CROSS-X-RUN001"
BENCHMARK_VERSION = "0.2.0"
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
NEUTRAL_HEADER = (
    "# Candidate proof\n\n"
    "This candidate addresses the frozen theorem in `task.md`. "
    "Audit only its mathematical content.\n\n"
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != data:
            raise RuntimeError(f"refusing to overwrite differing artifact: {path}")
        return
    path.write_bytes(data)


def _selected_body(text: str, start_marker: str, end_marker: str | None) -> tuple[str, int, int]:
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(start_marker))
    if end_marker is None:
        end = len(lines)
    else:
        end = next(
            index
            for index, line in enumerate(lines[start + 1 :], start + 1)
            if line.startswith(end_marker)
        )
    body = "\n".join(lines[start:end]).rstrip() + "\n"
    return body, start + 1, end


def _load_or_create_private_map(
    private_path: Path,
    run_id: str,
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if private_path.exists():
        loaded = json.loads(private_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise RuntimeError("private mapping must be a JSON object")
        if loaded.get("run_id") != run_id:
            raise RuntimeError("private mapping run_id mismatch")
        blind_labels = loaded.get("blind_labels")
        if not isinstance(blind_labels, dict) or set(blind_labels) != {"P1", "P2"}:
            raise RuntimeError("private mapping must contain exactly P1 and P2")
        if set(blind_labels.values()) != set(sources):
            raise RuntimeError("private mapping source aliases do not match current sources")
        recorded_sources = loaded.get("sources")
        if not isinstance(recorded_sources, dict):
            raise RuntimeError("private mapping sources must be a JSON object")
        for alias, source in sources.items():
            recorded = recorded_sources.get(alias, {})
            if not isinstance(recorded, dict):
                raise RuntimeError(f"private mapping source entry is invalid: {alias}")
            if recorded.get("source_document_sha256") != source["source_document_sha256"]:
                raise RuntimeError(f"private mapping source hash mismatch: {alias}")
            if recorded.get("source_line_range") != source["source_line_range"]:
                raise RuntimeError(f"private mapping source range mismatch: {alias}")
        return loaded

    keys = tuple(sources)
    coin = secrets.randbelow(2)
    ordered = keys if coin == 0 else tuple(reversed(keys))
    mapping = {
        "run_id": run_id,
        "warning": "PRIVATE UNTIL BOTH BLIND AUDITS ARE FROZEN",
        "coin_flip": coin,
        "blind_labels": {
            "P1": ordered[0],
            "P2": ordered[1],
        },
        "sources": {
            alias: {
                "repository_path": str(source["path"]),
                "source_document_sha256": source["source_document_sha256"],
                "source_line_range": source["source_line_range"],
            }
            for alias, source in sources.items()
        },
    }
    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_text(
        json.dumps(mapping, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return mapping


def prepare(repo_root: Path, run_id: str, run_dir: Path, private_map_path: Path) -> Path:
    """Prepare one new or byte-identical run without modifying source proofs."""

    repo_root = repo_root.resolve()
    run_dir = run_dir.resolve()
    private_map_path = private_map_path.resolve()
    if RUN_ID_RE.fullmatch(run_id) is None:
        raise ValueError("run_id must contain only letters, digits, dots, underscores, and hyphens")
    if run_dir.name != run_id:
        raise ValueError(f"run directory must be named {run_id}")
    benchmark_root = repo_root / "benchmarks" / "proof-verification"
    source_specs = (
        (
            "source-7f3a",
            repo_root / "research" / "proofs" / "planar-2r-exact-witness-proof-p1.md",
            "## Theorem",
            None,
        ),
        (
            "source-c91d",
            repo_root / "research" / "proofs" / "planar-2r-exact-witness-proof-p2.md",
            "## 1. Data, hypotheses, and the geometric problem",
            "## 11. Soundness and relative completeness",
        ),
    )

    sources: dict[str, dict[str, Any]] = {}
    for alias, path, start_marker, end_marker in source_specs:
        raw = path.read_bytes()
        body, first_line, last_line = _selected_body(raw.decode("utf-8"), start_marker, end_marker)
        sources[alias] = {
            "path": path,
            "source_document_sha256": _sha256(raw),
            "selected_body": body,
            "selected_body_sha256": _sha256(body.encode("utf-8")),
            "source_line_range": f"{first_line}-{last_line}",
        }

    private_map = _load_or_create_private_map(private_map_path, run_id, sources)

    version = (benchmark_root / "VERSION").read_text(encoding="utf-8").strip()
    if version != BENCHMARK_VERSION:
        raise RuntimeError(f"benchmark VERSION is {version!r}, expected {BENCHMARK_VERSION!r}")

    frozen_sources = {
        "task.md": benchmark_root / "items" / "public" / "RC-002" / "task.md",
        "ledger-prompt-v2.md": benchmark_root / "prompts" / "ledger-v2.md",
        "blind-audit-prompt-v2.md": benchmark_root / "prompts" / "blind-audit-v2.md",
        "adjudication-prompt-v2.md": benchmark_root / "prompts" / "adjudication-v2.md",
        "claude-handoff-rules-v2.md": benchmark_root / "prompts" / "claude-handoff-v2.md",
    }
    for destination_name, source_path in frozen_sources.items():
        _write_new(run_dir / "frozen" / destination_name, source_path.read_bytes())
    _write_new(run_dir / "frozen" / "VERSION", b"0.2.0\n")

    transform_entries: list[dict[str, Any]] = []
    for blind_label, alias in private_map["blind_labels"].items():
        source = sources[alias]
        packet = (NEUTRAL_HEADER + source["selected_body"]).encode("utf-8")
        destination = run_dir / "inputs" / f"proof-{blind_label.lower()}.md"
        _write_new(destination, packet)
        transform_entries.append(
            {
                "blind_label": blind_label,
                "source_alias": alias,
                "source_document_sha256": source["source_document_sha256"],
                "source_line_range": source["source_line_range"],
                "selected_body_sha256": source["selected_body_sha256"],
                "blinded_packet_sha256": _sha256(packet),
                "transformations": [
                    "selected declared RC-002 core line range",
                    "removed source title and attribution-bearing preamble",
                    "prepended the common neutral header",
                    "performed no mathematical-symbol normalization",
                ],
            }
        )
    _write_new(
        run_dir / "transformation-manifest.json",
        (
            json.dumps(
                {
                    "run_id": run_id,
                    "mapping_status": "withheld_outside_repository",
                    "entries": sorted(transform_entries, key=lambda item: item["blind_label"]),
                    "residual_leakage": [
                        "authorial prose style remains visible",
                        "section numbering and proof length remain visible",
                        "notation was not normalized because doing so could change semantics",
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8"),
    )

    task = (run_dir / "frozen" / "task.md").read_text(encoding="utf-8")
    ledger_prompt = (run_dir / "frozen" / "ledger-prompt-v2.md").read_text(encoding="utf-8")
    ledger_packet = (
        "# Session L — theorem intake packet\n\n"
        "Execution condition: fresh context, no tools, no repository access, and no prior "
        "proof or audit text. Return the complete observable response only.\n\n"
        "## Frozen instructions\n\n"
        f"{ledger_prompt.rstrip()}\n\n"
        "## Frozen theorem\n\n"
        f"{task.rstrip()}\n"
    )
    _write_new(
        run_dir / "handoff" / "claude-ledger-packet.md",
        ledger_packet.encode("utf-8"),
    )

    metadata = (
        f"""run_id: {run_id}
benchmark: RC-MPVB
benchmark_version: {BENCHMARK_VERSION}
item_id: RC-002
track: X
run_scope: verification_only
run_state: ledger_codex_pending
scoring_enabled: false
gold_defect_inventory: none
model_ranking: none
codex_model: pending_execution_metadata
codex_reasoning_effort: pending_execution_metadata
codex_context: pending_fresh_session
codex_tool_access: pending_execution_metadata
codex_tool_hard_disable: pending_execution_metadata
claude_model: pending_user_report
pre_run_pytest_baseline: pending_execution_metadata
rc002_tier_at_start: E1
implementation_correspondence: pending_final_gate_confirmation
"""
        "benchmark_spec_inconsistency: BENCHMARK.md_header_and_changelog_are_0.2.0_"
        "but_section_32_example_says_0.1.0\n"
        """private_mapping_location: outside_repository_under_system_temp
source_mapping_disclosure: withheld_until_both_blind_audits_frozen
"""
    )
    _write_new(run_dir / "metadata.yaml", metadata.encode("utf-8"))

    scores = {
        "benchmark_version": BENCHMARK_VERSION,
        "run_id": run_id,
        "item_id": "RC-002",
        "track": "X",
        "run_scope": "verification_only",
        "scoring_status": "not_applicable_no_gold_or_calibration_set",
        "generation_score": None,
        "audit_score": None,
        "repair_score": None,
        "final_score": None,
        "overall_score": None,
        "fatal_defects": None,
        "substantive_defects": None,
        "minor_defects": None,
        "expository_defects": None,
    }
    _write_new(
        run_dir / "scores.json",
        (json.dumps(scores, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )

    readme = f"""# {run_id}

This is a single-item, verification-only RC-002 cross-provider run under
RC-MPVB v0.2.0 and the v2 cross-verification protocol. It is not a scored
dataset run and supplies no model ranking.

Current state: `ledger_codex_pending`.

The original candidate proofs remain unchanged. Run-local P1/P2 labels were
assigned by a cryptographic random coin flip. The mapping is stored outside the
repository and must not be disclosed until both blind audits are frozen.

The next external checkpoint is `handoff/claude-ledger-packet.md`. It must be
run in a fresh, tool-free conversation. Return the complete observable ledger
response plus exact model/version and execution metadata; do not return hidden
chain-of-thought.

RC-002 remains E1. No run artifact may be interpreted as E2 before the union
ledger, both cross-provider blind audits, negation control, final independent
adjudications, implementation-correspondence gate, and run validation all pass.
"""
    _write_new(run_dir / "README.md", readme.encode("utf-8"))
    _write_new(
        run_dir / "reconciliation.md",
        (
            "# Reconciliation\n\nStatus: `NOT_STARTED` — both ledger outputs are required first.\n"
        ).encode(),
    )
    _write_new(
        run_dir / "outputs" / "README.md",
        b"# Frozen outputs\n\nNo stage output is accepted until stored verbatim and hash-bound.\n",
    )
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare a new, blinded RC-002 verification-only run without overwrites."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="RoboCert repository root (default: inferred from this script)",
    )
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="run artifact directory (default: benchmarks/proof-verification/runs/<run-id>)",
    )
    parser.add_argument(
        "--private-map",
        type=Path,
        help="private P1/P2 map file outside the repository (default: system temp)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_id = str(args.run_id)
    run_dir = (
        args.run_dir.resolve()
        if args.run_dir is not None
        else repo_root / "benchmarks" / "proof-verification" / "runs" / run_id
    )
    private_map_path = (
        args.private_map.resolve()
        if args.private_map is not None
        else Path(tempfile.gettempdir()) / "robocert-rcmpvb-private" / f"{run_id}-blinding-map.json"
    )
    try:
        run_dir = prepare(repo_root, run_id, run_dir, private_map_path)
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f"ERROR: {error}\n")
    print(f"prepared {run_dir}")
    print(f"private blinding map: {private_map_path}")


if __name__ == "__main__":
    main()
