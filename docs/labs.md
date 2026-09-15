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
| ex02 | 2026-09-17 | Linear regression & GD: MSE cost, grid search, GD, SGD, outliers, MAE subgradient descent | ⏳ student not started; template in repo (2026-09-15), no solution until after P1 deadline | Sheet identical to 2025. Details below. |
| ex03 | 2026-09-24 | Least squares, polynomial basis, train/test split, ridge | ⏳ | **P1 function** `least_squares`, `ridge_regression` |
| ex04 | 2026-10-01 | Cross-validation, bias–variance | ⏳ | |
| ex05 | 2026-10-08 | Logistic regression (+ regularized, Newton) | ⏳ | **P1 functions** `logistic_regression`, `reg_logistic_regression` |
| ex06 | 2026-10-15 | SVM via SGD and coordinate descent | ⏳ | |
| ex07 | 2026-10-29 | Kernels & NN intro | ⏳ | |
| ex08 | 2026-11-05 | NN training & CNNs (PyTorch) | ⏳ | |
| ex09 | 2026-11-12 | Adversarial robustness | ⏳ | |
| ex10 | 2026-11-19 | K-means (+ image compression) | ⏳ | |
| ex11 | 2026-11-26 | Matrix factorization / recommenders + P2 Q&A | ⏳ | |
| ex12 | 2026-12-03 | Matrix factorization notebook + P2 Q&A | ⏳ | |
| ex13 | 2026-12-10 | GPT multiplication & GANs | ⏳ | |

Topics for ex02–ex13 are the 2025 ones (see `docs/history-2025.md`); confirm when each 2026 sheet is published. **Solutions for ex02–ex07 are only released after the Project 1 deadline** (they are the P1 functions) — don't wait for them.

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
- Theory questions: rewrite MSE with e (Ex 1a); chain rule for subgradient (Ex 6a). 2025 theory solutions PDF: `git show '48f3822^:labs/ex02/solution/solutions-theory-questions.pdf'`.

## Gotchas / lessons learned (append as the semester goes)
- `np.std` uses population std (ddof=0) — matches the doctest in Task A.
- Broadcasting: `P[:, None, :] − Q[None, :, :]` gives (p, q, 2); reduce over the last axis.
