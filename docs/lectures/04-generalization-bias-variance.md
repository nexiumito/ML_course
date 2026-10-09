# Lecture 04 — Generalization, Model Selection & Validation; Bias–Variance Decomposition

Sources (lecturer: Nicolas Flammarion; pulled 2026-10-01; no annotated version — Flammarion does not annotate his slides (confirmed 2026-10-08)):
- §A `lectures/04/lecture04a.pdf` (27 p., 2026-09-29) — Generalization, model selection, validation
- §B `lectures/04/lecture04b.pdf` (34 p., 2026-09-30) — Bias–variance decomposition

**Slide numbering differs from lectures 01–03:** in these Flammarion decks the title page is p. 1, so **"slide N" = PDF page N** (04a prints the number on most slides; 04b prints almost none → use the PDF page). Render slide N with `pdftoppm -f N -l N`.
Formulas below were checked against rendered slides (2026-10-01); most formulas are real text in these PDFs.

## §A Generalization, model selection, validation (04a)
- **Scope (sl. 2–4):** how to verify a trained f is good, and how to choose **hyperparameters** (ridge λ, polynomial degree d, and for NNs: optimizer, step size, batch size, architecture, width/depth, weight decay, early stopping, data augmentation…).
- **Probabilistic setup (sl. 5):** unknown distribution 𝒟 on 𝒳 × 𝒴; dataset S = {(xₙ, yₙ)}ₙ₌₁ᴺ ~ 𝒟 i.i.d.; learning algorithm 𝒜(S) = f_S (write f_{S,λ} to show the hyperparameter).
- **True risk (sl. 6):** L_𝒟(f) = 𝔼_{(x,y)~𝒟}[ℓ(y, f(x))] — a.k.a. true/expected/generalization risk/error/loss. The quantity we care about; **not computable** (𝒟 unknown). ℓ e.g. ½(y − y')², logistic, hinge.
- **Empirical risk (sl. 7):** L_S(f) = (1/|S|) Σ_{(xₙ,yₙ)∈S} ℓ(yₙ, f(xₙ)). Random variable (S random); **unbiased** estimator of L_𝒟(f) for a *fixed* f; LLN: L_S(f) → L_𝒟(f) as |S| → ∞, but with fluctuations. **Generalization gap** = |L_𝒟(f) − L_S(f)|.
- **Training error (sl. 8):** L_S(f_S) — same data used to train and evaluate. It is what we minimize; **not** representative of fresh data since f_S depends on S → overfitting.
- **Train/test split (sl. 9):** S = S_train ∪ S_test; learn f_{S_train}, evaluate L_{S_test}(f_{S_train}). Independence ⇒ L_{S_test}(f_{S_train}) ≈ L_𝒟(f_{S_train}). Trade-off: less data for both learning and validation.
- **Generalization bound, one model (sl. 10–11):** for f fixed (not trained on S_test), ℓ ∈ [a, b]:
  ℙ[ |L_𝒟(f) − L_{S_test}(f)| ≥ √((b−a)² ln(2/δ) / (2|S_test|)) ] ≤ δ.
  Error shrinks as O(1/√|S_test|); δ only enters through ln (high-probability bound). Usable form: with prob. ≥ 1 − δ, L_𝒟(f_{S_train}) ≤ L_{S_test}(f_{S_train}) + √((b−a)² ln(2/δ) / (2|S_test|)) (computable RHS).
- **Proof = concentration (sl. 12–13):** Θₙ = ℓ(yₙ, f(xₙ)) ∈ [a, b] are i.i.d. **because f is fixed and independent of S_test**; their mean is L_{S_test}(f), their expectation L_𝒟(f). **Hoeffding:** ℙ[|(1/N) Σ Θₙ − 𝔼Θ| ≥ ε] ≤ 2 exp(−2Nε²/(b−a)²). Set δ = 2 exp(−2|S_test|ε²/(b−a)²) and solve for ε.
- **Model selection (sl. 14–15):** candidates {λₖ}ₖ₌₁ᴷ. Split once; train K times on S_train → f_{S_train,λₖ}; compute each test error; pick λ with the smallest test error. Curves (sl. 15): train/test error vs λ (ridge) and vs degree (polynomial).
- **Does it work? K models (sl. 16–18):** union bound over the K candidates:
  ℙ[ maxₖ |L_𝒟(fₖ) − L_{S_test}(fₖ)| ≥ √((b−a)² ln(2K/δ) / (2|S_test|)) ] ≤ δ.
  Cost of testing K models is only **ln K** inside the root (√ln K overall) ⇒ we can test many models cheaply; extends to infinitely many models. Proof: ℙ[∪ₖ Aₖ] ≤ Σₖ ℙ[Aₖ] ≤ 2K exp(−2Nε²/(b−a)²).
- **Selected model is near-optimal (sl. 19–20):** k* = argminₖ L_𝒟(fₖ), k̂ = argminₖ L_{S_test}(fₖ). Then
  ℙ[ L_𝒟(f_k̂) ≥ L_𝒟(f_k*) + 2√((b−a)² ln(2K/δ) / (2|S_test|)) ] ≤ δ.
  Factor **2**: worst case, true risk of k̂ is ε above its empirical risk, and empirical risk of k* is ε below its true risk (sl. 20 picture).
- **Cross-validation (sl. 21–22):** one split wastes data. **M-fold CV** (usually "K-fold"; M here because K = # hyperparameter values): randomly partition into M groups; train M times, each time hold out one group as test and train on the other M − 1; average the M results. Every point is used for training and for testing, the same number of times. Returns an estimate of the generalization error **and its variance**.
- **Bonus — Hoeffding proof (sl. 23–27, "Do we still have some time?"):** WLOG 𝔼Θ = 0; show one-sided bound, the other side is symmetric. For s ≥ 0: Markov on e^{s·mean} → product by independence → power N by identical distribution → **Hoeffding's lemma** 𝔼[e^{sX}] ≤ e^{s²(b−a)²/8} for 𝔼X = 0, X ∈ [a, b] (proof: convexity, e^{sx} below its chord on [a, b]) → bound e^{s²(b−a)²/(8N) − sε}, minimized at s = 4Nε/(b−a)² → e^{−2Nε²/(b−a)²}.

## §B Bias–variance decomposition (04b)
- **Scope (p. 2–4):** last time = *quantitative* (bounds, split, selection). Today = *qualitative*: how does the risk behave as a function of the **complexity of the model class**? → bias–variance trade-off.
- **1D experiment (p. 5–14):** true f is a cubic-like curve, 15-ish noisy samples. Degree 1 = bad fit (class not rich enough). Degree 12 = fits training points but wild outside. Randomness: we observed one S_train among many; even with the same xₙ the yₙ vary ⇒ f_S is random. Simple model: moving one point barely moves the line (**underfitting**); complex model: moving one point changes predictions a lot (**overfitting**). Learned functions over many S:
  degree 1 → **large bias, small variance**; degree 9 → **small bias, large variance**; degree 4 → balanced.
- **Data model (p. 15):** y = f(x) + ε, x ~ 𝒟_x (fixed, unknown), f arbitrary unknown (generally **not realizable**: f ∉ model class), ε ~ 𝒟_ε i.i.d., **independent of x**, 𝔼[ε] = 0. Square loss.
- **Setup (p. 16–18):** decomposition holds pointwise, so fix x₀: L(f_S) = 𝔼_ε[(f(x₀) + ε − f_S(x₀))²] — a random variable through S. Picture: run 𝒜 on many independent S₁, …, S_k → look at average and variance of the predictions f_{S₁}(x₀), …, f_{S_k}(x₀).
- **Derivation (p. 19–21):** quantity = 𝔼_{S~𝒟}[L(f_S)] = 𝔼_{S,ε}[(f(x₀) + ε − f_S(x₀))²].
  1. Expand: 𝔼[ε²] + 2𝔼_{S,ε}[ε(f(x₀) − f_S(x₀))] + 𝔼_S[(f(x₀) − f_S(x₀))²]. Cross term = 𝔼[ε]·𝔼_S[…] = 0 (ε ⊥ S, 𝔼ε = 0); 𝔼[ε²] = Var[ε].
  2. Trick: add and subtract 𝔼_{S'~𝒟}[f_{S'}(x₀)] (S' an independent copy; just a constant). Cross term again vanishes because 𝔼_S[𝔼_{S'}[f_{S'}(x₀)] − f_S(x₀)] = 0.
- **Result (p. 22):**
  𝔼_{S,ε}[(f(x₀) + ε − f_S(x₀))²] = **Var_ε[ε]** (noise) + **(f(x₀) − 𝔼_{S'}[f_{S'}(x₀)])²** (bias²) + **𝔼_S[(f_S(x₀) − 𝔼_{S'}[f_{S'}(x₀)])²]** (variance).
  Three **non-negative** terms, each a lower bound on the true error ⇒ need low bias **and** low variance simultaneously.
- **Noise (p. 23):** irreducible; even the true f has L(f) = 𝔼[ε²]; cannot be predicted from data (independent). Flat line vs complexity.
- **Bias (p. 24–25):** squared gap between truth and the *average* prediction; "how far off in general". Low complexity → high bias; high complexity → low bias (decreasing curve).
- **Variance (p. 26–27):** variability of the prediction at x₀ across training sets. Complex models → small changes in S cause big changes → high variance (increasing curve).
- **U-shaped curve (p. 28):** true error = noise + bias² + variance → U-shape; too simple = underfitting, too complex = overfitting. **Bias–variance trade-off.** Challenge + target picture (p. 29–30): low/high bias × low/high variance.
- **In practice (p. 31–32):** you don't know the bias (f unknown); if trained once per complexity level, you don't see the variance; you can't draw the curve before sweeping complexity levels. → Draw **learning curves** (train/test error vs size of data; easy with SGD).
- **Double descent (p. 33–34):** "but this depends on the algorithm!" Beyond the **interpolation threshold** (training risk → 0), test risk can decrease again: classical U-shaped regime (under-parameterized) then modern interpolating regime (over-parameterized). Ref: Belkin, Hsu, Ma, Mandal, PNAS 2019.

## Notation (new)
| Symbol | Meaning |
|---|---|
| 𝒟, 𝒟_x, 𝒟_ε | data distribution on 𝒳 × 𝒴; input marginal; noise distribution |
| 𝒜 | learning algorithm, 𝒜(S) = f_S |
| L_𝒟(f) | true / expected / generalization risk |
| L_S(f) | empirical risk on set S; L_S(f_S) = training error; L_{S_test}(f_{S_train}) = test error |
| ℓ ∈ [a, b] | bounded loss (needed for Hoeffding) |
| δ | failure probability of a high-probability bound |
| K | number of candidate hyperparameter values / models |
| M | number of folds in cross-validation (= "K-fold" elsewhere, e.g. exams and lab 4) |
| k*, k̂ | index of best model in true risk / in test (empirical) risk |

## Exam-relevant points / pitfalls
- Hoeffding applies to the **test** error of a model **independent** of S_test — **not** to the training error L_{S_train}(f_{S_train}), because the losses are no longer independent (f depends on all training points). 2023 Q30: the statement with S_train is **False**.
- 2023 Q31: the slide-19 bound (selected vs best ≤ 2ε, ln(2K/δ)) stated with k̂ = argmin of the **training** error and |S_train| is **False** — it holds only with k̂ chosen on the test/validation error and |S_test|. Same trap as Q30.
- Never tune / "train until low loss" on the test set — it stops being an estimate of unseen-data performance (2024 Q34 False).
- CV cost: K-fold CV over L hyperparameter values ⇒ **K·L trainings** (2025 Q24: 5 λ × 5 folds = **25**). Complexity in K of K-fold CV on linear regression = **O(K)** (2021 Q3: each fold uses (K−1)/K = O(1) of the data, K folds).
- CV helps **select** a model that overfits less; it does **not** lower the training MSE of a given model (2021, overfitting MCQ).
- Bias/variance definitions get swapped in MCQs: bias = truth vs **average** prediction; variance = spread of predictions across training sets. **Noise is the only term independent of the algorithm/complexity** (2025 Q25).
- Complex model = low bias, **high** variance (2025 Q25 trap). High bias does **not** imply low variance (2022 Q27 False: a random-output model has both high).
- A constant predictor (independent of data) has **zero variance** (2021 Q4: quadratic vs constant h = 1/2 → quadratic has lower bias, higher variance).
- σ² lower-bounds the **true** error, not the training error (2021 Q26 False — overfitting can push training error below σ²).
- Ridge vs least squares: ridge has **larger bias, smaller variance** (2022 Q6). λ ↑ ⇒ noise unchanged, bias ↑, variance ↓ (λ = ∞: zero variance) (2020 Q39, 3 pts open question). Same logic for k in k-NN (2025 Q33, week 6).
- Know the bound's shape: O(1/√|S_test|), δ only in ln, K models cost ln K; the factor 2 in the "selected vs best" bound.
- Double descent: no question in finals 2016–2025 (checked 2026-10-02) — culture only.
- Be able to redo the bias–variance derivation (add/subtract 𝔼_{S'}[f_{S'}(x₀)], kill the cross terms). 2025 had a 2-pt bias–variance open question.

## Not exam material
- Hoeffding proof (04a sl. 23–27) was presented as bonus ("Do we still have some time?"). No final exam 2016–2025 asks for it (checked 2026-10-01); exams only use the inequality (2023 Q30–31). Knowing the statement and how it's applied is essential; the proof is low priority. No annotated version will come; check the video if needed.

## Exercises mentioned
- Lab 4 (`labs/ex04/`, 2026-10-01): 4-fold cross-validation for ridge on polynomial degree 7 (train/test RMSE vs λ), best-degree selection over degrees 2–10, bias–variance visualization (degrees 1, 3, 6 over many random training sets; bonus: fixed degree, vary λ).
