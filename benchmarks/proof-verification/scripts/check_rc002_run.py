"""Validate the frozen RC-002 cross-verification run and its SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_RUN_ID = "RCMPVB-20260821-CROSS-X-RUN001"
EXPECTED_VERSION = "0.2.0"
MANIFEST_NAME = "manifest.sha256"
REQUIRED_ALWAYS = {
    "README.md",
    "frozen/VERSION",
    "frozen/task.md",
    "frozen/ledger-prompt-v2.md",
    "frozen/blind-audit-prompt-v2.md",
    "frozen/adjudication-prompt-v2.md",
    "frozen/claude-handoff-rules-v2.md",
    "handoff/claude-ledger-packet.md",
    "inputs/proof-p1.md",
    "inputs/proof-p2.md",
    "metadata.yaml",
    "outputs/README.md",
    "reconciliation.md",
    "scores.json",
    "transformation-manifest.json",
}
REQUIRED_STOPPED = {
    "handoff/claude-audit-p1-packet.md",
    "handoff/claude-audit-p2-packet.md",
    "outputs/ledger-claude.md",
    "outputs/ledger-claude-metadata.json",
    "outputs/ledger-union.md",
    "outputs/audit-p1-codex.md",
    "outputs/audit-p1-codex-metadata.json",
    "outputs/audit-p2-codex.md",
    "outputs/audit-p2-codex-metadata.json",
    "outputs/claude-audit-attempts.md",
}
FORBIDDEN_PACKET_STRINGS = (
    "rigorous soundness proof for the planar-2r exact-witness polynomial encoding",
    "the exact-witness polynomial encoding for the planar 2r arm",
    "a self-contained proof",
    "planar-2r-exact-witness-proof-p1.md",
    "planar-2r-exact-witness-proof-p2.md",
    "anthropic",
    "openai",
    "chatgpt",
    "claude",
    "known weakness",
    "where this argument is weakest",
)
NEUTRAL_PREFIX = (
    "# Candidate proof\n\n"
    "This candidate addresses the frozen theorem in `task.md`. "
    "Audit only its mathematical content.\n\n"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metadata(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def _artifact_paths(run_dir: Path) -> list[Path]:
    return sorted(
        (path for path in run_dir.rglob("*") if path.is_file() and path.name != MANIFEST_NAME),
        key=lambda path: path.relative_to(run_dir).as_posix(),
    )


def _manifest_content(run_dir: Path) -> str:
    lines = [
        f"{_sha256(path)}  {path.relative_to(run_dir).as_posix()}"
        for path in _artifact_paths(run_dir)
    ]
    return "\n".join(lines) + "\n"


def write_manifest(run_dir: Path) -> None:
    """Write an active run manifest, refusing every stopped-run write request."""

    metadata_path = run_dir / "metadata.yaml"
    if metadata_path.is_file():
        state = _metadata(metadata_path).get("run_state", "")
        if state.startswith("stopped_"):
            raise RuntimeError(f"refusing to rewrite manifest for stopped run: {run_dir.name}")

    manifest_path = run_dir / MANIFEST_NAME
    content = _manifest_content(run_dir)
    if manifest_path.is_file() and manifest_path.read_text(encoding="utf-8") == content:
        return
    manifest_path.write_text(content, encoding="utf-8", newline="\n")


def _validate_manifest(run_dir: Path, errors: list[str]) -> None:
    manifest_path = run_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        errors.append(f"missing {MANIFEST_NAME}")
        return
    observed: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, separator, relative = line.partition("  ")
        if not separator or len(digest) != 64:
            errors.append(f"malformed manifest line: {line!r}")
            continue
        observed[relative] = digest
    expected_paths = {
        path.relative_to(run_dir).as_posix(): path for path in _artifact_paths(run_dir)
    }
    if set(observed) != set(expected_paths):
        errors.append("manifest file set does not equal the run artifact file set")
    for relative, path in expected_paths.items():
        if observed.get(relative) != _sha256(path):
            errors.append(f"hash mismatch: {relative}")


def validate(run_dir: Path, expected_run_id: str | None = None) -> list[str]:
    expected_run_id = expected_run_id or run_dir.name
    errors: list[str] = []
    if run_dir.name != expected_run_id:
        errors.append(f"run directory must be named {expected_run_id}")
    for relative in sorted(REQUIRED_ALWAYS):
        if not (run_dir / relative).is_file():
            errors.append(f"missing required artifact: {relative}")

    metadata_path = run_dir / "metadata.yaml"
    if metadata_path.is_file():
        metadata = _metadata(metadata_path)
        if metadata.get("run_id") != expected_run_id:
            errors.append("metadata run_id mismatch")
        if metadata.get("benchmark_version") != EXPECTED_VERSION:
            errors.append("metadata benchmark_version mismatch")
        if metadata.get("run_scope") != "verification_only":
            errors.append("run must remain verification_only")
        if metadata.get("scoring_enabled") != "false":
            errors.append("scoring must remain disabled")
        state = metadata.get("run_state")
        if state == "awaiting_claude_ledger":
            if not (run_dir / "outputs" / "ledger-codex.md").is_file():
                errors.append("awaiting_claude_ledger requires outputs/ledger-codex.md")
            if not (run_dir / "outputs" / "ledger-codex-metadata.json").is_file():
                errors.append("awaiting_claude_ledger requires outputs/ledger-codex-metadata.json")
        elif state == "stopped_substantive_and_claude_audits_blocked":
            for relative in sorted(REQUIRED_STOPPED):
                if not (run_dir / relative).is_file():
                    errors.append(f"stopped run is missing required artifact: {relative}")
            if metadata.get("rc002_tier_at_end") != "E1":
                errors.append("stopped run must retain RC-002 at E1")
            if metadata.get("source_mapping_disclosure") != (
                "withheld_until_both_blind_audits_frozen"
            ):
                errors.append("stopped run must keep the private mapping withheld")
        elif state != "ledger_codex_pending":
            errors.append(f"unsupported run_state at this checkpoint: {state!r}")

    version_path = run_dir / "frozen" / "VERSION"
    if (
        version_path.is_file()
        and version_path.read_text(encoding="utf-8").strip() != EXPECTED_VERSION
    ):
        errors.append("frozen VERSION mismatch")

    scores_path = run_dir / "scores.json"
    if scores_path.is_file():
        scores = json.loads(scores_path.read_text(encoding="utf-8"))
        if scores.get("run_id") != expected_run_id:
            errors.append("scores.json run_id mismatch")
        if scores.get("run_scope") != "verification_only":
            errors.append("scores.json must say verification_only")
        if scores.get("scoring_status") != "not_applicable_no_gold_or_calibration_set":
            errors.append("scores.json scoring status is not null-run status")
        for key, value in scores.items():
            if key.endswith("_score") and value is not None:
                errors.append(f"scores.json {key} must be null")
            if key.endswith("_defects") and value is not None:
                errors.append(f"scores.json {key} must be null")

    ledger_metadata_path = run_dir / "outputs" / "ledger-codex-metadata.json"
    ledger_output_path = run_dir / "outputs" / "ledger-codex.md"
    if ledger_metadata_path.is_file() and ledger_output_path.is_file():
        ledger_metadata = json.loads(ledger_metadata_path.read_text(encoding="utf-8"))
        if ledger_metadata.get("observable_output_sha256") != _sha256(ledger_output_path):
            errors.append("Codex ledger output hash does not match its metadata")
        if ledger_metadata.get("context_forked") is not False:
            errors.append("Codex ledger metadata must record no context fork")

    for stem in ("ledger-claude", "audit-p1-codex", "audit-p2-codex"):
        metadata_path = run_dir / "outputs" / f"{stem}-metadata.json"
        output_path = run_dir / "outputs" / f"{stem}.md"
        if not metadata_path.is_file() or not output_path.is_file():
            continue
        output_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if output_metadata.get("observable_output_sha256") != _sha256(output_path):
            errors.append(f"{stem} output hash does not match its metadata")
        if output_metadata.get("fresh_context") is not True:
            errors.append(f"{stem} metadata must record a fresh context")
        if output_metadata.get("context_forked") is not False:
            errors.append(f"{stem} metadata must record no context fork")

    claude_metadata_path = run_dir / "outputs" / "ledger-claude-metadata.json"
    if claude_metadata_path.is_file():
        claude_metadata = json.loads(claude_metadata_path.read_text(encoding="utf-8"))
        if claude_metadata.get("tools_hard_disabled") is not True:
            errors.append("Claude ledger metadata must record hard-disabled tools")
        if claude_metadata.get("server_tool_use") != {
            "web_search_requests": 0,
            "web_fetch_requests": 0,
        }:
            errors.append("Claude ledger metadata records unexpected server tool use")

    proof_packets: list[str] = []
    for relative in ("inputs/proof-p1.md", "inputs/proof-p2.md"):
        path = run_dir / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        proof_packets.append(text)
        if not text.startswith(NEUTRAL_PREFIX):
            errors.append(f"{relative} does not use the common neutral header")
        lowered = text.lower()
        for forbidden in FORBIDDEN_PACKET_STRINGS:
            if forbidden in lowered:
                errors.append(f"{relative} leaks forbidden string: {forbidden}")
    if len(proof_packets) == 2 and proof_packets[0] == proof_packets[1]:
        errors.append("the two blinded proof packets are identical")

    ledger_packet = run_dir / "handoff" / "claude-ledger-packet.md"
    if ledger_packet.is_file():
        text = ledger_packet.read_text(encoding="utf-8").lower()
        if "# candidate proof" in text or "audit report" in text:
            errors.append("ledger packet contains proof or prior-audit material")

    for path in _artifact_paths(run_dir):
        relative = path.relative_to(run_dir).as_posix()
        if relative.startswith("handoff/") and "audit" in relative:
            text = path.read_text(encoding="utf-8")
            proof_markers = text.count("# Candidate proof")
            if proof_markers != 1:
                errors.append(f"{relative} must contain exactly one proof packet")

    transform_path = run_dir / "transformation-manifest.json"
    if transform_path.is_file():
        transform = json.loads(transform_path.read_text(encoding="utf-8"))
        if transform.get("run_id") != expected_run_id:
            errors.append("transformation manifest run_id mismatch")
        if transform.get("mapping_status") != "withheld_outside_repository":
            errors.append("source mapping was not marked as withheld")
        entries = transform.get("entries", [])
        if {entry.get("blind_label") for entry in entries} != {"P1", "P2"}:
            errors.append("transformation manifest lacks exactly P1 and P2")
        for entry in entries:
            for key in (
                "source_document_sha256",
                "selected_body_sha256",
                "blinded_packet_sha256",
                "source_line_range",
            ):
                if not entry.get(key):
                    errors.append(f"transformation entry lacks {key}")
            label = str(entry.get("blind_label", "")).lower()
            proof_path = run_dir / "inputs" / f"proof-{label}.md"
            if proof_path.is_file() and entry.get("blinded_packet_sha256") != _sha256(proof_path):
                errors.append(f"transformation hash mismatch for proof-{label}.md")

    _validate_manifest(run_dir, errors)
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate one or all frozen RC-002 runs without modifying artifacts."
    )
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--all-runs", action="store_true")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    runs_root = repo_root / "benchmarks" / "proof-verification" / "runs"

    if args.all_runs and (args.run_id is not None or args.run_dir is not None):
        parser.error("--all-runs cannot be combined with --run-id or --run-dir")
    if args.all_runs:
        targets = [(path, path.name) for path in sorted(runs_root.iterdir()) if path.is_dir()]
        if not targets:
            parser.exit(1, f"ERROR: no run directories found under {runs_root}\n")
    else:
        expected_run_id = args.run_id or (
            args.run_dir.name if args.run_dir is not None else DEFAULT_RUN_ID
        )
        run_dir = (
            args.run_dir.resolve() if args.run_dir is not None else runs_root / expected_run_id
        )
        targets = [(run_dir, expected_run_id)]

    failed = False
    for run_dir, expected_run_id in targets:
        if args.write_manifest:
            try:
                write_manifest(run_dir)
            except (OSError, RuntimeError) as error:
                failed = True
                print(f"ERROR [{expected_run_id}]: {error}")
                continue
        errors = validate(run_dir, expected_run_id)
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR [{expected_run_id}]: {error}")
            continue
        print(f"OK: {expected_run_id} artifacts, isolation rules, and SHA-256 manifest")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
