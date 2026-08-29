# Methodology sources

This directory holds the two source manuals that RoboCert's research-process layer
(`research/`, `.codex/`, `.claude/`) is adapted from:

- [`anthropic-research-methodology-source.md`](anthropic-research-methodology-source.md)
  — "Attacking a Conjecture with Anthropic Tools." Evidence tiers, the claim-ledger
  monotonicity rule, the adversarial referee protocol, and the six-workstream
  structure (refutation / reduction / special cases / proof attempts / obstructions /
  report) are taken from here.
- [`openai-research-methodology-source.md`](openai-research-methodology-source.md)
  — "Using OpenAI Tools as a Coordinated Mathematical Research Environment." The
  theorem-compatibility table, reduction-certificate format, and claim-evidence
  ledger codes (`D`/`T`/`C`/`N`/`E`/`H`/`?`) informed the same layer.

Both manuals were written for attacking an open mathematical conjecture from
scratch. RoboCert is not that: it already has a mature soundness policy
(`AGENTS.md`), a phased roadmap (`ROADMAP.md`), and a typed `Claim`/`Certificate`/
`Checker` code stack. The manuals are adapted, not applied literally — see
`research/README.md` for the concrete mapping and the tier definitions as redefined
for RoboCert.

## Cross-verification protocols

The candidate-proof cross-verification protocols are retained separately from the
two source manuals:

- [`cross-verification-protocol-v2.md`](cross-verification-protocol-v2.md) is
  the current recommended procedure. It structurally separates obligation-ledger
  construction, blind candidate-proof audits, and adjudication.
- [`cross-verification-protocol-v1.md`](cross-verification-protocol-v1.md) is
  retained as superseded methodology history.

Both files describe a review process only. They do not alter RoboCert result
statuses or replace its deterministic certificate-checking boundary.

## Concept → RoboCert artifact

| Manual concept | RoboCert artifact |
|---|---|
| `PROBLEM.md` | `README.md` (project-wide) + per-family formalization notes in `research/notes/` |
| `CLAIMS.md` ledger, evidence tiers | `research/CLAIMS.md` (`RC-xxx`), tiers redefined in `research/README.md` — distinct from the runtime `robocert.Claim` class |
| `ATTEMPTS.md` | `research/ATTEMPTS.md` |
| `OBSTRUCTIONS.md` | `research/OBSTRUCTIONS.md` |
| `literature/` verified locators | `research/literature/LIT-xxx.md`, operationalizing `AGENTS.md` §67 |
| `special-cases/` specialization lattice | `research/special-cases/`, keyed to `ROADMAP.md`'s benchmark ladder |
| Formal proof assistant (Lean/Coq) as the top evidence tier | Adopted in part — `formal/` holds Lean 4, Rocq, and Isabelle/HOL developments proving soundness of checker *models* and supporting algebraic/quantifier facts, but none is a tier: RoboCert's own `Checker`/`verify_certificate()` gate remains the tier-`E3` mechanism. A checker MAY additionally require proof-assistant attestations as a veto-only gate (`src/robocert/attestation.py`); an attestation can reject a certificate but never certify one. See `research/README.md` "Mechanization" and `formal/README.md`. |
| `certificates/` + `checkers/`, small trust base | Already exists: `src/robocert/certificates.py`, `src/robocert/checking.py`, `docs/architecture/trusted-computing-base.md` |
| Adversarial referee subagents | Codex: `.codex/agents/referee-hostile.toml`, `.codex/agents/referee-naive.toml`; Claude: `.claude/agents/referee-hostile.md`, `.claude/agents/referee-naive.md` |
| Counterexample search agent | Codex: `.codex/agents/adversary.toml`; Claude: `.claude/agents/adversary.md`; both complement `AGENTS.md` §31 and the planned `CounterexampleAgent` |
| `reports/` | `research/reports/`, one per `ROADMAP.md` §13 milestone |
| Agent skills, definitions, and hooks | Codex: `.agents/skills/`, `.codex/agents/`, `.codex/hooks.json`; Claude: `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`; see `research/README.md` and `.claude/CLAUDE.md` |

## Precedence

If a specific rule in these manuals conflicts with `AGENTS.md`, `AGENTS.md` wins —
it is RoboCert's canonical soundness policy. These manuals are the design rationale
for `research/`, not an independent authority.
