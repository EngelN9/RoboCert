"""The Lean/Python conformance harness must be able to fail.

A differential harness that cannot detect a planted error is worse than no harness: it
produces a green signal that means nothing. RC-002's own history records exactly that failure
mode -- a test cited as a warrant that "did not perform the described check" -- so the controls
here plant a specific defect at a specific site and require the harness to catch it.

The emitter tests need no toolchain. The control tests do: they are skipped when `lake` is
absent, and `scripts/check_lean_conformance.py --require-lean` (which CI passes) is what makes
an absent toolchain a failure rather than a skip.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from robocert.specification import (
    BoxDomain,
    Formula,
    IntervalDomain,
    MonomialPower,
    Polynomial,
    Predicate,
    QuantifierBlock,
    QuantifierKind,
    Rational,
    Relation,
    Term,
    Unit,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "check_lean_conformance.py"


def _load_script() -> Any:
    spec = importlib.util.spec_from_file_location("check_lean_conformance", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registering before exec is required: the module defines a dataclass, and
    # `dataclasses` resolves field types through `sys.modules[cls.__module__]`.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_COLLECTION_PROBE = _load_script().probe_lean_toolchain()
_needs_lean = pytest.mark.skipif(
    not _COLLECTION_PROBE.available,
    reason=(
        "Lean toolchain unrunnable; CI's `formal` job uses --require-lean: "
        f"{_COLLECTION_PROBE.diagnostic}"
    ),
)


@pytest.fixture(scope="module")
def script() -> Any:
    return _load_script()


@pytest.fixture(scope="module")
def vectors(script: Any) -> list[Any]:
    return script.build_vectors()


@pytest.fixture(scope="module")
def by_name(vectors: list[Any]) -> dict[str, Any]:
    return {vector.name: vector for vector in vectors}


# ---------------------------------------------------------------------------------------
# Emitter
# ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Rational(1, 2), "(mkRat 1 2)"),
        (Rational(-1, 3), "(mkRat (-1) 3)"),
        (Rational(7), "(mkRat 7 1)"),
        (Rational(0), "(mkRat 0 1)"),
        (Rational(1234567, 999983), "(mkRat 1234567 999983)"),
    ],
)
def test_rationals_emit_with_parenthesised_negatives(
    script: Any, value: Rational, expected: str
) -> None:
    """`mkRat -1 3` is a parse error; the negative numerator needs its own parentheses."""
    assert script.lean_rational(value) == expected


def test_unit_is_emitted_fully_qualified(script: Any) -> None:
    """Lean core has its own `Unit`, which `open RoboCert` does not shadow."""
    interval = IntervalDomain(
        domain_id="D",
        variable_id="v",
        lower=Rational(0),
        upper=Rational(1),
        unit=Unit.RADIAN,
    )
    assert "RoboCert.Unit.radian" in script.lean_interval(interval)


def test_every_enum_member_has_a_lean_constructor(script: Any) -> None:
    """A new Python enum member must not silently emit nothing."""
    from robocert.specification import (
        GeometrySemantics,
        QuantifierKind,
        UncertaintySemantics,
    )

    for table, enum in (
        (script._UNIT, Unit),
        (script._QUANTIFIER, QuantifierKind),
        (script._RELATION, Relation),
        (script._UNCERTAINTY, UncertaintySemantics),
        (script._GEOMETRY, GeometrySemantics),
    ):
        assert set(table) == set(enum), f"{enum.__name__} is not fully mapped"


def test_not_emits_a_single_operand_not_a_list(script: Any) -> None:
    """Divergence 1: Python's one-element `operands` tuple becomes Lean's single `Formula`."""
    emitted = script.lean_formula(Formula.negate(Formula.negate(Formula.predicate("p"))))
    assert emitted == '(Formula.not (Formula.not (Formula.pred "p")))'


def test_connectives_stay_n_ary(script: Any) -> None:
    emitted = script.lean_formula(Formula.all(Formula.predicate("a"), Formula.predicate("b")))
    assert emitted == '(Formula.and [(Formula.pred "a"), (Formula.pred "b")])'


def test_polynomial_emits_terms_and_exponents(script: Any) -> None:
    polynomial = Polynomial(
        terms=(
            Term(Rational(-3, 7), powers=(MonomialPower("v", 3),)),
            Term(Rational(2), powers=()),
        )
    )
    emitted = script.lean_polynomial(polynomial)
    assert "exponent := 3" in emitted
    assert "(mkRat (-3) 7)" in emitted
    assert "powers := []" in emitted


def test_witness_environment_chains_extends_in_sorted_order(script: Any) -> None:
    emitted = script.lean_env({"b": Rational(1), "a": Rational(2)})
    assert emitted.index('"a"') < emitted.index('"b"')
    assert emitted.startswith("((Env.empty.extend")


def test_empty_witness_is_the_empty_environment(script: Any) -> None:
    assert script.lean_env({}) == "Env.empty"


def test_predicate_relations_all_round_trip(script: Any) -> None:
    for relation in Relation:
        predicate = Predicate(
            predicate_id="p",
            left=Polynomial(terms=(Term(Rational(1), powers=(MonomialPower("v", 1),)),)),
            relation=relation,
            right=Polynomial.zero(),
        )
        assert script._RELATION[relation] in script.lean_predicate(predicate)


# ---------------------------------------------------------------------------------------
# The vector set itself
# ---------------------------------------------------------------------------------------


def test_vector_set_exercises_both_verdicts(vectors: list[Any]) -> None:
    """A set that only accepts would agree with a model returning `true` unconditionally."""
    accepted = [item for item in vectors if item.python_accepted]
    rejected = [item for item in vectors if not item.python_accepted]
    assert len(accepted) >= 5
    assert len(rejected) >= 5


def test_vector_names_are_unique(vectors: list[Any]) -> None:
    names = [item.name for item in vectors]
    assert len(names) == len(set(names))


def test_forall_vector_is_rejected_by_python(by_name: dict[str, Any]) -> None:
    """The RC-002 guard: one witness point cannot discharge a universal."""
    assert by_name["forall_block_rejected"].python_accepted is False


def test_boundary_vectors_split_on_the_closed_flag(by_name: dict[str, Any]) -> None:
    assert by_name["boundary_lower_closed"].python_accepted is True
    assert by_name["boundary_lower_open"].python_accepted is False
    assert by_name["boundary_upper_closed"].python_accepted is True
    assert by_name["boundary_upper_open"].python_accepted is False


def test_every_vector_satisfies_the_soundness_theorem_hypothesis(
    script: Any, vectors: list[Any]
) -> None:
    """`exactWitness_sound` assumes `FormulaVarsQuantified`; a vector outside it proves nothing.

    `build_vectors` already refuses to construct such a vector, so this asserts the property the
    guard is there to keep rather than re-testing the guard.
    """
    for vector in vectors:
        satisfied, unbound = script.formula_vars_quantified(vector.claim)
        assert satisfied, f"{vector.name}: unbound in the formula: {unbound}"


def test_the_wellformedness_check_can_say_no(script: Any) -> None:
    """Non-vacuity control. Without this, a helper returning True unconditionally would pass
    every assertion above and the guard in `build_vectors` would be decoration.

    A `Claim` mentioning an unquantified variable cannot be constructed -- `specification.py`
    rejects it at three separate points -- so the claim-level validation is bypassed with a
    stand-in carrying the four attributes the helper reads. Every sub-object is a real one; only
    `Claim.__post_init__` is skipped, and skipping it is the whole point of the control.
    """
    predicate = Predicate(
        predicate_id="mentions_free",
        left=Polynomial(terms=(Term(Rational(1), powers=(MonomialPower("free", 1),)),)),
        relation=Relation.GT,
        right=Polynomial.zero(),
    )
    axis = IntervalDomain(domain_id="B.v", variable_id="v", lower=Rational(0), upper=Rational(1))
    stand_in = SimpleNamespace(
        predicates=(predicate,),
        formula=Formula.predicate("mentions_free"),
        domains=(BoxDomain("B", components=(axis,)),),
        quantifiers=(QuantifierBlock(QuantifierKind.EXISTS, ("v",), "B"),),
    )

    satisfied, unbound = script.formula_vars_quantified(stand_in)
    assert satisfied is False
    assert unbound == ["free"]


def test_build_vectors_refuses_a_vector_outside_the_theorem_scope(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The guard must reject, not compute-and-discard. Forcing the check to fail must stop the
    vector set being built at all."""
    monkeypatch.setattr(script, "formula_vars_quantified", lambda _claim: (False, ["planted"]))
    with pytest.raises(ValueError, match="FormulaVarsQuantified"):
        script.build_vectors()


def test_wellformedness_mirrors_leans_fail_closed_lookups(script: Any) -> None:
    """An unresolvable id resolves the way `Wellformed.lean` resolves it, not the way Python's
    validator would. `Formula.Mentions` is `False` on a missed `findPredicate`, so an unknown
    predicate mentions nothing; `BoundBy` needs `findDomain` to succeed, so a block naming an
    unknown domain binds nothing. Neither raises."""
    axis = IntervalDomain(domain_id="B.v", variable_id="v", lower=Rational(0), upper=Rational(1))
    unknown_predicate = SimpleNamespace(
        predicates=(),
        formula=Formula.predicate("absent"),
        domains=(BoxDomain("B", components=(axis,)),),
        quantifiers=(QuantifierBlock(QuantifierKind.EXISTS, ("v",), "B"),),
    )
    assert script.formula_vars_quantified(unknown_predicate) == (True, [])

    predicate = Predicate(
        predicate_id="uses_v",
        left=Polynomial(terms=(Term(Rational(1), powers=(MonomialPower("v", 1),)),)),
        relation=Relation.GT,
        right=Polynomial.zero(),
    )
    unknown_domain = SimpleNamespace(
        predicates=(predicate,),
        formula=Formula.predicate("uses_v"),
        domains=(),
        quantifiers=(QuantifierBlock(QuantifierKind.EXISTS, ("v",), "absent"),),
    )
    assert script.formula_vars_quantified(unknown_domain) == (False, ["v"])


def test_guard_lines_map_to_every_vector(script: Any, vectors: list[Any]) -> None:
    source, guard_lines = script.emit_lean_source(vectors)
    assert sorted(guard_lines.values()) == sorted(item.name for item in vectors)
    lines = source.splitlines()
    for line_number, name in guard_lines.items():
        assert lines[line_number - 1].startswith("#guard "), name


# ---------------------------------------------------------------------------------------
# Planted-error controls -- the tests that make the rest of this file mean something
# ---------------------------------------------------------------------------------------


@_needs_lean
def test_unmutated_vectors_agree(script: Any, vectors: list[Any]) -> None:
    source, guard_lines = script.emit_lean_source(vectors)
    assert script.run_lean(source, guard_lines) == []


@_needs_lean
def test_a_flipped_python_verdict_is_detected(script: Any, vectors: list[Any]) -> None:
    """Control A: corrupt the recorded verdict, keeping the claim untouched."""
    planted = list(vectors)
    planted[0] = dataclasses.replace(planted[0], python_accepted=not planted[0].python_accepted)
    source, guard_lines = script.emit_lean_source(planted)
    failures = script.run_lean(source, guard_lines)
    assert failures, "a flipped verdict must not pass"
    assert vectors[0].name in failures[0]


# Each entry mutates ONE emitted vector at a site that is load-bearing FOR THAT VECTOR. A
# mutation applied to the first occurrence anywhere in the file is a poor control: it lands
# wherever it lands, and at many sites it genuinely preserves the verdict. Measured misses of
# that kind are recorded in formal/README.md rather than papered over.
_PLANTED = [
    ("and_with_false_operand", "Formula.and", "Formula.or"),
    ("or_first_operand_false", "Formula.or", "Formula.and"),
    ("boundary_lower_closed", "lowerClosed := true", "lowerClosed := false"),
    ("boundary_upper_open", "upperClosed := false", "upperClosed := true"),
    ("two_blocks_satisfied", "QuantifierKind.exists_", "QuantifierKind.forAll"),
    ("planar2r_worked_instance", "Relation.ge", "Relation.le"),
    ("high_exponent_arithmetic", "exponent := 3", "exponent := 2"),
    ("nested_not", "Formula.not", "Formula.and"),
]


@_needs_lean
@pytest.mark.parametrize(("vector_name", "old", "new"), _PLANTED)
def test_a_mutated_lean_model_is_detected(
    script: Any, by_name: dict[str, Any], vector_name: str, old: str, new: str
) -> None:
    """Control B: mutate the Lean the model actually elaborates, and require a failure."""
    source, guard_lines = script.emit_lean_source([by_name[vector_name]])
    mutated = source.replace(old, new)
    assert mutated != source, f"{old!r} does not occur in vector {vector_name!r}"
    failures = script.run_lean(mutated, guard_lines)
    assert failures, f"mutating {old!r} to {new!r} in {vector_name!r} was not detected"
    assert vector_name in failures[0]


@_needs_lean
def test_a_non_elaborating_file_is_not_reported_as_conformance(script: Any) -> None:
    """A broken emitter must not read as a conformance failure, nor as a pass."""
    failures = script.run_lean("import RoboCert.Checker\nthis is not Lean\n", {})
    assert len(failures) == 1
    assert "emitter or toolchain defect" in failures[0]


# ---------------------------------------------------------------------------------------
# Fail-closed behaviour of the entry point
# ---------------------------------------------------------------------------------------


def test_require_lean_fails_when_the_toolchain_is_absent(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The false-green the `rocq` job shipped on its first run, made impossible here."""
    monkeypatch.setattr(
        script,
        "probe_lean_toolchain",
        lambda _explicit=None: script.LeanToolchainProbe(None, None, "planted absent toolchain"),
    )
    assert script.main(["--require-lean"]) == 1


def test_absent_toolchain_without_the_flag_reports_and_exits_zero(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        script,
        "probe_lean_toolchain",
        lambda _explicit=None: script.LeanToolchainProbe(None, None, "planted absent toolchain"),
    )
    assert script.main([]) == 0


def test_lake_override_precedence_and_successful_probe(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("ROBOCERT_LAKE", "environment-lake")
    monkeypatch.setattr(
        script.shutil,
        "which",
        lambda command: f"resolved-{command}" if command != "lake" else "path-lake",
    )

    def run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="Lean (version 4.33.1)\n", stderr="")

    monkeypatch.setattr(script.subprocess, "run", run)

    explicit = script.probe_lean_toolchain("cli-lake")
    environment = script.probe_lean_toolchain()

    assert explicit.lake == "resolved-cli-lake"
    assert environment.lake == "resolved-environment-lake"
    assert explicit.available and environment.available
    assert calls == [
        ["resolved-cli-lake", "env", "lean", "--version"],
        ["resolved-environment-lake", "env", "lean", "--version"],
    ]


def test_path_shim_that_cannot_run_pinned_lean_is_unavailable(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ROBOCERT_LAKE", raising=False)
    monkeypatch.setattr(script.shutil, "which", lambda _command: "broken-lake-shim")
    monkeypatch.setattr(
        script.subprocess,
        "run",
        lambda *_a, **_k: SimpleNamespace(returncode=1, stdout="", stderr="no installed toolchain"),
    )

    probe = script.probe_lean_toolchain()

    assert probe.lake == "broken-lake-shim"
    assert not probe.available
    assert "no installed toolchain" in probe.diagnostic


def test_elan_proxy_does_not_auto_install_missing_pin(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake = tmp_path / "lake.exe"
    elan = tmp_path / "elan.exe"
    lake.touch()
    elan.touch()
    monkeypatch.delenv("ROBOCERT_LAKE", raising=False)
    monkeypatch.setattr(script.shutil, "which", lambda _command: str(lake))
    calls: list[list[str]] = []

    def run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(command)
        assert command == [str(elan), "toolchain", "list"]
        return SimpleNamespace(returncode=0, stdout="no installed toolchains\n", stderr="")

    monkeypatch.setattr(script.subprocess, "run", run)

    probe = script.probe_lean_toolchain()

    assert not probe.available
    assert "is not installed according to elan" in probe.diagnostic
    assert calls == [[str(elan), "toolchain", "list"]]


def test_main_passes_cli_lake_override_to_probe(
    script: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[str | None] = []

    def probe(explicit: str | None = None) -> Any:
        seen.append(explicit)
        return script.LeanToolchainProbe(None, None, "planted unavailable")

    monkeypatch.setattr(script, "probe_lean_toolchain", probe)

    assert script.main(["--lake", "C:/pinned/lake.exe"]) == 0
    assert seen == ["C:/pinned/lake.exe"]


def test_emit_only_writes_the_source_without_running_lean(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _fail(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("--emit-only must not invoke Lean")

    monkeypatch.setattr(script, "run_lean", _fail)
    target = tmp_path / "Conformance.lean"
    assert script.main(["--emit-only", str(target)]) == 0
    assert "import RoboCert.Checker" in target.read_text(encoding="utf-8")
