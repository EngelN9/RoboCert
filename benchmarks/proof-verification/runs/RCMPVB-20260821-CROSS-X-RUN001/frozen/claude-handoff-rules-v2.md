# RC-002 Claude handoff rules v2

Each packet under a run's `handoff/` directory is standalone and must be run in
a new Claude conversation with no inherited project context.

- Use exactly the packet contents; do not add either proof, another audit,
  source attribution, a known-weakness hint, or the private blinding map.
- Disable tools and repository access unless the packet explicitly changes that
  condition. This run's ledger and blind-audit packets require no tools.
- Return only the complete observable response. Do not provide or request hidden
  chain-of-thought.
- Alongside the response, record the exact public model name/version, displayed
  reasoning-effort setting, tool-access setting, date/time, and whether the
  conversation was fresh.
- Do not paraphrase, repair, or normalize the response before returning it.

The orchestrator must preserve the raw response byte-for-byte before any
reconciliation. A packet's existence does not authorize advancing to later
stages until the preceding stage is frozen and validated.
