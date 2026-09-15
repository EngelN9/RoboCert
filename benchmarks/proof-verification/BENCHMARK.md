# RoboCert Mathematical Proof Verification Benchmark

## Status

**Document:** `BENCHMARK.md`  
**Benchmark name:** RoboCert Mathematical Proof Verification Benchmark  
**Short name:** `RC-MPVB`  
**Version:** `0.2.0` (see §47 Changelog)  
**Purpose:** Reproducible evaluation of AI systems on research-level mathematical proof generation, skeptical peer review, defect repair, and final proof verification.

## Conformance language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt): **MUST**/**MUST NOT** denote absolute requirements for a conforming benchmark run; **SHOULD**/**SHOULD NOT** denote strong recommendations that MAY be departed from for stated, documented reasons; **MAY** denotes a genuinely optional provision. A run that violates a MUST requirement is not a valid RC-MPVB run and MUST NOT be reported as one without disclosing the deviation.

## Table of contents

1. [Purpose](#1-purpose)
2. [Benchmark philosophy](#2-benchmark-philosophy)
3. [Unit of evaluation](#3-unit-of-evaluation)
4. [Benchmark tracks](#4-benchmark-tracks)
5. [Assisted versus blind audit](#5-assisted-versus-blind-audit)
6. [Dataset design](#6-dataset-design)
7. [Contamination and leakage control](#7-contamination-and-leakage-control)
8. [Model and run controls](#8-model-and-run-controls)
9. [Defect severity taxonomy](#9-defect-severity-taxonomy)
10. [Gold defect inventory](#10-gold-defect-inventory)
11. [Matching reported defects to gold defects](#11-matching-reported-defects-to-gold-defects)
12. [Generation scoring](#12-generation-scoring)
13. [Audit scoring](#13-audit-scoring)
14. [Repair scoring](#14-repair-scoring)
15. [Final-proof scoring](#15-final-proof-scoring)
16. [Overall benchmark score](#16-overall-benchmark-score)
17. [First-pass reliability](#17-first-pass-reliability)
18. [Self-audit versus independent audit](#18-self-audit-versus-independent-audit)
19. [Tool-assisted verification](#19-tool-assisted-verification)
20. [Formal verification subset](#20-formal-verification-subset)
21. [Repeated trials](#21-repeated-trials)
22. [Statistical reporting](#22-statistical-reporting)
23. [Fair cross-model comparison](#23-fair-cross-model-comparison)
24. [Prompt freezing](#24-prompt-freezing)
25. [Recommended generation prompt](#25-recommended-generation-prompt)
26. [Recommended blind-audit prompt](#26-recommended-blind-audit-prompt)
27. [Recommended repair prompt](#27-recommended-repair-prompt)
28. [Recommended final-adjudication prompt](#28-recommended-final-adjudication-prompt)
29. [Benchmark artifact retention](#29-benchmark-artifact-retention)
30. [Recommended repository layout](#30-recommended-repository-layout)
31. [Run identifier](#31-run-identifier)
32. [Machine-readable result schema](#32-machine-readable-result-schema)
33. [RC-002 benchmark interpretation](#33-rc-002-benchmark-interpretation)
34. [Benchmark validity threats](#34-benchmark-validity-threats)
35. [Claims permitted from benchmark results](#35-claims-permitted-from-benchmark-results)
36. [Benchmark versioning](#36-benchmark-versioning)
37. [Benchmark governance](#37-benchmark-governance)
38. [Minimum acceptance standard for RoboCert proof claims](#38-minimum-acceptance-standard-for-robocert-proof-claims)
39. [Recommended benchmark summary table](#39-recommended-benchmark-summary-table)
40. [Core principle](#40-core-principle)
41. [Score comparability across tracks](#41-score-comparability-across-tracks)
42. [Calibration items and false-positive control](#42-calibration-items-and-false-positive-control)
43. [Human-rater reliability](#43-human-rater-reliability)
44. [Multi-judge disagreement resolution](#44-multi-judge-disagreement-resolution)
45. [Glossary](#45-glossary)
46. [License and citation](#46-license-and-citation)
47. [Changelog](#47-changelog)

---

# 1. Purpose

The RoboCert Mathematical Proof Verification Benchmark (`RC-MPVB`) evaluates whether an AI system can reliably perform mathematically rigorous reasoning at a standard suitable for scrutiny by a professional research mathematician.

The benchmark is designed for proof tasks arising in RoboCert and related certified-robotics mathematics, including but not limited to:

- real algebraic geometry;
- semialgebraic sets;
- polynomial systems;
- rational parameterizations;
- quantifier elimination;
- exact geometric encodings;
- interval and certified numerics;
- singularity analysis;
- computational geometry;
- sum-of-squares methods;
- semidefinite relaxations;
- exact and approximate proof obligations.

The benchmark is **not** intended to measure whether an AI can merely produce plausible mathematical prose. It measures whether the AI can:

1. produce a valid proof;
2. detect mathematical defects in a candidate proof;
3. distinguish real defects from false alarms;
4. repair identified defects without introducing new errors;
5. maintain logical consistency across revisions;
6. respect the exact statement, hypotheses, coefficient field, quantifiers, and domain;
7. state when a theorem is false or under-specified rather than forcing a proof.

---

# 2. Benchmark philosophy

A proof benchmark should measure more than final-answer plausibility.

For each benchmark item, the primary capabilities are separated into four stages:

$$
\text{Generation}
\longrightarrow
\text{Blind Audit}
\longrightarrow
\text{Repair}
\longrightarrow
\text{Independent Adjudication}.
$$

These stages are scored separately.

A system that produces a correct proof on the first attempt should receive more credit for first-pass reliability than a system that reaches the same proof only after receiving detailed criticism.

Likewise, a system that identifies many alleged defects but produces many false positives should not receive the same audit score as a precise referee.

---

# 3. Unit of evaluation

A benchmark item is a versioned mathematical task $T_i$.

Each item SHOULD contain:

```text
item_id
benchmark_version
domain
statement
definitions
explicit_hypotheses
allowed_references
forbidden_assumptions
coefficient_domain
quantifier_structure
expected_output_type
known_failure_modes
gold_defect_inventory
reference_resolution
difficulty
provenance
contamination_notes
```

Field definitions:

- `expected_output_type` — one of `proof`, `refutation`, `false_or_underspecified`; what a correct Track G response is allowed to look like.
- `known_failure_modes` — the item author's enumeration of the specific ways a candidate proof is expected to go wrong (drawn from the categories in §6 and §9); this field feeds the gold defect inventory (§10) and MUST be withheld from Blind Audit per §7.
- `gold_defect_inventory` — pointer to the hidden record defined in §10; not the record itself.
- `reference_resolution` — the exact edition, section, and theorem/lemma numbers of any external source the item's permitted references resolve to, so that Track F's source-verification step (§20) can check citations without reconstructing them from memory.
- `difficulty` — an integer 1–5 fixed at authoring time and frozen thereafter, calibrated against the categories in §6 (e.g. 1 = routine application of a cited result, 5 = requires an auxiliary construction not suggested by the statement); used to stratify reporting in §22 so aggregate scores are not dominated by whichever difficulty band is best represented in the dataset.
- `provenance` — where the item came from: originally authored for RC-MPVB, adapted from a published result (with citation), or adapted from RoboCert's own artifacts; feeds §7's contamination tracking.
- `contamination_notes` — free text recording anything relevant to §7 (e.g. "statement previously posted publicly on \<date\>").

The evaluator MUST distinguish between:

- facts given in the problem;
- facts that must be proved;
- implementation facts;
- external theorems;
- computational evidence;
- informal motivation.

Implementation-specific facts MUST NOT be treated as mathematical consequences unless they are explicitly included as hypotheses or separately verified.

---

# 4. Benchmark tracks

RC-MPVB defines four mandatory tracks and two optional tracks.

## 4.1 Track G — Proof Generation

### Input

The model receives:

- the theorem or proposition;
- definitions;
- explicit hypotheses;
- permitted prior results;
- any fixed notation required by the task.

The model MUST NOT receive:

- a reference proof;
- a gold defect inventory;
- referee comments;
- a list of known weak points;
- a repaired proof;
- hidden benchmark annotations.

### Task

Produce a complete, rigorous, logically self-contained proof.

The generation prompt SHOULD require the model not to omit nontrivial steps, silently add assumptions, or invoke a theorem without verifying its hypotheses. If the statement is false or under-specified, the model must identify the defect rather than forcing a proof.

### Output

A single proof or a justified rejection of the statement as false or insufficiently specified.

## 4.2 Track A — Blind Referee Audit

### Input

A fresh evaluator receives:

- the original task;
- a candidate proof.

The evaluator MUST NOT receive:

- the author model's hidden reasoning;
- known weak points;
- gold defects;
- repair notes;
- previous referee reports.

### Task

Act as a skeptical and strict referee.

The audit MUST inspect:

- every major inference;
- theorem applications;
- definitions;
- hypotheses;
- quantifiers;
- domain restrictions;
- sign conditions;
- case splits;
- existence claims;
- uniqueness claims;
- coefficient fields;
- denominator clearing;
- squaring arguments;
- equivalences;
- boundary cases;
- degeneracies;
- logical dependencies;
- use of implementation facts;
- scope of the final conclusion.

Each reported issue MUST contain:

1. the problematic step;
2. why it is problematic;
3. severity;
4. the required repair.

Severity labels are exactly:

- `fatal`
- `substantive`
- `minor`
- `expository`

## 4.3 Track R — Critique-Conditioned Repair

### Input

A fresh model instance receives:

- the original mathematical task;
- the candidate proof;
- a validated referee report.

A repair model MAY be the same model family as the generator, but the benchmark record MUST disclose this.

### Task

Repair every validated defect while preserving all valid portions of the argument.

The revised proof MUST:

- explicitly incorporate required missing hypotheses;
- remove invalid implications;
- eliminate circular reasoning;
- repair invalid algebraic transformations;
- cover missing cases;
- correct overstatements;
- preserve the exact theorem being proved;
- avoid introducing new defects.

The repair stage MUST NOT silently change the theorem unless the referee has established that the original theorem is false or under-specified.

If a statement must be corrected, the repair MUST distinguish:

1. the original statement;
2. the defect;
3. the corrected statement;
4. the proof of the corrected statement.

## 4.4 Track F — Final Independent Verification

### Input

The final verifier receives:

- the original task;
- the final repaired proof.

The verifier MUST NOT receive the generator's or repair model's hidden reasoning.

### Task

Determine whether the final proof is mathematically valid.

The verifier SHOULD use:

- independent human mathematical review whenever possible;
- multiple independent AI judges when human review is unavailable;
- symbolic or exact computational checks where appropriate;
- theorem provers or formalization tools where feasible.

The final verifier MUST NOT infer correctness from stylistic polish, length, confidence, agreement among non-independent agents, or numerical testing alone.

When multiple independent AI judges are used, their individual verdicts and defect reports MUST be recorded before any aggregation, and disagreement MUST be resolved according to §44 rather than by simple majority vote.

## 4.5 Optional Track D — Defect Localization

This track measures whether a model can detect deliberately inserted mathematical defects.

Candidate proofs MAY contain controlled errors such as:

- sign errors;
- invalid denominator clearing;
- quantifier reversal;
- missing cases;
- false biconditionals;
- unjustified squaring;
- hidden positivity assumptions;
- invalid theorem use;
- coefficient-domain mismatch;
- endpoint failures;
- degenerate geometry;
- circularity.

The benchmark MUST maintain a hidden gold defect inventory.

## 4.6 Optional Track X — Cross-Model Verification

A typical symmetric protocol is:

$$
A_G \rightarrow B_A \rightarrow A_R \rightarrow J_F
$$

and

$$
B_G \rightarrow A_A \rightarrow B_R \rightarrow J_F,
$$

where $J_F$ is an independent final adjudicator.

Both directions MUST be run to avoid directional bias.

---

# 5. Assisted versus blind audit

A benchmark item MAY contain a section such as `Where this argument is weakest` or `Known risks`.

Such information MUST NOT be provided in the Blind Audit track.

RC-MPVB therefore distinguishes:

## Blind Audit

The evaluator receives no known weakness labels. This measures independent defect discovery.

## Assisted Audit

The evaluator receives explicit candidate weak points. This measures depth of verification of already identified risks.

Scores from these two conditions MUST NOT be combined without labeling.

Assisted Audit is scored with the same formula as Blind Audit (§13), but every reported result MUST carry the `assisted_audit` label from §18 and MUST NOT be presented as evidence of unaided defect-detection ability. Because a model that is handed the weak points can raise WeightedRecall simply by restating them, Assisted Audit results are informative mainly for Precision and for the depth of the required-repair statements (§4.2), not for headline capability claims.

---

# 6. Dataset design

A benchmark is not defined by a single proof.

The dataset SHOULD contain diverse proof obligations and failure modes, including at minimum:

1. valid theorem with valid proof;
2. valid theorem with incomplete proof;
3. false theorem;
4. theorem missing a necessary hypothesis;
5. hidden denominator-sign dependency;
6. invalid squaring;
7. invalid equivalence after polynomialization;
8. spurious roots after algebraic transformation;
9. quantifier reversal;
10. incorrect theorem hypotheses;
11. boundary-case omission;
12. incorrect open/closed inequality;
13. overlapping case seams;
14. uncovered case;
15. degenerate geometric object;
16. coefficient-field mismatch;
17. implementation claim mistaken for a mathematical theorem;
18. circular argument;
19. proof establishing only one direction of an iff;
20. existence without proof;
21. uniqueness without proof;
22. misuse of continuity;
23. local argument asserted globally;
24. numerical evidence substituted for proof;
25. hidden regularity assumption;
26. undefined or inconsistent notation;
27. valid nontrivial proof requiring no repair.

The benchmark SHOULD balance positive and negative examples so that always accepting or always rejecting is not a viable strategy.

---

# 7. Contamination and leakage control

Each item SHOULD record:

```text
provenance
date_created
date_frozen
public_or_private
known_public_locations
reference_proof_publication_status
suspected_training_exposure
```

For high-integrity evaluation:

- some test items SHOULD remain private;
- reference proofs SHOULD remain hidden;
- gold defect inventories MUST remain hidden;
- known weak-point sections MUST be removed from blind audit inputs;
- model outputs from previous runs SHOULD NOT be included in later inputs unless required by the protocol;
- evaluation prompts SHOULD be frozen before scoring begins.

If public benchmark items are used, results MUST be labeled as potentially contamination-sensitive.

---

# 8. Model and run controls

Every benchmark run MUST record the exact evaluation conditions.

```yaml
model_provider:
model_name:
model_version:
date:
benchmark_version:
track:
system_prompt_hash:
user_prompt_hash:
temperature:
top_p:
seed_if_supported:
max_output_tokens:
reasoning_mode:
tool_access:
internet_access:
file_access:
code_execution:
formal_tools:
number_of_attempts:
token_budget:
cost_budget:
```

If a parameter is unavailable, record `not exposed by provider`.

---

# 9. Defect severity taxonomy

## Fatal

A `fatal` defect invalidates the main theorem or makes the proof incapable of establishing the stated conclusion without materially changing the result.

Examples include a false theorem, a reversed central implication, a missing essential case, a possibly zero denominator used as nonzero, a quantifier reversal changing the theorem, or circular dependence on the main result.

## Substantive

A `substantive` defect is mathematically important but repairable without replacing the main strategy.

Examples include a missing necessary hypothesis, a conditional result presented as unconditional, an important unproved lemma, a coefficient-field mismatch, an ambiguous Boolean case structure, or an implementation property claimed without verification.

## Minor

A `minor` defect is a local mathematical omission whose repair is straightforward and does not alter the architecture of the proof.

Examples include an omitted monotonicity argument or an unstated nonnegativity fact already guaranteed by the hypotheses.

## Expository

An `expository` defect does not invalidate the mathematics but reduces precision or readability.

Examples include ambiguous notation, misleading terminology, or imprecise degree descriptions.

---

# 10. Gold defect inventory

Each audit item SHOULD have a hidden gold record.

Example:

```yaml
item_id: RC-002
gold_defects:
  - id: RC002-D1
    severity: substantive
    location: theorem assumptions
    category: omitted_hypothesis
    description: obstacle radius nonnegativity required for distance squaring
    repair: require r >= 0 or R >= 0

  - id: RC002-D2
    severity: substantive
    location: segment_2
    category: conditional_dependency
    description: Q2 positivity valid only on FK locus
    repair: prove FK => Q2 = D1^2 L2^2 > 0
```

The gold record MUST NOT be exposed to the blind auditor.

---

# 11. Matching reported defects to gold defects

A reported issue counts as a true positive only if it identifies the same mathematical defect with sufficient precision.

Lexical similarity is not required.

A match SHOULD require agreement on:

- mathematical location;
- defect type;
- logical reason;
- consequence.

A vague statement such as `There may be hidden assumptions` receives no credit unless the model identifies the specific hidden assumption and why it matters.

---

# 12. Generation scoring

Let $F_G,S_G,M_G,E_G$ denote the numbers of fatal, substantive, minor, and expository defects.

A recommended raw generation score is

$$
G_{\mathrm{raw}}
=
100
-
40F_G
-
15S_G
-
3M_G
-
E_G.
$$

Set

$$
G=\max(0,G_{\mathrm{raw}}).
$$

A proof with any unresolved fatal defect MUST NOT receive a passing Generation rating regardless of numeric score.

Recommended interpretation:

| Score | Interpretation |
|---|---|
| 95–100 | publication-level or near-publication-level |
| 85–94 | strong, minor repair required |
| 70–84 | mathematically promising but substantive repair required |
| 50–69 | unreliable |
| 0–49 | seriously defective |

Thresholds MUST be frozen before model comparison.

---

# 13. Audit scoring

Let

$$
TP=\text{correctly identified gold defects},
$$

$$
FP=\text{reported defects that are not genuine},
$$

$$
FN=\text{gold defects missed}.
$$

Define

$$
\mathrm{Precision}=\frac{TP}{TP+FP},
\qquad
\mathrm{Recall}=\frac{TP}{TP+FN}.
$$

Define

$$
F_1=
\frac{2\,\mathrm{Precision}\,\mathrm{Recall}}
{\mathrm{Precision}+\mathrm{Recall}}.
$$

The implementation MUST specify conventions for zero denominators.

Recommended severity weights are

$$
w_{\mathrm{fatal}}=8,\qquad
w_{\mathrm{substantive}}=4,\qquad
w_{\mathrm{minor}}=1,\qquad
w_{\mathrm{expository}}=0.25.
$$

Define

$$
\mathrm{WeightedRecall}
=
\frac{
\sum_{\text{detected gold defect }d}w(d)
}{
\sum_{\text{gold defect }d}w(d)
}.
$$

Recommended Audit score:

$$
A
=
100
\left(
0.60\,\mathrm{WeightedRecall}
+
0.25\,\mathrm{Precision}
+
0.15\,F_1
\right).
$$

A model that misses any fatal defect MUST be flagged with:

```text
fatal_miss = true
```

---

# 14. Repair scoring

For each validated defect determine whether it is:

- fully repaired;
- partially repaired;
- unrepaired;
- replaced by a different defect.

Define

$$
\mathrm{RepairRate}
=
\frac{\text{weighted repaired defects}}
{\text{weighted validated defects}}.
$$

Let

$$
N_{\mathrm{new}}
=
\text{new mathematical defects introduced during repair}.
$$

Define

$$
\mathrm{RegressionPenalty}
=
\min(1,0.10N_{\mathrm{new}}).
$$

Recommended score:

$$
R
=
100\cdot
\mathrm{RepairRate}\cdot
(1-\mathrm{RegressionPenalty}).
$$

A new fatal defect causes automatic failure of the repair stage.

---

# 15. Final-proof scoring

Let $F_F,S_F,M_F,E_F$ denote remaining defects in the final proof.

Recommended score:

$$
F
=
100
-
50F_F
-
20S_F
-
5M_F
-
E_F.
$$

Clamp below at $0$.

A final proof passes only if:

$$
F_F=0
\quad\text{and}\quad
S_F=0.
$$

A strict benchmark MAY additionally require $F\ge95$.

---

# 16. Overall benchmark score

The four primary dimensions MUST be reported separately.

A combined convenience score MAY be:

$$
B
=
0.30G
+
0.25A
+
0.20R
+
0.25F.
$$

A single combined score MUST NOT replace component scores.

A recommended strict pass requires:

```text
Generation: no fatal defect
Audit: no fatal gold defect missed
Repair: no unresolved fatal or substantive defect
Final: no fatal or substantive defect
```

The per-track fatal/substantive/minor weights (§12, §13, §15) differ across tracks by design — see §41 before comparing raw numeric scores across tracks.

---

# 17. First-pass reliability

Report

$$
P_{\mathrm{first}}
=
\frac{\text{items correct without repair}}
{\text{all evaluated items}},
$$

and

$$
P_{\mathrm{final}}
=
\frac{\text{items correct after allowed repair}}
{\text{all evaluated items}}.
$$

These measure different capabilities and MUST NOT be conflated.

---

# 18. Self-audit versus independent audit

The benchmark SHOULD separately report:

```text
self_audit
same_family_audit
cross_model_audit
human_audit
```

A model auditing its own proof is not fully independent.

Preferred independence hierarchy:

$$
\text{human expert}
>
\text{independent model family}
>
\text{fresh instance of same model family}
>
\text{same conversational instance}.
$$

This hierarchy concerns independence, not absolute mathematical capability.

---

# 19. Tool-assisted verification

Tools MAY be used in designated tracks, including:

- symbolic algebra;
- exact rational arithmetic;
- SMT solvers;
- computer algebra systems;
- theorem provers;
- proof assistants;
- interval arithmetic;
- numerical tests used only as supporting evidence.

Tool use MUST be recorded.

Numerical testing MUST NOT be treated as proof of a universal statement unless the theorem itself reduces validity to the tested finite set.

Recommended conditions:

```text
no_tools
standard_tools
formal_verification_tools
```

---

# 20. Formal verification subset

Where feasible, a subset SHOULD be formalized in a proof assistant.

Formal checking does not remove the need to verify that:

- the formal theorem matches the intended theorem;
- hypotheses have not been silently changed;
- definitions correspond to the benchmark;
- imported axioms are disclosed.

---

# 21. Repeated trials

For stochastic systems, each item SHOULD be run multiple times.

Recommended minimum:

$$
n=5
$$

independent runs per model-item-track condition when cost permits.

For high-stakes comparison, $n\ge10$ is preferred.

Report:

- mean;
- median;
- standard deviation;
- minimum;
- maximum;
- number of passes;
- pass rate.

---

# 22. Statistical reporting

Report at minimum:

- mean score;
- item-level pass rate;
- first-pass success rate;
- final success rate;
- fatal-defect miss rate;
- false-positive audit rate.

Benchmark-level comparisons SHOULD include confidence intervals.

Bootstrap confidence intervals are acceptable if the method is specified in advance.

Statistical significance MUST NOT substitute for practical significance.

---

# 23. Fair cross-model comparison

For Model A and Model B to be compared fairly, the benchmark MUST attempt to equalize:

- task statement;
- context;
- prompt;
- number of attempts;
- tool access;
- external information access;
- evaluation stage;
- adjudication procedure.

The benchmark MUST disclose differences in:

- token budget;
- reasoning budget;
- API capability;
- context-window limitations;
- cost;
- tool implementation.

If exact equality is impossible, the mismatch MUST be reported.

---

# 24. Prompt freezing

All benchmark prompts SHOULD be versioned:

```text
prompts/
  generation-v1.md
  blind-audit-v1.md
  repair-v1.md
  adjudication-v1.md
```

Once an evaluation begins, prompts MUST NOT be silently modified.

The *preparation tool* is frozen on the same terms. `scripts/prepare_rc002_run.py` pins
`BENCHMARK_VERSION` and checks it against `VERSION`, so changing how a run is assembled is a
freezing question and not a refactor: RUN001 was prepared at `0.2.0`, and a run prepared under
different semantics is not comparable to it without a disclosed deviation.

As written the tool can only prepare a **two**-source run. It hardcodes the two source proofs,
`_load_or_create_private_map` requires the blind-label set to be exactly `{"P1", "P2"}`, and the
label assignment is a two-way coin flip. A repaired RC-002 package carrying
`research/proofs/rc002-frozen-task-corrigendum-2026-08-24.md` therefore cannot be frozen with it
until that decision is made and the tool follows — see the script's own module docstring.

---

# 25. Recommended generation prompt

```text
Provide a complete, rigorous, and logically self-contained proof of the
mathematical statement at the standard expected of a professional research
mathematician and suitable for scrutiny by a referee at a top mathematics
journal.

Do not omit any nontrivial step, silently add assumptions, or use a theorem
without verifying its hypotheses.

Check all quantifiers, domains, sign conditions, boundary cases, degenerate
cases, coefficient fields, and equivalences.

If the statement is false, incomplete, or under-specified as written, identify
the problem rather than forcing a proof.
```

---

# 26. Recommended blind-audit prompt

```text
Act as a skeptical and strict referee for a top mathematics journal.

Audit the candidate proof for mathematical correctness. Check every inference,
theorem application, quantifier, construction, domain restriction, case split,
and conclusion.

In particular, identify:
- hidden assumptions;
- unjustified implications;
- circular reasoning;
- misuse of definitions or theorems;
- omitted hypotheses;
- missing cases;
- invalid reductions;
- ambiguous notation;
- unproved existence or uniqueness claims;
- places where the argument proves less than the stated theorem.

For every issue found:
1. identify the problematic step;
2. explain precisely why it is problematic;
3. classify it as fatal, substantive, minor, or expository;
4. state what is needed to repair it.

Do not declare the proof correct merely because its overall strategy is
plausible.
```

---

# 27. Recommended repair prompt

```text
Using the original theorem and the validated referee report, repair every
mathematical defect.

Rewrite the proof in a self-contained, logically complete, fully rigorous final
form at the standard expected of a professional research mathematician after
scrutiny by a referee at a top mathematics journal.

Do not silently change the theorem. If the theorem requires additional
hypotheses or correction, explicitly state:
1. the original defect;
2. the corrected statement;
3. why the correction is necessary.

Do not introduce new assumptions beyond those required for correctness.
```

---

# 28. Recommended final-adjudication prompt

```text
Independently verify the final proof.

Do not assume the proof is correct because it has already been revised.

Reconstruct the logical dependency of the proof and verify every major
mathematical step.

Return:
- PASS, only if there is no fatal or substantive mathematical defect;
- FAIL, otherwise.

List every remaining defect with severity and required repair.
```

---

# 29. Benchmark artifact retention

For every run, retain:

```text
task.md
generation_prompt.md
generation_output.md
audit_prompt.md
audit_output.md
validated_audit.md
repair_prompt.md
repair_output.md
final_adjudication.md
metadata.yaml
scores.json
```

Where permitted, retain raw API responses separately.

Hidden chain-of-thought MUST NOT be required for benchmark validity. The benchmark evaluates observable mathematical outputs.

---

# 30. Recommended repository layout

```text
benchmark/
├── BENCHMARK.md
├── VERSION
├── prompts/
│   ├── generation-v1.md
│   ├── blind-audit-v1.md
│   ├── repair-v1.md
│   └── adjudication-v1.md
├── items/
│   ├── public/
│   └── private/
├── gold/
│   └── private/
├── runs/
│   └── <run-id>/
├── schemas/
│   ├── item.schema.json
│   ├── audit.schema.json
│   ├── metadata.schema.json
│   └── scores.schema.json
└── reports/
```

---

# 31. Run identifier

Recommended format:

```text
RCMPVB-YYYYMMDD-MODEL-TRACK-RUNNN
```

Example:

```text
RCMPVB-20260817-GPT56SOL-G-RUN001
```

---

# 32. Machine-readable result schema

```json
{
  "benchmark": "RC-MPVB",
  "benchmark_version": "0.2.0",
  "item_id": "RC-002",
  "model": "",
  "model_version": "",
  "track": "G",
  "run_id": "",
  "generation_score": null,
  "audit_score": null,
  "repair_score": null,
  "final_score": null,
  "fatal_defects": 0,
  "substantive_defects": 0,
  "minor_defects": 0,
  "expository_defects": 0,
  "fatal_miss": false,
  "first_pass_correct": false,
  "final_correct": false
}
```

---

# 33. RC-002 benchmark interpretation

For the planar-2R exact-witness soundness item, evaluation SHOULD separately test:

- denominator positivity;
- half-angle chart scope;
- exact forward-kinematics rationalization;
- singularity determinant derivation;
- validity of squaring;
- segment-1 projection cases;
- segment-1 seam behavior;
- segment-2 dependence on FK;
- positivity of the segment-2 squared-length denominator;
- segment-2 interior cancellation;
- segment-2 seam behavior;
- nonconstancy claims;
- coefficient-domain claims;
- bounded witness-domain claims;
- distinction between mathematical and implementation assertions;
- final iff scope.

If a derivation contains a section identifying these weak points, it MUST be removed in Blind Audit and MAY be retained only in Assisted Audit.

---

# 34. Benchmark validity threats

Every report SHOULD discuss:

## 34.1 Training contamination

The model may have seen public benchmark items.

## 34.2 Prompt leakage

The input may reveal the expected defect.

## 34.3 Judge dependence

The same model family may generate and judge.

## 34.4 Rubric drift

Evaluators may change standards across runs.

## 34.5 Budget inequality

Models may receive different reasoning or token resources.

## 34.6 Tool inequality

One system may have verification tools unavailable to another.

## 34.7 Small dataset effects

A few proof items cannot justify broad claims about mathematical intelligence.

## 34.8 Selection bias

Choosing only tasks on which a model performs well invalidates comparative conclusions.

---

# 35. Claims permitted from benchmark results

A benchmark result MAY support a statement such as:

> Under RC-MPVB version X, prompt version Y, and the stated computational conditions, Model A achieved an 82% first-pass proof success rate and a 94% final post-repair success rate on the evaluated task set.

A benchmark result MUST NOT, by itself, justify statements such as:

> Model A can reliably prove arbitrary research mathematics.

or:

> Model A is mathematically correct in general.

Conclusions MUST remain within the measured task distribution and protocol.

---

# 36. Benchmark versioning

Use semantic versioning:

```text
MAJOR.MINOR.PATCH
```

Increment:

- `MAJOR` when scoring or task semantics change incompatibly;
- `MINOR` when new items or tracks are added compatibly;
- `PATCH` for documentation or non-semantic corrections.

Every published score MUST state the benchmark version.

---

# 37. Benchmark governance

Changes to scoring weights, pass criteria, gold defects, task statements, prompts, or adjudication rules MUST be version controlled.

Changes MUST NOT be made after inspecting model results merely to improve or worsen a model's score.

If a gold answer is found to be wrong, the affected item MUST be:

1. suspended;
2. corrected;
3. re-versioned;
4. re-evaluated.

---

# 38. Minimum acceptance standard for RoboCert proof claims

A RoboCert proof evaluated under RC-MPVB SHOULD NOT be treated as benchmark-verified unless:

1. the Generation proof contains no unresolved fatal defect;
2. Blind Audit has been performed independently;
3. every validated fatal or substantive issue has been repaired;
4. the repaired proof has undergone independent final adjudication;
5. the final proof contains no fatal or substantive defect;
6. implementation-specific claims are separately checked against the implementation or formal specification;
7. computational tests are identified as supporting evidence rather than substitutes for proof;
8. the complete transcript and benchmark metadata are retained.

For publication or safety-critical certification, human expert review remains strongly recommended.

---

# 39. Recommended benchmark summary table

| Item | Model | G | A | R | F | First-pass | Final | Fatal miss |
|---|---|---:|---:|---:|---:|---|---|---|
| RC-002 | Model A |  |  |  |  |  |  |  |
| RC-002 | Model B |  |  |  |  |  |  |  |

Aggregate results SHOULD include confidence intervals where appropriate.

---

# 40. Core principle

The benchmark's central principle is:

$$
\boxed{
\text{plausibility}
\neq
\text{proof}
\neq
\text{verified proof}.
}
$$

Generation measures whether the model can construct an argument.

Audit measures whether the model can detect failures.

Repair measures whether the model can correct them.

Independent adjudication determines whether the final proof actually survives scrutiny.

The benchmark therefore evaluates the complete research-mathematics verification workflow rather than only the fluency of a single model response.

---

# 41. Score comparability across tracks

The fatal-defect weight is 40 in Generation (§12), 8 in Audit (§13, where it weights *recall of a detected gold defect* rather than the presence of a defect), and 50 in Final (§15). These are not the same quantity and MUST NOT be compared numerically across tracks — a Generation score of 60 and a Final score of 60 do not represent equivalent proof quality, because the two scores penalize different things (raw defect presence versus post-repair residual defects) on different scales chosen for that track's dynamic range.

Cross-track comparison MUST use the categorical pass/fail criteria in §16, the independently reported dimensions (`generation_score`, `audit_score`, `repair_score`, `final_score` in §32), or `B` from §16 — never a direct comparison of, say, `G` against `F`.

Weight values in §12, §13, and §15 are themselves part of the benchmark specification and are therefore subject to the versioning and change-control rules in §36–§37: a change to any weight is a MINOR or MAJOR version change, not a silent tuning adjustment.

---

# 42. Calibration items and false-positive control

An audit track that is only ever tested against defective proofs cannot distinguish a precise referee from one that reports plausible-sounding issues regardless of whether the proof is actually flawed. RC-MPVB therefore requires calibration coverage:

- At least one item in category 27 of §6 (a valid, nontrivial proof requiring no repair) MUST be included in every Blind Audit run set, and MUST be indistinguishable in framing, length, and presentation from the defective items it is evaluated alongside.
- For each such clean item, record `false_defects_on_clean_item`: the count of reported issues classified `fatal` or `substantive` against a proof with no gold defects at that severity.
- Define **Clean-Item False Discovery Rate**:

$$
\mathrm{CleanFDR}
=
\frac{
\text{fatal or substantive issues reported on clean items}
}{
\text{fatal or substantive issues reported across all audited items}
}.
$$

- `CleanFDR` MUST be reported alongside every Audit score (§13). A model with high `WeightedRecall` and high `CleanFDR` is not a reliable referee — it is over-triggering, and the benchmark record MUST state this explicitly rather than let the aggregate Audit score `A` obscure it.
- Clean items MUST be refreshed periodically (new valid proofs written for the same theorems, or new theorems entirely) once a model's training data may plausibly include a previously used clean item, per §7.

---

# 43. Human-rater reliability

Where human graders validate defect reports (§10, §11) or serve as the final verifier (§4.4), and more than one human rater is used:

- inter-rater agreement MUST be computed and reported, using Cohen's κ for two raters or Krippendorff's α for more than two, computed over the severity classification (§9) of each reported issue;
- κ (or α) below 0.6 on a benchmark item's ratings MUST be disclosed alongside any score derived from those ratings, since scores built on unreliable ground truth are not meaningful regardless of the numeric precision reported elsewhere;
- disagreements MUST be resolved by discussion and, failing consensus, by a third rater — never by discarding the dissenting rating silently;
- the resolution outcome and the pre-resolution individual ratings MUST both be retained in the run artifacts (§29), so that a resolved gold record can later be audited for over-correction toward one rater's judgment.

---

# 44. Multi-judge disagreement resolution

When Track F (§4.4) or Track X (§4.6) uses multiple independent AI judges in place of, or alongside, human review:

1. Record every judge's verdict (PASS/FAIL, §28) and full defect report independently before any comparison between judges.
2. If all judges agree on PASS/FAIL, the record is **CONCORDANT** and the shared verdict stands, but shared misses remain possible — see the shared-blind-spot considerations in §18's independence hierarchy, which apply here without modification.
3. If judges disagree on PASS/FAIL, or agree on the verdict but disagree on which defects are fatal versus substantive, the record is **DISCORDANT**. A discordant record MUST NOT be resolved by majority vote among the AI judges alone.
4. Resolution of a discordant record requires one of, in order of preference: (a) human expert adjudication of the specific disputed claim; (b) a targeted symbolic, numerical, or formal check (§19–§20) of the specific step in dispute, where the dispute is checkable by such means; (c) escalation to a judge from a model family independent of both disagreeing judges, with the new judge shown only the disputed step and its surrounding context, not the prior judges' verdicts.
5. The final published verdict for a discordant item MUST record which resolution path was used and MUST NOT be reported as a plain PASS/FAIL indistinguishable from a concordant item — tag it `resolved_discordant` in the run metadata.
6. The discordance rate itself (fraction of items requiring this section) is a reportable benchmark statistic and SHOULD be included in §22's statistical reporting; a high discordance rate indicates either genuinely difficult items or judges operating at the edge of their reliability, and is informative either way.

---

# 45. Glossary

- **Benchmark item** — a single versioned task $T_i$ (§3).
- **Blind Audit** — evaluation condition in which the auditor receives no known-weakness information (§5).
- **Assisted Audit** — evaluation condition in which the auditor receives known weak points (§5).
- **Fatal / Substantive / Minor / Expository** — the four defect severity classes, defined in §9.
- **Gold defect inventory** — the hidden, authoritative list of defects an item is known to contain, against which reported issues are matched (§10).
- **First-pass** — a result obtained without any repair step (§17).
- **Track G / A / R / F / D / X** — Generation, blind referee Audit, critique-conditioned Repair, Final independent verification, optional Defect-localization, optional cross-model X-verification (§4).
- **Same-family audit** — an auditor from the same model family as the generator but a fresh instance or conversation (§18).
- **CleanFDR** — Clean-Item False Discovery Rate, defined in §42.
- **Concordant / Discordant** — whether independent judges agree, defined in §44.

---

# 46. License and citation

State the license under which `BENCHMARK.md`, the item set, and the gold defect inventories are released (e.g. items and prompts under one license, hidden gold data withheld from public release entirely). Public items and prompt templates SHOULD carry a permissive license to allow independent reproduction; private items and gold defect inventories in `items/private/` and `gold/private/` (§30) are exempt by construction and MUST NOT be published in a way that defeats §7's contamination controls.

Recommended citation form for results produced under this benchmark:

```text
<Model>, evaluated under RC-MPVB v<benchmark_version>, <date>. 
Protocol: <this document, commit/version>. Run IDs: <run_id list>.
```

Any publication of RC-MPVB results SHOULD link to the exact frozen version of `BENCHMARK.md` and the prompt files (§24) used, so the claim in §35 remains checkable.

---

# 47. Changelog

```text
0.1.0 — initial benchmark specification (Tracks G/A/R/F/D/X, scoring, dataset
        design, contamination controls, prompts, artifact retention).
0.2.0 — added conformance-language note (RFC 2119); added table of contents;
        converted all display/inline math to standard $ / $$ delimiters for
        portability; defined previously-unlisted item schema fields
        (expected_output_type, known_failure_modes, gold_defect_inventory,
        reference_resolution, difficulty, provenance, contamination_notes,
        §3); added Assisted Audit scoring note (§5); added judge-disagreement
        pointer to Track F (§4.4); added §41 score comparability across
        tracks; added §42 calibration items and Clean-Item False Discovery
        Rate; added §43 human-rater reliability (κ/α); added §44 multi-judge
        disagreement resolution; added §45 glossary; added §46 license and
        citation; added this changelog. No scoring formula, pass criterion,
        or task semantics changed — per §36 this is a MINOR revision.
```
