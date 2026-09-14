# Lecture 02a — Optimization

Source: `lectures/02/lecture02a_optimization.pdf` (56 p.), dated 2026-09-09 + 09-15. Lecturer: Martin Jaggi.
Sections: learning as optimization → grid search → landscapes → smooth optimization (GD, SGD, variants) → non-smooth (subgradients) → implementation issues → optimality conditions → non-convex → constrained.

## Learning = optimization
- Given cost L(w), find `w★ = argmin_w L(w)`. Solved by an optimization algorithm.
- **Grid search:** evaluate L on a grid of w, keep the best. Works for any cost with very few parameters. **Curse of dimensionality:** 10 values per dim ⇒ 10^D evaluations; impossible for D ≈ millions; no guarantee of nearing an optimum; choosing ranges is hard. Hyperparameter tuning: not exam material.

## Landscapes / minima
- **Local minimum:** ∃ ε > 0 s.t. `L(w★) ≤ L(w)` ∀ w with ‖w − w★‖ < ε. **Global:** `L(w★) ≤ L(w)` ∀ w. **Strict** if inequality strict for w ≠ w★.

## Gradient descent (smooth case)
- Gradient `∇L(w) = [∂L/∂w₁, …, ∂L/∂w_D]ᵀ ∈ ℝ^D`: direction of steepest increase.
- **GD update:** `w^(t+1) := w^(t) − γ ∇L(w^(t))`, γ > 0 = step-size / learning rate.
- 1-param MSE example (`yₙ ≈ w₀`): `L(w₀) = 1/(2N) Σ (yₙ − w₀)²`, `∇L = w₀ − ȳ` with ȳ = Σyₙ/N ⇒ `w₀^(t+1) = (1−γ) w₀^(t) + γ ȳ`; converges iff 0 < γ < 2 (γ = 1 in one step).
- **Linear MSE:** error vector `e = y − Xw` (N), `L(w) = 1/(2N) eᵀe = 1/(2N) ‖y − Xw‖²`, **gradient `∇L(w) = −(1/N) Xᵀ e = −(1/N) Xᵀ(y − Xw)`**. (Exam 2025 Q5.)
- Cost: computing gradient from scratch O(ND) (Xw then Xᵀe); given e, still O(ND) for Xᵀe. Hessian `∇²L = (1/N) XᵀX`, cost O(ND²) (2025 Q6).
- Offset variant: append a constant-1 column to X (x̃) — same formulas with D+1.

## Stochastic gradient descent
- Sum objectives: `L(w) = (1/N) Σₙ Lₙ(w)`; for linear MSE `Lₙ(w) = ½ (yₙ − xₙᵀw)²`, `∇Lₙ(w) = −(yₙ − xₙᵀw) xₙ`.
- **SGD:** pick random n, `w^(t+1) := w^(t) − γ ∇Lₙ(w^(t))`. Cost per step O(D) (vs O(ND) for GD).
- Motivation: `𝔼ₙ[∇Lₙ(w)] = ∇L(w)` — cheap but **unbiased** estimate (2025 Q31 T/F: true, "noisy but unbiased").
- **Mini-batch SGD:** random B ⊆ [N], `g = (1/|B|) Σ_{n∈B} ∇Lₙ(w^(t))`, `w^(t+1) = w^(t) − γ g`. Parallelizable (GPU threads); B = [N] recovers batch GD.
- Variants (know names + one-line ideas): **momentum** (accumulate past gradients ⇒ acceleration); **Adam** (momentum variant of Adagrad, coordinate-wise adapted learning rate, fast forgetting of old gradients; strong in practice for NNs); **SignSGD** (only sign of each gradient entry, 1 bit ⇒ communication-efficient distributed training; convergence issues); **Muon** (matrix version of SignSGD: `msign` sets all singular values to 1 so update has operator norm 1; computed by 5 Newton–Schulz iterations, only matmuls, no SVD; used for 2-D weight matrices only, AdamW for embeddings/biases/gains/routers, γ ≈ 0.02).

## Non-smooth optimization (MAE etc.)
- Convexity, first-order characterization (differentiable L): `L(u) ≥ L(w) + ∇L(w)ᵀ(u − w)` ∀u, w (function lies above its linearization).
- **Subgradient** g ∈ ℝ^D at w: `L(u) ≥ L(w) + gᵀ(u − w)` ∀u. Defined for non-differentiable (even non-convex) L. If L convex and differentiable at w, the only subgradient is ∇L(w).
- **Subgradient descent:** same update with g in place of ∇L. Stochastic version: g subgradient of random Lₙ (still called SGD).
- Linear MAE: `L(w) = (1/N) Σ |yₙ − xₙᵀw|`; subgradient of |·| at 0 is any value in [−1, 1] (sign(e) with sign(0) ∈ [−1,1]); chain rule ⇒ `g = −(1/N) Xᵀ sign(e)`; per-example `−sign(eₙ) xₙ`. (Exercise sheet 2; mock midterm 2018 Q1.)

## Implementation issues
- **Step-size:** too big ⇒ divergence; too small ⇒ slow. Convergence guaranteed only with a schedule that becomes "small enough" (problem-dependent).
- **Stopping:** ‖∇L(w)‖ ≈ 0.
- **Feature normalization / pre-conditioning:** GD is sensitive to ill-conditioning (directions with very different curvature). Normalize features (and layers in NNs); rescaling the space = pre-conditioning.

## Optimality conditions
- First-order necessary: `∇L(w★) = 0` (critical point). If L convex, critical point ⇒ global optimum.
- **Hessian** `∇²L(w)` (D×D of second derivatives). Second-order sufficient: `∇L(w) = 0` and `∇²L(w) ≻ 0` (positive definite) ⇒ local minimum. Twice-differentiable L is convex ⇔ Hessian PSD everywhere.

## Non-convex & constrained
- Real problems are non-convex; convex tools still guide algorithm design.
- Constrained: `min_{w ∈ C} L(w)`, C ⊂ ℝ^D constraint set. **Convex set:** ∀u, v ∈ C, θ ∈ [0,1]: θu + (1−θ)v ∈ C. Intersections of convex sets are convex; projections onto convex sets are unique (often cheap).
- **Projected GD:** `w^(t+1) = P_C(w^(t) − γ ∇L(w^(t)))`, P_C(w') = argmin_{v∈C} ‖v − w'‖. Projected SGD: same, same convergence; projection cost is crucial.
- Alternative: penalty functions — indicator ("brick wall", discontinuous), penalize constraint violation (e.g. add λ·dist(w, C)²), linearized penalties (Lagrange multipliers).

## Not exam material (additional notes)
- Big-O: f = O(g) iff ∃c, x₀: f(x) ≤ c·g(x) ∀x ≥ x₀. Matrix–matrix (N×D)(D×K): O(NDK); matrix–vector O(ND).
- SGD theory: with large N, random-example steps are cheap; convergence needs γ^(t) → 0 "appropriately" — **Robbins–Monro:** Σₜ γ^(t) = ∞ and Σₜ (γ^(t))² < ∞, e.g. γ^(t) = 1/t^α with α ∈ (0.5, 1].
- Reading: Bubeck *Convex Optimization: Algorithms and Complexity*; Boyd & Vandenberghe.

## Exercises listed on the slides (→ Lab 2)
1. Chain rule refresher. 2. Big-O revision. 3. Complexity of grid search / GD / SGD for linear MSE (#steps, cost per step). 4. Gradients of linear MSE and MAE. 5–6. Implement GD and SGD; experiment with step-size.
