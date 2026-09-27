# RoboCert — Claude Code entry point

@../AGENTS.md

`AGENTS.md`, imported above, is RoboCert's policy for every agent and provider; nothing
here overrides it. Its reading guide points to the sections for each kind of task.

Earlier citations of "`.claude/CLAUDE.md` #1–#5" refer to the research-ledger rules that
now live in `AGENTS.md` §76.1–§76.5.

## Claude-specific wiring

- Skills: `.claude/skills/` (`cite`, `isolate-steps`, `log-attempt`, `referee`).
- Subagents: `.claude/agents/` (`adversary`, `lit-extractor`, `referee-hostile`,
  `referee-naive`).
- Hooks: `.claude/settings.json`; what they enforce is in `AGENTS.md` §76.6.
