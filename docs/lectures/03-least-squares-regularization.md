# Lecture 03 — Least Squares, Overfitting, Maximum Likelihood, Ridge & Lasso

Sources (lecturer: Martin Jaggi; pulled 2026-09-24; annotated versions `*_annotated.pdf` pulled 2026-09-25 and integrated in § Annotations below):
- §A `lectures/03/lecture03a_least_squares.pdf` (15 p., 2026-09-22)
- §B `lectures/03/lecture03b_overfitting.pdf` (10 p., 2026-09-22)
- §C `lectures/03/lecture03c_maximum_likelihood.pdf` (11 p., 2026-09-23)
- §D `lectures/03/lecture03d_ridge.pdf` (19 p., 2026-09-23)

Formulas below were checked against rendered slides (2026-09-24). "Slide N" = number printed bottom-right.

## §A Least squares (03a)
- **Scope:** linear regression + MSE is one of the rare cases with an analytic optimum → solve a linear system (the **normal equations**).
- Plan (sl. 2): show L is convex → optimality condition `∇L(w★) = 0` (a system of D equations).
- Cost (sl. 3): `L(w) = 1/(2N) Σₙ (yₙ − xₙᵀw)² = 1/(2N) (y − Xw)ᵀ(y − Xw)`, X is N×D.
- **Convexity, 3 proofs** (sl. 4–6): (1) sum with positive coefficients of (linear ∘ convex square); (2) definition: `L(λw + (1−λ)w') − (λL(w) + (1−λ)L(w')) = −1/(2N) λ(1−λ) ‖X(w − w')‖² ≤ 0`; (3) Hessian `∇²L = (1/N) XᵀX` is PSD (non-zero eigenvalues = squared singular values of X).
- **Gradient** (sl. 7): `∇L(w) = −(1/N) Xᵀ(y − Xw)` → normal equations **`Xᵀ(y − Xw) = 0`** (Xᵀ · error = 0).
- **Geometry** (sl. 8): the error `y − Xw★` is orthogonal to every column of X; `u★ = Xw★` is the **orthogonal projection of y onto span(X)** (column space).
- **Closed form** (sl. 9): `XᵀX ∈ ℝ^{D×D}` = **Gram matrix**; if invertible `w★ = (XᵀX)⁻¹Xᵀy`; prediction for a test point `ŷₘ = xₘᵀw★ = xₘᵀ(XᵀX)⁻¹Xᵀy`.
- **Invertibility** (sl. 10): XᵀX invertible ⇔ X has **full column rank**, rank(X) = D. Key step: `XᵀXv = 0 ⇒ 0 = vᵀXᵀXv = ‖Xv‖² ⇒ Xv = 0`.
- **Rank deficiency** (sl. 11): D > N ⇒ always rank(X) < D; D ≤ N with (nearly) collinear columns ⇒ ill-conditioned. Still solvable with a linear-system solver (infinitely many minimizers if rank-deficient).
- Summary (sl. 12): three methods for linear regression = grid search, (S)GD, least squares (closed form, linear MSE only).
- Additional notes (sl. 13–14, not core): use `np.linalg.solve(A, b)` (QR/LU), **never invert** a matrix (≥ 3× cost); MAE 1-parameter closed form = the **median** (MSE → mean).
- Lab/P1 link: `least_squares(y, tx)` = solve `XᵀX w = Xᵀy` with `np.linalg.solve` (lstsq forbidden in P1).

## §B Underfitting and overfitting (03b)
- **Underfit** = model family too limited; **overfit** = so rich it fits the noise. We only see data, so signal vs noise is unknown a priori.
- Data model (sl. 2): `yₙ = g(xₙ) + Zₙ`, Zₙ noise. A linear model `y = wx` cannot fit a non-linear g no matter N or noise (sl. 3).
- **Feature augmentation** (sl. 4–5): polynomial basis `ϕ(xₙ) = [1, xₙ, xₙ², …, xₙ^M]ᵀ`, fit `yₙ ≈ w₀ + w₁xₙ + … + w_M xₙ^M = ϕ(xₙ)ᵀw`. **Still linear in w** (so least squares still applies) but not in x. "Linear models are highly prone to overfitting, much more so than neural nets."
- Four fits (sl. 6–7, Bishop sin curve): M = 0, 1 underfit; M = 3 good; **M = 9 passes through every point = severe overfit**.
- More data (sl. 8): with M = 9 fixed, increasing N reduces overfitting.
- Notation (sl. 9): ϕ(x) when the distinction matters, otherwise augmentation is pre-processing and we just write x.

## §C Maximum likelihood (03c)
- Second, probabilistic route to least squares (same answer).
- Gaussian (sl. 2): `N(y | μ, σ²) = 1/√(2πσ²) · exp(−(y−μ)²/(2σ²))`; vector: `N(y | μ, Σ) = 1/√((2π)^D det Σ) · exp(−½ (y−μ)ᵀΣ⁻¹(y−μ))`. Independence: p(x, y) = p(x)p(y).
- Model (sl. 3): **`yₙ = xₙᵀw + εₙ`**, εₙ ~ N(0, σ²) iid, independent of the input.
- Likelihood (sl. 4): `p(y | X, w) = Πₙ p(yₙ | xₙ, w) = Πₙ N(yₙ | xₙᵀw, σ²)`. Best model = maximizes it.
- Log-likelihood (sl. 5): `L_LL(w) = log p(y | X, w) = −1/(2σ²) Σₙ (yₙ − xₙᵀw)² + cnst`.
- **MLE = MSE** (sl. 6–7): `argmin_w L_MSE(w) = argmax_w L_LL(w)` → a way to *design* cost functions from a noise model.
- Properties (sl. 8–9): MLE ≈ sample version of expected LL `E_{p(y,x)}[log p(y | x, w)]`; **consistent** (`w_MLE → w_true` in probability); **asymptotically normal** with covariance given by the inverse **Fisher information** `F(w) = −E[∂²L/∂w∂wᵀ]`; **efficient** (reaches the Cramér–Rao lower bound, `Cov(w_MLE) = F⁻¹(w_true)`). Know the names; derivations are not required.
- **Laplace noise** (sl. 10): `p(yₙ | xₙ, w) = 1/(2b) · e^{−|yₙ − xₙᵀw|/b}` → MLE gives **MAE**.

## §D Regularization: ridge & lasso (03d)
- Goal: fight the overfitting caused by feature augmentation. `min_w L(w) + Ω(w)`, Ω = regularizer measuring model complexity (sl. 2).
- **L2 / ridge** (sl. 4): `Ω(w) = λ‖w‖₂² = λ Σᵢ wᵢ²` → **`min_w 1/(2N) Σₙ (yₙ − xₙᵀw)² + λ‖w‖²`**. λ = 0 → least squares.
- **Closed form** (sl. 6): `w★_ridge = (XᵀX + λ'I)⁻¹Xᵀy` with **λ' = 2Nλ** (slide: "λ'/2N = λ"). Watch the factor: with the 1/(2N) MSE, gradient = `−(1/N)Xᵀ(y−Xw) + 2λw`.
- **Lifting the eigenvalues** (sl. 7–8): `XᵀX + λ'I = U[S + λ'I]Uᵀ` → every eigenvalue ≥ λ' > 0 ⇒ **always invertible**, even if D > N. Alt. proof via Rayleigh ratio `vᵀ(XᵀX + λ'I)v / vᵀv ≥ λ'`.
- **L1 / Lasso** (sl. 10): `min_w 1/(2N) Σₙ (yₙ − xₙᵀw)² + λ‖w‖₁`, `‖w‖₁ = Σᵢ |wᵢ|`. The L1 "ball" is a diamond/octahedron.
- **Why L1 is sparse** (sl. 11–12): level sets `{w : ‖y − Xw‖² = α}` are ellipsoids (XᵀX invertible) centred at w_LS; the optimum is where the smallest ellipsoid touches the L1 ball, most likely at a **corner** → some wᵢ = 0 → sparse = simple model / feature selection. L2 ball is round → no preferred corner, weights shrunk but not zero.
- Additional notes (sl. 14–19): other regularizers = shrinkage, dropout, weight decay, **early stopping**; constrained view `min L(w) s.t. ‖w‖² ≤ τ` (ridge) / `‖w‖₁ ≤ τ` (lasso); least squares = MLE (sl. 17, steps a–f); **ridge = MAP** estimate with prior wᵢ ~ N(0, 1/λ) iid (sl. 18, Bayes' law); regularization = prior information = "compressed data", like adding data.

## Annotations (from `*_annotated.pdf`, 2026-09-25)
**03a** — nothing beyond the slides; confirms the emphasis:
- sl. 2: plan "① show L convex ② ∇L ≐ 0 ⇒ w optimal"; sketch: non-convex curve where ∇L = 0 at a max / local min ("not enough") vs convex bowl ✓.
- sl. 3: `L = 1/(2N)‖Xw − y‖²`; a **column** of X = one feature ∈ ℝᴺ, a **row** = one datapoint ∈ ℝᴰ.
- sl. 4: rule "f∘g, g linear, f convex ⇒ f∘g convex". sl. 5: chord sketch; LHS written with w̄ = λw + (1−λ)w'.
- sl. 6: `∇²L = (1/N)XᵀX`; PSD proof **`wᵀXᵀXw = ‖Xw‖² ≥ 0`** (the one to write at the exam); "Hessian PSD ∀w ⇒ L convex".
- sl. 7: `XᵀXw = Xᵀy` ⇔ `Aw = b`, "D equations, D variables, linear system".
- sl. 8: `span(X) = {Xw | w ∈ ℝᴰ}`; e = y − Xw is orthogonal to all rows of Xᵀ (= columns of X); `min eᵀe = ‖y − Xw‖²`.
- sl. 10–11: two regimes drawn — **D ≪ N** (tall X, small D×D Gram) and **D ≫ N = "over-parametrized"** (wide X). sl. 11: "⇒ **don't invert XᵀX, but use a linear-system solver** on XᵀXw = Xᵀy".

**03b**: sl. 2 "M = 0 is a 1-param model f_w(x) = w₀"; sl. 4 ϕ(xₙ) ∈ ℝ^{M+1} (the leading 1 = bias); sl. 6 labels **M = 0 → 1 param, M = 1 → 2, M = 3 → 4, M = 9 → 10 params**: under-fitting / good fit / over-fitting (10 params for 10 points ⇒ interpolation); sl. 8 "M = 9 = 10-param model", N = 15 vs N = 100.

**03c**:
- sl. 1: scatter + red line f_w(x) and a **histogram of the errors eₙ = yₙ − xₙᵀw** that looks Gaussian ⇒ motivates the Gaussian noise model.
- sl. 2: 1-D bell p(y) centred at μ; 2-D contours: tilted ellipses for general Σ, **circles for Σ = I**.
- sl. 3: `p(εₙ) = N(εₙ | 0, σ²) ⇔ p(yₙ | xₙ, w) = N(yₙ | xₙᵀw, σ²)` (shift by xₙᵀw).
- sl. 4: product over n = **independence**; each factor Gaussian = **assumption on noise**.
- sl. 5: derivation worked out: `log Π N(…) = Σ log(c · exp(−(yₙ − xₙᵀw)²/(2σ²))) = −1/(2σ²) Σ (yₙ − xₙᵀw)² + cnst`. ⚠ The last handwritten line reads `Σ (1/σ²)(yₙ − xₙᵀw)² + cnst` — the minus sign and the ½ are dropped; the printed formula is the correct one.
- sl. 6: max L_LL vs min L_MSE differ only by a positive factor (1/(2σ²) vs 1/(2N)) and a constant **independent of w** ⇒ `argmax L_LL = argmin L_MSE`.
- sl. 8: `L_LL = (1/N) Σ log p(yₙ | xₙ, w)`; "∞ dataset" → expected LL; max over w gives w_MLE → w_true.
- **sl. 9 (asymptotic normality, Fisher information, Cramér–Rao) marked "optional"** → not exam material.
- sl. 10: `yₙ = xₙᵀw + ε` with Laplace ε: `max L_LL ⇔ min Σ |yₙ − xₙᵀw|` = **MAE**.

**03d**:
- sl. 2: `min L(w) + Ω(w)`: L = loss, Ω = model complexity.
- sl. 4: `−∇Ω = −2λw` = **weight decay** (the gradient step shrinks w toward 0) — link to NNs.
- sl. 6: `∇L = −(1/N)Xᵀ(y − Xw)` + `∇Ω = 2λw`, set the sum ≐ 0 ⇔ **`(XᵀX + λ'I_D)w = Xᵀy`** → "solve linear system → w★" (again: no inverse in code).
- sl. 7: eigenvalues "before: ≥ 0, after: ≥ λ' > 0".
- **sl. 8 (Rayleigh-ratio proof) marked "optional"**.
- sl. 10: `‖w‖₁ = Σᵢ|wᵢ|`; octahedron = `{‖w‖₁ ≤ 1}`; constrained form "min L(w) s.t. ‖w‖₁ ≤ c"; level sets L ≤ 1, 2, …, 5 = α drawn growing until they **touch the ball at a vertex** ⇒ sparse. sl. 11: `{w : ‖y − Xw‖² = α}` = "ellipse, level set of L".
- **Additional notes sl. 13–19: no annotations** (probably not covered in class; the MAP view is still asked at exams, e.g. 2022 Q5).

## Exam-relevant points / pitfalls
- Derive the normal equations and the ridge closed form by hand, **with the 2N factor** (2020 Q37–38: `w_ridge = [XᵀX + 2NλI]⁻¹Xᵀy`, and why it is invertible even if XᵀX is singular; 2025 Q43: derive ridge + show it is **biased**, E[ŵ_λ] ≠ w_true for λ > 0).
- D > N ⇒ XᵀX singular, ridge fixes it (2025 Q7). N ≤ D does **not** guarantee zero training error with normal equations (2020 Q26: counter-example with duplicated x, different y).
- Large λ ⇒ **underfit**, small λ ⇒ overfit (2022 Q25: the reversed statement is False).
- Ridge helps ill-conditioning but is **not sparse**; lasso is sparse (2023 Q16 True; 2016 L2 "sparse" = False; 2021 Q8 L1 reduces storage cost / is lasso with MSE; 2024 Q18 lasso vs ridge: feature selection, more interpretable).
- Lasso is **not scale-invariant**: rescaling a feature by 10 makes it *more likely* to be kept (2024 Q19). → Standardize features before regularizing (P1!).
- Lasso ↔ **Laplace prior** MAP, ridge ↔ Gaussian prior (2022 Q5). Gaussian noise ↔ MSE, Laplace noise ↔ MAE.
- Regularization includes weight decay, dropout, data augmentation, early stopping — **Adam is not** (2025 Q12). Ridge reduces train/test gap; feature augmentation increases overfitting (2021).
- Ridge vs LS bias–variance: ridge = larger bias, smaller variance (2022 Q6 — covered week 4).

## Not exam material
- Robust linear-system implementation details (Murphy §7.5.2). 03c sl. 9 (asymptotic normality, Fisher, Cramér–Rao) and 03d sl. 8 (Rayleigh proof): **marked "optional" by the prof**.

## Exercises mentioned
- Closed-form MAE for the 1-parameter model (median) — sl. 13 of 03a.
- Why L1 enforces sparsity; when is sparsity better than least squares — sl. 16 of 03d.
- Lab 3 (`labs/ex03/`, released 2026-09-24; lab 4 `labs/ex04/` released 2026-09-25): least squares, polynomial basis, train/test split, ridge regression.
