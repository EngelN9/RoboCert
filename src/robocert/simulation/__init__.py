"""Optional, untrusted physics-simulation and falsification layer.

Everything here sits in the FIRST layer of RoboCert's pipeline:

    search / simulation
            |
            v
    candidate or counterexample
            |
            v
    formal certificate construction
            |
            v
    independent checker
            |
            v
    CERTIFIED / REJECTED / UNKNOWN

A simulation observation never advances past the first arrow on its own. This subpackage
imports no part of `robocert.checking`, `robocert.results`, or `robocert.certificates`, so
there is no code path by which it can produce a `CERTIFIED_*` status. See
`docs/architecture/backends.md` and `docs/architecture/trusted-computing-base.md`.

`mujoco_backend` is deliberately NOT imported here: importing this subpackage must work
without the optional `mujoco` extra installed. Import it explicitly when you need it.
"""

from robocert.simulation.backend import (
    ContactRecord,
    JointState,
    SimulationBackend,
    SimulationObservation,
    SimulationProvenance,
    observe,
)
from robocert.simulation.falsification import (
    FalsificationOutcome,
    FalsificationReport,
    Region,
    SimulationProperty,
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

__all__ = [
    "ContactRecord",
    "FalsificationOutcome",
    "FalsificationReport",
    "JointState",
    "Region",
    "SimulationBackend",
    "SimulationObservation",
    "SimulationProperty",
    "SimulationProvenance",
    "Violation",
    "actuator_force_within",
    "candidate_assignment",
    "minimum_distance_at_least",
    "no_penetration",
    "observe",
    "region_from_box_domain",
    "region_from_sequence",
    "sample_configurations",
    "search_for_counterexample",
]
