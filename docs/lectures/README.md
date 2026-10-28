# Lecture summary sheets

One dense sheet per lecture PDF. Read the sheet first; open the PDF only if the sheet is insufficient (then improve the sheet).
Formulas in the PDFs are embedded images: the formulas below were reconstructed from slide text, the labs, and past exams using the course's conventions (see `docs/glossary.md`).

| # | Date | Sheet | Source PDF | Pages | Status |
|---|---|---|---|---|---|
| 01a | 2026-09-08 | [01-intro-regression-loss.md](01-intro-regression-loss.md) §A | `lectures/01/lecture01a_intro.pdf` | 53 | ✅ |
| 01b | 2026-09-08 | [01-intro-regression-loss.md](01-intro-regression-loss.md) §B | `lectures/01/lecture01b_regression.pdf` (+ `_annotated`) | 20 | ✅ (annotations not yet reviewed) |
| 01c | 2026-09-09 | [01-intro-regression-loss.md](01-intro-regression-loss.md) §C | `lectures/01/lecture01c_loss_functions.pdf` (+ `_annotated`) | 16 | ✅ annotations integrated |
| 02a | 2026-09-15/16 | [02-optimization.md](02-optimization.md) | `lectures/02/lecture02a_optimization.pdf` (+ `_annotated`) | 56 | ✅ annotations integrated |
| 03a | 2026-09-22 | [03-least-squares-regularization.md](03-least-squares-regularization.md) §A | `lectures/03/lecture03a_least_squares.pdf` (+ `_annotated`) | 15 | ✅ annotations integrated (2026-09-25); **student caught up 2026-09-25** |
| 03b | 2026-09-22 | [03-least-squares-regularization.md](03-least-squares-regularization.md) §B | `lectures/03/lecture03b_overfitting.pdf` (+ `_annotated`) | 10 | ✅ annotations integrated (2026-09-25); **student caught up 2026-09-25** |
| 03c | 2026-09-23 | [03-least-squares-regularization.md](03-least-squares-regularization.md) §C | `lectures/03/lecture03c_maximum_likelihood.pdf` (+ `_annotated`) | 11 | ✅ annotations integrated (2026-09-25); student at slide 6/10 (2026-09-26) |
| 03d | 2026-09-23 | [03-least-squares-regularization.md](03-least-squares-regularization.md) §D | `lectures/03/lecture03d_ridge.pdf` (+ `_annotated`) | 19 | ✅ annotations integrated (2026-09-25) |
| 04a | 2026-09-29 | [04-generalization-bias-variance.md](04-generalization-bias-variance.md) §A | `lectures/04/lecture04a.pdf` | 27 | ✅ sheet written 2026-10-01; no annotated version (Flammarion) |
| 04b | 2026-09-30 | [04-generalization-bias-variance.md](04-generalization-bias-variance.md) §B | `lectures/04/lecture04b.pdf` | 34 | ✅ sheet written 2026-10-01; no annotated version (Flammarion) |
| 05a | 2026-10-06 | [05-classification-logistic-regression.md](05-classification-logistic-regression.md) §A | `lectures/05/lecture05a.pdf` | 33 | ✅ sheet written 2026-10-08; **student caught up 2026-10-09**; **no annotated version** (Flammarion); 2025 annotated proxy in history |
| 05b | 2026-10-07 | [05-classification-logistic-regression.md](05-classification-logistic-regression.md) §B | `lectures/05/lecture05b.pdf` | 26 | ✅ sheet written 2026-10-08; **student caught up 2026-10-09**; **no annotated version** (Flammarion); 2025 annotated proxy in history |
| 06a | 2026-10-13 | [06-svm-knn.md](06-svm-knn.md) §A | `lectures/06/lecture06a.pdf` | 28 | ✅ sheet written 2026-10-13; **student caught up 2026-10-15**; no annotated 06 published (as of 2026-10-20); 2025 annotated proxy (same deck) integrated |
| 06b | 2026-10-14 | [06-svm-knn.md](06-svm-knn.md) §B | `lectures/06/lecture06b.pdf` | 48 | ✅ sheet written 2026-10-13; **student caught up 2026-10-20**; 2025 annotated proxy integrated |
| 07a | 2026-10-27 | [07-kernels-neural-networks.md](07-kernels-neural-networks.md) §A | `lectures/07/lecture07a.pdf` | 23 | ✅ sheet written 2026-10-28 (Flammarion, no annotated version); 2025 annotated proxy integrated (page map in the sheet) |
| 07b | 2026-10-28 | [07-kernels-neural-networks.md](07-kernels-neural-networks.md) §B | `lectures/07/lecture07b.pdf` | 46 | ✅ sheet written 2026-10-28; 2025 annotated proxy integrated |

Slide numbering: lectures 01–03 (Jaggi) print "slide N" = PDF page N+1; **lectures 04+ slide N = PDF page N** (title = p. 1; 04b, 05a/b, 06a/b, 07a/b have no printed numbers).

The break week (2026-10-20) is not counted in the semester weeks: `lectures/NN/` = week NN (week 7 = 2026-10-27).

**Flammarion does not publish annotated slides** (04, 05): don't wait for them. Lecture 06 is taught by **Jaggi** (Flammarion's slides) → annotated PDFs may come. For 05 and 06, the 2025 annotated decks (same slides) are in git history — see the sheets.

Annotated PDFs (`*_annotated.pdf`) arrive upstream ~1 day after the lecture; the handwriting is image-only → `pdftoppm -r 45 -png in.pdf out` then view the PNGs (tile them 2×4 to save tokens). Integrate the annotations into the sheet and mark it here.

Sheet format (keep consistent): **Scope → Key concepts → Notation → Formulas → Exam-relevant points / pitfalls → Not exam material → Exercises mentioned**.
