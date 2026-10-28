# CS-433 Fall 2026 — Week-by-week schedule

Source: course website (verified 2026-09-14). "Approximate, subject to change." Lectures Tue 16:15 + Wed 10:15, labs Thu 14:15.
Status column = **the student's personal progress** (not just what is published): ✅ caught up / done · 🔄 in progress · ⏳ upcoming. Update it every session. The student does not attend lectures; he catches up from slides + video (see `CLAUDE.md` § Working with the student).

| Wk | Tue | Tue lecture | Wed lecture | Thu lab | Deadlines / events | Status |
|---|---|---|---|---|---|---|
| 1 | 09-08 | Introduction; Linear Regression (01a, 01b) | Loss functions (01c) | Lab 1 (09-10): NumPy, vectorization | — | ✅ lectures 01a/b/c caught up (01c with video + annotations, 09-16); lab 1 not started |
| 2 | 09-15 | Optimization (02a) | Optimization (cont.) | Lab 2 (09-17): GD/SGD/grid search/MAE | **Project 1 launched 09-17** (deadline Thu 10-29 16:00) | ✅ 02a fully caught up (slides 1–50 + annotations, finished 2026-09-18); lab 2 not started (next session) |
| 3 | 09-22 | Least Squares; Overfitting | Max Likelihood; Ridge Regression; Lasso | Lab 3 (09-24) | Slides 03a–d + lab 3 + P1 data/helpers pulled 2026-09-24 | ✅ 03a + 03b caught up 2026-09-25; 03c caught up 2026-09-28 (sl. 9 optional, sl. 10 skipped); 03d slides 1–8 caught up 2026-09-28 (no sl. 5; sl. 8 optional); 03d sl. 10–12 (Lasso / L1 sparsity) seen **in broad strokes only** 2026-10-01 (to revisit in detail before the exam); additional notes skipped; lab 3 deferred (priority: lectures + P1) |
| 4 | 09-29 | Generalization; Model Selection; Validation (04a) | Bias–Variance decomposition (04b) | Lab 4 (10-01): 4-fold CV + bias–variance plots | Slides 04a/04b + ex03 solution pulled 2026-10-01; ex04 solution 2026-10-02 | ✅ 04a caught up 2026-10-01 (sl. 1–22; Hoeffding proof sl. 23–27 skipped as bonus); 04b caught up 2026-10-02 (all 34 p.); no annotated 04 (Flammarion does not annotate); lab 4 deferred |
| 5 | 10-06 | Classification (05a) | Logistic Regression (05b) | Lab 5 (10-08): least-squares classification, logistic regression GD/Newton/penalized | Slides 05a/05b pulled 2026-10-08 (no annotated version: Flammarion); ex05 template since 2026-10-02 | ✅ sheet ready 2026-10-08; **05a caught up 2026-10-08/09** (all 33 p.; deep dive on Bayes-classifier proof p. 25 and convex relaxation p. 28); **05b caught up 2026-10-09** (all 26 p.); **week-5 cards done 2026-10-09** (S7: 104 cards + 25 official); lab 5 deferred |
| 6 | 10-13 | Support Vector Machines (06a, Jaggi) | k-NN & curse of dimensionality (06b, Jaggi) | Lab 6 (10-15): SVM via SGD (primal) + coordinate ascent (dual) | Slides 06a/06b + ex06 template + ex05 solution pulled 2026-10-13 | ✅ sheet ready 2026-10-13 (`docs/lectures/06-svm-knn.md`); **06a caught up 2026-10-15 (sl. 1–27; sl. 9 skimmed, sl. 22–23 light)**; **06b caught up 2026-10-20** (proofs p. 37–46 idea only); **week-6 cards done 2026-10-20** (24 own + 34 official); lab 6 ⏳ |
| 7 | 10-20 | *no lecture listed (break)* | *no lecture listed* | *none listed* | — | ⏳ |
| 8 | 10-27 | Kernel ridge regression & kernel trick (07a, Flammarion) | NN: basic structure, representation power (07b, Flammarion) | Lab 7 (10-29): kernels theory, softmax cross-entropy, PyTorch intro (2-D function approx., MNIST) | **Project 1 due 10-29** · slides 07a/07b + ex07 template pulled 2026-10-28 | 🔄 sheet ready 2026-10-28 (`docs/lectures/07-kernels-neural-networks.md`); 07a catch-up starts 2026-10-28; 07b ⏳; week-8 cards ⏳ (after both); lab 7 ⏳ |
| 9 | 11-03 | NN: Backpropagation, activation functions | NN: CNNs, regularization, data augmentation, dropout | Lab 8 (11-05) | **Project 2 starts** (11-03) | ⏳ |
| 10 | 11-10 | NN: Transformers | Adversarial ML | Lab 9 (11-12) | — | ⏳ |
| 11 | 11-17 | Ethics and Fairness in ML | Unsupervised learning; K-Means; GMM | Lab 10 (11-19) | — | ⏳ |
| 12 | 11-24 | GMM; EM algorithm | Matrix Factorizations | Lab 11 + Project Q&A (11-26) | — | ⏳ |
| 13 | 12-01 | Text Representation Learning | LLMs | Lab 12 + Project Q&A (12-03) | — | ⏳ |
| 14 | 12-08 | LLMs; Self-supervised Learning | GANs + Diffusion models | Lab 13 (12-10) | — | ⏳ |
| 15 | 12-15 | Guest lecture — Edouard Grave: "Audio/Speech LM" | Projects pitch session (optional, 12-16) | — | **Project 2 due 12-17** | ⏳ |
| — | Jan 2027 | **Final exam** — date TBD (January session), STCC. Past years: mid-Jan, 15:15–18:15 | | | | ⏳ |

Notes
- Website lists labs on the Wednesday row, but sessions are Thursdays (lab 1 sheet is dated Sept 10). Dates above are Thursdays.
- 2025 edition had the same structure (P1 10 % then; **P1 is not graded in 2026**). 2025 exam: Thu 2026-01-15, 15:15–18:15.
- Lecture PDFs appear in `lectures/NN/` before each lecture (annotated version 1–2 days after); lab solutions a few days after (ex02 solution came 2026-09-21; the 2025 rule of withholding ex02–ex07 until the P1 deadline does not seem to apply in 2026). 2025 P2 description came out 10-09, three weeks before the P1 deadline.
- 2025 lab topics per week (likely identical): see `docs/history-2025.md`.
- Revision-app cards are written **once both lectures of the week are caught up** (not lecture by lecture, never ahead).
- Revision-app cards per lecture: the lectures listed in `revision/content/course.yaml` have their cards (01a–06b as of 2026-10-20).
- From week 8 on, lecture folder numbers lag the week number by one (week 7 = break): week 8 → `lectures/07/`.
