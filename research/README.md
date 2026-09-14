# Research-process ledger

This directory governs *how new certificate families, algorithms, and reductions get
designed, reviewed, and promoted* in RoboCert. It is distinct from `src/robocert`,
which is the runtime package, and from `schemas/claim.schema.json` /
`src/robocert/specification.py`, which define a single formal-claim *instance* about
one robot/task/uncertainty combination.

Background and rationale: `docs/methodology/`. Canonical engineering/soundness policy
(unchanged by this directory): `AGENTS.md`. Phased plan this ledger tracks progress
against: `ROADMAP.md`.

## Evidence tiers

Every entry in `research/CLAIMS.md` carries exactly one tier. No entry is untiered.

| Tier | Name | Meaning in RoboCert |
|---|---|---|
| `E0` | Suggestion | Unreviewed idea — chat, `research/notes/`. Zero weight. Never cited outside `notes/`. |
| `E1` | Read | A human has read and believes a written soundness argument for an algorithm, reduction, or checker design. Not yet adversarially reviewed. Still routinely wrong. |
| `E2` | Refereed | Survived the adversarial protocol: hostile + naive fresh-context review (Codex: `.codex/agents/referee-hostile.toml`, `.codex/agents/referee-naive.toml`; Claude: `.claude/agents/referee-hostile.md`, `.claude/agents/referee-naive.md`), step isolation, and negation control. Required before a production `Checker` implementing this claim may be written. |
| `E3` | Checked | Either (a) a concrete claim has a `CheckedCertificate` — a registered `Checker` accepted it via `verify_certificate()` — or (b) for a general algorithm/checker-design claim, the checker implementing it has passed the full positive/negative/adversarial/corrupted-certificate test suite required by `docs/architecture/trusted-computing-base.md`'s "Future certificate-family obligation". RoboCert's own checker gate is the `E3` mechanism. A Lean 4 development in `formal/` mechanizes soundness arguments about checker *models*; that is recorded separately and is **not** a tier — see "Mechanization" below. |
| `E4` | Cited | Taken from the literature with a verified locator in `research/literature/`. Inherits the literature's reliability — high, but not `E3`. |
| `EX` | Refuted | Known false. Never deleted — the reason it's false is the most valuable content in the entry. Lives in `research/OBSTRUCTIONS.md` or the ledger itself with `tier: EX`. |

## Mechanization

`formal/` holds three proof-assistant developments — Lean 4, Rocq, and Isabelle/HOL — each
proving soundness properties about a *model* of some part of RoboCert. Lean covers
`verify → Claim.Semantics` for the exact-witness family. Rocq covers exact polynomial
identities (currently, the RC-005 nondegeneracy facts that rule out a `Seg`-construct
unsoundness three isolated adversary runs independently found). Isabelle covers the
bounded-existential quantifier transport (currently, the RC-002 corrigendum's C2 step,
proved generically). None of the three attempts real quantifier elimination or an SOS/SDP
backend — that remains unimplemented, per `ROADMAP.md` Phase 3 and Phase 1.3/1.4.

Mechanization is deliberately **not** an evidence tier, for the same reason `E2` and `E3` are
not ordered: it is a different kind of evidence. A kernel-checked proof about a model of a
checker is not a `CheckedCertificate`, and it does not become one by being harder to obtain,
or by being confirmed by more than one kernel. Concretely, a proof from any of the three:

- does **not** raise any `RC-xxx` tier on its own;
- does **not** authorize registering a production checker;
- does **not** discharge the "Future certificate-family obligation" in
  `docs/architecture/trusted-computing-base.md`;
- proves things about a `formal/` model, **not** about `src/robocert/`. For Lean that
  correspondence is differentially tested — `scripts/check_lean_conformance.py`, run in CI —
  which is evidence on a finite vector set, not a proof of equivalence. For Rocq and Isabelle
  it has not been attempted. It is proved by none of them.

One channel is a narrow, deliberate exception: `src/robocert/attestation.py` lets a
registered checker *require* attestations from proof-assistant kernels, but only as a veto —
`AttestedChecker.check` computes `inner.accepted and not violations`, so an attestation can
never turn a rejection into an acceptance, only the reverse. Missing, corrupted, mismatched,
or failed proof checking rejects; it is never treated as `CERTIFIED_*`. See
`docs/architecture/trusted-computing-base.md`, "The attestation gate", for the full account.
Validating an attestation is not the same as running a kernel — it checks that a hash-bound
record *claims* a kernel accepted a statement. Re-running the kernel is
`scripts/check_attestations.py`'s job, in CI, where the toolchains are installed. Absent that
re-run, an attestation is provenance, not proof.

All three systems are proof-time only. None is a runtime dependency, none appears in
`dependencies`, and none is needed to reproduce a result under `AGENTS.md` §34.

A ledger entry records proof-assistant support in an optional `mechanized:` field, one
bullet per declaration, and **must** then carry a `fidelity:` field (enforced by
`scripts/check_ledger.py`). The two answer different questions. `mechanized:` says a kernel
accepted *some* proposition; `fidelity:` says whether that proposition is the one the entry
means, and records every known divergence -- a different quantifier domain, a different
object (a checker model rather than an encoding), a weaker hypothesis. "Not independently
checked" is an acceptable `fidelity:`; silence is not, because a kernel proves propositions,
not intentions. The fields were introduced on 2026-09-11 for RC-002 and RC-005, well after
those entries first acquired mechanized support; recording them is what surfaced that
several formal statements are the rational instances of steps the proofs state over the
reals.

`E2` is not a weak form of `E3`. It is a different kind of evidence — several
independent reviewers rather than one deterministic checker — and the two are not
additive.

## The monotonicity rule

> **A claim's tier is capped by the minimum tier of its dependencies.**

An algorithm whose soundness argument is `E2` but that cites an `E1` sub-lemma is an
`E1` result. This is enforced mechanically by `scripts/check_ledger.py` via the
`PostToolUse` hook on `research/CLAIMS.md` (see `.claude/settings.json`) — not by
convention, because the failure mode is silent and easy to miss under review pressure.

## Layout

```
research/
├── README.md          this file
├── CLAIMS.md           RC-xxx ledger — research/design claims, dependency DAG, tiers
├── ATTEMPTS.md         failed proof/algorithm attempts, diagnosed failure point
├── OBSTRUCTIONS.md     barrier theorems: "technique class T cannot work because..."
├── literature/         LIT-xxx.md, one file per verified source locator
├── special-cases/      specialization lattice, keyed to ROADMAP's benchmark ladder
├── notes/              exploratory scratch — explicitly E0, never cited
└── reports/            one report per ROADMAP §13 milestone
```

## Workstream → artifact mapping

| Manual workstream | RoboCert artifact |
|---|---|
| W1 — Refutation / counterexample search | Codex `.codex/agents/adversary.toml` and Claude `.claude/agents/adversary.md`; results are logged in `CLAIMS.md` / `OBSTRUCTIONS.md`. Complements `AGENTS.md` §31 and ROADMAP's planned `CounterexampleAgent`. |
| W2 — Reduction to known results | `literature/`, created only via the `cite` skill; operationalizes `AGENTS.md` §67. |
| W3 — Meaningful special cases | `special-cases/`, keyed to `ROADMAP.md`'s Benchmark Ladder (2R ⊃ 3R ⊃ spatial-3DOF ⊃ 6-DOF ⊃ 6/7-DOF robust ⊃ CAD workstation ⊃ continuous path). |
| W4 — Proof/algorithm attempts | `CLAIMS.md` (`RC-xxx`) for live claims, `ATTEMPTS.md` for abandoned routes. |
| W5 — Precise obstructions | `OBSTRUCTIONS.md`. |
| W6 — Report | `reports/`, one per `ROADMAP.md` §13 milestone. |

## Rules

1. A context that produced a research/soundness argument may never referee it.
   `E1` → `E2` promotion always goes through a fresh subagent
   (Codex `.codex/agents/referee-hostile.toml` / `referee-naive.toml` and Claude
   `.claude/agents/referee-hostile.md` / `referee-naive.md`, via the `referee`
   skill). Cross-provider runs must additionally follow the frozen protocol and
   handoff boundaries under `benchmarks/proof-verification/`.
2. The `adversary` agent and the agent constructing a proof/soundness argument must
   never share context. If the searcher knows what the answer is supposed to be, its
   search stops being honest.
3. Tiers change only by appending a `history:` line in the same edit that changes
   `tier:` in `CLAIMS.md`. Reaching `E2` or above additionally requires a non-`none`
   `referee:` field. Both are enforced by `scripts/check_ledger.py`.
4. Nothing in `research/` outranks `AGENTS.md`. If this directory's guidance and
   `AGENTS.md` conflict, `AGENTS.md` wins.
5. **A credible fatal objection freezes acceptance at once.** When an objection to a claim
   at `E1` or above is localized to a specific step, hypothesis, or definition -- not merely
   asserted -- the same edit that records it demotes the claim: to `EX` if it comes with a
   counterexample to the statement; otherwise to at most `E1`, and to `E0` if the objection
   invalidates the written argument the `E1` read relied on. "Probably still fine because several reviewers
   passed it" is not a status. Demotion cascades on its own: the monotonicity check then
   rejects every dependent that outranks the demoted claim, so they come down in the same
   edit (`tests/test_check_ledger.py` pins that cascade). Before blaming a kernel or a
   referee, rule out the ordinary causes: a statement or definition mismatch, an imported
   assumption, a different environment. The objection, its diagnosis, and the repair are
   recorded, never silently replaced (`ATTEMPTS.md`, `history:`).
6. **No tier currently requires an adversarial human review.** `E1` is a human read, which
   is not adversarial; `E2` means the claim survived adversarial *AI* review, whose
   reviewers share training data and failure modes however carefully their contexts are
   separated (`docs/methodology/cross-verification-protocol-v2.md`, Part 6). That is a known
   gap, stated rather than papered over. It is closed at one point only: registering a
   production checker additionally requires an adversarial human review
   (`docs/architecture/trusted-computing-base.md`, "Future certificate-family obligation").
