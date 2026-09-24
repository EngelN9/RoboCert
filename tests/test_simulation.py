"""Falsification search semantics, with no MuJoCo installed.

The fake backend below is the second implementation of `SimulationBackend`, which is the
whole reason the Protocol exists. Every assertion here is about the search's contract, not
about physics: determinism under a fixed seed, fail-closed behaviour on every error path,
and the guarantee that a report never leaks a raw float into canonical JSON.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from fractions import Fraction

import pytest

from robocert.artifacts import canonical_json_bytes, digest_json
from robocert.refutation import refute
from robocert.results import ResultStatus, counterexample_result
from robocert.simulation import (
    ContactRecord,
    FalsificationOutcome,
    JointState,
    SimulationBackend,
    SimulationObservation,
    SimulationProperty,
    SimulationProvenance,
    Violation,
    actuator_force_within,
    candidate_assignment,
    minimum_distance_at_least,
    no_penetration,
    region_from_box_domain,
    region_from_sequence,
    sample_configurations,
    search_for_counterexample,
)
from robocert.specification import BoxDomain, Claim, IntervalDomain, Rational, Unit
from robocert.witness_search2r import angle_to_t_candidate, t_to_angle

PROVENANCE = SimulationProvenance(
    backend_id="fake",
    backend_version="0",
    model_sha256="0" * 64,
    timestep=0.002,
    collision_margin=0.05,
    solver_settings=(("integrator", "0"),),
)


class FakeBackend:
    """A backend whose 'physics' is one explicit rule, so outcomes are exactly predictable.

    The modelled world: the configuration is unsafe when its first coordinate exceeds
    `violation_above`, and the reported distance falls linearly past that threshold.
    """

    def __init__(
        self,
        *,
        violation_above: float = float("inf"),
        provenance: SimulationProvenance = PROVENANCE,
        raise_at: int | None = None,
        raise_on_provenance: bool = False,
    ) -> None:
        self._violation_above = violation_above
        self._provenance = provenance
        self._raise_at = raise_at
        self._raise_on_provenance = raise_on_provenance
        self.configurations: list[tuple[float, ...]] = []
        self.controls: list[tuple[float, ...] | None] = []
        self.steps_taken = 0

    @property
    def provenance(self) -> SimulationProvenance:
        if self._raise_on_provenance:
            raise RuntimeError("model not loaded")
        return self._provenance

    def set_configuration(
        self, q: Sequence[float], *, control: Sequence[float] | None = None
    ) -> None:
        if self._raise_at is not None and len(self.configurations) == self._raise_at:
            raise RuntimeError("simulator exploded")
        self.configurations.append(tuple(q))
        self.controls.append(None if control is None else tuple(control))

    def step(self, steps: int = 1) -> None:
        self.steps_taken += steps

    def _distance(self) -> float:
        return 0.04 - (self.configurations[-1][0] - self._violation_above)

    def get_joint_state(self) -> JointState:
        current = self.configurations[-1]
        return JointState(positions=current, velocities=tuple(0.0 for _ in current))

    def get_contacts(self) -> tuple[ContactRecord, ...]:
        if self.configurations[-1][0] <= self._violation_above:
            return ()
        return (ContactRecord("link", "obstacle", self._distance()),)

    def get_minimum_distance(self) -> float | None:
        contacts = self.get_contacts()
        return None if not contacts else contacts[0].distance

    def get_actuator_forces(self) -> tuple[float, ...]:
        return tuple(10.0 * value for value in self.configurations[-1])


def test_fake_backend_satisfies_the_protocol() -> None:
    assert isinstance(FakeBackend(), SimulationBackend)


def test_sampling_is_deterministic_for_a_fixed_seed() -> None:
    region = ((-1.0, 1.0), (0.0, 0.5))
    assert sample_configurations(region, 8, 7) == sample_configurations(region, 8, 7)
    assert sample_configurations(region, 8, 7) != sample_configurations(region, 8, 8)


@pytest.mark.parametrize("generated", [[], [(float("nan"),)], [(2.0,)], [(0.0, 0.0)]])
def test_corrupt_samples_fail_before_backend_mutation(
    generated: list[tuple[float, ...]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "robocert.simulation.falsification.sample_configurations",
        lambda *args: generated,
    )
    backend = FakeBackend()
    report = search_for_counterexample(
        backend=backend,
        region=((0.0, 1.0),),
        property=no_penetration(),
        samples=1,
        seed=1,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    assert backend.configurations == []
    report.digest()


def test_samples_stay_inside_the_region() -> None:
    region = ((-1.0, 1.0), (0.25, 0.5))
    for configuration in sample_configurations(region, 64, 11):
        for value, (low, high) in zip(configuration, region, strict=True):
            assert low <= value <= high


def test_repeated_searches_with_one_seed_agree() -> None:
    region = ((0.0, 1.0), (0.0, 1.0))
    reports = [
        search_for_counterexample(
            backend=FakeBackend(violation_above=0.8),
            region=region,
            property=no_penetration(),
            samples=50,
            seed=4242,
        )
        for _ in range(2)
    ]
    assert reports[0].to_dict() == reports[1].to_dict()
    assert reports[0].digest() == reports[1].digest()


def test_a_planted_violation_is_found_and_reported() -> None:
    backend = FakeBackend(violation_above=0.5)
    report = search_for_counterexample(
        backend=backend,
        region=((0.0, 1.0), (0.0, 1.0)),
        property=no_penetration(),
        samples=100,
        seed=1,
    )
    assert report.outcome is FalsificationOutcome.COUNTEREXAMPLE_FOUND
    assert len(report.violations) == 1
    violation = report.violations[0]
    assert violation.configuration[0] > 0.5
    assert violation.observation.contacts[0].distance < 0.0
    assert report.samples_evaluated == violation.sample_index + 1
    assert any("does not falsify a RoboCert claim" in item for item in report.diagnostics)


def test_no_counterexample_is_not_a_positive_result() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(),
        region=((0.0, 1.0),),
        property=no_penetration(),
        samples=25,
        seed=3,
    )
    assert report.outcome is FalsificationOutcome.NO_COUNTEREXAMPLE_FOUND
    assert report.samples_evaluated == 25
    assert any("not evidence that the property holds" in item for item in report.diagnostics)


def test_backend_exception_fails_closed() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(raise_at=3),
        region=((0.0, 1.0),),
        property=no_penetration(),
        samples=25,
        seed=3,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    assert report.samples_evaluated == 3
    assert "RuntimeError" in report.diagnostics[0]


def test_unreadable_provenance_fails_closed() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(raise_on_provenance=True),
        region=((0.0, 1.0),),
        property=no_penetration(),
        samples=5,
        seed=3,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    assert report.provenance is None


def test_clearance_beyond_the_collision_margin_is_refused() -> None:
    backend = FakeBackend()
    report = search_for_counterexample(
        backend=backend,
        region=((0.0, 1.0),),
        property=minimum_distance_at_least(0.5),
        samples=25,
        seed=3,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    assert report.samples_evaluated == 0
    assert backend.configurations == []
    assert "collision" in report.diagnostics[0]


def test_clearance_within_the_collision_margin_runs() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(violation_above=0.5),
        region=((0.0, 1.0),),
        property=minimum_distance_at_least(0.05),
        samples=100,
        seed=5,
    )
    assert report.outcome is FalsificationOutcome.COUNTEREXAMPLE_FOUND


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), -0.1])
def test_invalid_property_thresholds_are_rejected(value: float) -> None:
    with pytest.raises(ValueError):
        minimum_distance_at_least(value)
    with pytest.raises(ValueError):
        actuator_force_within(value)


@pytest.mark.parametrize(
    ("region", "samples", "settle"),
    [
        ((), 10, 0),
        (((1.0, 0.0),), 10, 0),
        (((float("nan"), 1.0),), 10, 0),
        (((0.0, float("inf")),), 10, 0),
        (((0.0, 1.0),), 0, 0),
        (((0.0, 1.0),), 10, -1),
    ],
)
def test_malformed_search_arguments_fail_closed(
    region: tuple[tuple[float, float], ...], samples: int, settle: int
) -> None:
    report = search_for_counterexample(
        backend=FakeBackend(),
        region=region,
        property=no_penetration(),
        samples=samples,
        seed=1,
        settle_steps=settle,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    report.digest()  # even malformed inputs produce a serializable failure record


def test_a_property_that_does_not_return_bool_fails_closed() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(),
        region=((0.0, 1.0),),
        property=SimulationProperty("malformed", lambda observation: 1),  # type: ignore[arg-type]
        samples=2,
        seed=1,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    assert "return bool" in report.diagnostics[0]


def test_settle_steps_and_actuator_command_reach_the_backend() -> None:
    backend = FakeBackend()
    search_for_counterexample(
        backend=backend,
        region=((0.0, 1.0),),
        property=actuator_force_within(1000.0),
        samples=3,
        seed=1,
        settle_steps=4,
        command_actuators=True,
    )
    assert backend.steps_taken == 12
    assert backend.controls == backend.configurations


def test_actuator_force_property_detects_an_over_torqued_sample() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(),
        region=((0.0, 1.0),),
        property=actuator_force_within(5.0),
        samples=100,
        seed=9,
    )
    assert report.outcome is FalsificationOutcome.COUNTEREXAMPLE_FOUND
    assert abs(report.violations[0].observation.actuator_forces[0]) > 5.0


def test_region_from_box_domain_preserves_component_order() -> None:
    domain = BoxDomain(
        "Q",
        components=(
            IntervalDomain("Q.q1", "q1", Rational(-1, 2), Rational(3, 4), unit=Unit.RADIAN),
            IntervalDomain("Q.q2", "q2", Rational(0), Rational(1, 8), unit=Unit.RADIAN),
        ),
    )
    assert region_from_box_domain(domain) == ((-0.5, 0.75), (0.0, 0.125))


def test_region_from_sequence_normalizes_to_float_pairs() -> None:
    assert region_from_sequence([[0, 1], (2, 3)]) == ((0.0, 1.0), (2.0, 3.0))


def test_report_serializes_to_canonical_json_without_raw_floats() -> None:
    report = search_for_counterexample(
        backend=FakeBackend(violation_above=0.2),
        region=((0.0, 1.0), (0.0, 1.0)),
        property=no_penetration(),
        samples=50,
        seed=2,
    )
    payload = report.to_dict()
    encoded = canonical_json_bytes(payload)  # rejects float literals outright
    assert b'"outcome":"COUNTEREXAMPLE_FOUND"' in encoded
    assert str(report.digest()).startswith("sha256:")


def test_outcome_names_never_overlap_result_statuses() -> None:
    """A falsification outcome must not be mistakable for a certification status."""

    from robocert.results import ResultStatus

    outcomes = {member.value for member in FalsificationOutcome}
    assert outcomes.isdisjoint({member.value for member in ResultStatus})


_OBSERVATION = SimulationObservation(
    joint_state=JointState(positions=(0.0,), velocities=(0.0,)),
    contacts=(),
    minimum_distance=None,
    actuator_forces=(),
)

BRIDGE_MODEL_HASH = digest_json({"model": "bridge"})


def test_candidate_assignment_is_exact_by_default() -> None:
    """0.1 is not one tenth in binary. The default conversion says so instead of rounding."""

    assignment = candidate_assignment(Violation(0, (0.1, -0.25), _OBSERVATION), ("q1", "q2"))
    assert Fraction(assignment["q1"].numerator, assignment["q1"].denominator) == Fraction(0.1)
    assert assignment["q2"] == Rational(-1, 4)


def test_candidate_assignment_can_round_for_readability() -> None:
    assignment = candidate_assignment(
        Violation(0, (0.1, -0.25), _OBSERVATION), ("q1", "q2"), max_denominator=100
    )
    assert assignment["q1"] == Rational(1, 10)


def test_candidate_assignment_rejects_a_length_mismatch() -> None:
    with pytest.raises(ValueError, match="variable ids"):
        candidate_assignment(Violation(0, (0.1, 0.2), _OBSERVATION), ("q1",))


def test_candidate_assignment_rejects_ambiguous_or_invalid_reconstruction() -> None:
    violation = Violation(0, (0.1, 0.2), _OBSERVATION)
    with pytest.raises(ValueError, match="unique"):
        candidate_assignment(violation, ("q", "q"))
    with pytest.raises(ValueError, match="positive integer"):
        candidate_assignment(violation, ("q1", "q2"), max_denominator=0)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: JointState((float("nan"),), (0.0,)),
        lambda: ContactRecord("link", "obstacle", float("inf")),
        lambda: SimulationObservation(JointState((0.0,), (0.0,)), (), None, (float("nan"),)),
        lambda: SimulationProvenance("fake", "0", "0" * 64, 0.0, 0.05),
        lambda: SimulationProvenance("fake", "0", "not-a-hash", 0.002, 0.05),
    ],
)
def test_nonfinite_or_malformed_simulation_records_are_rejected(
    factory: Callable[[], object],
) -> None:
    with pytest.raises(ValueError):
        factory()


def test_a_simulator_lead_becomes_a_counterexample_only_after_exact_recheck(
    make_universal_claim: Callable[..., Claim],
) -> None:
    """The full bridge: the search proposes, `refutation` decides, `results` promotes.

    Note the direction. The simulation layer never calls the refutation machinery; it hands
    over a candidate point, and the trusted core re-derives everything from the claim alone.
    """

    claim = make_universal_claim(variable_ids=("q1", "q2"))
    report = search_for_counterexample(
        backend=FakeBackend(violation_above=0.5),
        region=((-1.0, 1.0), (-1.0, 1.0)),
        property=no_penetration(),
        samples=100,
        seed=17,
    )
    assert report.outcome is FalsificationOutcome.COUNTEREXAMPLE_FOUND

    assignment = candidate_assignment(report.violations[0], ("q1", "q2"))
    refutation = refute(claim, BRIDGE_MODEL_HASH, assignment)
    assert refutation.accepted, refutation.diagnostics
    assert refutation.checked_counterexample is not None

    result = counterexample_result(refutation.checked_counterexample)
    assert result.status is ResultStatus.COUNTEREXAMPLE
    assert result.claim_hash == claim.digest()


def test_a_lead_that_does_not_survive_the_recheck_is_not_promoted(
    make_universal_claim: Callable[..., Claim],
) -> None:
    """A candidate outside the claim's declared domain refutes nothing and must not pass."""

    claim = make_universal_claim(variable_ids=("q1", "q2"))
    outside = {"q1": Rational(9), "q2": Rational(0)}  # the domain is [-1, 1]
    refutation = refute(claim, BRIDGE_MODEL_HASH, outside)
    assert not refutation.accepted
    assert refutation.checked_counterexample is None


def test_a_simulator_violation_need_not_violate_the_claim(
    make_universal_claim: Callable[..., Claim],
) -> None:
    """The two models are different models, and the bridge must not paper over that.

    Here the simulator's property fails at a point where the claim's formula is true. The
    honest outcome is a rejection, not a counterexample.
    """

    claim = make_universal_claim(variable_ids=("q1", "q2"))
    satisfying = {"q1": Rational(-1, 4), "q2": Rational(0)}  # q1 <= 1/2 holds here
    refutation = refute(claim, BRIDGE_MODEL_HASH, satisfying)
    assert not refutation.accepted
    assert "not a counterexample" in refutation.diagnostics[0]


def test_a_radian_sample_composes_through_the_half_angle_transport(
    make_universal_claim: Callable[..., Claim],
) -> None:
    """The composition the shipped example cannot yet run, on a claim that can receive it.

    `make_universal_claim` is a plain `t`-box claim, so the transport is the only coordinate
    change involved. What this pins down is the plumbing -- radians in, exact rationals out,
    `refute` deciding -- not any statement about planar-2R geometry.
    """

    claim = make_universal_claim(variable_ids=("t1", "t2"))
    violation = Violation(0, (1.2, 0.1), _OBSERVATION)  # radians

    assignment = candidate_assignment(violation, ("t1", "t2"), transform=angle_to_t_candidate)

    # tan(0.6) is about 0.684, inside the claim's [-1, 1] box and above its 1/2 threshold.
    refutation = refute(claim, BRIDGE_MODEL_HASH, assignment)
    assert refutation.accepted, refutation.diagnostics
    counterexample = refutation.checked_counterexample
    assert counterexample is not None

    # The witness denotes an angle, and it is the one that was sampled.
    reported = dict(counterexample.assignment)
    recovered = t_to_angle(Fraction(reported["t1"].numerator, reported["t1"].denominator))
    assert recovered == pytest.approx(1.2, abs=1e-9)


def test_the_transport_refuses_an_angle_the_chart_cannot_represent() -> None:
    """A transform that raises must propagate, not silently yield a wrong configuration."""

    with pytest.raises(ValueError, match="strictly inside"):
        candidate_assignment(
            Violation(0, (math.pi, 0.0), _OBSERVATION),
            ("t1", "t2"),
            transform=angle_to_t_candidate,
        )


def test_a_transform_returning_an_inexact_value_is_refused() -> None:
    with pytest.raises(ValueError, match="exact Fraction"):
        candidate_assignment(
            Violation(0, (0.5, 0.5), _OBSERVATION),
            ("t1", "t2"),
            transform=lambda value: value,  # type: ignore[arg-type,return-value]
        )


def test_the_report_digest_covers_the_whole_provenance_record() -> None:
    """Provenance is inside the hash, so reports from different models or asset trees
    cannot collide. Checked without MuJoCo so it holds for any backend."""

    from dataclasses import replace

    base = search_for_counterexample(
        backend=FakeBackend(violation_above=0.5),
        region=((0.0, 1.0),),
        property=no_penetration(),
        samples=20,
        seed=3,
    )
    assert base.provenance is not None

    variants = [
        replace(base.provenance, model_sha256="1" * 64),
        replace(base.provenance, model_external_references=("meshes/link1.stl",)),
        replace(base.provenance, timestep=0.001),
        replace(base.provenance, collision_margin=0.04),
    ]
    digests = {replace(base, provenance=variant).digest() for variant in variants}
    assert base.digest() not in digests
    assert len(digests) == len(variants)
