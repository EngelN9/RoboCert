# Interactive Cross-Verification Protocol — v2

Revision of the v1 protocol. Changes are driven by one principle: **independence that is
structurally enforced beats independence that is merely instructed.** A single verifier told
"do not let Proof C influence your reading of Proof A" will be influenced anyway. Splitting the
work across separate conversations makes the contamination impossible rather than discouraged.

---

# PART 0 — WHAT *YOU* DO BEFORE ANY PROMPTING

This part is not pasted to any model.

### 0.1 Blind the proofs

v1 opens by telling the verifier that Proof C is ChatGPT's and Proof A is Claude's. Remove this.
When Claude verifies, it is being told which proof is its own; when ChatGPT verifies, likewise.
Self-preference and its inverse (overcorrecting against your own output) are both live risks, and
neither is detectable from the transcript.

- Relabel the proofs **P₁** and **P₂**.
- Randomize the assignment by coin flip, and record the mapping somewhere you will not paste.
- Strip headers, sign-offs, model-characteristic formatting (em-dash habits, section-numbering
  style, LaTeX macro preferences, "Great question"-type residue).
- Normalize both proofs to the same notation and the same LaTeX conventions where this can be
  done without altering mathematical content. Divergent notation is itself an attribution cue.

Perfect blinding is impossible — writing style survives normalization. That is what §1.4 below is
for.

### 0.2 The run matrix

Instead of two long single-conversation runs with reversed order, run **six short conversations**:

| Session | Conversation | Input | Output artifact |
|---|---|---|---|
| L | fresh | theorem only | LEDGER |
| L′ | fresh, *other model* | theorem only | LEDGER′ |
| A₁ | fresh | LEDGER + P₁ | AUDIT(P₁) |
| A₂ | fresh | LEDGER + P₂ | AUDIT(P₂) |
| X | fresh | LEDGER + both proofs + both audits | ADJUDICATION |
| S | fresh, optional | LEDGER + adjudicated arguments | SYNTHESIS |

Sessions A₁ and A₂ are the load-bearing ones. Because they are separate conversations, the second
proof is audited by a verifier that has no memory of the first — order effects are not *detected*,
they are *absent*. This is strictly stronger than reversing the order within one session.

For a research proof that matters, run A₁ and A₂ in **both** models: four audits, two per proof,
each blind. Then Session X consumes all four. Cost is lower than v1's two full runs, because each
session is short.

Reversed-order runs remain useful only if you insist on a single continuous conversation. If so,
note the asymmetry the reversal does *not* fix: the first proof is audited against the ledger
alone, while the second is audited by a verifier that has already committed to a provisional
verdict and built a preferred picture of how the argument should go. Agreement across the two
orders shows the conclusion is order-robust; it does not restore the second audit's independence.

### 0.3 Do not reveal your own suspicions

Not before Session X's verdict. If you have a step you distrust, hold it. After the verdict, ask
for a targeted re-examination (Part 5, command `PROBE`). Asking earlier converts your prior into
the model's finding.

---

# PART 1 — SESSION L: THEOREM INTAKE AND OBLIGATION LEDGER

Paste this with the theorem. **Do not paste either proof in this session.**

=== BEGIN SESSION L PROMPT ===

You are a senior research mathematician acting as referee for a journal with a high rejection
rate. In this session you will not see any candidate proof. Your task is to establish, from the
theorem alone, what a correct proof would be obliged to do.

THEOREM: [paste]
PERMITTED PRIOR RESULTS (usable without proof): [paste]
DEFINITIONS AND AMBIENT ASSUMPTIONS: [paste]

## L.1 Formal parse

Restate the theorem. Then list: all objects with domains and codomains; every hypothesis, numbered
H₁…H_m; every quantified variable **with quantifier order made explicit**; every existence,
uniqueness, implication, equivalence, and universal assertion; and every boundary or degenerate
case the wording admits. Where the logical form is not obvious, rewrite it schematically —
distinguish A ⟹ B from A ⟺ B, and ∀x∃y P(x,y) from ∃y∀x P(x,y).

## L.2 Is the theorem even true?

*(New in v2. This is mandatory and comes before any obligation-setting.)*

Spend real effort attempting to **disprove** the statement as written:

- evaluate the smallest admissible cases explicitly;
- test the boundary of each hypothesis;
- test whether dropping any hypothesis Hᵢ yields a statement you can falsify — and if you cannot,
  say so, because a hypothesis whose necessity you cannot demonstrate is a hypothesis the proofs
  may not actually need, which is itself diagnostic;
- check for quantifier-order readings under which the statement is false;
- do any arithmetic or symbolic computation that a small case permits.

Report: FOUND COUNTEREXAMPLE (state it) / NO COUNTEREXAMPLE FOUND (state what you tried and how
hard) / STATEMENT AMBIGUOUS (state the readings, ask me to disambiguate before continuing).

If the statement is ill-posed, stop here. Verifying proofs of an ill-posed claim is wasted work.

## L.3 The obligation ledger

Enumerate the proof obligations O₁…O_n that *any* correct proof must discharge, derived from the
theorem alone and not from any anticipated proof strategy. Each must be checkable in isolation.

Cover, **only where the theorem actually makes them live**, obligations of these kinds: existence;
uniqueness; well-definedness; independence of choices; nonvanishing denominators; invertibility;
exhaustiveness of case splits; boundary, zero, and singular cases; sign cases; chart coverage and
overlap compatibility; connectedness; continuity, differentiability, convergence; compactness,
finiteness, dimension; characteristic and algebraic-closure assumptions; measurability; rank
conditions; symmetry and orientation.

Do not pad. An obligation the theorem does not generate is noise that will dilute your attention
later. State the dependency structure, e.g. (H₁,H₂) ⟹ O₁, (O₁,O₂) ⟹ O₄, (O₃,O₄) ⟹ T.

## L.4 Pre-registered difficulty forecast

*(New in v2.)* Before seeing any proof, name the three to five points at which you expect a proof
of this theorem to be hardest or most likely to cheat, and say what the characteristic cheat would
look like at each. Number these F₁…F_k.

This is pre-registration: it is easy, later, to be persuaded that a difficulty was minor because a
proof glided over it. A forecast made in ignorance of the proofs is not revisable by them.

## L.5 Freeze

Output the whole of L.1, L.3, and L.4 as a single self-contained block labelled **LEDGER v1**,
written so it can be pasted into a fresh conversation with no other context. Then stop.

=== END SESSION L PROMPT ===

**Run L twice, once in each model.** Then compare the two ledgers yourself. Obligations that
appear in one ledger and not the other are the highest-value objects in this entire protocol: they
are difficulties one model cannot see unaided, and if that model also wrote one of the proofs, you
have located a likely blind spot before reading a single line of it. Merge into a union ledger.
Divergence in F₁…F_k is similarly diagnostic.

---

# PART 2 — SESSIONS A₁ / A₂: BLIND SINGLE-PROOF AUDIT

Run once per proof, each in a **fresh conversation**. Paste the merged ledger and exactly one
proof. Never mention that another proof exists.

=== BEGIN AUDIT PROMPT ===

You are refereeing a submitted proof for a journal with a high rejection rate. Your default
assumption is that the proof is wrong until each step is verified. The proof has already been
revised in response to a prior review; this is not evidence in its favour.

LEDGER v1: [paste]
PROOF: [paste]

## Ground rules

1. Do not repair the proof. A gap you can fill yourself is still a gap **in the proof**, and is
   logged as one. Note separately that you can fill it.
2. Do not add hypotheses, and do not adjust the theorem to fit the argument.
3. "Clearly", "it follows", "similarly", "standard", and "WLOG" are not justifications. Each is
   either expanded by you or logged as a gap.
4. If you cannot verify a step, write UNVERIFIED. Never write "presumably" or "one checks".
5. Separate mathematical correctness from exposition throughout. Do not let clarity, confidence of
   tone, or sophistication of vocabulary function as evidence.
6. Separate *does the cited theorem say this* from *are its hypotheses satisfied here*. These are
   never one judgment.
7. You may have authored this proof yourself. That is irrelevant to the verdict. If you suspect
   you did, say so explicitly and why, and then apply stricter scrutiny, not lesser.

## A.1 Reconstruct the dependency graph

Extract the principal claims S₁…S_r and the derivation structure the proof asserts. Present it as
a graph or indented dependency list. State which claims the theorem's conclusion actually rests on
and which are decorative.

## A.2 Screening pass — triage before depth

*(New in v2. v1 applied a 22-question checklist to every nontrivial inference; uniform depth
across dozens of steps produces uniform shallowness. Triage first.)*

Tag each step Sᵢ with the risk classes it touches, from:

`Q` quantifier movement · `E` existence/uniqueness assumed · `L→G` local promoted to global ·
`GEN` generic treated as universal · `DIV` division or cancellation · `INV` inversion ·
`ROOT` squaring/roots and sign loss · `CHART` coordinates or charts · `SYM` asserted symmetry ·
`CIT` external citation · `CIRC` possible circularity · `NOT` notation drift ·
`CASE` case split · `LIM` limit/sum/integral interchange · `REG` regularity or convergence

Then audit **in depth only the steps carrying tags**, plus every step touching an obligation Oᵢ or
a forecast point F_j, plus the final step that claims to deliver the theorem. Explicitly list the
untagged steps you are passing over, so the choice is visible and I can override it.

For each audited step give: what is asserted · what supports it · which external result is used ·
whether *each* of its hypotheses is satisfied here · whether it yields exactly the claimed
conclusion, or more, or less.

## A.3 Hypothesis-consumption test

*(New in v2 — high yield, and absent from v1.)*

For each hypothesis H₁…H_m of the theorem, name the **exact step** where the proof genuinely
consumes it. Then delete Hᵢ from the theorem and reread the proof text verbatim. If the argument
still appears to go through, one of these holds: the hypothesis is unused (and the proof proves
more than the theorem — suspicious), or the step that should consume it is doing so tacitly (a
hidden assumption), or the proof is invalid. Report which, per hypothesis.

Apply the same test in reverse: does this argument, essentially unchanged, also prove a statement
you know to be false? A proof that proves too much is broken regardless of how it reads.

## A.4 Degenerate-case attack

Actively search for parameter values at which any formula, determinant, denominator, selector,
chart, or auxiliary construction becomes zero, undefined, rank-deficient, non-unique, identically
true, identically false, or independent of the variable it is supposed to depend on. Do not assume
genericity unless genericity is hypothesized. Run the proof against each such value and report
what happens, not what should happen.

## A.5 Obligation matrix

For each Oᵢ in the ledger assign exactly one of: DISCHARGED · PARTIALLY DISCHARGED · NOT
DISCHARGED · INCORRECTLY DISCHARGED · NOT APPLICABLE (with justification). Give the precise
location in the proof where it is allegedly handled.

**Verification basis rule** *(new in v2)*: every DISCHARGED verdict must name its basis, one of —
(a) I derived the claim independently; (b) I checked the cited theorem's hypotheses one by one;
(c) I verified the case split is exhaustive; (d) I computed or evaluated it. If your basis is that
the proof's own explanation reads convincingly, the status is at most PARTIALLY DISCHARGED. This
rule exists because paraphrasing a proof fluently feels like verifying it and is not.

## A.6 Defect report

For each defect, as **F-k**: problematic step (quoted) · why, precisely · classification (Fatal /
Substantive / Minor / Expository) · affected obligations · downstream dependencies · what exactly
would have to be proved to repair it. Do not perform the repair.

## A.7 Verdict

One of: **V1** correct · **V2** correct modulo minor or expository issues · **V3** substantively
incomplete · **V4** incorrect but plausibly repairable · **V5** fatally incorrect.

State your confidence and name the specific thing that most reduces it. Then answer: *if this
proof is wrong, where is the error most likely to be?* Answer even if your verdict is V1.

## A.8 Freeze

Emit everything above as a self-contained block labelled **AUDIT REPORT — [P₁ or P₂]**, suitable
for pasting into a fresh conversation. Preserve all identifiers. Then stop.

=== END AUDIT PROMPT ===

---

# PART 3 — SESSION X: ADJUDICATION

Fresh conversation. Paste the ledger, both proofs, and all frozen audit reports. Keep the labels
P₁/P₂ — still no attribution.

=== BEGIN ADJUDICATION PROMPT ===

Two candidate proofs of the same theorem, and independent blind audits of each, are below. Both
proofs remain unverified. Audit reports are evidence, not authority; you may overturn any verdict
in them, and must say so explicitly when you do.

The governing rule: **agreement between the proofs is not evidence of correctness.** A defect
present in both is more dangerous than one present in either, because it indicates a correlated
failure mode rather than an isolated slip. Symmetrically, disagreement does not imply one is
wrong: they may be correct by different routes, or both wrong.

LEDGER v1: [paste] · PROOF P₁: [paste] · PROOF P₂: [paste] · AUDIT REPORTS: [paste all]

## X.1 Do they prove the same statement?

Before anything else. Compare the theorem each proof actually establishes: hypotheses used,
quantifier order delivered, scope of the conclusion, cases covered. Divergence here outranks every
difference in technique, and is the most commonly missed failure in AI-generated proof pairs.

## X.2 Obligation correspondence

Per obligation, a row: mechanism in P₁ · mechanism in P₂ · relationship, classified as one of —
same argument · substantially equivalent · genuinely independent · only P₁ addresses it · only P₂
addresses it · both omit it · both address it incorrectly · arguments conflict.

Justify "genuinely independent" whenever you claim it. Two arguments differing in presentation but
resting on the same lemma are not independent, and this is the distinction the whole protocol
turns on.

## X.3 Shared-blind-spot attack — mandatory

Construct the set of nontrivial claims used by both proofs. For each, ask: did both merely assume
the same "standard fact"? invoke the same theorem with the same unchecked hypothesis? divide by
the same quantity without establishing nonvanishing? overlook the same degenerate case? make the
same quantifier transition? inherit the same plausible-but-false lemma? confuse genericity with
universality in the same place?

Label these **SB-k**. For each, adjudicate from first principles — not by noting that two
independent systems agreed.

Then check the shared claims against the forecast points F₁…F_k from the ledger. A forecast
difficulty that *both* proofs pass smoothly and briefly is the single strongest signal available
that both are gliding rather than proving. Report every such coincidence explicitly.

## X.4 Disagreement adjudication

For each substantive disagreement **D-j**: claim in P₁ · claim in P₂ · are these actually
incompatible (if not, why not) · if yes, adjudicate from first principles. Never by majority,
plausibility of tone, or source. Conclude with exactly one of: P₁ correct / P₂ correct / both
wrong / both correct under different constructions / undecidable without a specified additional
lemma or source check (isolate the precise proposition needed).

## X.5 Source ledger

For every external result logically indispensable and not among the permitted prerequisites,
record separately: does the cited result state what is claimed, and are its hypotheses satisfied
here. Where you cannot responsibly verify the source, mark **SOURCE VERIFICATION REQUIRED**.
Never reconstruct a citation from memory to fill the gap.

## X.6 Reconciliation matrix

Per obligation: status in P₁ · status in P₂ · adjudicated status, from — rigorously discharged by
both · by P₁ only · by P₂ only · discharged by distinct independent arguments · not discharged ·
disputed · source verification required.

## X.7 Verdicts

Per proof, on the V1–V5 scale. Then exactly one cross-verification verdict:

- **CV-1** both correct, all obligations discharged, arguments sufficiently independent that
  agreement adds informal confidence
- **CV-2** both appear correct but key dependencies are shared; agreement adds little
- **CV-3** exactly one survives
- **CV-4** neither complete alone, plausibly combinable
- **CV-5** shared substantive defect
- **CV-6** distinct substantive defects
- **CV-7** unresolved pending further verification

## X.8 Residual risk — mandatory even for CV-1

Name the three to five most delicate points, and answer: **what is the strongest plausible way in
which both proofs are still wrong?** Then state the strongest proportionate next step — an
additional independent proof, a specific cited theorem to check, symbolic or numerical
certification, exhaustive finite case analysis, formalization of one critical lemma, or human
expert review. Name the specific portion; do not recommend formalization of the whole as a reflex.

=== END ADJUDICATION PROMPT ===

**Cut from v1:** the "relative assessment of the two proofs" stage (which is clearer, which is
better). The reconciliation matrix already carries every correctness-relevant comparison, and a
quality ranking invites exactly the model-versus-model framing the protocol's own preamble
disclaims. If you want it, run it after the verdict, never before.

---

# PART 4 — SESSION S: SYNTHESIS (OPTIONAL)

Fresh conversation, only after you have read the adjudication. Paste the ledger and the arguments
that survived, not the original proofs.

Construct P\* from the obligation ledger, using only adjudicated-surviving arguments. It must not
be a splice. For each defect found earlier, state explicitly why it cannot re-enter. Then run a
regression audit of P\* against the ledger using the Part 2 prompt, in yet another fresh
conversation — a synthesized proof is a new unverified proof, and inherits no credit from its
components.

---

# PART 5 — INTERACTION COMMANDS

Include in every session prompt:

> Complete only the current stage, then stop and tell me exactly what to provide next. Do not
> request anything belonging to a later stage. Preserve all identifiers across the session.
>
> End each stage with: `READY — CONTINUE / CHALLENGE <id> / DEFEND <id> / EXPAND <id> / PROBE <id>`
>
> - **CHALLENGE <id>** — I dispute your verdict and give an argument. Re-examine it seriously and
>   **keep your verdict if you can defend it.** Do not concede because I pushed. If you do change
>   your verdict, state precisely what changed your mind and what would change it back.
> - **DEFEND <id>** — give your strongest argument that the step is sound, then immediately your
>   strongest argument that it is not, then adjudicate between them.
> - **EXPAND <id>** — full formal detail of that step alone, with no summary of anything else.
> - **PROBE <id>** — re-examine with a specific concern I supply. Treat my concern as a
>   hypothesis to test, not a finding to confirm; report if it is unfounded.

The anti-capitulation clause matters more than it looks. The dominant failure mode of an
interactive verifier is not missing an error — it is abandoning a correct finding when the user
sounds confident.

---

# PART 6 — WHAT THIS DOES NOT GIVE YOU

Stated plainly, because the elaborateness of the apparatus is itself a persuasion risk.

- Four blind audits agreeing on a step that neither proof proves leaves that step unproved. The
  protocol's output is a **list of surviving obligations and their evidential basis**, not a
  verification.
- Blinding is imperfect. Style survives normalization, and a model that recognizes its own prose
  may not report it.
- Both models were trained on overlapping corpora. Their shared blind spots are correlated in ways
  no amount of procedural separation can decorrelate. §X.3 detects some of these; it cannot
  detect a misconception uniform across the literature both learned from.
- Nothing here is formal verification. The honest description of a clean CV-1 outcome is: *no
  defect was found by four independent blind audits working from a pre-registered obligation
  ledger* — which is a real and non-trivial statement, and considerably weaker than *proved*.
