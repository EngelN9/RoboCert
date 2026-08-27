# Sketch: SOS soundness for 2R singularity-margin certification (E0)

Status: **E0 — unreviewed sketch.** Referenced by `research/CLAIMS.md` RC-001. This
is a starting point for a human to read and, if believed, promote to `E1`; it has not
been adversarially reviewed and must not be cited as evidence anywhere outside
`research/notes/`.

## Target claim (RC-001)

For the planar 2R robot (`ROADMAP.md` §1.1) with tangent-half-angle variables
`t_i = tan(q_i/2)`, interval link lengths `L_i in [L_i^-, L_i^+]`, and Jacobian
`J(q, theta)`, certify

```
sigma_min(J(q, theta)) >= epsilon    for all (q, theta) in R x Theta
```

using a Positivstellensatz representation

```
det(J J^T) - gamma = sigma_0 + sum_i sigma_i * g_i(q, theta) + sum_j lambda_j * h_j(q, theta)
```

over the domain `K = {(q, theta) : g_i >= 0, h_j = 0}` defined by the region `R`,
joint limits, and the rationalized kinematic identities, where `sigma_min(J)^2` is
sufficient for the margin claim when `det(J J^T)` is used as the algebraic surrogate
(`README.md` §10 states the surrogate-sufficiency condition that must be checked
explicitly for this specific claim — not yet done here).

## Open gaps (why this is E0, not E1)

1. The surrogate condition "`det(J J^T) >= gamma > 0` is sufficient for the intended
   singularity claim" is asserted in `README.md` §10 in general but has not been
   verified for this specific 2R parameterization and margin definition.
2. The tangent-half-angle substitution introduces denominator conditions
   (`1 + t_i^2 != 0`, always true over the reals, but chart-boundary behavior at
   `q_i = pi` needs explicit handling per `AGENTS.md` §7.2/§46).
3. No degree bound or SOS relaxation order has been chosen; feasibility of finding
   `sigma_0, sigma_i` at a tractable degree is unverified.
4. Interval uncertainty `theta` has not been folded into the domain `K` explicitly —
   this note only sketches the nominal (`theta` fixed) case.

## Next step

Read this sketch, resolve gap 1–2 with an explicit derivation, and promote to `E1` in
`research/CLAIMS.md` (append a `history:` line). Only then dispatch the `referee`
skill for `E1` → `E2` promotion.
