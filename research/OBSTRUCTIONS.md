# Obstructions

An obstruction is not "this is hard." It is a theorem of the form: *any approach to
claim `C` using only technique class `T` would require statement `S`, and `S` is
false, open, or known to be intractable under the stated conditions.*

An obstruction candidate is promoted here once three or more independent routes in
`research/ATTEMPTS.md` fail at the same requirement, or once a barrier is proven
directly. Where possible, attack `S` itself with the `adversary` agent
(`.claude/agents/adversary.md`) before accepting the obstruction as real — a barrier
that survives adversarial search is a genuine result, not a hunch.

## Entry format

```markdown
## O-<number>
technique_class: <the family of methods this obstructs, e.g. "degree-2 SOS relaxations">
target: <the RC-xxx or claim family this blocks>
barrier_statement: <S, the precise intermediate statement that would be required>
status_of_S: false (counterexample) | intractable under conditions X | open
evidence: <pointer to counterexample, complexity argument, or the ATTEMPTS.md entries that seeded this>
consequence: <what remains viable — e.g. "rules out degree <=4 SOS; degree 6 untested">
tier: E2 | E3 | E4          # obstructions are tiered like any other research claim
date: <YYYY-MM-DD>
```

Obstructions are never deleted, even if a later technique class sidesteps them — the
barrier and why it holds is the valuable content.

---

*(No obstructions recorded yet.)*
