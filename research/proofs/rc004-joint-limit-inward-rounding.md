# RC-004: inward rationalization of principal-chart joint limits

Status: E0 draft, 2026-09-24. This is an argument for the current
`joint_limits_to_t_bounds` implementation (including commit `f350551`), not an
owner read, a referee verdict, or a certificate checker.

## Statement and hypotheses

Inputs are exact `Fraction` radian endpoints `a < b` with
`-31/10 <= a < b <= 31/10`, and a positive integer grid denominator `N`.
The function either raises `ValueError` or returns rational `L < U`. In the
latter case, for every **real** finite `t` in the closed interval `[L,U]`,
the represented principal angle `q = 2 atan(t)` lies in the requested closed
interval `[a,b]`. For a 2R box, apply this one-coordinate statement to each
joint and take the Cartesian product. No universal/existential quantifier is
reordered by this domain restriction.

The interval is deliberately narrower than `(-pi,pi)`: `31/10 < pi` (for
example, the perimeter of the regular inscribed 12-gon gives
`pi > 3(sqrt(6)-sqrt(2)) > 31/10`). Thus neither excluded chart endpoint
`+pi` nor `-pi` is in a supported input. The last strict inequality can be
checked without decimals: it is equivalent, after squaring positive sides,
to `sqrt(3) < 6239/3600`, whose square exceeds 3. Angles outside this range,
including intervals that cross a chart cut or represent another period, are
rejected; no periodic wrap or four-chart coverage is claimed.

## Exact endpoint enclosure

For `x = |q|/2 <= 31/20`, `_sin_cos_bounds` forms rational Taylor polynomials
through sine degree `2m+1` and cosine degree `2m`, with `m=24`. Taylor's
Lagrange theorem bounds the respective errors by
`x^(2m+2)/(2m+2)!` and `x^(2m+1)/(2m+1)!`: each next derivative is a sine or
cosine of absolute value at most one. Every power, factorial, sum, and bound
is evaluated as a rational, with no floating-point rounding. For negative
angles, oddness of sine reverses and negates its enclosure; cosine is even.
Consequently the returned four rational values enclose the *real* sine and
cosine of `q/2`, inclusive of the endpoints.

`_tan_half_bounds` refuses to proceed unless the computed cosine lower bound
is strictly positive. On a returned result, the true cosine is therefore
positive and the quotient `sin(q/2)/cos(q/2)` lies between the minimum and
maximum of the four rational corner quotients. This rectangle-to-quotient
bound follows because division is continuous on the positive denominator
interval and its extrema occur at corners (monotonic in the numerator and,
for each fixed numerator sign, monotonic in the denominator). The check is
load-bearing: no unsigned division through zero is permitted.

Let the enclosure for `tan(a/2)` have upper end `A_hi`, and that for
`tan(b/2)` have lower end `B_lo`. The implementation computes
`L = ceil(N*A_hi)/N` and `U = floor(N*B_lo)/N` with integer floor division
on exact `Fraction` values. Therefore

    tan(a/2) <= A_hi <= L < U <= B_lo <= tan(b/2).

If the inward grid is empty or a singleton, it raises instead of widening
either bound. The inequalities are non-strict at the original endpoints:
closed joint limits and closed rational boxes are preserved. The output
can omit valid boundary or near-boundary configurations; that is incompleteness,
not acceptance of an out-of-limit configuration.

## Transport back to angles

On `(-pi,pi)`, `q -> tan(q/2)` is continuous and strictly increasing: its
derivative is `(1/2) sec^2(q/2) > 0`. Its inverse on all finite real `t` is
`2 atan(t)`. Applying this inverse to the displayed inequalities and any
`L <= t <= U` yields `a <= 2 atan(t) <= b`. No claim extends to another
period of the physical revolute angle: periodic representatives must be
specified separately, not silently identified with this chart.

## Correspondence and limits

`joint_limits_to_t_bounds` checks endpoint order and the exact supported
range before constructing the enclosure, validates `N`, chooses the upper
enclosure at the lower endpoint and the lower enclosure at the upper endpoint,
then applies exact ceiling/floor and rejects `L >= U`. `t_bounds_to_joint_limits`
returns floating-point values for *reporting only*; it is not used to construct
the exact domain. `angle_to_t_candidate` is likewise a heuristic point
converter; its output must be rechecked as a different rational point.

This is a one-way conservatism argument for valid exact-rational inputs and
the current code. It is not a proof of physical joint calibration, model
correspondence, chart completeness, or any `CERTIFIED_*` result. The regression
tests catch the former libm endpoint defect but do not replace this argument.
