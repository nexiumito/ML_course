# Glossary & notation (CS-433 conventions)

Extend this file whenever a lecture introduces new notation. Conventions follow the course slides/labs/exams.

## Data & model
| Symbol | Meaning |
|---|---|
| N | number of training examples (data size); n indexes examples (1…N). Labs often use `n`/`num_samples`. |
| D | input dimensionality (number of features); d also used (labs, exams). |
| xₙ ∈ ℝ^D | input (feature) vector of example n. Also called features, covariates, predictors, regressors, independent/explanatory variables. |
| yₙ ∈ ℝ (regression) / label (classification) | output of example n. Also target, label, response, outcome, dependent variable, regressand. |
| X ∈ ℝ^{N×D} | data matrix, **rows = samples, columns = features**. `X[n]` = xₙᵀ. |
| y ∈ ℝ^N | output vector. |
| w ∈ ℝ^D | weights / parameters of the model. w★ = optimal weights. w^(t) = iterate at step t. |
| w₀ | offset / bias / intercept term. |
| x̃ₙ = [1, xₙ], w̃ = [w₀, w] | augmented input/weights including the offset (tilde notation). |
| f(x) = xᵀw (+ w₀) | linear model. Univariate: y ≈ w₀ + w₁x. |
| e = y − Xw ∈ ℝ^N | error / residual vector, eₙ = yₙ − xₙᵀw. |
| D = {(xₙ, yₙ)}ₙ | dataset (script D in slides). |
| θ | generic parameters of a probabilistic model, e.g. θ = (μ, Σ) for a Gaussian. |
| μ ∈ ℝ^d, Σ ∈ ℝ^{d×d} | mean and covariance matrix of a multivariate Gaussian: p(x|μ,Σ) = (2π)^{−d/2}|Σ|^{−1/2} exp(−½(x−μ)ᵀΣ⁻¹(x−μ)). |
| p > n | statistics name for the over-parameterized regime D > N. |

## Loss / optimization
| Symbol | Meaning |
|---|---|
| L(w) | loss = cost = energy = training objective. ℒ also used. |
| Lₙ(w) | loss contributed by example n; L = (1/N) Σ Lₙ. |
| MSE | mean squared error. **Labs / Project 1 / optimization lecture: L(w) = 1/(2N) Σₙ (yₙ − xₙᵀw)²** (½ so that ∇L = −(1/N)Xᵀe, Hessian (1/N)XᵀX). Loss-functions lecture slide 5 writes it **without the ½** (1/N). Same minimizer. |
| MAE | mean absolute error, L(w) = (1/N) Σₙ |yₙ − xₙᵀw|. Subgradient −(1/N)Xᵀsign(e). |
| Huber loss | quadratic for |e| ≤ δ, linear beyond; convex, differentiable, robust. |
| Tukey's bisquare | non-convex robust loss. |
| γ | step-size / learning rate. γ^(t): schedule. |
| GD | gradient descent: w^(t+1) = w^(t) − γ∇L(w^(t)); O(ND) per step for linear MSE. |
| SGD | stochastic gradient descent: same with ∇Lₙ for random n; O(D) per step; unbiased: 𝔼ₙ∇Lₙ = ∇L. |
| Mini-batch B ⊆ [N] | g = (1/|B|) Σ_{n∈B} ∇Lₙ. |B| = N ⇒ batch GD. |
| [N] | {1, …, N}. |
| Momentum, Adam, Adagrad, SignSGD, Muon, AdamW | SGD variants (see `docs/lectures/02-optimization.md`). |
| ∇L(w) | gradient (vector of partial derivatives). ∇²L(w): Hessian. ≻ 0 positive definite, ⪰ 0 PSD. |
| Subgradient g | L(u) ≥ L(w) + gᵀ(u − w) ∀u. |
| Convex function | h(λu + (1−λ)v) ≤ λh(u) + (1−λ)h(v). Strictly convex ⇒ unique global min. |
| Convex set C | θu + (1−θ)v ∈ C for u, v ∈ C, θ ∈ [0,1]. |
| P_C(w) | projection onto C. Projected GD: w^(t+1) = P_C(w^(t) − γ∇L). |
| Critical point | ∇L(w) = 0. |
| Robbins–Monro | Σγ^(t) = ∞, Σ(γ^(t))² < ∞ ⇒ SGD converges (e.g. γ^(t) = 1/t^α, α ∈ (0.5,1]). |
| Grid search | brute-force over a grid; 10^D evaluations for 10 values/dim ("curse of dimensionality"). |
| Ill-conditioning / pre-conditioning | very different curvature across directions; fix by feature normalization / rescaling. |
| O(·) | big-O complexity. Matrix–vector O(ND); matrix–matrix (N×D)(D×K) O(NDK). |

## General ML terms (from the syllabus; details added as lectures happen)
| Term | One-liner |
|---|---|
| Regression / classification / clustering / dimensionality reduction | predict real output / predict discrete label / group unlabeled data / compress features. |
| Overfitting | fitting noise; low train loss, high test loss. |
| Regularization | penalty on w (ridge = λ‖w‖₂², lasso = λ‖w‖₁) to fix identifiability/overfitting. |
| Cross-validation | estimating generalization by held-out folds; used for model/hyperparameter selection. |
| Bias–variance trade-off | decomposition of expected test error. |
| Standardization | (x − mean)/std per feature; ≠ whitening (which also decorrelates). |
| Vectorization | replacing Python loops by NumPy array ops (10–100× faster). |
| ML4Science | Project 2 format: ML applied to a research lab's problem. |
| AICrowd | competition platform for Project 1. |
| Noto | EPFL's hosted JupyterLab. |
