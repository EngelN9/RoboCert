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
2. **Every pending or attested supported system with a runnable toolchain is actually
   compiled**, and its assumptions/oracles are extracted with a planted positive control.
3. **Every pending or attested supported system without a toolchain is reported and skipped.**
   Nothing is invented. `--require SYSTEM` makes that skip a hard failure and forces the same
   re-run even after the system has moved out of `pending_systems`.
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
import re
import shutil
import subprocess
import sys
import tempfile
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


class AxiomExtractionError(RuntimeError):
    """The axiom extractor could not establish an answer, so it refuses to give one.

    Every path that cannot produce a positively-recognised result raises this. There is no
    branch returning an empty list as a fallback: `[]` means "the kernel said Closed under the
    global context", never "the parser did not understand the output". That distinction is the
    whole point -- a build failure is loud, but a silently empty axiom list would fail OPEN,
    writing an attestation asserting a proof depends on nothing.
    """


#: `Print Assumptions` reports assumptions under these headings. Anything else is unrecognised
#: output, which raises rather than being skipped.
_ASSUMPTION_SECTIONS = frozenset({"Axioms:", "Parameters:", "Variables:"})
_CLOSED = "Closed under the global context"
_LEMMA_RE = re.compile(r"^Lemma\s+(\w+)", re.MULTILINE)
_ISABELLE_LEMMA_RE = re.compile(r"^lemma\s+(\w+)\s*:", re.MULTILINE)
_ISABELLE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_'.]*$")
ISABELLE_PLANTED_CONTROL = "robocert_planted_control"
ISABELLE_SKIP_PROOF = "Pure.skip_proof"


def rocq_lemma_names(statement_text: str) -> list[str]:
    """The declarations to audit, taken from the committed statement file.

    Deriving them from the statement text rather than a constant here means the audited set is
    bound by `statement_digest`: narrowing it requires editing a file whose digest the
    attestation record pins, which invalidates the attestation. `check_lean_axioms.py` gets the
    same property from a hardcoded `REQUIRED_DECLARATIONS` list; this route is stronger.
    """
    names = _LEMMA_RE.findall(statement_text)
    if not names:
        raise AxiomExtractionError(
            "no `Lemma <name>` declarations found in the Rocq statement file. An empty audit "
            "set is never the answer -- the file is unreadable, malformed, or has changed shape."
        )
    return names


def parse_print_assumptions(output: str) -> list[str]:
    """Parse ONE `Print Assumptions` result. Raises unless the output is positively recognised.

    Two shapes are accepted and nothing else: the closed form, and one or more assumption
    sections whose entries are `name` or `name : type`, with wrapped types indented onto
    following lines.
    """
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    if not lines:
        raise AxiomExtractionError("`Print Assumptions` produced no output at all")
    if len(lines) == 1 and lines[0].strip() == _CLOSED:
        return []

    names: list[str] = []
    section_seen = False
    for line in lines:
        stripped = line.strip()
        if stripped == _CLOSED:
            raise AxiomExtractionError(
                f"output mixes the closed form with other content:\n{output}"
            )
        if not line[:1].isspace():
            if stripped.endswith(":") and " " not in stripped:
                if stripped not in _ASSUMPTION_SECTIONS:
                    raise AxiomExtractionError(
                        f"unrecognised `Print Assumptions` section {stripped!r}. Refusing to "
                        f"guess whether it carries assumptions:\n{output}"
                    )
                section_seen = True
                continue
            if not section_seen:
                raise AxiomExtractionError(
                    f"`Print Assumptions` output does not start with a known section:\n{output}"
                )
            names.append(stripped.split(":")[0].split()[0])
        # An indented line continues the previous entry's type. Nothing to collect.
    if not section_seen or not names:
        raise AxiomExtractionError(f"could not recognise `Print Assumptions` output:\n{output}")
    return names


def _rocq_print_assumptions(source: Path, declaration: str, preamble: str = "") -> list[str]:
    """Run `Print Assumptions <declaration>` and parse exactly that one result.

    One invocation per declaration, deliberately. `Print Assumptions` does not echo the name it
    was asked about, so a single batched file would yield unlabelled blocks that could only be
    matched back by position -- an alignment assumption that fails silently the moment the
    toolchain emits anything extra. Five fast invocations have no such assumption.
    """
    command = _rocq_command()
    if command is None:
        raise AxiomExtractionError("no rocq/rocqc/coqc on PATH")
    body = f"{preamble}Print Assumptions {declaration}.\n"
    with tempfile.TemporaryDirectory(prefix="robocert-assumptions-") as directory:
        probe = Path(directory) / "Assumptions.v"
        probe.write_text(
            f"Require Import RoboCert.{source.stem}.\n{body}", encoding="utf-8", newline="\n"
        )
        argv = [*command, "-Q", str(source.parent), "RoboCert", str(probe)]
        code, output = _run(argv, cwd=FORMAL_DIR)
    if code != 0:
        raise AxiomExtractionError(f"`Print Assumptions {declaration}` failed:\n{output}")
    return parse_print_assumptions(output)


#: Declared and consumed by the positive control below. The name is distinctive so that seeing
#: it anywhere near a real attestation is unmistakable.
PLANTED_AXIOM = "robocert_planted_axiom"


def _rocq_extractor_self_check(source: Path) -> None:
    """Prove the extractor can see an axiom before trusting it to report none.

    A parser that cannot detect a DELIBERATELY axiom-dependent proof has not earned the right to
    report `[]` for a real one. This runs on the same binary, in the same job, immediately
    before the real declarations -- so a parser wrong about this toolchain's output format fails
    loudly here instead of quietly certifying five lemmas as assumption-free.
    """
    preamble = (
        f"Axiom {PLANTED_AXIOM} : False.\n"
        "Lemma planted_control : False.\n"
        f"Proof. exact {PLANTED_AXIOM}. Qed.\n"
    )
    found = _rocq_print_assumptions(source, "planted_control", preamble=preamble)
    if PLANTED_AXIOM not in found:
        raise AxiomExtractionError(
            f"positive control FAILED: a proof built on `{PLANTED_AXIOM}` was reported as "
            f"depending on {found}. The parser does not understand this toolchain's "
            "`Print Assumptions` output, so its verdict on the real declarations means nothing."
        )


def rocq_axioms(source: Path, statement_text: str) -> dict[str, list[str]]:
    """Axiom dependencies of every declaration the statement file names.

    Raises `AxiomExtractionError` unless the positive control passes AND every declaration
    yields a positively-recognised result.
    """
    _rocq_extractor_self_check(source)
    return {
        name: _rocq_print_assumptions(source, name) for name in rocq_lemma_names(statement_text)
    }


def isabelle_theorem_names(statement_text: str) -> list[str]:
    """The declarations to audit, derived from the digest-bound Isabelle statement file."""
    names = _ISABELLE_LEMMA_RE.findall(statement_text)
    if not names:
        raise AxiomExtractionError(
            "no `lemma <name>:` declarations found in the Isabelle statement file. An empty "
            "audit set is never accepted."
        )
    if len(names) != len(set(names)):
        raise AxiomExtractionError(
            f"duplicate theorem names in the Isabelle statement file: {names}"
        )
    return names


def parse_isabelle_oracles(output: str, theorem_names: Sequence[str]) -> dict[str, list[str]]:
    """Parse the temporary audit session's exact TSV protocol, failing closed on drift."""
    expected = {ISABELLE_PLANTED_CONTROL, *theorem_names}
    found: dict[str, list[str]] = {}
    if not output:
        raise AxiomExtractionError("Isabelle oracle audit produced no output file")

    for line_number, line in enumerate(output.splitlines(), start=1):
        fields = line.split("\t")
        if len(fields) != 2:
            raise AxiomExtractionError(
                f"malformed Isabelle oracle output at line {line_number}: {line!r}"
            )
        declaration, encoded = fields
        if declaration not in expected:
            raise AxiomExtractionError(
                f"unrecognised declaration in Isabelle oracle output: {declaration!r}"
            )
        if declaration in found:
            raise AxiomExtractionError(
                f"duplicate declaration in Isabelle oracle output: {declaration!r}"
            )
        names = [] if encoded == "" else encoded.split(",")
        if any(_ISABELLE_NAME_RE.fullmatch(name) is None for name in names):
            raise AxiomExtractionError(f"malformed oracle name(s) for {declaration!r}: {names!r}")
        if len(names) != len(set(names)):
            raise AxiomExtractionError(f"duplicate oracle name(s) for {declaration!r}: {names!r}")
        found[declaration] = sorted(names)

    missing = sorted(expected - set(found))
    if missing:
        raise AxiomExtractionError(
            f"Isabelle oracle output omitted required declaration(s): {missing}"
        )
    planted = found.pop(ISABELLE_PLANTED_CONTROL)
    if planted != [ISABELLE_SKIP_PROOF]:
        raise AxiomExtractionError(
            "positive control FAILED: the deliberately sorry-ed theorem must report exactly "
            f"{ISABELLE_SKIP_PROOF!r}, got {planted!r}"
        )
    return {name: found[name] for name in theorem_names}


def isabelle_oracles(session_dir: Path, statement_text: str) -> dict[str, list[str]]:
    """Extract theorem oracles in a temporary quick-and-dirty child session.

    The committed RoboCert session remains strict. Only this throwaway audit child enables
    `quick_and_dirty`, solely so a planted `sorry` theorem can prove that
    `Thm_Deps.all_oracles` detects `Pure.skip_proof` before clean results are trusted.
    """
    tool = shutil.which("isabelle")
    if tool is None:
        raise AxiomExtractionError("no isabelle on PATH")
    theorem_names = isabelle_theorem_names(statement_text)
    ml_names = ", ".join(f'"{name}"' for name in theorem_names)

    with tempfile.TemporaryDirectory(prefix="robocert-isabelle-audit-") as directory:
        audit_dir = Path(directory)
        output_path = audit_dir / "oracles.tsv"
        root_text = (
            "session RoboCert_Oracle_Audit = RoboCert +\n"
            "  options [document = false, quick_and_dirty = true]\n"
            "  theories OracleAudit\n"
        )
        theory_text = f'''theory OracleAudit
  imports Planar2R
begin

lemma {ISABELLE_PLANTED_CONTROL}: False
  sorry

ML \u2039
  fun oracle_names name =
    Proof_Context.get_thm @{{context}} name
    |> single
    |> Thm_Deps.all_oracles
    |> map (fst o fst)
    |> sort_strings
    |> distinct (op =);
  val declarations = [{ml_names}];
  val results =
    ("{ISABELLE_PLANTED_CONTROL}", oracle_names "{ISABELLE_PLANTED_CONTROL}")
    :: map (fn name => (name, oracle_names name)) declarations;
  fun render (name, oracles) = name ^ "\\t" ^ space_implode "," oracles;
  File.write (Path.explode "{output_path.as_posix()}") (cat_lines (map render results));
\u203a

end
'''
        (audit_dir / "ROOT").write_text(root_text, encoding="utf-8", newline="\n")
        (audit_dir / "OracleAudit.thy").write_text(theory_text, encoding="utf-8", newline="\n")
        code, output = _run(
            [
                tool,
                "build",
                "-D",
                str(session_dir),
                "-D",
                str(audit_dir),
                "-v",
                "RoboCert_Oracle_Audit",
            ],
            cwd=FORMAL_DIR,
        )
        if code != 0:
            raise AxiomExtractionError(f"temporary Isabelle oracle session failed:\n{output}")
        try:
            extracted = output_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AxiomExtractionError(
                f"temporary Isabelle oracle session wrote no readable result: {exc}"
            ) from exc
    return parse_isabelle_oracles(extracted, theorem_names)


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


#: What an attestation entry needs that an evidence file does NOT establish. Kept as data so the
#: omission travels with the artifact instead of living only in a docstring, and computed per
#: file so the disclosure shrinks exactly as far as the evidence improves and no further.
AXIOM_GAP = (
    "axioms: this kernel is not interrogated for its axiom dependencies. Until it is, the "
    "`axioms` field of an entry cannot be filled from a real run, and writing one anyway -- "
    "including writing [] because the policy's allow-list happens to be empty -- is the "
    "fabrication formal/AGENTS.md rule 7 forbids."
)
TRANSCRIPTION_GAP = (
    "promotion stays a human step: an entry is written by hand from this file, so moving a "
    "system out of pending_systems is a reviewed edit rather than a scripted one."
)


def evidence_gaps(axioms: dict[str, list[str]] | None) -> list[str]:
    """What this particular evidence file still does not establish."""
    if axioms is None:
        return [AXIOM_GAP, TRANSCRIPTION_GAP]
    return [TRANSCRIPTION_GAP]


def _evidence(
    record: dict[str, Any],
    record_path: Path,
    system: str,
    source: Path,
    detail: str,
    axioms: dict[str, list[str]] | None = None,
    toolchain: str | None = None,
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
            "Provenance captured from a kernel run that really happened. It is NOT an "
            "attestation and must not be pasted into attestations.entries as-is.",
            *evidence_gaps(axioms),
        ],
        "record": record_path.name,
        "system": system,
        "toolchain": toolchain if toolchain is not None else _toolchain_version(system),
        "kernel_result": detail,
        "declaration_axioms": axioms,
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

    `evidence_dir`, when given, receives one JSON file per supported system whose kernel and
    assumption/oracle audit actually ran and passed. Nothing is written for a skipped or failed
    system. Evidence is provenance only and never promotes an attestation entry.
    """
    errors: list[str] = []
    try:
        record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: could not read/parse: {exc}"]

    entries = record.get("attestations", {}).get("entries", [])
    if not isinstance(entries, list):
        return [f"{path}: attestations.entries must be a list"]
    pending = record.get("pending_systems", {})
    if not isinstance(pending, dict):
        return [f"{path}: pending_systems must be an object"]

    attested_systems: set[str] = set()
    entries_by_system: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{path}: attestation entry is not an object")
            continue
        system = entry.get("system")
        if not isinstance(system, str):
            errors.append(f"{path}: attestation entry has no string 'system'")
            continue
        if system in entries_by_system:
            errors.append(f"{path}: duplicate attestation entry for system {system!r}")
            continue
        entries_by_system[system] = entry

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

    overlap = sorted(set(entries_by_system) & set(pending))
    for system in overlap:
        errors.append(
            f"{path}: system {system!r} is both attested and pending; promotion must be an "
            "unambiguous reviewed edit"
        )

    supported = {"rocq", "isabelle"}
    required = set(require_available)
    unsupported_required = sorted(required - supported)
    for system in unsupported_required:
        errors.append(
            f"{path}: {system!r} was REQUIRED, but this script has no kernel re-run adapter for it"
        )

    audit_systems = sorted((set(entries_by_system) | set(pending) | required) & supported)
    for system in audit_systems:
        info = pending.get(system, {})
        if not isinstance(info, dict):
            errors.append(f"{path}: pending_systems[{system!r}] must be an object")
            info = {}
        source = _resolve(record, "sources", system)
        if source is None or not source.is_file():
            errors.append(f"{path}: system {system!r} names a missing source {source}")
            attested_systems.discard(system)
            continue

        available = _rocq_command() is not None if system == "rocq" else _tool_available("isabelle")
        if not available:
            reason = info.get("reason", "toolchain unavailable on this machine")
            if system in required:
                errors.append(
                    f"{path}: {system!r} was REQUIRED to be available here but its toolchain "
                    "is not on PATH. Refusing to report success for a kernel that never ran."
                )
                attested_systems.discard(system)
            else:
                print(
                    f"check_attestations: {path.name}: {system!r} UNAVAILABLE on this machine "
                    f"-- reported, not treated as a pass ({reason})"
                )
            continue

        if system == "rocq":
            ok, detail = _check_rocq(source)
        else:
            ok, detail = _check_isabelle(source.parent.parent)
        if not ok:
            errors.append(f"{path}: system {system!r} is available but failed: {detail}")
            attested_systems.discard(system)
            continue

        statement = _resolve(record, "statements", system)
        if statement is None or not statement.is_file():
            errors.append(
                f"{path}: {system!r} compiled but names no readable statement file, so the "
                "set of declarations to audit cannot be determined"
            )
            attested_systems.discard(system)
            continue
        try:
            statement_text = statement.read_text(encoding="utf-8")
            axioms = (
                rocq_axioms(source, statement_text)
                if system == "rocq"
                else isabelle_oracles(source.parent.parent, statement_text)
            )
        except (AxiomExtractionError, OSError) as exc:
            errors.append(f"{path}: {system!r} axiom/oracle extraction failed: {exc}")
            attested_systems.discard(system)
            continue

        observed_axioms = sorted({name for names in axioms.values() for name in names})
        allowed = PLANAR2R_ATTESTATION_POLICY.allowed_axioms.get(system, frozenset())
        unexpected = sorted(set(observed_axioms) - allowed)
        if unexpected:
            errors.append(
                f"{path}: {system!r} declarations depend on axiom/oracle(s) outside the "
                f"policy allow-list: {unexpected}. Extracted: {axioms}"
            )
            attested_systems.discard(system)
            continue

        toolchain = _toolchain_version(system)
        if toolchain is None:
            errors.append(
                f"{path}: {system!r} kernel passed but its exact toolchain version could not "
                "be captured; refusing to emit or validate evidence"
            )
            attested_systems.discard(system)
            continue

        print(
            f"check_attestations: {path.name}: {system!r} axiom/oracle audit clean for "
            f"{len(axioms)} declaration(s) (positive control passed)"
        )

        entry = entries_by_system.get(system)
        if entry is not None:
            mismatch = False
            if entry.get("toolchain") != toolchain:
                errors.append(
                    f"{path}: {system!r} toolchain mismatch on kernel re-run -- committed "
                    f"{entry.get('toolchain')!r}, observed {toolchain!r}"
                )
                mismatch = True
            recorded_axioms = entry.get("axioms")
            if not isinstance(recorded_axioms, list) or not all(
                isinstance(name, str) for name in recorded_axioms
            ):
                errors.append(f"{path}: {system!r} committed axioms are not a string array")
                mismatch = True
            elif sorted(recorded_axioms) != observed_axioms:
                errors.append(
                    f"{path}: {system!r} axiom/oracle mismatch on kernel re-run -- committed "
                    f"{sorted(recorded_axioms)!r}, observed {observed_axioms!r}"
                )
                mismatch = True
            if mismatch:
                attested_systems.discard(system)
                continue
            print(
                f"check_attestations: {path.name}: {system!r} promoted attestation was "
                "revalidated by a fresh kernel run"
            )
        else:
            print(
                f"check_attestations: {path.name}: {system!r} toolchain available and "
                f"{detail} -- reviewed transcription may now move it out of pending_systems"
            )

        if evidence_dir is not None:
            evidence = _evidence(record, path, system, source, detail, axioms, toolchain=toolchain)
            evidence_dir.mkdir(parents=True, exist_ok=True)
            target = evidence_dir / f"{path.stem}.{system}.json"
            target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
            print(
                f"check_attestations: {path.name}: wrote run evidence for {system!r} to "
                f"{target} (toolchain {toolchain!r}). Provenance only -- see "
                "'not_an_attestation_entry' in the file."
            )

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
            "Write run provenance here for every supported system whose kernel and "
            "assumption/oracle audit passed: toolchain, digests, certificate binding, and "
            "per-declaration dependencies. Provenance only; this never promotes an entry."
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
