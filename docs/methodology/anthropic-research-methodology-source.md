# Attacking a Conjecture with Anthropic Tools

### A manual for running Claude surfaces as a coordinated, adversarial, independently checkable research environment

---

## 0. What this manual assumes, and what it will not give you

This manual describes an operating discipline for using Claude (chat, Projects, Claude Code, Skills, subagents, hooks, MCP connectors, the Messages and Batches APIs) to work on an open mathematical conjecture along six parallel fronts:

1. proving it,
2. refuting it by construction,
3. reducing it to known results,
4. establishing meaningful special cases,
5. identifying a precise obstruction,
6. producing a report a hostile referee can check without trusting you or the tools.

It will not give you a system that proves theorems. Language models generate fluent mathematical prose whose surface features — structure, register, confidence — are uncorrelated with correctness in exactly the regime you care about, namely near the frontier of what is known. The single most expensive mistake in this line of work is treating a well-formed proof as evidence of a proof.

The environment below is therefore built around one principle:

> **Claude is a generator of candidates. Nothing Claude asserts enters the record until an independent, non-linguistic process has had a fair chance to kill it.**

Everything else — the directory layout, the ledger, the hooks, the referee protocol — is machinery for enforcing that sentence when you are tired and the proof looks beautiful.

---

## 1. The evidence model

### 1.1 Tiers

Every mathematical assertion in the project carries exactly one tier. No assertion is untiered.

| Tier | Name | Meaning |
|---|---|---|
| `E0` | Suggestion | Produced by Claude or by you; unread or read casually. Heuristics, analogies, "this smells like X". Carries zero weight. |
| `E1` | Read | A human has read the argument line by line and believes it. Still routinely wrong. |
| `E2` | Refereed | Survived the adversarial protocol in §7: N independent hostile passes, step isolation, and control calibration. |
| `E3` | Checked | Machine-verified. Proof assistant kernel accepts it, no `sorry`/`admit`, axiom set audited. Or: a finite computation verified by an independently written checker. |
| `E4` | Cited | Taken from the literature with a *verified locator* (§6.2). Inherits the literature's reliability, which is high but not `E3`. |
| `EX` | Refuted | Known false. Never delete these — the reason it is false is the most valuable content in the repository. |

`E2` is not a weak form of `E3`. It is a different kind of evidence: many correlated readers rather than one uncorrelated kernel. Do not add them and call it more.

### 1.2 The monotonicity rule

This is the load-bearing rule of the whole system.

> **A claim's tier is capped by the minimum tier of its dependencies.**

A machine-checked theorem whose hypothesis is an `E1` lemma is an `E1` result. A beautiful `E2` proof that cites a paper you never actually opened is `E0` until you open the paper. Enforce this with a script, not with vigilance (§4.4), because the failure is silent and always happens at 2 a.m.

The dependency structure is a DAG. Run a cycle check on every edit. Circular dependency — lemma A proved using a corollary of a theorem later proved from A — is the second most common way these projects die, and it is undetectable by reading because the cycle spans three files written six weeks apart.

### 1.3 What "independently checkable" means

The final report is independently checkable when a competent stranger, who assumes you are either mistaken or dishonest, can:

- reconstruct every `E3` claim by running your artifacts on their machine from your manifest,
- locate every `E4` claim in the cited source by theorem number,
- attack every `E2` claim knowing exactly which steps you consider weakest, because you told them (§11.6),
- see precisely which regions of the search space you covered and which you did not,
- see the measured sensitivity of your own verification pipeline (§7.5) — that is, how often it catches errors you deliberately planted.

That last item is unusual and is what distinguishes this workflow from a pile of AI-generated notes. You are not asking the reader to trust that your referee process works. You are handing them its false-negative rate.

---

## 2. Repository layout

Everything lives in one Git repository. Git is the ledger of record; chat transcripts are not.

```
PROBLEM.md              Canonical statement, definitions, conventions, notation.
                        Single source of truth. Amended only deliberately.
CLAIMS.md               The claim ledger. Every assertion, its tier, its dependencies.
ATTEMPTS.md             Every failed proof route with a DIAGNOSED failure point.
OBSTRUCTIONS.md         Barrier statements and their proofs.
literature/             One file per source. Verified locators only.
lean/                   Formal statements first, proofs second.
search/                 Counterexample search: code, seeds, logs, coverage records.
special-cases/          The specialization lattice and its status.
notes/                  Exploratory transcripts. Explicitly E0. Never cited.
report/                 The deliverable.
.claude/
  skills/               Repeatable procedures (§4.2)
  agents/               Isolated-context workers (§4.3)
  settings.json         Hooks (§4.4)
CLAUDE.md               What every session must know before it does anything.
```

### 2.1 `PROBLEM.md`

Written once, carefully, before any tool touches the problem. It contains the conjecture stated in full, every definition used, every convention (is your graph simple? is `0 ∈ ℕ`? are your measures signed? is the inequality strict?), and a list of the *degenerate cases you are and are not including*.

Definition drift across sessions is the quiet killer of long AI-assisted projects: session 14 uses a slightly weaker notion of "regular" than session 3, both proofs are correct, and the combination proves nothing. `PROBLEM.md` is loaded into every session via `CLAUDE.md` and any deviation is a hard stop.

Write it, then hand it to a fresh Claude session with the instruction: *"Find every ambiguity in these definitions. For each, give two mathematical objects that a reasonable reader would classify differently."* This is the single highest-return prompt in the entire project and takes ten minutes.

### 2.2 `CLAIMS.md`

```markdown
## C-017
statement: For every 2-connected G with n ≥ 5, φ(G) ≤ (n-1)/2.
tier: E1
depends: [C-004, C-011, LIT-006]
proof: notes/2026-08-03-phi-bound.md
lean: lean/Claims/C017.lean   (statement only; proof has sorry)
referee: none
history:
  - 2026-08-03 created E0
  - 2026-08-05 → E1 after human read
```

Tiers change only via `scripts/set_tier.py`, which recomputes the monotonic bound and refuses illegal promotions. Editing the field by hand is blocked by a hook.

---

## 3. Which surface does what

| Surface | Role in this project | Why |
|---|---|---|
| **Claude Code** | Primary environment. Owns the repo, runs Lean, SageMath, Python, SAT/SMT solvers, executes searches, edits the ledger. | The only surface where assertions can be mechanically checked in the same loop that produces them. |
| **Subagents** (`.claude/agents/`) | Refereeing, literature extraction, step isolation. | Each runs in a **separate context window** with no memory of the main conversation. This isolation is not a convenience here; it is the entire basis of the referee protocol. |
| **Skills** (`.claude/skills/`) | Encoded procedures: how to referee, how to log an attempt, how to record a literature locator, house proof style. | Runs in-context, invoked by name or matched automatically. Makes the protocol repeatable rather than remembered. |
| **Hooks** (`.claude/settings.json`) | Enforcement. Ledger integrity, `sorry`-detection, blocking premature "QED". | Hooks execute deterministically outside Claude's context and Claude cannot override them. Use them for every rule you are unwilling to renegotiate mid-session. |
| **Claude.ai Projects** | Exploratory conversation with `PROBLEM.md` as project knowledge. Brainstorming attack routes, "what area does this resemble", sanity conversations. | Cheap breadth. Everything produced here is `E0` until it lands in the repo. |
| **Artifacts** | Interactive explorers: parameter sweeps over the special-case lattice, visualizations of extremal families, slack plots. | Seeing where the inequality gets tight is often how the obstruction is found. |
| **Messages API + Batches API** | N-replica refereeing, large-scale independent proof attempts, bulk step isolation. Batches take up to 10,000 requests, return within 24 hours, at half price. | Refereeing at N=40 is a batch job, not a conversation. |
| **MCP connectors** | arXiv/Semantic Scholar, Zotero, Overleaf, GitHub, a Lean language server. | Fetching a real paper instead of recalling a plausible one. |
| **Memory / past-chat search** | Continuity across sessions on the chat side. | Useful for "did we already try this?" — but the repo, not memory, is authoritative. |

Docs: [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) · [subagents](https://code.claude.com/docs/en/sub-agents) · [Batch processing](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)

---

## 4. Configuration

### 4.1 `CLAUDE.md`

Short. It is read every session, so it should contain only non-negotiables:

- Read `PROBLEM.md` before making any mathematical assertion.
- Every new assertion enters `CLAIMS.md` at `E0`. You may not assign a higher tier.
- Never write "clearly", "easy to see", "standard argument", "similar to the above", or "WLOG" without discharging it. If a step is easy, write it; if it is long, make it a numbered claim.
- Never state a citation without a verified locator. If you have not fetched the source in this session, say "unverified recollection" explicitly.
- Failed attempts go in `ATTEMPTS.md` with a diagnosed failure point. "This didn't work" is not a diagnosis.
- When you are unsure, the correct output is the precise statement you cannot settle, not a hedged paragraph.

### 4.2 Skills to write first

- **`referee`** — the adversarial checking protocol of §7, as an executable procedure.
- **`log-attempt`** — schema for `ATTEMPTS.md`: route, key idea, exact step where it broke, whether the break is repairable, what would have to be true to repair it.
- **`cite`** — refuses to record a reference without fetched evidence: URL retrieved this session, theorem/lemma number, verbatim hypothesis list transcribed, differences from your setting enumerated.
- **`isolate-steps`** — decomposes a proof into standalone implications with all goal-context stripped (§7.3).
- **`house-style`** — your proof conventions, so that generated LaTeX is diff-able across sessions.

### 4.3 Subagents to define

- **`referee-hostile`** — receives a proof with no provenance and the instruction that it contains an error.
- **`referee-naive`** — receives a single isolated implication with no knowledge of the conjecture.
- **`lit-extractor`** — reads one fetched paper, returns structured statements and hypotheses, forbidden from commenting on your conjecture.
- **`adversary`** — tasked only with constructing counterexamples; never shown proof attempts.

The `adversary` and the prover must never share context. If the searcher knows what the answer is supposed to be, its code will find it.

### 4.4 Hooks

```
PostToolUse  on edit of CLAIMS.md   → scripts/check_ledger.py
                                       (monotonicity, DAG acyclicity, orphan refs)
PreToolUse   on write to report/    → block if string "QED"/"we have proved" appears
                                       and the corresponding claim is below E2
PostToolUse  on edit of lean/       → lake build; grep sorry|admit; #print axioms
Stop                                → refuse to end session if CLAIMS.md is dirty
                                       or any claim was promoted without a referee record
```

The point of putting these in hooks rather than in `CLAUDE.md` is that a model can rationalize its way around an instruction and cannot rationalize its way around a non-zero exit code.

---

## 5. Phase 0: before any attack

Run these in order. Total cost: a day. Skipping them costs weeks.

1. **Disambiguate the statement** (§2.1).
2. **Formalize the statement in Lean** — statement only, proof `sorry`. Formalizing a statement forces every implicit quantifier and coercion into the open. It is common to discover at this stage that you were conjecturing something subtly different from what you meant.
3. **Establish the trivial cases by hand** and check the conjecture is not already false for `n = 1`, the empty object, or the degenerate configuration.
4. **Search for the conjecture in the literature.** With MCP-connected search, plus targeted web search, plus asking Claude for *the names of the areas* this belongs to rather than for citations. Then read the surveys yourself.
5. **Write down your prior.** One paragraph: do you believe it, why, and what would change your mind. Date it. You will want this later when you are 200 hours in and motivated reasoning has set in.

---

## 6. The six workstreams

Run them concurrently. They feed each other: failed proofs suggest where to search for counterexamples, near-misses in search suggest which special cases are meaningful, patterns across failed proofs become the obstruction.

### 6.1 W1 — Refutation

**Try to kill the conjecture first, and keep trying after every failed proof attempt.** Time spent proving a false statement is unrecoverable, and a conjecture that survives serious adversarial search is a better target.

Procedure:

1. Express the conjecture as a decidable predicate over an enumerable family, in `search/`.
2. **Write the checker in an isolated session that is not told what the answer should be.** Then validate the checker: feed it instances you have hand-verified as satisfying and violating, and feed it a deliberately fabricated near-counterexample to confirm it does not silently accept.
3. Layer the search:
   - exhaustive over the small regime, to the largest size that terminates;
   - random sampling over the medium regime, with recorded seeds;
   - structured adversarial search — SAT/SMT, ILP, local search, gradient methods on continuous relaxations — aimed at maximizing violation;
   - known extremal families from the literature, which is where counterexamples to plausible conjectures usually live.
4. **Record coverage precisely.** "Verified for all `n ≤ 11`; `10^8` random samples for `12 ≤ n ≤ 30` at seed 4471; SAT-refuted violation for `n ≤ 16` under the encoding in `search/enc_v3.py`." A negative search result stated this precisely is a publishable contribution. "We searched a lot" is not.
5. **Near-miss analysis.** Record the objects with minimal slack. If slack tends to zero as the parameter grows, the conjecture is tight, no argument with slack to spare can work, and you have probably just found your obstruction (§6.5).

If a counterexample appears: verify it in Lean or with an independently written checker before you believe it, and certainly before you tell anyone. Counterexample verification is usually a finite computation and therefore the cheapest `E3` result in the entire project. Get it.

### 6.2 W2 — Reduction to known results

Two directions, both worth pursuing:

- **Import:** find known `K` with `K ⟹ C`. Then the work is reducing `C` to `K`.
- **Export:** find known-false or known-hard `K'` with `C ⟹ K'`. This refutes `C` or shows it is at least as hard as something famous — which is itself a result.

The discipline that matters here is citation hygiene. Claude is genuinely strong at *recognizing structural similarity* — "this resembles the second-moment argument in additive combinatorics", "this is a Fourier-analytic statement in disguise" — and this is a real capability worth using aggressively. It is unreliable at *theorem numbers, exact hypotheses, and attributions*, and it fails in the most dangerous way: by producing a citation that is nearly right, to a real paper, with hypotheses subtly stronger or weaker than what the paper actually assumes.

Therefore: **`literature/` accepts an entry only with a verified locator.** The `cite` skill enforces the schema:

```markdown
## LIT-006
source: arXiv:1704.xxxxx v3, fetched 2026-08-14, DOI 10.xxxx/xxxxx
result: Theorem 3.2
statement: [transcribed, in the paper's own notation]
hypotheses: [enumerated verbatim]
translation: [into PROBLEM.md notation, with the translation justified]
gap: [every hypothesis we do not satisfy, and whether it is essential]
verified-by: human, 2026-08-14
```

The `gap` field is where reductions live or die. The common failure is a translation step that quietly assumes finiteness, or uniformity, or a compactness that your setting lacks.

### 6.3 W3 — Meaningful special cases

Build a **specialization lattice** in `special-cases/`: nodes are strengthenings of the hypothesis (fix a parameter, restrict the class, add symmetry, pass to characteristic zero, bound the degree, assume the object is generic), edges are implications, and each node carries a status.

A special case is *meaningful* — as opposed to decorative — when it passes three tests:

1. **Not already known.** Check W2 first.
2. **Retains the difficulty.** State explicitly which feature of the general problem you believe is the obstacle, and confirm the special case still has it. A special case that trivializes the obstacle proves you can do the easy part.
3. **The proof's dependence on the extra hypothesis is understood.** After proving the special case, run this prompt against a fresh context: *"Here is a proof of the statement under hypothesis H. Identify every step that uses H. For each, state what the step would require if H were dropped, and whether that requirement is plausible."* The output is a map of exactly what the general case needs — and it feeds directly into W5.

The danger to watch is **generalization theatre**: a special-case proof presented as "the general argument, modulo technicalities", where the technicalities are the entire problem. Force the question: is the extra hypothesis being used for convenience, or is it load-bearing? Only the second kind teaches you anything, and it teaches you a lot.

### 6.4 W4 — Proof attempts

Generate broadly, verify narrowly.

**Generation.** Use chat/Projects for breadth: ask for ten distinct attack strategies with the *reason each might work and the step most likely to fail*, before asking for any proof. Ask which areas of mathematics have machinery for statements of this shape. Ask what the statement would look like after a change of variables, dualization, or a probabilistic reformulation. This is where a broad, fast, associative system earns its cost.

**Structure.** Never accept a monolithic proof. Require decomposition into numbered claims that enter `CLAIMS.md` individually. A proof of the main result is then a claim whose dependencies are the lemmas, and the monotonicity rule does the rest: your headline theorem cannot outrank its weakest lemma, no matter how confident the prose.

**Independent replicas.** Submit the same lemma to N independent attempts via the Batches API, with no shared context. Then read the *disagreements*: where attempts diverge is where the difficulty is. Where all attempts produce the same slick step, be suspicious rather than reassured — correlated training produces correlated blind spots, and unanimity among replicas is not independent confirmation. Never convert an agreement rate into a probability.

**Verification.** Every proof goes through §7 before rising above `E1`, and through Lean before reaching `E3`.

### 6.5 W5 — Precise obstructions

An obstruction is not "this is hard". It is a theorem of the form:

> Any proof of `C` using only technique `T` would yield a proof of `S`. But `S` is false / open / known to be hard.

Getting there requires that your failures be *data*, which is why `ATTEMPTS.md` demands a diagnosed failure point. Procedure:

1. Log every failed route with the exact step that broke and what the step needed.
2. Cluster the failure points. Three or more distinct routes failing at the same requirement is a candidate obstruction.
3. Formulate the requirement as an explicit intermediate statement `S`.
4. **Attack `S` with the full W1 machinery.** If you find a counterexample to `S`, you have killed an entire family of proof strategies — a genuine, reportable result, and often more valuable than another special case.
5. Where the technique class can be formalized (relativizing arguments, natural-proof-style constructions, local or slack-based arguments in combinatorics, methods that only use the first two moments, arguments invariant under a symmetry the statement lacks), state the barrier as a theorem and prove it.

Tightness data from W1's near-miss analysis is the most common seed for this: if the inequality is asymptotically sharp on an explicit family, then every argument that discards a constant factor is dead, and you can say so precisely.

### 6.6 W6 — The report

See §11. It is written continuously, not at the end. The report is the project's actual output even if the conjecture remains open — especially then.

---

## 7. The adversarial verification protocol

This is the part that does the real work. Read it twice.

### 7.1 Rule of separation

**A context that produced an argument may never evaluate it.** Asking Claude to check its own proof produces agreement, because continuation is the model's operating mode and the proof is already in the context as an established premise. All verification happens in subagents or fresh API calls with no shared history.

### 7.2 Hostile framing

Do not ask "is this proof correct?" That question is answered agreeably. Ask instead:

> "The following proof contains at least one error. Find it. For each numbered step, state (a) the precise hypotheses used, (b) where each was established, (c) the exact instantiation of every quantifier, and (d) the strongest counterexample you can construct to that step *taken in isolation*. Report the step you consider weakest even if you cannot break it."

Presupposing the error is doing real work: it changes the task from ratification to search. The cost is false positives — hostile referees invent objections. That is the correct trade, and false positives are cheap to dismiss while false negatives end careers.

### 7.3 Step isolation

The strongest single technique available. Extract each inference as a standalone implication, strip all context — the conjecture, the surrounding proof, any indication of what should be true — and hand it to a referee that does not know what you want.

`"Let X be a measurable space and f: X → ℝ satisfy (i)…(ii)…. Does it follow that ∫f dμ ≥ 0? Prove or give a counterexample."`

With the goal removed, the pull toward the desired conclusion is removed with it. Steps that survive five referees in context frequently die in the first isolated pass. Automate this with the `isolate-steps` skill plus a batch job over the resulting implications.

### 7.4 Negation control

For any claim you are about to promote, run the *negation* through the identical pipeline. If the pipeline produces a confident proof of both `P` and `¬P`, it has no discriminating power on this material, and its verdict on `P` is worthless. Run this deliberately and record the outcome — it is a measurement of your instrument, and instruments that are never calibrated are not instruments.

### 7.5 Planted-error calibration

Seed your referee queue with proofs into which you have injected known errors of realistic subtlety: a swapped quantifier order, a limit interchanged without justification, an induction whose hypothesis is not the statement being proved, a bound applied outside its range of validity, a case analysis missing the boundary case, division by a quantity that can vanish.

Measure the detection rate per error class. This gives you:

- a decision rule for how many referee passes a claim needs before `E2`,
- a known blind-spot list (in practice: uniformity, boundary cases, and quantifier order are caught far less often than algebraic slips),
- **a number to publish in the report**, so that readers can discount your `E2` claims by your own measured false-negative rate rather than by their general suspicion of AI-assisted work.

This is what turns "we checked it with several AI passes" into something with evidential content.

### 7.6 The formal tier

The kernel is the only referee that cannot be persuaded. Full formalization of research-level mathematics remains expensive, so prioritize:

1. **Statements** — cheap, catches ambiguity, do it always.
2. **Counterexamples** — usually finite computation, cheap, and it is exactly where certainty matters most.
3. **Special cases** — often tractable, and they anchor the specialization lattice.
4. **The key lemma** — the step everything depends on. Even if the surrounding argument stays informal, formalizing the crux moves the whole structure's weakest point.
5. **The full proof** — if the result warrants the investment.

Claude Code with `lake build` in the loop is well suited to the grind of formalization: it iterates against compiler errors, which is a setting where its output is checked at every step. Guard the exits with hooks: no `sorry`, no `admit`, and `#print axioms` audited so that nothing sneaks in via an unexpected axiom or a `native_decide` you did not intend to trust.

---

## 8. Session discipline

- **One workstream per session.** Mixed sessions produce contaminated contexts — the prover learns what the searcher found and stops searching honestly.
- **Long sessions degrade.** When the context is full of a hundred pages of attempted proof, earlier errors have become established premises. Restart, carrying over only `CLAIMS.md` and `PROBLEM.md`.
- **The repo is the memory.** If it is not committed, it did not happen. Chat memory and transcript search are for convenience ("have we tried Fourier here?"), never for authority.
- **Commit failures.** `ATTEMPTS.md` grows faster than `CLAIMS.md` in any honest project. That ratio is a health indicator, not a problem.
- **Re-run W1 after every significant W4 failure.** Repeated failure at the same point is weak evidence of falsity, and the search should be re-aimed at the structure the failed proof needed.

### Rough budget

For a first serious pass at an open problem, a defensible allocation is: 20% refutation, 20% literature and reduction, 20% special cases, 25% proof attempts, 15% obstruction analysis — with the report written continuously throughout rather than allocated. Adjust as evidence accumulates; the point of the initial split is to prevent the natural drift in which proof attempts consume everything and the project produces nothing checkable.

---

## 9. Failure modes

| Failure | Signature | Countermeasure |
|---|---|---|
| Fluent wrong proof | "It is easy to see", "by a standard argument", "similar to the above", an unjustified WLOG, quantifier order slippage, implicit uniformity, interchanged limits, an unexamined degenerate case | §7.3 step isolation; ban the phrases in `CLAUDE.md` |
| Sycophantic verification | Referee agrees, praises the elegance, suggests a cosmetic improvement | §7.1 separation, §7.2 hostile framing, §7.4 negation control |
| Hallucinated citation | Real paper, plausible theorem number, hypotheses subtly different | `cite` skill; fetch or it does not exist |
| Circularity | Lemma A ← Corollary B ← Theorem C ← Lemma A, spanning weeks | DAG cycle check in a hook |
| Definition drift | Two correct proofs that do not compose | Single canonical `PROBLEM.md`; disambiguation pass |
| Search that agrees by construction | The checker encodes the conjecture's conclusion in its own predicate | Write and validate the checker in an isolated session; plant a fake counterexample and confirm detection |
| Overfitted special case | "Extends to the general case modulo technicalities" | §6.3 test 3 — enumerate every use of the extra hypothesis |
| Correlated replicas | 40/40 agreement treated as near-certainty | Never convert agreement into probability; unanimity on a hard step is a warning |
| Motivated reasoning | Month three, the proof is nearly done, the last gap keeps moving | Your dated Phase 0 prior; scheduled W1 re-runs |

---

## 10. Interpreting the outcomes

You will end in one of five states, and four of them are results.

**Refuted.** You have a counterexample. Verify it formally, minimize it, and characterize the failure — the interesting output is not the object but the structural reason the conjecture was wrong, and the repaired conjecture that survives it.

**Reduced.** `C` follows from known `K`, or implies known-hard `K'`. Publish the reduction with the `gap` analysis explicit.

**Partially resolved.** Special cases proved, general case open. The value is in the boundary: state precisely where your methods stop and why.

**Obstructed.** You have a theorem showing a class of methods cannot work. This is frequently the most valuable outcome, because it redirects everyone else's effort. Treat it as the headline result, not as an apology.

**Open with a map.** No resolution, but a precise account of what was searched, what was tried, where each route died, and what would have to be true for each to be repaired. This is a real contribution and it is what most honest attacks on open problems produce.

The failure state, distinct from all five, is: a confident-sounding proof no one has checked. The entire apparatus above exists to make that state unreachable by accident.

---

## 11. The report specification

`report/` contains a document that a hostile referee can process without trusting you.

**11.1 Statement and conventions.** Verbatim from `PROBLEM.md`, including the degenerate cases explicitly in or out of scope.

**11.2 Status summary.** Every claim, its tier, one line each. The reader should be able to see the shape of what you have in ninety seconds.

**11.3 Dependency graph.** Rendered from `CLAIMS.md`. Tiers visible on the nodes. This makes the monotonicity constraint auditable by inspection — if a node is `E3` and a parent is `E1`, the reader will see it immediately, and so will you.

**11.4 Results, with proofs at referee-checkable granularity.** No compression. Machine-checked results flagged with file path, commit hash, and toolchain version.

**11.5 Negative results, given equal weight.** Search coverage with exact regions, seeds, and encodings. Failed routes with diagnosed failure points. Obstructions with proofs. This section is the honest core of most such reports.

**11.6 Where to attack.** Your own ranked list of the weakest points in the argument, with reasons. Volunteering this is not weakness; it is the difference between a document that invites checking and one that resists it, and referees can tell the difference immediately.

**11.7 Verification methodology and its measured limits.** The referee protocol used, the number of passes per claim, and the planted-error detection rates from §7.5, broken down by error class.

**11.8 Reproducibility manifest.**

```yaml
repo: <url> @ <commit>
lean: <toolchain> / mathlib @ <commit>
compute: <python/sage versions, solver versions, hardware, wall time>
seeds: [ ... ]
models: [claude-<model>-<date>, ...]
batch_ids: [ ... ]      # for referee runs
date_range: 2026-05-01 .. 2026-08-14
```

Model identifiers and dates matter: model behavior changes across versions, so a referee attempting to reproduce your `E2` results needs to know what produced them, and a reader in two years needs to know it too.

**11.9 Disclosure.** State plainly which parts were AI-assisted and in what role: candidate generation, refereeing, formalization support, search implementation, exposition. State which claims are machine-checked and which rest on human reading. Follow the venue's policy; most now require this, and understating it is the fastest way to lose a referee's trust in everything else in the document.

---

## 12. Authorship

You are the author. Every claim in the report is one you are personally staking your name on, and "the model said so" is not a defense that exists in mathematics. The correct posture toward this environment is that of a researcher with an extremely fast, extremely well-read, extremely confident collaborator who is wrong often enough that you check everything and who cannot be held responsible for anything.

Do not post AI-generated proofs of open problems to arXiv or submit them to journals without verification at `E2` minimum and preferably `E3`. The volume of unverified claimed resolutions of famous conjectures is already a serious burden on the people who maintain these fields, and the cost of adding to it falls on exactly the researchers whose time is most worth protecting.

Used with the discipline above, though, this is a genuinely powerful setup — not because it proves things, but because it lets one person run breadth-first search over attack strategies, adversarial search over counterexamples, systematic literature reduction, and continuous formal verification, concurrently, at a scale that used to require a group. The theorem, if there is one, is still yours to find.
