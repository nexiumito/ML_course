# CS-433 Machine Learning — Course overview (Fall 2026)

Sources: `lectures/course_info_sheet.pdf`, course website, `lectures/01/lecture01a_intro.pdf` (logistics slides). Last verified 2026-09-14.

## Basics
- **Instructors:** Nicolas Flammarion, Martin Jaggi (MLO lab, EPFL IC).
- **Credits / language:** 8 ECTS, English. Coursebook: http://edu.epfl.ch/coursebook/en/machine-learning-CS-433
- **Admin email:** epfmlcourse@gmail.com (admin questions only). Content questions → Ed forum.
- **Head TAs:** Simin Fan, Gizem Yuce.
- **PhD TAs:** Alejandro Hernandez Cano, Benedikt Edler von Querfuth, Fares Fawzi, Hantao Zhang, Johan Wenckstern, Kaustubh Ponkshe, Liangze Jiang, Mark Rofin, Mingqiao Ye, Vinko Sabolcec.
- **Student TAs:** Anna Lavrenko, Benedek Balla, Cyrine Akrout, Giacomo Porpiglia, Miquel Lopez, Nahush Kohle, Naser Kazemi, Petar Damjanovic, Rali Lahlou, Semanur Avsar, Strahinja Nikolic, Tommaso Capone, Yinan Hu.

## Schedule (weekly)
| Slot | When | Where |
|---|---|---|
| Lecture | Tuesday 16:15–18:00 | Rolex Learning Center, RLCE1240 |
| Lecture | Wednesday 10:15–12:00 | Rolex Learning Center, RLCE1240 |
| Exercise session (lab) | Thursday 14:15–16:00 | By last name: INF1 (A–Da), INF119 (De–Fr), INJ218 (Fr–Lin), INM202 (Lind–Rr), INR219 (Ru–Z). Website also lists CO123. |

Semester: 2026-09-08 → 2026-12-17. Full week-by-week plan: `docs/schedule.md`.

## Grading
| Component | Weight | Deadline |
|---|---|---|
| Project 1 | not graded (preparation for P2) | **2026-10-29** (website + slides). ⚠ Info sheet's Project 1 section says "Nov 1st" — inconsistent; treat 10-29 as the deadline until clarified. |
| Project 2 | **30 %** | **2026-12-17** |
| Final exam | **70 %** | TBD, January 2027 exam session, SwissTech Convention Center (STCC). Past years: mid-January, 15:15–18:15, 180 min. |

Exam rules: closed book, **one A4 cheat sheet, both sides** allowed. No calculator, phone, laptop. Bring pen + white eraser. A sample exam is provided beforehand. See `docs/exams.md`.

## Projects (summary; details in `docs/projects.md`)
- Both in **groups of 3** (2 only exceptionally, with approval). Python code + PDF report.
- **P1:** implement the main methods from lectures/labs so far; AICrowd competition on a real dataset (https://www.aicrowd.com/challenges/epfl-machine-learning-project-1). 2-page report. Starts 2026-09-16/17.
- **P2 (ML4Science):** real-world challenge with any EPFL research group or Swiss academic institution (https://www.epfl.ch/labs/mlo/ml4science/). Ideas must be approved by the host lab and the course team **early November**. 4-page report. Starts 2026-11-03/04. Project Q&A during labs on 11-26 and 12-03. Optional pitch session 2026-12-16.

## Course goals (from info sheet)
Define and distinguish regression / classification / clustering / dimensionality reduction; implement and apply ML methods; evaluate rigorously with cross-validation; manage overfitting and cost/accuracy trade-offs; understand the fundamental theory. Warning from lab 1 sheet: **the final exam is heavily theoretical** despite the practical projects — do the theory exercises in the lab sheets.

## Syllabus (high level)
1. Regression & classification basics: linear models, overfitting, linear/ridge/logistic regression, SVM, k-NN.
2. Fundamentals: cost functions & optimization, cross-validation, bias–variance, curse of dimensionality, kernels.
3. Neural networks: basics, representation power, backprop, CNNs, transformers, regularization, data augmentation, dropout, adversarial examples/robustness.
4. Unsupervised / self-supervised: k-means, GMM, EM, generative models, LLMs, diffusion, GANs.
5. Representation learning: PCA, matrix factorization, word embeddings, recommender systems.

## Prerequisites to refresh
- Linear algebra: matrix products, inverse, rank, eigen-decomposition (Strang; linear algebra handout on the site).
- Matrix calculus: derivatives w.r.t. vectors/matrices (explained.ai/matrix-calculus, Matrix Cookbook).
- Probability: conditional/joint distributions, independence, Bayes, expectation, LLN, Gaussians (uni/multivariate, conditionals, marginals). Bishop ch. 2.
- Python basics (lab 1 tutorial). LaTeX preferred for reports.

## Textbooks (none mandatory)
Strang *Linear Algebra and Learning from Data*; Shalev-Shwartz & Ben-David *Understanding ML*; James et al. *ISLR*; Hastie et al. *ESL*; Bishop *PRML*; Murphy *ML: A Probabilistic Perspective*; Nielsen *Neural Networks and Deep Learning*.

## Links
- Course site: https://www.epfl.ch/labs/mlo/machine-learning-cs-433/
- GitHub (materials, solutions): https://github.com/epfml/ML_course
- Ed forum: https://edstem.org/eu/courses/3637/discussion
- Lecture videos: https://mediaspace.epfl.ch/channel/CS-433+Machine+learning/55647
- ML4Science: https://www.epfl.ch/labs/mlo/ml4science/
- Previous year's site (2025, Prof. Robert West; useful for structure): https://epfml.github.io/cs433-2025/
- Noto (EPFL Jupyter): https://noto.epfl.ch/hub/user-redirect/git-pull?repo=https://github.com/epfml/ML_course&urlpath=lab/tree/ML_course/labs/ex01/npprimer.ipynb
- Colab pattern: `http://colab.research.google.com/github/epfml/ML_course/blob/main/labs/exXY/<notebook>.ipynb`
- Research talks mailing list: ml@groupes.epfl.ch
