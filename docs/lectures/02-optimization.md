# Lecture 02a — Optimization

Source: `lectures/02/lecture02a_optimization.pdf` (56 p.), dated 2026-09-09 + 09-15 (+ 09-16). Lecturer: Martin Jaggi. Annotated version `lecture02a_optimization_annotated.pdf` (2026-09-16) integrated below as **[annot]**.
Sections: learning as optimization → grid search → landscapes → smooth optimization (GD, SGD, variants) → non-smooth (subgradients) → implementation issues → optimality conditions → non-convex → constrained.

## Learning = optimization
- Given cost L(w), find `w★ = argmin_w L(w)`. Solved by an optimization algorithm.
- **Grid search:** evaluate L on a grid of w, keep the best. Works for any cost with very few parameters. **Curse of dimensionality:** 10 values per dim ⇒ 10^D evaluations; impossible for D ≈ millions; no guarantee of nearing an optimum; choosing ranges is hard. [annot] sketch of a 4×3 grid over (w₀, w₁) with L(w) as vertical bars, D = 2; "D ≈ 100 → 10^D intractable"; sketch of a narrow dip between grid points = the optimum can be missed. Hyperparameter tuning: not exam material.

## Landscapes / minima
- **Local minimum:** ∃ ε > 0 s.t. `L(w★) ≤ L(w)` ∀ w with ‖w − w★‖ < ε. **Global:** `L(w★) ≤ L(w)` ∀ w. **Strict** if inequality strict (`<`) for w ≠ w★. [annot] on the Bertsekas figure: left cuvette circled = strict local, plateau = non-strict local minima, right = "global opt".

## Gradient descent (smooth case)
- Gradient `∇L(w) = [∂L/∂w₁, …, ∂L/∂w_D]ᵀ ∈ ℝ^D`: direction of steepest increase.
- [annot] slide 10: on the MSE bowl he draws the tangent plane at a point and the arrow **−∇L** pointing downhill in the (w₀, w₁) plane; on the MAE bowl the same at a kink where the plane is not unique. `f_w(x) = w₀ + w₁x`.
- **GD update:** `w^(t+1) := w^(t) − γ ∇L(w^(t))`, γ > 0 = step-size / learning rate. [annot] "Cauchy 1848"; "step-size", "learning rate (LR)", "LR schedule" are synonyms; an **exact** choice for the 1-D example is γ = 1, and a decaying schedule like γ = c/t is typical.
- 1-param MSE example (`yₙ ≈ w₀`): `L(w₀) = 1/(2N) Σ (yₙ − w₀)²`. [annot, worked in red] `∇L = ∂L/∂w₀ = (1/2N) Σ −2(yₙ − w₀) = −(1/N)Σyₙ + w₀ = w₀ − ȳ`; set to 0 ⇒ `w₀★ = ȳ`. So `w₀^(t+1) = w₀^(t) − γ(w₀^(t) − ȳ) = (1−γ) w₀^(t) + γ ȳ`. [annot] number line: γ < 1 → small step toward ȳ; **γ = 1 → lands exactly on ȳ = w★ in one step**; 1 < γ < 2 → overshoots but gets closer; γ > 2 → **diverges**. "Good: γ ∈ (0, 2)".
- **Linear MSE:** xₙ ∈ ℝ^D, w ∈ ℝ^D, X is N×D (row n = xₙᵀ), error vector `e = y − Xw ∈ ℝ^N`, `L(w) = 1/(2N) Σ(yₙ − xₙᵀw)² = 1/(2N) eᵀe`, **gradient `∇L(w) = −(1/N) Xᵀ e = −(1/N) Xᵀ(y − Xw)`**. (Exam 2025 Q5.) [annot] derivation per coordinate: `∂L/∂w₁ = (1/2N) Σ 2(yₙ − xₙᵀw)(−xₙ₁) = −(1/N)(X_{:,1})ᵀ e`, …, `∂L/∂w_D = −(1/N)(X_{:,D})ᵀ e` → stack the D columns ⇒ `−(1/N)Xᵀe`. "xₙᵀw = f_w(xₙ)" is a row of X times w.
- Cost [annot]: compute `e = y − Xw`: O(N·D); compute `∇L = −(1/N)Xᵀe`: O(N·D); total **O(N·D)** per GD step. Hessian `∇²L = (1/N) XᵀX`, cost O(ND²) (2025 Q6).
- Offset variant: append a constant-1 column to X (x̃, N×(D+1)), w ∈ ℝ^(D+1); `X̃w` = predictions. Same formulas.

## Stochastic gradient descent
- Sum objectives: `L(w) = (1/N) Σₙ Lₙ(w)`; [annot] `Lₙ = loss(yₙ − f_w(xₙ))`; for linear MSE `Lₙ(w) = ½ (yₙ − xₙᵀw)²`, `∇Lₙ(w) = −xₙ(yₙ − xₙᵀw) = −xₙ eₙ`.
- **SGD:** pick n **uniformly at random in {1, …, N}**, `w^(t+1) := w^(t) − γ ∇Lₙ(w^(t)) =: w^(t) − γ g`, iterate t ← t+1. [annot] GD uses the "full gradient" ∇L, SGD the "stochastic gradient" ∇Lₙ. Cost per step **O(D)** (vs O(N·D) for GD) — [annot] table: GD/MSE ∇L O(ND); GD/MAE g ∈ ∂L O(ND); SGD/MSE ∇Lₙ O(D); SGD/MAE g ∈ ∂Lₙ O(D).
- Motivation: `𝔼ₙ[∇Lₙ(w)] = Σₙ (1/N) ∇Lₙ(w) = ∇((1/N)Σₙ Lₙ(w)) = ∇L(w)` [annot, the "check"] — cheap but **unbiased** estimate (2025 Q31 T/F: true, "noisy but unbiased"). [annot] slide 22 sketch: loss vs t — GD smooth decreasing curve, SGD noisy zig-zag around it.
- **Mini-batch SGD:** random B ⊆ [N], `g = (1/|B|) Σ_{n∈B} ∇Lₙ(w^(t))`, `w^(t+1) = w^(t) − γ g`. [annot] |B| = 1 → basic SGD; |B| > 1 → mini-batch SGD; extreme case |B| = N → GD (full gradient). Parallelizable (GPU threads).
- Variants (know names + one-line ideas; in all of them g = ∇Lₙ is a stochastic gradient): **momentum** `m^(t+1) = β₁m^(t) + (1−β₁)g`, `w^(t+1) = w^(t) − γ m^(t+1)` (accumulate past gradients ⇒ acceleration); **Adam** `m = β₁m + (1−β₁)g`, `vᵢ = β₂vᵢ + (1−β₂)gᵢ²` per coordinate, `wᵢ ← wᵢ − γ mᵢ/√vᵢ` (momentum variant of Adagrad, coordinate-wise adapted learning rate, fast forgetting of old gradients; strong in practice for NNs). [annot] with no history, `mᵢ/√vᵢ = gᵢ/|gᵢ| = sign(gᵢ)` → Adam ≈ SignSGD at the first step; **memory: 3 model copies** (w, m, v); **SignSGD** (only sign of each gradient entry, 1 bit ⇒ communication-efficient distributed training; convergence issues); **Muon** (G = gradient entries of **one layer**'s weight matrix; matrix version of SignSGD: `msign(M) = UVᵀ` if `M = USVᵀ` (SVD), i.e. drop S; `msign` sets all singular values to 1 so update has operator norm 1; computed by 5 Newton–Schulz iterations, only matmuls, no SVD; used for 2-D weight matrices only, AdamW for embeddings/biases/gains/routers, γ ≈ 0.02).

## Non-smooth optimization (MAE etc.)
- [annot] section title: "non-differentiable"; sketches of |e| (MAE) and ReLU with many possible tangent lines at the kink.
- Convexity, first-order characterization (differentiable L): `L(u) ≥ L(w) + ∇L(w)ᵀ(u − w)` ∀u, w (function lies above its linearization = **1st-order Taylor expansion** [annot]).
- **Subgradient** g ∈ ℝ^D at w: `L(u) ≥ L(w) + gᵀ(u − w)` ∀u — any slope of a line through (w, L(w)) that stays below the graph [annot sketch]. Defined for non-differentiable (even non-convex) L. If L convex and differentiable at w, the only subgradient is ∇L(w). ∂L(w) = the **set** of all subgradients at w.
- **Subgradient descent:** same update with g in place of ∇L. Stochastic version: g subgradient of random Lₙ (still called SGD).
- Linear MAE: `L(w) = (1/N) Σ |yₙ − xₙᵀw|`. [annot] subgradient of h(e) = |e|: `g = −1 if e < 0, [−1, 1] if e = 0, +1 if e > 0` (the set ∂h). **Subgradient chain rule** [annot]: `L(w) = h(q(w))` with h non-differentiable, q differentiable ⇒ a subgradient is `g ∈ ∂h(q(w)) · ∇q(w)`. Here q(w) = yₙ − xₙᵀw, ∇q = −xₙ ⇒ per-example `−sign(eₙ) xₙ`; full `g = −(1/N) Xᵀ sign(e)`. (Exercise sheet 2; mock midterm 2018 Q1.)

## Implementation issues
- **Step-size:** too big ⇒ divergence; too small ⇒ slow. Convergence guaranteed only with a schedule that becomes "small enough" (problem-dependent). [annot] "learning rate (LR)", "LR schedule": sketch of LR vs t; examples 1/√t, linear decay, and **WSD** (warmup–stable–decay, used for Apertus LLM).
- **Stopping:** ‖∇L(w)‖ ≈ 0; [annot] "in practice ‖∇L(w)‖ → small".
- **Feature normalization / pre-conditioning:** GD is sensitive to ill-conditioning (directions with very different curvature). [annot] sketch: narrow parabola in w₁ vs flat parabola in w₂; level sets = **elongated ellipses** (ill-conditioned) → GD zig-zags across the valley; **circles** (well-conditioned) → GD goes straight to the center. Normalize features (and layers in NNs); rescaling the space = pre-conditioning.

## Optimality conditions
- First-order necessary: `∇L(w★) = 0` (critical point). If L convex, critical point ⇒ global optimum.
- **Hessian** `∇²L(w) ∈ ℝ^{D×D}` of second derivatives ("2nd-order" [annot]). Second-order sufficient: `∇L(w) = 0` and `∇²L(w) ≻ 0` (positive definite ⇔ `vᵀ∇²L v > 0 ∀v ≠ 0` [annot]) ⇒ local minimum. [annot] sketch: ∇²L > 0 at a valley bottom, ∇²L < 0 at a hilltop. Twice-differentiable L is convex ⇔ Hessian PSD everywhere.

## Non-convex & constrained
- Real problems are non-convex; convex tools still guide algorithm design. [annot] sketch of a bumpy landscape with "noise" and a local descent.
- Constrained: `min_{w ∈ C} L(w)`, C ⊂ ℝ^D constraint set. **Convex set:** ∀u, v ∈ C, θ ∈ [0,1]: θu + (1−θ)v ∈ C. Intersections of convex sets are convex; projections onto convex sets are unique (often cheap).
- **Projected GD:** `w^(t+1) = P_C(w^(t) − γ ∇L(w^(t)))` = "GD step, then project to C" [annot]; P_C(w') = argmin_{v∈C} ‖v − w'‖. Projected SGD: same, same convergence; **projection cost is crucial** — [annot] projecting onto a ball is cheap, onto a polytope (diamond) is costly.
- Alternative: penalty functions — indicator ("brick wall", discontinuous), penalize constraint violation: e.g. C = {w : Aw = b} (a **linear constraint**) → `min_w L(w) + λ‖Aw − b‖²` ([annot] the penalty = distance from C; λ = trade-off; "multi-objective"), linearized penalties (Lagrange multipliers).

## Exam questions mapped to slides (added 2026-09-18)
- Slide 32 subgradients: 2022 Q24 (|x−2023| at 2023: exists but NOT unique → False); 2020 Q6 (−x² at 0: no subgradient although differentiable — non-convex); 2021 Q16 (PReLU at 0, depends on a; check official answer).
- Slide 34 MAE subgradient: mock midterm 2018 Q1; lab 2 ex 6a.
- Slide 35 cost table [annot]: GD O(N·D) vs SGD O(D), same for MSE and MAE; 2020 Q5 (P·D GD iterations vs N·P·D SGD).
- Slide 36 step-size: 2022 Q4 (L = λ/2‖w‖²: γ = 1/λ one step, γ = 2/λ oscillates, converges iff γ ∈ (0, 2/λ)).
- Slide 38: 2020 Q28 (convex over convex set ⇒ unique global min → False; strictly convex needed).
- Slide 39 Hessian: 2025 Q37 (Hessian of MSE = (1/N)XᵀX constant in w → True); 2025 Q6 (cost O(N·D²)).
- Slide 46 convex sets: 2019 Q17 (unions → False), Q18 (intersections → True), Q19 (f∘g of convex → False).
- Slide 49 [annot]: projection onto ℓ₂ ball cheap, onto ℓ₁ ball (diamond) costly. Slide 50 [annot]: penalty λ‖Aw−b‖² = "distance from C", λ = trade-off, "multi-objective" → link to ridge (week 3).

## Not exam material (additional notes)
- Big-O: f = O(g) iff ∃c, x₀: f(x) ≤ c·g(x) ∀x ≥ x₀. Matrix–matrix (N×D)(D×K): O(NDK); matrix–vector O(ND).
- SGD theory: with large N, random-example steps are cheap; convergence needs γ^(t) → 0 "appropriately" — **Robbins–Monro:** Σₜ γ^(t) = ∞ and Σₜ (γ^(t))² < ∞, e.g. γ^(t) = 1/t^α with α ∈ (0.5, 1].
- Reading: Bubeck *Convex Optimization: Algorithms and Complexity*; Boyd & Vandenberghe.

## Exercises listed on the slides (→ Lab 2) — [annot] "chain rule everywhere"
1. Chain rule refresher. 2. Big-O revision. 3. Complexity of grid search / GD / SGD for linear MSE (#steps, cost per step). 4. Gradients of linear MSE and MAE. 5–6. Implement GD and SGD; experiment with step-size.
