# Kill-test instance D

Date: 2026-10-01. This note does [`first-target.md`](first-target.md) §5 step 4. It fixes
the inputs of the §6 kill test for one real SCARA arm and one real tray footprint, under
the modelling choices O1–O6 in [`modelling-choices.md`](modelling-choices.md) and the
freeze in [`revised-direction.md`](revised-direction.md).

**Status.**
- E0 planning record. Each input is marked **datasheet** or **assumption**.
- Nothing here is evaluated. Φ_D has not been computed; no witness or counterexample has
  been searched for; and no estimate is made of whether (ε_req, μ_req) survives. The
  instance status is `UNKNOWN`.
- These inputs await owner approval (§6, rule 1). Steps 5 and 6 have not started.
- Hypothesis H2 (the physical cell matches the model) remains an external assumption that
  no certificate checks.
- This note changes no ledger tier, registers no checker, and changes neither RC-002 nor
  `src/`.

## 1. Units, frames and arithmetic

- **Lengths** are in millimetres and **angles** in radians unless marked °. Every
  serialized value is an exact rational. Decimals below are exact decimal fractions, so
  27.93 means 2793/100. Values marked ≈ are illustration only and are not inputs.
- **Model frame W** (`AGENTS.md` §7.1):
  - The origin is on the Joint #1 axis, in the plane of the links.
  - The x-axis points along the centre of the Joint #1 motion range; the y-axis is
    90° counter-clockwise from it.
  - q₁ is measured from the x-axis, counter-clockwise positive. q₂ = 0 when Arm #2 is in
    line with Arm #1.
  - The tool point is the Joint #3/#4 shaft axis, with no tool offset (an assumption,
    A9 in §4).
- **Map from Epson's joint frame to W.**
  - Epson defines the J1 zero pulse as "the position where Arm #1 faces toward the
    positive (+) direction on the X-coordinate axis". Its J1 pulse range,
    −152918 to 808278, is not symmetric about zero. The midpoint of that range lies about
    90° counter-clockwise from Epson +X.
  - W therefore takes x_W = Epson +Y, which gives q₁ = θ₁,Epson − 90°. This offset is
    *inferred* from the pulse table. It has not been read from a stated frame drawing
    (assumption A1).
  - Epson's J2 zero is "the position where Arm #2 is in-line with Arm #1", the same as the
    model's q₂ = 0, so no J2 offset is needed.
  - Counter-clockwise is positive in both frames.
- **Out-of-plane geometry.** The model is planar (`first-target.md` §3.6). An object is an
  obstacle only if its plan-view projection reaches the height of the links (A6).

## 2. Choice of arm

**Epson LS6-B602**, a tabletop SCARA with 325 + 275 mm arms (600 mm reach).

Why this arm:
- It is a current-generation SCARA of the class that precision pick-and-place cells
  use.
- Its manipulator manual is public and carries a revision code. That manual gives per-joint
  motion ranges, pulse ranges and resolution in its text. Many vendor brochures give only
  reach and repeatability.
- An independent product sheet repeats the key values, so each datasheet value below was
  read from two documents.

Choosing this arm is a planning choice. It is not a claim about how often the arm is
used.

**Sources** (both fetched 2026-10-01 through the Firecrawl connector, since direct egress
to the Epson hosts is blocked from the working environment):

| Ref | Document | Revision | URL |
|---|---|---|---|
| E1 | Seiko Epson, *SCARA ROBOT LS3-B/LS6-B series MANIPULATOR MANUAL* | Rev.7, EM208R4429F | <https://files.support.epson.com/far/docs/epson_ls3-b_&_ls6-b_robot_manual_(r7).pdf> |
| E2 | Epson America, *LS6-B SCARA Robot* product specifications | CPD-57403 9/19 | <https://files.support.epson.com/far/docs/ls6-b_scara_robot_product_specifications_cpd-57403.pdf> |

Locators are given by section and table. The page numbers printed in E1 could not be
attributed unambiguously from the text extraction, so this note does not cite them.

**Repeatability is not accuracy.**
- E1 §2.4 and E2 both give a J1+J2 repeatability of ±0.02 mm.
- Repeatability bounds the scatter of repeated returns to a taught point. It says nothing
  about the error between the controller's kinematic model and the physical arm.
- Neither document gives an absolute-accuracy figure or a link-length tolerance. A text
  query over E1 found no absolute-accuracy statement.
- Repeatability is therefore **not** used for δ or for the β₂ bound. Both are assumptions
  (§3.1, §3.4).
- Every vendor value below is also an assumption to verify against the delivered unit
  and its calibration report.

## 3. Inputs

### 3.1 Link lengths and tolerance box Δ

| Symbol | Exact value | Units | Source type | Locator, or reason and replacement |
|---|---|---|---|---|
| L̄₁ | 325 | mm | datasheet | E1 §2.4 Specifications, row "Arm length / Arm #1", column LS6-B602\*. The arm-length total of 600 mm is repeated in E2, row "Arm Length, Joint #1 + Joint #2", column LS6-B60x. |
| L̄₂ | 275 | mm | datasheet | E1 §2.4, row "Arm length / Arm #2" (the LS6-B column). E1 §4.3.1 also uses "L₂ = 275" in its LS6-B worked example. |
| δ₁ = δ₂ = δ | 1/10, split as δ_mfg = 1/20 plus δ_cal = 1/20 | mm | **assumption** (A2) | Neither source publishes a link-length tolerance or an accuracy figure. This is a stress value equal to five times the stated repeatability. It is chosen, not sourced. **Replace with:** the delivered unit's calibration report, or a laser-tracker identification of the effective L₁ and L₂ with their uncertainty. |

So Δ = [3249/10, 3251/10] × [2749/10, 2751/10] mm.

### 3.2 Joint domain Q, target set R, placement tolerance ρ

**Joint limits** are taken from E1 §2.4, row "Max. operating range". E1 §5.1.1–5.1.2
("Max. Motion Range") and E2 ("Max. Motion Range") agree.

| Joint | Datasheet range | Pulse range (E1 §5.1) | Resolution (E1 §2.4) |
|---|---|---|---|
| J1 | ±132° | −152918 to 808278 pulse | 0.000275 °/pulse |
| J2 | ±150° | ±341334 pulse | 0.000439 °/pulse |

Under H1, these limits are rounded **inward** to rational half-angle bounds, which is sound
for the commanded-coordinate domain of an existential witness. Each rounding is
checked by an exact rational inequality.

| Symbol | Exact value | Source type | Check (exact) |
|---|---|---|---|
| t₂± | ±37/10 | datasheet, rounded inward | tan 75° = 2 + √3, and 37/10 − 2 = 17/10 < √3 because 289/100 < 3. The commanded limit is 2·atan(37/10) ≈ 149.75°. |
| t₁± | ±11/5 | datasheet, rounded inward, which leaves about 0.9° of slack for the inferred frame offset A1 | We need 2·atan(11/5) ≤ 132° = 11π/15, which holds if and only if atan(5/11) ≥ 2π/15. Since atan x ≥ x − x³/3 for x > 0, atan(5/11) ≥ 1690/3993. Since π < 22/7, 2π/15 < 44/105. Finally 1690·105 = 177450 > 44·3993 = 175692. The commanded limit is 2·atan(11/5) ≈ 131.1°. |

So T = [−11/5, 11/5] × [−37/10, 37/10] in half-angle coordinates.

**Tray.** Use a JEDEC CS-004, variant AD, QFP matrix tray for 28 mm square bodies.

- **Source T1:** TopLine, *QFP, LQFP, TQFP IC Matrix Trays Conform to JEDEC Standards*.
  It is one sheet of the 12-page drawing set
  <https://topline.tv/drawings/pdf/trays/Tray_JEDEC_Matrix_IC_Tray_ALL.pdf>, fetched
  2026-10-01. Two independent extractions gave the same row.
- **Revision:** none printed in the extracted text. This is a reseller drawing of a JEDEC
  outline.
- **Replace with:** JEDEC Publication 95, outline CS-004 (login-gated, not fetched). Also
  check against the delivered tray lot's drawing.

| Field (T1 column) | Value | Units | Source type |
|---|---|---|---|
| Columns N1, rows N2, cells N3 | 3, 8, 24 | — | datasheet |
| M "From Corner (+X)" | 3093/100 | mm | datasheet |
| M1 "From Corner (−Y)" | 2793/100 | mm | datasheet |
| M2 "−Y step" | 3702/100 | mm | datasheet |
| M3 "+X Step" | 3702/100 | mm | datasheet |
| Datum | the tray corner from which +X and −Y are measured, read as the upper-left corner | — | datasheet column headers; the corner's identity in the drawing image is not text-extractable (A3) |

Why this tray:
- It is a real footprint with an internally consistent row: N1·N2 = N3.
- Its 24 pockets keep the finite conjunction over P small for step 5.
- A finer tray, for example TQFP CS-007 AE with 90 pockets, would be equally real but
  costlier. It was not chosen to make the claim easier: the pocket set is used complete,
  with no rectangle enclosing it.

**Tray pose (assumption A4).**
- The tray corner datum sits at W-coordinates (300, 315/2).
- The tray axes are parallel to W: tray +X = W +x, and tray −Y = W −y.
- The pose centres the pocket rows laterally about the x-axis, in front of the base. It
  was fixed before any evaluation and was not tuned.
- **Replace with:** the integrator's cell layout drawing.

**Pick set P** is the 24 pocket centres:

$$
P=\{(300+\tfrac{3093}{100}+\tfrac{3702}{100}i,\ \tfrac{315}{2}-\tfrac{2793}{100}-\tfrac{3702}{100}j) : i=0,1,2;\ j=0,\dots,7\}
$$

Written out:
- x ∈ {33093/100, 7359/20, 40497/100}
- y ∈ {±12957/100, ±1851/20, ±5553/100, ±1851/100}

| Symbol | Exact value | Units | Source type | Reason and replacement |
|---|---|---|---|---|
| ρ | 1/2 | mm | **assumption** (A5) | This lumps the positional tolerance of the tray pockets with the location of the tray nest relative to the robot base. T1 gives no positional tolerance for the pockets. **Replace with:** the JEDEC CS-004 pocket-position tolerance plus a tolerance stack-up of the tray-nest fixture drawing. |

So R = P ⊕ B̄(0, 1/2), which is O4.

### 3.3 Obstacles O, link radius r, available clearance

Assumption A6 applies to every obstacle: each one rises to the height of the links, so its
plan-view projection is the obstacle. Its rational vertices are counter-clockwise in W.
**Replace the whole layout with:** the integrator's cell CAD, projected to the link plane,
with a recorded containment direction (`AGENTS.md` §4.6, outer-conservative).

| Obstacle | Vertices (mm) | Represents |
|---|---|---|
| O₁ | (328, 231), (408, 231), (408, 311), (328, 311) | An 80 × 80 mm feeder housing beside the tray, on the +y side |
| O₂ | (340, −271), (380, −271), (380, −231), (340, −231) | A 40 × 40 mm camera or lighting post, on the −y side |

**Layout rule (A7).** Each obstacle edge facing the tray was placed at least 100 mm from the
nearest target disc of R. This round figure exceeds r + μ_req, so a tool disc cannot meet an
obstacle *at a target itself*. That rule only excludes a layout that is trivially
inconsistent. It does not assess whether the links clear the obstacles in any configuration;
that is step 5.

**Available clearance between obstacle and target**, as a property of the stated layout:
- O₁: 231 − 12957/100 − 1/2 = 10093/100 mm.
- O₂: the same, by symmetry.

These are gaps between obstacles and target discs, not link clearances.

| Symbol | Exact value | Units | Source type | Reason and replacement |
|---|---|---|---|---|
| r | 60 | mm | **assumption** (A8) | E1 §3.3 *Mounting Dimensions* says: "The maximum space (R) includes the radius of the end effector. If it exceeds 60 mm, define the radius as the distance to the outer edge of maximum space." Epson's drawn envelope therefore assumes a tool radius of at most 60 mm. The same r is used as the half-width of both links (O6). The arm housings' widths appear only in the E1 §2.3.2 outer-dimension drawing, which is not text-extractable. **Replace with:** the larger of (a) half the width of each link housing in plan view, read from E1 §2.3.2, and (b) the actual end-effector radius. Both must be outer bounds. |

### 3.4 Requirement (ε_req, μ_req) and the O3 offset bound

**Velocity amplification (A10).**
- The integrator requirement is σ_min(J_L(θ)) ≥ S with S = 50 mm per rad.
- Equivalently, at every target a tool speed v needs joint speeds of at most v/S, so the
  tolerable amplification is A_max = 1/50 rad/mm.
- Reason: below S the arm moves the tool less than 50 mm per radian of joint motion in
  its weakest direction. That is under a fifth of either link length.
- This value is chosen, not sourced.
- **Replace with:** the integrator's tolerable amplification, derived from the cycle-time
  budget and the joint-speed limits.

**Derivation of ε_req.** This is an unrefereed input derivation, not a ledger claim.

For planar 2R, as `first-target.md` §3.2 states,

$$
\det J_L = L_1L_2\sin\theta_2, \qquad
\|J_L\|_F^2 = L_1^2 + 2L_2^2 + 2L_1L_2\cos\theta_2 \le (L_1+L_2)^2 + L_2^2.
$$

Since σ_min·σ_max = |det J_L| and σ_max ≤ ‖J_L‖_F,

$$
\sigma_{\min} \ge \frac{L_1L_2\,|\sin\theta_2|}{\sqrt{(L_1+L_2)^2+L_2^2}}.
$$

It is therefore sufficient, over all of Δ, that

$$
\sigma_B=|\sin\theta_2| \ \ge\ \frac{S\sqrt{(\bar L_1+\bar L_2+2\delta)^2+(\bar L_2+\delta)^2}}{(\bar L_1-\delta)(\bar L_2-\delta)},
$$

and ε_req = 37/100 meets this bound exactly. With m = (3249/10)(2749/10) = 8931501/100 and
N² = (6002/10)² + (2751/10)² = 8718401/20, check (37/100 · m)² ≥ 50² · N² exactly. It holds.
The next lower hundredth, 36/100, fails this check.

The bound σ_max ≤ ‖J‖_F is loose, so ε_req is *stronger* than A10 strictly needs. A
tighter derivation would lower it, which is open decision 4.

| Symbol | Exact value | Units | Source type | Reason and replacement |
|---|---|---|---|---|
| ε_req | 37/100 | dimensionless (σ_B, O2) | **assumption** (A10, through the exact derivation above) | Replace by repeating the derivation with the integrator's A_max and the replaced δ. |
| μ_req | 5 | mm | **assumption** (A11) | This is clearance beyond r, kept for unmodelled items such as cable and hose drape and variation between end effectors. It is chosen, not sourced. **Replace with:** the integrator's clearance specification. This is a layout requirement, not a safety distance (`first-target.md` §3.6). |
| U_β | u = tan(β₂/2) ∈ [−1/5000, 1/5000] | dimensionless | **assumption** (A12) | This is equivalent to \|β₂\| ≤ 2·atan(1/5000) ≈ 0.0229°, which is about 0.11 mm at the 275 mm Arm #2 tip, comparable to δ. Because the bound is stated directly on u, it needs no outward rounding. The J2 resolution of 0.000439 °/pulse (E1 §2.4) is a quantisation floor, about 52 pulses below this bound; it is not a calibration bound. **Replace with:** the residual J2 zero-offset uncertainty after the integrator's calibration routine (for example Epson's calibration procedure in the maintenance manual), stated as an angle and rounded *outward* to a rational bound on u. |

No base offset is included in the kill test, as O3 states in `modelling-choices.md`.

## 4. Assumptions register

| ID | Assumption | Why it is not sourced | What would replace it |
|---|---|---|---|
| A1 | x_W = Epson +Y, so q₁ = θ₁,Epson − 90° | Inferred from the asymmetric J1 pulse range; the E1 §5.4 motion-range drawing is not text-extractable | E1 §5.4 drawing read by a person, or the controller's joint-zero definition |
| A2 | δ = 1/10 mm per link, as manufacturing 1/20 plus calibration 1/20 | No link tolerance or accuracy figure is published | Calibration report or laser-tracker identification of the delivered unit |
| A3 | The tray datum is the upper-left corner, with +X along the 3-pocket rows | The column headers are text; the drawing image is not | A person reading T1, or JEDEC Pub. 95 CS-004 |
| A4 | Tray datum at (300, 315/2), axes parallel to W | No real cell exists | Integrator's layout drawing |
| A5 | ρ = 1/2 mm | No pocket position tolerance in T1; no nest drawing | JEDEC tolerance plus nest tolerance stack-up |
| A6 | O₁ and O₂ reach link height; the plan projection is exact | No real cell exists | Cell CAD, outer-conservative projection |
| A7 | Obstacle placement at least 100 mm from target discs | Layout design rule, chosen | Cell CAD |
| A8 | r = 60 mm for both links | Link widths appear only in a drawing image | E1 §2.3.2 widths and the real end effector, both outer bounds |
| A9 | Tool point on the shaft axis, no tool offset | No end effector specified | End-effector drawing; a tool offset changes the kinematics |
| A10 | S = 50 mm/rad, so A_max = 1/50 rad/mm | Integrator requirement not available | Integrator's tolerable amplification |
| A11 | μ_req = 5 mm | Integrator requirement not available | Integrator's clearance specification |
| A12 | \|u\| ≤ 1/5000 for β₂ | No published zero-offset accuracy | Post-calibration J2 zero uncertainty |

Every datasheet value is also subject to H2: it holds for the delivered unit only after
that unit is checked.

## 5. Open owner decisions before step 5

1. Approve or replace each of A1–A12, especially δ (A2), r (A8) and the obstacle layout
   (A4, A6, A7). These dominate whatever step 5 finds.
2. Approve the arm (Epson LS6-B602) and the tray (CS-004 AD, 24 pockets). Alternatively,
   choose a finer tray such as CS-007 AE with 90 pockets.
3. Decide whether a person should read the E1 §2.3.2 and §5.4 drawings, and the corner of
   T1, before step 5. That reading would turn A1, A3 and part of A8 into datasheet values.
4. Decide whether ε_req should come from the loose Frobenius bound used here or from a
   tighter σ_min bound. The tighter route needs its own argument, which would enter
   `research/CLAIMS.md` at E0 through `scripts/check_ledger.py` if it is relied on.
5. Decide whether the vendor sources E1, E2 and T1 should get `research/literature/`
   entries through the `cite` skill. That is open decision 3 in `revised-direction.md`.
   This note treats them as instance data to verify, not as literature claims.
