(** * Planar-2R exact polynomial identities

    Rocq's assignment in this phase, per [formal/README.md], is exact polynomial identities,
    Positivstellensatz/SOS-style certificates, real-closed-field reasoning, and validated
    interval arithmetic. This first file covers only the first: the identities the
    RC-005 adversary run in [research/notes/2026-08-28-rc005-adversary-search.md] turned out
    to be exactly what rules out an unsoundness in the generic point-to-segment [Seg]
    construct. Nothing else is attempted here.

    These are statements about a MODEL, not a physical robot. See [formal/README.md].

    Everything is over [Q] (exact rationals), matching [src/robocert/specification.py]'s
    exact-rational semantics -- no [R], no [Qc]/normalized-rational reasoning is needed for
    these particular identities, only the field axioms [ring] already has.
*)

Require Import Coq.QArith.QArith.
Require Import Coq.QArith.Qring.

Open Scope Q_scope.

(** ** Half-angle substitution quantities

    [t_i = tan(q_i / 2)] on the principal chart. [D_i], [C_i], [S_i] are the standard
    tangent-half-angle numerators; [D_i = 1 + t_i^2] is the substitution's shared
    denominator, [C_i = cos q_i * D_i] and [S_i = sin q_i * D_i] are its numerators. *)

Definition D (t : Q) : Q := 1 + t * t.
Definition C (t : Q) : Q := 1 - t * t.
Definition S (t : Q) : Q := 2 * t.

(** *** Lemma: the Pythagorean identity survives homogenization.

    [C_i^2 + S_i^2 = D_i^2] for every rational [t], with no side condition. This is the
    algebraic fact underlying [cos^2 + sin^2 = 1] after clearing the [D_i] denominator; the
    proof is a single [ring] call because it is a polynomial identity, not a trigonometric
    fact requiring [R]. *)

Lemma pythagorean_identity : forall t : Q,
  C t * C t + S t * S t == D t * D t.
Proof.
  intro t. unfold C, S, D. ring.
Qed.

(** ** Nondegeneracy of the two encoded segments

    [research/proofs/planar-2r-pose-tolerance-witness-proof-rc005.md] section 2 defines
    homogeneous endpoint numerators [A] and [B - A] whose squared norms are, as exact
    identities:

      Q1 = ||A||^2      = L1^2 * D1^2 * D2^2
      Q2 = ||B - A||^2  = L2^2 * D1^2 * D2^2

    where [D = D1 * D2]. This file states and proves those two identities directly in terms
    of [D1], [D2], and the link lengths, rather than re-deriving [A]/[B] from the angle-sum
    formulas -- the angle-sum step is orthogonal to what these identities are for.

    Their value: three mutually isolated [adversary] agents (Phase 0.5, RC-005 attack
    session) independently found that the generic point-to-segment [Seg] construct is
    UNSOUND at [Q_ = 0] -- branch III of [Seg] fires vacuously and reports clearance
    regardless of the true distance. RC-005 is safe only because [Q1 = L1^2 * D^2] and
    [Q2 = L2^2 * D^2] with [D >= 1], so nonzero link lengths force [Q_ > 0]. That safety
    argument rests on an algebraic identity that had never been mechanically checked before
    this file. It is now a Rocq theorem instead of an informal claim in a proof note.

    The two zero-implies-length-zero corollaries below restate the multiplied-out identity
    directly (not via [rewrite] on the [ring] lemmas above) and are proved using only
    [Qmult_integral] -- [Q]'s zero-divisor-free property -- applied repeatedly, to keep the
    proof independent of any less-standard QArith lemma name. *)

Lemma segment1_nondegenerate_identity : forall (L1 D1 D2 : Q),
  L1 * L1 * (D1 * D1) * (D2 * D2) == L1 * L1 * ((D1 * D2) * (D1 * D2)).
Proof.
  intros L1 D1 D2. ring.
Qed.

Lemma segment2_nondegenerate_identity : forall (L2 D1 D2 : Q),
  L2 * L2 * (D1 * D1) * (D2 * D2) == L2 * L2 * ((D1 * D2) * (D1 * D2)).
Proof.
  intros L2 D1 D2. ring.
Qed.

(** *** Corollary: [Q_ = 0] on an encoded segment forces the corresponding link length to
    be zero.

    This is the direction that actually matters for soundness: it is the contrapositive of
    "[L <> 0] implies [Q_ <> 0]", proved directly from the identity above plus [Q]'s
    integral-domain structure ([Qmult_integral]), without importing any order theory. *)

Lemma segment1_zero_implies_length_zero : forall (L1 D1 D2 : Q),
  D1 <> 0 -> D2 <> 0 ->
  L1 * L1 * (D1 * D1) * (D2 * D2) == 0 ->
  L1 == 0.
Proof.
  intros L1 D1 D2 hD1 hD2 hzero.
  destruct (Qmult_integral _ _ hzero) as [hLD1 | hD2sq].
  - destruct (Qmult_integral _ _ hLD1) as [hLsq | hD1sq].
    + destruct (Qmult_integral _ _ hLsq) as [h | h]; exact h.
    + exfalso. destruct (Qmult_integral _ _ hD1sq) as [h | h]; apply hD1; exact h.
  - exfalso. destruct (Qmult_integral _ _ hD2sq) as [h | h]; apply hD2; exact h.
Qed.

Lemma segment2_zero_implies_length_zero : forall (L2 D1 D2 : Q),
  D1 <> 0 -> D2 <> 0 ->
  L2 * L2 * (D1 * D1) * (D2 * D2) == 0 ->
  L2 == 0.
Proof.
  intros L2 D1 D2 hD1 hD2 hzero.
  destruct (Qmult_integral _ _ hzero) as [hLD1 | hD2sq].
  - destruct (Qmult_integral _ _ hLD1) as [hLsq | hD1sq].
    + destruct (Qmult_integral _ _ hLsq) as [h | h]; exact h.
    + exfalso. destruct (Qmult_integral _ _ hD1sq) as [h | h]; apply hD1; exact h.
  - exfalso. destruct (Qmult_integral _ _ hD2sq) as [h | h]; apply hD2; exact h.
Qed.

(** ** Scope, restated

    These lemmas establish algebraic identities in [Q] only. They do NOT establish:
    - that [src/robocert/kinematics2r.py] or the proposed pose-tolerance builder implement
      these formulas correctly (an implementation-correspondence obligation, open per
      RC-005 section 9);
    - anything about the [Seg] construct's three-branch case analysis, which is a Rocq
      statement for a later phase, not this file;
    - anything about a physical robot.

    RC-005 remains at tier E0 in [research/CLAIMS.md]. Nothing in this file promotes it;
    promotion requires a project-owner E1 read and the [referee] skill's hostile+naive
    protocol, per [research/README.md]. *)
