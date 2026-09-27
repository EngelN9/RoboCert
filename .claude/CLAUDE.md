# RoboCert — Claude Code entry point

Read [`AGENTS.md`](../AGENTS.md) in full before any task. It is RoboCert's canonical
engineering and soundness policy for every agent and provider (§0–§76: TCB rules,
quantifier discipline, result semantics, coding standards, citation and claim-wording
rules, testing requirements, research-ledger discipline). Start with its reading guide:
the core rules at a glance and the topic index. Nothing below overrides it.

Read [`research/README.md`](../research/README.md) before touching anything under
`research/`. It defines the evidence tiers and the ledger discipline.

## Research ledger

The ledger rules live in `AGENTS.md` §76, so Claude and Codex follow the same text.
They used to be numbered here, and earlier citations of "`.claude/CLAUDE.md` #n" mean
§76.n:

1. New research/design claims enter `research/CLAIMS.md` at `E0` (§76.1).
2. No self-refereeing; `E1` to `E2` only via the `referee` skill (§76.2).
3. Failed attempts go in `research/ATTEMPTS.md` with a diagnosis, via `log-attempt` (§76.3).
4. No literature claim without a `cite`-created `LIT-xxx` entry (§76.4).
5. The `adversary` never shares context with what it attacks (§76.5).

## Claude-specific wiring

- Skills: `.claude/skills/` (`cite`, `isolate-steps`, `log-attempt`, `referee`).
- Subagents: `.claude/agents/` (`adversary`, `lit-extractor`, `referee-hostile`,
  `referee-naive`).
- Hooks: `.claude/settings.json` runs `scripts/check_report_language.py` before edits,
  `scripts/check_ledger.py` after edits, and `scripts/session_ledger_reminder.py` at stop
  (§76.6). They cannot be argued around, by design.

## Everything else

`src/robocert` is the runtime package; changes there follow `AGENTS.md` §19–24
(repository architecture, module dependency rules, coding standards, testing
requirements) directly. `ROADMAP.md` is the ordered research plan (the original phased
plan is archived in `docs/archive/`); `research/` tracks progress against it, it does not
replace it.
