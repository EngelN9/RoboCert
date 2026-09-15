"""Exact verification of a Positivstellensatz / sum-of-squares certificate.

The mathematics being checked is the SUFFICIENCY direction, which is elementary:

    if  p - gamma  =  sigma_0 + sum_i sigma_i * g_i + sum_j lambda_j * h_j
    and every sigma is a sum of squares,
    then  p >= gamma  on  K = { x : g_i(x) >= 0, h_j(x) = 0 }.

At any point of `K` every `g_i` is nonnegative, every `h_j` vanishes, and every `sigma` is
nonnegative, so the right-hand side is nonnegative and `p - gamma >= 0`. Nothing here relies on
a Positivstellensatz *completeness* theorem, on a degree bound, or on any claim that such a
decomposition exists -- failure to find one is not evidence of anything, and callers must map it
to `UNKNOWN`.

**This module verifies; it does not search.** An external solver (Julia + SumOfSquares.jl + JuMP,
say) proposes Gram matrices. Those are untrusted numerical output: the proposal is meaningful
only once the identity has been re-derived exactly here and each Gram matrix shown exactly PSD.
See `docs/architecture/backends.md`.

**Deliberately not a `Checker`.** `checking.Checker` requires a `certificate_family`, and there
is no family to bind to: RC-001, which claims the SOS scheme suits the planar-2R
singularity-margin reduction, is `E0`. `research/README.md` requires `E2` before a production
checker implementing a claim may be written. What this module verifies is an algebraic identity
plus a PSD condition -- a mathematical primitive, not that reduction. Wrapping it in a `Checker`
and binding it to a family is a separate, evidence-gated change.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction

from robocert.linalg_exact import is_positive_semidefinite
from robocert.polynomial import (
    constant,
    is_zero,
    multiply,
    subtract,
    summation,
)
from robocert.specification import Polynomial

__all__ = [
    "PositivstellensatzCertificate",
    "SosBlock",
    "VerificationResult",
    "expand_sos_block",
    "gram_from_rows",
    "verify",
]


@dataclass(frozen=True, slots=True)
class SosBlock:
    """One `sigma = basis^T * gram * basis`, attached to a constraint or standing alone.

    `basis` entries are arbitrary polynomials rather than bare monomials. That is strictly more
    general, costs nothing (expansion is a polynomial product either way), and avoids a second
    monomial representation alongside `specification.MonomialPower`.

    `multiplier_index` is `None` for the free `sigma_0`, or an index into the certificate's
    `inequalities`.
    """

    basis: tuple[Polynomial, ...]
    gram: tuple[tuple[Fraction, ...], ...]
    multiplier_index: int | None = None


@dataclass(frozen=True, slots=True)
class PositivstellensatzCertificate:
    """A candidate decomposition. Construction implies nothing; only `verify` does."""

    target: Polynomial
    gamma: Fraction
    inequalities: tuple[Polynomial, ...] = ()
    equalities: tuple[Polynomial, ...] = ()
    sos_blocks: tuple[SosBlock, ...] = ()
    equality_multipliers: tuple[Polynomial, ...] = ()


@dataclass(frozen=True, slots=True)
class VerificationResult:
    accepted: bool
    diagnostics: tuple[str, ...] = ()


def expand_sos_block(block: SosBlock) -> Polynomial:
    """Expand `basis^T * gram * basis` symbolically.

    The caller must have established that `gram` is PSD; this function is pure expansion and
    makes no such check, so it must never be used on its own to conclude nonnegativity.
    """
    parts: list[Polynomial] = []
    for i, row in enumerate(block.gram):
        for j, entry in enumerate(row):
            if entry == 0:
                continue
            scaled = multiply(constant(entry), multiply(block.basis[i], block.basis[j]))
            parts.append(scaled)
    return summation(parts)


def _check_shape(certificate: PositivstellensatzCertificate) -> list[str]:
    """Every way the certificate can be malformed. All of them reject."""
    problems: list[str] = []

    if not certificate.sos_blocks:
        # Without this, a certificate carrying no SOS block would reduce the identity to
        # `p - gamma = sum_j lambda_j h_j`, which says nothing about nonnegativity. An empty
        # certificate must never be vacuously accepted.
        problems.append("certificate carries no SOS block; an empty certificate proves nothing")

    if len(certificate.equality_multipliers) != len(certificate.equalities):
        problems.append(
            f"{len(certificate.equality_multipliers)} equality multiplier(s) for "
            f"{len(certificate.equalities)} equality constraint(s); they must correspond"
        )

    for index, block in enumerate(certificate.sos_blocks):
        size = len(block.basis)
        if len(block.gram) != size:
            problems.append(
                f"SOS block {index}: gram has {len(block.gram)} rows for a basis of {size}"
            )
            continue
        for row_index, row in enumerate(block.gram):
            if len(row) != size:
                problems.append(
                    f"SOS block {index}: gram row {row_index} has {len(row)} of {size} entries"
                )
        if size == 0:
            problems.append(f"SOS block {index}: empty basis contributes nothing")
        if block.multiplier_index is not None and not (
            0 <= block.multiplier_index < len(certificate.inequalities)
        ):
            problems.append(
                f"SOS block {index}: multiplier_index {block.multiplier_index} is out of range "
                f"for {len(certificate.inequalities)} inequality constraint(s)"
            )
    return problems


def verify(certificate: PositivstellensatzCertificate) -> VerificationResult:
    """Accept only if every Gram matrix is exactly PSD and the identity holds exactly.

    Order matters: shape, then PSD, then the identity. A malformed or non-PSD block makes the
    identity meaningless even when it happens to balance, so those are not reported as an
    identity failure.
    """
    problems = _check_shape(certificate)
    if problems:
        return VerificationResult(False, tuple(problems))

    for index, block in enumerate(certificate.sos_blocks):
        psd, detail = is_positive_semidefinite(block.gram)
        if not psd:
            problems.append(f"SOS block {index}: {detail}")
    if problems:
        return VerificationResult(False, tuple(problems))

    reconstructed: list[Polynomial] = []
    for block in certificate.sos_blocks:
        sigma = expand_sos_block(block)
        if block.multiplier_index is None:
            reconstructed.append(sigma)
        else:
            reconstructed.append(multiply(sigma, certificate.inequalities[block.multiplier_index]))
    for multiplier, equality in zip(
        certificate.equality_multipliers, certificate.equalities, strict=True
    ):
        reconstructed.append(multiply(multiplier, equality))

    left = subtract(certificate.target, constant(certificate.gamma))
    residual = subtract(left, summation(reconstructed))
    if not is_zero(residual):
        return VerificationResult(
            False,
            (
                "the decomposition does not reproduce `target - gamma` exactly; residual has "
                f"{len(residual.terms)} nonzero term(s)",
            ),
        )

    return VerificationResult(True, ())


def gram_from_rows(rows: Sequence[Sequence[Fraction | int]]) -> tuple[tuple[Fraction, ...], ...]:
    """Convenience for building a Gram matrix from literals. No validation; `verify` does that."""
    return tuple(tuple(Fraction(entry) for entry in row) for row in rows)
