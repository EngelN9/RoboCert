"""Typed interface for physics-simulation backends. Untrusted by construction.

Nothing in this subpackage is part of the trusted computing base. A simulation backend
observes a *physics model*, which is a different mathematical object from the algebraic
model RoboCert certifies. Its observations are evidence for a search, never a certificate,
and never an input to `robocert.checking`.

Two properties of the types here exist for soundness rather than convenience.

`get_minimum_distance` returns `float | None`, and `None` means "no geometry pair lies
inside the model's collision margin, so the distance was never computed". It does not mean
"far away". Returning `inf` would report a number the simulator never calculated, which is
exactly the kind of silent false negative a falsification search must not produce.

Every `to_dict` encodes floats as strings via `repr`. `robocert.artifacts` rejects float
literals in canonical JSON outright (`_validate_json`), so this is what lets a simulation
report be hashed by the same `digest_json` that hashes claims -- without smuggling binary
floating-point into a canonical artifact.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from robocert.artifacts import JSONValue

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _finite_tuple(values: Sequence[float], label: str) -> tuple[float, ...]:
    normalized = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in normalized):
        raise ValueError(f"{label} must contain only finite values")
    return normalized


def encode_float(value: float) -> str:
    """Canonical-JSON-safe encoding of a finite float as its exact `repr` string."""

    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError("simulation artifacts cannot encode non-finite floats")
    return repr(normalized)


@dataclass(frozen=True, slots=True)
class JointState:
    """Generalized positions and velocities, in the simulation model's own units."""

    positions: tuple[float, ...]
    velocities: tuple[float, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "positions", _finite_tuple(self.positions, "joint positions"))
        object.__setattr__(self, "velocities", _finite_tuple(self.velocities, "joint velocities"))
        if len(self.positions) != len(self.velocities):
            raise ValueError("joint positions and velocities must have equal length")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "positions": [encode_float(item) for item in self.positions],
            "velocities": [encode_float(item) for item in self.velocities],
        }


@dataclass(frozen=True, slots=True)
class ContactRecord:
    """One contact pair the simulator reported.

    `distance` follows MuJoCo's sign convention: negative is penetration, positive is a
    near-contact still inside the collision margin. A pair outside the margin produces no
    record at all, which is why absence of records is not evidence of separation.
    """

    geom_a: str
    geom_b: str
    distance: float

    def __post_init__(self) -> None:
        if not isinstance(self.geom_a, str) or not self.geom_a:
            raise ValueError("contact geom_a must be a non-empty string")
        if not isinstance(self.geom_b, str) or not self.geom_b:
            raise ValueError("contact geom_b must be a non-empty string")
        distance = float(self.distance)
        if not math.isfinite(distance):
            raise ValueError("contact distance must be finite")
        object.__setattr__(self, "distance", distance)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "geom_a": self.geom_a,
            "geom_b": self.geom_b,
            "distance": encode_float(self.distance),
        }


@dataclass(frozen=True, slots=True)
class SimulationObservation:
    """Everything one sample of the search observed, at one instant."""

    joint_state: JointState
    contacts: tuple[ContactRecord, ...]
    minimum_distance: float | None
    actuator_forces: tuple[float, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.joint_state, JointState):
            raise ValueError("simulation observation requires a JointState")
        contacts = tuple(self.contacts)
        if any(not isinstance(item, ContactRecord) for item in contacts):
            raise ValueError("simulation contacts must be ContactRecord values")
        object.__setattr__(self, "contacts", contacts)
        if self.minimum_distance is not None:
            minimum_distance = float(self.minimum_distance)
            if not math.isfinite(minimum_distance):
                raise ValueError("minimum distance must be finite when present")
            object.__setattr__(self, "minimum_distance", minimum_distance)
        object.__setattr__(
            self,
            "actuator_forces",
            _finite_tuple(self.actuator_forces, "actuator forces"),
        )

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "joint_state": self.joint_state.to_dict(),
            "contacts": [item.to_dict() for item in self.contacts],
            "minimum_distance": (
                None if self.minimum_distance is None else encode_float(self.minimum_distance)
            ),
            "actuator_forces": [encode_float(item) for item in self.actuator_forces],
        }


@dataclass(frozen=True, slots=True)
class SimulationProvenance:
    """What a reader needs to re-run this search and get the same samples.

    Reproducibility is claimed relative to the recorded backend version and platform, not
    across them: a physics engine is free to change its solver between releases.

    `model_sha256` digests the top-level model file only. `model_external_references` lists
    the paths that file pulls in -- includes, meshes, textures -- as they are declared in it.
    When that tuple is EMPTY the digest identifies the model completely. When it is not, the
    digest identifies only the entry file, and a report carrying it is reproducible solely
    alongside the same asset tree. The field exists so a report never silently claims more
    provenance than it has.
    """

    backend_id: str
    backend_version: str
    model_sha256: str
    timestep: float
    collision_margin: float
    solver_settings: tuple[tuple[str, str], ...] = ()
    model_external_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.backend_id, str) or not self.backend_id:
            raise ValueError("backend_id must be a non-empty string")
        if not isinstance(self.backend_version, str) or not self.backend_version:
            raise ValueError("backend_version must be a non-empty string")
        if not isinstance(self.model_sha256, str) or not _SHA256_PATTERN.fullmatch(
            self.model_sha256
        ):
            raise ValueError("model_sha256 must be 64 lowercase hexadecimal characters")
        timestep = float(self.timestep)
        collision_margin = float(self.collision_margin)
        if not math.isfinite(timestep) or timestep <= 0.0:
            raise ValueError("simulation timestep must be positive and finite")
        if not math.isfinite(collision_margin) or collision_margin < 0.0:
            raise ValueError("collision margin must be nonnegative and finite")
        settings = tuple(self.solver_settings)
        if any(
            not isinstance(item, tuple)
            or len(item) != 2
            or not all(isinstance(part, str) and part for part in item)
            for item in settings
        ):
            raise ValueError("solver settings must be non-empty string pairs")
        keys = tuple(key for key, _ in settings)
        if len(keys) != len(set(keys)):
            raise ValueError("solver setting keys must be unique")
        references = tuple(self.model_external_references)
        if any(not isinstance(item, str) or not item for item in references):
            raise ValueError("model external references must be non-empty strings")
        if len(references) != len(set(references)):
            raise ValueError("model external references must be unique")
        object.__setattr__(self, "model_external_references", tuple(sorted(references)))
        object.__setattr__(self, "timestep", timestep)
        object.__setattr__(self, "collision_margin", collision_margin)
        object.__setattr__(self, "solver_settings", settings)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "model_sha256": self.model_sha256,
            "timestep": encode_float(self.timestep),
            "collision_margin": encode_float(self.collision_margin),
            "solver_settings": [[key, value] for key, value in self.solver_settings],
            "model_external_references": list(self.model_external_references),
        }


@runtime_checkable
class SimulationBackend(Protocol):
    """A loaded physics model that can be posed, stepped, and observed.

    A backend instance always has a model loaded -- loading is the factory's job (see
    `mujoco_backend.load_model`), not a method that must be remembered before every other
    call.
    """

    @property
    def provenance(self) -> SimulationProvenance:
        """Version, model hash, timestep, and solver settings for this loaded model."""
        ...

    def set_configuration(
        self, q: Sequence[float], *, control: Sequence[float] | None = None
    ) -> None:
        """Place the model at configuration `q`, zero velocities, refresh derived state.

        `control` sets the actuator command. It matters for `get_actuator_forces`: a
        position actuator left at its default command reports the servo error torque, not
        the load the pose actually requires. Pass the commanded setpoint (often `q` itself)
        when the search is about actuator effort rather than geometry.
        """
        ...

    def step(self, steps: int = 1) -> None:
        """Advance the dynamics by `steps` timesteps."""
        ...

    def get_joint_state(self) -> JointState: ...

    def get_contacts(self) -> tuple[ContactRecord, ...]: ...

    def get_minimum_distance(self) -> float | None:
        """Smallest reported contact distance, or `None` if nothing is within margin."""
        ...

    def get_actuator_forces(self) -> tuple[float, ...]: ...


def observe(backend: SimulationBackend) -> SimulationObservation:
    """Collect one full observation from `backend` at its current state."""

    return SimulationObservation(
        joint_state=backend.get_joint_state(),
        contacts=backend.get_contacts(),
        minimum_distance=backend.get_minimum_distance(),
        actuator_forces=backend.get_actuator_forces(),
    )


__all__ = [
    "ContactRecord",
    "JointState",
    "SimulationBackend",
    "SimulationObservation",
    "SimulationProvenance",
    "encode_float",
    "observe",
]
