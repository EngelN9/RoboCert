"""Proof-assistant-neutral attestations, and the tightening-only checker gate.

An *attestation* records that some proof-assistant kernel accepted a formal statement,
bound to the exact claim hash, model hash, and checker identity of a RoboCert certificate.
Attestations travel inside ``Certificate.payload``, because the certificate's own field set
is closed (``certificates.py`` compares field sets for equality, and the JSON Schema sets
``additionalProperties: false``).

Two properties are deliberate and load-bearing.

**Neutral.** No proof assistant is named in this module. A ``system`` is an opaque string,
and the set of accepted systems together with each one's permitted axioms is *policy data*
supplied by the caller. Adding a fourth assistant is a configuration change, not an edit here.

**Tightening only.** ``AttestedChecker`` computes ``inner.accepted and not violations``. An
attestation can only clear a conjunct that was already true, so it can never turn a rejection
into an acceptance -- it can only veto. A missing, failed, corrupted, or mismatched
attestation produces a rejection, which ``results.unknown_from_check`` maps to ``UNKNOWN``.
There is no path from this module to ``CERTIFIED_*``.

**What an attestation is not.** Validating one here does not run a kernel. It checks that a
well-formed, hash-bound record claims a kernel accepted a statement. Re-running the kernel is
CI's job (``scripts/check_attestations.py``). Absent that re-run, an attestation is
provenance, not proof -- see ``docs/architecture/trusted-computing-base.md``.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeGuard

from robocert.certificates import Certificate
from robocert.checking import Checker, CheckerDecision
from robocert.errors import ValidationError
from robocert.specification import Claim

#: Version tag for the payload block. A reader that does not recognise it must reject.
ATTESTATION_FORMAT = "robocert.attestation/1"

#: The payload key attestations live under.
ATTESTATION_KEY = "attestations"

_BLOCK_FIELDS = frozenset({"format", "entries"})

_ENTRY_FIELDS = frozenset(
    {
        "system",
        "toolchain",
        "claim_hash",
        "model_hash",
        "checker_id",
        "checker_version",
        "statement_digest",
        "artifact_digest",
        "axioms",
        "kernel_accepted",
    }
)

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _is_array(value: object) -> TypeGuard[Sequence[object]]:
    """Return True for a JSON array. ``str`` is a Sequence and must not be mistaken for one."""
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


@dataclass(frozen=True, slots=True)
class AttestationPolicy:
    """Which proof systems must attest, and which axioms each may depend on.

    ``required_systems`` names the systems whose attestation is mandatory; a system with no
    entry is treated as unavailable proof checking and vetoes.

    ``allowed_axioms`` maps every *recognised* system to the axioms its kernel may
    legitimately report. An entry naming an unrecognised system is rejected rather than
    ignored, so an unknown axiom base cannot enter unexamined. This is also the mechanism
    that catches an admitted proof: a placeholder axiom is simply absent from the allow-list.
    """

    required_systems: tuple[str, ...]
    allowed_axioms: Mapping[str, frozenset[str]]

    def __post_init__(self) -> None:
        object.__setattr__(self, "required_systems", tuple(self.required_systems))
        if not self.required_systems:
            raise ValidationError("attestation policy must require at least one proof system")
        if len(self.required_systems) != len(set(self.required_systems)):
            raise ValidationError("attestation policy required systems must be unique")
        frozen: dict[str, frozenset[str]] = {}
        for system, axioms in self.allowed_axioms.items():
            if not isinstance(system, str) or not system:
                raise ValidationError("attestation policy system names must be non-empty strings")
            frozen[system] = frozenset(axioms)
        missing = [item for item in self.required_systems if item not in frozen]
        if missing:
            raise ValidationError(
                f"attestation policy requires systems with no declared axiom allow-list: {missing}"
            )
        object.__setattr__(self, "allowed_axioms", MappingProxyType(frozen))

    def recognised_systems(self) -> tuple[str, ...]:
        """Return every system this policy knows how to judge."""
        return tuple(sorted(self.allowed_axioms))

    def violations(self, certificate: Certificate) -> tuple[str, ...]:
        """Return every reason this certificate's attestations are unacceptable.

        An empty tuple means the attestation block is well formed, hash-bound to this exact
        certificate, kernel-accepted, axiom-clean, and complete. It never means "proved".
        """
        diagnostics: list[str] = []
        block = certificate.payload.get(ATTESTATION_KEY)
        if block is None:
            return (f"certificate payload carries no {ATTESTATION_KEY!r} block",)
        if not isinstance(block, Mapping):
            return (f"{ATTESTATION_KEY!r} must be a JSON object",)
        if set(block) != _BLOCK_FIELDS:
            return (
                f"{ATTESTATION_KEY!r} fields do not match the versioned contract; "
                f"expected {sorted(_BLOCK_FIELDS)}, got {sorted(block)}",
            )
        if block["format"] != ATTESTATION_FORMAT:
            return (f"unsupported attestation format {block['format']!r}",)
        entries = block["entries"]
        if not _is_array(entries):
            return ("attestation entries must be a JSON array",)

        attested: set[str] = set()
        for index, raw in enumerate(entries):
            system = self._check_entry(certificate, index, raw, diagnostics)
            if system is None:
                continue
            if system in attested:
                diagnostics.append(f"entry {index}: duplicate attestation for system {system!r}")
                continue
            attested.add(system)

        for system in self.required_systems:
            if system not in attested:
                diagnostics.append(
                    f"no usable attestation for required proof system {system!r} "
                    "(unavailable or rejected proof checking)"
                )
        return tuple(diagnostics)

    def _check_entry(
        self,
        certificate: Certificate,
        index: int,
        raw: object,
        diagnostics: list[str],
    ) -> str | None:
        """Validate one entry, returning its system name only if the entry is fully usable."""
        before = len(diagnostics)

        def fail(message: str) -> None:
            diagnostics.append(f"entry {index}: {message}")

        if not isinstance(raw, Mapping):
            fail("attestation entry must be a JSON object")
            return None
        if set(raw) != _ENTRY_FIELDS:
            fail(
                "attestation entry fields do not match the versioned contract; "
                f"expected {sorted(_ENTRY_FIELDS)}, got {sorted(raw)}"
            )
            return None

        system = raw["system"]
        if not isinstance(system, str) or not system:
            fail("system must be a non-empty string")
            return None
        if system not in self.allowed_axioms:
            fail(
                f"unrecognised proof system {system!r}; "
                f"recognised systems are {list(self.recognised_systems())}"
            )
            return None

        toolchain = raw["toolchain"]
        if not isinstance(toolchain, str) or not toolchain:
            fail("toolchain must be a non-empty string identifying the exact pinned version")

        # Bind to the certificate. These mirror the cross-checks that
        # `checking._run_checker` already performs on the certificate itself, so an
        # attestation cannot be replayed against a different claim, model, or checker
        # version.
        for field, expected in (
            ("claim_hash", str(certificate.claim_hash)),
            ("model_hash", str(certificate.model_hash)),
            ("checker_id", certificate.checker_id),
            ("checker_version", certificate.checker_version),
        ):
            actual = raw[field]
            if actual != expected:
                fail(f"{field} {actual!r} does not match the certificate value {expected!r}")

        for field in ("statement_digest", "artifact_digest"):
            value = raw[field]
            if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
                fail(f"{field} must be a 'sha256:' digest of 64 lowercase hex characters")

        axioms = raw["axioms"]
        if not _is_array(axioms):
            fail("axioms must be a JSON array of strings")
        else:
            names = [name for name in axioms if isinstance(name, str)]
            if len(names) != len(axioms):
                fail("axioms must be a JSON array of strings")
            else:
                unexpected = sorted(set(names) - self.allowed_axioms[system])
                if unexpected:
                    fail(
                        f"depends on axiom(s) outside the allow-list for {system!r}: "
                        f"{unexpected}. An admitted or incomplete proof is not an attestation."
                    )

        accepted = raw["kernel_accepted"]
        if type(accepted) is not bool:
            fail("kernel_accepted must be a JSON boolean")
        elif not accepted:
            fail("kernel_accepted is false; the proof did not check")

        return system if len(diagnostics) == before else None


class AttestedChecker:
    """Wrap a checker so that it additionally requires proof-assistant attestations.

    The decision is ``inner.accepted and not violations``. This is the whole tightening
    guarantee, and it is structural rather than conventional: there is no branch in which a
    passing attestation makes the result more accepting than the inner checker's own verdict.

    Identity is inherited from the inner checker except for ``checker_id``, which is suffixed
    so that a certificate produced for the bare checker cannot be replayed against the
    attested one -- ``checking._run_checker`` compares ``checker_id`` exactly.
    """

    def __init__(self, inner: Checker, policy: AttestationPolicy, *, id_suffix: str) -> None:
        if not id_suffix:
            raise ValidationError("attested checker requires a non-empty checker id suffix")
        self._inner = inner
        self._policy = policy
        self.checker_id = f"{inner.checker_id}{id_suffix}"
        self.checker_version = inner.checker_version
        self.certificate_family = inner.certificate_family
        self.arithmetic_mode = inner.arithmetic_mode

    @property
    def policy(self) -> AttestationPolicy:
        """Return the attestation policy this checker enforces."""
        return self._policy

    def check(self, claim: Claim, certificate: Certificate) -> CheckerDecision:
        inner = self._inner.check(claim, certificate)
        violations = self._policy.violations(certificate)
        return CheckerDecision(
            inner.accepted and not violations,
            inner.diagnostics + violations,
        )


def attestation_entry(
    *,
    system: str,
    toolchain: str,
    claim_hash: str,
    model_hash: str,
    checker_id: str,
    checker_version: str,
    statement_digest: str,
    artifact_digest: str,
    axioms: Iterable[str],
    kernel_accepted: bool,
) -> dict[str, object]:
    """Build one payload entry. A convenience for producers; the checker trusts nothing."""
    return {
        "system": system,
        "toolchain": toolchain,
        "claim_hash": claim_hash,
        "model_hash": model_hash,
        "checker_id": checker_id,
        "checker_version": checker_version,
        "statement_digest": statement_digest,
        "artifact_digest": artifact_digest,
        "axioms": list(axioms),
        "kernel_accepted": kernel_accepted,
    }


def attestation_block(entries: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Build the payload block. See :func:`attestation_entry`."""
    return {"format": ATTESTATION_FORMAT, "entries": [dict(entry) for entry in entries]}


__all__ = [
    "ATTESTATION_FORMAT",
    "ATTESTATION_KEY",
    "AttestationPolicy",
    "AttestedChecker",
    "attestation_block",
    "attestation_entry",
]
