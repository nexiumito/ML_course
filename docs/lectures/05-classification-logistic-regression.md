# Lecture 05 — Classification; Logistic Regression

Sources (lecturer: Nicolas Flammarion; pulled 2026-10-08):
- §A `lectures/05/lecture05a.pdf` (33 p., 2026-10-06) — Classification
- §B `lectures/05/lecture05b.pdf` (26 p., 2026-10-07) — Logistic regression

**No annotated version will be published** (Flammarion does not annotate; "everything essential is on the slides" — same for lecture 04).
**Slide numbering:** no printed numbers on these decks → **"slide N" = PDF page N** (title = p. 1). Render with `pdftoppm -f N -l N`.
Formulas below were checked against the rendered slides (2026-10-08); most formulas are real text in these PDFs.

**Proxy for annotations:** the 2025 edition had the same decks (credits Flammarion, 05b taught by R. West) **with handwritten annotations**:
`git show '48f3822^:lectures/05/lecture05a_annotated.pdf'` (37 p.) and `…/lecture05b_annotated.pdf` (34 p.). Content is identical except build-up animation pages (2025 has 4 + 8 extra) and the 05a bonus slide (see below). Useful notes from them are integrated here, marked *(2025 ann.)*.

## §A Classification (05a)
- **Definition (p. 2–3):** S = {(xₙ, yₙ)}ₙ₌₁ᴺ ∈ 𝒳 × 𝒴 with 𝒴 a **discrete set**. Binary: y ∈ {c₁, c₂}, encoded {0, 1} or {−1, 1}. Multi-class: y ∈ {c₁, …, c_K}, encoded {1, …, K}; ⚠ **no ordering between classes**.
- **Examples (p. 4–6):** spam detection, image classification (cat/dog), credit-card default (balance vs income).
- **Classifier (p. 7–9):** f : 𝒳 → 𝒴 divides the input space into regions, one per class, separated by **decision boundaries** — linear or nonlinear.
- **Classification as regression? (p. 10–14):** encode y ∈ {0, 1}, fit least squares, predict class 1 iff f_S(x) ≥ 0.5. Three failures, all because **the square loss is not suited to classification**:
  A. predictions are not probabilities (not in [0, 1]);
  B. **unbalanced classes** move the line (balanced 1:1 vs 1:15);
  C. **extreme values**: far-away, *correctly classified* points still pull the line (square loss penalizes "too correct" predictions).
- **How to classify (p. 15):** fundamental task = divide the space into decision regions. Quick tour today, details later (k-NN and SVM = week 6, kernels = week 8).
- **k-NN (p. 16–17):** nearby points have similar labels; classify x by **majority vote of its k nearest neighbours**. Pros: no optimization/training, easy, works well in **low dimension**, very complex boundaries. Cons: **slow at query time**, bad in high dimension, the choice of the distance is crucial.
- **Linear decision boundaries (p. 18):** f(x) = sign(xᵀw); boundary = hyperplane {x : xᵀw = 0}, w is normal to it.
- **Separating hyperplane, margin (p. 19–21):** data **linearly separable** ⇔ some hyperplane separates the classes perfectly; then infinitely many exist. **Margin** = distance from the hyperplane to the **closest** point. Pick the **max-margin** hyperplane: small changes of the training set keep misclassifications low → leads to SVM and logistic regression.
- **Nonlinear classifiers (p. 22):** e.g. concentric circles — use **feature augmentation** (x, x², x³, x⁴) or the **kernel method**.
- **Formal setting (p. 23):** (X, Y) ~ 𝒟, 𝒴 = {−1, 1}. **0-1 loss** ℓ(y, y') = 𝟙_{y≠y'}. True risk L_𝒟(f) = 𝔼_𝒟[𝟙_{Y≠f(X)}] = ℙ_𝒟[Y ≠ f(X)] = **probability of error** (classification error).
- **Bayes classifier (p. 24):** f* ∈ argmin_f L_𝒟(f) is the best possible classifier, regardless of data size. **Claim:** f*(x) ∈ argmax_{y∈{−1,1}} ℙ(Y = y | X = x) — predict the most probable label given x. Unattainable gold standard (𝒟 unknown).
- **Proof (p. 25):** conditional error r_x(y) = ℙ(Y ≠ y | X = x) = 1 − ℙ(Y = y | X = x). Step 1: g* (argmax of the posterior) minimizes r_x pointwise ⇒ r_x(f(x)) − r_x(g*(x)) ≥ 0 ∀f, x. Step 2 (tower rule): L_𝒟(f) = 𝔼_X[r_X(f(X))] ⇒ L_𝒟(f) − L_𝒟(g*) = 𝔼_X[r_X(f(X)) − r_X(g*(X))] ≥ 0.
- **Two families (p. 26):** **non-parametric** = approximate ℙ(Y = y | X = x) by local averaging (k-NN); **parametric** = minimize the empirical risk on training data (**ERM**).
- **ERM with 0-1 loss (p. 27):** min_f L_train(f) = (1/N) Σ 𝟙_{f(xₙ)≠yₙ} = (1/N) Σ 𝟙_{yₙ f(xₙ) ≤ 0}. **Not convex**: (1) the set of classifiers is not convex (𝒴 discrete); (2) the indicator is not continuous → not convex (and gradient = 0 a.e.).
- **Convex relaxation (p. 28):** (1) learn g : 𝒳 → ℝ in a convex set 𝒢 of continuous functions, predict f(x) = sign(g(x)); (2) replace 𝟙_{yg(x)≤0} by a **convex surrogate** ϕ(yₙ g(xₙ)) — a function of the **functional margin** yₙ g(xₙ) ⇒ convex problem. Remark: under technical assumptions on ϕ, the 0-1 risk is bounded by the ϕ-risk.
- **Losses vs functional margin η = y g(x) (p. 29):** zero-one 𝟙_{η≤0}; square (1 − η)² (grows again for η > 1 → penalizes "too correct" points); **logistic** log(1 + e^{−η}) → logistic regression; **hinge** max(0, 1 − η) → max-margin classification (SVM).
- **Bonus (p. 30–32, "Do we still have time?"):** — 2025 ann.: answered "No." (skipped in 2025).
  - Good regressor ⇒ good classifier: for 𝒴 = {−1, 1}, f_η = sign(η(x)); η* = 𝔼[Y | X = x] minimizes the square risk and f* = f_{η*}; **L^classif(f_η) − L^classif(f*) ≤ √(L^ℓ₂(η) − L^ℓ₂(η*))** (2025 version for 𝒴 = {0, 1} with threshold ½ had a factor 2). Converse false.
  - Over-parameterized regime (n ≪ d): gradient descent gives the same solution for logistic and square loss.
- **Recap (p. 33):** classification ≠ special case of regression (classical regime); non-parametric (k-NN) vs parametric (ERM); nonlinear classifiers; over-parameterized regime: regression and classification solutions coincide.

## §B Logistic regression (05b)
- **Setting (p. 2):** y ∈ {0, 1} (⚠ not {−1, 1} in this lecture).
- **Motivation (p. 3):** model the **probability** ℙ(Y = 1 | X = x) instead of Y. Linear model xᵀw + w₀ fails: not in [0, 1], and very confident predictions still count as error. Fix: map (−∞, +∞) → [0, 1].
- **Log-odds (p. 4):** probability y ∈ [0, 1] ⇔ odds y/(1 − y) ∈ [0, ∞[ ⇔ log-odds log(y/(1 − y)) ∈ ]−∞, ∞[. **Model the log-odds linearly**: log(y/(1 − y)) = xᵀw + w₀ ⇒ y = e^{xᵀw+w₀}/(1 + e^{xᵀw+w₀}) = 1/(1 + e^{−(xᵀw+w₀)}). (logit = σ⁻¹.)
- **Logistic function (p. 5):** σ(η) = eᶯ/(1 + eᶯ) = 1/(1 + e^{−η}). Properties: **1 − σ(η) = 1/(1 + eᶯ) = σ(−η)**; **σ'(η) = eᶯ/(1 + eᶯ)² = σ(η)(1 − σ(η))**.
- **Model (p. 6):** p(1|x) = ℙ(Y = 1 | X = x) = σ(xᵀw + w₀), p(0|x) = 1 − σ(xᵀw + w₀). Predict 1 iff p(1|x) ≥ ½ ⇔ xᵀw + w₀ ≥ 0: **only the sign matters** for the class ⇒ **linear decision boundary**. |xᵀw + w₀| large ⇒ p near 0 or 1 (high confidence); small ⇒ p ≈ ½ (low confidence).
- **Logistic vs linear regression (p. 7–9):** same fit on balanced data; logistic is **robust to unbalanced data and to extreme values**, linear is not.
- **Geometry (p. 10–12, "see video"):** w is **orthogonal** to the transition surface; transition at the hyperplane w^⊥ = {v : vᵀw = 0}. **Scaling w** (t·w) makes the transition sharper or smoother (‖w‖ → ∞ ⇒ step function). **Changing w₀** shifts the region along w; transition at {v : vᵀw + w₀ = 0}.
- **Bias term (p. 13):** w₀ needed (no reason for the hyperplane to pass through 0). In practice append 1 to x: x = (x, 1), w = (w, w₀) ⇒ wᵀx instead of wᵀx + w₀. Equivalent.
- **MLE recap (p. 14):** w* = argmax ℒ(w) = p(z₁, …, z_N | w) = Πₙ p(zₙ | w) (i.i.d.) = argmin −Σₙ log p(zₙ | w). Consistent (under mild conditions): converges to the true parameter if the data follow the model.
- **MLE for logistic regression (p. 15):** assumption **X independent of w**: ℒ(w) = p(y, X | w) = p(X) p(y | X, w), p(X) constant in w. Then p(y | X, w) = Πₙ σ(xₙᵀw)^{yₙ} [1 − σ(xₙᵀw)]^{1−yₙ} (the exponent trick selects the right factor for yₙ ∈ {0, 1}).
- **Negative log-likelihood (p. 16):** −log p(y | X, w) = −Σ [yₙ log σ(xₙᵀw) + (1 − yₙ) log(1 − σ(xₙᵀw))] = Σ [−yₙ xₙᵀw + log(1 + e^{xₙᵀw})] using log(σ/(1 − σ)) = η and −log(1 − σ(η)) = log(1 + eᶯ). **Cost:**
  **L(w) = (1/N) Σₙ [−yₙ xₙᵀw + log(1 + e^{xₙᵀw})]** (y ∈ {0, 1}; a different form for y ∈ {−1, 1}).
- **Logistic loss (p. 17):** NLL = ERM with the logistic loss (surrogate of 0-1). y ∈ {0, 1}: ℓ(y, g(x)) = −y g(x) + log(1 + e^{g(x)}). **y ∈ {−1, 1}: ℓ(y, g(x)) = log(1 + e^{−y g(x)})**. g can be a neural network's output (= cross-entropy).
- **Gradient (p. 18):** ∇L(w) = (1/N) Σ (σ(xₙᵀw) − yₙ) xₙ = **(1/N) Xᵀ(σ(Xw) − y)**. Same form as least squares (Xᵀ(Xw − y)) with σ. **No closed form** for ∇L = 0. L is convex.
- **Convexity, proof 1 (p. 19–21):** convexity-preserving operations: positive combinations of convex functions; convex ∘ linear; linear functions are convex and concave; h(η) = log(1 + eᶯ) is convex since h' = σ, h'' = σ' = eᶯ/(1 + eᶯ)² ≥ 0.
- **Convexity, proof 2 (p. 22):** Hessian ∇²L(w) = (1/N) Σ σ(xₙᵀw)(1 − σ(xₙᵀw)) xₙxₙᵀ = **(1/N) XᵀSX**, S = diag[σ(xₙᵀw)(1 − σ(xₙᵀw))] ⪰ 0 ⇒ vᵀXᵀSXv = (Xv)ᵀS(Xv) ≥ 0 *(2025 ann.)* ⇒ PSD ⇒ convex.
- **Optimization (p. 23):** GD w_{t+1} = w_t − (γ_t/N) Σ (σ(xₙᵀw_t) − yₙ) xₙ (slow per step). SGD w_{t+1} = w_t − γ_t (σ(x_{n_t}ᵀw_t) − y_{n_t}) x_{n_t}, ℙ[n_t = n] = 1/N (cheap step, slower convergence).
- **Newton (p. 24):** minimize the 2nd-order Taylor model φ_t(w) = L(w_t) + ∇L(w_t)ᵀ(w − w_t) + ½(w − w_t)ᵀ∇²L(w_t)(w − w_t) ⇒ ∇L(w_t) + ∇²L(w_t)(w̃ − w_t) = 0 ⇒ **w_{t+1} = w_t − γ_t ∇²L(w_t)⁻¹ ∇L(w_t)** (damped Newton: step size needed for convergence). Fewer iterations than GD, but each costs more (Hessian + linear system).
- **Linearly separable data (p. 25):** inf_w L(w) = 0 = lim_{α→∞} L(α·w̄) for a separating w̄: **infimum not attained** at finite w, the optimizer drives ‖w‖ → ∞. Fix: **ℓ₂ regularization (ridge logistic regression)**: (1/N) Σ [−yₙ xₙᵀw + log(1 + e^{xₙᵀw})] + (λ/2)‖w‖₂². Optimization view: stabilizes; statistical view: avoids overfitting.
- **Recap (p. 26):** outputs class probabilities; robust to unbalanced data and extreme values; solve by minimizing NLL = logistic loss with gradient or second-order methods; separable data ⇒ weights → ∞, add ℓ₂ penalty.

## Notation (new)
| Symbol | Meaning |
|---|---|
| 𝟙_{y≠y'} | 0-1 loss |
| f* | Bayes classifier, argmax_y ℙ(Y = y | X = x) |
| r_x(y) | conditional error ℙ(Y ≠ y | X = x) |
| g, 𝒢 | real-valued score function and its (convex) class; prediction sign(g(x)) |
| ϕ | convex surrogate of the 0-1 loss, applied to the functional margin y g(x) |
| σ(η) | logistic / sigmoid function 1/(1 + e^{−η}) |
| p(1|x) | ℙ(Y = 1 | X = x) = σ(xᵀw) |
| log(p/(1 − p)) | log-odds = logit; logistic regression models it linearly |
| ℒ(w) | likelihood (vs L(w) = cost = NLL / N) |
| S (05b) | diag[σ(xₙᵀw)(1 − σ(xₙᵀw))], Hessian = (1/N) XᵀSX ⚠ not a dataset here |

## Exam-relevant points / pitfalls
- **k-NN is the non-parametric method**; logistic regression, SVM, linear boundaries, NNs are parametric (2025 Q1).
- **Logistic MLE on tiny data**: 1-D model σ(wx), two points at x = 1 and x = −1 with the same label → ℒ ∝ σ(w)σ(−w) = p(1 − p), maximized at p = ½ ⇒ **w = 0** (2025 Q2). Set up the likelihood with the exponent trick, then maximize.
- **Bayes classifier by hand**: compute ℙ(Y = y | X = x) from a joint table / generative process, predict the argmax; best accuracy = Σₓ max_y ℙ(x, y) (or conditional, 2018 Q3: X ≥ 0 ⇒ 5/9). 2025 Q3 with a latent Z: f*(x) given X only ≠ g*(x, z) given (X, Z) in general.
- **Bayes-classifier proof technique is examined as an open problem**: final 2022 Q37–Q52 (≈ 25 pts, Flammarion-style, solutions pp. 15–19): η(x) = ℙ(Y = 1 | x), 𝔼[Y | x] = 2η(x) − 1 (y ∈ {−1, 1}); show sgn(𝔼[Y | x]) is a Bayes classifier; **L* = 𝔼[min(η(X), 1 − η(X))]** via the tower rule + case split on η ≥ ½; square-loss minimizer g* = 𝔼[Y | x] ⇒ sgn(g*) = Bayes; classification-calibrated surrogates ϕ (hinge, logistic, square). Know the 05a p. 25 proof (pointwise optimality + law of total expectation) well enough to redo it.
- **Linear regression predicts class labels / numbers, logistic models the probability** (2024 Q8). Logistic regression boundary is **linear** in the original features (no non-linear boundary without feature augmentation); **no closed form** (2023 Q5, 2024 Q8); GD on separable data does **not** converge in finite steps — weights diverge (2023 Q5, 2024 Q8).
- **Separable data**: 100 % training accuracy reachable but **loss 0 never attained** (2021 Q27 False).
- Effect of x₀ → x₀ + 1 on p̂: depends on x₀ (σ saturates); it's the **odds** that are multiplied by e^{θ₁}, not the probability (2024 Q9).
- **Logistic regression assumes a linear relation between inputs and the logit** of ℙ(Y = 1), not the probability (2020 Q3).
- Know the **gradient** (1/N) Xᵀ(σ(Xw) − y) — 2022 Q3 asks to pick it among look-alikes. **SGD step changes w even for correctly classified points** since σ(xᵀw) ≠ y ∈ {0, 1} always (2023 Q19 False).
- **Standardized features, sign of weights** = direction of correlation with class 1; irrelevant feature ⇒ w ≈ 0 (2022 Q7).
- **GD vs Newton**: GD steps cheaper, Newton fewer steps (2022 Q8). Hessian = (1/N) XᵀSX costs O(ND²) + solve O(D³).
- **Strong ℓ₂ penalty on one weight** (C/2 · w₂²) ⇒ that weight ≈ 0 ⇒ boundary x₁ = 0 (2021 Q17).
- Logistic loss does **not** penalize both directions equally (unlike MSE): wrong side heavily, "too correct" side almost not (2022 Q26 False; 2016 Q12: logistic preferred over L2 for classification because far correctly classified points barely matter).
- **0-1 loss unsuitable for (S)GD**: piecewise constant, gradient zero a.e. (2024 Q39 True).
- Exponential loss (1/N) Σ exp(−yᵢxᵢᵀw): convex; L(w*) < 1/N ⇒ every term < 1 ⇒ yᵢxᵢᵀw* > 0 ∀i ⇒ separates the data (2022 Q1).
- **Numerically stable σ**: use 1/(1 + e^{−x}) for x > 0 and eˣ/(1 + eˣ) otherwise (2019 Q6) — matters for the lab / Project 1.
- Linear separability of 4 points (XOR-like labels impossible) and margin bounds (2024 Q23).
- Imbalanced data: 85 % accuracy with 90 % majority class is worse than the trivial classifier (2017 Q25) — always compare with the constant baseline.
- Medical probability prediction ⇒ logistic rather than linear regression (2020 Q27 True).
- Remember: lecture uses **y ∈ {0, 1}** for the NLL form; with **y ∈ {−1, 1}** the loss is log(1 + e^{−y xᵀw}). Don't mix the two.

## Not exam material / off-syllabus
- **Exponential family / GLMs** (2016 Q7, 2019 Q2, 2020 Q8, Q23, 2022 Q20, mock 2017–2018, Poisson open questions): **not in the 2026 (nor 2025) lecture 05** — older editions' content. Low priority unless it reappears (checked 2026-10-08).
- Bonus slides 05a p. 30–32 (regressor ⇒ classifier bound, over-parameterized regime): skipped in 2025; culture only. No final 2016–2025 asks about them (checked 2026-10-08).
- Multi-class logistic regression (softmax / log-sum-exp, mock 2014–2015): not covered in 05b.

## Exercises mentioned
- Lab 5 (`labs/ex05/`, 2026-10-08): classification with least squares on height/weight → gender; logistic regression by GD (sigmoid, loss, gradient); Newton's method (Hessian, `np.linalg.solve`); penalized logistic regression (λ‖w‖², penalty excluded from the reported loss). **Project 1 functions** `logistic_regression`, `reg_logistic_regression`.
