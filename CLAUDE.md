# CS-433 Machine Learning (EPFL, Fall 2026) — personal course repo

Fork of the official course repo `epfml/ML_course` (remote `upstream`; `origin` = personal fork).
Contains lecture PDFs, weekly labs (templates + solutions), projects (later), past exams.
Owner: Elie Bsd, M1 student. Agents help with labs, theory, revision, and projects.

## Read this first
- `docs/course-overview.md` — grading, deadlines, rooms, staff, links.
- `docs/schedule.md` — week-by-week table with status. **Check here to know where we are in the semester.**
- `docs/lectures/README.md` — index of lecture summary sheets (one per lecture PDF).
- `docs/labs.md` — lab structure, how to run/test, per-lab status.
- `docs/projects.md` — Project 1 / Project 2 info (mostly TODO until published).
- `docs/exams.md` — exam inventory, format, recurring topics, revision advice.
- `docs/glossary.md` — course notation (N, D, X, w, L(w), …) and acronyms.
- `docs/history-2025.md` — **the whole 2025 edition is in git history** (`git show '48f3822^:<path>'`): look ahead at labs, lectures, solutions, project descriptions.

## Repository layout
```
lectures/NN/lectureNNx_topic.pdf    official slides (formulas are images; use docs/lectures/*.md)
lectures/course_info_sheet.pdf      org info — already summarized in docs/course-overview.md
labs/exNN/exerciseNN.pdf            lab sheet (practical tasks + theory questions)
labs/exNN/template/                 notebooks with `raise NotImplementedError` stubs → student fills these
labs/exNN/solution/                 official solutions (published ~1 week later, pulled from upstream)
labs/exNN/template/test_utils.py    doctest runner: `test(fn)` checks the docstring examples
exam/final-exam-YYYY[-solutions].pdf   finals 2016–2025 (all have solutions)
exam/mock-midterm-exam/             mock midterms 2014, 2015, 2017, 2018 (with solutions)
projects/                           (not yet present; will hold project1/, project2/)
docs/                               agent-facing documentation (this system)
```

## Conventions
- Python 3, NumPy-first. Labs forbid explicit for-loops where vectorization is possible.
- Data matrix `X` is `(N, D)`: rows = samples, columns = features. Weights `w` are `(D,)`.
- Labs/Project 1 MSE uses the `1/(2N)` factor: `L(w) = 1/(2N) Σ (y_n − xₙᵀw)²`. Keep it in lab code. (Loss-functions lecture slides write 1/N; same minimizer.)
- Notebook first cell: `%matplotlib inline`, `%load_ext autoreload`, `%autoreload 2`, `from test_utils import test`.
- Lab functions carry doctests in their docstring; run `test(fn)` after implementing.
- Student work goes in `labs/exNN/template/` (edit the stubs in place). Never modify `solution/`.
- Course language: English. Docs in English. User speaks French; reply in the user's language.
- Do not modify official course files (PDFs, official notebooks, solutions). Sync with `git pull upstream main`.
- Upstream is reset every September; previous editions stay in history (see `docs/history-2025.md`). Lab solutions for the labs that implement Project 1 functions (ex02–ex07) are withheld until after the P1 deadline.

## Documentation maintenance (mandatory for every agent)
- `docs/lectures/*.md` are an **index**, not a substitute: for any question on course content, locate the section with the sheet, then read those pages of the PDF itself (`pdftotext -f N -l M -layout`). Formulas in the sheets are reconstructed from image-based slides; the PDF is the source of truth. For other docs (`schedule`, `labs`, `projects`, `exams`), read the doc first and open the PDF only if it is insufficient — then update the doc.
- New `lectures/NN/` folder → create `docs/lectures/NN-<topic>.md` (use the existing sheets as the format), add a row to `docs/lectures/README.md`, mark the week in `docs/schedule.md`, add new notation to `docs/glossary.md`.
- New or completed `labs/exNN/` → update the lab's row/section in `docs/labs.md` (status, gotchas, what was hard) and `docs/schedule.md`.
- Project starts → fill `docs/projects.md` from the official description PDF and create `projects/projectN/CLAUDE.md` (team, deadlines, structure, how to run).
- Always keep the ✅/⏳ status column in `docs/schedule.md` current.
- Keep this file under 80 lines. Details go in `docs/`, not here.
- Write dates as absolute (e.g. `2026-10-29`), never "next week".
- When a fact is unknown, write `TODO — not yet published (as of YYYY-MM-DD)`; never invent.
- Extract PDF text with `pdftotext -layout file.pdf out.txt` (installed). Formulas are images: reconstruct them from context and mark them as reconstructed if unsure. Handwritten annotations (`*_annotated.pdf`): `pdftoppm -r 45 -png` + view PNGs (tile pages with PIL to save tokens).

## Working with the student
- He does **not attend lectures**: he catches up each lecture at home from the slide PDF + mediaspace video (the prof annotates slides live). Basic slides go fast; on technical slides he stops and asks questions. Help him understand deeply and tell him what is essential / exam-relevant to note.
- Annotated slides (`lectureNNx_*_annotated.pdf`) arrive upstream 1–2 days after each lecture: suggest `git pull upstream main` and use them.
- Weekly goal: the two lectures of the week + the Thursday lab. Status of what he has actually caught up: `docs/schedule.md` and `docs/labs.md` — update after each session.
- Project team (P1 & P2): Elie, Gabin, Antoine.

## Key links
- Course site: https://www.epfl.ch/labs/mlo/machine-learning-cs-433/
- Upstream repo: https://github.com/epfml/ML_course
- Ed forum: https://edstem.org/eu/courses/3637/discussion
- Videos: https://mediaspace.epfl.ch/channel/CS-433+Machine+learning/55647
- Previous year site (2025): https://epfml.github.io/cs433-2025/
