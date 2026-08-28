# Reports

One report per `ROADMAP.md` §13 milestone (e.g. `01-formal-claim-schema.md`,
`06-2r-robust-reachability-certificate.md`), written continuously as work
progresses, not assembled at the end. A report is the project's actual output even
when the underlying claim remains open — especially then.

`PreToolUse` on writes to this directory runs `scripts/check_report_language.py`
(`.claude/settings.json`), which blocks certification/completion language
(`AGENTS.md` §36's "Avoid" list, plus "QED", "we have proved", "100% safe") unless
the surrounding text cites a `research/CLAIMS.md` entry at tier `E2`+ or a real
`CheckedCertificate`.

## Required sections

1. **Statement and conventions** — pulled from the relevant `research/special-cases/`
   node and `README.md`'s formal model, including degenerate cases explicitly in or
   out of scope.
2. **Status summary** — every relevant `RC-xxx` claim, its tier, one line each. A
   reader should see the shape of what's established within ninety seconds.
3. **Dependency graph** — rendered from `research/CLAIMS.md`'s `depends:` edges,
   tiers visible on the nodes, so a tier violation is visible by inspection.
4. **Results** at referee-checkable granularity. No compression. Machine-checked
   results (`E3`) flagged with file path, commit hash, and toolchain version
   (`docs/architecture/trusted-computing-base.md` §Future certificate-family
   obligation lists what must be recorded).
5. **Negative results, equal weight** — `research/ATTEMPTS.md` entries and
   `research/OBSTRUCTIONS.md` barriers relevant to this milestone, with exact search
   coverage where applicable (region, seeds, encoding).
6. **Where to attack** — the author's own ranked list of the weakest points, with
   reasons. Volunteering this is not weakness.
7. **Verification methodology** — referee passes per claim, and any planted-error
   detection rate measured for this milestone (seeded manually: inject a known bug
   into a soundness argument before sending it to `referee-hostile`, record whether
   it's caught).
8. **Reproducibility manifest** — repo/commit, toolchain versions, solver versions,
   seeds, model identifiers and dates used for any AI-assisted step
   (`AGENTS.md` §34 Reproducibility Rules).
9. **Disclosure** — which parts were AI-assisted and in what role (candidate
   generation, refereeing, formalization support, search implementation,
   exposition), and which claims are machine-checked vs. rest on human reading.

No report should be created for a milestone with no real content yet — an empty or
aspirational report is worse than no report, since it invites exactly the confident-
prose-mistaken-for-progress failure mode this whole layer exists to prevent.
