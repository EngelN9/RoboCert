# Fatal-flaw rules, adapted for RoboCert

Adapted from [`fatal-flaw-rules-source.md`](fatal-flaw-rules-source.md), *Professional Rules
for Handling Fatal Flaws in AI-Reviewed and Formally Verified Mathematical Proofs*, which is
retained verbatim alongside the two other source manuals. Its forty rules are condensed to
twelve here, and each one is mapped to the RoboCert mechanism that already enforces it. Where
nothing enforced a rule, the gap was closed on 2026-09-11; those are marked below.

This document adds no authority. `AGENTS.md` is the canonical soundness policy and
`research/README.md` defines the tiers; if this page and either of them disagree, they win.

## The chain being protected

The source's central point is that four objects are routinely conflated:

```text
intended theorem -> specification -> formal statement -> proof
```

A defect at any arrow can sink the result even when the final proof is kernel-accepted. In
RoboCert the chain has two formal branches, not one. A research claim (`RC-xxx`) is encoded
once as a runtime `Claim` built in Python and checked by exact evaluation, and possibly again
as Lean, Rocq, or Isabelle statements checked by a kernel. Each encoding is its own arrow,
and each one can be the one that is wrong. RoboCert's own record shows this is not
hypothetical. RC-003 is `EX`, and A-001 and A-003 both failed at the same point: an encoding
that did not mean what its author intended.

## Twelve rules

| # | Rule | Source | Enforced by | Status |
|---|---|---|---|---|
| R1 | **State the theorem before proving it.** Write it independently of any encoding, with the quantifier prefix, each quantifier's domain, and every assumption explicit. | 1, 2, 18 | RC `statement:`; `AGENTS.md` §1, §6, §59; protocol v2 L.1 and L.5 (intake and freeze) | Covered |
| R2 | **Encoding fidelity is an obligation of its own.** A kernel accepting T says nothing about whether T is the intended theorem, so every formal statement is compared with the claim it is recorded against, and every divergence is written down. | 3, 20; the source's fidelity factor | `mechanized:` requires `fidelity:` in `research/CLAIMS.md`, enforced by `scripts/check_ledger.py` | **Closed 2026-09-11** |
| R3 | **The object is Γ ⊢ T, not T.** Inventory Γ, including imported assumptions and typeclass structure, and test whether a hypothesis already implies the conclusion. | 4, 5 | `Claim.assumptions`; protocol v2 A.3 (hypothesis consumption) | Covered |
| R4 | **Audit definitions with positive, negative, degenerate, and boundary cases.** | 6, 7 | `AGENTS.md` §24, §46, §47 | Covered for code |
| R5 | **Try to falsify before accepting, and formalize the objection itself.** | 8, 28 | `adversary` agent (W1), isolated from provers; the Rocq nondegeneracy identities answering the adversaries' `Seg` finding | Covered |
| R6 | **Localize every flaw.** A failed proof is not a false theorem, and no repair starts until the theorem's own status is known. | 9, 10, 11 | `ATTEMPTS.md` `broke_at` and `status_of_required`; tier `EX`; protocol v2 L.2 | Covered |
| R7 | **AI agreement is correlated evidence.** Assign adversarial roles, blind the contexts, and require explicit uncertainty. Prose is never a certificate. | 12–16, 39, 40 | `referee-hostile` / `referee-naive`; protocol v2 X.3 and Part 6; `AGENTS.md` §4.5 | Covered; **gap stated 2026-09-11** (no tier requires adversarial human review; required before production registration) |
| R8 | **Trace every external claim to a locator.** | 17 | `cite` skill; `research/literature/LIT-xxx.md` | Covered |
| R9 | **Several provers are not several validations.** Say what each one proves. | 19, 25 | `trusted-computing-base.md` "Trusted to PROVE"; per-declaration `mechanized:` bullets | Covered |
| R10 | **Audit the trusted base and the axiom closure.** Tactic success is not kernel acceptance. Freeze reproducible artifacts. | 21–24, 26 | `scripts/check_lean_axioms.py`; attestation `allowed_axioms`; RUN001 SHA-256 manifest | Partial: Rocq has no committed lockfile (`AGENTS.md` §57); a Lean attestation's digests do not cover the files that define what its statement means (`trusted-computing-base.md`, "What the digests bind", recorded 2026-09-14) |
| R11 | **A credible fatal objection freezes acceptance immediately.** Demotion cascades to dependents; a counterexample retracts the claim; if T and ¬T both check, rule out the ordinary causes before suspecting a kernel. | 27, 29–32, 35 | `research/README.md` rule 5; the monotonicity check cascades demotion (`tests/test_check_ledger.py`) | **Closed 2026-09-11** |
| R12 | **Repair at the earliest defective layer, and keep the whole history.** | 33, 34, 36–38 | `ATTEMPTS.md` `layer:`; `EX` entries and attempts are never deleted | **Closed 2026-09-11** (`layer:` axis) |

Rule 37 of the source (publish corrections in the channels the original reached) has no
separate row. RoboCert publishes only through this repository, and R12's history rule already
covers it there.

## Where this departs from the source

**1. Weakest link, not a product.** The source scores confidence as
`statement validity × proof validity × formalization fidelity × trusted-base integrity ×
independence of review`. Multiplying implies calibrated probabilities that nobody has. The
enforceable version is ordinal: confidence is capped by the weakest link. RoboCert already
applies that rule along dependencies, where a claim's tier cannot exceed its weakest
dependency's (`research/README.md`, "The monotonicity rule"). R2 extends the same idea to
fidelity, the factor tiers do not otherwise measure.

**2. The four statuses are renamed.** The source's "Verified", "Validated", and "formally
verified" collide with `AGENTS.md` §36, which puts *verified* on its list of vague terms, and
with the `scripts/check_report_language.py` blocklist. Adapted:

| Source status | RoboCert term | What establishes it here |
|---|---|---|
| Verified | **kernel-accepted** | A `mechanized:` bullet. Not a tier (`research/README.md`, "Mechanization"). |
| Validated | **statement-checked** | A `fidelity:` field recording a completed comparison, not "not independently checked". |
| Independently Replicated | **independently replicated** | Protocol v2 X.2 "genuinely independent" correspondence, or a second encoding built separately. |
| Mathematically Accepted | **accepted** | No single mark. Requires `E2` or above, R2 closed, and, before registration, an adversarial human review. |

None of these is an evidence tier, and none raises one.

**3. Severity and layer are separate axes.** The source's taxonomy
(`expositional < local proof gap < missing hypothesis < definition defect < statement
mismatch < false theorem < trusted-base inconsistency`) mixes how bad a flaw is with where it
sits. Protocol v2 §A.6 already grades severity (Fatal / Substantive / Minor / Expository), so
the source's list becomes the separate `layer:` field in `research/ATTEMPTS.md`. That field
is what "repair at the earliest layer" needs: a missing hypothesis can be cosmetic or fatal,
but it is always repaired at the hypothesis.

**4. Duplicates merged.** {2, 3, 18, 20} → R1/R2; {6, 7} → R4; {8, 28} → R5; {9, 10, 11} → R6;
{12–16, 39, 40} → R7; {19, 25} → R9; {21–24, 26} → R10; {27, 29–32, 35} → R11;
{33, 34, 36–38} → R12.

## What closing R2 found immediately

Recording `mechanized:` and `fidelity:` for RC-002 and RC-005, which already had formal
support but no ledger trace of it, surfaced three divergences at once. The details are
in the entries.

- The Isabelle transport `bounded_existential_transport` binds its points as `rat`. The
  corrigendum step it formalizes (C2.1) is stated over `R^2`, and RC-005's proof applies its
  existential to the real box. The artifact is the rational instance of the intended step.
- The Rocq identities are likewise stated over `Q`, for facts RC-005's proof uses
  "for every finite real (t1,t2)".
- RC-005's own `statement:` never says whether `t` ranges over `R` or `Q`. R1 requires it
  to say.

None of the three is known to make anything false: the transport's proof is generic, and
restating it over `real` is expected to be routine. Each is exactly the kind of gap R2
exists to make visible, and the owner has to settle them. No recording step decides them.

## What this does not change

No tier moved. No checker was registered. `CERTIFIED_*` stays unreachable, and every rule
above constrains what is already here rather than widening what may be certified. By the
`accepted` row above, nothing in this repository is accepted yet.
