# LEDGER v1

**Item:** RC-002 · benchmark 0.2.0 · referee pass, frozen theorem only
**Conditions of this pass:** no tools, no repository, no proof text, no prior conversation. Everything below is derived from the frozen statement by hand.

---

## §0 · Reading conventions fixed for this ledger

- `dist(P,[A,B]) := min_{s∈[0,1]} ‖P − (A + s(B−A))‖₂` (the permitted definition; the minimum, not an infimum over an open set).
- `J(q) := ∂p₂/∂q` is differentiation in the **q-coordinates** `(q₁,q₂)`, evaluated at `q = (2 arctan t₁, 2 arctan t₂)`. It is *not* `∂p₂/∂t`. §1.9/A4 and F2 below.
- "Predicate" in the final syntactic claim is read as "**atom**" (see A1).
- `Φ₁`, `Φ₂` are literally functions of `t₁` only; `G` is a function of `t₂` only; `F_x,F_y` involve both.
- Truth values are classical; all inequalities are weak (`≥`, `≤`); there are no strict inequalities anywhere in `Φ`.

---

## §1 · Formal parse

### 1.1 Signature and instance data

Sort: ordered field `R` with distinguished subfield `Q`. Instance constants (all in `Q`):

```
L₁, L₂, r, μ, ε, x, y, c_x, c_y, a₁, b₁, a₂, b₂   ∈ Q
```

Derived: `R := r+μ ∈ Q`, `C := (c_x,c_y) ∈ Q²`, `P⋆ := (x,y) ∈ Q²`, `B := [a₁,b₁]×[a₂,b₂] ⊆ R²`.

Free variable of the theorem: `t = (t₁,t₂) ∈ R²` ("finite real pair" = ordinary reals, not extended).

### 1.2 Hypotheses (labelled for the usage audit, O19)

| tag | hypothesis | first apparent role |
|---|---|---|
| H1 | `L₁ > 0` | `‖p₁−p₀‖ = L₁ ≠ 0`; segment 1 nondegenerate; sign of `D₁L₁²` |
| H2 | `L₂ > 0` | `‖p₂−p₁‖ = L₂ ≠ 0`; segment 2 nondegenerate **on the FK set** |
| H3 | `r > 0, μ > 0` ⇒ `R > 0` | licenses `dist ≥ R ⟺ dist² ≥ R²` |
| H4 | `ε > 0` | licenses `\|det J\| ≥ ε ⟺ (det J)² ≥ ε²` |
| H5 | `ε ≤ \|L₁L₂\|` | **no apparent role in T1/T2/T3** — satisfiability nondegeneracy only (O19) |
| H6 | `a_i < b_i` | `B ≠ ∅`; not needed for the biconditional T2, only for its usefulness |
| H7 | all constants in `Q` | rationality of coefficients (T3) |

Note H5 is vacuous as an absolute value: under H1∧H2, `|L₁L₂| = L₁L₂`.

### 1.3 Chart and derived geometry (definitions, not claims)

For each `i`: `D_i := 1+t_i²`, `C_i := 1−t_i²`, `S_i := 2t_i`, `q_i := 2 arctan(t_i) ∈ (−π,π)`.

```
p₀ := (0,0)
p₁ := L₁(cos q₁, sin q₁)
p₂ := p₁ + L₂(cos(q₁+q₂), sin(q₁+q₂))
J(q) := ∂p₂/∂q      (2×2)
```

The chart `t ↦ q = 2 arctan t` is a strictly increasing bijection `R → (−π,π)`; `q_i = π` is **not in the image**. This is the chart hole (§1.9).

### 1.4 Atom inventory of `Φ` (with `Q`-degrees)

Distinct atoms, 15 in total (`H_{1,B} ≥ 0` occurs twice, in `Φ₁` and in `Φ₂`):

| # | atom | normal form | deg `t₁` | deg `t₂` |
|---|---|---|---|---|
| A1 | `F_x = 0` | `P = 0` | ≤2 | ≤2 |
| A2 | `F_y = 0` | `P = 0` | ≤2 | ≤2 |
| A3 | `G ≥ 0` | `P ≥ 0` | 0 | ≤4 |
| A4 | `W₁ ≤ 0` | `−W₁ ≥ 0` | ≤2 | 0 |
| A5 | `H_{1,A} ≥ 0` | `P ≥ 0`, **constant** | 0 | 0 |
| A6 | `W₁ − D₁L₁² ≥ 0` | `P ≥ 0` | ≤2 | 0 |
| A7 | `H_{1,B} ≥ 0` | `P ≥ 0` | ≤4 | 0 |
| A8 | `W₁ ≥ 0` | `P ≥ 0` | ≤2 | 0 |
| A9 | `D₁L₁² − W₁ ≥ 0` | `P ≥ 0` | ≤2 | 0 |
| A10 | `H_{1,I} ≥ 0` | `P ≥ 0` | ≤4 | 0 |
| A11 | `W₂ ≤ 0` | `−W₂ ≥ 0` | ≤2 | 0 |
| A12 | `H_{2,A} ≥ 0` | `P ≥ 0`, **constant** | 0 | 0 |
| A13 | `W₂D₁ − Q₂ ≥ 0` | `P ≥ 0` | ≤4 | 0 |
| A14 | `W₂ ≥ 0` | `P ≥ 0` | ≤2 | 0 |
| A15 | `Q₂ − W₂D₁ ≥ 0` | `P ≥ 0` | ≤4 | 0 |
| A16 | `H_{2,I} ≥ 0` | `P ≥ 0` | ≤4 | 0 |

Structural observations a referee must confirm, not assume:
- A5 and A12 are **degree-0**: their truth is instance-fixed, independent of `t`. So disjunct 1 of `Φ₁` (resp. `Φ₂`) is governed entirely by the sign guard `W₁ ≤ 0` (resp. `W₂ ≤ 0`) times a constant Boolean.
- Rationality of A3, A5, A7, A10, A12, A16 requires `R² = (r+μ)² ∈ Q` and `ε² ∈ Q` — immediate from H7, but it is the only place H7 is load-bearing for T3.
- A9 = ¬-free complement of A6 at the seam; A15 = complement of A13. The pairs are **not** mutually exclusive: they overlap exactly on the seam `{W₁ = D₁L₁²}`, `{W₂D₁ = Q₂}`.

### 1.5 Boolean structure

```
Φ  =  A1 ∧ A2 ∧ A3 ∧ Φ₁ ∧ Φ₂
Φ₁ =  (A4∧A5) ∨ (A6∧A7) ∨ (A8∧A9∧A10)
Φ₂ =  (A11∧A12) ∨ (A13∧A7) ∨ (A14∧A15∧A16)
```

Shape: conjunction of 3 atoms with two 3-way disjunctions of 2-or-3-atom conjunctions. DNF expansion: 9 disjuncts, each of 3+2/3+2/3 = 7 to 9 atoms. This shape is exactly what E1 below must match.

### 1.6 Claim separation

Three mathematical claims and one non-mathematical claim are bundled. They must be graded separately.

- **T1 (pointwise).** `∀ t ∈ R² :  Φ(t₁,t₂) ⟺ [ p₂ = P⋆ ∧ dist(C,[p₀,p₁]) ≥ R ∧ dist(C,[p₁,p₂]) ≥ R ∧ |det J(q)| ≥ ε ]`, where `q = (2 arctan t₁, 2 arctan t₂)` and `p₁,p₂,J` are the objects of §1.3 evaluated at that `q`. Biconditional: **both directions carry content and must be proved separately.**
- **T2 (bounded existential corollary).** `(∃ t ∈ B : Φ(t)) ⟺ (∃ t ∈ B : [system])`. The word "Consequently" fixes the intended derivation as instantiation of T1; a proof of T2 by any other route must be checked for smuggled hypotheses.
- **T3 (syntactic).** Every atom of the displayed formulas is `P = 0` or `P ≥ 0` with `P ∈ Q[t₁,t₂]`.
- **E (implementation correspondence).** *Not a mathematical claim.* Cannot be discharged from prose, from T1–T3, or from this ledger. Recorded as E1–E4 in §6.

### 1.7 Quantifier structure

- T1: `∀t ∈ R²` outermost, biconditional inside. No existential.
- T2: `∃t ∈ B` on **each** side of the biconditional, over the **same** box, in **t-coordinates**. Matches metadata `quantifier_structure: one existential witness pair after fixed instance data`.
- T2 does **not** quantify over `q ∈ (−π,π)²`, over the torus `T²`, or over instance parameters. The image of `B` under the chart is the `q`-box `[2 arctan a₁, 2 arctan b₁] × [2 arctan a₂, 2 arctan b₂]`, whose endpoints are in general **irrational**; the theorem never asserts anything about that box, and a proof must not need to.

### 1.8 Boundary and degenerate case register

Every entry here is admissible (in scope) unless marked *excluded*.

| case | status | required behaviour |
|---|---|---|
| `t₂ = 0` (`q₂ = 0`, `det J = 0`) | admissible | `G(0) = −ε² < 0`; `Φ` false. Consistent. |
| `t₂ = ±1` (`\|sin q₂\| = 1`, `\|det J\| = L₁L₂` maximal) | admissible | if `ε = L₁L₂` then `G = −L₁²L₂²(t₂²−1)² ≤ 0` with equality **only** at `t₂ = ±1` |
| `ε = \|L₁L₂\|` (boundary of H5) | admissible | `G ≥ 0` holds at exactly two points |
| `ε > L₁L₂` (violates H5) | out of hypothesis | would make `G < 0` everywhere; T1 still true (both sides false) |
| `dist = R` exactly | admissible | weak inequality ⇒ **must** be accepted |
| `\|det J\| = ε` exactly | admissible | weak inequality ⇒ **must** be accepted |
| `W₁ = 0` (projection at `p₀`) | seam | disjuncts 1 and 3 of `Φ₁` both fire; must agree |
| `W₁ = D₁L₁²` (projection at `p₁`) | seam | disjuncts 2 and 3 of `Φ₁` both fire; must agree |
| `W₂ = 0` (projection at `P⋆`) | seam | disjuncts 1 and 3 of `Φ₂` both fire |
| `W₂D₁ = Q₂` (projection at `p₁`) | seam | disjuncts 2 and 3 of `Φ₂` both fire |
| `C = p₀`, `C = p₁`, `C = P⋆`, `C` on a link | admissible | `dist = 0 < R`; `Φ` must be false |
| `Q₂ = 0` i.e. `p₁ = P⋆` | **admissible in `R²`, excluded on the FK set** | off the FK set `Φ₂` degenerates to `TRUE` (see §2.4); on the FK set impossible by H2 |
| `‖p₁−p₀‖ = 0` | **impossible** by H1 | segment 1 is never degenerate |
| `q_i = π` | **excluded** — outside the chart image | scope exclusion, not a defect |
| `D_i = 0` | **impossible**: `D_i = 1+t_i² ≥ 1` | all denominator clearing is sign-safe |
| `B` degenerate (`a_i = b_i`) | excluded by H6 | harmless either way |

### 1.9 Scope exclusions parsed as explicit *non-claims*

The item asserts **nothing** about: (i) completeness on the configuration torus `T²` (the chart misses `q_i = π`); (ii) robustness/uncertainty in `L, r, μ, ε, P⋆, C`; (iii) path feasibility or connectivity of the witness set; (iv) certified infeasibility from a failed witness search — absence of `t ∈ B` with `Φ(t)` proves nothing about the physical problem. A proof that establishes any of (i)–(iv) has exceeded the item; a proof that *needs* any of (i)–(iv) has misread it.

**Ambiguity register (all non-blocking; resolved as stated, not grounds to stop):**

- **A1.** "*every displayed predicate is a polynomial equality or weak inequality*" — `Φ`, `Φ₁`, `Φ₂` are Boolean combinations, not single (in)equalities. Read as "every **atom**". Under any other reading T3 is false as stated for `Φ,Φ₁,Φ₂`.
- **A2.** In `(RC-002-exists)` the right-hand system suppresses that `p₁,p₂,J` depend on the quantified `t` through `q = 2 arctan t`. Read as the same `t`.
- **A3.** `|L₁L₂|` — absolute value vacuous under H1∧H2.
- **A4.** `J(q) := ∂p₂/∂q` — differentiation in `q`, not `t`. Consequential: `∂p₂/∂t = J(q)·diag(2/D₁, 2/D₂)`, so `det(∂p₂/∂t) = 4·det J(q)/(D₁D₂)`. Under the `t`-reading, `G` would be the wrong polynomial. See F2.
- **A5.** Degenerate-segment convention for `dist(P,[A,A])`. Never needed for segment 1 (H1); for segment 2 it is neutralized by O12.

---

## §2 · Counterexample search

### 2.1 Method

Direct evaluation of `Φ` against the geometric system on: (a) the full boundary/degenerate register of §1.8; (b) all four selector seams; (c) both squaring steps at sign-critical points; (d) sign of every quantity used to clear a denominator; (e) each of the 9 DNF branches for false-positive and false-negative behaviour; (f) both quantifier readings of T2; (g) the standalone-vs-conditional reading of `Φ₂`. Small rational instances with `L₁=L₂=1` were used throughout so that all arithmetic is exact and reproducible.

### 2.2 Probe log (representative; exact rationals)

| probe | instance | `Φ` | geometry | agree |
|---|---|---|---|---|
| P1 positive, at **both** boundaries | `L₁=L₂=1, ε=1, P⋆=(1,1), C=(3,0), R=1/4, t=(0,1)` | `F_x=F_y=0`; `G = 2−1−1 = 0 ≥ 0`; `Φ₁` via disjunct 2 (`W₁−D₁L₁² = 2`, `H_{1,B} = 63/16`); `Φ₂` via disjuncts 2 **and** 3 (`W₂D₁−Q₂ = 0`, `H_{2,I} = 63/16`) ⇒ **true** | `p₂=(1,1)=P⋆`; `dist₁ = dist₂ = 2 ≥ 1/4`; `\|det J\| = 1 = ε` ⇒ **true** | ✓ |
| P2 seam agreement, segment 2 | same as P1: `s₂⋆ = W₂D₁/Q₂ = 1` exactly | both overlapping disjuncts evaluate to `63/16 ≥ 0` | closest point is `p₁`, `dist = 2` | ✓ |
| P3 interior branch, negative | `L₁=1, t₁=0, C=(1/2,1/10), R=1/4` | `W₁ = 1/2 ∈ [0,1]`; `H_{1,I} = (1/100 − 1/16) = −21/400 < 0`; other disjuncts fail ⇒ `Φ₁` **false** | `dist₁ = 1/10 < 1/4` ⇒ **false** | ✓ |
| P4 singularity, `t₂=0` | any | `G = −ε² < 0` ⇒ **false** | `det J = 0 < ε` ⇒ **false** | ✓ |
| P5 singularity, sub-threshold | `L₁L₂=1, ε=9/10, t₂=1/2` | `G = (4−81/50)(1/4) − 81/1600 − 81/100 < 0` ⇒ **false** | `\|det J\| = 4/5 < 9/10` ⇒ **false** | ✓ |
| P6 singularity, super-threshold | `L₁L₂=1, ε=1/2, t₂=1/2` | `G = 7/8 − 1/64 − 1/4 = 39/64 > 0` ⇒ **true** | `\|det J\| = 4/5 ≥ 1/2` ⇒ **true** | ✓ |
| P7 H5 at equality | `ε = L₁L₂` | `G = −L₁²L₂²(t₂²−1)² ≤ 0`, `= 0` iff `t₂=±1` | `\|det J\| ≥ ε` iff `\|sin q₂\|=1` iff `q₂=±π/2` iff `t₂=±1` | ✓ |
| P8 `C` at obstacle-on-endpoint | `C = P⋆`, any `t` on FK set | `W₂ = 0`, `H_{2,A} = −R² < 0`, `H_{2,I} = −R²Q₂ < 0`, `W₂D₁−Q₂ = −Q₂ < 0` ⇒ `Φ₂` **false** | `dist₂ = 0 < R` ⇒ **false** | ✓ |
| P9 `C = p₀` | `C = (0,0)` | `W₁ = 0`, `H_{1,A} = −R² < 0`, `H_{1,I} = −R²D₁²L₁² < 0` ⇒ `Φ₁` **false** | `dist₁ = 0 < R` ⇒ **false** | ✓ |
| P10 guard coverage | `Φ₁`: `(−∞,0] ∪ [D₁L₁²,∞) ∪ [0,D₁L₁²] = R` since `D₁L₁² > 0`; `Φ₂`: same in `s₂⋆` since `Q₂ > 0` on the FK set | covers | covers | ✓ |
| P11 `Q₂ = 0` **inside** `Φ` | requires `p₁ = P⋆` **and** `p₂ = P⋆`, i.e. `p₁ = p₂`, contradicting `‖p₂−p₁‖ = L₂ > 0` | unreachable | — | ✓ (vacuous) |
| P12 T2 quantifier reading | `B` in `t`-coordinates on both sides | T1 holds `∀t ∈ R² ⊇ B`; instantiation is immediate in both directions | — | ✓ |

Additional checks that came out clean and are recorded so they need not be re-derived: `C_i² + S_i² = D_i²` (hence `‖p₁‖ = L₁` **identically in `t₁`**, so segment 1 never degenerates); `F_x = (x − p_{2,x})D₁D₂` and `F_y = (y − p_{2,y})D₁D₂` exactly, with `D₁D₂ ≥ 1 > 0`; `E = D₁(C − p₁)` hence `H_{1,B} = D₁²(‖C−p₁‖² − R²)`; `H_{1,I} = D₁²L₁²(dist₁² − R²)` on the interior branch; `V = D₁(p₁ − P⋆)`, `W₂ = D₁⟨C−P⋆, p₁−P⋆⟩`, `s₂⋆ = W₂D₁/Q₂`; the reuse of `H_{1,B}` in `Φ₂`'s middle disjunct is **correct, not a typo** — `p₁` is the shared endpoint of both segments, and the `s₂⋆ ≥ 1` branch of segment 2 is exactly the `p₁`-endpoint branch; and `4L₁²L₂²t₂² ≥ ε²(1+t₂²)²` rearranges to `G ≥ 0` with no residual term.

### 2.3 Verdict

```
NO COUNTEREXAMPLE FOUND
```

for T1, T2 and T3 **as written**, under the readings fixed in §0 and the ambiguity register A1–A5. The statement is well-posed; the referee does not stop here.

This verdict is a search result, not a proof. It records that the encoding survived every degenerate case, seam, sign condition and squaring step probed above; it does **not** discharge any obligation in §3.

### 2.4 Recorded refutation of a reading the theorem does *not* make

The following is **not** a counterexample to RC-002. It is retained because it refutes the most natural over-strong lemma a proof may reach for, and because it pins the exact hypothesis that makes `Φ₂` sound.

**Claim refuted:** "`Φ₂(t₁) ⟺ dist(C,[p₁,p₂]) ≥ R` for all `t ∈ R²`" (i.e. `Φ₂` read as a standalone encoding of segment-2 clearance).

**Instance:** `L₁ = L₂ = 1`, `P⋆ = (x,y) = (1,10)`, `C = (1, −1/2)`, `r = μ = 1/8` so `R = 1/4`, `ε = 1`. Evaluate at `t = (0, −1)`, i.e. `q = (0, −π/2)`.

```
p₁ = (1,0),  p₂ = (1,0) + (cos(−π/2), sin(−π/2)) = (1,−1)
true segment 2 = [(1,0),(1,−1)]  ∋  C = (1,−1/2)   ⇒  dist(C,[p₁,p₂]) = 0 < 1/4 = R   (geometry FALSE)

V_x = L₁C₁ − xD₁ = 1 − 1 = 0            V_y = L₁S₁ − yD₁ = 0 − 10 = −10
Q₂  = 100                                W₂ = (1−1)·0 + (−1/2−10)·(−10) = 105
W₂D₁ − Q₂ = 105 − 100 = 5 ≥ 0           (middle guard fires)
E_x = c_xD₁ − L₁C₁ = 0                   E_y = c_yD₁ − L₁S₁ = −1/2
H_{1,B} = 0 + 1/4 − (1/16)(1) = 3/16 > 0
⇒ Φ₂(0) = TRUE                                                        (encoding TRUE)
```

`Φ₂` measured clearance to the **virtual** segment `[p₁,P⋆] = [(1,0),(1,10)]`, whose nearest point to `C` is `p₁` at distance `1/2 ≥ R`. The true segment is elsewhere.

**Why RC-002 is untouched:** at this `t`, `F_y = 10·1·2 − 0 − (0·0 + 1·(−2)) = 22 ≠ 0` (indeed `p_{2,y} = −1 ≠ 10`), so `Φ` is false and the theorem's biconditional is unstrained. (`F_x = 0` here by coincidence — `p_{2,x} = 1 = x` — which is exactly why the check must use **both** `F_x` and `F_y`.)

**Consequence for the ledger:** segment-2 correctness is a **conditional** lemma over the FK variety `{F_x = F_y = 0}`, and `Q₂ > 0` is a **derived** fact on that variety, not a standing hypothesis. Off that variety `Q₂ = 0` is attainable (`p₁ = P⋆`), and there `W₂ = 0`, `H_{2,I} = 0`, so *all three* guards fire and `Φ₂` collapses to `TRUE` unconditionally. See O12, O14, O15, F1, F3.

---

## §3 · Obligation ledger

Each obligation is stated so it can be checked in isolation given its dependencies. Numbering is derived from the theorem's own structure; it does not presuppose any proof strategy.

**Tier 0 — primitives (no dependencies)**

- **O1 · Chart identities.** For all `t ∈ R` with `q = 2 arctan t`: (a) `q ∈ (−π,π)` and `t ↦ q` is a strictly increasing bijection `R → (−π,π)`; (b) `cos q = C/D`, `sin q = S/D` where `D = 1+t²`, `C = 1−t²`, `S = 2t`; (c) `C² + S² = D²`. *Not quotable as elementary:* (b) is a nontrivial trigonometric equivalence and must be proved (and proved on all of `R`, not merely for `q ∈ (−π/2,π/2)`).
  *Deps:* —
- **O2 · Positivity and rationality register.** `D_i = 1+t_i² ≥ 1 > 0`; `D₁D₂ > 0`; `D_i² > 0`; `L₁,L₂,R,ε > 0` (H1–H4); `D₁L₁² > 0`; `R², ε², 4L₁²L₂² ∈ Q`. Every later multiplication of an inequality by a cleared denominator must cite the specific entry here that gives its sign.
  *Deps:* —
- **O3 · Nonnegative squaring lemma.** For `u,v ∈ R` with `u ≥ 0` and `v ≥ 0`: `u ≥ v ⟺ u² ≥ v²`. State and prove; it is used at three distinct places with three distinct `v` (`R`, `ε`, and clearing `‖·‖`), and it is **false** without both nonnegativity hypotheses.
  *Deps:* —
- **O4 · Point-to-segment normal form.** For `A ≠ B` in `R²`, `P ∈ R²`, `d := B−A`, `s⋆ := ⟨P−A,d⟩/‖d‖²`: the minimum in the definition of `dist(P,[A,B])` is attained; and
  `dist² = ‖P−A‖²` if `s⋆ ≤ 0`; `dist² = ‖P−B‖²` if `s⋆ ≥ 1`; `dist² = ‖P−A‖² − ⟨P−A,d⟩²/‖d‖²` if `0 ≤ s⋆ ≤ 1`.
  Includes: attainment (continuity + compactness of `[0,1]`, or strict convexity of `s ↦ ‖P−A−sd‖²` with positive leading coefficient `‖d‖² > 0`); the clamping argument; and **agreement of the three formulas on the overlaps `s⋆ = 0` and `s⋆ = 1`** (the three guards are not a partition). Also record the `A = B` convention and why it is never invoked (O12).
  *Deps:* —
- **O7 · Jacobian determinant.** With `p₂` as in §1.3 and differentiation in `q`: compute the four entries of `J(q)` and prove `det J(q) = L₁L₂ sin q₂`, hence `|det J(q)| = L₁L₂|sin q₂|` under H1∧H2. Separately record `∂p₂/∂t = J(q)·diag(2/D₁, 2/D₂)` and `det(∂p₂/∂t) = 4 det J(q)/(D₁D₂)`, and confirm the theorem's `J` is the former.
  *Deps:* —

**Tier 1 — encoding identities**

- **O5 · Forward-kinematics clearing.** As polynomial identities in `Q[t₁,t₂]` composed with O1: `F_x = (x − p_{2,x})·D₁D₂` and `F_y = (y − p_{2,y})·D₁D₂`. Conclude `(F_x = 0 ∧ F_y = 0) ⟺ p₂ = P⋆`, citing `D₁D₂ ≠ 0` from O2. Both directions.
  *Deps:* O1, O2
- **O6 · Link-length identities.** For all `t ∈ R²`: `‖p₁ − p₀‖ = L₁` and `‖p₂ − p₁‖ = L₂`. (Via O1(c) in the half-angle form, or directly from `cos²+sin² = 1`.) Consequence to record: segment 1 is never degenerate.
  *Deps:* O1
- **O8 · Singularity encoding.** For all `t₂ ∈ R`: `|det J(q)| ≥ ε ⟺ G(t₂) ≥ 0`. Chain: `L₁L₂|sin q₂| ≥ ε` (O7) `⟺ 4L₁²L₂²t₂² ≥ ε²D₂²` (O3 with `u = L₁L₂|sin q₂| ≥ 0`, `v = ε > 0`; O1(b); O2 for `D₂² > 0`) `⟺ G ≥ 0` by expanding `ε²(1+t₂²)² = ε²t₂⁴ + 2ε²t₂² + ε²` and collecting. Verify the collected coefficient of `t₂²` is exactly `4L₁²L₂² − 2ε²`.
  *Deps:* O1, O2, O3, O7
- **O18 · Syntactic/algebraic claim (T3).** Enumerate the 15 distinct atoms of §1.4; for each, exhibit the normal form `P = 0` or `P ≥ 0` with `P ∈ Q[t₁,t₂]` and confirm its degree bounds; confirm no strict inequality and no non-polynomial atom occurs; conclude (a) the solution set of `Φ` is a **closed** semialgebraic subset of `R²` defined over `Q`, and (b) `Φ` is exactly decidable at any rational point by finite `Q`-arithmetic with no rounding and no root extraction. Note explicitly that `H_{1,A}` and `H_{2,A}` are degree-0.
  *Deps:* O2

**Tier 2 — segment 1 (unconditional)**

- **O9 · Segment-1 projection parameter.** `‖p₁−p₀‖² = L₁² > 0`; `⟨C−p₀, p₁−p₀⟩ = W₁/D₁`; hence `s₁⋆ = W₁/(D₁L₁²)`. Guard translation, each step citing `D₁L₁² > 0` (O2): `s₁⋆ ≤ 0 ⟺ W₁ ≤ 0`; `s₁⋆ ≥ 1 ⟺ W₁ − D₁L₁² ≥ 0`; `0 ≤ s₁⋆ ≤ 1 ⟺ (W₁ ≥ 0 ∧ D₁L₁² − W₁ ≥ 0)`.
  *Deps:* O1, O2, O6
- **O10 · Segment-1 branch equivalences.** With `dist₁ := dist(C,[p₀,p₁])`, prove each of:
  (a) `s₁⋆ ≤ 0 ⇒ ( dist₁ ≥ R ⟺ H_{1,A} ≥ 0 )`;
  (b) `s₁⋆ ≥ 1 ⇒ ( dist₁ ≥ R ⟺ H_{1,B} ≥ 0 )`, via `E = D₁(C−p₁)` and `H_{1,B} = D₁²(‖C−p₁‖² − R²)`;
  (c) `0 ≤ s₁⋆ ≤ 1 ⇒ ( dist₁ ≥ R ⟺ H_{1,I} ≥ 0 )`, via `H_{1,I} = D₁²L₁²(dist₁² − R²)`.
  Each uses O4 for the branch formula and O3 with `u = dist₁ ≥ 0`, `v = R > 0` for the squaring; each multiplication by `D₁²` or `D₁²L₁²` cites O2.
  *Deps:* O2, O3, O4, O9
- **O12 · Segment-2 nondegeneracy.** (a) Identity `Q₂ = D₁²‖p₁ − P⋆‖²` for all `t₁`. (b) On `{F_x = F_y = 0}`: `p₂ = P⋆` (O5) and `‖p₂ − p₁‖ = L₂ > 0` (O6, H2) force `p₁ ≠ P⋆`, hence `Q₂ = D₁²L₂² > 0`. (c) **Failure mode to record:** off that set `Q₂ = 0` is attainable, and then `W₂ = 0`, `H_{2,I} = 0`, all three guards of `Φ₂` fire and `Φ₂ ≡ TRUE`; therefore O14/O15 must be stated conditionally and O4 must never be invoked with a degenerate segment.
  *Deps:* O2, O5, O6

**Tier 3 — segment 2 (conditional on FK)**

- **O13 · Segment-2 projection parameter.** With base point `P⋆` and direction `d = p₁ − P⋆`: `V = D₁(p₁−P⋆)`; `W₂ = D₁⟨C−P⋆, p₁−P⋆⟩`; `‖d‖² = Q₂/D₁²`; hence `s₂⋆ = W₂D₁/Q₂`. Guard translation, each step citing `Q₂ > 0` (O12b) and `D₁ > 0` (O2): `s₂⋆ ≤ 0 ⟺ W₂ ≤ 0`; `s₂⋆ ≥ 1 ⟺ W₂D₁ − Q₂ ≥ 0`; `0 ≤ s₂⋆ ≤ 1 ⟺ (W₂ ≥ 0 ∧ Q₂ − W₂D₁ ≥ 0)`.
  *Deps:* O2, O12
- **O14 · Segment-2 branch equivalences (conditional).** Assume `F_x = F_y = 0`, so `[p₁,p₂] = [p₁,P⋆]` (O5). With `dist₂ := dist(C,[p₁,p₂])`:
  (a) `s₂⋆ ≤ 0 ⇒ ( dist₂ ≥ R ⟺ H_{2,A} ≥ 0 )` — nearest point is `P⋆ = p₂`;
  (b) `s₂⋆ ≥ 1 ⇒ ( dist₂ ≥ R ⟺ H_{1,B} ≥ 0 )` — nearest point is `p₁`; **justify the reuse of `H_{1,B}`** by the shared-endpoint identity `H_{1,B} = D₁²(‖C−p₁‖² − R²)` from O10(b), and confirm no `L₂`- or `P⋆`-dependence is missing;
  (c) `0 ≤ s₂⋆ ≤ 1 ⇒ ( dist₂ ≥ R ⟺ H_{2,I} ≥ 0 )`, via `H_{2,I} = Q₂(dist₂² − R²)`, multiplying by `Q₂ > 0` (O12b).
  *Deps:* O3, O4, O5, O10, O12, O13
- **O11 · Segment-1 assembly.** The three guards of `Φ₁` cover `R` (O9 + `D₁L₁² > 0`); therefore, by the covering-guard schema — *if guards `Γ_k` cover and `Γ_k ⇒ (P_k ⟺ Ψ)` for each `k`, then `⋁_k (Γ_k ∧ P_k) ⟺ Ψ`* — conclude `∀ t₁ ∈ R : Φ₁(t₁) ⟺ dist(C,[p₀,p₁]) ≥ R`, **unconditionally**. Prove the schema (both directions; note it tolerates overlapping guards and does *not* require a partition).
  *Deps:* O9, O10
- **O15 · Segment-2 assembly (conditional).** The three guards of `Φ₂` cover `R` in `s₂⋆` given `Q₂ > 0` (O13); by the same schema, `∀ t ∈ R² : (F_x = 0 ∧ F_y = 0) ⇒ ( Φ₂(t₁) ⟺ dist(C,[p₁,p₂]) ≥ R )`. Record explicitly that the unconditional form is **false** (§2.4), so this obligation may not be strengthened.
  *Deps:* O13, O14

**Tier 4 — theorem assembly**

- **O16 · Pointwise equivalence (T1).** Both directions, with the FK conjunct discharged *before* segment 2 is invoked:
  (⇒) `Φ ⇒ F_x = F_y = 0 ⇒ p₂ = P⋆` (O5); then `G ≥ 0 ⇒ |det J| ≥ ε` (O8); `Φ₁ ⇒ dist₁ ≥ R` (O11); `Φ₂ ∧ FK ⇒ dist₂ ≥ R` (O15).
  (⇐) system `⇒ p₂ = P⋆ ⇒ F_x = F_y = 0` (O5); `|det J| ≥ ε ⇒ G ≥ 0` (O8); `dist₁ ≥ R ⇒ Φ₁` (O11); `dist₂ ≥ R` together with the already-established FK conjunct `⇒ Φ₂` (O15).
  Confirm no step of the (⇐) direction uses O15 before FK is available.
  *Deps:* O5, O8, O11, O15
- **O17 · Bounded-witness equivalence (T2).** Since O16 holds for every `t ∈ R²` and `B ⊆ R²`, instantiate at an arbitrary `t ∈ B` and apply `∃`-introduction/elimination in both directions. Confirm: the same box on both sides; the box is in `t`-coordinates; no appeal to compactness, continuity, or connectedness of `B`; no appeal to H6 (which is needed only for `B ≠ ∅`, i.e. for the statement to be non-trivially interesting, not for its truth).
  *Deps:* O16

**Tier 5 — audits**

- **O19 · Hypothesis-usage audit.** For each of H1–H7, list every obligation that uses it and the exact step. Specifically establish: **H5 (`ε ≤ |L₁L₂|`) is used nowhere in O1–O18** — and if a candidate proof does use it, locate the step and determine whether the use is essential (which would indicate an error, since T1 is true for `ε > L₁L₂` as well, both sides being false). Confirm H3 is used only as `R ≥ 0` in O3-applications, H4 only as `ε ≥ 0` in O8, H1 in O6/O9, H2 in O12b, H6 in O17 only for non-vacuity, H7 in O18.
  *Deps:* O1–O18
- **O20 · Scope-fidelity audit.** Confirm no obligation asserts or requires: torus completeness (`q_i = π` is outside the chart); robustness over parameter or task-point uncertainty; path feasibility; or infeasibility certification from a failed search. Confirm the `t`-box `B` is never silently identified with a `q`-box, and that no rationality claim is made about `2 arctan a_i`.
  *Deps:* O16, O17

---

## §4 · Dependency graph

Edge list (`X → Y` = "Y depends on X"):

```
O1 → O5, O6, O8, O9
O2 → O5, O8, O9, O10, O12, O13, O18
O3 → O8, O10, O14
O4 → O10, O14
O7 → O8
O5 → O12, O14, O16
O6 → O9, O12
O8 → O16
O9 → O10, O11
O10 → O11, O14
O12 → O13, O14
O13 → O14, O15
O14 → O15
O11 → O16
O15 → O16
O16 → O17, O19, O20
O17 → O19, O20
O18 → O19
```

Layered rendering (each layer depends only on strictly earlier layers):

```
L0  O1   O2   O3   O4   O7                      primitives
      |    |    |    |    |
L1  O5   O6   O8   O18                          encoding identities
      |    |    |
L2  O9   O12                                    projection setup (seg1 / seg2-nondegeneracy)
      |    |
L3  O10  O13                                    branch equivalences / seg2 guards
      |    |
L4  O11  O14                                    seg1 assembly / seg2 branches
           |
L5       O15                                    seg2 conditional assembly
           |
L6       O16   ← also from O5, O8, O11          T1  pointwise
           |
L7       O17                                    T2  bounded existential
           |
L8  O19  O20                                    audits
```

Roots (checkable with no prerequisites): **O1, O2, O3, O4, O7**.
Critical path (longest chain to T1): `O2 → O12 → O13 → O14 → O15 → O16`, gated at O12 by `O5 → O6 → O1`. **O12 is the single articulation point of the whole ledger**: remove it and O13–O16 lose their sign justification and O15 becomes false (§2.4).
Independent side-branch: **O18** (T3) touches nothing else except through O2; it can be graded in parallel and its failure does not affect T1/T2.

---

## §5 · Difficulty forecast

Five points where a candidate proof is most likely to break, each with the characteristic invalid shortcut.

**F1 · Segment 2 is only conditionally encoded.**
`Φ₂` measures clearance to the *virtual* segment `[p₁,P⋆]`, not to `[p₁,p₂]`. These coincide only on `{F_x = F_y = 0}`.
*Invalid shortcut:* proving a standalone lemma "`Φ₂(t₁) ⟺ dist(C,[p₁,p₂]) ≥ R`" and then conjoining. Refuted in §2.4: at `L₁=L₂=1`, `P⋆=(1,10)`, `C=(1,−1/2)`, `R=1/4`, `t=(0,−1)`, `Φ₂` is true while `dist₂ = 0`.
*Secondary shortcut:* in the (⇐) direction of O16, invoking the segment-2 lemma before `p₂ = P⋆` has been established — a circularity that is easy to miss because both facts are conjuncts of the same system.
*Detection:* the proof must exhibit `F_x = F_y = 0` as an explicit hypothesis of its segment-2 lemma, in **both** directions.

**F2 · Jacobian taken in the wrong coordinates, or quoted.**
`det J(q) = L₁L₂ sin q₂` is stated for `∂p₂/∂q`. But `∂p₂/∂t = J(q)·diag(2/D₁, 2/D₂)`, so `det(∂p₂/∂t) = 4 det J(q)/(D₁D₂)` — differing by a `t`-dependent factor. Encoding the latter would yield a polynomial other than `G`.
*Invalid shortcut (a):* differentiating `p₂` in the chart variables `t` because that is where the algebra lives, and calling the result `det J`.
*Invalid shortcut (b):* asserting `det J = L₁L₂ sin q₂` as "the standard planar-2R result". `permitted_prior_results` admits only elementary real arithmetic, trigonometric identities, and the point-to-segment definition; every nontrivial equivalence beyond these must be proved. The four partials and the cancellation of the `L₂² sin(q₁+q₂)cos(q₁+q₂)` terms must appear.
*Also check:* the sign convention (`q₂` relative, not absolute) matches `p₂ = p₁ + L₂(cos(q₁+q₂), sin(q₁+q₂))`.

**F3 · Sign discipline in squaring and denominator clearing.**
Three distinct squarings (`dist₁ ≥ R`, `dist₂ ≥ R`, `|det J| ≥ ε`) and at least five denominator-clearings (`×D₁D₂`, `×D₁²`, `×D₁²L₁²`, `×D₂²`, `×Q₂`) occur.
*Invalid shortcut (a):* squaring a guard. The guards `W₁ ≤ 0`, `W₂ ≤ 0`, `W₁ − D₁L₁² ≥ 0` are sign conditions on quantities of **unknown sign**; `u ≥ v ⟺ u² ≥ v²` (O3) does not apply and squaring them destroys the case split.
*Invalid shortcut (b):* multiplying the interior-branch inequality by `Q₂` without first proving `Q₂ > 0` — the exact gap that makes `Φ₂` vacuous at `Q₂ = 0` (§2.4, O12c). A proof that says "`Q₂ = D₁²L₂² > 0` since the second link has length `L₂`" **without citing `F_x = F_y = 0` first** has assumed its conclusion.
*Invalid shortcut (c):* omitting `R ≥ 0` / `ε ≥ 0` when invoking O3, i.e. treating `dist ≥ R ⟺ dist² ≥ R²` as unconditional.
*Cheap detection:* every inequality manipulation in the proof should name the positive quantity it multiplied by and cite where positivity was proved.

**F4 · The three-branch selector: coverage, overlap, and direction.**
The guard triples are **covers, not partitions** — they overlap exactly on the seams `W₁ = 0`, `W₁ = D₁L₁²`, `W₂ = 0`, `W₂D₁ = Q₂`.
*Invalid shortcut (a):* arguing "let `k` be *the* branch containing `s⋆`" and concluding from a unique branch — the reasoning silently assumes disjointness, and the (⇐) direction then needs a branch-selection that the proof has not supplied.
*Invalid shortcut (b):* proving only `Γ_k ∧ P_k ⇒ Ψ` (soundness) and declaring the equivalence done. Completeness (`Ψ ⇒ ⋁_k Γ_k ∧ P_k`) needs coverage *and* `Γ_k ⇒ (P_k ⟸ Ψ)`.
*Invalid shortcut (c):* claiming the branches must be checked for mutual consistency at the seams and then *proving* consistency by direct algebra instead of deriving it from `P_k ⟺ Ψ` on `Γ_k`. Not wrong, but it is work the schema makes unnecessary — and doing it by hand invites arithmetic slips. (The seams do agree; verified at P1/P2 and at `W₁ = D₁L₁²`, where both branches reduce to `c_x² + c_y² − R² ≥ L₁²`.)
*Also verify:* coverage of `Φ₂`'s guards presupposes `Q₂ > 0`, so F4 for segment 2 is downstream of F3(b).

**F5 · Boundary cases, equality cases, and the unused hypothesis.**
*Invalid shortcut (a):* proving strict versions (`dist > R`, `|det J| > ε`) and asserting the weak case "follows by continuity". It does not follow, and the weak cases are the operationally important ones (`|det J| = ε` at `t₂ = ±1` when `ε = L₁L₂` is the *only* point where `G ≥ 0` holds at all).
*Invalid shortcut (b):* using H5 (`ε ≤ |L₁L₂|`) as if it licensed the squaring in O8, or as if `G ≥ 0` were satisfiable-by-hypothesis. O8 is unconditional in `ε`; H5 is a satisfiability nondegeneracy and appears nowhere in T1/T2/T3 (O19). A proof that *needs* H5 has an error elsewhere.
*Invalid shortcut (c):* treating `H_{1,A}` / `H_{2,A}` as `t`-dependent, or conversely concluding from their constancy that the first disjunct is instance-decidable and can be dropped — it cannot; it is still gated by `W₁ ≤ 0` / `W₂ ≤ 0`.
*Invalid shortcut (d):* silently extending the chart to `q_i = π` (e.g. by "`t → ∞`", or by claiming `Φ` decides the torus). That is an explicit scope exclusion; asserting it converts a true theorem into a false one.

---

## §6 · Separate implementation-correspondence evidence obligations

**Not derivable from prose, from §3, or from any proof of T1–T3.** Discharging §3 says nothing about these; passing these says nothing about §3. Each requires deterministic, re-runnable code/test artifacts.

- **E1 · Builder fidelity.** Artifact showing the serialized predicate coefficients and Boolean structure match §1.4–§1.5 exactly: the 15 distinct atoms with their polynomials over `Q`, the top-level 5-way conjunction, the two 3-way disjunctions with arities `2/2/3`, and in particular that `H_{1,B}` is the object reused in `Φ₂`'s middle disjunct (not a separately-derived duplicate that could drift). Coefficient-level golden comparison, not structural spot-check.
- **E2 · Quantifier and box handling.** Artifact showing the emitted `EXISTS (t1,t2)` prefix binds exactly the two chart variables, over the box `[a₁,b₁]×[a₂,b₂]` in **`t`-coordinates**, with closed (weak) bounds, and that the box is not confused with any `q`-space interval.
- **E3 · Exact-rational evaluation.** Artifact showing the registered checker evaluates atoms and the full formula in exact `Q` arithmetic — no floating point, no tolerance, no root extraction — including tests that land exactly on the seams (`W₁ = 0`, `W₁ = D₁L₁²`, `W₂ = 0`, `W₂D₁ = Q₂`) and on the equality cases (`dist = R`, `|det J| = ε`), where any epsilon-fudging flips the answer.
- **E4 · Fail-closed behaviour.** Artifact showing rejection (not silent acceptance, not silent coercion) of: unsupported quantifier prefixes; malformed witnesses; witnesses outside `B`; and non-rational witness data. Include a negative test in which a rejected input would otherwise have been reported as a satisfied witness.

**End of LEDGER v1.**
