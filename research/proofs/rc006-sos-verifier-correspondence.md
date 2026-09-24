# RC-006: correspondence of the exact SOS verification utility

Status: E0 draft, 2026-09-24. Read against `src/robocert/sos.py`,
`linalg_exact.py`, `polynomial.py`, and the validated polynomial constructors
at this revision. No owner read or independent referee review has occurred.

## Accepted implies the stated algebraic conditions

Assume a well-typed `PositivstellensatzCertificate`: polynomials are valid
canonical `specification.Polynomial` values, Gram entries and `gamma` are
`Fraction`, and sequences are stable during this call. These are input
preconditions, not consequences of the frozen dataclass annotations. The
statement is one-way: `verify(c).accepted` implies the obligations below;
rejection is not a proof that no decomposition exists.

`verify` first calls `_check_shape`. Acceptance requires at least one SOS
block, a nonempty basis in every block, exactly as many equality multipliers
as equalities, exactly square Gram dimensions matching each basis, and each
non-`None` inequality index in range. Any shape problem returns a rejected
result before indexing or algebra. Zero or multiple free SOS blocks are
allowed: their sum is the free `sigma_0`. An inequality may have zero or
multiple blocks: their sum is its `sigma_i`; a missing index denotes zero.
Thus absent blocks do not secretly impose a positivity obligation or cause
an inequality to disappear from the stated domain. No free block is *required*
if at least one valid indexed block exists; the free sum may be zero.

For each well-shaped block, `is_positive_semidefinite` checks exact symmetry
and copies every entry into `Fraction`. It repeatedly chooses the largest
remaining diagonal pivot. A negative pivot rejects. With a positive pivot
`d`, the nested update computes the exact symmetric Schur complement
`S_ij = A_ij - A_ip A_pj/d` on the active indices. The congruence identity
`[d, v^T; v, B] ~ diag(d, B-vv^T/d)` says PSD of the current matrix is
equivalent to PSD of this complement. With maximal pivot zero, every active
diagonal is nonpositive; negative ones have already been excluded by the
maximal-pivot check, hence all are zero. A PSD matrix with zero diagonal must
have zero corresponding off-diagonals (its 2-by-2 principal minors would
otherwise be negative). The code checks the *whole* remaining block is zero
and rejects if not. If it returns true, the remaining zero block is PSD.
Induction through the exact Schur steps proves every accepted Gram is PSD
over Q (and hence over R). Singular PSD matrices are permitted; a zero pivot
with a nonzero row is not.

`expand_sos_block` forms the exact polynomial
`sigma = sum_ij G_ij b_i b_j`; zero entries are skipped only because they
contribute the zero polynomial. Every polynomial operation distributes and
multiplies `Fraction` coefficients, adds exponents, and passes the result to
the canonical `Polynomial` constructor, which combines like monomials and
drops zero coefficients. For real `x`, PSD of `G` implies
`sigma(x) = b(x)^T G b(x) >= 0` even when basis polynomials are dependent.

After PSD checks, `verify` appends each free `sigma`, or its product with the
indexed `g_i`, to `reconstructed`. It also appends every paired
`lambda_j h_j`; the length check makes the `zip(..., strict=True)` pairing
exhaustive. The left side is `target - constant(gamma)`. It subtracts the
sum of all reconstructed terms and accepts only when `is_zero(residual)`.
For canonical polynomials, `terms == ()` means every coefficient vanished,
so this is an exact identity in Q[x], not sampled agreement or a tolerance.
Grouping same-index and free blocks gives precisely

    target - gamma = sigma_0 + sum_i sigma_i*g_i + sum_j lambda_j*h_j.

At every real point of `K = {x | g_i(x)>=0 and h_j(x)=0}`, each SOS is
nonnegative, each inequality product is nonnegative, and every equality
product vanishes. Hence `target(x) >= gamma`. This is the elementary
*sufficiency* direction only; no completeness or fixed-degree claim follows.

## Rejection and trust boundary

Malformed dimensions, empty blocks, out-of-range indices, missing equality
multipliers, nonsymmetric or indefinite matrices, and nonzero residuals reject
in distinct branches. A caller bypassing the typed/stable input preconditions
can trigger a Python exception; this utility is not a total parser for
arbitrary objects. Neither a failing return nor such an exception establishes
infeasibility; a production caller must fail closed to `UNKNOWN`.

`sos.py` is not a `checking.Checker`, is bound to no serialized certificate
family or robot-property encoding, and cannot emit `CERTIFIED_*`. In particular
this argument does not justify RC-001's proposed planar-2R reduction, model
hash binding, geometric correspondence, or production checker registration.
Tests exercise representative positive and corruption cases; they do not
replace the unperformed owner read and adversarial review. RC-006 remains E0.
