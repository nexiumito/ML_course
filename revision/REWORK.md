# Card rework — exam-format cards (mission file)

Self-contained mission for an **autonomous** Claude Code session (cloud). Written 2026-10-11 after a discussion with the
student. He is away while you work: **make every decision yourself** following this file; do not stop to ask. When this
file and older parts of `SPEC.md` disagree, **this file wins** (SPEC §8 was already rewritten to match it).

Read first: `CLAUDE.md` (repo conventions), `revision/SPEC.md` §0, §4.2, §8 (card schema and writing rules — §8.2 is the
new rule set), `revision/README.md` (commands), `docs/exams.md` (exam format + recurring topics).

---

## 1. Why (the student's feedback, 2026-10-11)

After 5 course weeks the app holds **412 cards / 586 review items** (cloze cards create one item per blank). The student
finds it demotivating and stopped wanting to review. Two problems, both confirmed by the numbers:

1. **Too many cards.** ~120 new items per week ⇒ ~1500 items by the end of the semester; with spaced repetition every
   card costs reviews for weeks, so the daily pile becomes crushing. Week 5 alone got 66 concept cards (05a + 05b): the
   author aimed at covering everything instead of selecting.
2. **Cloze cards are badly suited.** 138 cloze cards, 312 blanks, **101 blanks are phrases of ≥ 4 words**: the student
   has to guess the author's wording, not recall a concept, so he never knows whether he "got it" and self-grading is
   painful. Examples:
   - `03b-more-data`: "Keeping M fixed and [increasing the number of data points N] [reduces overfitting]".
   - `05b-odds` c3: the blank is a whole sentence ("the log-odds as a linear function: …").
   - `05a-bonus-regressor` c2: the blank is the author's paraphrase of a theorem's conclusion.
   - `04a-m-fold-cv`: 4 blanks for a procedure understood in one sentence.
   - Counter-example that works: `02a-subdifferential-abs` (∂|e| = {−1}, [−1, 1], {+1}) — each blank has one exact answer.

**The goal changes.** The cards are not there to make him know the course from A to Z. They are there to **pass the
exam**, in a format that trains for the exam:
- The final (Jan 2027, `docs/exams.md`) is **multiple choice (2 pts) + true/false (1.5 pts)** + open questions. There is
  **no fill-in-the-blank**: the answer is almost always in front of you.
- **One double-sided A4 cheat sheet is allowed** ⇒ memorizing formulas by heart is nearly useless; they go on the sheet.
- What earns points: **recognizing the true statement** among 4–5, **spotting the trap** in a statement, and doing a
  **quick mini-computation** to pick an option (MSE gradient, logistic MLE on 2 points, CV training count, …).
- Open questions (derivations, EM by hand, …) are **out of scope** here (separate topic, later).

Desirable difficulty is fine (retrieval effort is what makes spaced repetition work); **ambiguity is not**.

## 2. Rules of the rework

1. **No cloze cards anymore.** Do not write any. Every existing cloze card is converted (to tf/mcq) or deleted. The app
   code keeps supporting `cloze` — do **not** touch backend/frontend unless strictly necessary.
2. **Almost everything is `tf` or `mcq` (auto-graded).**
   - Distractors reproduce **real traps** from past exams and from the lecture sheets' "pitfalls" sections
     (sign errors, wrong direction of λ, forgotten conditions, training vs test error, 1/N vs 1/(2N), bias/variance swap…).
   - `explanation` says why the right answer is right **and why each wrong option is wrong** (so a mistake teaches).
   - `trap`: one line when there is a classic trap.
   - `tf`: one crisp claim, exam-style; avoid trivially true statements; aim for a balanced mix of true and false.
   - `mcq`: 4 options (3–5 fine), one correct unless deliberately `multi: true` (then all-or-nothing, like the exam's
     "select all that apply"). If an option is "All of the above"-like, set `shuffle: false`.
     When `shuffle` is on, explanations must not cite option letters.
   - Mini-computations are **mcq with numeric options** (wrong options = results of the typical mistakes).
   - `basic` only exceptionally: a mini-computation whose answer is short and unique and cannot be turned into options
     sensibly. No "derive …" cards, no "list …" cards.
3. **Select by exam relevance**, using `revision/content/exam-index.yaml` (431 classified past questions: topics, areas,
   lectures) and `docs/exams.md` § Recurring topics. Keep a concept only if it has appeared in past exams, is a classic
   trap, or is a prerequisite that exam questions test directly. A concept never asked and with no classic trap is
   **deleted, even if it is on the slides**. Course-organisation and pure-history content: never.
4. **Cap: at most 20 cards per lecture**, counting `concept` + `exam_style` (= one app session; `new_per_day` is 20).
   Fewer is fine for light lectures (01a, 03b: ~5–10). `exam_official` cards **do not count** toward the cap.
5. **Official questions (`content/exams/*.yaml`, 108 cards) stay** as they are — fix only a proven error (then follow
   SPEC §8.3: answer read from the ticked box / solution text). Do not write your own card that duplicates an official
   question of the same lecture (same claim / same computation): the official one already covers it.
6. **Origin and ids.** Every non-official card you write in tf/mcq format gets `origin: exam_style` and id
   `style-<lecture>-<slug>` (so Exam mode covers all of them and they show the "Unofficial" badge). `origin: concept` is
   kept only for the rare `basic` cards. Keep an existing id when the card keeps its meaning (an existing `style-…` card
   kept as is or with a typo fix); a converted card gets a new id. The old ids simply disappear from the YAML.
7. **Losing FSRS progress is accepted** by the student. Removed cards become orphan items in the DB (kept, ignored by the
   queue — `db.sync_items`); nothing to migrate. Do not try to remap progress.
8. **Existing `exam_style` cards (66)** are re-read like the others: keep, improve, merge or delete; they count in the cap.
9. **Student-specific points** (SPEC §8.4: confusions he had while catching up) are high-value: each one that is
   exam-relevant should survive as a tf/mcq (e.g. λ direction, Hoeffding only on held-out data, 0.5 threshold = midpoint
   of codes, k vs distance in k-NN, separable data ⇒ ‖w‖ → ∞, Newton vs GD cost). Derivation-only points (Bayes classifier
   proof steps, Hessian derivation) become at most one mcq on the *result* or the key step, or are dropped.
10. **Keep every still-valid rule of SPEC §8.2**: content from the PDF pages (source of truth; lecture sheets are only an
    index), `sources` with **verified PDF page** and correct label (slide numbering per deck: SPEC §0.1 / §8.7), course
    notation (`docs/glossary.md`, 1/(2N) MSE in lab context), English only, context cue `*(Ridge)*` at the start of the
    front, never invent facts (uncertain ⇒ no card), math layout rule 10b (display math for long formulas, no whole-formula
    `\left…\right`, `\tfrac` in exponents, no raw HTML, trailing `\` only outside lists), check at 375 px.
11. `priority`: `core` for nearly everything you keep; `detail` should become rare (bonus slides like 04a Hoeffding proof,
    05a p. 30–32 at most one card each, or none).

## 3. Execution plan

Work in the session's branch. Commit after each step that passes the checks (title-only messages, see §5).

**Step 0 — setup.** `cd revision && uv sync && uv run revision content check && uv run pytest -q`;
`cd frontend && npm install && npm run check-math`. Record the "before" numbers per lecture (cards by origin/type, items)
with a small script (read the YAML, a cloze card counts one item per distinct `cN`). Starting point (2026-10-11):

| Lecture | concept (cloze/basic) | exam_style | official | items |
|---|---|---|---|---|
| 01a | 6 / 2 | 0 | 7 | 19 |
| 01b | 5 / 3 | 3 | 4 | 19 |
| 01c | 8 / 8 | 4 | 8 | 35 |
| 02a | 25 / 14 | 7 | 23 | 92 |
| 03a | 10 / 6 | 5 | 8 | 43 |
| 03b | 7 / 1 | 3 | 2 | 24 |
| 03c | 9 / 2 | 4 | 3 | 33 |
| 03d | 15 / 7 | 7 | 11 | 63 |
| 04a | 13 / 10 | 8 | 8 | 53 |
| 04b | 11 / 10 | 7 | 9 | 53 |
| 05a | 12 / 17 | 9 | 10 | 71 |
| 05b | 17 / 20 | 9 | 15 | 81 |
| **total** | **138 / 100** | **66** | **108** | **586** |

**Step 1 — pilot on 05a and 05b.** For each lecture:
1. Read `docs/lectures/05-classification-logistic-regression.md`, SPEC §8.4 "Week 5", the existing
   `content/cards/05x.yaml` and `content/exams/05x.yaml`, and the exam-index entries whose `areas`/`lectures` match.
2. Build a short list of exam-relevant points (what past exams ask + classic traps + §8.4 confusions), minus what official
   cards already cover. Pick ≤ 20.
3. Rewrite `content/cards/05x.yaml` entirely (re-using good existing tf/mcq). Verify every formula / claim on the PDF
   pages (`pdftotext -f P -l P -layout`; formulas are often images → render the page, see §4).
4. `uv run revision content check`, `npm run check-math`, layout check (§4).
5. **Self-review, critically, as the student would**: for each card ask "would this exact kind of question help me at
   the exam? Is there exactly one defensible answer? Is the trap realistic? Is it readable on a phone?" Fix, then judge
   the pilot as a whole (count, balance tf/mcq, difficulty, overlap with officials). Adjust the approach if needed and
   write the lessons in §6 of this file (they apply to the next lectures).

**Step 2 — lectures 01a → 04b**, in course order, same procedure (sheets: `docs/lectures/01-…` to `04-…`; SPEC §8.4 for
weeks 1–4 confusions). 02a is the densest: still ≤ 20 — pick by exam frequency.

**Step 3 — global pass.** No duplicates across lectures; themes still valid (`course.yaml` vocabulary); `course.yaml`
untouched except if a theme becomes unused (keep it, harmless); `exam-index.yaml` unchanged (officials untouched — run
`uv run revision content mark-added` anyway, it must report no change).

**Step 4 — tests & docs.**
- `uv run pytest`, `uv run ruff check backend`, `cd frontend && npm run typecheck && npm run lint && npm test`. Tests that
  read the real content (if any) may need updated counts — fix tests only for that reason.
- `SPEC.md`: tick the "Rework" milestone in §12 and add a §13 session-log entry with the **before/after table**
  (cards by origin/type and items per lecture) and the main decisions.
- `docs/exams.md`: nothing expected; `docs/schedule.md`: nothing expected.
- Update §6 below (lessons) and set the status line at the top of §7.

## 4. Done when

- [ ] No `type: cloze` left in `content/cards/`; ≤ 20 `concept` + `exam_style` cards per lecture; officials unchanged
      (except proven errors, listed in the log).
- [ ] `uv run revision content check` OK; `cd frontend && npm run check-math` 0 errors.
- [ ] `uv run pytest` green, ruff clean, frontend typecheck/lint/vitest green.
- [ ] Visual check at 375 px: run `.claude/launch.json` → `revision-api-test` (data in `revision/data/test/`, delete it
      afterwards) + build or dev UI, open `/sheet?lecture=<id>&check=1` (mobile preset) for **every** lecture, fix every
      overflow/KaTeX error it lists, and scroll through a sample of cards. **If no browser is available in the cloud
      session**, say so in the log (the student's local session will do it); the automatic checks above remain mandatory.
- [ ] Before/after table in the SPEC §13 log; commits pushed to the session branch.

Rendering helpers (from earlier sessions, easy to recreate): render a slide `pdftoppm -f P -l P -r 70 -png file.pdf out`
(or with **pypdfium2**, already a dependency: `pdfium.PdfDocument(path)[P-1].render(scale=1).to_pil()`), tile several
pages into one PNG with PIL to save tokens. If `pdftotext`/`pdftoppm` (poppler) are missing in the cloud environment,
install poppler-utils if possible, otherwise use pypdfium2 (`page.get_textpage().get_text_range()`).

## 5. Constraints of the cloud session

- **No access to the VPS** (`ml-vps` is tailnet-only): no deployment, and the open card reports (stored in the VPS DB)
  cannot be read — they will be processed when the student is back. Do not try to reach it.
- Gitignored files are absent: `revision/data/`, `revision/deploy/VPS.md`. Use `revision-api-test` / a temp data dir.
- Commits: **title line only** — no body, no `Co-Authored-By`, no attribution line. Work on the session's branch.
- Never modify official course files (PDFs, notebooks, `labs/*/solution/`, `exam/`).
- Cards and docs in English. If you leave a note for the student, write it in the SPEC §13 log (English) — he reads it
  with a local Claude session.

## 6. Lessons from the pilot (fill in during step 1)

- TODO — not yet written (as of 2026-10-11).

## 7. Status and hand-off

Status: **not started** (2026-10-11).

When the session is done, the student (with a local Claude session on his Mac):
1. reviews and merges the session branch into `main`, `git pull`, `git push origin main`;
2. processes the open card reports on the VPS (`revision/README.md` § Production) — cards they refer to may no longer
   exist (resolve them with a note);
3. deploys: `ssh elie@ml-vps '~/ML_course/revision/deploy/update.sh'`;
4. does the 375 px visual check if the cloud session could not.
