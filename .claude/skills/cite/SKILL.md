---
name: cite
description: Create a verified-locator entry in research/literature/ before citing a paper/source in research/CLAIMS.md. Use whenever a research claim's soundness argument or reduction relies on a published result, and no LIT-xxx entry for it exists yet.
---

# cite

Operationalizes `AGENTS.md` §67 (Research Citation Policy) as an enforced schema.
**Refuses to record a reference without a same-session fetch.** A recalled "I
believe paper X shows Y" is not a citation and must not appear in a
`research/CLAIMS.md` `depends:` list or be treated as `E4` evidence.

## Procedure

1. **Fetch the source this session.** Use `WebFetch` (or an authenticated MCP
   connector — arXiv/Semantic Scholar/Zotero if connected) on the actual paper, not
   a summary of it, not a search-result snippet. If you cannot fetch it, stop and
   say so explicitly — do not proceed from memory.
2. **Transcribe verbatim.** Copy the exact theorem/algorithm statement and its
   hypotheses in the paper's own notation. Do not paraphrase at this step —
   paraphrasing is where hallucinated hypotheses creep in.
3. **Translate.** Restate the result in RoboCert's semialgebraic/quantifier
   notation (`README.md` §2–4), and justify the translation step by step.
4. **Identify every gap.** Enumerate every hypothesis RoboCert's setting does not
   satisfy verbatim, and state whether each is essential or can be relaxed for the
   present use. This field is where most bad reductions actually break — do not
   leave it as "none" without having actually checked.
5. **Write the entry.** Next free `LIT-<number>` in `research/literature/`, using
   the format in `research/literature/README.md`. Set `verified-by: human, <date>`
   only once a human has actually read the transcription against the fetched
   source — not automatically.

## Using a LIT-xxx entry

Once written, `LIT-xxx` may be referenced from a `research/CLAIMS.md` entry's
`proof:` narrative to justify `tier: E4`, or as supporting evidence inside an `E1`
argument being prepared for referee review. It does not itself create an `RC-xxx`
entry — a citation is evidence for a claim, not a claim.

## Do not

- Do not cite a paper merely because it contains similar terminology (explicit rule
  in `AGENTS.md` §67).
- Do not accept a Level III source (forum post, unsourced blog, AI-generated
  summary) as a `LIT-xxx` entry on its own — it may motivate a search for the
  actual primary source, but the entry must point at that primary source.
