# The exact-witness polynomial encoding for the planar 2R arm

**A self-contained proof.**

---

## 0. Introduction and statement of results

A planar two-link revolute arm with link lengths $L_1,L_2$ is positioned by a pair of joint angles $q=(q_1,q_2)$. Three requirements are natural for a *certified witness* configuration: the tool must reach a prescribed point $P^\star$; both links must stay clear of a disc-shaped obstacle by a prescribed margin; and the arm must be quantitatively far from a kinematic singularity. Call these conditions (a), (b), (c), and call $q$ **admissible** when all three hold.

The conditions are transcendental in $q$. This document proves that they are exactly equivalent — not approximately, not generically, and with no sampling or numerical step anywhere — to a system of polynomial equations and inequalities in two real unknowns $(t_1,t_2)$, obtained through the half-angle substitution $q_i=2\arctan t_i$.

Two things make such a statement delicate. First, the half-angle chart is a bijection onto the *open* square $(-\pi,\pi)^2$, not onto the configuration torus $\mathbb T:=(\mathbb R/2\pi\mathbb Z)^2$; whether that loss is real or repairable is a mathematical question, not a bookkeeping one. Second, the encoding of the clearance condition for the second link replaces the tool point $P(q)$, which depends on $q_2$, by the *constant* $P^\star$; this substitution is licensed only where (a) already holds, so the resulting predicate has no standalone meaning and the equivalence proof must be staged to avoid circularity.

Both issues are settled below. Write $\Theta(t_1,t_2):=(2\arctan t_1,\,2\arctan t_2)$ and let $\Phi$ be the semialgebraic predicate of Definition 10.1.

> **Theorem A (exact equivalence on the chart; Theorem 10.2).** For every $(t_1,t_2)\in\mathbb R^2$,
> $$\Phi(t_1,t_2)\iff\Theta(t_1,t_2)\text{ is admissible.}$$

> **Theorem B (soundness; Corollary 11.1).** Every real solution of $\Phi$ yields an admissible configuration.

> **Theorem C (relative completeness; Corollaries 11.2–11.3).** $\Theta$ restricts to a bijection from the solution set of $\Phi$ onto the set of admissible $q\in(-\pi,\pi)^2$; a box restriction on $(t_1,t_2)$ corresponds to a closed rectangle of configurations.

> **Theorem D (the chart loss is real; Theorem 12.1).** There are rational data satisfying all standing hypotheses for which an admissible $q\in\mathbb T$ exists although $\Phi$ has no real solution. Hence $\Phi$ is sound but **not** complete on the torus, and "$\Phi$ unsatisfiable" does not by itself certify infeasibility.

> **Theorem E (the loss is repairable; Theorem 13.5).** Let $\Phi_{\lambda_1,\lambda_2}$ denote $\Phi$ built with $(L_1,L_2)$ replaced by $(\lambda_1,\lambda_2)$. An admissible $q\in\mathbb T$ exists **iff** at least one of the four predicates $\Phi_{\pm L_1,\pm L_2}$ has a real solution. The four differ from $\Phi$ by signs only.

> **Theorem F (exact stability of the case split; §14).** The three-way point-to-segment case split uses overlapping, non-strict selectors. Soundness survives *every* tightening of these selectors (Theorem 14.2); completeness survives a tightening iff the tightened selectors still cover $\mathbb R$ (Theorem 14.3), and Theorem 14.4 determines exactly which tightenings do. Theorem 14.6 computes, in closed form, the exact set of parameters at which a non-covering family fails; contrary to what a dimension count suggests, this set is **not** always finite (Theorem 14.7(4), Example 14.8).

Throughout, "the encoding" means $\Phi$ exactly as written in Definition 10.1; every claim is proved from the hypotheses of §1.2 and from nothing else.

---

## 1. Data, hypotheses, and the geometric problem

### 1.1 Data

Fix real constants
$$L_1,\ L_2,\ x,\ y,\ c_x,\ c_y,\ r,\ \mu,\ \varepsilon\ \in\ \mathbb R,$$
and write
$$O:=(0,0),\qquad C:=(c_x,c_y),\qquad P^\star:=(x,y),\qquad R:=r+\mu .$$
Here $C$ is the obstacle centre, $r$ its radius, $\mu$ a clearance margin, $P^\star$ the target tool point, and $\varepsilon$ a singularity margin. Only the combination $R=r+\mu$ ever occurs.

### 1.2 Standing hypotheses

* **(H1)** $L_1\neq0$ and $L_2\neq0$;
* **(H2)** $\varepsilon\ge0$;
* **(H3)** $R\ge0$.

**Remark 1.1 (each hypothesis is at the strength actually used).**

* (H1) is stated as $L_i\neq0$, not $L_i>0$. Every use below is of $L_1^2>0$, of $L_2\neq0$, or of $\lvert L_2\rvert>0$; no proof uses a sign. This matters concretely: §13 applies the entire development with $L_1$ or $L_2$ replaced by its negative, and that is what repairs the chart loss of Theorem 12.1.
* (H3) is stated as $R\ge0$, not $R>0$. The only consumer of a hypothesis on $R$ is Lemma 2.3, whose hypothesis is $b\ge0$. The hypothesis is nonetheless **not** removable: if $R<0$ then the geometric requirement $\operatorname{dist}\ge R$ is vacuously true while its squared encoding $\operatorname{dist}^2\ge R^2$ is a genuine restriction, so the encoding would reject admissible configurations. Nothing in the data forces $r\ge0$ unless it is assumed; in particular assuming $\mu>0$ does not give (H3), and no hypothesis "$\mu>0$" appears above because $\mu$ enters only through $R$.
* (H2) is stated as $\varepsilon\ge0$ for the same reason. The case $\varepsilon=0$ is genuinely exceptional in exactly one place, the closed form of Corollary 5.4, and is handled there.

In the intended application $L_1,L_2>0$, $r\ge0$, $\mu>0$ and $\varepsilon>0$, so (H1)–(H3) hold with strict inequalities. No hypothesis of rationality is made or used: rationality of the data matters only for exact arithmetic in an implementation, and all statements below are over $\mathbb R$.

### 1.3 Euclidean conventions

For $u,v\in\mathbb R^2$, $u\cdot v$ is the standard inner product and $\lVert u\rVert^2=u\cdot u$. For $A,B\in\mathbb R^2$,
$$[A,B]:=\{A+s(B-A):s\in[0,1]\},\qquad
\operatorname{dist}(C,[A,B]):=\min_{p\in[A,B]}\lVert C-p\rVert .$$
The minimum is attained: $[A,B]$ is the continuous image of $[0,1]$, hence nonempty and compact, and $p\mapsto\lVert C-p\rVert$ is continuous.

### 1.4 Kinematics

For $q=(q_1,q_2)\in\mathbb R^2$ put
$$E(q_1):=\bigl(L_1\cos q_1,\ L_1\sin q_1\bigr),\qquad
P(q):=E(q_1)+L_2\bigl(\cos(q_1+q_2),\ \sin(q_1+q_2)\bigr),$$
the elbow and tool points, and let $J(q):=\partial P/\partial q\in\mathbb R^{2\times2}$. The two link segments are
$$\mathcal S^{(1)}(q):=\bigl[\,O,\ E(q_1)\,\bigr],\qquad
\mathcal S^{(2)}(q):=\bigl[\,E(q_1),\ P(q)\,\bigr].$$

### 1.5 The geometric conditions

For $q\in\mathbb R^2$:

* **(a)** $P(q)=P^\star$;
* **(b)** $\operatorname{dist}\bigl(C,\mathcal S^{(1)}(q)\bigr)\ge R$ **and** $\operatorname{dist}\bigl(C,\mathcal S^{(2)}(q)\bigr)\ge R$;
* **(c)** $\lvert\det J(q)\rvert\ge\varepsilon$.

Call $q$ **admissible** if (a), (b) and (c) all hold.

**Remark 1.2 (the scope of "admissible").** Conditions (a), (b), (c) are definitions internal to this document, and every soundness and completeness statement below is relative to them and to nothing else. In particular (b) models both links as segments of zero thickness and the obstacle as the closed disc of radius $r$ about $C$ inflated by $\mu$. Whether that is an adequate model of physical collision-freeness — link width, joint hardware, the region swept during motion — is not addressed here and must not be read into the word "admissible".

**Lemma 1.3 (periodicity).** $E$, $P$, $J$ and $\det J$ are $2\pi$-periodic in each of $q_1,q_2$. Consequently admissibility is well defined on $\mathbb T=(\mathbb R/2\pi\mathbb Z)^2$.

*Proof.* $E(q_1)$ depends on $q_1$ only through $\cos q_1,\sin q_1$, which are $2\pi$-periodic, and not on $q_2$. The second summand of $P$ depends on $q$ only through $\cos(q_1+q_2),\sin(q_1+q_2)$; replacing $q_i$ by $q_i+2\pi$ changes $q_1+q_2$ by $2\pi$ and so leaves these unchanged. Hence $E$ and $P$ are $2\pi$-periodic in each variable, and therefore so are their partial derivatives, hence $J$ and $\det J$. Conditions (a), (b), (c) are built from $E$, $P$ and $\det J$ together with the constants $C,P^\star,R,\varepsilon$, so each is $2\pi$-periodic in each variable. $\blacksquare$

---

## 2. Elementary tools

**Lemma 2.1 (positive rescaling preserves $=$ and $\ge$).** Let $p,q\in\mathbb R$ and $\lambda>0$. Then
$$p=q\iff\lambda p=\lambda q,\qquad\qquad p\ge q\iff\lambda p\ge\lambda q .$$

*Proof.* If $p=q$ then $\lambda p=\lambda q$; conversely $\lambda\neq0$, so multiplying $\lambda p=\lambda q$ by $\lambda^{-1}$ gives $p=q$. If $p\ge q$ then $p-q\ge0$, and $\lambda>0$ gives $\lambda(p-q)\ge0$, i.e. $\lambda p\ge\lambda q$. Conversely, $\lambda p\ge\lambda q$ gives $\lambda(p-q)\ge0$, and $\lambda^{-1}>0$ gives $p-q\ge0$. $\blacksquare$

**Convention 2.2.** Lemma 2.1 is used pointwise: for $f,g:S\to\mathbb R$ and $\lambda:S\to(0,\infty)$,
$$\{s:f(s)=g(s)\}=\{s:\lambda(s)f(s)=\lambda(s)g(s)\},\qquad
\{s:f(s)\ge g(s)\}=\{s:\lambda(s)f(s)\ge\lambda(s)g(s)\}.$$
Every denominator-clearing step below is an instance of this, and the strict positivity of the multiplier is verified at each use.

**Lemma 2.3 (squaring an inequality).** Let $a\in\mathbb R$ and $b\ge0$. Then
$$\lvert a\rvert\ge b\iff a^2\ge b^2 .$$

*Proof.* **Case $b=0$.** Both sides hold unconditionally, since $\lvert a\rvert\ge0$ and $a^2\ge0$; so the equivalence holds.

**Case $b>0$.** $(\Rightarrow)$ From $\lvert a\rvert\ge b>0$ we obtain $\lvert a\rvert>0$, so Lemma 2.1 may be applied with $\lambda:=\lvert a\rvert$. Doing so to the inequality $\lvert a\rvert\ge b$ gives $\lvert a\rvert^2\ge b\lvert a\rvert$; applying Lemma 2.1 to the same inequality with $\lambda:=b>0$ gives $b\lvert a\rvert\ge b^2$. Chaining, $a^2=\lvert a\rvert^2\ge b^2$.
$(\Leftarrow)$ By contraposition. Suppose $\lvert a\rvert<b$. Multiplying this strict inequality by $\lvert a\rvert\ge0$ gives $\lvert a\rvert^2\le b\lvert a\rvert$, and multiplying it by $b>0$ gives $b\lvert a\rvert<b^2$. Hence $a^2=\lvert a\rvert^2<b^2$. $\blacksquare$

*(The case split is on $b$, not on $a$. It is needed because the multiplier $\lvert a\rvert$ of Lemma 2.1 must be shown strictly positive, and that follows from $b>0$ and only from it.)*

**Remark 2.4.** The hypothesis $b\ge0$ cannot be dropped: for $a=0$, $b=-1$ the left-hand side holds and the right-hand side fails. It is exactly $b\ge0$ that makes the equivalence hold for *every* $a$.

**Lemma 2.5 (half-angle chart).** Define $\tau:\mathbb R\to(-\pi,\pi)$ by $\tau(t):=2\arctan t$. Then $\tau$ is a continuous, strictly increasing bijection with inverse $q\mapsto\tan(q/2)$, and for $q=\tau(t)$, writing $D:=1+t^2$,
$$\cos q=\frac{1-t^2}{D},\qquad\sin q=\frac{2t}{D}.$$

*Proof.* The restriction of $\tan$ to $(-\pi/2,\pi/2)$ is continuous, strictly increasing and surjective onto $\mathbb R$; hence its inverse $\arctan:\mathbb R\to(-\pi/2,\pi/2)$ is a continuous, strictly increasing bijection, and so is $\tau=2\arctan$ onto $(-\pi,\pi)$, with inverse $q\mapsto\tan(q/2)$ (legitimate because $q/2\in(-\pi/2,\pi/2)$).

For the identities set $\theta:=q/2\in(-\pi/2,\pi/2)$, so that $\cos\theta>0$ and $t=\tan\theta=\sin\theta/\cos\theta$. Dividing $\sin^2\theta+\cos^2\theta=1$ by $\cos^2\theta>0$ gives $1+t^2=1/\cos^2\theta$, i.e. $\cos^2\theta=1/D$. Hence
$$\cos q=\cos2\theta=2\cos^2\theta-1=\frac2D-1=\frac{2-D}{D}=\frac{1-t^2}{D},
\qquad
\sin q=2\sin\theta\cos\theta=2t\cos^2\theta=\frac{2t}{D}. \qquad\blacksquare$$

**Notation 2.6.** Put
$$\Theta:\mathbb R^2\to(-\pi,\pi)^2,\qquad \Theta(t_1,t_2):=\bigl(\tau(t_1),\tau(t_2)\bigr),$$
a bijection by Lemma 2.5. **Throughout §§3–12, $q=(q_1,q_2)$ denotes $\Theta(t_1,t_2)$**, and $D_i:=1+t_i^2$.

---

## 3. The chart: unconditional positivity, and its exact cost

**Proposition 3.1.** For every $t\in\mathbb R$ we have $D=1+t^2\ge1>0$, with equality iff $t=0$. In particular $D$ has no real zero.

*Proof.* $t^2\ge0$ for every real $t$, so $1+t^2\ge1$; and $1+t^2=1$ iff $t^2=0$ iff $t=0$. No case distinction on the sign of $t$ arises. $\blacksquare$

**Corollary 3.2.** For all $t_1,t_2\in\mathbb R$ the quantities
$$D_1,\quad D_2,\quad D_1D_2,\quad D_1^2,\quad D_2^2,\quad L_1^2,\quad L_1^2D_1,\quad L_1^2D_1^2$$
are strictly positive, and $\varepsilon D_2\ge0$. Consequently Lemma 2.1 may be applied with any of the former as $\lambda$, and Lemma 2.3 with $b=\varepsilon D_2$.

*Proof.* Strict positivity of $D_1,D_2$ is Proposition 3.1; $L_1^2>0$ by (H1); products of strictly positive reals are strictly positive. Finally $\varepsilon\ge0$ by (H2) and $D_2>0$ give $\varepsilon D_2\ge0$. $\blacksquare$

Thus the chart is **unconditionally** denominator-safe: no restriction of $t_1$ or $t_2$ to a finite interval is used, or needed, at any point below. What a restricted range does is restrict *scope*, which is a separate matter recorded next and pursued in §§12–13.

**Proposition 3.3 (scope of the chart).**

1. $\operatorname{im}\Theta=(-\pi,\pi)^2$. Hence a configuration with $q_1\equiv\pi$ or $q_2\equiv\pi\pmod{2\pi}$ has no $\Theta$-preimage and is not representable in the encoding.
2. For finite $\ell_i<u_i$,
$$\Theta\bigl([\ell_1,u_1]\times[\ell_2,u_2]\bigr)=[\tau(\ell_1),\tau(u_1)]\times[\tau(\ell_2),\tau(u_2)].$$

*Proof.* (1) is Lemma 2.5 together with the definition of $\Theta$. (2): $\tau$ is a continuous strictly increasing bijection onto $(-\pi,\pi)$, hence maps $[\ell,u]$ onto $[\tau(\ell),\tau(u)]$; now take products. $\blacksquare$

Both restrictions are one-directional: they can only *remove* configurations from consideration, never introduce spurious ones. Theorem 12.1 shows the removal is not vacuous; Theorem 13.5 removes it.

---

## 4. Rational forward kinematics

**Definition 4.1.** Define $F_x,F_y\in\mathbb R[t_1,t_2]$ by
$$
\begin{aligned}
F_x&:=L_1(1-t_1^2)D_2+L_2\bigl[(1-t_1^2)(1-t_2^2)-4t_1t_2\bigr]-x\,D_1D_2,\\[2pt]
F_y&:=2L_1t_1D_2+2L_2\bigl[t_1(1-t_2^2)+t_2(1-t_1^2)\bigr]-y\,D_1D_2 .
\end{aligned}
$$

**Lemma 4.2 (monomial expansion).** As elements of $\mathbb R[t_1,t_2]$,
$$
\begin{aligned}
F_x=\;&(L_1+L_2-x)+(-L_1-L_2-x)\,t_1^2+(L_1-L_2-x)\,t_2^2\\
&+(-L_1+L_2-x)\,t_1^2t_2^2-4L_2\,t_1t_2,\\[6pt]
F_y=\;&-y+2(L_1+L_2)\,t_1+2L_2\,t_2-y\,t_1^2-y\,t_2^2\\
&+2(L_1-L_2)\,t_1t_2^2-2L_2\,t_1^2t_2-y\,t_1^2t_2^2 .
\end{aligned}
$$
All monomials not displayed have coefficient $0$; in particular the coefficient of $t_1t_2$ in $F_y$ vanishes.

*Proof.* Expand the three summands of $F_x$:
$$L_1(1-t_1^2)D_2=L_1\bigl(1+t_2^2-t_1^2-t_1^2t_2^2\bigr),$$
$$L_2\bigl[(1-t_1^2)(1-t_2^2)-4t_1t_2\bigr]=L_2\bigl(1-t_1^2-t_2^2+t_1^2t_2^2-4t_1t_2\bigr),$$
$$-x\,D_1D_2=-x\bigl(1+t_1^2+t_2^2+t_1^2t_2^2\bigr).$$
Only the monomials $1,\ t_1^2,\ t_2^2,\ t_1^2t_2^2,\ t_1t_2$ occur, with coefficients respectively
$$L_1+L_2-x,\quad-L_1-L_2-x,\quad L_1-L_2-x,\quad-L_1+L_2-x,\quad-4L_2,$$
which is the displayed formula for $F_x$. Similarly
$$2L_1t_1D_2=2L_1t_1+2L_1t_1t_2^2,$$
$$2L_2\bigl[t_1(1-t_2^2)+t_2(1-t_1^2)\bigr]=2L_2t_1-2L_2t_1t_2^2+2L_2t_2-2L_2t_1^2t_2,$$
$$-y\,D_1D_2=-y-y\,t_1^2-y\,t_2^2-y\,t_1^2t_2^2 .$$
Only $1,\ t_1,\ t_2,\ t_1^2,\ t_2^2,\ t_1t_2^2,\ t_1^2t_2,\ t_1^2t_2^2$ occur, with coefficients respectively
$$-y,\quad 2L_1+2L_2,\quad 2L_2,\quad -y,\quad -y,\quad 2L_1-2L_2,\quad -2L_2,\quad -y,$$
as displayed. No summand contributes a $t_1t_2$ term to $F_y$. $\blacksquare$

**Proposition 4.3 (rationalised forward kinematics).** For every $(t_1,t_2)\in\mathbb R^2$, with $q=\Theta(t_1,t_2)$,
$$P(q)=P^\star\iff\bigl(F_x(t_1,t_2)=0\ \text{ and }\ F_y(t_1,t_2)=0\bigr).$$

*Proof.* The angle-sum identities hold for all real $q_1,q_2$. Substituting Lemma 2.5,
$$\cos(q_1+q_2)=\cos q_1\cos q_2-\sin q_1\sin q_2=\frac{(1-t_1^2)(1-t_2^2)-4t_1t_2}{D_1D_2},$$
$$\sin(q_1+q_2)=\sin q_1\cos q_2+\cos q_1\sin q_2=\frac{2t_1(1-t_2^2)+2t_2(1-t_1^2)}{D_1D_2},$$
the denominators being legitimate since $D_1D_2>0$ (Corollary 3.2). Hence
$$P(q)_1=\frac{L_1(1-t_1^2)D_2+L_2\bigl[(1-t_1^2)(1-t_2^2)-4t_1t_2\bigr]}{D_1D_2},\qquad
P(q)_2=\frac{2L_1t_1D_2+2L_2\bigl[t_1(1-t_2^2)+t_2(1-t_1^2)\bigr]}{D_1D_2}.$$
Now $P(q)=P^\star$ holds iff both coordinate equations hold. For the first, Lemma 2.1 with $\lambda=D_1D_2>0$ gives
$$P(q)_1=x\iff L_1(1-t_1^2)D_2+L_2\bigl[\cdots\bigr]=x\,D_1D_2\iff F_x=0,$$
and identically for the second coordinate with $F_y$. $\blacksquare$

**Remark 4.4 (spot checks of the expansion only).** Let $L_1=L_2=1$. For $(t_1,t_2)=(1,0)$ we have $q=(\pi/2,0)$ and $P(q)=(0,2)$; with $(x,y)=(0,2)$, Lemma 4.2 gives $F_x=2-2=0$ and $F_y=-2+4-2=0$. For $(t_1,t_2)=(0,1)$, $q=(0,\pi/2)$ and $P(q)=(1,1)$; with $(x,y)=(1,1)$, $F_x=1-1=0$ and $F_y=-1+2-1=0$. For $(t_1,t_2)=(1,1)$, $q=(\pi/2,\pi/2)$ and $P(q)=(-1,1)$; with $(x,y)=(-1,1)$, $F_x=3-1+1+1-4=0$ and $F_y=-1+4+2-1-1+0-2-1=0$. These verify the *expansion* of Lemma 4.2. Proposition 4.3 is proved above without appeal to them.

---

## 5. The singularity margin

**Lemma 5.1.** For every $q\in\mathbb R^2$, $\ \det J(q)=L_1L_2\sin q_2$.

*Proof.* Write $c_1=\cos q_1$, $s_1=\sin q_1$, $c_{12}=\cos(q_1+q_2)$, $s_{12}=\sin(q_1+q_2)$. From $P(q)=(L_1c_1+L_2c_{12},\ L_1s_1+L_2s_{12})$ and $\partial(q_1+q_2)/\partial q_1=\partial(q_1+q_2)/\partial q_2=1$,
$$J=\begin{pmatrix}-L_1s_1-L_2s_{12}&-L_2s_{12}\\[2pt] L_1c_1+L_2c_{12}&L_2c_{12}\end{pmatrix},$$
whence
$$
\begin{aligned}
\det J&=(-L_1s_1-L_2s_{12})(L_2c_{12})+(L_2s_{12})(L_1c_1+L_2c_{12})\\
&=-L_1L_2s_1c_{12}-L_2^2s_{12}c_{12}+L_1L_2s_{12}c_1+L_2^2s_{12}c_{12}\\
&=L_1L_2\bigl(s_{12}c_1-c_{12}s_1\bigr)
=L_1L_2\sin\bigl((q_1+q_2)-q_1\bigr)=L_1L_2\sin q_2,
\end{aligned}
$$
using $\sin(\alpha-\beta)=\sin\alpha\cos\beta-\cos\alpha\sin\beta$ with $\alpha=q_1+q_2$, $\beta=q_1$. $\blacksquare$

**Definition 5.2.** $\ G(t_2):=\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)t_2^2-\varepsilon^2t_2^4-\varepsilon^2\ \in\ \mathbb R[t_2]$.

**Proposition 5.3.** For every $t_2\in\mathbb R$, every $q_1\in\mathbb R$, and $q_2=\tau(t_2)$,
$$\bigl\lvert\det J(q_1,q_2)\bigr\rvert\ge\varepsilon\iff G(t_2)\ge0 .$$

*Proof.* By Lemma 5.1 and Lemma 2.5, $\det J=L_1L_2\sin q_2=2L_1L_2t_2/D_2$, which does not involve $q_1$. Since $D_2>0$ we have $\lvert2L_1L_2t_2/D_2\rvert=\lvert2L_1L_2t_2\rvert/D_2$, and Lemma 2.1 with $\lambda=D_2>0$ gives
$$\lvert\det J\rvert\ge\varepsilon\iff\lvert2L_1L_2t_2\rvert\ge\varepsilon D_2 .$$
Apply Lemma 2.3 with $a:=2L_1L_2t_2$ and $b:=\varepsilon D_2$; its hypothesis $b\ge0$ holds by Corollary 3.2, globally in $t_2$, so no case distinction on the sign of $t_2$ or of $\det J$ arises. Hence
$$\lvert\det J\rvert\ge\varepsilon\iff 4L_1^2L_2^2t_2^2\ge\varepsilon^2D_2^2 .$$
Finally $D_2^2=1+2t_2^2+t_2^4$, so the last inequality reads
$$4L_1^2L_2^2t_2^2-\varepsilon^2-2\varepsilon^2t_2^2-\varepsilon^2t_2^4\ge0,$$
which is exactly $G(t_2)\ge0$. $\blacksquare$

**Corollary 5.4 (feasibility of the singularity constraint).**

1. If $\varepsilon=0$ then $G(t_2)=4L_1^2L_2^2t_2^2\ge0$ for every $t_2$, so $\{t_2:G(t_2)\ge0\}=\mathbb R$.
2. If $\varepsilon>0$ then $\{t_2:G(t_2)\ge0\}\neq\emptyset$ iff $\varepsilon\le\lvert L_1L_2\rvert$, and in that case
$$\{t_2:G(t_2)\ge0\}=\bigl\{t_2:\ u_-\le t_2^2\le u_+\bigr\},\qquad
u_\pm=\frac{\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)\pm\sqrt{\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)^2-4\varepsilon^4}}{2\varepsilon^2},$$
with $0<u_-\le1\le u_+$.

*Proof.* (1) is immediate from Definition 5.2 with $\varepsilon=0$.

(2) Put $z:=t_2^2\ge0$. Then $G\ge0$ reads
$$\varepsilon^2z^2-\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)z+\varepsilon^2\le0,$$
a quadratic in $z$ with strictly positive leading coefficient $\varepsilon^2$. Its solution set in $\mathbb R$ is nonempty iff the discriminant
$$\Delta:=\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)^2-4\varepsilon^4$$
is $\ge0$, in which case that set is the closed interval $[u_-,u_+]$ with $u_\pm$ as displayed.

Now $\Delta=\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)^2-(2\varepsilon^2)^2\ge0$ iff $\bigl\lvert4L_1^2L_2^2-2\varepsilon^2\bigr\rvert\ge2\varepsilon^2$. The branch $4L_1^2L_2^2-2\varepsilon^2\le-2\varepsilon^2$ forces $L_1^2L_2^2\le0$, hence $L_1L_2=0$, contradicting (H1). So
$$\Delta\ge0\iff4L_1^2L_2^2\ge4\varepsilon^2\iff(L_1L_2)^2\ge\varepsilon^2\iff\lvert L_1L_2\rvert\ge\varepsilon,$$
the last step by Lemma 2.3 with $a=L_1L_2$, $b=\varepsilon\ge0$.

Assume $\Delta\ge0$. The product of the two roots is $\varepsilon^2/\varepsilon^2=1>0$ and their sum is $\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)/\varepsilon^2\ge2>0$, using $4L_1^2L_2^2-2\varepsilon^2\ge2\varepsilon^2$ from the previous paragraph. Hence both roots are positive, and $u_-u_+=1$ forces $u_-\le1\le u_+$. Since $z=t_2^2$ ranges over $[0,\infty)$ and $[u_-,u_+]\subseteq(0,\infty)$, the set $\{t_2:u_-\le t_2^2\le u_+\}$ is exactly the solution set, and it is nonempty (it contains $t_2=1$). $\blacksquare$

**Remark 5.5 (independent check).** By Lemma 5.1, condition (c) says $\lvert\sin q_2\rvert\ge\varepsilon/\lvert L_1L_2\rvert$, which is satisfiable by some $q_2\in(-\pi,\pi)$ iff $\varepsilon\le\lvert L_1L_2\rvert$. This agrees with Corollary 5.4 and is obtained without reference to $G$.

---

## 6. Point-to-segment distance: the case split

**Lemma 6.1.** Let $A,B,C\in\mathbb R^2$ with $v:=B-A\neq0$ and $w:=C-A$, and set
$$s^\star:=\frac{w\cdot v}{v\cdot v}\qquad(\text{well defined, since }v\cdot v>0).$$
Define
$$d_{\mathrm I}^2:=w\cdot w,\qquad d_{\mathrm{II}}^2:=\lVert C-B\rVert^2,\qquad
d_{\mathrm{III}}^2:=w\cdot w-\frac{(w\cdot v)^2}{v\cdot v},$$
and put $d^2:=\operatorname{dist}\bigl(C,[A,B]\bigr)^2$. Then:

1. $s^\star\le0\implies d^2=d_{\mathrm I}^2$;
2. $s^\star\ge1\implies d^2=d_{\mathrm{II}}^2$;
3. $0\le s^\star\le1\implies d^2=d_{\mathrm{III}}^2$;
4. *(seam agreement)* $s^\star=0\implies d_{\mathrm I}^2=d_{\mathrm{III}}^2$, and $s^\star=1\implies d_{\mathrm{II}}^2=d_{\mathrm{III}}^2$;
5. *(covering)* at least one of $s^\star\le0$, $s^\star\ge1$, $0\le s^\star\le1$ holds.

*Proof.* For $s\in\mathbb R$ put
$$f(s):=\lVert A+sv-C\rVert^2=\lVert sv-w\rVert^2=(v\cdot v)s^2-2(w\cdot v)s+w\cdot w .$$
Since $v\cdot v>0$, completing the square gives
$$f(s)=(v\cdot v)\bigl(s-s^\star\bigr)^2+d_{\mathrm{III}}^2 ,$$
so $f$ is strictly decreasing on $(-\infty,s^\star]$, strictly increasing on $[s^\star,\infty)$, and $f(s^\star)=d_{\mathrm{III}}^2$ is the global minimum. By definition of $[A,B]$, $d^2=\min_{s\in[0,1]}f(s)$.

(1) If $s^\star\le0$ then $[0,1]\subseteq[s^\star,\infty)$, where $f$ is increasing, so the minimum over $[0,1]$ is at $s=0$: $d^2=f(0)=w\cdot w=d_{\mathrm I}^2$.

(2) If $s^\star\ge1$ then $[0,1]\subseteq(-\infty,s^\star]$, where $f$ is decreasing, so the minimum is at $s=1$:
$$d^2=f(1)=\lVert v-w\rVert^2=\lVert(B-A)-(C-A)\rVert^2=\lVert B-C\rVert^2=d_{\mathrm{II}}^2 .$$

(3) If $0\le s^\star\le1$ then $s^\star\in[0,1]$, and $f(s^\star)$ is the global minimum of $f$, a fortiori the minimum over $[0,1]$; so $d^2=d_{\mathrm{III}}^2$.

(4) If $s^\star=0$ then $w\cdot v=0$, so $d_{\mathrm{III}}^2=w\cdot w=d_{\mathrm I}^2$. If $s^\star=1$ then $w\cdot v=v\cdot v$, so $d_{\mathrm{III}}^2=w\cdot w-(v\cdot v)$, while
$$d_{\mathrm{II}}^2=\lVert v-w\rVert^2=v\cdot v-2\,w\cdot v+w\cdot w=w\cdot w-v\cdot v ;$$
the two agree.

(5) If $s^\star<0$ the first alternative holds; if $s^\star>1$ the second; otherwise $0\le s^\star\le1$. $\blacksquare$

**Corollary 6.2 (a correct disjunctive split with overlapping selectors).** With $A,B,C,v,w,s^\star$ as in Lemma 6.1 and any $R\ge0$,
$$\operatorname{dist}\bigl(C,[A,B]\bigr)\ge R
\iff\bigvee_{k\in\{\mathrm I,\mathrm{II},\mathrm{III}\}}\bigl(\sigma_k\wedge d_k^2\ge R^2\bigr),$$
where
$$\sigma_{\mathrm I}:\ s^\star\le0,\qquad \sigma_{\mathrm{II}}:\ s^\star\ge1,\qquad \sigma_{\mathrm{III}}:\ 0\le s^\star\le1 .$$

*Proof.* First, $\operatorname{dist}(C,[A,B])\ge R\iff d^2\ge R^2$ by Lemma 2.3 applied with $a:=\operatorname{dist}(C,[A,B])\ge0$ (so $\lvert a\rvert=a$ and $a^2=d^2$) and $b:=R\ge0$.

$(\Leftarrow)$ Suppose $\sigma_k$ and $d_k^2\ge R^2$ hold for some $k$. By Lemma 6.1(1)–(3), $\sigma_k$ implies $d_k^2=d^2$; hence $d^2\ge R^2$.

$(\Rightarrow)$ Suppose $d^2\ge R^2$. By Lemma 6.1(5) some $\sigma_k$ holds, and then $d_k^2=d^2\ge R^2$ by Lemma 6.1(1)–(3). $\blacksquare$

**Remark 6.3.** The three selectors overlap at $s^\star\in\{0,1\}$. The overlap is harmless in the $(\Leftarrow)$ direction because, by Lemma 6.1(4), the overlapping formulas return the *same real number*; and the non-strictness is precisely what supplies the covering property (5), which the $(\Rightarrow)$ direction consumes. Section 14 determines exactly which changes to these inequalities break which direction, and where.

---

## 7. Rational data for the two segments

Throughout this section $t_1\in\mathbb R$ is arbitrary and $q_1=\tau(t_1)$.

**Definition 7.1.** Put
$$\mathbf e(t_1):=\bigl(L_1(1-t_1^2),\ 2L_1t_1\bigr)\qquad\text{(the \emph{elbow numerator})},$$
$$\mathbf g(t_1):=D_1C-\mathbf e(t_1),\qquad \mathbf h(t_1):=\mathbf e(t_1)-D_1P^\star,$$
with components $\mathbf g=(g_x,g_y)$ and $\mathbf h=(h_x,h_y)$, and
$$\Pi^{(1)}(t_1):=C\cdot\mathbf e(t_1),\qquad
\Pi^{(2)}(t_1):=(C-P^\star)\cdot\mathbf h(t_1),\qquad
\Sigma^{(2)}(t_1):=\lVert\mathbf h(t_1)\rVert^2 .$$
Explicitly,
$$
\begin{aligned}
\Pi^{(1)}&=L_1\bigl(c_x+2c_yt_1-c_xt_1^2\bigr),\\
g_x&=(c_x-L_1)+(c_x+L_1)t_1^2, &\qquad g_y&=c_y-2L_1t_1+c_yt_1^2,\\
h_x&=(L_1-x)-(L_1+x)t_1^2, &\qquad h_y&=-y+2L_1t_1-yt_1^2,\\
\Pi^{(2)}&=(c_x-x)h_x+(c_y-y)h_y, &\qquad \Sigma^{(2)}&=h_x^2+h_y^2 .
\end{aligned}
$$
All seven are polynomials in $t_1$ alone with real coefficients.

**Remark 7.2 (reading the notation).** $\mathbf e$, $\mathbf g$, $\mathbf h$ are *numerator vectors*, not points. By Lemma 7.3 below,
$$\mathbf e=D_1E(q_1),\qquad \mathbf g=D_1\bigl(C-E(q_1)\bigr),\qquad \mathbf h=D_1\bigl(E(q_1)-P^\star\bigr).$$
In particular no component of $\mathbf g$ or $\mathbf h$ is a coordinate of any of the points $E(q_1)$, $C$, $C-E(q_1)$, $E(q_1)-P^\star$: each is $D_1$ times such a coordinate. Superscripts $(1),(2)$ index **segments**; subscripts $1,2$ index **joints**. Both conventions occur inside a single formula (for instance $D_1\Pi^{(2)}$), and must not be conflated.

**Lemma 7.3 (unconditional identities).** For every $t_1\in\mathbb R$:

1. $E(q_1)=\mathbf e(t_1)/D_1$, and $\lVert\mathbf e(t_1)\rVert^2=L_1^2D_1^2$, hence $\lVert E(q_1)\rVert=\lvert L_1\rvert$;
2. $\mathbf g(t_1)=D_1\bigl(C-E(q_1)\bigr)$, hence $\lVert C-E(q_1)\rVert^2=\bigl(g_x^2+g_y^2\bigr)/D_1^2$;
3. $\mathbf h(t_1)=D_1\bigl(E(q_1)-P^\star\bigr)$, hence $\lVert E(q_1)-P^\star\rVert^2=\Sigma^{(2)}/D_1^2$;
4. $C\cdot E(q_1)=\Pi^{(1)}/D_1$ and $(C-P^\star)\cdot\bigl(E(q_1)-P^\star\bigr)=\Pi^{(2)}/D_1$;
5. $D_1\Pi^{(2)}-\Sigma^{(2)}=\mathbf g\cdot\mathbf h$ and $D_1\bigl(\Pi^{(1)}-L_1^2D_1\bigr)=\mathbf g\cdot\mathbf e$.

None of these uses any hypothesis beyond (H1); in particular none uses condition (a).

*Proof.* (1) By Lemma 2.5,
$$E(q_1)=\Bigl(L_1\frac{1-t_1^2}{D_1},\ L_1\frac{2t_1}{D_1}\Bigr)=\frac{\mathbf e}{D_1},$$
and
$$\lVert\mathbf e\rVert^2=L_1^2(1-t_1^2)^2+4L_1^2t_1^2=L_1^2\bigl(1-2t_1^2+t_1^4+4t_1^2\bigr)=L_1^2(1+t_1^2)^2=L_1^2D_1^2 .$$
Dividing by $D_1^2>0$ gives $\lVert E(q_1)\rVert^2=L_1^2$, so $\lVert E(q_1)\rVert=\lvert L_1\rvert$.

(2) $\mathbf g=D_1C-\mathbf e=D_1C-D_1E(q_1)=D_1\bigl(C-E(q_1)\bigr)$; divide by $D_1>0$ and take squared norms.

(3) $\mathbf h=\mathbf e-D_1P^\star=D_1E(q_1)-D_1P^\star=D_1\bigl(E(q_1)-P^\star\bigr)$; likewise.

(4) $\Pi^{(1)}=C\cdot\mathbf e=D_1\,C\cdot E(q_1)$ and $\Pi^{(2)}=(C-P^\star)\cdot\mathbf h=D_1\,(C-P^\star)\cdot\bigl(E(q_1)-P^\star\bigr)$ by (1) and (3); divide by $D_1>0$.

(5) Using (3) in the second step,
$$D_1\Pi^{(2)}-\Sigma^{(2)}=\mathbf h\cdot\bigl(D_1(C-P^\star)-\mathbf h\bigr)
=\mathbf h\cdot\bigl(D_1C-D_1P^\star-\mathbf e+D_1P^\star\bigr)=\mathbf h\cdot(D_1C-\mathbf e)=\mathbf h\cdot\mathbf g .$$
Similarly, using (1),
$$\mathbf g\cdot\mathbf e=(D_1C-\mathbf e)\cdot\mathbf e=D_1\Pi^{(1)}-L_1^2D_1^2=D_1\bigl(\Pi^{(1)}-L_1^2D_1\bigr). \qquad\blacksquare$$

**Lemma 7.4 (degrees).** As polynomials in $t_1$:

| polynomial | degree at most | leading coefficient | the degree drops exactly when |
|---|---|---|---|
| $\Pi^{(1)}$ | $2$ | $-L_1c_x$ | $c_x=0$ |
| $g_x$ | $2$ | $c_x+L_1$ | $c_x=-L_1$ |
| $g_y$ | $2$ | $c_y$ | $c_y=0$ |
| $h_x$ | $2$ | $-(L_1+x)$ | $x=-L_1$ |
| $h_y$ | $2$ | $-y$ | $y=0$ |
| $\Pi^{(2)}$ | $2$ | $-\bigl[(c_x-x)(L_1+x)+(c_y-y)y\bigr]$ | that expression vanishes |
| $\Sigma^{(2)}$ | $4$ | $(L_1+x)^2+y^2$ | $(x,y)=(-L_1,0)$ |

*Proof.* Read the coefficients off the displayed formulas of Definition 7.1. For $\Sigma^{(2)}=h_x^2+h_y^2$ the coefficient of $t_1^4$ is $(L_1+x)^2+y^2$, a sum of two squares, which vanishes iff $x=-L_1$ and $y=0$. $\blacksquare$

**Remark 7.5.** The entries of the second column are *upper bounds*, attained only under the side conditions of the fourth. Nothing below depends on the degrees; the table is recorded because it is the interface an implementation must respect, and because an implementation that *asserts* $\deg\Sigma^{(2)}=4$ fails on the reachable instance $(x,y)=(-L_1,0)$.

The two link segments share the endpoint $E(q_1)$ and differ only in their other endpoint, which is a constant in both cases once (a) is imposed. The next lemma treats both at once.

**Lemma 7.6 (uniform segment data).** Let $A\in\mathbb R^2$ be a constant point, and set
$$\mathbf h_A(t_1):=\mathbf e(t_1)-D_1A,\qquad \Pi_A:=(C-A)\cdot\mathbf h_A,\qquad \Sigma_A:=\lVert\mathbf h_A\rVert^2 .$$
Put $B:=E(q_1)$, $v:=B-A$, $w:=C-A$. Then
$$v=\frac{\mathbf h_A}{D_1},\qquad v\cdot v=\frac{\Sigma_A}{D_1^2},\qquad w\cdot v=\frac{\Pi_A}{D_1},$$
and $v\neq0\iff\Sigma_A>0$. If $\Sigma_A>0$, then with $s^\star$ and $d_k^2$ as in Lemma 6.1,
$$s^\star=\frac{D_1\Pi_A}{\Sigma_A},\qquad
d_{\mathrm I}^2=\lVert C-A\rVert^2,\qquad
d_{\mathrm{II}}^2=\frac{g_x^2+g_y^2}{D_1^2},\qquad
d_{\mathrm{III}}^2=\lVert C-A\rVert^2-\frac{\Pi_A^2}{\Sigma_A}.$$

*Proof.* By Lemma 7.3(1), $\mathbf h_A=\mathbf e-D_1A=D_1E(q_1)-D_1A=D_1v$; hence $v=\mathbf h_A/D_1$ and $v\cdot v=\Sigma_A/D_1^2$. Since $D_1>0$, $v=0\iff\mathbf h_A=0\iff\Sigma_A=0$. Also $w\cdot v=(C-A)\cdot\mathbf h_A/D_1=\Pi_A/D_1$.

Assume $\Sigma_A>0$. Then
$$s^\star=\frac{w\cdot v}{v\cdot v}=\frac{\Pi_A/D_1}{\Sigma_A/D_1^2}=\frac{D_1\Pi_A}{\Sigma_A}.$$
Next, $d_{\mathrm I}^2=w\cdot w=\lVert C-A\rVert^2$; and $d_{\mathrm{II}}^2=\lVert C-B\rVert^2=\lVert C-E(q_1)\rVert^2=(g_x^2+g_y^2)/D_1^2$ by Lemma 7.3(2); and
$$d_{\mathrm{III}}^2=w\cdot w-\frac{(w\cdot v)^2}{v\cdot v}
=\lVert C-A\rVert^2-\frac{\Pi_A^2/D_1^2}{\Sigma_A/D_1^2}=\lVert C-A\rVert^2-\frac{\Pi_A^2}{\Sigma_A}. \qquad\blacksquare$$

**Corollary 7.7 (the elbow predicate is shared for a structural reason).** In Lemma 7.6 the quantity $d_{\mathrm{II}}^2$ does not depend on $A$. Since both link segments have $B=E(q_1)$ as an endpoint, the case-$\mathrm{II}$ quantity is in both cases the single real number
$$\lVert C-E(q_1)\rVert^2=\frac{g_x^2+g_y^2}{D_1^2},$$
the squared distance from the obstacle centre to the elbow. Two occurrences of one real-valued function of $t_1$ introduce no coupling between the two segments.

**Proposition 7.8 (generic disjunction).** In the setting of Lemma 7.6, assume $\Sigma_A(t_1)>0$ and $R\ge0$. Then
$$\operatorname{dist}\bigl(C,[A,E(q_1)]\bigr)\ge R\iff\Psi_A(t_1),$$
where $\Psi_A(t_1)$ denotes the disjunction
$$
\begin{aligned}
&\bigl[\ \Pi_A\le0\ \wedge\ \lVert C-A\rVert^2-R^2\ge0\ \bigr]\\
\vee\;&\bigl[\ D_1\Pi_A-\Sigma_A\ge0\ \wedge\ g_x^2+g_y^2-R^2D_1^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi_A\ge0\ \wedge\ \Sigma_A-D_1\Pi_A\ge0\ \wedge\ \bigl(\lVert C-A\rVert^2-R^2\bigr)\Sigma_A-\Pi_A^2\ge0\ \bigr].
\end{aligned}
$$

*Proof.* By Lemma 7.6, $v\neq0$, so Lemma 6.1 and Corollary 6.2 apply, the latter using $R\ge0$.

*Selectors.* Since $\Sigma_A>0$, Lemma 2.1 with $\lambda=\Sigma_A$ turns $s^\star\le0$ into $\Sigma_As^\star\le0$, i.e. $D_1\Pi_A\le0$, and Lemma 2.1 with $\lambda=D_1^{-1}>0$ turns this into $\Pi_A\le0$. The same two steps give $s^\star\ge1\iff D_1\Pi_A\ge\Sigma_A\iff D_1\Pi_A-\Sigma_A\ge0$, and consequently
$$0\le s^\star\le1\iff\Pi_A\ge0\ \wedge\ \Sigma_A-D_1\Pi_A\ge0 .$$

*Case values.* $d_{\mathrm I}^2\ge R^2\iff\lVert C-A\rVert^2-R^2\ge0$. By Lemma 2.1 with $\lambda=D_1^2>0$,
$$d_{\mathrm{II}}^2\ge R^2\iff g_x^2+g_y^2\ge R^2D_1^2 .$$
By Lemma 2.1 with $\lambda=\Sigma_A>0$,
$$d_{\mathrm{III}}^2\ge R^2\iff\bigl(\lVert C-A\rVert^2-R^2\bigr)\Sigma_A-\Pi_A^2\ge0 .$$

Substituting these six equivalences into Corollary 6.2 yields exactly $\Psi_A$. $\blacksquare$

---

## 8. Segment 1 (shoulder to elbow)

Here $A=O$, so $\mathbf h_O=\mathbf e$, $\ \Sigma_O=\lVert\mathbf e\rVert^2=L_1^2D_1^2$ and $\Pi_O=C\cdot\mathbf e=\Pi^{(1)}$.

**Definition 8.1.** $\Psi^{(1)}(t_1)$ denotes the disjunction
$$
\begin{aligned}
&\bigl[\ \Pi^{(1)}\le0\ \wedge\ c_x^2+c_y^2-R^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi^{(1)}-L_1^2D_1\ge0\ \wedge\ g_x^2+g_y^2-R^2D_1^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi^{(1)}\ge0\ \wedge\ L_1^2D_1-\Pi^{(1)}\ge0\ \wedge\ \bigl(c_x^2+c_y^2-R^2\bigr)L_1^2D_1^2-\bigl(\Pi^{(1)}\bigr)^2\ge0\ \bigr].
\end{aligned}
$$

**Proposition 8.2 (segment 1; unconditional).** For every $t_1\in\mathbb R$, with $q_1=\tau(t_1)$,
$$\operatorname{dist}\bigl(C,\mathcal S^{(1)}(q)\bigr)\ge R\iff\Psi^{(1)}(t_1).$$
No hypothesis beyond (H1)–(H3) is used; in particular condition (a) is **not** required.

*Proof.* We have $\Sigma_O=L_1^2D_1^2>0$ by Corollary 3.2, so Proposition 7.8 applies with $A=O$. Using $\lVert C-O\rVert^2=c_x^2+c_y^2$ and $\Sigma_O=L_1^2D_1^2$, it yields the equivalence of $\operatorname{dist}(C,\mathcal S^{(1)}(q))\ge R$ with
$$
\begin{aligned}
&\bigl[\Pi^{(1)}\le0\wedge c_x^2+c_y^2-R^2\ge0\bigr]\\
\vee\;&\bigl[D_1\Pi^{(1)}-L_1^2D_1^2\ge0\wedge g_x^2+g_y^2-R^2D_1^2\ge0\bigr]\\
\vee\;&\bigl[\Pi^{(1)}\ge0\wedge L_1^2D_1^2-D_1\Pi^{(1)}\ge0\wedge\bigl(c_x^2+c_y^2-R^2\bigr)L_1^2D_1^2-\bigl(\Pi^{(1)}\bigr)^2\ge0\bigr].
\end{aligned}
$$
By Lemma 2.1 with $\lambda=D_1>0$,
$$D_1\Pi^{(1)}-L_1^2D_1^2\ge0\iff\Pi^{(1)}-L_1^2D_1\ge0,\qquad
L_1^2D_1^2-D_1\Pi^{(1)}\ge0\iff L_1^2D_1-\Pi^{(1)}\ge0 .$$
Substituting these gives exactly $\Psi^{(1)}$. $\blacksquare$

**Remark 8.3.** The cancellation of one factor $D_1$ in the second and third clauses is the only reason $\Psi^{(1)}$ and $\Psi^{(2)}$ below are not of literally identical shape: for segment 1 the squared length $\Sigma_O=L_1^2D_1^2$ carries the factor $D_1^2$ explicitly, while for segment 2 the corresponding quantity does not factor.

---

## 9. Segment 2 (elbow to tool)

The far endpoint of $\mathcal S^{(2)}(q)=[E(q_1),P(q)]$ depends on $q_2$. The encoding replaces $P(q)$ by the constant $P^\star$. This replacement is an identity of sets exactly on the locus where (a) holds. Everything in this section is organised around making that statement, and its failure elsewhere, precise.

Here $A=P^\star$, so $\mathbf h_{P^\star}=\mathbf h$, $\ \Sigma_{P^\star}=\Sigma^{(2)}$ and $\Pi_{P^\star}=\Pi^{(2)}$.

**Definition 9.1.** $\Psi^{(2)}(t_1)$ denotes the disjunction
$$
\begin{aligned}
&\bigl[\ \Pi^{(2)}\le0\ \wedge\ (c_x-x)^2+(c_y-y)^2-R^2\ge0\ \bigr]\\
\vee\;&\bigl[\ D_1\Pi^{(2)}-\Sigma^{(2)}\ge0\ \wedge\ g_x^2+g_y^2-R^2D_1^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi^{(2)}\ge0\ \wedge\ \Sigma^{(2)}-D_1\Pi^{(2)}\ge0\ \wedge\ \bigl((c_x-x)^2+(c_y-y)^2-R^2\bigr)\Sigma^{(2)}-\bigl(\Pi^{(2)}\bigr)^2\ge0\ \bigr].
\end{aligned}
$$
This is a predicate in $t_1$ alone.

**Lemma 9.2 (the degeneracy locus; unconditional).** For every $t_1\in\mathbb R$,
$$\Sigma^{(2)}(t_1)=0\iff E(\tau(t_1))=P^\star .$$
Moreover, if $\Sigma^{(2)}(t_1)=0$ then **no** $t_2\in\mathbb R$ makes $(t_1,t_2)$ satisfy (a); and $\Sigma^{(2)}$ can vanish at some $t_1$ only if $x^2+y^2=L_1^2$.

*Proof.* By Lemma 7.3(3) — which is unconditional — $\Sigma^{(2)}=D_1^2\lVert E(q_1)-P^\star\rVert^2$ with $D_1^2>0$; hence $\Sigma^{(2)}=0\iff E(q_1)=P^\star$.

Suppose $\Sigma^{(2)}(t_1)=0$ and that some $t_2$ made $(t_1,t_2)$ satisfy (a). By definition $P(q)-E(q_1)=L_2\bigl(\cos(q_1+q_2),\sin(q_1+q_2)\bigr)$, a vector of norm $\lvert L_2\rvert>0$ by (H1). Under (a) we have $P(q)=P^\star$, so $\lVert E(q_1)-P^\star\rVert=\lvert L_2\rvert>0$, contradicting $E(q_1)=P^\star$.

Finally $\lVert E(q_1)\rVert=\lvert L_1\rvert$ by Lemma 7.3(1), so $E(q_1)=P^\star$ forces $x^2+y^2=L_1^2$. $\blacksquare$

**Lemma 9.3 (nondegeneracy under (a)).** If $(t_1,t_2)\in\mathbb R^2$ satisfies (a), then
$$\lVert E(q_1)-P^\star\rVert=\lvert L_2\rvert>0\qquad\text{and}\qquad\Sigma^{(2)}(t_1)=L_2^2D_1^2>0 .$$

*Proof.* As in the previous proof, $\lVert P(q)-E(q_1)\rVert=\lvert L_2\rvert$, and (a) gives $P(q)=P^\star$, whence $\lVert E(q_1)-P^\star\rVert=\lvert L_2\rvert$, which is $>0$ by (H1). By Lemma 7.3(3),
$$\Sigma^{(2)}=D_1^2\lVert E(q_1)-P^\star\rVert^2=D_1^2L_2^2>0 . \qquad\blacksquare$$

**Proposition 9.4 (what $\Psi^{(2)}$ says, with and without (a)).** Let $t_1\in\mathbb R$.

1. If $\Sigma^{(2)}(t_1)>0$, then
$$\operatorname{dist}\bigl(C,[E(q_1),P^\star]\bigr)\ge R\iff\Psi^{(2)}(t_1).$$
2. If $(t_1,t_2)$ satisfies (a) for some $t_2$, then $\Sigma^{(2)}(t_1)>0$ and $[E(q_1),P^\star]=\mathcal S^{(2)}(q)$, so
$$\operatorname{dist}\bigl(C,\mathcal S^{(2)}(q)\bigr)\ge R\iff\Psi^{(2)}(t_1).$$
3. If $\Sigma^{(2)}(t_1)=0$, then $\Psi^{(2)}(t_1)$ is **true**, whatever the value of $\lVert C-P^\star\rVert$.

*Proof.* (1) Apply Proposition 7.8 with $A=P^\star$, using $\lVert C-P^\star\rVert^2=(c_x-x)^2+(c_y-y)^2$.

(2) $\Sigma^{(2)}(t_1)>0$ is Lemma 9.3. Under (a), $P(q)=P^\star$, so $\mathcal S^{(2)}(q)=[E(q_1),P(q)]=[E(q_1),P^\star]$ as sets — an identity, not an approximation. Now apply (1).

(3) If $\Sigma^{(2)}(t_1)=0$ then $\mathbf h(t_1)=0$, hence also $\Pi^{(2)}=(C-P^\star)\cdot\mathbf h=0$. The third clause of $\Psi^{(2)}$ then reads
$$0\ge0\ \wedge\ 0-0\ge0\ \wedge\ \bigl(\lVert C-P^\star\rVert^2-R^2\bigr)\cdot0-0\ge0,$$
all three of which hold. Hence $\Psi^{(2)}(t_1)$ is true. $\blacksquare$

**Remark 9.5 ($\Psi^{(2)}$ has no standalone meaning).** Proposition 9.4(3) is sharp and is the exact reason for this restriction. At a parameter $t_1$ with $E(q_1)=P^\star$ the set $[E(q_1),P^\star]$ degenerates to the single point $P^\star$, whose distance to $C$ is $\lVert C-P^\star\rVert$ and may be arbitrarily smaller than $R$ — and yet $\Psi^{(2)}(t_1)$ holds. Thus $\Psi^{(2)}$ **on its own is unsound** as a clearance certificate. Lemma 9.2 shows this can never do harm inside the conjunction defining $\Phi$, because $\Sigma^{(2)}(t_1)=0$ rules out $F_x=F_y=0$. Even where $\Sigma^{(2)}(t_1)>0$ but (a) fails, $\Psi^{(2)}(t_1)$ constrains the distance from $C$ to $[E(q_1),P^\star]$, which is not a link of the configuration $q$. Accordingly $\Psi^{(2)}$ must not be exposed as a separately meaningful predicate — not as a pruning filter, not as an independently reported clearance certificate, not as a lemma quoted elsewhere.

---

## 10. The encoded predicate and the main equivalence

**Definition 10.1.** The encoded predicate $\Phi$ on $\mathbb R^2$ is
$$\Phi(t_1,t_2):\qquad F_x=0\ \wedge\ F_y=0\ \wedge\ G(t_2)\ge0\ \wedge\ \Psi^{(1)}(t_1)\ \wedge\ \Psi^{(2)}(t_1).$$
It is a conjunction of polynomial equations with disjunctions of polynomial inequalities in $(t_1,t_2)$ — a semialgebraic condition — involving no denominators and no auxiliary variables.

**Theorem 10.2 (main equivalence).** Assume (H1)–(H3). For every $(t_1,t_2)\in\mathbb R^2$, with $q=\Theta(t_1,t_2)$,
$$\Phi(t_1,t_2)\iff q\ \text{is admissible, i.e. (a), (b) and (c) hold at }q .$$

*Proof.* $(\Rightarrow)$ Assume $\Phi(t_1,t_2)$.

*Step 1.* From $F_x=F_y=0$ and Proposition 4.3, condition **(a)** holds at $q$.
*Step 2.* From $G(t_2)\ge0$ and Proposition 5.3, condition **(c)** holds at $q$.
*Step 3.* From $\Psi^{(1)}(t_1)$ and Proposition 8.2 — which is unconditional — the first inequality of **(b)** holds.
*Step 4.* Because Step 1 has already established (a), Proposition 9.4(2) is applicable at $t_1$; combined with $\Psi^{(2)}(t_1)$ it yields $\operatorname{dist}(C,\mathcal S^{(2)}(q))\ge R$, the second inequality of **(b)**.

Hence (a), (b) and (c) all hold, and $q$ is admissible.

$(\Leftarrow)$ Assume $q$ is admissible. By Proposition 4.3, $F_x=F_y=0$. By Proposition 5.3, $G(t_2)\ge0$. By Proposition 8.2, the first inequality of (b) gives $\Psi^{(1)}(t_1)$. Because (a) holds, Proposition 9.4(2) is applicable, and the second inequality of (b) gives $\Psi^{(2)}(t_1)$. Hence $\Phi(t_1,t_2)$. $\blacksquare$

**Remark 10.3 (the staging of the proof is load-bearing).** Proposition 9.4(2) carries (a) as a hypothesis, and (a) is one of the three conclusions being derived in the $(\Rightarrow)$ direction. The argument is not circular because the derivation is strictly staged: $\Phi\Rightarrow$ (a) — by Step 1, which uses only the conjuncts $F_x=F_y=0$ — and only then is Proposition 9.4(2) invoked to obtain the second half of (b). Interchanging Steps 1 and 4 would be circular. No analogous risk arises for $\Psi^{(1)}$, since Proposition 8.2 is unconditional. The one remaining gap — that $\Psi^{(2)}$ is a *total* predicate, evaluable, and by Proposition 9.4(3) in fact *true*, at parameters where $s^\star$ is undefined — is closed by Lemma 9.2: at such $t_1$ both sides of the asserted equivalence are false, the left because $F_x=F_y=0$ is unattainable there, the right because (a) fails.

---

## 11. Soundness and relative completeness

**Corollary 11.1 (soundness).** If $\Phi(t_1,t_2)$ holds for some $(t_1,t_2)\in\mathbb R^2$, then $q:=\Theta(t_1,t_2)$ satisfies (a), (b) and (c). Equivalently, the encoding never accepts a configuration violating (a), (b) or (c) as defined in §1.5.

*Proof.* This is the $(\Rightarrow)$ direction of Theorem 10.2. $\blacksquare$

*(By Remark 1.2, "admissible" means precisely (a) $\wedge$ (b) $\wedge$ (c); the adequacy of (b) as a model of physical collision-freeness is not part of this claim.)*

**Corollary 11.2 (relative completeness).** $\Theta$ restricts to a bijection
$$\bigl\{(t_1,t_2)\in\mathbb R^2:\Phi(t_1,t_2)\bigr\}\ \xrightarrow{\ \sim\ }\ \bigl\{q\in(-\pi,\pi)^2:q\ \text{admissible}\bigr\}.$$
In particular $\Phi$ is satisfiable over $\mathbb R^2$ iff some $q\in(-\pi,\pi)^2$ is admissible.

*Proof.* $\Theta:\mathbb R^2\to(-\pi,\pi)^2$ is a bijection by Lemma 2.5 and Proposition 3.3(1). By Theorem 10.2 it carries the first set onto the second, and the restriction of an injection is an injection. $\blacksquare$

**Corollary 11.3 (box restriction).** Let $\ell_i<u_i$ be finite, and put
$$\mathcal B:=[\ell_1,u_1]\times[\ell_2,u_2],\qquad \mathcal Q:=[\tau(\ell_1),\tau(u_1)]\times[\tau(\ell_2),\tau(u_2)].$$
Then:

1. the set of configurations *representable* by parameters in $\mathcal B$ is exactly $\mathcal Q$;
2. $\Theta$ restricts to a bijection
$$\bigl\{t\in\mathcal B:\Phi(t)\bigr\}\ \xrightarrow{\ \sim\ }\ \bigl\{q\in\mathcal Q:q\ \text{admissible}\bigr\}.$$

*Proof.* (1) is Proposition 3.3(2). (2): by (1) and injectivity, $\Theta$ maps $\mathcal B$ bijectively onto $\mathcal Q$; intersecting with the two sets matched by Theorem 10.2 gives the claim. $\blacksquare$

**Warning 11.4.** Statements (1) and (2) of Corollary 11.3 concern *different sets* and must not be merged. $\mathcal Q$ is the set of configurations the box can express; the set of configurations the box **accepts** is the proper subset $\{q\in\mathcal Q:q\text{ admissible}\}$. To assert that the accepted set "is $\mathcal Q$" would be to assert that every configuration in the rectangle is admissible, which is false for any instance possessing an inadmissible configuration in $\mathcal Q$ — that is, for essentially every instance.

**Warning 11.5.** Corollary 11.2 characterises the admissible configurations **in the open square $(-\pi,\pi)^2$**, not on the torus $\mathbb T$. The two are inequivalent: Theorem 12.1 exhibits data for which $\Phi$ is unsatisfiable although an admissible $q\in\mathbb T$ exists. Consequently, an inference from "$\Phi$ has no real solution" to "no admissible configuration exists" is invalid, unless the four-chart encoding of §13 is used, for which Theorem 13.5 licenses exactly that inference.

---

## 12. The single chart is genuinely incomplete

**Theorem 12.1.** Take
$$L_1=L_2=1,\qquad P^\star=(-1,-1),\qquad C=\bigl(0,-\tfrac12\bigr),\qquad
r=\tfrac15,\ \mu=\tfrac1{10}\ \bigl(\text{so }R=\tfrac3{10}\bigr),\qquad\varepsilon=\tfrac12 .$$
All data are rational and satisfy (H1)–(H3). Then:

1. the configuration $q^A:=(\pi,\ \pi/2)\in\mathbb T$ is admissible;
2. $\Phi(t_1,t_2)$ is false for every $(t_1,t_2)\in\mathbb R^2$.

Hence the encoding rejects an admissible configuration: it is sound (Corollary 11.1) but not complete on $\mathbb T$.

*Proof.* **(1).** Work with the representative $q^A=(-\pi,\pi/2)$; by Lemma 1.3 the choice is immaterial. Then $E(-\pi)=(\cos(-\pi),\sin(-\pi))=(-1,0)$ and $q_1+q_2=-\pi/2$, so
$$P(q^A)=(-1,0)+\bigl(\cos(-\tfrac\pi2),\sin(-\tfrac\pi2)\bigr)=(-1,0)+(0,-1)=(-1,-1)=P^\star,$$
so (a) holds. By Lemma 5.1, $\det J(q^A)=1\cdot1\cdot\sin(\pi/2)=1$, so $\lvert\det J\rvert=1\ge\tfrac12=\varepsilon$ and (c) holds. For (b):

*First segment.* $\mathcal S^{(1)}(q^A)=[(0,0),(-1,0)]=\{(-u,0):u\in[0,1]\}$, and
$$\bigl\lVert C-(-u,0)\bigr\rVert^2=u^2+\tfrac14,$$
minimised over $[0,1]$ at $u=0$ with value $\tfrac14$. Hence $\operatorname{dist}=\tfrac12\ge\tfrac3{10}$.

*Second segment.* $\mathcal S^{(2)}(q^A)=[(-1,0),(-1,-1)]=\{(-1,-u):u\in[0,1]\}$, and
$$\bigl\lVert C-(-1,-u)\bigr\rVert^2=1+\bigl(u-\tfrac12\bigr)^2\ge1 .$$
Hence $\operatorname{dist}\ge1\ge\tfrac3{10}$.

So (b) holds and $q^A$ is admissible.

**(2).** By Corollary 11.2 it suffices to show that no $q\in(-\pi,\pi)^2$ is admissible. We solve (a) on $(-\pi,\pi]^2$, which contains $(-\pi,\pi)^2$.

For any $q$, writing $u:=\bigl(\cos(q_1+q_2),\sin(q_1+q_2)\bigr)$,
$$
\begin{aligned}
\lVert P(q)\rVert^2&=\lVert E(q_1)+L_2u\rVert^2
=L_1^2+L_2^2+2L_1L_2\bigl(\cos q_1\cos(q_1+q_2)+\sin q_1\sin(q_1+q_2)\bigr)\\
&=L_1^2+L_2^2+2L_1L_2\cos q_2 .
\end{aligned}
$$
With $L_1=L_2=1$ this is $2+2\cos q_2$, while $\lVert P^\star\rVert^2=2$. So (a) forces $\cos q_2=0$, i.e. $q_2\in\{\pi/2,-\pi/2\}$ within $(-\pi,\pi]$.

*Case $q_2=\pi/2$.* Here $\cos(q_1+\pi/2)=-\sin q_1$ and $\sin(q_1+\pi/2)=\cos q_1$, so
$$P(q)=\bigl(\cos q_1-\sin q_1,\ \sin q_1+\cos q_1\bigr).$$
Setting this equal to $(-1,-1)$ and adding the two scalar equations gives $2\cos q_1=-2$, so $\cos q_1=-1$ and hence $\sin q_1=0$; both original equations are then satisfied, since $-1-0=-1$ and $0+(-1)=-1$. Thus $q_1\equiv\pi\pmod{2\pi}$, i.e. $q_1=\pi$ within $(-\pi,\pi]$. This is $q^A$, and $q_1=\pi\notin(-\pi,\pi)$, so this solution lies outside $\operatorname{im}\Theta$.

*Case $q_2=-\pi/2$.* Here $\cos(q_1-\pi/2)=\sin q_1$ and $\sin(q_1-\pi/2)=-\cos q_1$, so
$$P(q)=\bigl(\cos q_1+\sin q_1,\ \sin q_1-\cos q_1\bigr).$$
Setting this equal to $(-1,-1)$ and adding gives $2\sin q_1=-2$, so $\sin q_1=-1$ and $\cos q_1=0$, i.e. $q_1=-\pi/2$. Call this configuration $q^B=(-\pi/2,-\pi/2)\in(-\pi,\pi)^2$. Its elbow is $E(-\pi/2)=(0,-1)$, so
$$\mathcal S^{(1)}(q^B)=[(0,0),(0,-1)]=\{(0,-u):u\in[0,1]\}\ \ni\ \bigl(0,-\tfrac12\bigr)=C$$
(take $u=\tfrac12$). Hence $\operatorname{dist}(C,\mathcal S^{(1)}(q^B))=0<\tfrac3{10}=R$, and $q^B$ violates (b).

So on $(-\pi,\pi]^2$ the only solutions of (a) are $q^A$, which lies outside the chart, and $q^B$, which is inadmissible. Therefore no $q\in(-\pi,\pi)^2$ is admissible, and by Corollary 11.2, $\Phi$ is unsatisfiable. $\blacksquare$

**Remark 12.2.** The obstruction is not a set-theoretic nicety about a boundary point. On this instance the encoding reports "no witness" while an admissible, non-singular, clearance-respecting configuration exists. Note further that the two inverse-kinematics branches genuinely differ in clearance ($q^A$ clears the obstacle, $q^B$ passes through it), so one cannot argue that a chart-excluded solution always possesses a representable twin. Remark 13.6 shows how this instance is recovered.

---

## 13. Full completeness on the torus: the four-chart encoding

The image of $\Theta$ omits the classes with $q_1\equiv\pi$ or $q_2\equiv\pi$. We recover all of $\mathbb T$ using four copies of the *same* predicate, differing only in the signs of $L_1,L_2$. This is where (H1) is used in the form $L_i\neq0$ rather than $L_i>0$.

**Notation 13.1.** For $\lambda=(\lambda_1,\lambda_2)$ with $\lambda_1\lambda_2\neq0$, let $E_\lambda,P_\lambda,J_\lambda,\mathcal S^{(1)}_\lambda,\mathcal S^{(2)}_\lambda$ and the conditions (a)$_\lambda$, (b)$_\lambda$, (c)$_\lambda$ be defined as in §1 with $(L_1,L_2)$ replaced by $\lambda$ and the remaining data $C,P^\star,R,\varepsilon$ unchanged; call $q$ *$\lambda$-admissible* accordingly. Let $\Phi_\lambda$ be the predicate of Definition 10.1 built from $\lambda$. Since $\lambda_i\neq0$, hypotheses (H1)–(H3) hold for $\lambda$, so **every result of §§3–12 applies verbatim to $\Phi_\lambda$**. (The only points at which a sign could conceivably intervene are Lemmas 9.2 and 9.3, where the length of the second link appears as $\lvert\lambda_2\rvert$; and Corollary 5.4, where the feasibility threshold is $\lvert\lambda_1\lambda_2\rvert$.)

For $\delta=(\delta_1,\delta_2)\in\{0,\pi\}^2$ put
$$\eta_i:=\begin{cases}+1,&\delta_i=0,\\-1,&\delta_i=\pi,\end{cases}
\qquad\text{and}\qquad
\lambda(\delta):=\bigl(\eta_1L_1,\ \eta_1\eta_2L_2\bigr).$$
Explicitly,
$$\lambda(0,0)=(L_1,L_2),\quad\lambda(\pi,0)=(-L_1,-L_2),\quad\lambda(0,\pi)=(L_1,-L_2),\quad\lambda(\pi,\pi)=(-L_1,L_2),$$
so the four values of $\lambda(\delta)$ are exactly the four sign choices $(\pm L_1,\pm L_2)$.

**Lemma 13.2 (shifting by $\pi$ equals flipping signs).** For every $q\in\mathbb R^2$ and every $\delta\in\{0,\pi\}^2$, writing $\lambda:=\lambda(\delta)$:
$$E_L(q_1+\delta_1)=E_\lambda(q_1),\qquad P_L(q+\delta)=P_\lambda(q),\qquad\det J_L(q+\delta)=\det J_\lambda(q).$$
Consequently $\mathcal S^{(i)}_L(q+\delta)=\mathcal S^{(i)}_\lambda(q)$ for $i=1,2$, and
$$q+\delta\ \text{is }L\text{-admissible}\iff q\ \text{is }\lambda(\delta)\text{-admissible}.$$

*Proof.* Throughout we use $\cos(\alpha+\pi)=-\cos\alpha$ and $\sin(\alpha+\pi)=-\sin\alpha$, which give
$$\bigl(\cos(\alpha+\delta_i),\sin(\alpha+\delta_i)\bigr)=\eta_i\bigl(\cos\alpha,\sin\alpha\bigr).$$

*Elbow.* $E_L(q_1+\delta_1)=L_1\bigl(\cos(q_1+\delta_1),\sin(q_1+\delta_1)\bigr)=\eta_1L_1\bigl(\cos q_1,\sin q_1\bigr)=E_\lambda(q_1)$, since $\lambda_1=\eta_1L_1$.

*Tool.* The second summand of $P_L(q+\delta)$ is
$$L_2\bigl(\cos(q_1+q_2+\delta_1+\delta_2),\ \sin(q_1+q_2+\delta_1+\delta_2)\bigr)=\eta_1\eta_2L_2\bigl(\cos(q_1+q_2),\sin(q_1+q_2)\bigr),$$
and $\lambda_2=\eta_1\eta_2L_2$. Adding the elbow term computed above,
$$P_L(q+\delta)=E_\lambda(q_1)+\lambda_2\bigl(\cos(q_1+q_2),\sin(q_1+q_2)\bigr)=P_\lambda(q).$$

*Jacobian.* By Lemma 5.1, $\det J_L(q+\delta)=L_1L_2\sin(q_2+\delta_2)=\eta_2L_1L_2\sin q_2$. On the other hand $\lambda_1\lambda_2=\eta_1L_1\cdot\eta_1\eta_2L_2=\eta_2L_1L_2$ because $\eta_1^2=1$, so $\det J_\lambda(q)=\lambda_1\lambda_2\sin q_2=\eta_2L_1L_2\sin q_2$ as well.

*Segments and conditions.* $\mathcal S^{(1)}_L(q+\delta)=[O,E_L(q_1+\delta_1)]=[O,E_\lambda(q_1)]=\mathcal S^{(1)}_\lambda(q)$, and $\mathcal S^{(2)}_L(q+\delta)=[E_L(q_1+\delta_1),P_L(q+\delta)]=[E_\lambda(q_1),P_\lambda(q)]=\mathcal S^{(2)}_\lambda(q)$. Since $C,P^\star,R,\varepsilon$ are unchanged, (a)$_L$ holds at $q+\delta$ iff (a)$_\lambda$ holds at $q$, and likewise for (b) and (c). $\blacksquare$

**Lemma 13.3 (the four charts cover $\mathbb T$; none is redundant).** For $\delta\in\{0,\pi\}^2$ put
$$U_\delta:=\bigl\{\Theta(t)+\delta\bmod2\pi\ :\ t\in\mathbb R^2\bigr\}\subseteq\mathbb T .$$
Then, with classes taken mod $2\pi$,
$$U_\delta=\bigl\{q\in\mathbb T:\ q_1\neq\pi+\delta_1\ \text{ and }\ q_2\neq\pi+\delta_2\bigr\},\qquad
\bigcup_{\delta\in\{0,\pi\}^2}U_\delta=\mathbb T,$$
and no three of the four sets cover $\mathbb T$.

*Proof.* By Proposition 3.3(1), $\operatorname{im}\Theta=(-\pi,\pi)^2$, whose image in $\mathbb T$ is $\{q:q_1\neq\pi,\ q_2\neq\pi\}$; translating by $\delta$ gives the displayed description of $U_\delta$.

*Covering.* Suppose some $q\in\mathbb T$ lay in no $U_\delta$. Then for every $\delta$ we would have $q_1=\pi+\delta_1$ or $q_2=\pi+\delta_2$. Taking $\delta=(0,0)$ gives $q_1=\pi$ or $q_2=\pi$; by the symmetry of the argument in the two coordinates we may assume $q_1=\pi$. Taking $\delta=(\pi,0)$ gives $q_1=0$ or $q_2=\pi$; since $q_1=\pi\neq0$, we get $q_2=\pi$. Taking $\delta=(\pi,\pi)$ gives $q_1=0$ or $q_2=0$; but $q_1=\pi\neq0$ and $q_2=\pi\neq0$ — a contradiction. Hence $\bigcup_\delta U_\delta=\mathbb T$.

*Non-redundancy.* The class $(\pi,\pi)$ lies in $U_{(\pi,\pi)}$ and in no other $U_\delta$: for $\delta_1=0$ it fails $q_1\neq\pi$, and for $\delta_2=0$ it fails $q_2\neq\pi$. Likewise $(\pi,0)$ lies only in $U_{(\pi,0)}$, $(0,\pi)$ only in $U_{(0,\pi)}$, and $(0,0)$ only in $U_{(0,0)}$. So each of the four sets contains a point contained in no other. $\blacksquare$

**Definition 13.4.** The **four-chart encoding** is the disjunction
$$\Phi^{\mathbb T}:\qquad\bigvee_{\delta\in\{0,\pi\}^2}\ \exists\,t\in\mathbb R^2:\ \Phi_{\lambda(\delta)}(t),$$
i.e. satisfiability of at least one of $\Phi_{(L_1,L_2)},\ \Phi_{(-L_1,-L_2)},\ \Phi_{(L_1,-L_2)},\ \Phi_{(-L_1,L_2)}$.

**Theorem 13.5 (full completeness on the torus).** Assume (H1)–(H3). There exists an $L$-admissible $q\in\mathbb T$ **iff** $\Phi^{\mathbb T}$ holds, i.e. iff at least one of the four predicates $\Phi_{\pm L_1,\pm L_2}$ has a real solution.

*Proof.* $(\Leftarrow)$ Suppose $\Phi_{\lambda(\delta)}(t)$ holds for some $\delta$ and $t\in\mathbb R^2$. Since $\lambda(\delta)$ satisfies (H1)–(H3), Theorem 10.2 applies to $\Phi_{\lambda(\delta)}$ and shows that $q:=\Theta(t)$ is $\lambda(\delta)$-admissible. By Lemma 13.2, $q+\delta$ is $L$-admissible.

$(\Rightarrow)$ Suppose $\hat q\in\mathbb T$ is $L$-admissible. By Lemma 13.3 there are $\delta\in\{0,\pi\}^2$ and $t\in\mathbb R^2$ with $\hat q=\Theta(t)+\delta$ in $\mathbb T$. By Lemma 13.2, applied with $q:=\Theta(t)$, the configuration $\Theta(t)$ is $\lambda(\delta)$-admissible. By Theorem 10.2 applied to $\Phi_{\lambda(\delta)}$, we conclude $\Phi_{\lambda(\delta)}(t)$. $\blacksquare$

**Remark 13.6 (the instance of Theorem 12.1 is recovered).** For the data of Theorem 12.1, take $\delta=(\pi,0)$, so $\lambda(\delta)=(-1,-1)$, and $t=(0,1)$, so that $\Theta(t)=(0,\pi/2)$ and $\Theta(t)+\delta=(\pi,\pi/2)=q^A$. Theorem 12.1(1) states that $q^A$ is $L$-admissible; by Lemma 13.2 the configuration $(0,\pi/2)$ is $(-1,-1)$-admissible; by Theorem 10.2 applied to $\Phi_{(-1,-1)}$ we obtain $\Phi_{(-1,-1)}(0,1)$. Thus the four-chart encoding finds precisely the witness the single chart misses.

**Remark 13.7 (what Theorem 13.5 obliges).** Theorem 13.5 concerns four *separate* instantiations of Definition 10.1: each $\Phi_\lambda$ has its own $F_x,F_y,G,\Psi^{(1)},\Psi^{(2)}$, obtained by substituting $\lambda_i$ for $L_i$ throughout Definitions 4.1, 5.2, 7.1, 8.1 and 9.1. Nothing may be shared between them beyond the data $C,P^\star,R,\varepsilon$. An alternative route to the torus is to replace the half-angle chart by the algebraic parametrisation $(\cos q_i,\sin q_i)=(a_i,b_i)$ subject to $a_i^2+b_i^2=1$, which is a bijection onto $\mathbb T$ and also keeps everything polynomial; but that is not a substitution into $\Phi$. There $D_i\equiv1$, so every denominator-clearing step of §§4–9 and every power of $D_i$ in $\Psi^{(1)},\Psi^{(2)}$ must be re-derived and an analogue of Theorem 10.2 re-proved, at the cost of two extra variables and two extra equations. The four-chart route requires no new proof beyond Lemmas 13.2 and 13.3.

---

## 14. Exact stability of the case split

The selectors of Corollary 6.2 use non-strict inequalities and therefore overlap at $s^\star\in\{0,1\}$. This section determines exactly what a change of strictness costs, and exactly where.

**Setting 14.1.** Write the four *boundary inequalities* of Corollary 6.2 as
$$\beta_1:\ s^\star\le0\quad(\text{in }\sigma_{\mathrm I}),\qquad
\beta_2:\ s^\star\ge1\quad(\text{in }\sigma_{\mathrm{II}}),\qquad
\beta_3:\ s^\star\ge0,\qquad \beta_4:\ s^\star\le1\quad(\text{both in }\sigma_{\mathrm{III}}).$$
For $T\subseteq\{\beta_1,\beta_2,\beta_3,\beta_4\}$ let $\sigma^T_k$ be obtained from $\sigma_k$ by replacing each $\beta_j\in T$ by its strict version. Say a family $\{\sigma'_k\}$ **covers** if for every $s\in\mathbb R$ at least one $\sigma'_k$ holds at $s^\star=s$.

**Theorem 14.2 (soundness is monotone).** Let $\sigma'_{\mathrm I},\sigma'_{\mathrm{II}},\sigma'_{\mathrm{III}}$ be any predicates with $\sigma'_k\Rightarrow\sigma_k$. Then, in the setting of Lemma 6.1 with $R\ge0$,
$$\bigvee_k\bigl(\sigma'_k\wedge d_k^2\ge R^2\bigr)\ \Longrightarrow\ \operatorname{dist}\bigl(C,[A,B]\bigr)\ge R .$$
In particular **no** tightening of the selectors — including every $T$ of Setting 14.1 — can make the encoding unsound.

*Proof.* Suppose $\sigma'_k$ and $d_k^2\ge R^2$ hold for some $k$. Then $\sigma_k$ holds, so $d_k^2=d^2$ by Lemma 6.1(1)–(3), whence $d^2\ge R^2$; conclude by Lemma 2.3 as in the proof of Corollary 6.2. $\blacksquare$

**Theorem 14.3 (completeness is equivalent to covering).** Let $\sigma'_k\Rightarrow\sigma_k$. The implication
$$\operatorname{dist}\bigl(C,[A,B]\bigr)\ge R\ \Longrightarrow\ \bigvee_k\bigl(\sigma'_k\wedge d_k^2\ge R^2\bigr)$$
holds for **all** $A,B,C\in\mathbb R^2$ with $B\neq A$ and all $R\ge0$ **iff** $\{\sigma'_k\}$ covers.

*Proof.* $(\Leftarrow)$ If $\{\sigma'_k\}$ covers then, for the given data, some $\sigma'_k$ holds; then $\sigma_k$ holds, so $d_k^2=d^2\ge R^2$ by Lemma 6.1(1)–(3) and Lemma 2.3.

$(\Rightarrow)$ Suppose some $s_0\in\mathbb R$ is covered by no $\sigma'_k$. Take
$$A:=(0,0),\qquad B:=(1,0),\qquad C:=(s_0,1),\qquad R:=0,$$
which is admissible data since $R\ge0$. Then $v=(1,0)\neq0$, $w=(s_0,1)$, $v\cdot v=1$ and $s^\star=w\cdot v=s_0$. The hypothesis $\operatorname{dist}\ge0$ holds trivially, but no $\sigma'_k$ holds at $s^\star=s_0$, so the disjunction is false and the implication fails. $\blacksquare$

**Theorem 14.4 (which tightenings preserve covering).** With Setting 14.1, the family $\{\sigma^T_k\}$ covers **iff**
$$\{\beta_1,\beta_3\}\not\subseteq T\qquad\text{and}\qquad\{\beta_2,\beta_4\}\not\subseteq T .$$

*Proof.* $(\Rightarrow$, contrapositive$)$ If $\{\beta_1,\beta_3\}\subseteq T$, evaluate at $s=0$: $\sigma^T_{\mathrm I}$ requires $s<0$, false; $\sigma^T_{\mathrm{II}}$ requires $s\ge1$ or $s>1$, false; $\sigma^T_{\mathrm{III}}$ requires $s>0$, false. So $s=0$ is uncovered. Symmetrically, if $\{\beta_2,\beta_4\}\subseteq T$ then $s=1$ is uncovered.

$(\Leftarrow)$ Assume neither pair is contained in $T$, and let $s\in\mathbb R$. If $s<0$ then $\sigma^T_{\mathrm I}$ holds, both versions of $\beta_1$ being satisfied. If $s>1$ then $\sigma^T_{\mathrm{II}}$ holds. If $0<s<1$ then $\sigma^T_{\mathrm{III}}$ holds, both versions of $\beta_3$ and of $\beta_4$ being satisfied. If $s=0$: since $\beta_1,\beta_3$ are not both in $T$, either $\beta_1\notin T$, and then $\sigma^T_{\mathrm I}$ reads $s\le0$, true; or $\beta_3\notin T$, and then $\sigma^T_{\mathrm{III}}$ requires $0\le s$ (true) together with $\beta_4$ in one of its versions ($0\le1$ or $0<1$), also true. If $s=1$: symmetrically, either $\beta_2\notin T$, and $\sigma^T_{\mathrm{II}}$ reads $s\ge1$, true; or $\beta_4\notin T$, and $\sigma^T_{\mathrm{III}}$ requires $\beta_3$ in one of its versions ($1\ge0$ or $1>0$) and $s\le1$, both true. $\blacksquare$

**Corollary 14.5.** Any *single* replacement of $\le$ by $<$ among the four boundary inequalities leaves a covering family, hence changes nothing (Theorems 14.2 and 14.3). Exactly two failure modes exist: $\{\beta_1,\beta_3\}\subseteq T$, which loses the seam $s^\star=0$, and $\{\beta_2,\beta_4\}\subseteq T$, which loses the seam $s^\star=1$.

We now compute, for the encoding of §§8–9, the exact set of parameters at which such a loss bites.

**Theorem 14.6 (the seam loci).** Define, as subsets of $\mathbb R$,
$$Z^{(1)}_0:=\bigl\{t_1:\Pi^{(1)}=0\bigr\},\qquad Z^{(1)}_1:=\bigl\{t_1:\Pi^{(1)}-L_1^2D_1=0\bigr\},$$
$$Z^{(2)}_0:=\bigl\{t_1:\Pi^{(2)}=0\bigr\},\qquad Z^{(2)}_1:=\bigl\{t_1:D_1\Pi^{(2)}-\Sigma^{(2)}=0\bigr\}.$$
By Lemma 7.6 and Proposition 7.8 these are exactly the loci where $s^\star=0$, respectively $s^\star=1$, for the two segments (for segment 2, on $\{\Sigma^{(2)}>0\}$). Then:

1. $Z^{(1)}_0=\mathbb R\iff C=O$; otherwise $\#Z^{(1)}_0\le2$.
2. $Z^{(1)}_1\neq\mathbb R$ always, and $\#Z^{(1)}_1\le2$.
3. $Z^{(2)}_0=\mathbb R\iff C=P^\star$; otherwise $\#Z^{(2)}_0\le2$.
4. $Z^{(2)}_1=\mathbb R\iff\bigl(P^\star=-C\ \text{ and }\ \lVert C\rVert=\lvert L_1\rvert\bigr)$; otherwise $\#Z^{(2)}_1\le4$.

*Proof.* Throughout, a nonzero real polynomial of degree at most $d$ has at most $d$ real roots, and $L_1\neq0$ by (H1).

(1) $\Pi^{(1)}=L_1\bigl(c_x+2c_yt_1-c_xt_1^2\bigr)$ vanishes identically iff $c_x=c_y=0$, i.e. $C=O$; otherwise it is a nonzero polynomial of degree at most $2$.

(2) $\Pi^{(1)}-L_1^2D_1=\bigl(L_1c_x-L_1^2\bigr)+2L_1c_y\,t_1-\bigl(L_1c_x+L_1^2\bigr)t_1^2$. Identical vanishing would force $L_1c_x=L_1^2$ and $L_1c_x=-L_1^2$, hence $L_1^2=0$, contradicting (H1). The degree is at most $2$.

(3) In $\Pi^{(2)}=(c_x-x)h_x+(c_y-y)h_y$ the polynomial $h_x$ has no $t_1$-term while $h_y$ has the term $2L_1t_1$; so the coefficient of $t_1$ in $\Pi^{(2)}$ is $2L_1(c_y-y)$, and $\Pi^{(2)}\equiv0$ forces $c_y=y$. Then $\Pi^{(2)}=(c_x-x)h_x$, and $h_x=(L_1-x)-(L_1+x)t_1^2\equiv0$ would force $x=L_1$ and $x=-L_1$, hence $L_1=0$; so $c_x=x$. Thus $\Pi^{(2)}\equiv0\iff C=P^\star$. Otherwise the degree is at most $2$.

(4) By Lemma 7.3(5) and Lemma 7.3(2),(3),
$$D_1\Pi^{(2)}-\Sigma^{(2)}=\mathbf g\cdot\mathbf h=D_1^2\bigl(C-E(q_1)\bigr)\cdot\bigl(E(q_1)-P^\star\bigr),$$
a polynomial in $t_1$ of degree at most $4$. Since $D_1^2>0$, it vanishes identically iff
$$\bigl(C-E(q_1)\bigr)\cdot\bigl(E(q_1)-P^\star\bigr)=0\qquad\text{for all }t_1 .$$
Expanding and using $\lVert E(q_1)\rVert^2=L_1^2$ (Lemma 7.3(1)),
$$\bigl(C-E\bigr)\cdot\bigl(E-P^\star\bigr)=E\cdot(C+P^\star)-C\cdot P^\star-L_1^2 .$$
Put $K:=C+P^\star=(K_x,K_y)$ and $\kappa:=C\cdot P^\star+L_1^2$. Multiplying by $D_1>0$ and using $E=\mathbf e/D_1$, identical vanishing is equivalent to
$$\mathbf e\cdot K-\kappa D_1=\bigl(L_1K_x-\kappa\bigr)+2L_1K_y\,t_1-\bigl(L_1K_x+\kappa\bigr)t_1^2\equiv0 .$$
Since $L_1\neq0$, the coefficient of $t_1$ gives $K_y=0$, and the remaining two coefficients give $L_1K_x=\kappa$ and $L_1K_x=-\kappa$, hence $\kappa=0$ and then $K_x=0$. So $K=0$, i.e. $P^\star=-C$; and then
$$\kappa=C\cdot(-C)+L_1^2=L_1^2-\lVert C\rVert^2=0,$$
i.e. $\lVert C\rVert=\lvert L_1\rvert$. Conversely, if $P^\star=-C$ and $\lVert C\rVert=\lvert L_1\rvert$ then $K=0$ and $\kappa=0$, so all three coefficients vanish. If the polynomial is not identically zero it has degree at most $4$, hence at most $4$ roots. $\blacksquare$

**Theorem 14.7 (where a lost seam bites).** Suppose the tightening $T$ loses a seam, as classified in Corollary 14.5.

1. **Generic parameters.** If $C\neq O$, $C\neq P^\star$, and it is not the case that both $P^\star=-C$ and $\lVert C\rVert=\lvert L_1\rvert$, then all four loci of Theorem 14.6 are finite, of cardinality at most $4$. Hence the set of $t_1$ at which the tightened encoding can wrongly reject is finite, and any probability measure on $\mathbb R$ without atoms assigns it probability $0$.
2. **Deterministic sampling is not covered by (1).** A grid is not a random sample, and finiteness says nothing about whether a grid meets a finite set. Concretely, if $c_x=0$ then $\Pi^{(1)}(0)=L_1c_x=0$, so $0\in Z^{(1)}_0$, and $t_1=0$ belongs to every grid symmetric about the origin. Whether a grid search detects a lost seam therefore depends on the instance, in both directions.
3. **The endpoint degeneracies.** If $C=O$ then $\operatorname{dist}(C,\mathcal S^{(1)}(q))=0$ for every $q$; if $C=P^\star$ then, under (a), $\operatorname{dist}(C,\mathcal S^{(2)}(q))=0$. Hence if $R>0$ no configuration is admissible and nothing can be wrongly rejected. If $R=0$, the corresponding half of (b) holds for every $q$, while by Theorem 14.6(1),(3) the seam locus is all of $\mathbb R$; the tightened selector family then fires nowhere, exactly as in (4), and rejection occurs on all of $\mathbb R$.
4. **The Thales degeneracy is neither finite nor vacuous.** Suppose $P^\star=-C$ and $\lVert C\rVert=\lvert L_1\rvert$, so that $Z^{(2)}_1=\mathbb R$ by Theorem 14.6(4), and suppose $T\supseteq\{\beta_2,\beta_4\}$ for segment 2. Then the tightened $\Psi^{(2)}$ is identically false, so the tightened $\Phi$ is unsatisfiable — while admissible configurations may exist (Example 14.8). The rejection therefore occurs on a set of full measure, not a null set.

*Proof.* (1) is Theorem 14.6. (2) is the displayed computation.

(3) If $C=O$ then $C$ is an endpoint of $\mathcal S^{(1)}(q)$ for every $q$, so the distance is $0$; if $C=P^\star$ then, under (a), $C=P^\star=P(q)$ is an endpoint of $\mathcal S^{(2)}(q)$, so again $0$. If $R>0$ then (b) fails for every $q$. If $R=0$, the argument of (4) applies with $\Pi^{(1)}\equiv0$ (resp. $\Pi^{(2)}\equiv0$): the tightened $\sigma_{\mathrm I}$ requires $\Pi<0$ and the tightened lower bound of $\sigma_{\mathrm{III}}$ requires $\Pi>0$, both false, while $\sigma_{\mathrm{II}}$ requires $\Pi^{(1)}-L_1^2D_1\ge0$, i.e. $-L_1^2D_1\ge0$, false (resp. $D_1\Pi^{(2)}-\Sigma^{(2)}=-\Sigma^{(2)}\ge0$, which forces $\Sigma^{(2)}=0$, whence no $t_2$ realises (a) by Lemma 9.2).

(4) Let $t_1$ be such that $\Sigma^{(2)}(t_1)>0$. By Theorem 14.6(4), $D_1\Pi^{(2)}-\Sigma^{(2)}=0$, i.e. $s^\star=1$ by Lemma 7.6; hence
$$\Pi^{(2)}=\frac{s^\star\Sigma^{(2)}}{D_1}=\frac{\Sigma^{(2)}}{D_1}>0 .$$
Therefore the first clause of the tightened $\Psi^{(2)}$ fails, since it requires $\Pi^{(2)}\le0$; the second fails, since the tightened $\beta_2$ requires $D_1\Pi^{(2)}-\Sigma^{(2)}>0$; and the third fails, since the tightened $\beta_4$ requires $\Sigma^{(2)}-D_1\Pi^{(2)}>0$. So the tightened $\Psi^{(2)}(t_1)$ is false. If instead $\Sigma^{(2)}(t_1)=0$, then by Lemma 9.2 no $t_2$ makes $(t_1,t_2)$ satisfy (a), so $F_x=F_y=0$ fails there. In either case the tightened $\Phi$ fails at $(t_1,t_2)$ for every $t_2$, so it is unsatisfiable. $\blacksquare$

**Example 14.8 (the Thales degeneracy is realisable).** Take
$$L_1=L_2=1,\qquad C=(1,0),\qquad P^\star=(-1,0),\qquad R=\tfrac12,\qquad\varepsilon=\tfrac12 .$$
Then $P^\star=-C$ and $\lVert C\rVert=1=\lvert L_1\rvert$, so $Z^{(2)}_1=\mathbb R$ by Theorem 14.6(4). The configuration $q:=(2\pi/3,\ 2\pi/3)\in(-\pi,\pi)^2$ is admissible:

* By the sum-to-product identities, $\cos q_1+\cos(q_1+q_2)=2\cos\frac{q_2}2\cos\bigl(q_1+\frac{q_2}2\bigr)$ and $\sin q_1+\sin(q_1+q_2)=2\cos\frac{q_2}2\sin\bigl(q_1+\frac{q_2}2\bigr)$. Here $2\cos\frac{q_2}2=2\cos\frac\pi3=1$ and $q_1+\frac{q_2}2=\pi$, so $P(q)=(\cos\pi,\sin\pi)=(-1,0)=P^\star$ and (a) holds.
* By Lemma 5.1, $\lvert\det J(q)\rvert=\lvert\sin(2\pi/3)\rvert=\tfrac{\sqrt3}2\ge\tfrac12$, so (c) holds.
* $E(2\pi/3)=\bigl(-\tfrac12,\tfrac{\sqrt3}2\bigr)$. For segment 1, $s^\star=C\cdot E(q_1)/L_1^2=-\tfrac12\le0$, so by Lemma 6.1(1) the distance is $\lVert C-O\rVert=1\ge\tfrac12$.
* For segment 2, with $A=P^\star$ we get $v=E(q_1)-P^\star=\bigl(\tfrac12,\tfrac{\sqrt3}2\bigr)$ and $w=C-P^\star=(2,0)$, so $v\cdot v=1$, $w\cdot v=1$ and $s^\star=1$; by Lemma 6.1(2) the distance is $\lVert C-E(q_1)\rVert=\bigl\lVert\bigl(\tfrac32,-\tfrac{\sqrt3}2\bigr)\bigr\rVert=\sqrt3\ge\tfrac12$.

So (b) holds. Since $q\in(-\pi,\pi)^2$, Theorem 10.2 gives $\Phi(t)$ for $t=(\sqrt3,\sqrt3)$, as $\tan(\pi/3)=\sqrt3$. By Theorem 14.7(4), a simultaneous strictening of segment 2's two seam-$1$ inequalities would reject this witness — and every other.

**Corollary 14.9 (what a test suite can and cannot decide).** By Theorem 14.2 no test can exhibit a soundness failure caused by tightening, because there is none. By Theorems 14.3–14.4 the only detectable failure is the loss of the seam $s^\star=0$ or $s^\star=1$ in one of the two segments. A test for the loss of a given seam is conclusive only if the test instance is **independently certified admissible**: if the constructed configuration is inadmissible, the encoding correctly rejects it and the test passes vacuously, detecting nothing. Accordingly a correct suite consists, for each of the two segments and each of the two seams, of an instance for which

1. the seam value $s^\star\in\{0,1\}$ is attained at a specific $t_1$, and
2. the configuration $\Theta(t_1,t_2)$ is verified to satisfy (a), (b), (c) by an argument independent of $\Psi^{(1)}$ and $\Psi^{(2)}$,

as in Example 14.8 and Theorem 12.1(1). Solving $\Pi^{(1)}(t_1)=0$, or $\Pi^{(1)}(t_1)=L_1^2D_1(t_1)$, for $(c_x,c_y)$ at a chosen $t_1$ — a single linear equation in two unknowns, hence always solvable over $\mathbb Q$ for rational $t_1$ — supplies (1) but never (2); (2) must be established separately.

---

## 15. Scope

**Established above, from (H1)–(H3) and nothing else.**

* Unconditional positivity of the chart denominators, and the exact scope cost of the chart (Prop. 3.1, Cor. 3.2, Prop. 3.3).
* The rationalised forward kinematics, with the monomial expansion verified coefficient by coefficient (Lemma 4.2, Prop. 4.3).
* $\det J=L_1L_2\sin q_2$; the singularity polynomial $G$; and the feasibility criterion $\varepsilon\le\lvert L_1L_2\rvert$, including the exceptional case $\varepsilon=0$ (Lemma 5.1, Prop. 5.3, Cor. 5.4).
* The point-to-segment case split, with seam agreement and covering, and its correctness as a disjunction with overlapping selectors (Lemma 6.1, Cor. 6.2).
* The unconditional rational identities, and a uniform treatment of both segments from which the sharing of the elbow predicate follows as a theorem (Lemma 7.3, Lemma 7.6, Cor. 7.7, Prop. 7.8).
* Segment 1, unconditionally (Prop. 8.2).
* Segment 2, conditionally on (a), together with the exact failure mode of $\Psi^{(2)}$ outside that hypothesis (Lemmas 9.2, 9.3, Prop. 9.4, Rem. 9.5).
* The main equivalence, with an explicitly staged, non-circular derivation (Thm. 10.2, Rem. 10.3).
* Soundness, relative completeness, and the correct statement of the box restriction (Cor. 11.1–11.3, Warnings 11.4–11.5).
* Failure of completeness on the torus for the single chart, by explicit rational counterexample (Thm. 12.1).
* Restoration of completeness on the torus by four sign-flipped copies of the same predicate (Lemmas 13.2–13.3, Thm. 13.5).
* An exact stability analysis of the case split, including the degenerate families at which the naive expectation of a null failure set is wrong (Thms. 14.2–14.7, Ex. 14.8, Cor. 14.9).

**Not addressed here.**

* Whether condition (b) is an adequate model of physical collision-freeness (Remark 1.2). Link thickness, joint geometry, and the region swept during motion all lie outside (b), and no statement above concerns them.
* Robustness over an interval of link lengths or over a task-region box, and any sums-of-squares treatment of a robust singularity margin. Every statement above is for *fixed* data.
* The behaviour of any solver applied to $\Phi$. Theorem 10.2 is a statement about $\Phi$ **as written**; whether a solver's normalisation of the disjunctions preserves it is a separate obligation. By Theorem 14.2, any tightening of the selectors performed by a preprocessor is safe for soundness; by Theorems 14.3–14.7 it is unsafe for completeness in precisely the two ways classified there.
* The correspondence between $\Phi$ as given in Definition 10.1 and the predicates constructed in any particular implementation. That verification is symbol-by-symbol against Definitions 4.1, 5.2, 7.1, 8.1, 9.1 and the degree table of Lemma 7.4, and it is not discharged by any statement in this document.
