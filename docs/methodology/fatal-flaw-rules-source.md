# Professional Rules for Handling Fatal Flaws in AI-Reviewed and Formally Verified Mathematical Proofs

At a professional level, the right standard is not “several AIs agreed and several proof assistants accepted it.” The right standard is **traceable mathematical validity across the entire chain from intended meaning to kernel-checked proof**.

A robust policy should distinguish four objects that are often conflated:

$$
\text{intended theorem}
\;\longrightarrow\;
\text{mathematical specification}
\;\longrightarrow\;
\text{formal statement}
\;\longrightarrow\;
\text{formal proof}.
$$

A defect in any arrow can invalidate the overall result even if the final formal proof is perfectly kernel-checked.

## Professional Validation Rules

1. **Treat the theorem statement as an object of verification, not merely the proof.**  
   Before checking a proof, establish exactly what proposition is being asserted. Record all quantifiers, hypotheses, ambient categories, regularity assumptions, finiteness assumptions, choice principles, set-theoretic foundations, universe restrictions, and conventions. In serious mathematics, “the theorem” is not just the displayed sentence; it includes the mathematical environment in which that sentence is interpreted.

2. **Maintain a canonical specification independent of any proof assistant.**  
   Write a mathematically precise reference statement in ordinary mathematical language or a neutral specification language. Lean, Isabelle, and Rocq encodings should be checked against this canonical specification. Otherwise, all three systems can faithfully prove the same mistranslation.

3. **Separate theorem validation from proof verification.**  
   Verification asks

   $$
   \Gamma\vdash T?
   $$

   Validation asks

   $$
   T = T_{\text{intended}}?
   $$

   The first can be automated extremely well. The second is partly semantic and must be audited separately. A kernel can certify that $T$ follows from $\Gamma$; it cannot certify that $T$ expresses the theorem you had in mind.

4. **A successful formal proof is conditional on its assumptions.**  
   The mathematically relevant object is never merely

   $$
   \vdash T.
   $$

   It is

   $$
   \Gamma\vdash T.
   $$

   Therefore, every theorem audit must include an explicit inventory of $\Gamma$. Hidden structure assumptions, typeclass instances, local axioms, imported propositions, coercions, classical choice, quotient constructions, extensionality principles, and auxiliary lemmas all belong to the effective hypothesis set.

5. **Audit for assumption leakage.**  
   Determine whether the hypotheses already imply the conclusion, directly or indirectly. A common formalization failure has the shape

   $$
   H_1,\ldots,H_n \vdash C
   $$

   where one $H_i$, perhaps through a definition or imported structure, is stronger than intended and contains essentially $C$. The formal proof is then valid but mathematically uninformative.

6. **Audit definitions before auditing proofs.**  
   A theorem can be formally valid and conceptually wrong because a definition is wrong. Definitions of continuity, genericity, independence, nonsingularity, admissibility, equivalence, stability, or other domain-specific concepts must therefore be independently checked. In formal mathematics, an incorrect definition is often more dangerous than an incorrect lemma because every downstream theorem may remain internally consistent.

7. **Demand bidirectional specification tests when possible.**  
   For an important definition $D_{\mathrm{formal}}$, prove or test that it agrees with the accepted mathematical notion $D_{\mathrm{math}}$. Ideally establish an equivalence

   $$
   D_{\mathrm{formal}}(x)\iff D_{\mathrm{math}}(x)
   $$

   on representative classes of examples. At minimum, verify positive examples, negative examples, degenerate cases, and boundary cases.

8. **Attempt falsification before accepting verification.**  
   Search actively for counterexamples. This should occur both informally and computationally when appropriate. Small finite models, extremal examples, degenerate cases, low-dimensional cases, characteristic $p$ examples, singular examples, empty objects, zero objects, disconnected spaces, pathological topologies, and non-Noetherian examples often expose omitted assumptions. A theorem that survives adversarial falsification is more credible than one that has merely accumulated approving reviews.

9. **Localize every flaw.**  
   When a fatal defect is found, do not say merely “the proof is wrong.” Identify the minimal failed proposition

   $$
   A\Rightarrow B
   $$

   used at step $k$, the violated hypothesis, or the counterexample $x$ for which the claimed implication fails. This localization determines whether the defect is expositional, local, structural, or theorem-fatal.

10. **Distinguish proof failure from theorem failure.**  
    If a proof contains an invalid inference but the theorem may still be true, classify the result as “proof invalid; theorem status unresolved.” If a counterexample to the theorem exists, classify it as “theorem false.” These are materially different outcomes and must never be conflated.

11. **Do not repair a proof before determining whether the theorem itself survives.**  
    Patching an invalid line can obscure the real issue. First ask whether the statement remains true under the original hypotheses. If not, determine the weakest natural additional hypothesis or strongest valid weakened conclusion.

12. **Treat AI agreement as correlated evidence, not independent proof.**  
    ChatGPT, Claude, Gemini, or other models may share training data, proof conventions, common mathematical sources, and similar failure modes. Their outputs are therefore not statistically independent reviews. Agreement among them should not be interpreted as multiplying confidence in the same way as genuinely independent derivations.

13. **Use heterogeneous AI roles rather than repeated approval prompts.**  
    One model should attempt to prove the theorem; another should attempt to refute it; another should search for hidden assumptions; another should compare the informal and formal statements; another should inspect definitions; and another should generate edge cases. Asking five systems “Is this proof correct?” creates confirmation pressure. Assigning adversarial roles is much stronger.

14. **Do not allow AI reviewers to inherit the same proof unless necessary.**  
    If every reviewer sees the original proof, they may reproduce its conceptual framing. A stronger protocol asks one reviewer to derive the theorem independently from the statement alone. Agreement between independent derivations is more informative than agreement between critiques of the same derivation.

15. **Require explicit uncertainty from AI systems.**  
    An AI review should distinguish “checked,” “not checked,” “plausible,” “depends on lemma $L$,” and “requires external verification.” A response that simply says “the proof is correct” without exposing what was actually examined has low evidentiary value.

16. **Never treat natural-language chain-of-thought as a proof certificate.**  
    AI-generated explanations are heuristic artifacts. The mathematically relevant objects are the explicit proof, formal derivation, cited lemmas, executable certificates, or kernel-checkable proof terms. Eloquence is not evidence.

17. **Trace every nontrivial external claim.**  
    If an AI invokes a theorem, verify its exact statement, hypotheses, source, and applicability. A frequent mathematical failure is citing a true theorem in a setting where one hypothesis is missing.

18. **Formalize the statement independently before formalizing the proof.**  
    Ideally, one person or system writes the formal theorem statement from the mathematical specification, and another develops the proof. This reduces the risk of modifying the statement unconsciously to make the proof go through.

19. **For high-stakes results, use independent formalizations rather than mechanical translations.**  
    A Lean proof mechanically ported to Rocq and Isabelle is not three independent validations. Stronger evidence comes from separately constructed encodings using each system's native libraries and mathematical abstractions.

20. **Compare formal statements semantically, not syntactically.**  
    Lean, Isabelle, and Rocq may encode the same concept differently. What matters is whether the encoded propositions are mathematically equivalent. Where feasible, construct a translation argument or a shared test suite of models.

21. **Audit the trusted computing base.**  
    Record the proof assistant, version, kernel version where relevant, library versions, plugins, code generators, external solvers, compiler assumptions, and imported axioms. Formal correctness is always relative to a trusted base.

22. **Eliminate or explicitly declare proof escape mechanisms.**  
    In Lean, audit for `sorry`, custom axioms, untrusted metaprogramming pathways, and theorem imports whose trust status is unclear. In Rocq, inspect `Admitted`, axioms, opaque assumptions, plugins, and external tactics. In Isabelle, inspect oracles, axiomatizations, `sorry`, and external prover integration. The presence of such mechanisms does not automatically make a development worthless, but it changes the claim from “fully verified” to “verified conditional on these assumptions.”

23. **Ask the system what axioms the final theorem depends on.**  
    This is often more informative than reading the final proof. The relevant question is not only whether the theorem compiles, but what foundational principles or user-introduced axioms occur in its dependency closure.

24. **Distinguish tactic success from kernel acceptance.**  
    Tactics are proof search mechanisms. The high-confidence endpoint is a proof object accepted by the trusted kernel. External SMT, SAT, CAS, or automated theorem provers should ideally return a certificate that the trusted system verifies, rather than merely a Boolean “valid.”

25. **Do not overstate what multiple proof assistants establish.**  
    Lean, Isabelle, and Rocq are powerful evidence against implementation-specific bugs, but they do not automatically provide foundational independence. They may use related logical foundations, shared mathematical ideas, common libraries, similar encodings, or imported computational results.

26. **Preserve a reproducible frozen artifact.**  
    For every significant theorem, archive the source, dependency lockfiles, compiler/prover versions, build commands, theorem statement, assumptions, hashes, and generated certificates. A result that cannot later be reproduced has weaker audit value.

27. **A discovered fatal flaw freezes the acceptance status immediately.**  
    Once a credible fatal objection appears, the correct status is not “probably still correct because three systems checked it.” The result becomes “under investigation” until the objection is resolved.

28. **Try to formalize the objection.**  
    If someone claims that a step is invalid, encode the disputed claim itself. If the theorem is allegedly false, formalize the counterexample. Formalizing the refutation is often the fastest way to determine whether the disagreement is mathematical or semantic.

29. **If a counterexample exists to the intended theorem, retract the theorem claim.**  
    No amount of AI consensus or formal proof of a differently encoded proposition overrides a genuine counterexample. A single valid counterexample settles a universal theorem:

    $$
    \exists x\,[P(x)\land\neg Q(x)]
    \quad\Longrightarrow\quad
    \neg\forall x\,[P(x)\Rightarrow Q(x)].
    $$

30. **If the counterexample also satisfies the formal hypotheses, compare it directly with the formal theorem.**  
    Encode the object $x$, prove the formal version of $P(x)$, and prove $\neg Q(x)$. If the original formal theorem proves $Q(x)$, you now have a concrete inconsistency to diagnose.

31. **If both $T$ and $\neg T$ are kernel-checkable in the same environment, escalate immediately.**  
    Under a consistent logic and sound trusted kernel, this should not happen. Investigate imported axioms, inconsistent user axioms, definitional mistakes, proof-assistant bugs, unsafe extensions, build corruption, mismatched environments, or misinterpretation of what was actually checked.

32. **Do not infer a kernel bug until simpler explanations have been exhausted.**  
    In practice, specification mismatch, inconsistent axioms, different namespaces, theorem shadowing, imported assumptions, or different environments are vastly more common than a soundness bug in a mature kernel.

33. **Classify the severity of the flaw.**  
    A useful professional taxonomy is:

    $$
    \text{expositional}
    <\text{local proof gap}
    <\text{missing hypothesis}
    <\text{definition defect}
    <\text{statement mismatch}
    <\text{false theorem}
    <\text{trusted-base inconsistency}.
    $$

    The response should be proportional to the severity.

34. **Repair at the earliest defective layer.**  
    If the issue is a definition, do not merely patch the theorem. If the issue is the theorem statement, do not merely patch the proof. If the issue is an imported lemma, repair that dependency and revalidate everything downstream.

35. **After any structural repair, invalidate downstream certification until rechecked.**  
    Changing a definition or major hypothesis can affect every dependent theorem. All downstream results should be rebuilt and, for important claims, re-audited.

36. **Record the defect history.**  
    Keep the original claim, the discovered flaw, the diagnosis, the corrected formulation, and the new verification results. Silent replacement is bad scientific practice because it destroys provenance.

37. **Publish corrections proportionally to the original dissemination.**  
    If the result appeared in a preprint, repository, thesis, paper, talk, or software release, update the same channels. State whether the theorem was false, the proof was incomplete, the formal statement differed from the intended theorem, or the trusted assumptions changed.

38. **Do not conceal the existence of a serious previous flaw.**  
    A corrected proof is stronger when accompanied by a transparent account of what failed and why the new argument avoids that failure.

39. **For research-level claims, require at least one genuinely adversarial human review.**  
    Formal verification is exceptionally strong evidence, but mathematical judgment is still required for interpretation, relevance, specification, and novelty. A reviewer should explicitly attempt to break the theorem rather than merely confirm it.

40. **For extraordinary claims, require stronger independence.**  
    If the theorem is surprising, resolves a major open problem, contradicts accepted expectations, or depends on unusual foundations, raise the evidentiary threshold. Require independent reconstructions, alternative proofs where possible, expert domain review, and independent formalization.

## Confidence Model

The overarching rule is

$$
\boxed{
\text{Confidence in a theorem}
\neq
\text{number of systems that said “correct”.}
}
$$

A more defensible model is

$$
\boxed{
\text{Confidence}
=
\text{statement validity}
\times
\text{proof validity}
\times
\text{formalization fidelity}
\times
\text{trusted-base integrity}
\times
\text{independence of review}.
}
$$

This multiplicative viewpoint matters. If formalization fidelity is effectively zero because the formal theorem is not the intended theorem, then perfect kernel verification does not rescue the original claim.

## What Should Be Required Before Calling a Theorem “Formally Verified”?

A strong standard is:

$$
\begin{aligned}
&\text{intended mathematical statement independently specified},\\
&\Downarrow\\
&\text{formal statement independently checked against it},\\
&\Downarrow\\
&\text{definitions tested against intended semantics},\\
&\Downarrow\\
&\text{proof kernel-checked without undeclared gaps},\\
&\Downarrow\\
&\text{axiom/dependency closure audited},\\
&\Downarrow\\
&\text{counterexample search performed},\\
&\Downarrow\\
&\text{independent mathematical review performed},\\
&\Downarrow\\
&\text{reproducible build archived}.
\end{aligned}
$$

For a particularly important result, add

$$
\text{independent second formalization}
$$

and preferably

$$
\text{independent proof strategy}.
$$

## Recommended Four-Status System

Instead of using only “correct/incorrect,” professional work should distinguish:

### 1. Verified

The exact formal proposition has been kernel-checked under an audited assumption set.

### 2. Validated

There is strong evidence that the formal proposition faithfully represents the intended mathematical theorem.

### 3. Independently Replicated

Another investigator or formal development reconstructed the result without simply reusing the original proof path.

### 4. Mathematically Accepted

The theorem has survived specification audit, proof audit, adversarial review, and relevant mathematical scrutiny.

These are different claims. A result can be formally verified without yet being fully validated.

## Final Principles

The deepest principle is:

$$
\boxed{
\text{A proof assistant proves propositions, not intentions.}
}
$$

And for AI:

$$
\boxed{
\text{An AI reviewer provides evidence, not mathematical authority.}
}
$$

For professional research, the target should therefore be:

**independent specification + adversarial mathematical review + audited kernel verification + reproducibility**

rather than simple agreement among multiple AIs and formal systems.
