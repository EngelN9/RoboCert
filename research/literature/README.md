# Literature — verified locators only

Entries here are created only via the `cite` skill (`.claude/skills/cite/SKILL.md`),
which refuses to record a reference without a same-session fetch, a theorem/lemma
number, and a verbatim hypothesis transcription. This operationalizes `AGENTS.md`
§67 (Research Citation Policy) as an enforced schema rather than a written-only rule.

A source here may be cited as an `E4` dependency in `research/CLAIMS.md`. A recalled
"I believe paper X shows Y" with no entry here is not a citation and may not appear
in a `depends:` list.

## Entry format

```markdown
## LIT-<number>
source: <arXiv id / DOI / publisher>, fetched <date>
authors: <verbatim>
result: <which theorem/algorithm/section is being cited>
statement: <transcribed, in the paper's own notation, as close to verbatim as practical>
hypotheses: <enumerated verbatim from the paper>
translation: <into RoboCert's semialgebraic/quantifier notation, with the translation justified>
gap: <every hypothesis RoboCert's setting does not satisfy, and whether it is essential>
verified-by: human, <date>
```

The `gap` field is where reductions live or die — the common failure mode is a
translation step that quietly assumes something (finiteness, convexity, a specific
parameterization) that RoboCert's setting doesn't actually have.
