# Rigorous Soundness Proof for the Planar-2R Exact-Witness Polynomial Encoding

## Theorem

Let

\[
L_1,L_2>0,\qquad r\ge 0,\qquad \mu>0,\qquad \varepsilon>0,
\]

and let

\[
x,y,c_x,c_y\in\mathbf R.
\]

Set

\[
R:=r+\mu>0.
\]

For \(i=1,2\), let \(t_i\in\mathbf R\), and define

\[
D_i:=1+t_i^2,\qquad
C_i:=1-t_i^2,\qquad
S_i:=2t_i.
\]

Define the corresponding joint angles by

\[
q_i:=2\arctan(t_i)\in(-\pi,\pi).
\]

Then

\[
t_i=\tan\frac{q_i}{2},
\qquad
\cos q_i=\frac{C_i}{D_i},
\qquad
\sin q_i=\frac{S_i}{D_i}.
\]

Let the planar two-link manipulator have shoulder

\[
p_0:=(0,0),
\]

elbow

\[
p_1
:=
L_1(\cos q_1,\sin q_1),
\]

and tool point

\[
p_2
:=
p_1+
L_2
\bigl(
\cos(q_1+q_2),
\sin(q_1+q_2)
\bigr).
\]

Let

\[
C:=(c_x,c_y)
\]

be the center of the circular obstacle.

Define the forward-kinematics polynomials

\[
F_x
:=
xD_1D_2
-
L_1C_1D_2
-
L_2(C_1C_2-S_1S_2),
\]

and

\[
F_y
:=
yD_1D_2
-
L_1S_1D_2
-
L_2(S_1C_2+C_1S_2).
\]

Define the singularity polynomial

\[
G
:=
(4L_1^2L_2^2-2\varepsilon^2)t_2^2
-
\varepsilon^2t_2^4
-
\varepsilon^2.
\]

For the first arm segment define

\[
W_1
:=
c_xL_1C_1+c_yL_1S_1,
\]

\[
E_x:=c_xD_1-L_1C_1,
\qquad
E_y:=c_yD_1-L_1S_1,
\]

and

\[
H_{1,A}:=c_x^2+c_y^2-R^2,
\]

\[
H_{1,B}:=E_x^2+E_y^2-R^2D_1^2,
\]

\[
H_{1,I}
:=
(c_x^2+c_y^2-R^2)D_1^2L_1^2-W_1^2.
\]

Let \(\Phi_1(t_1)\) be the quantifier-free semialgebraic formula

\[
\begin{aligned}
\Phi_1:\quad
&
\bigl(
W_1\le0
\;\wedge\;
H_{1,A}\ge0
\bigr)
\\
&\vee
\bigl(
W_1-D_1L_1^2\ge0
\;\wedge\;
H_{1,B}\ge0
\bigr)
\\
&\vee
\bigl(
W_1\ge0
\;\wedge\;
D_1L_1^2-W_1\ge0
\;\wedge\;
H_{1,I}\ge0
\bigr).
\end{aligned}
\]

For the second arm segment define

\[
V_x:=L_1C_1-xD_1,
\qquad
V_y:=L_1S_1-yD_1,
\]

\[
Q_2:=V_x^2+V_y^2,
\]

and

\[
W_2:=(c_x-x)V_x+(c_y-y)V_y.
\]

Also define

\[
H_{2,A}
:=
(x-c_x)^2+(y-c_y)^2-R^2,
\]

and

\[
H_{2,I}
:=
\bigl((x-c_x)^2+(y-c_y)^2-R^2\bigr)Q_2-W_2^2.
\]

Let \(\Phi_2(t_1)\) be the quantifier-free semialgebraic formula

\[
\begin{aligned}
\Phi_2:\quad
&
\bigl(
W_2\le0
\;\wedge\;
H_{2,A}\ge0
\bigr)
\\
&\vee
\bigl(
W_2D_1-Q_2\ge0
\;\wedge\;
H_{1,B}\ge0
\bigr)
\\
&\vee
\bigl(
W_2\ge0
\;\wedge\;
Q_2-W_2D_1\ge0
\;\wedge\;
H_{2,I}\ge0
\bigr).
\end{aligned}
\]

Then, for every \((t_1,t_2)\in\mathbf R^2\),

\[
\boxed{
F_x=F_y=0,\quad
G\ge0,\quad
\Phi_1,\quad
\Phi_2
}
\]

holds if and only if the corresponding configuration \(q=(q_1,q_2)\) satisfies

\[
\boxed{
\begin{aligned}
p_2&=(x,y),\\
\operatorname{dist}(C,[p_0,p_1])&\ge R,\\
\operatorname{dist}(C,[p_1,p_2])&\ge R,\\
|\det J(q)|&\ge\varepsilon.
\end{aligned}}
\]

Thus the geometric requirements are represented exactly by a quantifier-free Boolean combination of polynomial equalities and weak polynomial inequalities in \(t_1,t_2\).

If, in addition,

\[
L_1,L_2,x,y,c_x,c_y,r,\mu,\varepsilon\in\mathbf Q,
\]

then all of the displayed polynomial predicates have coefficients in \(\mathbf Q\).

Finally, if the actual witness encoding also imposes finite rational bounds

\[
a_i\le t_i\le b_i,
\qquad
a_i,b_i\in\mathbf Q,
\qquad
a_i<b_i,
\]

and if \(\mathcal D(t_1,t_2)\) denotes the conjunction of those domain predicates, then the exact bounded-witness statement is

\[
\mathcal D\wedge
(F_x=F_y=0)\wedge(G\ge0)\wedge\Phi_1\wedge\Phi_2
\]

if and only if

\[
\mathcal D
\wedge
\bigl(p_2=(x,y)\bigr)
\wedge
\bigl(\operatorname{dist}(C,[p_0,p_1])\ge R\bigr)
\wedge
\bigl(\operatorname{dist}(C,[p_1,p_2])\ge R\bigr)
\wedge
\bigl(|\det J(q)|\ge\varepsilon\bigr).
\]

The assertion that the implementation in fact permits only such finite rational bounds is an implementation/specification assertion and is not part of the mathematical theorem proved below.

---

## Proof

### 1. The half-angle chart and denominator positivity

For every real number \(t\),

\[
1+t^2\ge1>0.
\]

Consequently,

\[
D_i=1+t_i^2>0
\]

for \(i=1,2\). In particular, none of the denominators occurring below can vanish, and every product

\[
D_1^{m_1}D_2^{m_2},
\qquad
m_1,m_2\in\mathbf Z_{\ge0},
\]

is strictly positive.

It follows that multiplication of an equality by any such product preserves equivalence, and multiplication of an inequality by any such product preserves both equivalence and the direction of the inequality.

Now let

\[
q=2\arctan t.
\]

Since

\[
\arctan t\in
\left(-\frac{\pi}{2},\frac{\pi}{2}\right),
\]

we have

\[
q\in(-\pi,\pi).
\]

Moreover,

\[
\tan\frac q2=t.
\]

Because

\[
1+\tan^2\theta=\frac1{\cos^2\theta},
\]

with \(\theta=q/2\), we obtain

\[
\cos^2\frac q2=\frac1{1+t^2}.
\]

Hence

\[
\begin{aligned}
\cos q
&=
\cos^2\frac q2-\sin^2\frac q2\\
&=
\cos^2\frac q2
\left(
1-\tan^2\frac q2
\right)\\
&=
\frac{1-t^2}{1+t^2},
\end{aligned}
\]

and

\[
\begin{aligned}
\sin q
&=
2\sin\frac q2\cos\frac q2\\
&=
2\tan\frac q2\cos^2\frac q2\\
&=
\frac{2t}{1+t^2}.
\end{aligned}
\]

Therefore

\[
\cos q_i=\frac{C_i}{D_i},
\qquad
\sin q_i=\frac{S_i}{D_i}.
\]

This proves the mathematical denominator-positivity assertion of S1.

If a finite witness interval

\[
a_i\le t_i\le b_i
\]

is imposed, then monotonicity of \(\arctan\) gives

\[
2\arctan a_i
\le
q_i
\le
2\arctan b_i.
\]

Because \(a_i,b_i\) are finite,

\[
-\pi
<
2\arctan a_i
<
2\arctan b_i
<
\pi.
\]

Thus a finite \(t_i\)-domain maps to a proper subinterval of the half-angle chart \((-\,\pi,\pi)\). In particular, it excludes \(q_i=\pm\pi\), and in fact excludes an entire neighborhood of those chart endpoints.

---

### 2. Exact rationalization of forward kinematics

By the angle-addition formulas,

\[
\cos(q_1+q_2)
=
\cos q_1\cos q_2-\sin q_1\sin q_2.
\]

Using the half-angle expressions derived above,

\[
\cos(q_1+q_2)
=
\frac{C_1C_2-S_1S_2}{D_1D_2}.
\]

Likewise,

\[
\sin(q_1+q_2)
=
\frac{S_1C_2+C_1S_2}{D_1D_2}.
\]

The first coordinate of \(p_2\) is therefore

\[
(p_2)_x
=
\frac{L_1C_1}{D_1}
+
L_2
\frac{C_1C_2-S_1S_2}{D_1D_2}.
\]

Putting both terms over the common denominator \(D_1D_2\),

\[
(p_2)_x
=
\frac{
L_1C_1D_2
+
L_2(C_1C_2-S_1S_2)
}{D_1D_2}.
\]

Since \(D_1D_2>0\), and hence \(D_1D_2\ne0\),

\[
(p_2)_x=x
\]

if and only if

\[
xD_1D_2
-
L_1C_1D_2
-
L_2(C_1C_2-S_1S_2)
=0.
\]

The latter equality is exactly

\[
F_x=0.
\]

Similarly,

\[
(p_2)_y
=
\frac{L_1S_1}{D_1}
+
L_2
\frac{S_1C_2+C_1S_2}{D_1D_2},
\]

hence

\[
(p_2)_y
=
\frac{
L_1S_1D_2+
L_2(S_1C_2+C_1S_2)
}{D_1D_2}.
\]

Therefore

\[
(p_2)_y=y
\]

if and only if

\[
F_y=0.
\]

Combining the two coordinate statements,

\[
\boxed{
F_x=F_y=0
\iff
p_2=(x,y).
}
\]

Thus clearing the denominators introduces no additional solutions and removes no solutions.

This establishes S2.

---

### 3. Exact polynomial encoding of the singularity margin

The forward-kinematics map is

\[
f(q_1,q_2)
=
\begin{pmatrix}
L_1\cos q_1+L_2\cos(q_1+q_2)\\[1mm]
L_1\sin q_1+L_2\sin(q_1+q_2)
\end{pmatrix}.
\]

Its Jacobian matrix is

\[
J(q)
=
\begin{pmatrix}
-L_1\sin q_1-L_2\sin(q_1+q_2)
&
-L_2\sin(q_1+q_2)
\\[2mm]
L_1\cos q_1+L_2\cos(q_1+q_2)
&
L_2\cos(q_1+q_2)
\end{pmatrix}.
\]

Its determinant is

\[
\begin{aligned}
\det J(q)
&=
\bigl(
-L_1\sin q_1-L_2\sin(q_1+q_2)
\bigr)
L_2\cos(q_1+q_2)
\\
&\quad
-
\bigl(
-L_2\sin(q_1+q_2)
\bigr)
\bigl(
L_1\cos q_1+L_2\cos(q_1+q_2)
\bigr).
\end{aligned}
\]

The two terms containing \(L_2^2\) cancel, so

\[
\det J(q)
=
L_1L_2
\left(
\sin(q_1+q_2)\cos q_1
-
\sin q_1\cos(q_1+q_2)
\right).
\]

Using

\[
\sin(\alpha-\beta)
=
\sin\alpha\cos\beta-\cos\alpha\sin\beta,
\]

we obtain

\[
\det J(q)=L_1L_2\sin q_2.
\]

Hence

\[
\det J(q)
=
\frac{2L_1L_2t_2}{D_2}.
\]

Because \(D_2>0\),

\[
|\det J(q)|\ge\varepsilon
\]

is equivalent to

\[
|2L_1L_2t_2|
\ge
\varepsilon D_2.
\]

Both sides are nonnegative; indeed,

\[
\varepsilon D_2>0.
\]

For nonnegative real numbers \(a,b\),

\[
a\ge b
\iff
a^2\ge b^2,
\]

because the squaring function is strictly increasing on \([0,\infty)\).

Consequently,

\[
|2L_1L_2t_2|
\ge
\varepsilon D_2
\]

if and only if

\[
4L_1^2L_2^2t_2^2
\ge
\varepsilon^2D_2^2.
\]

Since

\[
D_2^2=(1+t_2^2)^2
=
1+2t_2^2+t_2^4,
\]

this becomes

\[
4L_1^2L_2^2t_2^2
-
\varepsilon^2
-
2\varepsilon^2t_2^2
-
\varepsilon^2t_2^4
\ge0.
\]

Equivalently,

\[
G\ge0.
\]

Thus

\[
\boxed{
G\ge0
\iff
|\det J(q)|\ge\varepsilon.
}
\]

No sign branch for \(\sin q_2\) is required.

This proves S3.

---

### 4. A point-to-segment distance lemma

We now prove the geometric fact used for both arm segments.

Let \(A,B,C\in\mathbf R^2\) with \(A\ne B\). Put

\[
v:=B-A,
\qquad
w:=C-A.
\]

Since \(A\ne B\),

\[
v\cdot v=\|v\|^2>0.
\]

Define

\[
s:=\frac{w\cdot v}{v\cdot v}.
\]

Every point of the segment \([A,B]\) is uniquely of the form

\[
A+uv,
\qquad
0\le u\le1.
\]

For such \(u\),

\[
\begin{aligned}
\|C-(A+uv)\|^2
&=
\|w-uv\|^2\\
&=
\|w\|^2-2u(w\cdot v)+u^2\|v\|^2.
\end{aligned}
\]

Since

\[
w\cdot v=s\|v\|^2,
\]

we obtain

\[
\begin{aligned}
\|w-uv\|^2
&=
\|w\|^2
-
2us\|v\|^2
+
u^2\|v\|^2\\
&=
\|v\|^2(u-s)^2
+
\|w\|^2-s^2\|v\|^2\\
&=
\|v\|^2(u-s)^2
+
\|w\|^2
-
\frac{(w\cdot v)^2}{\|v\|^2}.
\end{aligned}
\]

The second term is independent of \(u\). Hence minimizing the squared distance is equivalent to minimizing

\[
(u-s)^2
\]

over \(u\in[0,1]\).

We now determine the minimizer.

If \(s\le0\), then for every \(u\in[0,1]\),

\[
u-s\ge -s\ge0,
\]

and therefore

\[
|u-s|\ge|-s|.
\]

Thus the minimum occurs at \(u=0\).

If \(0\le s\le1\), then \(u=s\) is permitted and gives

\[
(u-s)^2=0,
\]

which is the minimum possible value.

If \(s\ge1\), then for every \(u\in[0,1]\),

\[
s-u\ge s-1\ge0,
\]

hence

\[
|u-s|\ge|1-s|,
\]

and the minimum occurs at \(u=1\).

Consequently,

\[
\operatorname{dist}(C,[A,B])^2
=
\begin{cases}
\|w\|^2,
&
s\le0,
\\[2mm]
\displaystyle
\|w\|^2-
\frac{(w\cdot v)^2}{\|v\|^2},
&
0\le s\le1,
\\[4mm]
\|w-v\|^2,
&
s\ge1.
\end{cases}
\]

The cases deliberately overlap at \(s=0\) and \(s=1\). We verify that the corresponding formulas agree exactly at those seams.

If \(s=0\), then

\[
w\cdot v=0,
\]

so the interior formula becomes

\[
\|w\|^2,
\]

which is the \(s\le0\) endpoint formula.

If \(s=1\), then

\[
w\cdot v=\|v\|^2.
\]

The interior expression becomes

\[
\|w\|^2-\|v\|^2.
\]

On the other hand,

\[
\begin{aligned}
\|w-v\|^2
&=
\|w\|^2
-
2w\cdot v
+
\|v\|^2\\
&=
\|w\|^2
-
2\|v\|^2
+
\|v\|^2\\
&=
\|w\|^2-\|v\|^2.
\end{aligned}
\]

Thus the two formulas agree at \(s=1\) as well.

Finally, throughout the remainder of the proof we shall use the following elementary equivalence. Since every Euclidean distance \(d\) satisfies \(d\ge0\), and since \(R>0\),

\[
d\ge R
\iff
d^2\ge R^2.
\]

This is legitimate because squaring is strictly increasing on \([0,\infty)\).

---

### 5. Segment 1: shoulder to elbow

The elbow is

\[
p_1
=
\left(
\frac{L_1C_1}{D_1},
\frac{L_1S_1}{D_1}
\right).
\]

First,

\[
\begin{aligned}
C_1^2+S_1^2
&=
(1-t_1^2)^2+4t_1^2\\
&=
1-2t_1^2+t_1^4+4t_1^2\\
&=
1+2t_1^2+t_1^4\\
&=
(1+t_1^2)^2\\
&=
D_1^2.
\end{aligned}
\]

Hence

\[
\begin{aligned}
\|p_1\|^2
&=
\frac{L_1^2(C_1^2+S_1^2)}{D_1^2}\\
&=
L_1^2.
\end{aligned}
\]

Since \(L_1>0\),

\[
p_1\ne p_0.
\]

Thus the point-to-segment lemma applies.

Take

\[
A=p_0=(0,0),
\qquad
B=p_1.
\]

Then

\[
v=p_1,
\qquad
w=C.
\]

The scalar product is

\[
\begin{aligned}
w\cdot v
&=
c_x\frac{L_1C_1}{D_1}
+
c_y\frac{L_1S_1}{D_1}\\
&=
\frac{W_1}{D_1}.
\end{aligned}
\]

Since

\[
v\cdot v=L_1^2,
\]

the projection parameter is

\[
s
=
\frac{W_1}{D_1L_1^2}.
\]

Because

\[
D_1L_1^2>0,
\]

we obtain

\[
s\le0
\iff
W_1\le0,
\]

\[
s\ge1
\iff
W_1-D_1L_1^2\ge0,
\]

and

\[
0\le s\le1
\iff
W_1\ge0
\quad\text{and}\quad
D_1L_1^2-W_1\ge0.
\]

#### Case 1: \(s\le0\)

The nearest point is \(p_0\), so

\[
\operatorname{dist}(C,[p_0,p_1])^2
=
c_x^2+c_y^2.
\]

Hence

\[
\operatorname{dist}(C,[p_0,p_1])\ge R
\]

if and only if

\[
c_x^2+c_y^2-R^2\ge0,
\]

that is,

\[
H_{1,A}\ge0.
\]

#### Case 2: \(s\ge1\)

The nearest point is \(p_1\). We have

\[
C-p_1
=
\left(
c_x-\frac{L_1C_1}{D_1},
c_y-\frac{L_1S_1}{D_1}
\right)
=
\frac{(E_x,E_y)}{D_1}.
\]

Thus

\[
\|C-p_1\|^2
=
\frac{E_x^2+E_y^2}{D_1^2}.
\]

Since \(D_1^2>0\),

\[
\|C-p_1\|^2\ge R^2
\]

if and only if

\[
E_x^2+E_y^2-R^2D_1^2\ge0,
\]

that is,

\[
H_{1,B}\ge0.
\]

#### Case 3: \(0\le s\le1\)

The point-to-segment lemma gives

\[
\operatorname{dist}(C,[p_0,p_1])^2
=
\|C\|^2
-
\frac{(C\cdot p_1)^2}{L_1^2}.
\]

Using

\[
C\cdot p_1=\frac{W_1}{D_1},
\]

we obtain

\[
\operatorname{dist}(C,[p_0,p_1])^2
=
c_x^2+c_y^2
-
\frac{W_1^2}{D_1^2L_1^2}.
\]

Therefore the clearance condition is equivalent to

\[
c_x^2+c_y^2
-
\frac{W_1^2}{D_1^2L_1^2}
\ge
R^2.
\]

Since

\[
D_1^2L_1^2>0,
\]

this is equivalent to

\[
(c_x^2+c_y^2-R^2)D_1^2L_1^2-W_1^2\ge0,
\]

that is,

\[
H_{1,I}\ge0.
\]

The three selector ranges cover every real \(s\), and the adjacent distance formulas agree at \(s=0\) and \(s=1\). Hence the Boolean disjunction \(\Phi_1\) is equivalent to the geometric clearance condition:

\[
\boxed{
\Phi_1
\iff
\operatorname{dist}(C,[p_0,p_1])\ge R.
}
\]

This proves S4.

---

### 6. The segment-2 numerator \(Q_2\) is nonconstant

Before imposing forward kinematics, consider \(Q_2\) purely as a polynomial in \(t_1\).

Writing \(t=t_1\),

\[
\begin{aligned}
V_x
&=
L_1(1-t^2)-x(1+t^2)\\
&=
(L_1-x)-(L_1+x)t^2,
\end{aligned}
\]

and

\[
\begin{aligned}
V_y
&=
2L_1t-y(1+t^2)\\
&=
-y t^2+2L_1t-y.
\end{aligned}
\]

Thus

\[
Q_2(t)=V_x(t)^2+V_y(t)^2.
\]

The coefficient of \(t^4\) in \(Q_2\) is

\[
(L_1+x)^2+y^2.
\]

If

\[
(L_1+x)^2+y^2>0,
\]

then \(Q_2\) has degree four and is therefore nonconstant.

The only remaining possibility is

\[
(L_1+x)^2+y^2=0.
\]

A sum of two squares of real numbers is zero only when both squares vanish, so

\[
x=-L_1,
\qquad
y=0.
\]

In that case,

\[
V_x
=
L_1(1-t^2)+L_1(1+t^2)
=
2L_1,
\]

and

\[
V_y=2L_1t.
\]

Hence

\[
Q_2(t)
=
4L_1^2+4L_1^2t^2
=
4L_1^2(1+t^2).
\]

Since \(L_1>0\), this is again nonconstant.

Therefore, for every permitted \(x,y\),

\[
\boxed{Q_2(t_1)\ \text{is a nonconstant polynomial in }t_1.}
\]

This proves the nonconstancy assertion contained in S5.

Notice that \(Q_2\) is the cleared numerator of the squared segment length. It is not itself the squared segment length. The actual squared segment length is

\[
\frac{Q_2}{D_1^2}.
\]

This distinction is essential.

---

### 7. Positivity of \(Q_2\) on the forward-kinematics locus

We now prove the conditional fact required for the segment-2 case split.

Assume

\[
F_x=F_y=0.
\]

By Step 2,

\[
p_2=(x,y).
\]

Let

\[
A:=(x,y)=p_2,
\qquad
B:=p_1.
\]

By the definition of forward kinematics,

\[
p_2-p_1
=
L_2
\bigl(
\cos(q_1+q_2),
\sin(q_1+q_2)
\bigr).
\]

Therefore

\[
\begin{aligned}
\|p_2-p_1\|^2
&=
L_2^2
\left(
\cos^2(q_1+q_2)
+
\sin^2(q_1+q_2)
\right)\\
&=
L_2^2.
\end{aligned}
\]

Since \(L_2>0\),

\[
\|p_2-p_1\|^2=L_2^2>0,
\]

and hence \(p_1\ne p_2\).

Moreover,

\[
p_1-(x,y)
=
\left(
\frac{L_1C_1}{D_1}-x,
\frac{L_1S_1}{D_1}-y
\right)
=
\frac{(V_x,V_y)}{D_1}.
\]

Consequently,

\[
\|p_1-(x,y)\|^2
=
\frac{V_x^2+V_y^2}{D_1^2}
=
\frac{Q_2}{D_1^2}.
\]

Combining this with

\[
\|p_1-p_2\|^2=L_2^2
\]

and \(p_2=(x,y)\), we obtain

\[
\frac{Q_2}{D_1^2}=L_2^2.
\]

Thus, on the FK locus,

\[
\boxed{
Q_2=D_1^2L_2^2.
}
\]

Since both \(D_1\) and \(L_2\) are strictly positive,

\[
\boxed{
Q_2>0.
}
\]

This establishes the precise dependence of S5 on S2.

There is no circularity. S2 was proved independently. S5 uses S2 only to establish positivity of \(Q_2\) on the locus on which the full conjunction can possibly hold.

Formally, if \(K\) denotes the forward-kinematics proposition

\[
K:\quad F_x=F_y=0,
\]

and if \(\Psi_2\) denotes the geometric segment-2 clearance proposition, it suffices to prove

\[
K\Longrightarrow(\Phi_2\iff\Psi_2).
\]

From this implication one obtains

\[
K\wedge\Phi_2
\iff
K\wedge\Psi_2.
\]

Indeed:

- if \(K\wedge\Phi_2\) holds, then \(K\) holds and the implication gives \(\Psi_2\);
- if \(K\wedge\Psi_2\) holds, then \(K\) holds and the same equivalence gives \(\Phi_2\).

Therefore the behavior of \(\Phi_2\) away from the FK locus is irrelevant to the truth set of the complete conjunction.

---

### 8. Segment 2: elbow to tool

Continue under the hypothesis

\[
F_x=F_y=0.
\]

Then

\[
A:=(x,y)=p_2,
\qquad
B:=p_1
\]

are the endpoints of the second physical link.

Set

\[
v:=B-A,
\qquad
w:=C-A.
\]

From the definitions,

\[
v
=
\frac{(V_x,V_y)}{D_1},
\]

whereas

\[
w=(c_x-x,c_y-y).
\]

Therefore

\[
v\cdot v
=
\frac{Q_2}{D_1^2}.
\]

By Step 7,

\[
Q_2>0,
\]

so \(v\cdot v>0\), as required by the point-to-segment lemma.

Furthermore,

\[
\begin{aligned}
w\cdot v
&=
(c_x-x)\frac{V_x}{D_1}
+
(c_y-y)\frac{V_y}{D_1}\\
&=
\frac{W_2}{D_1}.
\end{aligned}
\]

Thus

\[
\begin{aligned}
s
&=
\frac{w\cdot v}{v\cdot v}\\
&=
\frac{W_2/D_1}{Q_2/D_1^2}\\
&=
\frac{W_2D_1}{Q_2}.
\end{aligned}
\]

Since

\[
D_1>0,
\qquad
Q_2>0,
\]

the sign comparisons may be cleared without reversing inequalities.

Hence

\[
s\le0
\iff
W_2\le0,
\]

because

\[
s\le0
\iff
W_2D_1\le0
\iff
W_2\le0.
\]

Also,

\[
s\ge1
\]

if and only if

\[
W_2D_1\ge Q_2,
\]

equivalently,

\[
W_2D_1-Q_2\ge0.
\]

Finally,

\[
0\le s\le1
\]

if and only if

\[
W_2\ge0
\]

and

\[
Q_2-W_2D_1\ge0.
\]

We now analyze the three geometric cases.

#### Case 1: \(s\le0\)

The nearest point on the segment is

\[
A=(x,y).
\]

Therefore

\[
\operatorname{dist}(C,[A,B])^2
=
(c_x-x)^2+(c_y-y)^2.
\]

Thus

\[
\operatorname{dist}(C,[A,B])\ge R
\]

if and only if

\[
(x-c_x)^2+(y-c_y)^2-R^2\ge0,
\]

which is

\[
H_{2,A}\ge0.
\]

#### Case 2: \(s\ge1\)

The nearest point is

\[
B=p_1.
\]

But \(B\) is precisely the elbow appearing in the endpoint-\(B\) case for segment 1. Hence

\[
C-B
=
\frac{(E_x,E_y)}{D_1}.
\]

Thus

\[
\operatorname{dist}(C,[A,B])^2
=
\frac{E_x^2+E_y^2}{D_1^2}.
\]

The clearance condition is therefore equivalent to

\[
H_{1,B}\ge0.
\]

The reuse of \(H_{1,B}\) introduces no unintended mathematical coupling: both occurrences encode the identical proposition

\[
\|C-p_1\|\ge R
\]

for the same physical elbow point \(p_1\).

#### Case 3: \(0\le s\le1\)

By the point-to-segment lemma,

\[
\operatorname{dist}(C,[A,B])^2
=
\|w\|^2
-
\frac{(w\cdot v)^2}{v\cdot v}.
\]

Now

\[
\|w\|^2
=
(c_x-x)^2+(c_y-y)^2,
\]

while

\[
(w\cdot v)^2
=
\frac{W_2^2}{D_1^2},
\]

and

\[
v\cdot v
=
\frac{Q_2}{D_1^2}.
\]

Therefore

\[
\begin{aligned}
\frac{(w\cdot v)^2}{v\cdot v}
&=
\frac{W_2^2/D_1^2}{Q_2/D_1^2}\\
&=
\frac{W_2^2}{Q_2}.
\end{aligned}
\]

Thus

\[
\operatorname{dist}(C,[A,B])^2
=
(c_x-x)^2+(c_y-y)^2-\frac{W_2^2}{Q_2}.
\]

The factors \(D_1^2\) cancel exactly. There is no residual \(D_1\) factor.

The clearance condition is therefore

\[
(c_x-x)^2+(c_y-y)^2-\frac{W_2^2}{Q_2}
\ge
R^2.
\]

Since \(Q_2>0\), multiplying by \(Q_2\) preserves equivalence and gives

\[
\bigl(
(c_x-x)^2+(c_y-y)^2-R^2
\bigr)Q_2-W_2^2
\ge0.
\]

This is exactly

\[
H_{2,I}\ge0.
\]

The three selector conditions cover every real value of \(s\). At \(s=0\) and \(s=1\), the adjacent distance formulas agree exactly by the general point-to-segment lemma proved in Step 4.

Consequently, under the forward-kinematics hypothesis,

\[
\boxed{
\Phi_2
\iff
\operatorname{dist}(C,[p_1,p_2])\ge R.
}
\]

Equivalently,

\[
\boxed{
(F_x=F_y=0)\wedge\Phi_2
\iff
(F_x=F_y=0)
\wedge
\bigl(
\operatorname{dist}(C,[p_1,p_2])\ge R
\bigr).
}
\]

This proves the mathematical content of S5.

---

### 9. Combination of the five components

We have proved:

\[
F_x=F_y=0
\iff
p_2=(x,y);
\]

\[
G\ge0
\iff
|\det J(q)|\ge\varepsilon;
\]

\[
\Phi_1
\iff
\operatorname{dist}(C,[p_0,p_1])\ge R;
\]

and

\[
(F_x=F_y=0)\wedge\Phi_2
\iff
(F_x=F_y=0)
\wedge
\bigl(
\operatorname{dist}(C,[p_1,p_2])\ge R
\bigr).
\]

We now prove the complete equivalence explicitly.

Suppose first that

\[
F_x=F_y=0,
\qquad
G\ge0,
\qquad
\Phi_1,
\qquad
\Phi_2.
\]

From

\[
F_x=F_y=0
\]

we obtain

\[
p_2=(x,y).
\]

From

\[
G\ge0
\]

we obtain

\[
|\det J(q)|\ge\varepsilon.
\]

From

\[
\Phi_1
\]

we obtain

\[
\operatorname{dist}(C,[p_0,p_1])\ge R.
\]

Finally, since both

\[
F_x=F_y=0
\]

and \(\Phi_2\) hold, the conditional segment-2 equivalence gives

\[
\operatorname{dist}(C,[p_1,p_2])\ge R.
\]

Thus all four geometric requirements hold.

Conversely, suppose that

\[
p_2=(x,y),
\]

\[
\operatorname{dist}(C,[p_0,p_1])\ge R,
\]

\[
\operatorname{dist}(C,[p_1,p_2])\ge R,
\]

and

\[
|\det J(q)|\ge\varepsilon.
\]

The forward-kinematics equivalence gives

\[
F_x=F_y=0.
\]

The singularity equivalence gives

\[
G\ge0.
\]

The segment-1 equivalence gives

\[
\Phi_1.
\]

Because

\[
F_x=F_y=0
\]

holds, the segment-2 conditional equivalence applies; from the segment-2 clearance assumption we therefore obtain

\[
\Phi_2.
\]

Hence

\[
F_x=F_y=0,
\qquad
G\ge0,
\qquad
\Phi_1,
\qquad
\Phi_2.
\]

Therefore

\[
\boxed{
\begin{aligned}
&
(F_x=F_y=0)
\wedge
(G\ge0)
\wedge
\Phi_1
\wedge
\Phi_2
\\[1mm]
&\qquad\iff
\\[1mm]
&
\bigl(p_2=(x,y)\bigr)
\wedge
\bigl(\operatorname{dist}(C,[p_0,p_1])\ge R\bigr)
\\
&\qquad\qquad
\wedge
\bigl(\operatorname{dist}(C,[p_1,p_2])\ge R\bigr)
\wedge
\bigl(|\det J(q)|\ge\varepsilon\bigr).
\end{aligned}}
\]

This proves the claimed exact soundness-and-completeness equivalence.

---

### 10. The bounded witness domain

Suppose additionally that the witness domain is specified by finite rational bounds

\[
a_i\le t_i\le b_i,
\qquad
a_i,b_i\in\mathbf Q,
\qquad
a_i<b_i,
\]

and let

\[
\mathcal D(t_1,t_2)
\]

denote their conjunction.

For arbitrary propositions \(P,Q,D\),

\[
P\iff Q
\]

implies

\[
D\wedge P
\iff
D\wedge Q.
\]

Applying this elementary propositional fact to the equivalence established in Step 9 yields

\[
\begin{aligned}
&
\mathcal D
\wedge
(F_x=F_y=0)
\wedge
(G\ge0)
\wedge
\Phi_1
\wedge
\Phi_2
\\
&\qquad\iff
\\
&
\mathcal D
\wedge
\bigl(p_2=(x,y)\bigr)
\wedge
\bigl(\operatorname{dist}(C,[p_0,p_1])\ge R\bigr)
\\
&\qquad\qquad
\wedge
\bigl(\operatorname{dist}(C,[p_1,p_2])\ge R\bigr)
\wedge
\bigl(|\det J(q)|\ge\varepsilon\bigr).
\end{aligned}
\]

Thus inclusion of the witness-domain predicates does not disturb the exact equivalence, provided the same domain restriction is included on the geometric side.

The mathematical proof does not itself establish that a particular software class accepts only finite rational intervals. That assertion is a property of the implementation or its formal specification and must be checked there separately.

---

### 11. Coefficient field

Every expression introduced above is obtained from

\[
L_1,L_2,x,y,c_x,c_y,r,\mu,\varepsilon
\]

by finitely many additions, subtractions, and multiplications.

Consequently, if all these constants lie in \(\mathbf Q\), then every polynomial occurring in

\[
F_x,\ F_y,\ G,\ \Phi_1,\ \Phi_2
\]

belongs to

\[
\mathbf Q[t_1,t_2].
\]

If \(L_1\) or \(L_2\) is an arbitrary real constant, then the same proof remains valid, but the appropriate coefficient ring is generally a subring of \(\mathbf R\), not necessarily \(\mathbf Q\).

This distinction concerns the coefficient representation of the exact checker; it does not alter the geometric equivalence proved above.

---

Hence, subject only to the explicitly stated hypotheses, the half-angle polynomial encoding is exactly equivalent to the planar-2R forward-kinematics, obstacle-clearance, and singularity-margin requirements on the represented witness domain. No denominator clearing introduces spurious solutions; no squaring step loses sign information; the clearance case splits cover all projection positions and agree at their seams; and the segment-2 division is justified precisely on the forward-kinematics locus by

\[
Q_2=D_1^2L_2^2>0.
\]

\[
\square
\]
