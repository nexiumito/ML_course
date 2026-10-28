# Labs (exercise sessions)

Thursday 14:15–16:00. Not graded, but the theory questions in each sheet are the best exam preparation. Lab materials appear in `labs/exNN/` (pull from upstream); solutions are pushed ~1 week later.

## Standard structure of a lab folder
```
labs/exNN/
  exerciseNN.pdf          problem set: practical tasks (A, B, C, …) + "Theory Questions" section
  template/               notebooks with stubs — THIS is where the student works
    taskX.ipynb           one notebook per task, functions contain:
                            # INSERT YOUR CODE HERE / # TODO … / raise NotImplementedError
    test_utils.py         doctest runner (identical in template/ and solution/)
    *.py                  (later labs) helper modules to complete, imported by notebooks
  solution/               official solutions (arrive later); solved notebooks keep the template
                          text in a `### SOLUTION … ### TEMPLATE … ### END SOLUTION` block
  npprimer.ipynb, python_setup_tutorial.md   (ex01 only) NumPy primer + environment setup
```

## Running & testing
- Local: `cd labs/exNN/template && jupyter notebook` (or VS Code notebooks). Anaconda / Noto / Colab all fine; no GPU needed for early labs.
- Standard first cell: `%matplotlib inline`, `import numpy as np`, `import matplotlib.pyplot as plt`, `%load_ext autoreload`, `%autoreload 2`, `from test_utils import test`.
- **Testing:** every stub has doctest examples in its docstring (`>>> fn(...)` → expected array). After implementing, run `test(fn)`; it prints `✅ Your fn passed k tests.` or `❌` with the doctest diff. `test_utils.test` finds doctests via `doctest.DocTestFinder` with globals `{fn, np}` — so examples may only use `np` and the function itself.
- Precision: doctest compares printed repr, so return NumPy arrays with the exact shape/dtype expected (e.g. `(n,)` not `(n,1)`).
- Headless check of a notebook: `jupyter nbconvert --to notebook --execute template/taskA.ipynb --output /tmp/out.ipynb`.
- Keep everything vectorized (no Python loops over samples) unless the task explicitly asks for a naive baseline.

## Lab status
| Lab | Date | Topic | Status | Notes |
|---|---|---|---|---|
| ex01 | 2026-09-10 | NumPy / vectorization (standardize, pairwise distances, Gaussian likelihood) | ⏳ student not started (solutions available in `labs/ex01/solution/`) | |
| ex02 | 2026-09-17 | Linear regression & GD: MSE cost, grid search, GD, SGD, outliers, MAE subgradient descent | ⏳ student not started; template (2026-09-15) **and solution (2026-09-21)** in repo | Sheet identical to 2025. Details below. Solution includes `solutions-theory-questions.pdf`. |
| ex03 | 2026-09-24 | Least squares, polynomial basis, train/test split, ridge | ⏳ template pulled 2026-09-24; **solution published 2026-10-01** (`solution/`, incl. theory-question PDF); deferred by the student (lectures + P1 first) | **P1 function** `least_squares`, `ridge_regression` |
| ex04 | 2026-10-01 | 4-fold CV for ridge (degree 7, RMSE vs λ), best-degree selection (2–10), bias–variance visualization (degrees 1/3/6, many seeds) | ⏳ template published early, 2026-09-25; **solution published 2026-10-02**; no theory questions in the sheet | reuses ex03 `ridge_regression`, `least_squares`, `build_poly` |
| ex05 | 2026-10-08 | Logistic regression: least-squares classification, GD, Newton, penalized | ⏳ template published 2026-10-02 (sheet dated Oct 7); **solution published 2026-10-13**; no theory questions; deferred | **P1 functions** `logistic_regression`, `reg_logistic_regression`. Details below. |
| ex06 | 2026-10-15 | SVM: SGD on the primal (hinge + ridge), coordinate ascent on the dual; theory: convexity, softmax regression, mixture of linear regressions | ⏳ template pulled 2026-10-13 (sheet identical to 2025); solution not yet (2025 one in history) | Details below. Lecture: `docs/lectures/06-svm-knn.md` §A. |
| ex07 | 2026-10-29 | Kernels (theory), softmax cross-entropy, PyTorch intro: ReLU MLP approximating a 2-D function, MNIST classifier | ⏳ template pulled 2026-10-28 (notebook identical to 2025); solution not yet (2025 one in history) | Details below. Lecture: `docs/lectures/07-kernels-neural-networks.md`. Colab recommended (PyTorch). |
| ex08 | 2026-11-05 | NN training & CNNs (PyTorch) | ⏳ | |
| ex09 | 2026-11-12 | Adversarial robustness | ⏳ | |
| ex10 | 2026-11-19 | K-means (+ image compression) | ⏳ | |
| ex11 | 2026-11-26 | Matrix factorization / recommenders + P2 Q&A | ⏳ | |
| ex12 | 2026-12-03 | Matrix factorization notebook + P2 Q&A | ⏳ | |
| ex13 | 2026-12-10 | GPT multiplication & GANs | ⏳ | |

Topics for ex02–ex13 are the 2025 ones (see `docs/history-2025.md`); confirm when each 2026 sheet is published. The 2025 policy of withholding ex02–ex07 solutions until the P1 deadline does **not** hold in 2026: the ex02 solution was pushed 2026-09-21 (4 days after the lab).

## ex01 — Efficient Python/NumPy programming (details)
Sheet: `labs/ex01/exercise01.pdf`. Goal: vectorized NumPy instead of for-loops. Useful ops: `a*b` elementwise, `a.dot(b)`/`@`, `a.max(0)` per column, `np.sum(a, axis=k)`, `np.mean/np.std`, `a.shape`, `np.linalg.inv`.
- **Task A `standardize(x)`** (x: (N,D)): `(x − x.mean(axis=0)) / x.std(axis=0)` — column-wise zero mean, unit variance. Not whitening (no decorrelation).
- **Task B pairwise distances** P (p,2), Q (q,2) → D (p,q), `D[i,j] = ‖Pᵢ − Qⱼ‖₂`. Four versions compared by `%timeit`: `naive` (triple loop), `with_indices` (`rows, cols = np.indices((p,q))`, then `np.sqrt(np.sum((P[rows.ravel()] − Q[cols.ravel()])**2, axis=1)).reshape(p,q)`), `scipy_version` (`scipy.spatial.distance.cdist`), `tensor_broadcasting` (`np.sqrt(np.sum((P[:,None,:] − Q[None,:,:])**2, axis=2))`). Template also expects optional `naive_2`, `with_indices_2` (comment them out of `methods` if not implemented).
- **Task C Gaussian likelihood** — assign each xₙ to the more likely of k = 2 multivariate Gaussians θₘ = (μₘ, Σₘ). Density `p(x|μ,Σ) = (2π)^{−d/2} |Σ|^{−1/2} exp(−½ (x−μ)ᵀΣ⁻¹(x−μ))`. `compute_p` is given (3 vectorized options for the quadratic form: `np.sum(dxm * (dxm @ inv), axis=1)`; `((dxm @ inv) @ dxm.T).diagonal()`; loop). Student implements **`compute_log_p`**: `−½ Σ_k [dxm ⊙ (dxm Σ⁻¹)]_k − (d/2) log(2π) − ½ log|Σ|`. Use logs to avoid underflow; assignment = `np.argmax(log_ps, axis=0)`. `taskC_detailed_solution.ipynb` shows the diagonal-Σ simplification and timing comparison (vectorized 10–100× faster).
- **Theory part (week 1):** no exercises; refresh linear algebra (multiplication, transpose, inverse, rank, independence, eigen), gradients (Matrix Cookbook), probability (conditional/joint, Bayes, expectation/variance, Gaussian; Bishop ch. 2).
- `npprimer.ipynb` covers: array creation, elementwise ops, indexing/slicing, reshape, reductions, linear algebra, boolean masks, `np.indices`, SciPy intro.

## ex02 — Linear regression and gradient descent (details)
Sheet: `labs/ex02/exercise02.pdf` (identical to 2025 except dates). Work in `labs/ex02/template/ex02.ipynb`, then copy code into `costs.py`, `grid_search.py`, `gradient_descent.py`, `stochastic_gradient_descent.py`, `subgradient_mae.py` for reuse (**Project 1 needs them**).
- **Data:** `height_weight_genders.csv` (10 000 rows: Gender, Height, Weight). `helpers.load_data(sub_sample=True, add_outlier=False)` converts to metric (height×0.025, weight×0.454), sub-samples 1/50 (200 pts), and can append two outliers (heights 1.1/1.2 m, weights in pounds). `standardize(x)` → `(x, mean_x, std_x)` (scalar mean/std, 1-D input). `build_model_data(height, weight)` → `y = weight`, `tx = [1, height]` (N×2). `batch_iter(y, tx, batch_size, num_batches=1, shuffle=True)` yields mini-batches. `plots.py`: `grid_visualization`, `gradient_descent_visualization` (used with `ipywidgets.interact` sliders).
- **Model:** `yₙ ≈ w₀ + w₁ xₙ₁`, w = [w₀, w₁]; X̃ = [1, x] so `tx @ w` gives predictions.
- **Ex 1 `compute_loss(y, tx, w)`:** MSE `L(w) = 1/(2N) eᵀe` with `e = y − tx @ w`. Later modified for MAE `1/N Σ|eₙ|`.
- **Ex 2 `grid_search(y, tx, grid_w0, grid_w1)`:** returns loss matrix over all (w₀, w₁) combos (`generate_w(num_intervals)` builds grids; `get_best_parameters(w0, w1, losses)` picks the min). Compare grid spacing 50 vs 10; cost is exponential in #parameters.
- **Ex 3 `compute_gradient(y, tx, w)`:** `−(1/N) tx.T @ e`. `gradient_descent(y, tx, initial_w, max_iters, gamma)` returns `(losses, ws)` lists (**note: lab returns all iterates; Project 1 wants only the last `(w, loss)`**). Experiments: γ ∈ {0.001, 0.01, 0.5, 1, 2, 2.5} (diverges for γ ≥ 2 on standardized data — Hessian ≈ I so 0 < γ < 2), initializations (0,0), (100,10), (−1000,1000) with γ = 0.1.
- **Ex 4 `compute_stoch_gradient(y, tx, w)`** (same formula on a batch) and `stochastic_gradient_descent(y, tx, initial_w, batch_size, max_iters, gamma)` using `batch_iter`. Project 1 requires batch size 1.
- **Ex 5:** reload with `sub_sample=True` then `add_outlier=True`; MSE fit is dragged by the 2 outliers.
- **Ex 6 `compute_subgradient_mae(y, tx, w)`:** `−(1/N) tx.T @ sign(e)` (any value in [−1,1] at eₙ = 0); `subgradient_descent` and `stochastic_subgradient_descent` mirror Ex 3/4. Questions: MAE fit better with outliers? did you hit a non-differentiable point? (practically never with float data).
- Theory questions: rewrite MSE with e (Ex 1a); chain rule for subgradient (Ex 6a). Theory solutions: `labs/ex02/solution/solutions-theory-questions.pdf`.

## ex05 — Logistic regression (details)
Sheet: `labs/ex05/exercise05.pdf` (Problem Set 5, Oct 7, 2026). Work in `labs/ex05/template/ex05.ipynb`; copy `least_squares` from ex03 into `least_squares.py`. Data: `height_weight_genders.csv` (200 random points), predict gender from height/weight. Lecture: `docs/lectures/05-classification-logistic-regression.md` §B.
- **Ex 1:** classify with least squares (threshold the regression output), `visualization()` plots the boundary.
- **Ex 2:** `sigmoid`, `calculate_loss` (NLL, y ∈ {0,1}, 1/N factor), `calculate_gradient` = (1/N) Xᵀ(σ(Xw) − y), `learning_by_gradient_descent` (one step, returns loss and new w).
- **Ex 3:** `calculate_hessian` = (1/N) XᵀSX, `logistic_regression` returns (loss, gradient, Hessian) without updating w, `learning_by_newton_method` (one damped step; use `np.linalg.solve`, never invert).
- **Ex 4:** `penalized_logistic_regression` adds λ‖w‖² (gradient + 2λw); **the reported loss excludes the penalty** (same convention as Project 1). Check that ‖w‖ shrinks as λ grows and that tiny λ reproduces Ex 2.
- Pitfalls: y must be (N,) in {0,1} (not ±1); stable sigmoid / log(1 + eᶻ) (`np.logaddexp(0, z)`) to avoid overflow; doctests compare exact shapes.

## ex06 — Support Vector Machines (details)
Sheet: `labs/ex06/exercise06.pdf` (Problem Set 6, Oct 15, 2026; identical to 2025 apart from wording of 2.4). Work in `labs/ex06/template/ex06.ipynb`. Data: a scikit-learn toy dataset (no more height/weight), labels **y ∈ {−1, +1}**.
- **Problem 1 (SGD, primal)** objective (1/N) Σ [1 − yₙxₙᵀw]₊ + (λ/2)‖w‖². Stubs: `calculate_primal_objective(y, X, w, lambda_)`, `calculate_accuracy(y, X, w)` (predict sign(Xw)), `calculate_stochastic_gradient(y, X, w, lambda_, n, num_examples)` = −yₙxₙ·𝟙[yₙxₙᵀw < 1] + λw; `sgd_for_svm_demo` given.
- **Problem 2 (coordinate ascent, dual)** max_{α∈[0,1]ᴺ} αᵀ1/N − αᵀYXXᵀYα/(2λN²), w(α) = XᵀYα/(λN). Derive: f(α + γeₙ) is a concave quadratic in γ ⇒ γ* = λN(1 − yₙwᵀxₙ)/‖xₙ‖², then **clip** αₙ to [0, 1]; update w ← w + (αₙ_new − αₙ_old) yₙxₙ/(λN). Both O(D). Stubs: `calculate_coordinate_update(y, X, lambda_, alpha, w, n)` → (w, alpha), `calculate_dual_objective(y, X, w, alpha, lambda_)` = (1/N)Σα − (λ/2)‖w‖² (uses w(α), no N×N matrix). Then compare primal vs dual objectives: the duality gap should → 0.
- **Theory (no lecture-06 content):** convexity proofs (affine, sums, g∘f with g increasing, f(wᵀx + b), uniqueness of the minimizer of a strictly convex f), multiclass logistic regression with softmax (log-likelihood, gradient, convexity via Hölder), mixture of linear regressions (likelihood with rₙₖ, marginal, convexity/identifiability). 2025 theory solutions: `git show '48f3822^:labs/ex06/solution/solutions-theory-questions.pdf'`.
- Pitfalls: copy αₙ before updating (`old_alpha_n`); w is updated in place; doctests compare exact float output.

## ex07 — Kernels & NN introduction (details)
Sheet: `labs/ex07/exercise07.pdf` (Problem Set 7, Oct 29, 2026). Notebook `labs/ex07/template/ex07.ipynb` (byte-identical to 2025); needs **PyTorch** (sheet recommends Google Colab; `torchvision` for MNIST).
- **Problem 1 (kernels, theory):** k₁ valid ⇒ f(k₁) valid for f a polynomial with positive coefficients (sums + products + constants); exp(k₁) valid (limit of the Taylor partial sums, using the given closure-under-limits property).
- **Problem 2 (softmax cross-entropy, theory):** stable softmax (subtract maxⱼ xⱼ); ∂H/∂xⱼ = zⱼ − yⱼ for one-hot y; minimizer pushes x_y − x_other → ∞ (no finite minimizer) → label smoothing ŷ = (1 − ε)y + ε1/d.
- **Problem 3 (PyTorch):** intro (tensors, autograd, `zero_grad`, `torch.no_grad`). Ex 1: approximate f(x₁, x₂) = cos(10‖x‖)·exp(−4‖x‖²) on [−1, 1]² with a ReLU MLP — stubs `get_model_weights(L, K, device)`, `predict(X, weights, biases)`, `train_network(...)` (full-batch Adam); play with depth/width. Ex 2: MNIST classifier `MNIST_model(torch.nn.Module)` + fill `train_epoch`.
- 2025 theory solutions: `git show '48f3822^:labs/ex07/solution/solutions-theory-questions.pdf'`; 2025 notebook solution: `…/labs/ex07/solution/ex07.ipynb`.

## Gotchas / lessons learned (append as the semester goes)
- `np.std` uses population std (ddof=0) — matches the doctest in Task A.
- Broadcasting: `P[:, None, :] − Q[None, :, :]` gives (p, q, 2); reduce over the last axis.
