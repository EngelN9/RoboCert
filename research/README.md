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
| `E3` | Checked | Either (a) a concrete claim has a `CheckedCertificate` — a registered `Checker` accepted it via `verify_certificate()` — or (b) for a general algorithm/checker-design claim, the checker implementing it has passed the full positive/negative/adversarial/corrupted-certificate test suite required by `docs/architecture/trusted-computing-base.md`'s "Future certificate-family obligation". RoboCert's own checker gate is the `E3` mechanism; no external proof assistant is used. |
| `E4` | Cited | Taken from the literature with a verified locator in `research/literature/`. Inherits the literature's reliability — high, but not `E3`. |
| `EX` | Refuted | Known false. Never deleted — the reason it's false is the most valuable content in the entry. Lives in `research/OBSTRUCTIONS.md` or the ledger itself with `tier: EX`. |

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
