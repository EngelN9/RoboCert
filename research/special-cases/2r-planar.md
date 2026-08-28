# 2R planar family

Top of this file's lattice: `C_2R-planar-exact` — the Phase-1 benchmark
(`ROADMAP.md` §32, "First minimal viable theorem").

## C_2R-planar-exact.nominal

parent: none (root of this family)
extra_hypothesis: link lengths `L_1, L_2` fixed (no manufacturing tolerance); one
  circular obstacle; rectangular task region `T`; rectangular joint limits.
status: open
test_1_not_known: not found as an exact match in `research/literature/` — LIT-001
  (C-Iris) addresses convex C-space regions generally but not the exact/QE route for
  this small a system; no conflict.
test_2_retains_difficulty: retains quantifier alternation
  (`forall x in T, exists q`), exact rationalized kinematics, and the joint
  singularity-margin requirement — the three hardest features of the general Phase-1
  target. Does not yet retain uncertainty (see child node below).
test_3_hypothesis_dependence: not yet applicable — no proof exists yet at this node.
claims: [RC-001]

## C_2R-planar-exact.interval-uncertainty

parent: C_2R-planar-exact.nominal
extra_hypothesis: relaxes the nominal-length assumption — link lengths
  `L_i in [L_i^-, L_i^+]` (interval uncertainty), i.e. the actual Phase-1 target
  theorem in full (`ROADMAP.md` §1.2).
status: open
test_1_not_known: not found in `research/literature/`.
test_2_retains_difficulty: adds robust quantification `forall theta in Theta` on
  top of the nominal node's difficulties — this is the node RC-001 is actually
  about.
test_3_hypothesis_dependence: pending — to be filled in once RC-001 reaches `E1`
  and a full soundness argument exists to inspect.
claims: [RC-001]
