# Lecture 01 — Introduction, Regression, Loss Functions

Sources: `lectures/01/lecture01a_intro.pdf` (53 p.), `lectures/01/lecture01b_regression.pdf` (20 p.), `lectures/01/lecture01c_loss_functions.pdf` (16 p.). Dates 2026-09-08/09. Lecturer: Martin Jaggi (credits Emtiyaz Khan).

## A. 01a — Introduction (mostly context, little exam material)
- Logistics (see `docs/course-overview.md`). "What to expect": overview of ML, basic understanding of main methods, practical experience. "Not": becoming an expert.
- **ML definition:** algorithms that learn from data. Traditional programming: data + rules → output. ML: data + desired output → rules (model weights **w**). Then test data + model → output.
- Learning functions from data: input → output examples (image classification, translation, speech-to-text, captioning, web search, recommenders, medical imaging, text generation, …).
- Classification picture: x_i ∈ ℝ^d, learning algorithm outputs w; SGD update `w := w − γ·(…)·x`, **iteration cost O(d)**. Perceptron (Rosenblatt 1957) → SVM (Cortes & Vapnik 1995).
- AI vs Statistics vs CS vs application domain; "data/ML scientist" = coding + math/stats + domain.
- History: not new (1854 cholera map; 1950s–60s NNs, Turing). Compute: 10³ FLOPs (1950s) → 10²⁵ (2024; Llama 3.1 405B ≈ 3.8×10²⁵ ops).
- Challenges: hype cycles, ethics/privacy/fairness, interpretability, social impact, superhuman-AI risk → need scientific method, reproducibility, open source/data.
- Long lists of past ML4Science student projects (2020–2024) — useful for Project 2 inspiration only.
- Data types: images, text, genetic, audio/multimodal, sensor, games, internet/recommenders (matrix with ★ ratings ⇒ U·V factorization), LLMs (next-word prediction from previous words), generative AI.

## B. 01b — Regression
- **Regression:** relate input variables to output, to (1) **predict** outputs for new inputs and/or (2) **interpret** the effect of inputs on output.
- **Data:** N pairs (xₙ, yₙ); yₙ ∈ ℝ output, xₙ ∈ ℝ^D input vector. N = data size, D = dimensionality.
- Need a function f approximating y given x; everything that follows is about choosing f and fitting it.
- **Linear regression** — simplest useful f; simple, widely used, generalizes to nonlinear models, and "almost all fundamental ML concepts can be learned with regression alone".
  - Univariate: `yₙ ≈ f(xₙ) = w₀ + w₁ xₙ₁`, parameters w = (w₀, w₁).
  - Multivariate: `yₙ ≈ w₀ + w₁xₙ₁ + … + w_D xₙ_D = x̃ₙᵀ w̃`, with `x̃ₙ = [1, xₙ₁, …, xₙ_D]`, `w̃ = [w₀, …, w_D]` (tilde = includes offset/bias term w₀). So D+1 parameters.
  - Alternative without offset (common in high-dim data): D parameters, `f(x) = xᵀw`.
- **Learning / estimation / fitting:** finding w̃ from data → needs an optimization algorithm (lecture 02).
- **Overparameterization (D > N):** with N = 1 you cannot uniquely determine (w₀, w₁). When #parameters > #examples the problem is under-determined ("p > n" in statistics). **Regularization** fixes identifiability (later). Overparameterization can also help training dynamics.
- Warning: #weights ≠ D in general (e.g. neural networks).
- Not exam material: correlation ≠ causation; jargon (inputs = features/covariates/regressors/predictors; outputs = target/label/response/regressand); prediction vs interpretation questions; matrix-multiplication shape rule (M×N)·(N×D) = M×D.

## C. 01c — Loss functions
- **Loss / cost / energy / training objective L(w):** quantifies how well the model explains the data ("how costly our mistakes are"); used to learn w.
- Two desirable properties (real-valued y): symmetric around 0 (positive/negative errors penalized equally); "large" and "very large" mistakes penalized similarly (robustness).
- **Statistical vs computational trade-off:** statistical = copes with outliers; computational = convex so we can find the minimum. Better statistical properties ⇒ worse computational ones.
- **MSE** (course convention, with 1/2N):
  `L(w) = MSE(w) = 1/(2N) Σₙ (yₙ − f(xₙ))² = 1/(2N) Σₙ eₙ²`, error `eₙ = yₙ − xₙᵀw`.
  Symmetric; convex; **not robust to outliers** (quadratic growth). Exercise on slides: 1-param model, y = (1,2,3,4) then adding y₅ = 20 shifts the minimizer a lot.
- **MAE:** `L(w) = 1/N Σₙ |yₙ − f(xₙ)|`. Robust to outliers (linear growth), convex, but non-differentiable at 0 (kink) → subgradients (lecture 02).
- **Outliers:** examples far from the bulk; common in practice (Newcomb speed-of-light data). Handling them = statistical property.
- **Convexity:** h: ℝ^D → ℝ is convex iff ∀u, v, ∀λ ∈ [0,1]: `h(λu + (1−λ)v) ≤ λ h(u) + (1−λ) h(v)` (segment between two graph points lies above the graph). Strictly convex if strict inequality.
  - Strictly convex ⇒ unique global minimum w★. Convex ⇒ every local minimum is global.
  - Sums of convex functions are convex ⇒ **MSE + linear model is convex in w** (each (yₙ − xₙᵀw)² is convex in w). Same for MAE (|affine| is convex).
- Additional reading: **Huber loss** (quadratic near 0, linear beyond δ: convex, differentiable, robust; δ hard to set); **Tukey's bisquare** (non-convex, robust; defined via gradient). Robust statistics (Wikipedia; Murphy §2.4). Karpathy's lossfunctions.tumblr.com.

## Exam-relevant points / pitfalls
- Know MSE vs MAE: convex both; MSE differentiable, MAE robust. Which loss for a bounded real-valued target? (2025 Q4: MAE, not logistic/hinge/0-1.)
- Definition of convexity and "sum of convex is convex" appear in open questions (e.g. 2024 Q40 on convex f₁, f₂).
- D > N ⇒ XᵀX singular ⇒ least squares non-unique; ridge fixes it (2025 Q7).
- Keep dimensions straight: X is N×D, w is D (or D+1 with offset).
