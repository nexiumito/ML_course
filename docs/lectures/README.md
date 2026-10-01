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
| 04a | 2026-09-29 | [04-generalization-bias-variance.md](04-generalization-bias-variance.md) §A | `lectures/04/lecture04a.pdf` | 27 | ✅ sheet written 2026-10-01; annotated: TODO — not yet published (as of 2026-10-01) |
| 04b | 2026-09-30 | [04-generalization-bias-variance.md](04-generalization-bias-variance.md) §B | `lectures/04/lecture04b.pdf` | 34 | ✅ sheet written 2026-10-01; annotated: TODO — not yet published (as of 2026-10-01) |

Slide numbering: lectures 01–03 (Jaggi) print "slide N" = PDF page N+1; **lecture 04 (Flammarion) slide N = PDF page N** (title = p. 1; 04b has almost no printed numbers).

Annotated PDFs (`*_annotated.pdf`) arrive upstream ~1 day after the lecture; the handwriting is image-only → `pdftoppm -r 45 -png in.pdf out` then view the PNGs (tile them 2×4 to save tokens). Integrate the annotations into the sheet and mark it here.

Sheet format (keep consistent): **Scope → Key concepts → Notation → Formulas → Exam-relevant points / pitfalls → Not exam material → Exercises mentioned**.
