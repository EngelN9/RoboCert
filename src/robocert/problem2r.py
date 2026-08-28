"""Parse the historical 0.1.0 planar-2R research problem format.

This parser performs a floating-point radian-to-half-angle transformation and is
deliberately not wired into the public CLI while the evidence gates are closed.

The input boundary. Every number arrives as a decimal string or an integer and
is converted with `Fraction`, which is exact for both -- `Fraction("7.8")` is
39/5, not a float approximation. JSON float literals are refused outright rather
than silently accepted, because a float here would propagate into predicate
coefficients and quietly leave the exact-arithmetic regime the whole design
depends on (AGENTS.md SS22.3).

Nothing in this module is trusted for certification.
"""

from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from robocert.certify2r import Planar2RProblem
from robocert.errors import ValidationError
from robocert.witness_search2r import joint_limits_to_t_bounds

SCHEMA_VERSION = "0.1.0"
_NUMBER_PATTERN = re.compile(r"^-?[0-9]+(\.[0-9]+)?(/[0-9]+)?$")
_PROBLEM_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")

# When no obstacle is given we still need the encoding's obstacle predicates to
# be satisfiable, so we place a token circle far outside any reachable point.
# This models "no obstacle was declared" -- it certifies nothing about whether
# the real workspace is clear.
_ABSENT_OBSTACLE_DISTANCE = Fraction(10**6)


def _exact(value: object, label: str) -> Fraction:
    """Convert an integer or decimal/rational string to an exact Fraction."""
    if isinstance(value, bool):
        raise ValidationError(f"{label} must be a number, not a boolean")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        raise ValidationError(
            f'{label} is a JSON float; write it as a string (e.g. "7.8") so it is '
            "parsed exactly rather than through binary floating point"
        )
    if isinstance(value, str) and _NUMBER_PATTERN.match(value):
        return Fraction(value)
    raise ValidationError(f"{label} must be an integer or a decimal/rational string")


def _require(mapping: object, key: str, label: str) -> Any:
    if not isinstance(mapping, dict):
        raise ValidationError(f"{label} must be a JSON object")
    if key not in mapping:
        raise ValidationError(f"{label} is missing required field {key!r}")
    return mapping[key]


def _pair(value: object, label: str) -> tuple[Fraction, Fraction]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValidationError(f"{label} must be a two-element array")
    return (_exact(value[0], f"{label}[0]"), _exact(value[1], f"{label}[1]"))


def parse_problem(document: object) -> tuple[Planar2RProblem, dict[str, Any]]:
    """Parse a problem document into a `Planar2RProblem` plus reporting metadata.

    The metadata carries the requested radian joint limits and the interval
    actually certified after inward rounding, so the report can state the
    difference rather than hide it.
    """
    if not isinstance(document, dict):
        raise ValidationError("problem document must be a JSON object")

    version = document.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"unsupported problem schema_version {version!r}; expected {SCHEMA_VERSION!r}"
        )

    problem_id = document.get("problem_id")
    if not isinstance(problem_id, str) or not _PROBLEM_ID_PATTERN.match(problem_id):
        raise ValidationError(
            "problem_id must start with a letter and use only letters, digits, '.', ':', '-', '_'"
        )

    robot = _require(document, "robot", "problem")
    if _require(robot, "kind", "robot") != "planar_2r":
        raise ValidationError("only robot.kind 'planar_2r' is supported")
    lengths = _require(robot, "link_lengths", "robot")
    l1, l2 = _pair(lengths, "robot.link_lengths")
    if l1 <= 0 or l2 <= 0:
        raise ValidationError("robot.link_lengths must both be strictly positive")

    limits = _require(document, "joint_limits", "problem")
    q1_lower, q1_upper = _pair(_require(limits, "q1", "joint_limits"), "joint_limits.q1")
    q2_lower, q2_upper = _pair(_require(limits, "q2", "joint_limits"), "joint_limits.q2")
    t1_bounds = joint_limits_to_t_bounds(q1_lower, q1_upper)
    t2_bounds = joint_limits_to_t_bounds(q2_lower, q2_upper)

    task = _require(document, "task", "problem")
    target = _pair(_require(task, "target", "task"), "task.target")

    margins = _require(document, "margins", "problem")
    clearance = _exact(_require(margins, "clearance", "margins"), "margins.clearance")
    epsilon = _exact(_require(margins, "singularity", "margins"), "margins.singularity")
    if clearance <= 0:
        raise ValidationError("margins.clearance must be strictly positive")
    if epsilon <= 0:
        raise ValidationError("margins.singularity must be strictly positive")
    if epsilon > abs(l1 * l2):
        raise ValidationError(
            f"margins.singularity ({epsilon}) exceeds |L1*L2| ({abs(l1 * l2)}); no "
            "configuration of this arm can satisfy it (proof P2 Corollary 5.4)"
        )

    obstacle = document.get("obstacle")
    obstacle_declared = obstacle is not None
    if obstacle_declared:
        if _require(obstacle, "kind", "obstacle") != "circle":
            raise ValidationError("only obstacle.kind 'circle' is supported")
        center = _pair(_require(obstacle, "center", "obstacle"), "obstacle.center")
        radius = _exact(_require(obstacle, "radius", "obstacle"), "obstacle.radius")
        if radius <= 0:
            raise ValidationError("obstacle.radius must be strictly positive")
    else:
        center = (_ABSENT_OBSTACLE_DISTANCE, _ABSENT_OBSTACLE_DISTANCE)
        radius = Fraction(1)

    problem = Planar2RProblem(
        l1=l1,
        l2=l2,
        target=target,
        obstacle_center=center,
        obstacle_radius=radius,
        clearance_margin=clearance,
        epsilon=epsilon,
        t1_bounds=t1_bounds,
        t2_bounds=t2_bounds,
        problem_id=problem_id,
    )
    metadata: dict[str, Any] = {
        "problem_id": problem_id,
        "obstacle_declared": obstacle_declared,
        "joint_limits_requested": {
            "q1": [str(q1_lower), str(q1_upper)],
            "q2": [str(q2_lower), str(q2_upper)],
        },
        "joint_limits_certified": {
            "q1": [
                2 * math.atan(float(t1_bounds[0])),
                2 * math.atan(float(t1_bounds[1])),
            ],
            "q2": [
                2 * math.atan(float(t2_bounds[0])),
                2 * math.atan(float(t2_bounds[1])),
            ],
        },
    }
    return problem, metadata


def load_problem(path: Path) -> tuple[Planar2RProblem, dict[str, Any]]:
    """Read and parse a problem file, rejecting JSON float literals."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read problem file {path}: {exc}") from exc
    try:
        document = json.loads(raw, parse_float=_reject_float)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"problem file is not valid JSON: {exc}") from exc
    return parse_problem(document)


def _reject_float(literal: str) -> Fraction:
    raise ValidationError(
        f"problem file contains the float literal {literal}; quote it as a string "
        f'("{literal}") so it is parsed exactly'
    )


__all__ = ["SCHEMA_VERSION", "load_problem", "parse_problem"]
