# Claude blind-audit attempts

Both fresh, tool-free Claude blind-audit sessions were started on 2026-08-24
after the Claude theorem-only ledger and union ledger had been frozen. Neither
session consumed a proof: the service rejected both requests before inference.

| proof | session id | result |
|---|---|---|
| P1 | `899db062-1d0d-4694-a075-e32f1a010572` | HTTP 429: `You've hit your session limit · resets 3pm (Asia/Taipei)` |
| P2 | `3ff0ddaa-ce7d-4c67-9fac-5dfdb70d2aa0` | HTTP 429: `You've hit your session limit · resets 3pm (Asia/Taipei)` |

These are `BLOCKED` external-provider attempts, not audit reports. They provide
no mathematical evidence and cannot be replaced by additional Codex reports.
The proof-source mapping remains withheld because both cross-provider blind
audits were not frozen.
