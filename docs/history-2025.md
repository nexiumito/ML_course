# Previous edition (Fall 2025) — recoverable from git history

The upstream repo is reset every September (`remove old materials`, 2026-09-08, commit `48f3822`), but the **full 2025 content is still in git history**. Run `git fetch upstream` once, then read any 2025 file with:
```
git show '48f3822^:<path>' > /tmp/file        # quote the ref: zsh mangles the ':' otherwise
git ls-tree -r --name-only '48f3822^' -- labs/ex05   # list files
```
Use this to **look ahead**: lab sheets, lecture PDFs, solutions and project descriptions for the whole semester (2025 content is likely ≈ 2026 content; instructors were R. West in 2025, Flammarion & Jaggi in 2026 and 2024, so 2024 files under `lectures/2024/` in that tree are also relevant).

## 2025 labs (path → topic → sections)
| Lab | 2025 date | Topic | Sections / files |
|---|---|---|---|
| ex02 | 09-19 | Linear regression & gradient descent | cost function (MSE/MAE), grid search, GD, SGD, outliers & MAE, subgradient descent. Files: `costs.py`, `grid_search.py`, `gradient_descent.py`, `stochastic_gradient_descent.py`, `subgradient_mae.py`, `helpers.py`, `plots.py`, `ex02.ipynb`. Theory solutions PDF. |
| ex03 | 09-26 | Least squares, ridge regression, overfitting | least squares & polynomial basis (`build_polynomial.py`), train/test split evaluation, ridge regression |
| ex04 | 10-02 | Cross-validation & bias–variance | k-fold CV (`least_squares.py`, `ridge_regression.py`), visualizing bias–variance decomposition |
| ex05 | 10-09 | Logistic regression | classification with linear regression, logistic regression (GD, Newton), regularized logistic regression |
| ex06 | 10-16 | SVM | SVM via SGD, SVM via coordinate descent (dual) |
| ex07 | 10-30 | Kernels & NN introduction | theory-solutions PDF available |
| ex08 | 11-06 | NN training & CNNs | PyTorch, theory-solutions PDF |
| ex09 | 11-13 | Adversarial robustness | theory-solutions PDF |
| ex10 | 11-20 | K-means clustering | theory, implementing k-means, image compression with k-means |
| ex11 | 11-27 | Matrix factorization & recommender systems + Project Q&A | theory-solutions PDF |
| ex12 | 12-05 | Matrix factorizations & recommender systems (notebook) | |
| ex13 | 12-11 | GPT & GANs | `gpt-multiplication.ipynb`, `gans.ipynb` |

2025 lectures: 01a intro, 01b regression, 01c linear_regression, 01d loss_functions, 02a optimization, 03a least_squares, 03b overfitting, 03c maximum_likelihood, 03d ridge, 04a/b, 05a/b, 06a/b, 07a/b, 08a/b, 09a/b, 10a/b, 11a/b, 12a text, 12b llms, 13a self_supervised, 13b generative (each with an `_annotated` version). Plus `lectures/handout_linalg_book.pdf`.

## 2025 publication timeline (predicts 2026)
- Lecture slides: pushed the day of / day before the lecture; annotated version 1–2 days after.
- Lab sheet + template: pushed the day before or the day of the Thursday session.
- **Lab solutions for ex02–ex07 were withheld until after the Project 1 deadline** (published 2025-11-03 → 11-10) because those labs implement the six Project 1 functions. Solutions for ex01 and ex08+ came within a week. ⇒ Do not wait for solutions of labs 2–7; they are your Project 1.
- Project 1 launched 2025-09-18 (week 2 lab), deadline 2025-10-31. Project 2 description published 2025-10-09 (before the P1 deadline!), deadline 2025-12-18, team-formation cutoff 11-18, lab-registration form for ML4Science by 11-04.

## 2025 Project 1 files (all under `projects/project1/` in `48f3822^`)
`project1_description.pdf`, `helpers.py` (`load_csv_data(data_path, sub_sample=False)` → `x_train, x_test, y_train, train_ids, test_ids`, labels in {−1, 1}; `create_csv_submission(ids, y_pred, name)`), `data/dataset.zip` (77 MB; x_train.csv, y_train.csv, x_test.csv), `data/sample-submission.csv`, `grading_tests/` (`pytest --github_link <repo> .` from that dir, checks signatures of the 6 functions, conda `environment.yml`), `latex-example-paper/` (IEEEtran 2-column template + `literature.bib`).

## 2025 Project 2 files
`project2_description.pdf`, `project_road_segmentation/` (README, `segment_aerial_images.ipynb`, `tf_aerial_images.py`), `project_text_classification/` (README, GloVe co-occurrence pipeline: `build_vocab.sh`, `cut_vocab.sh`, `pickle_vocab.py`, `cooc.py`, `glove_template.py`/`glove_solution.py`).
