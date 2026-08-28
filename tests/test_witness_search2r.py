from __future__ import annotations

import math
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from robocert.witness_search2r import (
    joint_limits_to_t_bounds,
    solve_reachable_targets,
    t_bounds_to_joint_limits,
)

_L1 = Fraction(5)
_L2 = Fraction(3)  # reach annulus is [2, 8]


def _forward_kinematics(q1: float, q2: float, l1: float, l2: float) -> tuple[float, float]:
    return (
        l1 * math.cos(q1) + l2 * math.cos(q1 + q2),
        l1 * math.sin(q1) + l2 * math.sin(q1 + q2),
    )


def test_solver_returns_nothing_outside_the_reach_annulus() -> None:
    """Emptiness is evidence of unreachability, never a proof of it -- but the
    solver must at least not fabricate candidates for impossible targets."""
    assert solve_reachable_targets(_L1, _L2, (Fraction(50), Fraction(0))) == []
    assert solve_reachable_targets(_L1, _L2, (Fraction(0), Fraction(0))) == []  # inner hole


def test_solver_finds_both_elbow_branches() -> None:
    candidates = solve_reachable_targets(_L1, _L2, (Fraction(6), Fraction(2)))
    assert {c.elbow_branch for c in candidates} == {"up", "down"}


def test_achieved_point_is_exact_and_deviation_is_consistent() -> None:
    """The achieved point must be the exact rational image of the witness, and
    the reported deviation must be exactly the squared distance to the request --
    both checkable by hand, no floats involved."""
    requested = (Fraction(6), Fraction(2))
    best = solve_reachable_targets(_L1, _L2, requested)[0]

    d1 = 1 + best.t1 * best.t1
    d2 = 1 + best.t2 * best.t2
    cos_q1, sin_q1 = (1 - best.t1 * best.t1) / d1, 2 * best.t1 / d1
    cos_q2, sin_q2 = (1 - best.t2 * best.t2) / d2, 2 * best.t2 / d2
    expected = (
        _L1 * cos_q1 + _L2 * (cos_q1 * cos_q2 - sin_q1 * sin_q2),
        _L1 * sin_q1 + _L2 * (sin_q1 * cos_q2 + cos_q1 * sin_q2),
    )
    assert best.achieved == expected
    assert best.requested == requested
    assert best.deviation_squared == (
        (best.achieved[0] - requested[0]) ** 2 + (best.achieved[1] - requested[1]) ** 2
    )


@given(
    x=st.fractions(min_value=Fraction(-7), max_value=Fraction(7), max_denominator=16),
    y=st.fractions(min_value=Fraction(-7), max_value=Fraction(7), max_denominator=16),
)
@settings(max_examples=40, deadline=None)
def test_reachable_targets_are_approached_closely(x: Fraction, y: Fraction) -> None:
    """For any target inside the annulus the best candidate must land very near
    it. This is a quality property of the untrusted search, not a soundness one:
    a poor candidate is rejected by the checker, never wrongly accepted."""
    reach = math.hypot(float(x), float(y))
    if not (2.2 < reach < 7.8):  # stay clear of the annulus boundaries
        return
    candidates = solve_reachable_targets(_L1, _L2, (x, y))
    assert candidates, (x, y)
    assert math.sqrt(float(candidates[0].deviation_squared)) < 1e-6


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (Fraction(-5, 2), Fraction(5, 2)),
        (Fraction(-1, 2), Fraction(1, 2)),
        (Fraction(0), Fraction(3)),
        (Fraction(-31, 10), Fraction(31, 10)),  # very close to +-pi
    ],
)
def test_joint_limit_conversion_rounds_inward(lower: Fraction, upper: Fraction) -> None:
    """The soundness-relevant direction (RC-004): the certified q-interval must be
    a SUBSET of the requested one. Rounding outward would let the checker accept
    a configuration violating the user's stated joint limits."""
    t_lower, t_upper = joint_limits_to_t_bounds(lower, upper)
    q_lower, q_upper = t_bounds_to_joint_limits(t_lower, t_upper)
    assert q_lower >= float(lower)
    assert q_upper <= float(upper)
    assert q_lower < q_upper


def test_joint_limit_conversion_is_tight_enough_to_be_useful() -> None:
    """Inward rounding must not throw away meaningful range -- conservative is
    fine, useless is not."""
    t_lower, t_upper = joint_limits_to_t_bounds(Fraction(-5, 2), Fraction(5, 2))
    q_lower, q_upper = t_bounds_to_joint_limits(t_lower, t_upper)
    assert abs(q_lower - (-2.5)) < 1e-9
    assert abs(q_upper - 2.5) < 1e-9


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (Fraction(-4), Fraction(1)),  # below -pi
        (Fraction(1), Fraction(4)),  # above +pi
        (Fraction(1), Fraction(1)),  # empty
        (Fraction(2), Fraction(1)),  # inverted
    ],
)
def test_joint_limit_conversion_rejects_unrepresentable_intervals(
    lower: Fraction, upper: Fraction
) -> None:
    with pytest.raises(ValueError):
        joint_limits_to_t_bounds(lower, upper)
