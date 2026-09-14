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
| ex01 | 2026-09-10 | NumPy / vectorization (standardize, pairwise distances, Gaussian likelihood) | ✅ solutions available (`labs/ex01/solution/`) | Student's own status: TODO — update when done |
| ex02 | 2026-09-17 | Linear regression & GD: cost (MSE/MAE), grid search, GD, SGD, subgradient (2025 files: `costs.py`, `grid_search.py`, `gradient_descent.py`, `stochastic_gradient_descent.py`, `subgradient_mae.py`) | ⏳ not yet in repo | 2025 version viewable via `git show '48f3822^:labs/ex02/exercise02.pdf'` |
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

## Gotchas / lessons learned (append as the semester goes)
- `np.std` uses population std (ddof=0) — matches the doctest in Task A.
- Broadcasting: `P[:, None, :] − Q[None, :, :]` gives (p, q, 2); reduce over the last axis.
