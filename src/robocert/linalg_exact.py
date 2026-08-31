"""Exact positive-semidefiniteness over the rationals.

A sum-of-squares certificate is only meaningful if its Gram matrix is genuinely PSD. Deciding
that in floating point is not a decision: a matrix with a tiny negative eigenvalue is
indefinite, and no tolerance distinguishes it from a rounding artefact. This module decides it
exactly, over `Fraction`, or refuses to decide.

The method is symmetric Gaussian elimination with complete diagonal pivoting -- the exact
analogue of Cholesky. A symmetric matrix is PSD iff the elimination completes with every pivot
nonnegative and every zero pivot sitting in an entirely zero row.

**The failure mode this is written around.** A naive LDL^T loop divides by the pivot and, on
meeting a zero diagonal entry, either divides by zero or skips the row. Skipping accepts

    [[0, 1],
     [1, 0]]

which is symmetric, has a zero diagonal, and has eigenvalues +1 and -1 -- indefinite. Accepting
it would let a checker certify a "sum of squares" that is not one. The zero-pivot branch below
therefore requires the whole remaining row to vanish, and rejects otherwise. That case has its
own test.
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction

__all__ = ["is_positive_semidefinite", "is_symmetric"]

Matrix = Sequence[Sequence[Fraction]]


def is_symmetric(matrix: Matrix) -> tuple[bool, str]:
    """Square and equal to its transpose. Exact comparison; no tolerance."""
    size = len(matrix)
    for index, row in enumerate(matrix):
        if len(row) != size:
            return False, f"matrix is not square: row {index} has {len(row)} of {size} entries"
    for i in range(size):
        for j in range(i + 1, size):
            if matrix[i][j] != matrix[j][i]:
                return False, f"matrix is not symmetric: [{i}][{j}] != [{j}][{i}]"
    return True, "symmetric"


def is_positive_semidefinite(matrix: Matrix) -> tuple[bool, str]:
    """Decide PSD exactly, returning the verdict and a diagnostic.

    The empty matrix is PSD vacuously -- it is the Gram matrix of an empty basis, representing
    the zero polynomial. Callers that must not accept an empty certificate reject it themselves;
    that is a certificate-shape question, not a linear-algebra one.
    """
    symmetric, detail = is_symmetric(matrix)
    if not symmetric:
        return False, detail

    size = len(matrix)
    # Mutable working copy; the input is never modified.
    work = [[Fraction(entry) for entry in row] for row in matrix]
    active = list(range(size))

    while active:
        # Complete diagonal pivoting: take the largest remaining diagonal entry. With exact
        # arithmetic this is not about numerical stability -- it is what makes the zero-pivot
        # branch below reachable only when EVERY remaining diagonal entry is zero.
        pivot = max(active, key=lambda index: work[index][index])
        value = work[pivot][pivot]

        if value < 0:
            return False, f"not PSD: diagonal entry [{pivot}][{pivot}] = {value} is negative"

        if value == 0:
            # Every remaining diagonal entry is zero (pivoting chose the largest). For a PSD
            # matrix that forces the whole remaining block to vanish: if x_i x_j were nonzero
            # anywhere off-diagonal, the 2x2 minor [[0, a], [a, 0]] would have eigenvalues +-a.
            for index in active:
                for other in active:
                    if work[index][other] != 0:
                        return (
                            False,
                            f"not PSD: every remaining diagonal entry is zero but "
                            f"[{index}][{other}] = {work[index][other]} is not. A zero diagonal "
                            "entry in a PSD matrix forces its entire row and column to vanish.",
                        )
            return True, "positive semidefinite"

        active.remove(pivot)
        for i in active:
            factor = work[i][pivot] / value
            if factor == 0:
                continue
            for j in active:
                work[i][j] -= factor * work[pivot][j]

    return True, "positive semidefinite"
