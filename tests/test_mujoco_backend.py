"""MuJoCo adapter tests. Skipped entirely when the optional extra is not installed.

The core suite must pass without MuJoCo, so nothing here may be imported at collection time
by any other test module.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

mujoco = pytest.importorskip("mujoco")

from robocert.simulation import (  # noqa: E402  (must follow importorskip)
    FalsificationOutcome,
    minimum_distance_at_least,
    no_penetration,
    observe,
    search_for_counterexample,
)
from robocert.simulation.mujoco_backend import (  # noqa: E402
    BACKEND_ID,
    MujocoBackend,
    load_model,
)

MODEL_PATH = Path(__file__).resolve().parents[1] / "examples" / "simulation" / "planar_2r.xml"

# Poses chosen from the example model's geometry: the obstacle sits where the arm sweeps at
# small positive q1, and is out of reach when both joints are folded back.
COLLIDING = (0.5, 0.0)
CLEAR = (-1.0, -1.0)


@pytest.fixture
def backend() -> MujocoBackend:
    return load_model(MODEL_PATH)


def test_provenance_records_everything_needed_to_replay(backend: MujocoBackend) -> None:
    provenance = backend.provenance
    assert provenance.backend_id == BACKEND_ID
    assert provenance.backend_version == mujoco.__version__
    assert len(provenance.model_sha256) == 64
    assert provenance.timestep > 0.0
    assert provenance.collision_margin == pytest.approx(0.05)
    assert dict(provenance.solver_settings).keys() >= {"integrator", "solver", "iterations"}


def test_model_hash_matches_the_file_on_disk(backend: MujocoBackend) -> None:
    assert backend.provenance.model_sha256 == hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()


def test_timestep_override_is_recorded() -> None:
    assert load_model(MODEL_PATH, timestep=0.001).provenance.timestep == pytest.approx(0.001)


def test_configuration_round_trips(backend: MujocoBackend) -> None:
    backend.set_configuration(CLEAR)
    state = backend.get_joint_state()
    assert state.positions == pytest.approx(CLEAR)
    assert state.velocities == pytest.approx((0.0, 0.0))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_inputs_preserve_engine_state(backend: MujocoBackend, value: float) -> None:
    backend.set_configuration(CLEAR, control=CLEAR)
    before = backend.get_joint_state()
    control_before = tuple(backend._data.ctrl)
    for q, control in [((value, 0.0), CLEAR), ((0.0, 0.0), (value, 0.0))]:
        with pytest.raises(ValueError, match="finite"):
            backend.set_configuration(q, control=control)
        assert backend.get_joint_state() == before
        assert tuple(backend._data.ctrl) == control_before


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), 0.0, -1.0])
def test_invalid_timestep_rejected_before_loading(value: float) -> None:
    with pytest.raises(ValueError, match="positive and finite"):
        load_model("nonexistent-model.xml", timestep=value)


def test_wrong_configuration_length_is_rejected(backend: MujocoBackend) -> None:
    with pytest.raises(ValueError):
        backend.set_configuration((0.0, 0.0, 0.0))


def test_wrong_control_length_is_rejected(backend: MujocoBackend) -> None:
    with pytest.raises(ValueError):
        backend.set_configuration((0.0, 0.0), control=(0.0,))


def test_a_colliding_pose_reports_penetrating_contacts(backend: MujocoBackend) -> None:
    backend.set_configuration(COLLIDING)
    observation = observe(backend)
    assert observation.contacts
    assert observation.minimum_distance is not None
    assert observation.minimum_distance < 0.0
    assert {"obstacle"} <= {contact.geom_b for contact in observation.contacts}


def test_a_clear_pose_reports_no_distance_rather_than_a_large_one(backend: MujocoBackend) -> None:
    backend.set_configuration(CLEAR)
    observation = observe(backend)
    assert observation.contacts == ()
    assert observation.minimum_distance is None  # unknown, deliberately not `inf`


def test_commanded_actuators_report_gravity_load(backend: MujocoBackend) -> None:
    backend.set_configuration((0.0, 0.0), control=(0.0, 0.0))
    backend.step(50)
    forces = backend.get_actuator_forces()
    assert len(forces) == 2
    assert abs(forces[0]) > 1.0  # the arm is horizontal under gravity, so q1 is loaded


def test_search_finds_a_violation_in_an_optimistic_region(backend: MujocoBackend) -> None:
    report = search_for_counterexample(
        backend=backend,
        region=((0.2, 0.9), (-0.2, 0.6)),
        property=minimum_distance_at_least(0.02),
        samples=200,
        seed=20260831,
    )
    assert report.outcome is FalsificationOutcome.COUNTEREXAMPLE_FOUND
    assert report.violations[0].observation.minimum_distance is not None


def test_search_is_reproducible_at_a_fixed_seed(backend: MujocoBackend) -> None:
    kwargs = {
        "region": ((0.2, 0.9), (-0.2, 0.6)),
        "property": minimum_distance_at_least(0.02),
        "samples": 200,
        "seed": 20260831,
    }
    first = search_for_counterexample(backend=backend, **kwargs)
    second = search_for_counterexample(backend=backend, **kwargs)
    assert first.digest() == second.digest()


def test_search_finds_nothing_in_a_folded_back_region(backend: MujocoBackend) -> None:
    report = search_for_counterexample(
        backend=backend,
        region=((-1.2, -0.4), (-1.2, -0.4)),
        property=no_penetration(),
        samples=200,
        seed=20260831,
    )
    assert report.outcome is FalsificationOutcome.NO_COUNTEREXAMPLE_FOUND
    assert report.samples_evaluated == 200


def test_clearance_beyond_the_models_margin_is_refused(backend: MujocoBackend) -> None:
    report = search_for_counterexample(
        backend=backend,
        region=((-1.2, -0.4), (-1.2, -0.4)),
        property=minimum_distance_at_least(0.20),
        samples=10,
        seed=1,
    )
    assert report.outcome is FalsificationOutcome.SIMULATION_ERROR
    assert report.samples_evaluated == 0


def test_a_self_contained_model_records_no_external_references(backend: MujocoBackend) -> None:
    """Empty means the digest identifies the whole model, which is the case worth having."""

    assert backend.provenance.model_external_references == ()


def test_a_model_pulling_in_another_file_says_so(tmp_path: Path) -> None:
    """The provenance gap, closed by disclosure rather than by a silent partial hash.

    `model_sha256` covers the entry file only. A model that includes another file is not
    identified by that digest, and the report must not imply otherwise.
    """

    included = tmp_path / "shared_defaults.xml"
    included.write_text(
        '<mujocoinclude><default><geom margin="0.05"/></default></mujocoinclude>',
        encoding="utf-8",
    )
    entry = tmp_path / "arm.xml"
    entry.write_text(
        '<mujoco model="included">'
        '<compiler angle="radian"/>'
        '<include file="shared_defaults.xml"/>'
        '<worldbody><body name="link"><joint name="q" type="hinge" axis="0 1 0"/>'
        '<geom name="g" type="capsule" fromto="0 0 0 0.2 0 0" size="0.02" mass="1"/>'
        "</body></worldbody></mujoco>",
        encoding="utf-8",
    )

    provenance = load_model(entry).provenance
    assert provenance.model_external_references == ("shared_defaults.xml",)
    # The digest still covers only the entry file, which is exactly what the list discloses.
    assert provenance.model_sha256 == hashlib.sha256(entry.read_bytes()).hexdigest()


def test_the_report_digest_is_bound_to_the_backend_version(backend: MujocoBackend) -> None:
    """Two reports from different MuJoCo builds must not be conflatable.

    Cross-version reproducibility is not claimed, so the version has to be inside the hash;
    otherwise two searches that genuinely disagree could present the same digest.
    """

    from dataclasses import replace

    report = search_for_counterexample(
        backend=backend,
        region=((0.2, 0.9), (-0.2, 0.6)),
        property=minimum_distance_at_least(0.02),
        samples=50,
        seed=7,
    )
    assert report.provenance is not None
    other_version = replace(report.provenance, backend_version="0.0.0-other")
    assert replace(report, provenance=other_version).digest() != report.digest()
