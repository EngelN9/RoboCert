"""The exact PSD test, and above all the ways it must refuse.

A sum-of-squares certificate is worth exactly as much as this predicate. If it accepts an
indefinite matrix, the checker built on it will certify a "sum of squares" that is not one, and
every downstream guarantee is void. So the negative cases here carry more weight than the
positive ones.
"""

from __future__ import annotations

from fractions import Fraction

from hypothesis import given
from hypothesis import strategies as st

from robocert.linalg_exact import is_positive_semidefinite, is_symmetric


def _matrix(rows: list[list[int | Fraction]]) -> list[list[Fraction]]:
    return [[Fraction(entry) for entry in row] for row in rows]


# ---------------------------------------------------------------------------------------
# Accepts
# ---------------------------------------------------------------------------------------


def test_identity_is_psd() -> None:
    accepted, _ = is_positive_semidefinite(_matrix([[1, 0], [0, 1]]))
    assert accepted


def test_psd_but_singular_is_accepted() -> None:
    """[[1,-1],[-1,1]] has eigenvalues 0 and 2. This is the Gram matrix of (x-1)^2, so
    rejecting singular-but-PSD matrices would reject the most ordinary certificate there is."""
    accepted, _ = is_positive_semidefinite(_matrix([[1, -1], [-1, 1]]))
    assert accepted


def test_all_zeros_is_psd() -> None:
    accepted, _ = is_positive_semidefinite(_matrix([[0, 0], [0, 0]]))
    assert accepted


def test_empty_matrix_is_vacuously_psd() -> None:
    """An empty basis is a certificate-shape question, rejected in `sos._check_shape`, not here."""
    accepted, _ = is_positive_semidefinite([])
    assert accepted


def test_rational_entries_stay_exact() -> None:
    accepted, _ = is_positive_semidefinite(
        _matrix([[Fraction(1, 3), Fraction(1, 3)], [Fraction(1, 3), Fraction(1, 3)]])
    )
    assert accepted


# ---------------------------------------------------------------------------------------
# Refuses -- the tests that decide whether any of this is worth anything
# ---------------------------------------------------------------------------------------


def test_zero_diagonal_with_nonzero_off_diagonal_is_rejected() -> None:
    """THE case a naive LDL^T gets wrong.

    [[0,1],[1,0]] is symmetric with a zero diagonal and eigenvalues +1 and -1 -- indefinite. A
    loop that skips zero pivots instead of demanding a zero row accepts it, and a checker built
    on that would certify x*y as a sum of squares.
    """
    accepted, detail = is_positive_semidefinite(_matrix([[0, 1], [1, 0]]))

    assert not accepted
    assert "row and column to vanish" in detail


def test_negative_diagonal_is_rejected() -> None:
    accepted, detail = is_positive_semidefinite(_matrix([[1, 0], [0, -1]]))

    assert not accepted
    assert "negative" in detail


def test_indefinite_with_positive_diagonal_is_rejected() -> None:
    """Every diagonal entry positive is not sufficient: this has determinant 1 - 4 = -3."""
    accepted, _ = is_positive_semidefinite(_matrix([[1, 2], [2, 1]]))
    assert not accepted


def test_barely_indefinite_is_rejected() -> None:
    """Off by one part in a million. Exact arithmetic has no tolerance to hide inside."""
    epsilon = Fraction(1, 1_000_000)
    accepted, _ = is_positive_semidefinite(_matrix([[1, 1], [1, 1 - epsilon]]))

    assert not accepted


def test_barely_psd_is_accepted() -> None:
    """The same matrix perturbed the other way must still be accepted -- the predicate has to be
    sharp in both directions, not merely conservative."""
    epsilon = Fraction(1, 1_000_000)
    accepted, _ = is_positive_semidefinite(_matrix([[1, 1], [1, 1 + epsilon]]))

    assert accepted


def test_asymmetric_matrix_is_rejected() -> None:
    accepted, detail = is_positive_semidefinite(_matrix([[1, 2], [3, 1]]))

    assert not accepted
    assert "not symmetric" in detail


def test_ragged_matrix_is_rejected() -> None:
    accepted, detail = is_positive_semidefinite([[Fraction(1), Fraction(0)], [Fraction(0)]])

    assert not accepted
    assert "not square" in detail


def test_larger_indefinite_matrix_is_rejected() -> None:
    """The 2x2 obstruction hidden inside a 4x4 that is otherwise well behaved."""
    accepted, _ = is_positive_semidefinite(
        _matrix([[2, 0, 0, 0], [0, 1, 3, 0], [0, 3, 1, 0], [0, 0, 0, 5]])
    )
    assert not accepted


def test_is_symmetric_reports_the_offending_entry() -> None:
    symmetric, detail = is_symmetric(_matrix([[1, 2], [3, 1]]))

    assert not symmetric
    assert "[0][1]" in detail


# ---------------------------------------------------------------------------------------
# Property: anything of the form L^T L is PSD, by construction
# ---------------------------------------------------------------------------------------


_entries = st.integers(min_value=-4, max_value=4)


@given(st.lists(st.lists(_entries, min_size=3, max_size=3), min_size=3, max_size=3))
def test_gram_matrices_are_always_psd(rows: list[list[int]]) -> None:
    """L^T L is PSD for every real L, singular ones included. A predicate rejecting any of
    these would reject certificates a solver legitimately produces."""
    size = len(rows)
    gram = [
        [sum(Fraction(rows[k][i]) * Fraction(rows[k][j]) for k in range(size)) for j in range(size)]
        for i in range(size)
    ]

    accepted, detail = is_positive_semidefinite(gram)

    assert accepted, detail


@given(st.lists(st.lists(_entries, min_size=3, max_size=3), min_size=3, max_size=3))
def test_negated_gram_matrices_are_psd_only_when_zero(rows: list[list[int]]) -> None:
    """-L^T L is PSD only in the degenerate case where L^T L vanishes."""
    size = len(rows)
    gram = [
        [
            -sum(Fraction(rows[k][i]) * Fraction(rows[k][j]) for k in range(size))
            for j in range(size)
        ]
        for i in range(size)
    ]

    accepted, _ = is_positive_semidefinite(gram)

    assert accepted == all(entry == 0 for row in gram for entry in row)
