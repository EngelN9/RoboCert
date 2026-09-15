"""MuJoCo adapter. The only module in RoboCert that imports `mujoco`.

MuJoCo is an untrusted **search** backend, on the far left of
`search -> certificate construction -> independent checker` (docs/architecture/backends.md).
It simulates a higher-fidelity physical model than the algebraic one RoboCert certifies, which
is exactly what makes it useful for falsification and exactly what disqualifies it from
supporting a certificate: a contact it reports is a fact about MuJoCo's model, not RoboCert's.

Nothing here can reach `robocert.checking` or `robocert.results`; the subpackage imports
neither, and `tests/test_simulation_boundary.py` enforces that mechanically.

Install with the optional extra:

    pip install "robocert[mujoco]"
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from robocert.simulation.backend import (
    ContactRecord,
    JointState,
    SimulationProvenance,
)

try:
    import mujoco
except ImportError as exc:  # pragma: no cover - only reachable without the extra installed
    raise ImportError(
        "robocert.simulation.mujoco_backend requires the optional 'mujoco' extra; "
        'install it with: pip install "robocert[mujoco]"'
    ) from exc

BACKEND_ID = "mujoco"


class MujocoBackend:
    """A loaded MJCF model, posable and steppable. Implements `SimulationBackend`.

    Construct through `load_model`; the constructor is not a supported entry point.
    """

    def __init__(self, model: Any, data: Any, provenance: SimulationProvenance) -> None:
        self._model = model
        self._data = data
        self._provenance = provenance

    @property
    def provenance(self) -> SimulationProvenance:
        return self._provenance

    @property
    def degrees_of_freedom(self) -> int:
        return int(self._model.nq)

    def set_configuration(
        self, q: Sequence[float], *, control: Sequence[float] | None = None
    ) -> None:
        """Write `q` into `qpos`, zero velocities, optionally set `ctrl`, refresh state.

        `mj_forward` runs collision detection without advancing time, so contacts and
        distances are observable at the pose the search chose rather than one the dynamics
        drifted into.
        """

        if len(q) != int(self._model.nq):
            raise ValueError(
                f"configuration has {len(q)} coordinates but the model has {int(self._model.nq)}"
            )
        if control is not None and len(control) != int(self._model.nu):
            raise ValueError(
                f"control has {len(control)} entries but the model has "
                f"{int(self._model.nu)} actuators"
            )
        positions = tuple(float(value) for value in q)
        controls = None if control is None else tuple(float(value) for value in control)
        if any(not math.isfinite(value) for value in positions):
            raise ValueError("configuration must be finite")
        if controls is not None and any(not math.isfinite(value) for value in controls):
            raise ValueError("control must be finite")
        self._data.qpos[:] = positions
        self._data.qvel[:] = [0.0] * int(self._model.nv)
        if controls is not None:
            self._data.ctrl[:] = controls
        mujoco.mj_forward(self._model, self._data)

    def step(self, steps: int = 1) -> None:
        if steps < 0:
            raise ValueError("step count cannot be negative")
        for _ in range(steps):
            mujoco.mj_step(self._model, self._data)

    def get_joint_state(self) -> JointState:
        return JointState(
            positions=tuple(float(value) for value in self._data.qpos),
            velocities=tuple(float(value) for value in self._data.qvel),
        )

    def _geom_name(self, geom_id: int) -> str:
        name = mujoco.mj_id2name(self._model, mujoco.mjtObj.mjOBJ_GEOM, int(geom_id))
        return str(name) if name else f"geom:{int(geom_id)}"

    def get_contacts(self) -> tuple[ContactRecord, ...]:
        """Contact pairs MuJoCo currently reports.

        Only pairs inside the model's collision margin appear. An empty result means
        "nothing within margin", not "nothing near".
        """

        records: list[ContactRecord] = []
        for index in range(int(self._data.ncon)):
            contact = self._data.contact[index]
            geom_a, geom_b = (int(value) for value in contact.geom)
            records.append(
                ContactRecord(
                    geom_a=self._geom_name(geom_a),
                    geom_b=self._geom_name(geom_b),
                    distance=float(contact.dist),
                )
            )
        return tuple(records)

    def get_minimum_distance(self) -> float | None:
        contacts = self.get_contacts()
        if not contacts:
            return None
        return min(contact.distance for contact in contacts)

    def get_actuator_forces(self) -> tuple[float, ...]:
        return tuple(float(value) for value in self._data.actuator_force)


def _solver_settings(model: Any) -> tuple[tuple[str, str], ...]:
    options = model.opt
    return (
        ("integrator", str(int(options.integrator))),
        ("solver", str(int(options.solver))),
        ("iterations", str(int(options.iterations))),
        ("cone", str(int(options.cone))),
        ("jacobian", str(int(options.jacobian))),
        ("tolerance", repr(float(options.tolerance))),
    )


def _declared_external_references(xml_text: str) -> tuple[str, ...]:
    """Paths this MJCF declares that live outside it: includes, meshes, textures.

    Read off the XML as declared, without resolving `meshdir`/`assetdir` or following
    nested includes -- a half-correct resolution would be a worse provenance record than an
    honest list of what was referenced. An empty result means the entry file is the whole
    model, which is the only case where its digest identifies the model completely.
    """

    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        # MuJoCo already parsed this file, so a failure here means the two parsers disagree.
        # Fail closed rather than record "no external references" on an unread document.
        raise ValueError(
            "MJCF could not be re-parsed for provenance scanning; refusing to record a "
            "model digest whose completeness is unknown"
        ) from None
    return tuple(
        sorted({element.get("file", "") for element in root.iter()} - {""}),
    )


def load_model(path: Path | str, *, timestep: float | None = None) -> MujocoBackend:
    """Load an MJCF file and return a posable backend bound to it.

    `model_sha256` digests the bytes of THIS file only. When the file pulls in `<include>`
    files or mesh assets, those paths are recorded in
    `SimulationProvenance.model_external_references` so a report never claims the digest
    identifies more than it does; an empty list there means the model is self-contained.
    """

    if timestep is not None and (not math.isfinite(timestep) or timestep <= 0.0):
        raise ValueError("timestep must be positive and finite")
    source = Path(path)
    raw = source.read_bytes()
    model = mujoco.MjModel.from_xml_path(str(source))
    if timestep is not None:
        if timestep <= 0.0:
            raise ValueError("timestep must be positive")
        model.opt.timestep = timestep
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)

    margins = [float(value) for value in model.geom_margin]
    provenance = SimulationProvenance(
        backend_id=BACKEND_ID,
        backend_version=str(mujoco.__version__),
        model_sha256=hashlib.sha256(raw).hexdigest(),
        timestep=float(model.opt.timestep),
        collision_margin=min(margins) if margins else 0.0,
        solver_settings=_solver_settings(model),
        model_external_references=_declared_external_references(raw.decode("utf-8")),
    )
    return MujocoBackend(model, data, provenance)


__all__ = ["BACKEND_ID", "MujocoBackend", "load_model"]
