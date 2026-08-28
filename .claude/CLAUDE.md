# RoboCert — Claude Code entry point

Read [`AGENTS.md`](../AGENTS.md) in full before any task. It is RoboCert's canonical
engineering and soundness policy (75 sections: TCB rules, quantifier discipline,
result semantics, coding standards, citation policy, claim-wording rules,
overclaiming rules, testing requirements). Nothing below overrides it.

Read [`research/README.md`](../research/README.md) before touching anything under
`research/` — it defines the evidence tiers and the ledger discipline referenced
below.

## Non-negotiables specific to the research ledger

These don't already live in `AGENTS.md`; everything else does.

1. Every new research/design claim enters `research/CLAIMS.md` at `E0`. You may not
   self-assign a higher tier, no matter how confident the argument looks.
2. A context that produced a research/soundness argument may never referee it.
   Promoting a claim from `E1` to `E2` always goes through the `referee` skill,
   which dispatches `referee-hostile` and `referee-naive` as fresh subagents with no
   memory of how the argument was constructed.
3. A failed attempt is logged in `research/ATTEMPTS.md` with a diagnosed failure
   point via the `log-attempt` skill. "This didn't work" is not a diagnosis.
4. Never state a literature claim without a `research/literature/LIT-xxx.md` entry
   created via the `cite` skill in the same session — a recalled citation with no
   entry is not a citation.
5. The `adversary` subagent and whatever produced the proof/algorithm it's attacking
   must never share context. If the searcher knows what the answer is supposed to
   be, its search stops being honest.

`research/CLAIMS.md` edits are checked automatically by `scripts/check_ledger.py`
(monotonicity, DAG acyclicity, orphan references, referee gate, history gate).
`research/reports/` writes are checked by `scripts/check_report_language.py`
(blocks overclaiming language without a qualifying `E2`+ citation). Both run as
hooks (`.claude/settings.json`) — they cannot be argued around, by design.

## Everything else

`src/robocert` is the runtime package; changes there follow `AGENTS.md` §19–24
(repository architecture, module dependency rules, coding standards, testing
requirements) directly. `ROADMAP.md` is the phased plan; `research/` tracks
progress against it, it does not replace it.
