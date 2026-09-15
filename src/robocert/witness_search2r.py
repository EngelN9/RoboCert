"""Untrusted, research-only generation for the planar-2R exact-witness family.

This module is deliberately not wired into the public CLI.

Nothing here is part of the trusted computing base (AGENTS.md SS5.2/SS20): its job
is to produce a `Certificate` payload for `checkers.ExactWitnessChecker` to verify,
never to decide acceptance itself.

Two generation strategies live here.

`instance_from_witness` picks a rational witness first and derives the target
from it, so the instance is reachable by construction with zero rounding error.
Useful for benchmarks; useless for answering a user's question, since it
requires knowing the answer first.

`solve_reachable_targets` runs closed-form inverse kinematics for an
independently chosen target. The FK conjunct of the encoding is an EXACT
equality, and a rationally reconstructed witness essentially never satisfies an
exact equality -- so this does NOT hand the checker a witness for the requested
point. Instead it reconstructs a nearby rational witness and computes the exact
rational point that witness actually reaches. What then gets certified is
reachability of the achieved point, with the deviation from the requested point
reported as an exact rational. RC-003's attempt to add tolerance while keeping
the remaining conjuncts unchanged is refuted. RC-005 proposes an actual-endpoint
pose-tolerance encoding, but remains E0 and is not implemented here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

# Reconstruction ladder. Larger denominators put the achieved point nearer the
# request at the cost of bigger coefficients; the search walks this until the
# deviation stops improving materially.
_DENOMINATOR_LADDER: tuple[int, ...] = (10**3, 10**5, 10**7, 10**9, 10**12)

# Squared deviation treated as "close enough": 1e-9 in the problem's length
# unit, i.e. a nanometre for a metre-scale arm. Well below any manufacturing
# tolerance a real 2R arm has, so buying more precision only costs coefficient
# size. Callers can override per problem.
DEFAULT_TOLERANCE_SQUARED = Fraction(1, 10**18)


@dataclass(frozen=True)
class Planar2RInstance:
    l1: Fraction
    l2: Fraction
    x: Fraction
    y: Fraction
    t1: Fraction
    t2: Fraction


def instance_from_witness(
    l1: Fraction, l2: Fraction, t1: Fraction, t2: Fraction
) -> Planar2RInstance:
    """Derive (x, y) exactly from a chosen rational witness (t1, t2)."""
    d1 = 1 + t1 * t1
    d2 = 1 + t2 * t2
    cos_q1, sin_q1 = (1 - t1 * t1) / d1, 2 * t1 / d1
    cos_q2, sin_q2 = (1 - t2 * t2) / d2, 2 * t2 / d2
    x = l1 * cos_q1 + l2 * (cos_q1 * cos_q2 - sin_q1 * sin_q2)
    y = l1 * sin_q1 + l2 * (sin_q1 * cos_q2 + cos_q1 * sin_q2)
    return Planar2RInstance(l1=l1, l2=l2, x=x, y=y, t1=t1, t2=t2)


@dataclass(frozen=True, slots=True)
class WitnessCandidate:
    """A reconstructed rational witness and the point it exactly reaches.

    `deviation_squared` is the exact rational squared distance from the achieved
    point to the requested one -- exact because both are rationals, so a reader
    can confirm it with a calculator. It is NOT part of any certificate: it is a
    fact about two constants, not about the witness.
    """

    t1: Fraction
    t2: Fraction
    achieved: tuple[Fraction, Fraction]
    requested: tuple[Fraction, Fraction]
    deviation_squared: Fraction
    elbow_branch: str  # "up" | "down"


def _inverse_kinematics_branches(
    l1: float, l2: float, x: float, y: float
) -> list[tuple[float, float, str]]:
    """Closed-form planar-2R IK. Floats throughout -- untrusted by construction."""
    reach_squared = x * x + y * y
    denominator = 2.0 * l1 * l2
    if denominator == 0.0:
        return []
    cos_q2 = (reach_squared - l1 * l1 - l2 * l2) / denominator
    if not -1.0 <= cos_q2 <= 1.0:
        return []  # outside the annulus; no real solution
    q2_magnitude = math.acos(max(-1.0, min(1.0, cos_q2)))

    solutions: list[tuple[float, float, str]] = []
    for q2, branch in ((q2_magnitude, "up"), (-q2_magnitude, "down")):
        q1 = math.atan2(y, x) - math.atan2(l2 * math.sin(q2), l1 + l2 * math.cos(q2))
        # Normalize into (-pi, pi) so tan(q/2) is finite and the chart applies.
        q1 = math.atan2(math.sin(q1), math.cos(q1))
        solutions.append((q1, q2, branch))
        if q2_magnitude == 0.0:
            break  # the two branches coincide
    return solutions


def solve_reachable_targets(
    l1: Fraction,
    l2: Fraction,
    target: tuple[Fraction, Fraction],
    *,
    tolerance_squared: Fraction = DEFAULT_TOLERANCE_SQUARED,
) -> list[WitnessCandidate]:
    """Candidate rational witnesses near the IK solutions for `target`.

    Ordering deliberately prefers the COARSEST witness that lands within
    `tolerance_squared` of the request, not the most accurate one. Finer
    reconstruction buys deviation far below any physical relevance while
    inflating the rational coefficients -- and through the quartic forward
    kinematics that inflation is severe, producing certificates with
    fifty-digit numerators that are correct but hostile to audit. Certificate
    size is a stated evaluation metric (README SS24) and AGENTS.md SS7.3 warns
    against gratuitous coefficient growth. If nothing meets the tolerance, fall
    back to the most accurate candidate available.

    Emptiness means the float IK found nothing -- evidence of unreachability,
    NOT a proof of it, and it must never be reported as one.
    """
    x, y = target
    branches = _inverse_kinematics_branches(float(l1), float(l2), float(x), float(y))

    candidates: list[WitnessCandidate] = []
    for q1, q2, branch in branches:
        for limit in _DENOMINATOR_LADDER:
            # q = +-pi has no finite tan(q/2); skip rather than overflow.
            if abs(abs(q1) - math.pi) < 1e-12 or abs(abs(q2) - math.pi) < 1e-12:
                continue
            t1 = Fraction(math.tan(q1 / 2.0)).limit_denominator(limit)
            t2 = Fraction(math.tan(q2 / 2.0)).limit_denominator(limit)
            reached = instance_from_witness(l1, l2, t1, t2)
            achieved = (reached.x, reached.y)
            deviation = (achieved[0] - x) ** 2 + (achieved[1] - y) ** 2
            candidates.append(
                WitnessCandidate(
                    t1=t1,
                    t2=t2,
                    achieved=achieved,
                    requested=(x, y),
                    deviation_squared=deviation,
                    elbow_branch=branch,
                )
            )

    def coefficient_size(candidate: WitnessCandidate) -> int:
        return max(
            abs(candidate.t1.denominator),
            abs(candidate.t2.denominator),
            abs(candidate.achieved[0].denominator),
            abs(candidate.achieved[1].denominator),
        )

    within_tolerance = [c for c in candidates if c.deviation_squared <= tolerance_squared]
    if within_tolerance:
        within_tolerance.sort(key=lambda c: (coefficient_size(c), c.deviation_squared))
        return within_tolerance
    candidates.sort(key=lambda c: c.deviation_squared)
    return candidates


def joint_limits_to_t_bounds(
    q_lower: Fraction, q_upper: Fraction, *, denominator: int = 10**12
) -> tuple[Fraction, Fraction]:
    """Convert a radian joint interval to an exact rational `t = tan(q/2)` box,
    rounding INWARD.

    For generic rational radian limits `tan(q/2)` is irrational, so the exact
    rational `IntervalDomain` cannot represent the requested interval (proof P2
    SS3). Rounding inward makes the certified `t`-box a subset of the true
    `q`-box, so the direction of the approximation is:

        certified configurations  SUBSET OF  configurations you asked for

    which can only reject a valid witness near a limit (incomplete, and safe),
    never accept one outside the true limits (which would be unsound). This is
    the conservative-modeling direction AGENTS.md SS49 permits, stated explicitly
    rather than left implicit. Tracked as RC-004.

    Requires -pi < q_lower < q_upper < pi: the chart does not reach +-pi, and a
    caller wanting configurations there needs the four-chart driver instead.
    """
    if q_lower >= q_upper:
        raise ValueError("joint limit lower bound must be strictly below the upper bound")
    if not (-math.pi < float(q_lower) and float(q_upper) < math.pi):
        raise ValueError(
            "joint limits must lie strictly inside (-pi, pi); the half-angle chart "
            "cannot represent +-pi (see certify2r for four-chart coverage)"
        )

    lower_exact = math.tan(float(q_lower) / 2.0)
    upper_exact = math.tan(float(q_upper) / 2.0)

    # tan(q/2) is strictly increasing on (-pi, pi), so inward means: raise the
    # lower bound, lower the upper bound. limit_denominator can round either
    # way, so nudge and then assert the direction actually holds.
    lower = Fraction(lower_exact).limit_denominator(denominator)
    upper = Fraction(upper_exact).limit_denominator(denominator)
    step = Fraction(1, denominator)
    while float(lower) < lower_exact:
        lower += step
    while float(upper) > upper_exact:
        upper -= step

    if lower >= upper:
        raise ValueError(
            "joint limit interval is too narrow to represent exactly after inward "
            "rounding; widen the limits or raise the denominator"
        )
    return (lower, upper)


def angle_to_t_candidate(q: float, *, denominator: int = 10**12) -> Fraction:
    """Rational `t = tan(q/2)` candidate for a joint angle in radians.

    For generic radian angles `tan(q/2)` is irrational, so no exact rational equals it and
    this returns a nearby one. The returned `t` therefore denotes a slightly DIFFERENT
    configuration from `q`; `t_to_angle` reports which one.

    **This needs no rounding-direction argument, and that is worth saying explicitly because
    its sibling `joint_limits_to_t_bounds` does.** That function builds a DOMAIN, which
    nothing downstream re-derives, so its inward rounding is load-bearing: it is what makes
    the certified box a subset of the requested one. A candidate POINT is different. Every
    consumer of this function re-derives the point from scratch -- `refutation.refute`
    re-checks domain membership and re-evaluates the whole formula, and
    `checkers.ExactWitnessChecker` does the same for witnesses. A candidate that drifts out
    of the domain, or that no longer violates what it was meant to violate, is rejected on
    its own merits. Rounding direction can therefore cost a lead but cannot buy an unsound
    acceptance, which makes it an ergonomics choice rather than a soundness one.

    A consequence worth expecting: an angle very close to a joint limit may transport to a
    `t` outside a box that `joint_limits_to_t_bounds` rounded inward. That is the two
    approximations disagreeing at the boundary, and the honest outcome is a rejection.

    **`denominator` trades witness size against angle accuracy, and the default is biased
    toward accuracy.** At the default the returned rational typically has a twelve-digit
    denominator, which round-trips to the sampled angle within float precision but is
    hostile to audit -- and certificate size is a stated evaluation metric (`README` SS24),
    with `AGENTS.md` SS7.3 warning against gratuitous coefficient growth. A caller reporting
    a witness to a human should pass something far coarser and check the result still does
    what it was wanted for; `solve_reachable_targets` in this module applies exactly that
    policy, preferring the coarsest candidate that still meets its tolerance. The default
    matches `joint_limits_to_t_bounds` so that a point and a domain built from the same
    angle agree rather than straddling an endpoint.

    Requires `-pi < q < pi`: the half-angle chart does not reach `+-pi` (P2 Theorem 12.1).
    """
    if not -math.pi < q < math.pi:
        raise ValueError(
            "angle must lie strictly inside (-pi, pi); the half-angle chart cannot "
            "represent +-pi (see certify2r for four-chart coverage)"
        )
    return Fraction(math.tan(q / 2.0)).limit_denominator(denominator)


def t_to_angle(t: Fraction) -> float:
    """The radian angle a `t` value actually denotes: `q = 2*atan(t)`. Reporting only."""
    return 2 * math.atan(float(t))


def t_bounds_to_joint_limits(t_lower: Fraction, t_upper: Fraction) -> tuple[float, float]:
    """The radian interval a `t`-box actually certifies. Reporting only."""
    return (2 * math.atan(float(t_lower)), 2 * math.atan(float(t_upper)))


def witness_payload(t1: Fraction, t2: Fraction) -> dict[str, dict[str, dict[str, int]]]:
    return {
        "witness": {
            "t1": {"numerator": t1.numerator, "denominator": t1.denominator},
            "t2": {"numerator": t2.numerator, "denominator": t2.denominator},
        }
    }


__all__ = [
    "Planar2RInstance",
    "WitnessCandidate",
    "angle_to_t_candidate",
    "instance_from_witness",
    "joint_limits_to_t_bounds",
    "solve_reachable_targets",
    "t_bounds_to_joint_limits",
    "t_to_angle",
    "witness_payload",
]
