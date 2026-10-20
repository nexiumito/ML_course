# Lecture 06 — Support Vector Machines; Nearest Neighbors & Curse of Dimensionality

Sources (lecturer 2026: **Martin Jaggi**, slide credits Nicolas Flammarion; pulled 2026-10-13):
- §A `lectures/06/lecture06a.pdf` (28 p., 2026-10-13) — Support Vector Machines
- §B `lectures/06/lecture06b.pdf` (48 p., 2026-10-14) — Nearest-neighbor classifiers and the curse of dimensionality

**Slide numbering:** no printed numbers → **"slide N" = PDF page N** (title = p. 1). Render with `pdftoppm -f N -l N`. Many pages are build-up animations of the previous one (06a p. 6–8, 11–13, 15–17, 22–23; 06b p. 3–20, 26–30, 34–36, 41–45).
**Annotated version:** Jaggi lectures this year → `*_annotated.pdf` may arrive upstream ~2026-10-14/15 (`git pull upstream main`); integrate it here when it lands.
**Proxy:** the 2025 decks are **identical except the title page** (2025 taught by R. West): `git show '48f3822^:lectures/06/lecture06a_annotated.pdf'` (28 p.) and `…/lecture06b_annotated.pdf` (48 p.), same page numbers as 2026. Notes from them are marked *(2025 ann.)*.
Formulas below come from the PDF text layer (real text in these decks), checked against the 2025 annotated renders.

## §A Support Vector Machines (06a)
- **Setting (p. 2–3):** Vapnik's invention (Boser–Guyon–Vapnik 1992, Cortes–Vapnik 1995). Binary classification, **y ∈ {−1, 1}** (⚠ not {0, 1} as in 05b). S = {(xₙ, yₙ)}ₙ₌₁ᴺ, f_S = 𝒜(S).
- **Linear classifier (p. 4):** hyperplane {x : wᵀx = 0} with **‖w‖ = 1**; prediction f(x) = sign(xᵀw). ⚠ **No bias term** in the lecture (hyperplane through 0; append a constant feature if needed).
- **Distance point–hyperplane (p. 4–5):** for ‖w‖ = 1, dist(x₀, {wᵀx = 0}) = **|wᵀx₀|** (in general |wᵀx₀| / ‖w‖). Proof: dist = min_{u : wᵀu = 0} ‖x₀ − u‖; set v = x₀ − (wᵀx₀)w (projection on the hyperplane); Pythagoras ‖x₀ − u‖² = (wᵀx₀)² + ‖v − u‖² ≥ (wᵀx₀)², equality at u = v.
- **Hard-SVM (p. 6–8):** assume the data **linearly separable**. **Margin** of a hyperplane = minₙ |wᵀxₙ| (distance to the closest point). Max-margin separating hyperplane:
  (I) max_{‖w‖=1} minₙ |wᵀxₙ| s.t. ∀n yₙxₙᵀw ≥ 0
  ⇔ (II) max_{M, ‖w‖=1} M s.t. ∀n yₙxₙᵀw ≥ M
  ⇔ (III) **min_w ½‖w‖² s.t. ∀n yₙxₙᵀw ≥ 1** — margin **M = 1/‖w‖** (band width between wᵀx = ±1 is 2/‖w‖).
- **Proofs (p. 9–10):** (I)⇔(II): squeeze M₁ ≥ minₙ|w₂ᵀxₙ| ≥ M₂ ≥ M₁ using admissibility in each direction. (II)⇔(III): the constraint yₙxₙᵀ(w/‖w‖) ≥ M is scale-invariant → drop ‖w‖ = 1, **fix the scale ‖w‖ = 1/M** ⇒ max 1/‖w‖ s.t. yₙxₙᵀw ≥ 1 ⇔ min ½‖w‖². *(2025 ann.: "yₙxₙᵀw ≥ 0 ⇔ correct side, so |xₙᵀw| = yₙxₙᵀw".)*
- **Soft-SVM (p. 11–13):** for non-separable data, slack variables ξₙ ≥ 0, constraint yₙxₙᵀw ≥ 1 − ξₙ:
  min_{w,ξ} (λ/2)‖w‖² + (1/N) Σₙ ξₙ s.t. yₙxₙᵀw ≥ 1 − ξₙ, ξₙ ≥ 0
  ⇔ **min_w (λ/2)‖w‖² + (1/N) Σₙ [1 − yₙxₙᵀw]₊**, [α]₊ = max{0, α}.
  Proof (p. 13): fix w, minimize over ξ: if yₙxₙᵀw ≥ 1 ⇒ ξₙ = 0; else ξₙ = 1 − yₙxₙᵀw ⇒ ξₙ = [1 − yₙxₙᵀw]₊. Geometric distance of a violating point to its margin boundary = ξₙ/‖w‖ (figure ξᵢ* = ξᵢ/‖w‖).
- **Classification by risk minimization (p. 14):** true risk L(f) = 𝔼_𝒟[𝟙_{Y≠f(X)}]; ERM min_w (1/N) Σ ϕ(yₙwᵀxₙ), ϕ = loss of the **functional margin** yₙxₙᵀw, convex surrogate of 0-1. *(2025 ann.: yxᵀw ≥ 0 ⇔ sign(wᵀx) = y.)*
- **Margin-based losses, η = y xᵀw (p. 15–17):** quadratic (1 − η)²; logistic log(1 + e^{−η})/log 2 (rescaled so it equals 1 at η = 0); **hinge [1 − η]₊**. All **convex** and **upper bounds of the 0-1 loss**. Behaviour: MSE penalizes any deviation from 1 (even "too correct"); logistic: asymmetric, **always** a (small) penalty; **hinge: penalty only if wrong or not confident (η < 1), exactly 0 for η ≥ 1**. *(2025 ann.: "Platt scaling" next to hinge — SVM outputs no probabilities; Platt scaling fits a sigmoid on the scores afterwards.)*
- **Summary (p. 18):** SVM = **ERM with hinge loss + ridge (ℓ₂) regularization**. Margin region {x : |xᵀw| ≤ 1}, width 2/‖w‖. Separable data, small λ: (1) direction of w s.t. w^⊥ separates, (2) scale w so no point is inside the margin, (3) pick the largest margin.
- **Optimization (p. 19):** convex but **non-smooth** objective → **subgradient / stochastic subgradient method** (lab 6 Problem 1). Per-sample subgradient: −yₙxₙ·𝟙[yₙxₙᵀw < 1] + λw.
- **Convex duality (p. 20):** find G(w, α) with min_w L(w) = min_w max_α G(w, α). Primal = min_w max_α G; dual = max_α min_w G. Three questions: how to find G? when can min/max be swapped? why is the dual easier?
- **Q1 — G (p. 21):** [z]₊ = max(0, z) = **max_{α∈[0,1]} αz** ⇒ [1 − yₙxₙᵀw]₊ = max_{αₙ∈[0,1]} αₙ(1 − yₙxₙᵀw) ⇒
  **G(w, α) = (1/N) Σₙ αₙ(1 − yₙxₙᵀw) + (λ/2)‖w‖²**, α ∈ [0, 1]ᴺ. G is **convex in w, concave (linear) in α**.
- **Q2 — swap (p. 22–23):** **always** max_α min_w G ≤ min_w max_α G (weak duality; proof: min_w G(α, w) ≤ G(α, w′) ∀w′ → take max_α then min_w′). **Equality** (strong duality, minimax theorem) if G convex in w, concave in α, and the domains are convex and compact. Saddle-point picture.
- **Application to SVM (p. 24):** condition met ⇒ swap. ∇_w G = −(1/N) Σ αₙyₙxₙ + λw = 0 ⇒ **w(α) = (1/(λN)) Σₙ αₙyₙxₙ = (1/(λN)) XᵀYα**, Y = diag(y). Plug in ⇒ **dual problem**:
  **max_{α∈[0,1]ᴺ} αᵀ1/N − (1/(2λN²)) αᵀYXXᵀYα** (YXXᵀY is PSD ⇒ concave quadratic).
- **Q3 — why the dual (p. 25):** (1) differentiable concave **QP** with box constraints → QP solvers, **coordinate ascent** (lab 6 Problem 2); (2) depends on the data only through the **kernel (Gram) matrix K = XXᵀ ∈ ℝᴺˣᴺ** → no dependency on d → **kernel trick** (lecture 08); (3) **α is typically sparse**: non-zero only for the points that determine the boundary.
- **Interpretation of α (p. 26):** αₙ maximizes αₙ(1 − yₙxₙᵀw) over [0, 1]:
  - correct side, **outside** the margin (yₙxₙᵀw > 1) ⇒ **αₙ = 0**;
  - **on** the margin (yₙxₙᵀw = 1) ⇒ αₙ ∈ [0, 1];
  - **strictly inside** the margin or **misclassified** (yₙxₙᵀw < 1) ⇒ **αₙ = 1**.
  Points with **αₙ > 0 = support vectors**.
- **Supported by the support vectors (p. 27):** w = (1/(λN)) Σ αₙyₙxₙ ⇒ **w does not depend on (xₙ, yₙ) if αₙ = 0**: moving/removing a non-support point (staying outside the margin) leaves the SVM unchanged.
- **Recap (p. 28):** hard SVM min ½‖w‖² s.t. yₙxₙᵀw ≥ 1; soft SVM min (λ/2)‖w‖² + (1/N)Σ[1 − yₙxₙᵀw]₊ via (stochastic) subgradient; duality min max = max min (convex–concave) → QP / coordinate ascent; cost depends on data via the kernel matrix.

## §B Nearest neighbors & curse of dimensionality (06b)
- **Neighborhood (p. 3–9):** nbh_{S_train,k}(x) = the k elements of S_train closest to x. **Ties** (equal distances) → not uniquely defined, implementation-dependent, often broken randomly (p. 8). Any metric can be used; **high computational cost for large N** (efficient data structures exist, e.g. k-d trees) (p. 9).
- **k-NN regression (p. 10–13):** f(x) = (1/k) Σ_{n : xₙ ∈ nbh_k(x)} yₙ (average of neighbour labels).
- **k-NN classification (p. 14–20):** f(x) = majority{yₙ : xₙ ∈ nbh_k(x)}. Example: f₁(x) = 1 but f₃(x) = 0 for the same point; f₄ → tie. Remarks: **choose k odd** (binary) to avoid ties; generalization = smoothing kernels / weighted combination of the neighbours.
- **Why it works (p. 21):** relevant when labels have **spatial correlation**; implicitly models intricate boundaries in **low dimension**.
- **Bias–variance in k (p. 22–24):** **small k (k = 1): low bias, complex boundary, high variance — overfitting** (1-NN has **zero training error**). **Large k: high bias, low variance** (k = N ⇒ constant prediction = majority class / mean). U-shaped test error vs k; **complexity (degrees of freedom ≈ N/k) increases as k decreases**. Choose k (by CV) to balance both (15-NN example). Figures from ESL (Hastie et al., Fig. 2.4).
- **Summary k-NN (p. 25):** Pros: **no optimization or training**, easy to implement, works well in **low dimension** with very complex boundaries. Cons: **slow at query time**, **not suited to high-dimensional data**, choosing the right local distance is crucial.
- **Curse of dimensionality, claim 1 (p. 26–28):** fixed-size training sets cover a vanishing fraction of the space. x ~ U([0, 1]ᵈ); a box of side r around x₀ has ℙ = **rᵈ = α**. To capture α = 1 % of the data: d = 10 ⇒ r = 0.01^{1/10} ≈ **0.63**; d = 100 ⇒ r ≈ **0.95** → the "local" neighbourhood spans almost the whole cube.
- **Claim 2 (p. 29–30):** points are far from each other. N i.i.d. uniform points: ℙ(xᵢ ∉ box ∀i) = (1 − rᵈ)ᴺ, so ℙ(∃xᵢ ∈ box) = 1 − (1 − rᵈ)ᴺ ≥ ½ ⟹ **r ≥ (1 − 1/2^{1/N})^{1/d}**. d = 10, N = 500 ⇒ r ≥ 0.52.
- **1-NN generalization bound — setup (p. 31–33):** (X, Y) ~ 𝒟 on [0, 1]ᵈ × {0, 1}, L(f) = ℙ(Y ≠ f(X)). η(x) = ℙ(Y = 1 | X = x). **Bayes classifier f*(x) = 𝟙_{η(x) ≥ 1/2}** (= argmax_y ℙ(Y = y | x), proof 1 p. 32). **Bayes risk L(f*) = 𝔼_X[min{η(X), 1 − η(X)}]** (proof 2 p. 33: tower rule + case split on η ≥ ½ — same technique as 05a p. 25).
- **Bound (p. 34–36):** assume η is **c-Lipschitz**: |η(x) − η(x′)| ≤ c‖x − x′‖ ("nearby points likely share the label"). Then
  **𝔼_{S_train}[L(f_{S_train})] ≤ 2L(f*) + c·𝔼[‖X − nbh_{S_train,1}(X)‖] ≤ 2L(f*) + 4c√d · N^{−1/(d+1)}**
  (geometric term = average distance from a random point to its nearest training point). Interpretation: fixed d, N → ∞ ⇒ **1-NN error ≤ 2× Bayes risk**; to keep a constant error, **N ∝ d^{(d+1)/2}**, i.e. **exponential in d** = curse of dimensionality; an **interpolating** method (zero training error) can still generalize — against common belief.
- **Proof (p. 37–40):** draw unlabeled S_train,X and X, X′ = nbh₁(X), labels Y ~ η(X), Y′ ~ η(X′) ⇒ 𝔼[L] = 𝔼[ℙ(Y ≠ Y′)]. Lemma: ℙ(Y ≠ Y′) = η(x)(1 − η(x′)) + η(x′)(1 − η(x)) = 2η(x)(1 − η(x)) + (2η(x) − 1)(η(x) − η(x′)) ≤ **2 min{η(x), 1 − η(x)} + c‖x − x′‖** (uses |2η − 1| ≤ 1, Lipschitz, and η(1 − η) ≤ min{η, 1 − η}). Take expectations ⇒ 2L(f*) + c𝔼‖X − X′‖.
- **Geometric term (p. 41–46):** ε-cover of [0, 1]ᵈ by boxes of side ε, pₖ = ℙ(X ∈ Boxₖ). If X's box contains a training point (prob. 1 − (1 − pₖ)ᴺ) ⇒ distance ≤ √d·ε (box diagonal); else ≤ √d (cube diagonal), prob. (1 − pₖ)ᴺ. ⇒ 𝔼‖X − nbh(X)‖ ≤ Σₖ pₖ[(1 − pₖ)ᴺ√d + (1 − (1 − pₖ)ᴺ)√d ε]; optimize over pₖ and ε. Intuition: large pₖ ⇒ box likely occupied; small pₖ ⇒ rarely visited.
- **Local averaging (p. 47):** k-NN approximates the Bayes predictor directly, no optimization: plug-in estimate p̂(y | x) = Σₙ ŵₙ(x)𝟙_{y=yₙ}, ŵₙ = 1/k for the k nearest neighbours (0 otherwise); classification f(x) ∈ argmax_y p̂(y | x), regression f(x) = 𝔼̂[Y | x].
- **Recap (p. 48):** local averaging for regression and classification; small/large k ⇒ low/high bias, high/low variance; curse of dimensionality: neighbourhoods are hard to define as d ↗; N → ∞ ⇒ 1-NN competitive with Bayes (≤ 2×); N must scale exponentially in d.

## Notation (new)
| Symbol | Meaning |
|---|---|
| y ∈ {−1, 1} | label encoding for SVM (≠ 05b's {0, 1}) |
| M, 1/‖w‖ | margin; with constraint yₙxₙᵀw ≥ 1 the margin is 1/‖w‖, band width 2/‖w‖ |
| ξₙ | slack variable (soft SVM), optimal ξₙ = [1 − yₙxₙᵀw]₊ |
| [z]₊ | max{0, z}; hinge loss [1 − η]₊ |
| α ∈ [0, 1]ᴺ | dual variables; αₙ > 0 ⇔ support vector |
| G(w, α) | Lagrangian-like saddle function, convex in w, concave in α |
| Y = diag(y) | diagonal label matrix in the dual |
| K = XXᵀ | kernel / Gram matrix of inner products, N × N (vs XᵀX, D × D) |
| nbh_{S,k}(x) | the k training points closest to x |
| η(x) | ℙ(Y = 1 | X = x) (06b; ⚠ in 06a p. 15 η is the functional margin yxᵀw) |
| c | Lipschitz constant of η |

## Exam-relevant points / pitfalls
- **Hard-SVM constraint**: yₙwᵀxₙ ≥ 1 (pick it among look-alikes — 2021 Q2). Distance of x to {wᵀx = 0} = |wᵀx|/‖w‖ (2020 Q13: w = (4, 0, −3), x = (−1, 3, 2) ⇒ 10/5 = 2).
- **Solve a tiny hard-SVM by hand**: find the max-margin hyperplane through 0, then scale so the closest points satisfy yₙwᵀxₙ = 1 (2022 Q9: w* = (0, 0.5), not (0, 1)). Margin achievable ≤ half the distance between closest opposite points (2024 Q23).
- **Support vectors / robustness**: moving or removing a point that is correctly classified and **outside the margin** ⇒ **no change for SVM**, small change for logistic regression (logistic loss is never exactly 0) (2019 Q3, 2020 Q2, 2021 Q1 also 1-NN unchanged by a far outlier).
- **Number of support vectors is not bounded by 2d** (collinear points on the margin) (2023 Q22 False).
- **Soft-SVM facts** (2024 Q24): no solution can have all ξᵢ ≥ 1 (−w would do better); ξᵢ can exceed 1 (misclassified points); soft SVM ≠ regularized logistic; it has a solution even if data not separable.
- **No single λ makes soft = hard SVM for all separable datasets** (2020 Q25 False; depends on the data scale).
- **SVM does not output probabilities** (needs Platt scaling) (2025 Q9). Kernel SVM training cost scales with N / support vectors, not with the input dimension (2025 Q34 False). One SGD step for SVM costs O(D) (2019 Q22).
- **L1-SVM** (‖w‖₁ instead of ‖w‖²): still convex, non-smooth, sparse w (feature selection), but the dual is **not** expressed via kernels (2025 Q10).
- Hinge loss is **classification-calibrated**; its conditional risk minimizer is sign(2η − 1), min = 2 min{η, 1 − η} (2022 Q45–Q50, open problem).
- Adversarial ℓ₂ training of a hinge-loss linear model gives max{0, 1 − yxᵀw + ε‖w‖₂} — **not** the soft-SVM objective (2022 Q33 True).
- **k-NN**: **non-parametric** (2025 Q1); **no training phase** — cost is at prediction time (2025 Q38 False); must store the data, slow in high dimension, **any distance** (L1, L2, L4…) works and **the metric matters** (2021 Q14, 2022 Q21, 2024 Q25); can do **regression** by averaging (2022 Q34 False, 2024 Q25).
- **1-NN training error = 0** (2019 Q13 True); figure with training error going to 0 as hyperparameter changes ⇒ k-NN with decreasing k (2020 Q7). 1-NN boundary is non-linear (2020 Q4: only SVM & logistic give a linear boundary).
- **Bias–variance in k**: to reduce bias (underfitting) **decrease** k (2025 Q33 False); k = N: variance low but **not 0**, bias not 0 (2024 Q25).
- **LOO-CV with 1-NN vs 3-NN** on a picture: count by hand (2024 Q20).
- 1-NN with ℓ₁ distance on 2 points: boundary ≠ max-margin linear boundary (2024 Q32 False — the ℓ₁ bisector is not a straight perpendicular line).
- **Curse of dimensionality numbers**: halving the NN distance δ → δ/2 needs ≈ **2ᴰN** samples (volume ∝ rᴰ) (2019 Q4). Data on a p-dim plane in ℝᵈ ⇒ N scales with the **intrinsic** dimension, ∝ 2ᵖ (2023 Q6, uses the 1-NN bound 2L(f*) + 4c√d N^{−1/(d+1)}).
- Perceptron converges in time ∝ R²/γ², but not to the max-margin hyperplane (2021 Q46–Q49, open problem).

## Not exam material / lower priority
- The ε-cover optimization giving 4c√d N^{−1/(d+1)} (p. 46): only the intuition is on the slide; know the **result and its interpretation**, not the computation.
- Proof of the minimax theorem (only weak duality is proved on p. 23).

## Exercises mentioned
- Lab 6 (`labs/ex06/`, 2026-10-15, identical to 2025): SVM on a scikit-learn toy dataset. **Problem 1** SGD on the primal (`calculate_primal_objective`, `calculate_accuracy`, `calculate_stochastic_gradient`). **Problem 2** coordinate ascent on the dual: derive the closed-form update αₙ ← clip(αₙ + λN(1 − yₙxₙᵀw)/‖xₙ‖², 0, 1), then w ← w + (Δαₙ/(λN)) yₙxₙ (both O(D)); `calculate_coordinate_update`, `calculate_dual_objective` = (1/N)Σα − (λ/2)‖w‖². Compare primal–dual gap. Plus theory: convexity proofs, multiclass (softmax) logistic regression, mixture of linear regressions. Details in `docs/labs.md`.
