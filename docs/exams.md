# Exams

## Inventory (`exam/`)
All finals 2016–2025 have solutions. Format with MC / true-false / open parts since the **2019** edition; 2016–2018 use numbered problems.

| Year (edition) | Held | Exam | Solutions | Pages | Format |
|---|---|---|---|---|---|
| 2025 | 2026-01-15, 15:15–18:15, STCC (Prof. R. West) | `exam/final-exam-2025.pdf` | `exam/final-exam-2025-solutions.pdf` | 23 / 27 | MC + T/F + open |
| 2024 | 2025-01-16, 15:15–18:15, STCC | `exam/final-exam-2024.pdf` | `exam/final-exam-2024-solutions.pdf` | 20 / 21 | MC + T/F + open |
| 2023 | 2024-01-18, 15:15–18:15, STCC | `exam/final-exam-2023.pdf` | `exam/final-exam-2023-solutions.pdf` | 20 / 17 | MC + T/F + open |
| 2022 | 2023-01-20, 15:15–18:15, STCC | `exam/final-exam-2022.pdf` | `exam/final-exam-2022-solutions.pdf` | 24 / 20 | MC + T/F + open |
| 2021 | 2022-01-20, 08:15–11:15, STCC | `exam/final-exam-2021.pdf` | `exam/final-exam-2021-solutions.pdf` | 20 / 21 | MC + T/F + open |
| 2020 | 2021-01-13, 16:15–19:15, STCC | `exam/final-exam-2020.pdf` | `exam/final-exam-2020-solutions.pdf` | 20 / 22 | MC + T/F + open |
| 2019 | 2020-01-15 (Jaggi & Urbanke) | `exam/final-exam-2019.pdf` | `exam/final-exam-2019-solutions.pdf` | 16 / 16 | MC + T/F + open (first of this format) |
| 2018 | 2019-01-17 | `exam/final-exam-2018.pdf` | `exam/final-exam-2018-solutions.pdf` | 22 / 29 | numbered problems, 1–2.5 pts each (MC/short) |
| 2017 | 2018-01-17 | `exam/final-exam-2017.pdf` | `exam/final-exam-2017-solutions.pdf` | 20 / 20 | numbered problems, 1–1.5 pts each (MC/short) |
| 2016 | 2017-01-16, 16:15–19:15 (Jaggi & Urbanke) | `exam/final-exam-2016.pdf` | `exam/final-exam-2016-solutions.pdf` | 18 / 18 | 5 problems (I: 57 pts MC-ish, II–V: 5/10/10/20) ; exam was 60 % then |

Mock midterms (`exam/mock-midterm-exam/`, short derivation problems, mid-November of the respective year — **there is no midterm in 2026**, useful as extra theory exercises on the first half: regression, MAE subgradient, multi-output regression, ridge, logistic regression, …):
| Year | Exam | Solutions | Pages |
|---|---|---|---|
| 2014 | `mock-exam-2014.pdf` | `mock-exam-2014-solutions.pdf` | 6 / 9 |
| 2015 | `mock-exam-2015.pdf` | `mock-exam-2015-solutions.pdf` | 8 / 5 |
| 2017 | `mock-exam-2017.pdf` | `mock-exam-2017-solutions.pdf` | 5 / 5 |
| 2018 | `mock-exam-2018.pdf` (2018-11-19) | `mock-exam-2018-solutions.pdf` | 6 / 7 |

## Current format (2019–2025, expected for Jan 2027)
- **180 min**, closed book, **one double-sided A4 cheat sheet** (hand-written or ≥ 11 pt in 2020 rules), no electronics. Held at SwissTech (STCC). Each student gets a different (shuffled) version. Booklet of 20 pages; answers only in the booklet; last 2 pages scrap.
- "This exam has many questions. We do not expect you to solve all of them even for the best grade."
- **Part 1 — Multiple choice:** exactly one correct answer (some "select all that apply"), **2 pts** correct / 0 otherwise (no negative points). 2025: Q1–Q28; 2024: Q1–Q25; 2023: Q1–Q12.
- **Part 2 — True/False:** **1.5 pts** correct / 0 otherwise. 2025: Q29–Q42; 2024: Q26–Q39; 2023: Q13–Q32.
- **Part 3 — Open questions:** 2–5 themed problems with sub-questions worth 1–8 pts each; "answer must be justified with all steps"; boxes are for graders. 2025: Q43–Q51 (≈38 pts: ridge bias 3, momentum variance 3, MLE 3, EM light bulbs 8, backprop/scaling 7, PPO 3, bias–variance 2, symmetric init 5, diffusion forward marginals 4). 2024: Q40–Q46 (convexity 3, logistic loss 3, kernels 1+4+2, ReLU nets implementing identity/max 4+6). 2023: Q33–Q42 (NN/GeLU, GMM/EM derivations, weighted objectives, diffusion score matching).
- 2025 total ≈ 28×2 + 14×1.5 + 38 = 115 pts; grading scale not published.

## Recurring topics (from 2023–2025 question labels)
Linear regression & least squares (gradient of MSE, Hessian complexity, projection matrix, orthogonal design, feature scaling/centering) · ridge/lasso (d > n, bias of ridge) · MLE · optimization (GD convergence on convex loss, SGD unbiasedness, momentum, 0-1 loss unsuitability, MAE robustness) · logistic regression (MLE on tiny datasets, SGD step) · SVM (soft-margin, support vectors, L1-SVM, advantages) · k-NN (non-parametric, training cost, bias–variance in K, 1-NN generalization bound) · kernels (validity, sums/products of kernels, polynomial kernel proofs, kernel trick) · generalization (Hoeffding, overfitting on test data, cross-validation / model selection, bias–variance decomposition) · neural nets (ReLU nets implementing functions, backprop by hand, receptive fields/pooling in CNNs, batch norm, GeLU, symmetric initialization) · transformers (attention formula, causal mask, complexity O(n²), BERT vs GPT objectives, in-context learning, 3-D parallelism) · adversarial ML (FGSM, adversarial risk, robustness/accuracy trade-off) · fairness (independence / FPR criteria) · unsupervised (k-means, k-means++, GMM, EM E/M-steps by hand, PCA ↔ k-means as matrix factorization) · matrix factorization for recommenders · text representation (FastText, word embeddings) · generative models (GANs discriminator, diffusion forward process, denoising score matching) · contrastive / self-supervised learning · RL basics (PPO in 2025).

## Revision advice
- The exam is **theory-heavy** (lab 1 sheet explicitly warns about this): do the theory questions in every lab sheet, derive gradients/updates by hand.
- Work through 2023–2025 in exam conditions (they match the current syllabus best), then 2020–2022; older ones for extra derivation practice.
- Build the A4 cheat sheet progressively from `docs/lectures/*.md` + `docs/glossary.md`.
- No negative marking ⇒ answer every MC/TF question.
- A sample exam for 2026 will be provided by the teaching team before the session (per info sheet) — add it here when it appears.
