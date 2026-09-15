#!/usr/bin/env python3
"""Falsify a candidate safe joint region for the planar-2R MJCF model.

Run:

    python examples/simulation/falsify_planar_2r.py [output-directory]

Two candidate regions are attacked with the same seed and sample count:

  * `optimistic` claims 20 mm clearance from the obstacle over a joint box that in fact
    sweeps the arm straight through it. MuJoCo finds a violating configuration.
  * `conservative` keeps the arm folded away from the obstacle. MuJoCo finds nothing --
    which establishes NOTHING about the region. It is a failed refutation, not a proof.

Each search writes a structured report. The report is what a later, rigorous stage would
consume: a violating configuration is a *lead* for exact re-validation against RoboCert's
algebraic model, and only that exact re-validation could ever justify a RoboCert
`COUNTEREXAMPLE`. Nothing here touches `robocert.certify` or `robocert.check`.

That re-validation is `robocert.refutation.refute`, and this example deliberately stops
short of it -- for a mathematical reason, not a missing helper. `refute` needs a claim whose
quantifier prefix is purely universal, and the planar-2R claim RoboCert can build
(`kinematics2r.build_planar2r_claim`) is an `exists (t1, t2)` claim carrying exact
forward-kinematics equalities. Dropping those equalities to universally quantify the box
would detach the second-segment clearance conjunct from the conjunction that gives it
meaning, which P2 Remark 9.5 proves unsound. See `research/ATTEMPTS.md` A-003.

The coordinate transport itself is solved and shipped:
`witness_search2r.angle_to_t_candidate` turns a sampled radian into an exact rational
`t = tan(q/2)`, and `candidate_assignment(..., transform=...)` composes it. What is missing
is a universally quantified claim for a transported point to refute. The plumbing is
exercised in
`tests/test_simulation.py::test_a_radian_sample_composes_through_the_half_angle_transport`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from robocert.artifacts import canonical_json_bytes
from robocert.simulation import (
    FalsificationOutcome,
    FalsificationReport,
    Region,
    minimum_distance_at_least,
    search_for_counterexample,
)

MODEL = Path(__file__).parent / "planar_2r.xml"
SEED = 20260831
SAMPLES = 200
REQUIRED_CLEARANCE = 0.02  # metres; must not exceed the MJCF's geom margin (0.05 m)

CANDIDATE_REGIONS: dict[str, Region] = {
    # (q1_low, q1_high), (q2_low, q2_high) in radians.
    "optimistic": ((0.2, 0.9), (-0.2, 0.6)),
    "conservative": ((-1.2, -0.4), (-1.2, -0.4)),
}


def describe(name: str, report: FalsificationReport) -> str:
    lines = [f"{report.outcome.value}  ({name})"]
    for violation in report.violations:
        joints = ", ".join(f"{value:.6f}" for value in violation.configuration)
        distance = violation.observation.minimum_distance
        lines.append(f"  q = ({joints})")
        lines.append(f"  minimum reported distance = {distance}")
    for diagnostic in report.diagnostics:
        lines.append(f"  {diagnostic}")
    lines.append(f"  report digest = {report.digest()}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    try:
        from robocert.simulation.mujoco_backend import load_model
    except ImportError as exc:
        print(f"{exc}", file=sys.stderr)
        return 2

    out_dir = Path(argv[1]) if len(argv) > 1 else Path("run/simulation")
    out_dir.mkdir(parents=True, exist_ok=True)

    backend = load_model(MODEL)
    print(f"model {MODEL.name}  mujoco {backend.provenance.backend_version}")
    print(f"model sha256 {backend.provenance.model_sha256}")
    print(f"collision margin {backend.provenance.collision_margin} m\n")

    exit_code = 0
    for name, region in CANDIDATE_REGIONS.items():
        report = search_for_counterexample(
            backend=backend,
            region=region,
            property=minimum_distance_at_least(REQUIRED_CLEARANCE),
            samples=SAMPLES,
            seed=SEED,
        )
        destination = out_dir / f"{name}.falsification.json"
        destination.write_bytes(canonical_json_bytes(report.to_dict()))
        print(describe(name, report))
        print(f"  written to {destination}\n")
        if report.outcome is FalsificationOutcome.SIMULATION_ERROR:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
