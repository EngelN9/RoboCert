"""Positivstellensatz certificate verification, and the tampering it must catch.

Every negative case below is a certificate that a numerical solver could plausibly emit -- a
Gram matrix off in one entry, a basis one monomial short, a bound raised past what the
decomposition supports. Accepting any of them would promote unverified solver output, which is
the single failure this architecture exists to prevent.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from robocert.polynomial import add, constant, monomial, summation
from robocert.sos import (
    PositivstellensatzCertificate,
    SosBlock,
    expand_sos_block,
    gram_from_rows,
    verify,
)

# p = x^2 - 2x + 2, and p - 1 = (x - 1)^2. The Gram matrix below is PSD but SINGULAR
# (eigenvalues 0 and 2), which is the ordinary case, not an edge case.
_P = summation([monomial(1, x=2), monomial(-2, x=1), constant(2)])
_BASIS_1_X = (constant(1), monomial(1, x=1))
_SQUARE_GRAM = gram_from_rows([[1, -1], [-1, 1]])


def _square_certificate() -> PositivstellensatzCertificate:
    return PositivstellensatzCertificate(
        target=_P,
        gamma=Fraction(1),
        sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM),),
    )


# ---------------------------------------------------------------------------------------
# Accepts
# ---------------------------------------------------------------------------------------


def test_unconstrained_square_is_accepted() -> None:
    result = verify(_square_certificate())

    assert result.accepted, result.diagnostics


def test_expansion_reproduces_the_square() -> None:
    """The Gram expansion itself, checked independently of the identity test around it."""
    expanded = expand_sos_block(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM))

    assert expanded == summation([monomial(1, x=2), monomial(-2, x=1), constant(1)])


def test_inequality_multiplier_is_accepted() -> None:
    """x >= 0 given g = x - 1 >= 0, via x - 0 = 1 + 1*(x - 1)."""
    one = (constant(1),)
    certificate = PositivstellensatzCertificate(
        target=monomial(1, x=1),
        gamma=Fraction(0),
        inequalities=(add(monomial(1, x=1), constant(-1)),),
        sos_blocks=(
            SosBlock(basis=one, gram=gram_from_rows([[1]])),
            SosBlock(basis=one, gram=gram_from_rows([[1]]), multiplier_index=0),
        ),
    )

    result = verify(certificate)

    assert result.accepted, result.diagnostics


def test_equality_multiplier_is_accepted() -> None:
    """x^2 + y >= 0 given h = y = 0, via (x^2 + y) - 0 = x^2 + 1*y."""
    certificate = PositivstellensatzCertificate(
        target=add(monomial(1, x=2), monomial(1, y=1)),
        gamma=Fraction(0),
        equalities=(monomial(1, y=1),),
        sos_blocks=(SosBlock(basis=(monomial(1, x=1),), gram=gram_from_rows([[1]])),),
        equality_multipliers=(constant(1),),
    )

    result = verify(certificate)

    assert result.accepted, result.diagnostics


def test_rational_gamma_is_exact() -> None:
    """gamma = 3/4, with p - 3/4 = (x - 1)^2 + 1/4.

    Not a tight bound: p attains 1 at x = 1, so gamma must be at most 1, and the slack shows up
    as the second, constant SOS block. An earlier draft of this test used gamma = 7/4 and the
    checker rejected it -- correctly, since p >= 7/4 is false. Keeping the corrected version
    documents that the bound is a real obligation, not a label.
    """
    certificate = PositivstellensatzCertificate(
        target=_P,
        gamma=Fraction(3, 4),
        sos_blocks=(
            SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM),
            SosBlock(basis=(constant(1),), gram=gram_from_rows([[Fraction(1, 4)]])),
        ),
    )

    result = verify(certificate)

    assert result.accepted, result.diagnostics


# ---------------------------------------------------------------------------------------
# Refuses
# ---------------------------------------------------------------------------------------


def test_perturbed_gram_entry_is_rejected() -> None:
    """One entry off by a millionth. The identity no longer closes, and no tolerance exists."""
    perturbed = gram_from_rows([[1, -1], [-1, Fraction(1_000_001, 1_000_000)]])
    certificate = PositivstellensatzCertificate(
        target=_P, gamma=Fraction(1), sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=perturbed),)
    )

    result = verify(certificate)

    assert not result.accepted
    assert "does not reproduce" in result.diagnostics[0]


def test_non_psd_gram_is_rejected_before_the_identity() -> None:
    """[[0,1],[1,0]] expands to 2x, so `2x = p - gamma` is false anyway -- but the report must
    name the PSD failure, because an indefinite block invalidates the argument even when the
    algebra happens to balance."""
    certificate = PositivstellensatzCertificate(
        target=monomial(2, x=1),
        gamma=Fraction(0),
        sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=gram_from_rows([[0, 1], [1, 0]])),),
    )

    result = verify(certificate)

    assert not result.accepted
    assert "row and column to vanish" in result.diagnostics[0]


def test_gamma_raised_above_the_true_bound_is_rejected() -> None:
    """p - 1 is a square; p - 2 is not, and claiming it must fail."""
    certificate = PositivstellensatzCertificate(
        target=_P, gamma=Fraction(2), sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM),)
    )

    result = verify(certificate)

    assert not result.accepted


def test_truncated_basis_is_rejected() -> None:
    certificate = PositivstellensatzCertificate(
        target=_P,
        gamma=Fraction(1),
        sos_blocks=(SosBlock(basis=(constant(1),), gram=_SQUARE_GRAM),),
    )

    result = verify(certificate)

    assert not result.accepted
    assert "gram has 2 rows for a basis of 1" in result.diagnostics[0]


def test_empty_certificate_is_rejected() -> None:
    """Without this an empty certificate reduces the identity to a statement about equality
    multipliers alone, which says nothing about nonnegativity."""
    result = verify(PositivstellensatzCertificate(target=_P, gamma=Fraction(1)))

    assert not result.accepted
    assert "no SOS block" in result.diagnostics[0]


def test_empty_basis_block_is_rejected() -> None:
    certificate = PositivstellensatzCertificate(
        target=_P, gamma=Fraction(1), sos_blocks=(SosBlock(basis=(), gram=()),)
    )

    result = verify(certificate)

    assert not result.accepted
    assert "empty basis" in " ".join(result.diagnostics)


def test_multiplier_index_out_of_range_is_rejected() -> None:
    certificate = PositivstellensatzCertificate(
        target=_P,
        gamma=Fraction(1),
        sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM, multiplier_index=3),),
    )

    result = verify(certificate)

    assert not result.accepted
    assert "out of range" in " ".join(result.diagnostics)


def test_mismatched_equality_multipliers_are_rejected() -> None:
    certificate = PositivstellensatzCertificate(
        target=_P,
        gamma=Fraction(1),
        equalities=(monomial(1, y=1),),
        sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM),),
        equality_multipliers=(),
    )

    result = verify(certificate)

    assert not result.accepted
    assert "must correspond" in " ".join(result.diagnostics)


def test_motzkin_attempt_is_rejected() -> None:
    """The Motzkin polynomial x^4y^2 + x^2y^4 - 3x^2y^2 + 1 is nonnegative but NOT a sum of
    squares. This checker cannot prove that -- it only checks the certificate it is handed -- so
    what is asserted here is the honest thing: a plausible attempted decomposition is rejected
    on the identity, not waved through.
    """
    motzkin = summation(
        [
            monomial(1, x=4, y=2),
            monomial(1, x=2, y=4),
            monomial(-3, x=2, y=2),
            constant(1),
        ]
    )
    basis = (constant(1), monomial(1, x=1, y=1), monomial(1, x=2, y=1), monomial(1, x=1, y=2))
    certificate = PositivstellensatzCertificate(
        target=motzkin,
        gamma=Fraction(0),
        sos_blocks=(SosBlock(basis=basis, gram=gram_from_rows([[1, 0, 0, 0], *[[0] * 4] * 3])),),
    )

    result = verify(certificate)

    assert not result.accepted


@pytest.mark.parametrize("numerator", [999_999, 1_000_001])
def test_single_coefficient_tampering_is_rejected(numerator: int) -> None:
    """Scale the target by one part in a million, either direction."""
    tampered = summation(
        [monomial(Fraction(numerator, 1_000_000), x=2), monomial(-2, x=1), constant(2)]
    )
    certificate = PositivstellensatzCertificate(
        target=tampered,
        gamma=Fraction(1),
        sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM),),
    )

    result = verify(certificate)

    assert not result.accepted


def test_no_certificate_means_rejection_not_an_exception() -> None:
    """Failure to certify must be a clean verdict the caller maps to UNKNOWN -- never a crash,
    and never a claim of infeasibility."""
    certificate = PositivstellensatzCertificate(
        target=monomial(1, x=1),  # x is negative somewhere; no SOS certificate exists
        gamma=Fraction(0),
        sos_blocks=(SosBlock(basis=_BASIS_1_X, gram=_SQUARE_GRAM),),
    )

    result = verify(certificate)

    assert not result.accepted
    assert result.diagnostics
