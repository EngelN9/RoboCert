# `formal/` — nested agent policy

Scope: this file governs `formal/` (Lean, Rocq, and Isabelle/HOL) and
`src/robocert/attestation.py`, the one module that reads results from this directory back
into the runtime. Per root `AGENTS.md` §3, a nested `AGENTS.md` MAY impose stricter
obligations and MUST NOT weaken root soundness rules. Everything here is stricter. Root
`AGENTS.md` wins on any conflict.

## Hard rules

1. **No incomplete proof in an audited target, in any system.** Lean: no `sorry`, `admit`, or
   `native_decide` in the `RoboCert` library — permitted only under `Statements/`, which is
   quarantined and never imported by `RoboCert`; enforced by the axiom audit in
   `RoboCert/Audit.lean` (`scripts/check_lean_axioms.py`). Rocq: no `admit` or `Admitted` in
   `formal/rocq/RoboCert/`; enforced by `scripts/check_attestations.py`, which greps compiler
   output for it. Isabelle: no `sorry` in `formal/isabelle/RoboCert/`; enforced the same way.
   This is the multi-system analogue of the empty production checker registry — a fail-closed
   gate, not a lint, and not optional for any of the three.

2. **No new axioms, in any system, without a documented reason.** Lean: audited theorems may
   depend only on `propext`, `Classical.choice`, and `Quot.sound`. Rocq and Isabelle do not
   yet have a committed axiom allow-list as strict as Lean's — until one exists, treat any
   axiom beyond each system's own standard library foundations as a stop-and-ask. Anything new
   is a reviewed change that must be justified in `docs/architecture/trusted-computing-base.md`.

3. **No dependency may be added, to any of the three toolchains, without updating the TCB
   document.** A dependency must appear in the "Trusted to PROVE" table, satisfying
   `docs/architecture/trusted-computing-base.md` obligation 3 ("identifies all additional
   trusted libraries and versions"). For Lean this lands in `lake-manifest.json`; Rocq and
   Isabelle do not yet have an equivalent committed lockfile — their CI jobs pin a version by
   URL/opam package instead, and that pin is itself the thing to update.

4. **No declaration name, in any system, may contain `safe`, `verified_safe`, or
   `certified`.** See `AGENTS.md` §66 on overclaiming. This applies to Lean theorem names,
   Rocq lemma names, and Isabelle lemma names identically.

5. **No proof from any of the three systems promotes anything on its own.** None can register
   a production checker, none can emit `CERTIFIED_*` directly, and none raises a
   `research/CLAIMS.md` tier by itself. Tier changes go through the mechanisms in
   `research/README.md`, unchanged.

6. **The attestation gate may only tighten, never loosen.** Any change to
   `src/robocert/attestation.py` or to an `AttestationPolicy` instance must preserve
   `inner.accepted and not violations` as the acceptance formula — an attestation vetoes, it
   never grants. A change that makes an attestation able to accept what the inner checker
   rejected is a soundness regression, not a feature, regardless of how it is described.

7. **An attestation record is not a kernel run.** `formal/attestations/*.json` records what a
   kernel is *claimed* to have accepted. Setting `kernel_accepted: true` for a system that was
   not actually run is fabrication — see `AGENTS.md` §22.5 (fail closed) and §66
   (no overclaiming) — regardless of how confident the proof looks. If the toolchain was not
   run, the entry belongs under `pending_systems`, not `entries`.

8. **Divergences from `src/robocert/` are recorded, not silently absorbed.** If a formal model
   in any of the three systems and the Python implementation differ, the difference goes in
   `formal/README.md` under "Deliberate divergences" before the code is committed. An
   unrecorded divergence is a defect even when the formal side is the more correct of the two.

## When a model and the implementation disagree

Do not "fix" the formal model to match Python. Report the disagreement. The whole point of
this layer is that it can be right when the implementation is wrong — silently conforming the
model to the code destroys the only thing this directory is for.

## When two proof assistants disagree with each other

This has not happened yet — Lean, Rocq, and Isabelle currently prove disjoint statements
(checker-model soundness; polynomial identities; quantifier transport), not the same
statement three ways. If a future change makes two of them prove the same claim and they
disagree, that is a `research/OBSTRUCTIONS.md`-or-`research/ATTEMPTS.md`-worthy finding in its
own right, not a bug to silently resolve by picking the one that says what was expected —
see `research/README.md` rule 2 on searcher/proof independence, which applies here by
analogy: agreement between two kernels that share a design flaw is not evidence of anything.
