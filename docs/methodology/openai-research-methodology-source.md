# Manual: Using OpenAI Tools as a Coordinated Mathematical Research Environment

## 1. Purpose

This manual describes a disciplined way to use OpenAI tools as a coordinated research environment for attacking a mathematical conjecture.

The objective is not merely to make ChatGPT generate a plausible proof. The research environment should be capable of pursuing several logically distinct outcomes:

1. prove the conjecture;
2. construct a counterexample;
3. reduce the conjecture to one or more known theorems;
4. establish nontrivial special cases;
5. isolate a precise obstruction explaining why a natural proof strategy fails;
6. produce a rigorous research report that another mathematician can independently check.

The central principle is:

> **Separate exploration from verification.**

During exploration, speculative ideas, computations, analogies, conjectural lemmas, and incomplete arguments are useful. During verification, none of these receives credit unless every hypothesis, inference, calculation, and citation can be checked independently.

Accordingly, the correct goal is not:

> “Ask an AI to solve the conjecture.”

It is:

> **Construct a research process in which AI-generated mathematical claims are progressively converted into explicit, auditable mathematical objects.**

---

# 2. The OpenAI research environment

A useful mathematical research environment can be organized around several OpenAI capabilities.

## 2.1 Projects: the research workspace

Create a dedicated **ChatGPT Project** for the conjecture.

Treat the Project as the equivalent of a research group's common workspace.

It should contain:

- the exact conjecture;
- definitions and notation;
- relevant papers and books;
- known examples and counterexamples;
- computational data;
- proof attempts;
- rejected arguments;
- open lemmas;
- bibliographic information;
- verification reports;
- the evolving final manuscript.

Do **not** conduct the entire investigation in one enormous conversation.

Instead, create separate chats for separate research functions.

A recommended structure is:

```text
PROJECT: Conjecture X

00 — Problem specification
01 — Literature and known results
02 — Structural analysis
03 — Proof attempt A
04 — Proof attempt B
05 — Counterexample search
06 — Reduction to known theorems
07 — Special cases
08 — Computational experiments
09 — Obstruction analysis
10 — Referee / adversarial audit
11 — Final proof reconstruction
12 — Research report
```

This separation reduces contamination between speculative reasoning and later verification.

---

# 3. Assign different chats different mathematical roles

The environment works best when different conversations have sharply defined responsibilities.

## Role A — Problem formalizer

Its task is to determine exactly what is being claimed.

It should not attempt to prove the conjecture yet.

Ask:

> Rewrite the conjecture with all quantifiers explicit. Define every mathematical object and convention. Identify implicit assumptions, degenerate cases, boundary cases, and possible ambiguities. Determine whether the statement is even well-posed.

The output should include:

- domain of quantification;
- hypotheses;
- conclusion;
- dependence of constants;
- finiteness assumptions;
- regularity assumptions;
- characteristic assumptions;
- compactness/properness/completeness assumptions;
- equivalence relations being used;
- treatment of empty or degenerate objects.

A surprising number of apparent research problems become easier once the precise logical statement is exposed.

---

## Role B — Literature mapper

Use **Deep Research** primarily for this stage.

The literature mapper should answer questions such as:

- Has the conjecture already appeared under another name?
- Is there a stronger theorem in the literature?
- Are apparently similar statements actually weaker because of an omitted hypothesis?
- Are there known counterexamples nearby?
- Which standard theories contain the relevant machinery?
- Which authors and papers form the citation graph surrounding the problem?

A strong Deep Research instruction is:

> Investigate whether the following conjecture is known, equivalent to a known problem, implied by a known theorem, contradicted by known examples, or contained in a stronger existing result. Prefer primary mathematical sources. Distinguish exact matches from superficially similar statements. For every potentially relevant theorem, state its precise hypotheses and explain whether they match the conjecture.

The output should not merely be a bibliography.

Create a **theorem compatibility table**:

| Result | Conclusion | Required hypotheses | Match? | Missing condition |
|---|---|---|---|---|
| Theorem A | ... | ... | exact | none |
| Theorem B | ... | ... | partial | compactness |
| Theorem C | ... | ... | no | assumes characteristic 0 |

The missing-condition column often reveals the real obstruction.

---

# 4. Use Search for theorem verification, not only discovery

In mathematical research, Search is especially useful for **targeted verification**.

For example:

> Locate the original source for Theorem X. Verify the precise published formulation rather than relying on secondary descriptions.

Or:

> Search for counterexamples to the statement obtained by deleting hypothesis H from theorem T.

Or:

> Determine whether the term “property P” has competing definitions in this literature.

When a proof depends on an external theorem, record:

```text
Theorem:
Source:
Exact statement:
Page/theorem number:
Hypotheses:
How each hypothesis is satisfied:
Exact conclusion used:
```

Never permit the proof to contain a line such as

> “By a standard theorem...”

unless the theorem has actually been identified and its hypotheses checked.

---

# 5. Build a primary-source library

Upload the important papers, preprints, notes, book chapters, computational outputs, and earlier drafts.

For serious mathematics, distinguish three source levels:

### Level I — authoritative

- published paper;
- author's final manuscript;
- authoritative monograph;
- official theorem-prover library;
- primary computational dataset.

### Level II — useful but secondary

- survey;
- lecture notes;
- thesis;
- MathOverflow discussion;
- review article.

### Level III — discovery only

- informal webpage;
- forum discussion;
- unsourced AI response.

A Level III source may suggest a theorem.

It should normally not be the final authority for that theorem.

---

# 6. Construct a mathematical dependency graph

Before attempting a long proof, decompose the conjecture.

Suppose the conjecture is $C$.

Ask the structural-analysis chat:

> Decompose $C$ into the smallest useful sequence of intermediate statements. Distinguish necessary reductions from merely plausible lemmas. Construct a dependency DAG rather than forcing a linear proof.

You may obtain something like

$$
L_1,L_2 \Longrightarrow L_4,
$$

$$
L_3 \Longrightarrow L_5,
$$

$$
L_4,L_5,L_6 \Longrightarrow C.
$$

Record the status of every node:

```text
PROVED
PROVED USING EXTERNAL THEOREM
COMPUTATIONALLY VERIFIED ONLY
PLAUSIBLE
OPEN
FALSE
FALSE WITHOUT ADDITIONAL HYPOTHESIS
```

This prevents an argument from silently using an unproved intermediate claim.

A useful lemma ledger is:

| ID | Statement | Status | Dependencies | Evidence |
|---|---|---|---|---|
| L1 | ... | proved | none | direct proof |
| L2 | ... | open | L1 | — |
| L3 | ... | false | — | counterexample E4 |
| L4 | ... | conditional | L2 | derivation |

---

# 7. Run proof search and counterexample search in parallel

Do not make “try to prove it” the only research direction.

At minimum, maintain two independent branches.

## Branch P — proof search

Ask:

> Attempt to prove the conjecture. Before writing a polished proof, enumerate several genuinely different strategies and identify the pivotal lemma required by each.

Possible strategy families include:

- induction;
- minimal-counterexample arguments;
- extremal arguments;
- compactness;
- duality;
- localization;
- deformation;
- normalization;
- spectral sequences;
- probabilistic methods;
- algebraic or analytic estimates;
- reduction modulo primes;
- representation theory;
- categorical reformulation;
- convexity;
- topological obstruction arguments;
- computational algebra.

The relevant families depend on the field.

Require each proposed strategy to expose its critical point:

```text
Strategy:
Key reduction:
Hardest lemma:
Why the lemma might hold:
Known theorem that resembles it:
Likely failure mode:
```

This makes proof search diagnosable.

---

## Branch C — counterexample search

Simultaneously ask another chat:

> Assume the conjecture is false. Search systematically for the smallest, most degenerate, most asymmetric, or most singular possible counterexamples. Do not use the proof attempt as evidence that no counterexample exists.

Test:

- smallest dimensions;
- smallest cardinalities;
- rank-one cases;
- reducible objects;
- nonreduced objects;
- singular examples;
- boundary parameter values;
- finite fields;
- positive characteristic;
- noncompact examples;
- disconnected examples;
- nonseparable examples;
- pathological topological spaces;
- extremal combinatorial configurations.

The exact list depends on the field.

The important principle is:

> **Attack the universal quantifiers first.**

If the claim says

$$
\forall X\in\mathcal C,\quad P(X),
$$

search for the cheapest possible $X$ for which $P(X)$ could fail.

---

# 8. Convert counterexample search into computation

For finitely parameterized cases, computational experiments are especially valuable.

Possible applications include:

- enumerate small graphs;
- enumerate finite groups;
- search integer solutions;
- test inequalities;
- perform symbolic manipulation;
- compute matrices and ranks;
- investigate recurrence relations;
- search polynomial systems;
- generate random instances;
- optimize candidate extremizers;
- visualize parameter spaces;
- test conjectured monotonicity.

But computational evidence must be classified correctly.

If a program checks all cases up to $n=20$, the conclusion is:

> “The conjecture has been verified computationally for $n\le 20$.”

It is **not**:

> “The conjecture is probably proved.”

Likewise, floating-point verification is not automatically an exact proof.

Whenever numerical computation matters, record:

```text
software version
code
input parameters
random seeds
precision
tolerances
algorithm
output
checksums if appropriate
```

For an exact theorem, prefer exact arithmetic, certified interval arithmetic, symbolic computation, proof-producing software, or a separate mathematical argument whenever feasible.

---

# 9. Use Codex for reproducible mathematical software

When the investigation requires substantial code, move the computational component into **Codex**.

A suitable repository might be:

```text
conjecture-x/
│
├── README.md
├── environment/
│   └── requirements.txt
│
├── src/
│   ├── enumerate.py
│   ├── invariants.py
│   └── search.py
│
├── tests/
│   ├── test_invariants.py
│   └── test_small_cases.py
│
├── data/
│   ├── raw/
│   └── verified/
│
├── notebooks/
│
├── proofs/
│
├── references/
│
└── reports/
```

Ask Codex not merely to generate code but to make experiments reproducible:

> Implement the finite search described in experiment E7. Add tests for every invariant. Use exact arithmetic wherever possible. Make the enumeration deterministic. Record sufficient output that another researcher can independently reproduce the computation.

For computational mathematics, a result becomes substantially more valuable when another researcher can clone the repository, run a command, and obtain the same certificate.

---

# 10. Search aggressively for reductions

A conjecture often does not require a completely new proof.

It may follow from a stronger theorem after translating the terminology.

Create a dedicated **Reduction Specialist** chat.

Ask it to search for statements of the form

$$
A\Longrightarrow B\Longrightarrow C,
$$

where $C$ is the target conjecture.

The task is not simply to find mathematically related theorems.

The task is to establish an explicit implication.

Require a reduction certificate:

```text
Target conjecture C:

Known theorem T:

Hypothesis T1:
Why T1 holds:

Hypothesis T2:
Why T2 holds:

...

Conclusion of T:
Exact translation into C:

Additional lemmas needed:
```

There are three important outcomes.

### Exact reduction

The conjecture follows immediately once terminology is translated.

### Conditional reduction

The conjecture follows if one remaining lemma $L$ is established.

This is already useful because the research problem has become:

$$
\boxed{\text{Prove }L}
$$

rather than the original larger statement.

### Near reduction

A known theorem would prove the conjecture except for hypothesis $H$.

Then ask:

> Is $H$ genuinely necessary, or can it be weakened in the present setting?

This question frequently generates a meaningful research direction.

---

# 11. Establish meaningful special cases

If the full conjecture remains inaccessible, do not stop at “unsolved.”

Construct the largest tractable parameter region.

Typical restrictions include:

$$
n\le N,
$$

$$
\dim X\le d,
$$

smooth $X$,

irreducible $X$,

characteristic $0$,

abelian objects,

rank $\le r$,

generic configurations,

sufficiently large $n$,

symmetric cases,

or objects possessing an additional invariant.

Create a **Special Cases** chat and ask:

> Construct a lattice of progressively weaker hypotheses under which the conjecture might become provable. Prioritize special cases that reveal the mechanism of the general problem rather than trivial cases.

For example:

$$
C_{\mathrm{general}}
$$

may contain

$$
C_{\mathrm{smooth}}
\supset
C_{\mathrm{smooth,\ char}\,0}
\supset
C_{\mathrm{dimension}\,2}
\supset
C_{\mathrm{dimension}\,1}.
$$

For each special case, record why it matters.

A strong special case should preferably do at least one of the following:

- introduce a new technique;
- identify the correct invariant;
- establish the conjecture in a natural major subclass;
- expose where the general case becomes harder;
- reduce the unsolved part to a sharply defined singular or exceptional locus.

---

# 12. Treat failed proofs as data

A failed proof can be mathematically informative.

Suppose a proof strategy reaches

$$
A\Longrightarrow B\Longrightarrow D
$$

but requires

$$
D\Longrightarrow E,
$$

and that implication cannot be justified.

Do not simply discard the attempt.

Create an **Obstruction Analysis** entry:

```text
Strategy:
Point of failure:
Required statement:
Is the required statement true?
If false, smallest counterexample:
If unknown, known related results:
Extra hypothesis under which it becomes true:
Consequence for the original conjecture:
```

There are several kinds of obstruction.

## Logical obstruction

The proposed lemma is false.

## Structural obstruction

The method loses an invariant needed later.

## Quantitative obstruction

The estimate is too weak.

For example, the proof needs

$$
f(n)=O(n),
$$

but the method provides only

$$
f(n)=O(n\log n).
$$

## Geometric obstruction

A construction fails at a singular or boundary locus.

## Functorial obstruction

A property is not preserved under the required operation.

## Compactness obstruction

A limiting sequence exists but the limiting object leaves the relevant category.

## Effectivity obstruction

An existence theorem gives no uniform or computable bound required by the conjecture.

A precise statement such as

> “The natural induction fails because invariant $I$ can increase under the reduction operation”

is much more valuable than

> “The induction did not work.”

---

# 13. Institute an adversarial referee stage

No proposed solution should proceed directly from discovery to final manuscript.

Create a fresh chat whose sole task is to attack the argument.

Give it the theorem statement and the candidate proof, but explicitly instruct it not to repair the proof initially.

Use a prompt such as:

> Act as a skeptical referee for a top mathematics journal. Audit this argument line by line. Check every quantifier, implication, theorem application, construction, existence claim, uniqueness claim, limiting argument, interchange of operations, and case distinction. Identify hidden assumptions, circular reasoning, ambiguous notation, missing hypotheses, and places where the argument establishes less than the claimed result. Do not infer missing arguments charitably.

Require an audit table:

| Step | Claim | Dependency | Valid? | Issue | Severity |
|---|---|---|---|---|---|

Use severity classes:

- **fatal** — destroys the claimed theorem;
- **substantive** — major missing argument;
- **minor** — repairable local gap;
- **expository** — mathematically valid but insufficiently explicit.

Only after this audit should another conversation repair the proof.

---

# 14. Do not ask the discoverer to be the only verifier

Using another chat does not create a mathematically independent human referee, because the conversations may still involve related model technology.

Nevertheless, role separation is useful.

A stronger verification protocol is:

```text
Attempt A
    ↓
Adversarial audit A

Attempt B from scratch
    ↓
Compare A and B

Source verification
    ↓
Computational verification where relevant

Fresh proof reconstruction
    ↓
Final adversarial audit

Human / formal / external verification
```

Particularly important claims should be derived twice using substantially different approaches where possible.

If two arguments depend on the same hidden false lemma, agreement between them proves nothing.

---

# 15. Force theorem applications into explicit form

Whenever the proof says

> “By theorem $T$...”

expand it into the following logical structure:

$$
H_1\land\cdots\land H_k\Longrightarrow Q.
$$

Then show

$$
H_1,\ldots,H_k
$$

one at a time.

For example:

> Theorem $T$ applies because:
>
> 1. $X$ is Noetherian by ...
> 2. $f$ is proper by ...
> 3. $\mathcal F$ is coherent by ...
> 4. the base satisfies ...
>
> Therefore the theorem yields exactly ...

This protocol is especially important in advanced areas where theorems differ by subtle hypotheses.

---

# 16. Maintain a claim-evidence ledger

Every important claim should have an evidence type.

Use the following classification.

| Code | Evidence |
|---|---|
| D | proved directly |
| T | consequence of cited theorem |
| C | exact computation |
| N | numerical evidence only |
| E | empirical examples |
| H | heuristic |
| ? | unresolved |

For example:

```text
C17: Every object in class A has property P.
Status: T

Source:
Theorem 4.7 of ...

Hypotheses:
H1 verified in Lemma L8.
H2 verified in Proposition P3.
H3 follows from definition.

Dependency:
L8, P3
```

This makes it difficult for heuristic evidence to migrate silently into the proof.

---

# 17. Require reproducibility for computational claims

If computation enters an argument, separate three levels.

## Level 1 — exploratory computation

Used to discover patterns.

No proof status.

## Level 2 — exhaustive computation

All members of a finite class have been checked.

Potentially proof-relevant if the enumeration and implementation are correct.

## Level 3 — certified computation

The computation produces an independently checkable certificate or uses a formally justified algorithm with auditable output.

Aim for Level 3 when computation forms an essential part of the theorem.

The research report should explain exactly which level applies.

---

# 18. Use formal proof systems when warranted

For particularly delicate arguments, consider translating critical lemmas or the complete theorem into a proof assistant such as Lean, Coq, Isabelle, or another appropriate formal system.

However:

> **AI-generated formalization is not itself certification.**

The relevant guarantee comes from successful checking by the proof assistant's trusted kernel.

A useful strategy is not necessarily to formalize the entire paper immediately.

Formalize the most dangerous components first:

- long finite case analyses;
- complicated algebraic identities;
- induction hypotheses;
- subtle coercions;
- combinatorial enumeration;
- foundational lemmas on which many later statements depend.

---

# 19. Conduct a final proof reconstruction from scratch

Once all apparent gaps have been repaired, do **not** merely edit the accumulated exploratory proof.

Create a new conversation and supply:

- the exact theorem;
- definitions;
- verified lemmas;
- permitted external theorems;
- resolved referee objections.

Then ask:

> Reconstruct the complete proof from the verified dependency graph. Do not inherit wording or implicit steps from earlier proof attempts. Include every nontrivial inference required to make the argument independently checkable.

This serves as a form of mathematical “clean build.”

The final proof should depend only on verified components, not on the historical path by which those components were discovered.

---

# 20. Final referee audit

Give the reconstructed proof to another fresh adversarial review.

Ask the reviewer to reconstruct its logical dependency tree.

In particular, require checks for:

- quantifier changes;
- unproved existence;
- unproved uniqueness;
- hidden choice arguments;
- unjustified limits;
- invalid exchange of limits/integrals/sums;
- misuse of compactness;
- dimension assumptions;
- characteristic assumptions;
- connectedness or irreducibility assumptions;
- generic-versus-universal statements;
- incorrect use of induction;
- circular dependency among lemmas;
- undefined notation;
- improper strengthening of a cited result;
- proof of only a weaker statement.

The standard should be:

> Could a skeptical expert reconstruct every logical step without guessing what the author intended?

---

# 21. Producing the research report

Use the verified material—not the raw brainstorming chats—to produce the final report.

A strong report should have the following structure.

## 21.1 Abstract

State exactly what was established.

Possible outcomes include:

> We prove Conjecture C.

or

> We disprove Conjecture C by constructing ...

or

> We reduce Conjecture C to Lemma L.

or

> We prove Conjecture C under hypotheses H1–H3.

or

> We identify obstruction O preventing the standard strategy S from extending beyond class A.

Never make the abstract stronger than the verified result.

---

## 21.2 Problem statement

State:

- definitions;
- notation;
- hypotheses;
- exact quantifiers;
- historical context;
- why the problem is nontrivial.

---

## 21.3 Known results

For every result used:

- give a precise statement;
- give the source;
- distinguish published facts from conjectural claims;
- explain its relationship to the present problem.

---

## 21.4 Main result

State the strongest theorem actually established.

---

## 21.5 Proof architecture

Present the dependency graph before presenting technical details.

For example:

$$
\text{Lemma 2.1}
+
\text{Lemma 2.4}
\Longrightarrow
\text{Proposition 3.2}
$$

and

$$
\text{Proposition 3.2}
+
\text{Theorem A}
\Longrightarrow
\text{Main Theorem}.
$$

---

## 21.6 Proof

Give the complete verified argument.

---

## 21.7 Computational component

If applicable, report:

- algorithms;
- software;
- repository;
- versions;
- parameters;
- exact-versus-numerical status;
- reproducibility instructions.

---

## 21.8 Failed strategies and obstruction

For research-level work this section may be extremely useful.

Document:

- natural strategies attempted;
- exact point where each fails;
- whether the failure is intrinsic;
- additional hypotheses that repair it.

This information can prevent future researchers from repeating the same dead end.

---

## 21.9 Remaining open problems

State what remains unresolved.

Prefer precise questions such as

$$
\boxed{\text{Does Lemma 4.3 remain true without normality?}}
$$

rather than

> “The general case remains interesting.”

---

# 22. Recommended project instructions

Place instructions resembling the following in the Project.

```text
This project concerns research on Conjecture C.

Mathematical correctness has priority over producing an answer.

Rules:

1. Never claim a conjecture is proved unless every nontrivial step has been justified.
2. Distinguish proved statements, cited theorems, computations, experimental evidence, heuristics, and conjectures.
3. Never silently strengthen or weaken hypotheses.
4. Verify the hypotheses of every external theorem before applying it.
5. Give primary sources whenever feasible.
6. Explicitly identify uncertainty.
7. Search for counterexamples in parallel with proof attempts.
8. Treat failed proof attempts as research data and identify the exact obstruction.
9. Preserve counterexamples and rejected lemmas in the research record.
10. Do not repair a gap silently during referee review; report it first.
11. For computational results, preserve code, versions, inputs, outputs, and reproducibility information.
12. The final report must be independently checkable without access to private AI reasoning.
```

The final sentence is particularly important.

A mathematical paper must contain the argument itself.

No reader should need access to an AI model's internal reasoning process in order to verify the theorem.

---

# 23. Recommended prompts for the main research stages

## A. Formalize the conjecture

```text
Formalize the following conjecture as a precise mathematical proposition.
Make all quantifiers, dependencies, domains, conventions, and exceptional
cases explicit. Identify any ambiguity or missing hypothesis. Do not try
to prove it yet.
```

## B. Find known results

```text
Conduct a literature investigation of this conjecture. Determine whether
it is known, equivalent to a known problem, implied by a stronger theorem,
or contradicted by a known example. Prefer primary sources. For every
relevant theorem, reproduce its hypotheses precisely and compare them
one by one with the present conjecture.
```

## C. Generate proof strategies

```text
Generate several genuinely distinct proof strategies. For each strategy,
identify the decisive intermediate lemma, explain why it might hold,
identify known machinery that could prove it, and state the most likely
failure mode. Do not present any strategy as a proof unless every step is
established.
```

## D. Hunt counterexamples

```text
Assume the conjecture is false. Search systematically for counterexamples,
starting with the smallest and most degenerate admissible objects. Examine
boundary cases, singular objects, reducible objects, low dimensions,
small cardinalities, and exceptional characteristics where applicable.
For every candidate, verify all hypotheses before testing the conclusion.
```

## E. Search for reductions

```text
Try to reduce the conjecture to known results. Give an explicit implication
chain. For every external theorem, verify every hypothesis. If the reduction
fails by exactly one missing condition, isolate that condition as a separate
lemma or obstruction.
```

## F. Find special cases

```text
Identify mathematically meaningful subclasses on which the conjecture
may be provable. Organize them from strongest to weakest restrictions.
Prioritize cases that expose mechanisms relevant to the full conjecture.
For each case, explain exactly which difficulty of the general problem
disappears.
```

## G. Analyze a failed proof

```text
Do not repair this proof yet. Locate the first logically unjustified step.
State exactly what proposition would be needed there. Determine whether
that proposition is true, false, or unknown. If false, search for the
smallest counterexample. If true under extra hypotheses, identify the
weakest plausible additional hypothesis.
```

## H. Referee audit

```text
Act as a skeptical referee for a top mathematics journal. Reconstruct the
logical dependency of this proof and audit every inference. Identify hidden
assumptions, unjustified implications, circularity, missing cases, incorrect
theorem applications, quantifier errors, ambiguous notation, and unproved
existence or uniqueness claims. Classify every defect as fatal, substantive,
minor, or expository. Do not repair defects until after reporting them.
```

## I. Repair after audit

```text
Using the referee report, repair every identified defect. If a defect cannot
be repaired under the stated hypotheses, say so and weaken or reject the
claimed theorem rather than forcing a proof. Then reconstruct the argument
from the beginning in a logically complete form.
```

## J. Final independent reconstruction

```text
Using only the verified lemmas and explicitly permitted external theorems
listed below, reconstruct a complete proof from scratch. Do not rely on
the wording or implicit reasoning of previous attempts. Verify the
hypotheses of every cited theorem at its point of use.
```

---

# 24. A coordinated attack protocol

The entire workflow can be summarized as follows:

```text
                    ┌─────────────────────┐
                    │ Exact conjecture C  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Literature        Proof search    Counterexample
          search              branches        search
              │                │                │
              ▼                ▼                ▼
       Known results       Candidate        Examples /
       and reductions       lemmas         computations
              │                │                │
              └────────┬───────┴───────┬────────┘
                       │               │
                       ▼               ▼
                 Special cases     Obstructions
                       │               │
                       └───────┬───────┘
                               ▼
                         Claim ledger
                               │
                               ▼
                       Adversarial audit
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
                 Repair              Reject/modify
                    │
                    ▼
             Fresh reconstruction
                    │
                    ▼
              Final referee audit
                    │
                    ▼
            Independent checking
                    │
                    ▼
               Research report
```

---

# 25. What counts as success?

The workflow should not define success exclusively as proving the original statement.

There are at least six legitimate endpoints.

## Outcome I — Proof

You obtain

$$
H\Longrightarrow C
$$

with a complete independently checkable derivation.

## Outcome II — Counterexample

You construct an object $X$ satisfying every hypothesis but violating the conclusion:

$$
H(X)\land\neg C(X).
$$

## Outcome III — Reduction

You prove

$$
T\Longrightarrow C
$$

where $T$ is known, or

$$
L\Longrightarrow C
$$

where $L$ is a sharply formulated remaining open lemma.

## Outcome IV — Special case

You establish

$$
H+H'\Longrightarrow C
$$

for a mathematically meaningful additional hypothesis $H'$.

## Outcome V — Obstruction

You prove that a natural strategy cannot work because of a precise phenomenon $O$.

## Outcome VI — Negative research result

You establish that an apparently natural intermediate claim is false and characterize its failure.

All six can constitute real mathematical progress.

---

# 26. The most important discipline: preserve epistemic status

Throughout the project, statements should retain their status.

Do not permit

```text
experimental pattern
       ↓
plausible lemma
       ↓
“obvious fact”
       ↓
used inside final proof
```

Instead require:

```text
experimental pattern
       ↓
conjectured lemma
       ↓
independent proof / theorem / certified computation
       ↓
verified lemma
       ↓
permitted inside final proof
```

This single discipline prevents many AI-assisted research failures.

---

# 27. Minimal viable workflow

For a smaller problem, the full infrastructure can be reduced to seven steps:

1. **Create a Project** containing the exact problem and references.
2. **Run Deep Research** to identify known theorems and nearby counterexamples.
3. **Open separate proof and counterexample chats.**
4. **Use computation/Codex** whenever finite or symbolic experiments could test the claim.
5. **Extract special cases and exact obstructions** from failed attempts.
6. **Submit every candidate argument to a fresh adversarial referee chat.**
7. **Reconstruct the final argument from verified components and make all computations and references independently reproducible.**

That is the minimum process recommended for serious AI-assisted mathematics.

---

# 28. The stronger research-laboratory model

For a genuinely difficult conjecture, use the following division of labor:

| Research function | Primary OpenAI capability |
|---|---|
| Problem formalization | Chat |
| Long-term context | Projects |
| Literature mapping | Deep Research |
| Precise source verification | Search |
| Paper/book analysis | File uploads |
| Connected document retrieval | Apps |
| Brainstorming proofs | reasoning-oriented Chat |
| Counterexample generation | reasoning-oriented Chat |
| Numerical/symbolic experiments | Data Analysis |
| Reproducible research software | Codex |
| Repository-based verification | Codex + GitHub |
| Adversarial proof review | fresh Chat |
| Final research artifact | Work |
| Human-independent machine checking | external proof assistant / certificate checker |

The important word is **coordinated**.

The value does not come from any single model response. It comes from making different tools perform different epistemic functions while maintaining a strict boundary between:

$$
\boxed{\text{idea}}
,\qquad
\boxed{\text{evidence}}
,\qquad
\boxed{\text{proof}}.
$$

A conjecture should be declared solved only when the last box has been reached.
