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

    The first real run of the `rocq` CI job did exactly that: opam installed Rocq,
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


# ---------------------------------------------------------------------------------------
# Run evidence
#
# The script used to print "record it with kernel_accepted: true" when a pending kernel
# passed, and throw away everything the promotion needed. The toolchain version is the part
# that cannot be recovered afterwards: digests recompute from committed files at any time,
# but which binary accepted the proof is knowable only on the machine that ran it.
#
# Neither Rocq nor Isabelle is installed on the machine these tests were written on -- the
# same fact `pending_systems` records -- so the kernel runner is stubbed. What is under test
# is the evidence path, not the prover.
# ---------------------------------------------------------------------------------------


def _pending_rocq_record() -> dict[str, Any]:
    record = _record()
    record["pending_systems"] = {"rocq": {"reason": "stubbed in this test"}}
    record["sources"]["rocq"] = _REAL_SOURCE
    record["statements"]["rocq"] = _REAL_STATEMENT
    record["certificate"] = {
        "claim_hash": _WRONG_DIGEST,
        "model_hash": _WRONG_DIGEST,
        "checker_id": "robocert.planar2r_exact_witness.attested",
        "checker_version": "0.1.0",
    }
    return record


def _stub_passing_rocq(script: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """A Rocq toolchain that compiles cleanly and audits clean.

    `rocq_axioms` is stubbed alongside the compiler because axiom extraction now runs on every
    available toolchain, not only when evidence is requested -- an axiom escaping the allow-list
    must fail the job that noticed it. Tests that care about extraction override this stub.
    """
    monkeypatch.setattr(script, "_rocq_command", lambda: ["rocq", "compile"])
    monkeypatch.setattr(script, "_check_rocq", lambda _source: (True, "compiled cleanly"))
    monkeypatch.setattr(
        script, "_toolchain_version", lambda _system: "The Rocq Prover, version 9.2.0"
    )
    monkeypatch.setattr(script, "rocq_axioms", lambda *_a, **_k: {"pythagorean_identity": []})


def test_evidence_is_written_when_a_pending_kernel_passes(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_rocq(script, monkeypatch)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    script.check_record(path, evidence_dir=evidence_dir)

    written = json.loads((evidence_dir / "record.rocq.json").read_text(encoding="utf-8"))
    assert written["system"] == "rocq"
    assert written["toolchain"] == "The Rocq Prover, version 9.2.0"
    assert written["artifact_digest"].startswith("sha256:")
    assert written["statement_digest"].startswith("sha256:")
    assert written["certificate"]["checker_version"] == "0.1.0"


def test_evidence_says_it_is_not_an_attestation_entry(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one property that stops this becoming a fabricated entry by copy-paste.

    Its field names deliberately do not match `attestation._ENTRY_FIELDS`, it carries no
    `kernel_accepted`, and it names the axiom gap that still blocks promotion. Pasting it into
    `attestations.entries` would be rejected by the policy rather than silently accepted.
    """
    from robocert.attestation import _ENTRY_FIELDS

    _stub_passing_rocq(script, monkeypatch)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    script.check_record(path, evidence_dir=evidence_dir)
    written = json.loads((evidence_dir / "record.rocq.json").read_text(encoding="utf-8"))

    assert "kernel_accepted" not in written
    assert set(written) != _ENTRY_FIELDS
    assert not set(written) >= _ENTRY_FIELDS
    disclosure = " ".join(written["not_an_attestation_entry"])
    assert "NOT an attestation" in disclosure
    assert script.TRANSCRIPTION_GAP in disclosure


def test_the_axiom_gap_is_disclosed_exactly_when_axioms_are_unknown(script: Any) -> None:
    """Isabelle, today, has no extractor, so its evidence must still say so. Rocq's must not
    keep claiming a gap it has closed."""
    unknown = script.evidence_gaps(None)
    known = script.evidence_gaps({"lemma": []})

    assert script.AXIOM_GAP in unknown
    assert script.AXIOM_GAP not in known
    assert script.TRANSCRIPTION_GAP in unknown
    assert script.TRANSCRIPTION_GAP in known


def test_no_evidence_is_written_when_the_toolchain_is_absent(script: Any, tmp_path: Path) -> None:
    """Nothing is invented. An unavailable kernel leaves no trace claiming it ran."""
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    script.check_record(path, evidence_dir=evidence_dir)

    assert not evidence_dir.exists()


def test_no_evidence_is_written_when_the_kernel_fails(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failing kernel is an error, not provenance."""
    monkeypatch.setattr(script, "_rocq_command", lambda: ["rocq", "compile"])
    monkeypatch.setattr(script, "_check_rocq", lambda _source: (False, "compilation failed"))
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    errors = list(script.check_record(path, evidence_dir=evidence_dir))

    assert any("available but failed" in error for error in errors)
    assert not evidence_dir.exists()


def test_evidence_is_opt_in(script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Without --emit-evidence the behaviour is exactly what it was before."""
    _stub_passing_rocq(script, monkeypatch)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")

    assert list(script.check_record(path)) == []
    assert list(tmp_path.iterdir()) == [path]


# ---------------------------------------------------------------------------------------
# Rocq axiom extraction
#
# The rule these tests exist to enforce: `[]` means "the kernel said Closed under the global
# context", NEVER "the parser did not understand the output". A build failure is loud; a
# silently empty axiom list fails OPEN, writing an attestation that asserts a proof depends on
# nothing. Every unrecognised shape below must raise.
#
# Rocq is not installed on the machine these were written on, so the parser is exercised on
# captured output shapes. The one thing that cannot be tested here -- that these shapes are what
# THIS toolchain actually emits -- is what the CI positive control is for.
# ---------------------------------------------------------------------------------------


def test_closed_form_parses_to_no_axioms(script: Any) -> None:
    assert script.parse_print_assumptions("Closed under the global context\n") == []


def test_single_axiom_is_reported(script: Any) -> None:
    output = "Axioms:\nfunctional_extensionality : forall A B, True\n"
    assert script.parse_print_assumptions(output) == ["functional_extensionality"]


def test_several_axioms_across_sections_are_reported(script: Any) -> None:
    output = (
        "Axioms:\n"
        "proof_irrelevance : forall P, True\n"
        "functional_extensionality\n"
        "  : forall A B, True\n"
        "Variables:\n"
        "some_variable : nat\n"
    )
    assert script.parse_print_assumptions(output) == [
        "proof_irrelevance",
        "functional_extensionality",
        "some_variable",
    ]


@pytest.mark.parametrize(
    ("label", "output"),
    [
        ("empty", "\n  \n"),
        ("prose", "some unexpected diagnostic\n"),
        ("unknown section", "Sorceries:\nfoo : bar\n"),
        ("entries before any section", "foo : bar\nAxioms:\nbaz : qux\n"),
        ("closed mixed with content", "Closed under the global context\nAxioms:\nfoo : bar\n"),
        ("section with no entries", "Axioms:\n"),
    ],
)
def test_unrecognised_output_raises_rather_than_returning_empty(
    script: Any, label: str, output: str
) -> None:
    """Each of these would fail OPEN if the parser fell back to `[]`."""
    with pytest.raises(script.AxiomExtractionError):
        script.parse_print_assumptions(output)
    assert label  # named for the failure message only


def test_lemma_names_come_from_the_statement_file(script: Any) -> None:
    text = (_REPO_ROOT / "formal" / "attestations" / "statements" / "rocq.txt").read_text(
        encoding="utf-8"
    )
    names = script.rocq_lemma_names(text)

    assert names == [
        "pythagorean_identity",
        "segment1_nondegenerate_identity",
        "segment2_nondegenerate_identity",
        "segment1_zero_implies_length_zero",
        "segment2_zero_implies_length_zero",
    ]


def test_a_statement_file_with_no_lemmas_raises(script: Any) -> None:
    """An empty audit set is never the answer; it means the file changed shape."""
    with pytest.raises(script.AxiomExtractionError, match="empty audit"):
        script.rocq_lemma_names("(* nothing here *)\n")


def test_the_positive_control_rejects_a_parser_that_cannot_see_an_axiom(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control's own control. If `_rocq_print_assumptions` reported the planted axiom as
    absent, `rocq_axioms` must refuse to run rather than certify the real lemmas."""
    monkeypatch.setattr(script, "_rocq_print_assumptions", lambda *_a, **_k: [])

    with pytest.raises(script.AxiomExtractionError, match="positive control FAILED"):
        script.rocq_axioms(_REPO_ROOT / "formal" / "rocq" / "RoboCert" / "Planar2R.v", "Lemma a :")


def test_extraction_covers_every_named_declaration(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[str] = []

    def fake(_source: Path, declaration: str, preamble: str = "") -> list[str]:
        seen.append(declaration)
        return [script.PLANTED_AXIOM] if preamble else []

    monkeypatch.setattr(script, "_rocq_print_assumptions", fake)
    text = (_REPO_ROOT / "formal" / "attestations" / "statements" / "rocq.txt").read_text(
        encoding="utf-8"
    )

    result = script.rocq_axioms(_REPO_ROOT / "formal" / "rocq" / "RoboCert" / "Planar2R.v", text)

    assert seen[0] == "planted_control"
    assert sorted(result) == sorted(script.rocq_lemma_names(text))
    assert all(value == [] for value in result.values())


def test_an_axiom_outside_the_allow_list_fails_the_check(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Caught where it is produced, not left for a human to notice while transcribing."""
    _stub_passing_rocq(script, monkeypatch)
    monkeypatch.setattr(
        script, "rocq_axioms", lambda *_a, **_k: {"pythagorean_identity": ["sneaky_axiom"]}
    )
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")

    errors = list(script.check_record(path))

    assert any("outside the policy allow-list" in error for error in errors)
    assert any("sneaky_axiom" in error for error in errors)


def test_extraction_failure_blocks_the_record(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_rocq(script, monkeypatch)

    def boom(*_a: object, **_k: object) -> dict[str, list[str]]:
        raise script.AxiomExtractionError("planted parser failure")

    monkeypatch.setattr(script, "rocq_axioms", boom)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")

    errors = list(script.check_record(path))

    assert any("axiom/oracle extraction failed" in error for error in errors)


def test_evidence_records_extracted_axioms_and_drops_that_gap(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The disclosure shrinks exactly as far as the evidence improves, and no further."""
    _stub_passing_rocq(script, monkeypatch)
    monkeypatch.setattr(script, "rocq_axioms", lambda *_a, **_k: {"pythagorean_identity": []})
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_rocq_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    assert list(script.check_record(path, evidence_dir=evidence_dir)) == []
    written = json.loads((evidence_dir / "record.rocq.json").read_text(encoding="utf-8"))

    assert written["declaration_axioms"] == {"pythagorean_identity": []}
    disclosure = " ".join(written["not_an_attestation_entry"])
    assert script.AXIOM_GAP not in disclosure
    assert script.TRANSCRIPTION_GAP in disclosure
    # Still not an entry: promotion remains a reviewed human edit.
    assert "kernel_accepted" not in written


# ---------------------------------------------------------------------------------------
# Promoted-system revalidation
# ---------------------------------------------------------------------------------------


def _promoted_rocq_record() -> dict[str, Any]:
    record = _pending_rocq_record()
    record["pending_systems"] = {}
    template = record["attestations"]["entries"][0]
    record["attestations"]["entries"].append(
        {
            **template,
            "system": "rocq",
            "toolchain": "The Rocq Prover, version 9.2.0",
            "axioms": [],
        }
    )
    return record


def test_require_reruns_a_promoted_kernel(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Promotion must not turn a real prover CI job into a digest-only false green."""
    _stub_passing_rocq(script, monkeypatch)
    calls: list[Path] = []

    def check(source: Path) -> tuple[bool, str]:
        calls.append(source)
        return True, "compiled cleanly"

    monkeypatch.setattr(script, "_check_rocq", check)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_promoted_rocq_record()), encoding="utf-8")

    errors = script.check_record(path, require_available=["rocq"])

    assert errors == []
    assert len(calls) == 1


def test_promoted_toolchain_mismatch_fails_closed(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_rocq(script, monkeypatch)
    record = _promoted_rocq_record()
    record["attestations"]["entries"][1]["toolchain"] = "different toolchain"
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    errors = script.check_record(path, require_available=["rocq"])

    assert any("toolchain mismatch on kernel re-run" in error for error in errors)


def test_promoted_axiom_mismatch_fails_closed(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_rocq(script, monkeypatch)
    record = _promoted_rocq_record()
    record["attestations"]["entries"][1]["axioms"] = ["functional_extensionality"]
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    errors = script.check_record(path, require_available=["rocq"])

    assert any("axiom/oracle mismatch on kernel re-run" in error for error in errors)


def test_failed_promoted_kernel_emits_no_evidence(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_rocq(script, monkeypatch)
    monkeypatch.setattr(script, "_check_rocq", lambda _source: (False, "planted failure"))
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_promoted_rocq_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    errors = script.check_record(path, require_available=["rocq"], evidence_dir=evidence_dir)

    assert any("planted failure" in error for error in errors)
    assert not evidence_dir.exists()


# ---------------------------------------------------------------------------------------
# Isabelle oracle extraction
# ---------------------------------------------------------------------------------------


def _isabelle_statement() -> str:
    return (_REPO_ROOT / "formal" / "attestations" / "statements" / "isabelle.txt").read_text(
        encoding="utf-8"
    )


def _pending_isabelle_record() -> dict[str, Any]:
    record = _record()
    record["pending_systems"] = {"isabelle": {"reason": "stubbed"}}
    record["sources"]["isabelle"] = "formal/isabelle/RoboCert/Planar2R.thy"
    record["statements"]["isabelle"] = "formal/attestations/statements/isabelle.txt"
    return record


def _stub_passing_isabelle(script: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(script, "_tool_available", lambda name: name == "isabelle")
    monkeypatch.setattr(script, "_check_isabelle", lambda _session: (True, "built cleanly"))
    monkeypatch.setattr(script, "_toolchain_version", lambda _system: "Isabelle2025")
    monkeypatch.setattr(
        script,
        "isabelle_oracles",
        lambda *_a, **_k: {
            "singleton_box_admits_its_point": [],
            "bounded_existential_transport": [],
            "empty_box_forces_false": [],
        },
    )


def test_isabelle_theorem_names_come_from_the_statement_file(script: Any) -> None:
    assert script.isabelle_theorem_names(_isabelle_statement()) == [
        "singleton_box_admits_its_point",
        "bounded_existential_transport",
        "empty_box_forces_false",
    ]


@pytest.mark.parametrize(
    ("label", "output"),
    [
        ("empty", ""),
        ("malformed", "only-one-field\n"),
        ("unknown", "unknown\t\n"),
        (
            "duplicate",
            "robocert_planted_control\tPure.skip_proof\n"
            "robocert_planted_control\tPure.skip_proof\n",
        ),
        ("malformed oracle", "robocert_planted_control\tbad oracle\n"),
    ],
)
def test_isabelle_oracle_parser_rejects_unrecognised_output(
    script: Any, label: str, output: str
) -> None:
    with pytest.raises(script.AxiomExtractionError):
        script.parse_isabelle_oracles(output, ["real_theorem"])
    assert label


def test_isabelle_oracle_parser_requires_every_real_theorem(script: Any) -> None:
    output = "robocert_planted_control\tPure.skip_proof\n"
    with pytest.raises(script.AxiomExtractionError, match="omitted"):
        script.parse_isabelle_oracles(output, ["real_theorem"])


def test_isabelle_oracle_parser_requires_skip_proof_positive_control(script: Any) -> None:
    output = "robocert_planted_control\t\nreal_theorem\t\n"
    with pytest.raises(script.AxiomExtractionError, match="positive control FAILED"):
        script.parse_isabelle_oracles(output, ["real_theorem"])


def test_isabelle_oracle_parser_returns_per_declaration_results(script: Any) -> None:
    output = (
        "robocert_planted_control\tPure.skip_proof\nfirst\t\nsecond\tNamed_Theorems.some_oracle\n"
    )
    assert script.parse_isabelle_oracles(output, ["first", "second"]) == {
        "first": [],
        "second": ["Named_Theorems.some_oracle"],
    }


def test_isabelle_extractor_uses_a_temporary_child_and_planted_sorry(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        script.shutil,
        "which",
        lambda name: "isabelle" if name == "isabelle" else None,
    )

    def run(cmd: list[str], *, cwd: Path) -> tuple[int, str]:
        del cwd
        audit_dir = Path(cmd[cmd.index("-D", cmd.index("-D") + 1) + 1])
        root = (audit_dir / "ROOT").read_text(encoding="utf-8")
        theory = (audit_dir / "OracleAudit.thy").read_text(encoding="utf-8")
        assert "quick_and_dirty = true" in root
        assert 'imports "RoboCert.Planar2R"' in theory
        assert "sorry" in theory
        assert "Thm_Deps.all_oracles" in theory
        names = script.isabelle_theorem_names(_isabelle_statement())
        lines = [f"{script.ISABELLE_PLANTED_CONTROL}\t{script.ISABELLE_SKIP_PROOF}"]
        lines.extend(f"{name}\t" for name in names)
        (audit_dir / "oracles.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0, ""

    monkeypatch.setattr(script, "_run", run)
    result = script.isabelle_oracles(tmp_path, _isabelle_statement())
    assert result == {
        "singleton_box_admits_its_point": [],
        "bounded_existential_transport": [],
        "empty_box_forces_false": [],
    }


def test_isabelle_extraction_failure_emits_no_evidence(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = _pending_isabelle_record()
    _stub_passing_isabelle(script, monkeypatch)
    monkeypatch.setattr(
        script,
        "isabelle_oracles",
        lambda *_a, **_k: (_ for _ in ()).throw(
            script.AxiomExtractionError("missing Pure.skip_proof")
        ),
    )
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    errors = script.check_record(path, evidence_dir=evidence_dir)

    assert any("missing Pure.skip_proof" in error for error in errors)
    assert not evidence_dir.exists()


def test_isabelle_evidence_records_clean_oracles_and_drops_axiom_gap(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_isabelle(script, monkeypatch)
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_isabelle_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    errors = script.check_record(path, evidence_dir=evidence_dir)

    assert errors == []
    written = json.loads((evidence_dir / "record.isabelle.json").read_text(encoding="utf-8"))
    assert written["toolchain"] == "Isabelle2025"
    assert written["declaration_axioms"] == {
        "singleton_box_admits_its_point": [],
        "bounded_existential_transport": [],
        "empty_box_forces_false": [],
    }
    assert script.AXIOM_GAP not in " ".join(written["not_an_attestation_entry"])


def test_unexpected_isabelle_oracle_fails_and_emits_no_evidence(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_passing_isabelle(script, monkeypatch)
    monkeypatch.setattr(
        script,
        "isabelle_oracles",
        lambda *_a, **_k: {"singleton_box_admits_its_point": ["Bad.oracle"]},
    )
    path = tmp_path / "record.json"
    path.write_text(json.dumps(_pending_isabelle_record()), encoding="utf-8")
    evidence_dir = tmp_path / "evidence"

    errors = script.check_record(path, evidence_dir=evidence_dir)

    assert any("outside the policy allow-list" in error for error in errors)
    assert any("Bad.oracle" in error for error in errors)
    assert not evidence_dir.exists()
