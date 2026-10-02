# CS-433 Revision App — Specification

Self-contained spec for building and feeding a personal spaced-repetition web app (Anki-like, but tailored to EPFL CS-433 Machine Learning, Fall 2026). A fresh Claude Code session must be able to build everything from this file + the repo's self-doc. Written 2026-10-02 (course week 4).

**How to use this file:** read §0–§2 once, then go to §12 (milestones) and resume at the first unchecked item. At the end of every session: tick the checklist in §12, write a one-line entry in §13 (session log), commit.

---

## 0. Context

### 0.1 The course and the repo
- Repo = personal fork of the official course repo (lecture PDFs, labs, past exams) + an agent-maintained self-doc in `docs/`. **Read `CLAUDE.md` first** (repo layout, conventions, doc-maintenance rules, how to work with the student).
- Docs to know (point to them, never copy them):
  - `docs/schedule.md` — week-by-week table + the student's personal progress (✅/🔄/⏳). **Source of truth for which lectures are caught up.**
  - `docs/lectures/README.md` + `docs/lectures/NN-*.md` — one summary sheet per lecture: key concepts, formulas, **exam-relevant points / pitfalls with past-exam question references**. Main input for writing cards.
  - `docs/exams.md` — inventory of past exams (finals 2016–2025 with solutions, mock midterms 2014/15/17/18), exam format (MC 2 pts, T/F 1.5 pts, open questions), recurring topics.
  - `docs/glossary.md` — notation (N, D, X, w, L(w), L_𝒟, L_S, …). Cards must follow it.
- Lecture PDFs: `lectures/NN/*.pdf` (+ `*_annotated.pdf` with the professor's handwriting, a few days later). Exams: `exam/final-exam-YYYY[-solutions].pdf`, `exam/mock-midterm-exam/`.
- **Slide numbering differs per deck** (see `CLAUDE.md` and `docs/lectures/README.md`): lectures 01–03 print "slide N" ≈ PDF page N+1 (with exceptions, e.g. 03d has no slide 5 so later slides line up with PDF pages); lecture 04+ (Flammarion) slide N = PDF page N. **Cards therefore store the PDF page explicitly** (never compute it from a slide number) plus a human label.
- Never modify official files (PDFs, official notebooks, `labs/*/solution/`). The app only *reads* them.

### 0.2 The student (the only user)
- Elie, EPFL M1. Does not attend lectures; catches up each lecture at home with Claude (slides + video), asking questions on technical slides. Speaks French; **talk to him in French**. Course, exam and **all card content are in English**.
- Final exam: January 2027 (date TBD), closed book, 180 min, MC + T/F + open questions, in English. See `docs/exams.md`.
- Git commits: **title line only**, no body, no Co-Authored-By/attribution.

### 0.3 What he wants (requirements, from the 2026-10-02 discussion)
1. A **custom spaced-repetition app** built from scratch (not Anki), optimized for this course, to memorize the course continuously and do most of the revision work ahead of the exam period.
2. **Two families of cards:**
   - *Concept cards* covering every aspect of the course (definitions, formulas, intuitions, derivations, comparisons, pitfalls).
   - *Exam cards*: True/False and multiple-choice questions, **auto-graded**:
     - **official** questions transcribed from past exams (finals 2016–2025, mock midterms), including questions with figures (image extracted from the PDF);
     - **unofficial exam-style** questions written by Claude, **clearly labeled as unofficial** everywhere they appear.
   - Open (free-text) exam questions are **out of scope for now**.
3. **Every card links to its source**: the lecture PDF opened at the right slide, or exam year + question number (with the exam page viewable).
4. A **"flag this card" button** that records a report (wrong / unclear / typo / …); the next Claude session processes open reports.
5. **Review modes:** global (all active cards), by **week**, by **lecture** (01a, 03d, …), by **theme** (cross-cutting tag), **exam mode** (exam cards only), **weak points**.
6. **Progressive content:** cards are created only once the lecture has been caught up — never written in advance. Content creation is part of the usual repo pipeline (new slides → doc update → lecture caught up → cards). At launch, the app contains everything up to **week 4 (lectures 01a → 04b)**.
7. **Works great on desktop and phone** (responsive, keyboard shortcuts on desktop, touch-first on phone, installable to the home screen).
8. **Hosting:** develop and run locally on his Mac first; then deploy on a **VPS (Ubuntu LTS, provider not chosen yet — probably OVH)**, reachable **only from his own devices through Tailscale** (phone + Mac), running even when the Mac is off. The VPS may later host other projects. Single source of truth for progress = the server.
9. Quality bar: "for me, but complete and well made". Correctness of card content matters more than anything (a wrong card = memorizing something false).

---

## 1. Architecture overview

```
 Phone / Mac browser ──HTTPS (tailnet only, *.ts.net cert)──► tailscale serve ──► 127.0.0.1:8433
                                                                                     │
                                                         FastAPI app (uvicorn) ──────┤
                                                           ├─ serves built SPA (frontend/dist)
                                                           ├─ JSON API (/api/*)
                                                           ├─ renders PDF pages → PNG (source viewer)
                                                           ├─ loads card content (YAML in git) at startup
                                                           └─ SQLite (progress, review log, reports)
```

- **Content** (cards, images, course registry) lives in git under `revision/content/` → authored by Claude, reviewed by diff, deployed with `git pull`.
- **State** (FSRS memory state per item, full review log, reports, settings) lives in **SQLite** outside git (`REVISION_DATA_DIR`), backed up automatically.
- Single user, no login: security comes from **network isolation** (bind to localhost; exposed only via `tailscale serve`, never `tailscale funnel`).

---

## 2. Technical decisions (with rationale)

| Concern | Choice | Why |
|---|---|---|
| Backend language | **Python ≥ 3.12**, managed with **uv** (installed on the Mac: uv 0.12, Python 3.14) | Repo is Python; official FSRS implementation is Python; easy to test; one tool for env + run. |
| Web framework | **FastAPI** + **uvicorn** | Typed, small, auto OpenAPI docs, serves static files too. |
| Scheduler | **`fsrs`** (py-fsrs, PyPI, v6.x at time of writing, MIT) — `Scheduler`, `Card`, `Rating`, `ReviewLog`, `to_json/from_json`, `get_card_retrievability`, optional `Optimizer` via `fsrs[optimizer]` | FSRS is the state-of-the-art algorithm (Anki's default since 23.10), better than SM-2. Do not reimplement. **Verify the installed version's API before coding** (README: https://github.com/open-spaced-repetition/py-fsrs). UTC datetimes only. |
| Database | **SQLite** via stdlib `sqlite3` (WAL mode, foreign keys on), tiny hand-written migration table | One file, zero admin, trivial backups; ORM is overkill for ~6 tables. |
| Content format | **YAML** files (one per lecture, cards as list), markdown + LaTeX inside block scalars (`|`), validated with **pydantic v2** | Human-diffable, comments allowed, easy for Claude to author; strict validation catches mistakes. |
| PDF page rendering | **`pypdfium2`** (pip wheel, BSD/Apache) → PNG cached on disk | Works on iOS (Safari ignores `#page=N` in PDFs), no system dependency. |
| CLI | **typer** (`uv run revision …`) | Content check, serve, backup, reports, export. |
| Extra deps (S1) | **Pillow** (pypdfium2 `to_pil()` → PNG), **tzdata** (zoneinfo on any host) | |
| Frontend | **React + TypeScript + Vite**, **Tailwind CSS**, **react-markdown + remark-math + rehype-katex** (KaTeX), **vite-plugin-pwa** | Mainstream, well-known stack; KaTeX renders course formulas properly; PWA = home-screen install. Node is installed on the Mac (v25, npm 11). |
| Charts | Small hand-written SVG components (heatmap, bars, line) — no heavy chart lib | Few charts, keeps bundle small. |
| Tests | **pytest** (backend: content loader/validator, scheduler wrapper, queue building, grading, API), **vitest** for non-trivial frontend logic; `ruff` + `tsc --noEmit` | |
| Process manager (VPS) | **systemd** service + systemd timers (backup, optional auto-update) | Native on Ubuntu, no Docker needed (Docker is not installed on the Mac anyway). |

Ports: backend `8433`; Vite dev server `5173` proxying `/api` and `/files` to `8433`.

---

## 3. Folder structure

```
revision/
  SPEC.md                    # this file
  README.md                  # short: how to run, how to add content (create in M0)
  pyproject.toml             # uv project, package "revision" (src layout below), entry point `revision`
  uv.lock
  backend/
    revision/
      __init__.py
      config.py              # paths/env (REPO_ROOT auto-detected = parent of revision/, REVISION_DATA_DIR, timezone, port)
      content.py             # pydantic models + YAML loader + validator
      db.py                  # connection, migrations, queries
      scheduler.py           # FSRS wrapper (rating → new state, interval previews, retrievability)
      queue.py               # session/queue building for each mode + filters + daily limits
      grading.py             # auto-grading for tf/mcq
      stats.py
      sources.py             # PDF page → PNG (pypdfium2) with cache; whitelisted paths
      reports.py
      reviews.py             # apply review / undo / suspend / item JSON view (added S1)
      settings.py            # Settings pydantic model + load/update (added S1)
      api.py                 # FastAPI routers
      app.py                 # app factory, static SPA serving
      cli.py                 # typer CLI
    tests/
  frontend/
    package.json, vite.config.ts, tsconfig.json, index.html, tailwind config
    public/                  # icons, manifest assets
    src/
      api/                   # typed client
      components/            # CardView, Markdown (with KaTeX), ChoiceList, GradeBar, SourceViewer, ReportDialog, Heatmap…
      pages/                 # Home, Review, Browse, Stats, Reports, Settings
      hooks/, lib/
  content/
    course.yaml              # registry: lectures (id, week, title, pdf, active, …) + theme vocabulary + exam date
    cards/<lecture_id>.yaml  # concept cards + unofficial exam-style cards of that lecture
    exams/<lecture_id>.yaml  # official past-exam questions whose primary lecture is <lecture_id>
    exam-index.yaml          # classification of EVERY official MC/TF question of every past exam (see §8.3)
    img/                     # extracted figures (PNG/WebP), named after the card id
  deploy/
    VPS.md                   # step-by-step runbook (§10)
    revision.service         # systemd unit
    revision-backup.service, revision-backup.timer
    update.sh                # on the VPS: pull, sync deps, build if needed, content check, restart
    pull-backup.sh           # on the Mac: fetch latest backup from the VPS over Tailscale
  data/                      # LOCAL default REVISION_DATA_DIR — gitignored (db, cache/, backups/)
```

Add to the root `.gitignore`: `revision/data/`, `revision/frontend/node_modules/`, `revision/frontend/dist/`, `revision/.venv/`, `__pycache__/`.

---

## 4. Content model

### 4.1 `content/course.yaml`
```yaml
exam_date: null            # set when published (Jan 2027); used by stats countdown + optional exam-date mode
timezone: Europe/Zurich
day_rollover_hour: 4       # a "day" starts at 04:00 local time (Anki-like)
lectures:
  - id: "04a"              # string id = lecture code used in docs/lectures/README.md
    week: 4
    title: "Generalization, Model Selection, Validation"
    date: 2026-09-29
    pdf: lectures/04/lecture04a.pdf
    annotated_pdf: null    # fill when *_annotated.pdf arrives
    sheet: docs/lectures/04-generalization-bias-variance.md
    active: true           # false = cards exist but are excluded (should rarely be needed)
themes:
  - {id: generalization, label: "Generalization & risk"}
  - {id: model-selection, label: "Model selection & cross-validation"}
  # … controlled vocabulary; extend when new lectures need it (see §8.5 starter list)
```
Weeks are derived from lectures. A lecture appears in `course.yaml` only once its cards are written.

### 4.2 Card schema (`content/cards/*.yaml`, `content/exams/*.yaml`)
Each file is a YAML list of cards. Fields:

| Field | Req. | Meaning |
|---|---|---|
| `id` | ✔ | **Stable, unique, never reused** (progress is keyed on it). Concept: `<lecture>-<slug>` (`04a-hoeffding-bound`). Official exam: `exam-<year>-q<NN>` (finals), `mock-<year>-q<N>[<sub>]` (mock midterms). Unofficial: `style-<lecture>-<slug>`. Typo fixes keep the id; a change of meaning/answer ⇒ new id (old one deleted). |
| `type` | ✔ | `basic` (self-graded Q→A), `cloze` (self-graded fill-in), `tf` (auto-graded True/False), `mcq` (auto-graded multiple choice). |
| `origin` | ✔ | `concept` · `exam_official` · `exam_style` (unofficial). `tf`/`mcq` may be any origin; `exam_official` must be `tf`/`mcq`. |
| `lecture` | ✔ | Primary lecture id (must exist in `course.yaml`). Week is derived. |
| `also_lectures` | | Other lectures the card depends on (card is active only if **all** are active). |
| `themes` | ✔ | ≥ 1 theme id from the vocabulary. |
| `priority` | ✔ | `core` (exam-essential — must know) or `detail`. Enables an "essentials only" filter. |
| `front` | ✔ | Markdown + LaTeX. `cloze`: text with `{{c1::answer}}` / `{{c1::answer::hint}}`; each distinct `cN` = one review item. |
| `back` | basic | Answer (short). |
| `choices` | mcq | List of markdown strings (2–6). |
| `answer` | tf/mcq | tf: `true`/`false`. mcq: list of 0-based indices into `choices` (≥ 1). |
| `multi` | | mcq "select all that apply" (all-or-nothing grading). Default false. |
| `shuffle` | | mcq: shuffle choices at display (default true; set false for "All of the above"-type choices). |
| `explanation` | exam_* ✔ | Why the answer is right **and why the distractors are wrong**; for concept cards optional extra intuition. |
| `trap` | | One-line "classic trap" shown highlighted (e.g. "Hoeffding does NOT apply to the training error"). |
| `images` | | Paths relative to `content/` (e.g. `img/exam-2023-q12.png`); rendered under the question; each with `alt`. Format: `[{src: ..., alt: ...}]`. |
| `sources` | ✔ | ≥ 1: `{kind: lecture\|exam\|lab\|doc, pdf: <repo-relative path>, page: <PDF page, 1-based>, label: "04a slide 17"}`; exam: label `"Final 2023 Q30"`, pdf = the **solutions** PDF, page = page of the question there. `kind: doc` uses `path: <repo-relative file>` instead of `pdf`/`page`. |
| `added` | ✔ | ISO date. |
| `notes` | | Internal authoring notes (not shown), e.g. "formula reconstructed from slide image; verified 2026-10-05". |

Validation (`uv run revision content check`, also run at app startup, fatal on error):
unique ids across all files; known lecture/theme ids; required fields per type/origin; mcq answer indices in range and ≥ 1; tf answer boolean; cloze has ≥ 1 well-formed `{{cN::…}}` and numbering starts at 1 without gaps; image files exist; source PDFs exist and `page` ≤ page count; no leftover `TODO` in shown fields; markdown/LaTeX sanity (balanced `$`); warn on very long fronts (> 400 chars; not for `exam_official`, whose stems are verbatim) or backs (> 300 chars, excluding explanation).
*Implemented (S1) — also errors:* id conventions per origin (`<lecture>-…`, `style-<lecture>-…`, `exam-YYYY-qN` / `mock-YYYY-qN[sub]`); file placement (`cards/<lecture>.yaml` for concept + exam_style, `exams/<lecture>.yaml` for exam_official; `lecture` = file stem); unknown fields (typos) rejected; source PDFs must be in the viewer whitelist; official cards need an `exam` source; a cloze answer must not split a `$…$` span (wrap whole math spans: `{{c1::$…$}}`); lectures in `course.yaml` in week order.

### 4.3 Examples (illustrative — page numbers to be verified when writing real cards)
```yaml
- id: 04a-hoeffding-bound
  type: cloze
  origin: concept
  lecture: "04a"
  themes: [generalization]
  priority: core
  front: |
    For a fixed $f$ independent of $S_\text{test}$ and a loss $\ell \in [a,b]$, with probability $\ge 1-\delta$:
    $|L_\mathcal{D}(f) - L_{S_\text{test}}(f)| \le$ {{c1::$\sqrt{\frac{(b-a)^2 \ln(2/\delta)}{2|S_\text{test}|}}$}}
  explanation: |
    Hoeffding applied to the i.i.d. losses $\Theta_n = \ell(y_n, f(x_n))$. Error shrinks as $O(1/\sqrt{|S_\text{test}|})$; $\delta$ only enters through a log.
  trap: "Requires f independent of the test set — never valid for the training error."
  sources:
    - {kind: lecture, pdf: lectures/04/lecture04a.pdf, page: 10, label: "04a slide 10"}
  added: 2026-10-02

- id: exam-2023-q30
  type: tf
  origin: exam_official
  lecture: "04a"
  themes: [generalization]
  priority: core
  front: |
    *(Generalization)* When the loss function $\ell \in [a,b]$ is bounded, Hoeffding's inequality allows us to bound the
    difference between the true error $L_\mathcal{D}(f_{S_\text{train}})$ and the training error $L_{S_\text{train}}(f_{S_\text{train}})$, which leads to
    $$\mathbb{P}_{S_\text{train}}\Big[|L_\mathcal{D}(f_{S_\text{train}}) - L_{S_\text{train}}(f_{S_\text{train}})| \ge \sqrt{\tfrac{(b-a)^2\ln(2/\delta)}{2|S_\text{train}|}}\Big] \le \delta.$$
  answer: false
  explanation: |
    Hoeffding bounds the gap between the true error and the error on a **held-out** set ($S_\text{test}$). On the training set the
    losses $\ell(f_{S_\text{train}}(x_i), y_i)$ are not independent (the predictor depends on all training points) and
    $L_\mathcal{D}$ is not their expectation.
  trap: "Hoeffding ⇒ test/validation error only."
  sources:
    - {kind: exam, pdf: exam/final-exam-2023-solutions.pdf, page: 11, label: "Final 2023 Q30"}
    - {kind: lecture, pdf: lectures/04/lecture04a.pdf, page: 13, label: "04a slides 12–13"}
  added: 2026-10-02

- id: exam-2025-q24
  type: mcq
  origin: exam_official
  lecture: "04a"
  themes: [model-selection]
  priority: core
  front: |
    *(Cross-Validation)* A student performs model selection for ridge regression over 5 candidate values
    $\{\lambda_1,\dots,\lambda_5\}$ using K-fold cross-validation with K = 5. How many times must the learning algorithm be trained?
  choices: ["25", "1", "5", "10"]
  answer: [0]
  explanation: |
    A full 5-fold CV is run **for each** candidate λ: 5 trainings × 5 values = 25.
  sources:
    - {kind: exam, pdf: exam/final-exam-2025-solutions.pdf, page: 12, label: "Final 2025 Q24"}
  added: 2026-10-02

- id: style-03d-lambda-direction
  type: tf
  origin: exam_style
  lecture: "03d"
  themes: [regularization]
  priority: core
  front: "In ridge regression, decreasing $\\lambda$ towards 0 makes the model more prone to underfitting."
  answer: false
  explanation: "Small λ = weak penalty ⇒ close to least squares ⇒ overfitting risk. Large λ ⇒ weights shrunk to 0 ⇒ underfitting."
  sources:
    - {kind: lecture, pdf: lectures/03/lecture03d_ridge.pdf, page: 4, label: "03d"}
  added: 2026-10-02
```

---

## 5. Scheduling (FSRS) and review logic

### 5.1 Items
A *review item* is the unit scheduled by FSRS: `basic`/`tf`/`mcq` card → 1 item (`item_id = card_id`); `cloze` card → one item per cloze index (`item_id = card_id::c1`, …). When reviewing a cloze item, only that cloze is blanked; the others are shown in full.

### 5.2 Scheduler settings (stored in `settings`, editable in the UI)
- `desired_retention` default **0.90** (UI: 0.80–0.97). `learning_steps` (1 min, 10 min), `relearning_steps` (10 min), `maximum_interval` 36500, fuzzing on — all py-fsrs defaults.
- `new_per_day` default **20**; `max_reviews_per_day` default **200** (soft cap; "review anyway" button).
- New-card order: course order (week → lecture order in `course.yaml` → position in file); concept cards of a lecture before its exam cards. Option: random.
- Interleave new cards among due reviews (≈ 1 new per 4 reviews). Learning/relearning items due within the session are re-inserted when due (re-poll; if nothing else, show "next card in 3 min" with a wait/continue option).
- Day boundary: `day_rollover_hour` in `timezone` (default 04:00 Europe/Zurich); store all datetimes in **UTC** (py-fsrs requirement).

*Implemented (S1):* new cloze siblings are buried (at most one new cloze of a card per day, none once a sibling was reviewed that day); learn-ahead window 20 min (`learn_ahead_minutes`); interleaving is stateless (new item when session reviews ≥ `interleave_ratio` × (session new + 1)); the queue takes `exclude=<last item>` to avoid immediate repeats. py-fsrs 6.3 has **no New state** (a fresh `Card` is Learning step 0): "new" = `items.state = 'new'` / `introduced_utc IS NULL`, tracked by us. Interval previews use a no-fuzz copy of the scheduler.

### 5.3 Grading
- **Self-graded** (`basic`, `cloze`): front → reveal (tap / Space) → back + explanation + trap → four buttons **Again / Hard / Good / Easy**, each showing its **next-interval preview** (computed by simulating `review_card` on a copy, e.g. "10m · 1d · 3d · 9d").
- **Auto-graded** (`tf`, `mcq`): answer → **Check** → result (✓/✗, correct choice highlighted, explanation, trap, "Unofficial" badge for `exam_style`). Rating is derived: wrong ⇒ **Again**; correct ⇒ **Good**; correct + "I guessed" toggle ⇒ **Hard**; optional "Too easy" ⇒ **Easy**. `multi` mcq: exact set match required.
- Store in the review log: rating, whether auto-graded, chosen answer, correctness, guessed flag, response time (ms, capped at 5 min), mode, content hash of the card at review time.
- **Undo** last review (restores the previous FSRS state stored with the log entry; `U` key / button).

### 5.4 Modes and filters
All modes respect `active` lectures and suspended items. Reviews done in any mode update the single FSRS schedule (like Anki filtered decks); reviewing before due is allowed (FSRS handles early reviews).

| Mode | Content |
|---|---|
| **Global** | Due items + new items (daily limits) across all active lectures. Default "Study now". |
| **Filtered** | Same, restricted by any combination of: **week(s)**, **lecture(s)**, **theme(s)**, origin (concept / official exam / unofficial exam), type, priority (`core` only). Weeks/lectures/themes selectable as chips on Home. |
| **Exam mode** | Only `tf`/`mcq` items (`exam_official` + `exam_style`, toggles for each). Option "include not-yet-due" to drill all unlocked exam questions in random order. |
| **Weak points** | Items ranked by a weakness score — e.g. `lapses × 2 + (1 − retrievability now) × 3 + difficulty/10 + (last rating was Again in last 7 days ? 2 : 0)` — top N (default 30), regardless of due date. Also shows the weakest lectures/themes. |
| **Custom drill** | "Review N random items from <filter>" ignoring due dates (useful in the revision period). |
| *Mock exam* (stretch, §12 M8) | Timed exam simulation from official questions of active lectures, scored with real exam points (MC 2, T/F 1.5), results page; answers also applied as reviews. |
| *Exam-date mode* (stretch) | When `exam_date` is set: in the last N weeks raise desired retention (e.g. 0.95) and offer "cram all cards with R < 0.9". |

### 5.5 Suspend / reports
- **Suspend** an item (excluded until unsuspended) from the review screen or Browse.
- **Flag this card** (`R` key / ⚑ button): dialog with reason (`wrong`, `unclear`, `typo`, `too-long`, `duplicate`, `bad-source`, `other`) + free comment → `reports` table (status `open`). Reviewing continues.
- Report circuit: `uv run revision reports list --open` (markdown to stdout; works locally and on the VPS over `ssh`) → Claude fixes the card in `content/` (new id if the answer changes) → `uv run revision reports resolve <id> --note "…"`. Reports page in the UI lists open/resolved reports with the card. **Every content session starts by processing open reports** (§9).

---

## 6. Data model (SQLite)

```
schema_version(version)
items(item_id PK, card_id, cloze_index NULL, fsrs_card_json, state new|learning|review|relearning, due_utc NULL,
      stability, difficulty, reps, lapses, last_review_utc NULL, suspended INT DEFAULT 0, introduced_utc NULL, created_utc)
review_log(id PK, item_id FK, card_id, reviewed_utc, rating 1–4, auto_graded INT, correct INT NULL, guessed INT,
           answer_json NULL, duration_ms, mode, session_id NULL, card_hash, prev_state, prev_item_json, fsrs_review_log_json)
reports(id PK, card_id, item_id NULL, reason, comment, created_utc, status open|resolved, resolved_utc NULL, resolution_note NULL)
settings(key PK, value_json)
mock_exams(...)            # stretch
```
- *As implemented (S1):* `prev_item_json` stores the **whole previous item row** (FSRS card + reps/lapses/state/introduced), so undo restores it exactly and deletes the log row. `session_id` (client-generated) drives drill/weak sessions, interleaving and the session summary. Datetimes are fixed-width UTC strings `YYYY-MM-DDTHH:MM:SS.ffffffZ` (lexicographic = chronological).
- Content sync at startup/reload: create `items` rows for new card items (state New, not introduced); items whose card disappeared are kept but hidden (orphans; report them in `content check --db`).
- The review log is the ground truth (FSRS state can be recomputed from it; also feeds the optional FSRS optimizer).
- `revision backup` = SQLite online backup API → `backups/revision-YYYYMMDD-HHMM.db`, keep last 30. `revision export` = full JSON dump (download button in Settings too).

---

## 7. API (FastAPI, JSON) and UI

### 7.1 Endpoints (indicative)
- `GET /api/meta` — lectures (with week, title, active, counts), themes, settings, exam date.
- `GET /api/queue?mode=&weeks=&lectures=&themes=&origin=&type=&priority=` — next item + counts (new / learning / review remaining) + interval previews.
- `POST /api/review` — `{item_id, rating?, answer?, guessed?, duration_ms, mode}` → grading result (for tf/mcq: correct + correct answer) + next due.
- `POST /api/undo`
- `GET /api/cards?q=&filters…` (Browse, full-text search) · `GET /api/cards/{id}` (content + per-item stats + history) · `POST /api/items/{item_id}/suspend|unsuspend`
- `POST /api/reports` · `GET /api/reports?status=` · `POST /api/reports/{id}/resolve`
- `GET /api/stats/overview|calendar|forecast|by-lecture|by-theme|exam`
- `GET /api/source/page?pdf=&page=&scale=` → PNG (rendered with pypdfium2, cached in `DATA_DIR/cache/pages/`); `GET /files/{path}` → raw PDF. **Whitelist**: only `lectures/`, `exam/`, `labs/*/exercise*.pdf`, `revision/content/img/`; reject `..`.
- `GET/PUT /api/settings` · `GET /api/export` · `GET /api/health`
- *Added in S1:* `GET /api/session/{session_id}/summary`, `GET /api/stats/weakest`, `POST /api/admin/reload` (reload content + sync items; 422 with the error list if invalid, old content kept). Queue params: `mode=study|exam|weak|drill`, filters as comma lists (`weeks`, `lectures`, `themes`, `origins`, `types`) + `core`, `session_id`, `exclude`, `include_not_due`, `learn_ahead`, `ignore_limits`, `limit`. For tf/mcq the queue **withholds** `answer`, `explanation`, `trap`; they come back in the `POST /api/review` result. Cloze items arrive pre-rendered: `front` with the blank as `**[…]**` (or `**[hint]**`), `back` with the answer in bold.
- `GET /content-img/{path}` → card images.

### 7.2 Pages
- **Home**: big "Study now" with due counts; streak + today's count; quick-start tiles: *Exam mode*, *Weak points*, *Essentials only*; filter builder with chips (weeks, lectures with titles, themes); per-week progress bars (cards seen / mature).
- **Review**: one card at a time; header shows lecture/theme chips, origin badge (**Official exam 2023 Q30** / **Unofficial — exam-style**), remaining counts; footer = action bar. Source button opens a **SourceViewer** sheet showing the rendered PDF page (pinch-zoom on phone, prev/next page, "open full PDF").
- **Browse**: searchable, filterable card list; card detail with rendered content, sources, per-item state (due, stability, difficulty, retrievability, lapses), review history, suspend.
- **Stats**: reviews per day (last 90 d) + calendar heatmap; true retention (last 7/30 d, self vs auto-graded); card counts by state; due forecast (next 30 d); mastery by lecture and by theme (mean retrievability, % mature = interval ≥ 21 d); exam stats (accuracy by year, by theme, official vs unofficial); weakest 20 cards; countdown to exam date if set.
- **Reports**: open/resolved list.
- **Settings**: retention, daily limits, new-card order, interleaving, theme (light/dark/system), font size, swipe gestures on/off, export/backup download.

### 7.3 UX requirements
- **Mobile-first**, works from 360 px wide; no horizontal page scroll (long formulas scroll horizontally inside their own box); iPhone safe areas (`env(safe-area-inset-*)`); action buttons in the thumb zone, ≥ 44 px targets; tap anywhere on the card to reveal; optional swipe gestures (left = Again, right = Good on self-graded cards; off by default to avoid mis-grades).
- **Desktop keyboard**: `Space`/`Enter` reveal → `Good`; `1–4` Again/Hard/Good/Easy; mcq `1–6` or `A–F` select, `Enter` check/continue; tf `T`/`F` (or `←`/`→`); `G` toggle "I guessed"; `U` undo; `S` source; `R` flag; `Esc` end session; `?` shortcut help overlay.
- Light/dark (follow system + manual), comfortable reading typography, KaTeX in display and inline mode, images responsive with tap-to-zoom.
- **PWA**: manifest (name "CS-433 Review", standalone, theme color), icons incl. `apple-touch-icon`, service worker caching only the app shell (API = network-only; show an offline banner — offline reviewing is out of scope).
- Session summary screen at the end (count, accuracy on auto-graded, time, items to come back to).
- Snappy: prefetch the next item; response < 100 ms locally.

---

## 8. Content production (the most important part)

### 8.1 When
Cards for a lecture are written **in the catch-up session where the student finishes that lecture** (or right after), never ahead: at that moment Claude has the lecture fresh and knows what the student found hard (those confusions become cards). The lecture is then added to `course.yaml` with `active: true`. Official exam questions are added when **all** lectures they depend on are active.

### 8.2 Card-writing rules (adapted from SuperMemo's "20 rules" + exam focus)
1. **Understand before memorizing**: base every card on the PDF pages (source of truth) and the lecture sheet; the sheet is only an index. Formulas in lectures 01–03 are images: verify them on the rendered slide (`pdftoppm -f P -l P -r 70 -png`), as `CLAUDE.md` explains.
2. **Minimum information**: one fact / one idea per card; short answers (≤ 2 lines); extra context goes to `explanation`.
3. **Formulas → cloze**, blanking one meaningful part at a time (not the whole formula when it is long; use several `cN`).
4. **No long enumerations**: lists > 3 items → split or cloze each element.
5. **Why / intuition cards** ("Why does L1 give sparse solutions?") and **contrast cards** ("Ridge vs Lasso: which is sparse and why?").
6. **Derivation cards** (`basic`, priority `core` when exam-relevant): front = "Derive …", back = numbered key steps (e.g. bias–variance decomposition: expand, kill cross term with 𝔼ε = 0 and ε ⊥ S, add/subtract 𝔼_S'[f_S'(x₀)]…).
7. **Traps**: every pitfall listed in the sheet's "Exam-relevant points / pitfalls" becomes a card (often a `tf`/`mcq` exam-style card with `trap`).
8. Context cue at the start of the front when ambiguous (`*(Ridge)*`, `*(Hoeffding)*`).
9. Course notation (`docs/glossary.md`); lab/P1 MSE uses the **1/(2N)** factor; λ' = 2Nλ in the ridge closed form.
10. English only; neutral, exam-like wording; no French.
11. `sources` always present and **page verified**; for concept cards prefer the annotated PDF page when the professor's handwriting adds the key idea (use `annotated_pdf` path in the source).
12. Never invent facts. If something is uncertain or reconstructed, say so in `notes` and verify; if still uncertain, don't make the card.
13. Volume guide: ~15–40 concept cards per lecture depending on density (01a intro: only the few exam-relevant definitions; skip course organisation), plus 3–10 unofficial exam-style tf/mcq per lecture targeting its traps. Mark exam-essential ones `core`.

### 8.3 Official exam questions — extraction and verification
1. **Build `content/exam-index.yaml` once** (milestone M4): for every final 2016–2025 and mock midterm, list every MC and T/F question: `{exam: final-2023, q: 30, type: tf|mcq, topic: "<short>", lectures: [04a], status: added|pending|open-excluded|figure, page: <page in solutions PDF>}`. Open/derivation questions get `open-excluded` (out of scope for now). 2016–2018 finals use numbered problems: index only their MC/short-answer sub-questions that can be auto-graded; mock midterms are mostly derivations (`open-excluded`). This index lets each later content session simply pick `pending` questions whose lectures became active.
2. Text: `pdftotext -layout exam/final-exam-YYYY-solutions.pdf -`. Clean the "DRAFT" watermark noise (stray `DR`, `AF`, `T` fragments) and broken math; rewrite math in LaTeX faithfully. Keep the **stem and choices verbatim** (wording matters for the exam), only fix extraction artifacts.
3. **Correct answer**: read the "Solution:" text; when the solution only marks a ticked box, **render the page** (`pdftoppm -f P -l P -r 80 -png`) and read which box is filled. Never guess. If the official answer looks wrong, keep it but say so in `explanation` and flag for the student.
4. **Figures**: crop the figure from the rendered page (PIL; ~1000 px wide max, PNG or WebP, < 200 KB) into `content/img/<card-id>.png` with alt text.
5. Explanation = official solution reasoning (paraphrased) + why each distractor is wrong + link to the lecture slide (second source).

Questions already identified during sessions (non-exhaustive — the index in step 1 is the authoritative sweep). Lecture mapping in brackets:
- **Regression / loss (01b–01c):** 2025 Q4 (MAE for a bounded real target). 2024 Q40 is open (excluded).
- **Optimization (02a):** 2025 Q5 (MSE gradient), 2025 Q6 (Hessian cost O(N·D²)), 2025 Q31 (SGD gradient unbiased — T), 2025 Q37 (MSE Hessian constant in w — T), 2022 Q24 (subgradient of |x−2023| not unique — F), 2020 Q6 (−x² has no subgradient at 0), 2021 Q16 (PReLU subgradient — check official answer; may depend on NN lectures), 2020 Q5 (GD vs SGD cost), 2022 Q4 (step size on λ/2‖w‖²), 2020 Q28 (convex ⇒ unique min — F), 2019 Q17–Q19 (convex sets/compositions).
- **Least squares / overfitting / MLE / ridge & lasso (03a–03d):** 2025 Q7 (D > N singular, ridge), 2020 Q26 (N ≤ D ⇏ zero training error — F), 2022 Q25 (λ direction — F), 2023 Q16 (L1 sparse — T), 2016 (L2 "sparse" — F; locate exact number), 2021 Q8 (L1 storage / lasso), 2024 Q18 (lasso vs ridge), 2024 Q19 (lasso scale: ×10 feature more likely kept), 2022 Q5 (Laplace prior ↔ lasso), 2025 Q12 (Adam is not regularization), 2021 overfitting MCQ (ridge reduces train/test gap; locate number). 2020 Q37–38 and 2025 Q43 are open (excluded).
- **Generalization / model selection / CV / bias–variance (04a–04b):** 2023 Q30 (Hoeffding on training error — F), 2023 Q31 (selection bound with training error — F), 2024 Q34 (train until low test loss — F), 2025 Q24 (5 λ × 5 folds = 25), 2021 Q3 (K-fold cost O(K)), 2025 Q25 (bias/variance/noise definitions — noise only algorithm-independent term), 2022 Q27 (high bias ⇒ low variance — F), 2021 Q4 (quadratic vs constant model: lower bias, higher variance), 2021 Q26 (training error ≥ σ² — F), 2022 Q6 (ridge vs OLS: larger bias, smaller variance). 2020 Q39 is open (excluded; can inspire an unofficial tf). 2025 Q33 (k-NN) and 2018 LOO-CV with k-NN wait for the k-NN lecture (week 6).

### 8.4 Student-specific points (from catch-up sessions — make sure cards cover them)
- He inverted the λ direction once (thought small λ ⇒ underfitting). Large λ ⇒ underfit, small λ ⇒ overfit; λ and polynomial degree d act in opposite directions.
- `f_S` is a **function** (the trained predictor); `f_S(x)` is one prediction.
- "s.t." = subject to (constrained form min L(w) s.t. ‖w‖₁ ≤ c ⇔ penalized form).
- Sparse = most coordinates exactly 0 ⇒ feature selection.
- MAP: regularizer = −log prior; Gaussian prior ⇔ ridge, Laplace prior ⇔ lasso.
- Lasso is not scale-invariant (2024 Q19): standardize features first.
- Why L1 is sparse — three views (1-D soft-thresholding vs ridge shrinkage; constant vs vanishing pull; geometry: corners of the L1 ball, ellipse level sets centered at w_LS). He saw 03d slides 10–12 **only in broad strokes** → give these extra cards.
- Training error is optimistic; Hoeffding only on data independent of the model (2023 Q30–31).
- Bias = average prediction vs truth (systematic), variance = spread across training sets; simple model ⇒ high bias / low variance. "Not realizable" = f not in the model class (not "impossible to compute").
- Learning curves: high variance = large train/test gap, test still decreasing (more data helps); high bias = curves meet at a high plateau (more data useless).
- The Hoeffding proof (04a slides 23–27) was presented as a bonus → `detail` priority at most.

### 8.5 Starter theme vocabulary
`ml-basics`, `linear-regression`, `loss-functions`, `convexity`, `optimization`, `gradient-descent`, `sgd`, `subgradients`, `constrained-optimization`, `least-squares`, `overfitting`, `polynomial-features`, `mle`, `probability`, `regularization`, `ridge`, `lasso`, `generalization`, `model-selection`, `cross-validation`, `bias-variance`. Extend as lectures progress (classification, logistic-regression, svm, knn, kernels, neural-nets, …).

### 8.6 Initial content scope (weeks 1–4)
| Week | Lecture id | PDF | Sheet | Notes |
|---|---|---|---|---|
| 1 | 01a | `lectures/01/lecture01a_intro.pdf` | `docs/lectures/01-intro-regression-loss.md` §A | intro: few cards (task types, terminology) |
| 1 | 01b | `lectures/01/lecture01b_regression.pdf` (+ annotated) | same §B | |
| 1 | 01c | `lectures/01/lecture01c_loss_functions.pdf` (+ annotated) | same §C | |
| 2 | 02a | `lectures/02/lecture02a_optimization.pdf` (+ annotated) | `docs/lectures/02-optimization.md` | 56 pages, dense: biggest card set |
| 3 | 03a–03d | `lectures/03/lecture03{a,b,c,d}_*.pdf` (+ annotated) | `docs/lectures/03-least-squares-regularization.md` | 03c slide 9 and 03d slide 8 optional (`detail`); 03d additional notes optional |
| 4 | 04a, 04b | `lectures/04/lecture04{a,b}.pdf` (annotated not yet out on 2026-10-02) | `docs/lectures/04-generalization-bias-variance.md` | slide N = PDF page N |
Check `docs/schedule.md` for the exact caught-up status and what was skipped/optional.

### 8.7 Content-session checklist (each lecture)
1. Process open reports (§5.5). 2. Read the sheet, then the PDF pages (and annotated pages). 3. Write concept cards → 4. unofficial exam-style cards → 5. official exam questions now unlockable (from `exam-index.yaml`) → 6. `uv run revision content check` → 7. open the app locally and visually check every new card (rendering, KaTeX, images, source page) → 8. update `exam-index.yaml` statuses and `course.yaml` → 9. commit (title-only message) → 10. deploy (§10.6) after asking the student.

---

## 9. Integration with the repo pipeline
At milestone M7, update `CLAUDE.md` (keep it < 80 lines) with:
- a pointer line: revision app = `revision/` (spec `revision/SPEC.md`, run instructions `revision/README.md`);
- in "Documentation maintenance": *"Lecture caught up by the student → write its cards (`revision/SPEC.md` §8), run `uv run revision content check`, commit, push, deploy. Start every content session by processing open card reports."*
- in `docs/schedule.md` notes: cards status per lecture can be read from `revision/content/course.yaml`.
Also add a line to `docs/labs.md`/`docs/exams.md` if relevant (e.g. exam-index location).

---

## 10. Deployment

### 10.1 Local (Mac)
```
cd revision
uv sync
uv run revision content check
uv run revision serve --reload          # API on http://127.0.0.1:8433
cd frontend && npm install && npm run dev   # UI on http://localhost:5173 (proxies /api, /files, /content-img)
# production-like: npm run build, then `uv run revision serve` serves frontend/dist at http://127.0.0.1:8433/
```
Local data dir: `revision/data/` (gitignored). Optional quick phone test before the VPS exists: `tailscale serve --bg 8433` on the Mac (Tailscale.app is installed) — tailnet-only.

### 10.2 VPS — choose & order (done by the student)
Any provider (OVH VPS likely). Smallest plan is enough (1–2 vCPU, 2–4 GB RAM, ≥ 20 GB disk), EU region, **Ubuntu LTS (24.04 or newer)**, add his SSH public key at creation. Claude never handles passwords or payment; the student performs purchases and first login.

### 10.3 VPS — base setup & hardening (runbook in `deploy/VPS.md`, executed step by step with the student)
1. First SSH as the provider's default user; `apt update && apt full-upgrade`; set hostname (e.g. `ml-vps`) and timezone `Europe/Zurich`.
2. Create a sudo user (e.g. `elie`), install his SSH key; disable password auth and root login (`/etc/ssh/sshd_config.d/99-hardening.conf`), reload sshd **after** verifying key login in a second terminal.
3. `unattended-upgrades` enabled; optional `fail2ban`.
4. Install **Tailscale** (official instructions from tailscale.com), `sudo tailscale up --ssh`; in the Tailscale admin console enable **MagicDNS** and **HTTPS certificates**; disable key expiry for this machine.
5. Firewall (`ufw`): default deny incoming, allow outgoing, `allow in on tailscale0`; keep public 22 open until SSH over Tailscale is verified, then remove it. The provider's web console is the rescue path — mention it before closing port 22.
6. Install `uv` (official installer), Node LTS (NodeSource or official binaries), `git`, `sqlite3`.

### 10.4 App install
- Clone **shallow** (the repo's history is ~1.4 GB): `git clone --depth 1 https://github.com/nexiumito/ML_course.git ~/ML_course` (the fork is public; no credentials needed). Updates: `git fetch --depth 1 origin main && git reset --hard origin/main` (safe: the VPS never edits the repo; data lives outside it).
- Data dir: `/var/lib/revision` (owned by the app user) via `REVISION_DATA_DIR`.
- `deploy/revision.service` (systemd): `User=elie`, `WorkingDirectory=/home/elie/ML_course/revision`, `Environment=REVISION_DATA_DIR=/var/lib/revision`, `ExecStart=/home/elie/.local/bin/uv run --frozen revision serve --host 127.0.0.1 --port 8433`, `Restart=always`. Enable + start.
- Expose: `sudo tailscale serve --bg 8433` → `https://ml-vps.<tailnet>.ts.net/` (valid TLS, tailnet-only). **Never use `tailscale funnel`.**
- Acceptance: page loads on the phone over Tailscale; `curl http://<public-ip>:8433` from outside fails; app survives `sudo reboot`.
- Add to the phone home screen (Safari → Share → Add to Home Screen).

### 10.5 Backups
- `revision-backup.timer` daily 03:30 → `revision backup` (keeps 30). Restore procedure documented in `VPS.md` (stop service, copy file, start).
- Off-box copy: `deploy/pull-backup.sh` on the Mac (`scp` over Tailscale of the latest backup into `revision/data/backups/`) — run manually or via a launchd job; plus the "Export" button in Settings.
- If he reviewed locally before the VPS existed: migrate once (`revision backup` locally → copy to `/var/lib/revision/revision.db` → restart), then use only the VPS.

### 10.6 Content updates
After a content session on the Mac: commit → `git push origin main` (ask the student first) → `ssh elie@ml-vps '~/ML_course/revision/deploy/update.sh'` (via Tailscale SSH). `update.sh`: fetch/reset, `uv sync --frozen`, rebuild frontend only if `revision/frontend/` changed, `revision content check` (abort on failure, keep the old version running), `systemctl restart revision`. Optional: a 15-min systemd timer running `update.sh` automatically.

---

## 11. Quality, testing, conventions
- Backend tests: content validator (good/bad fixtures), cloze parsing, item creation/sync, scheduler wrapper (ratings → state; previews), grading (tf, mcq, multi), queue building per mode/filter + daily limits + day rollover, undo, reports, source path whitelist, API smoke tests (`TestClient`). Run `uv run pytest` before every commit touching the backend.
- Frontend: `npm run typecheck`, `npm run lint`, vitest for queue/keyboard logic; manual check at 375×812 (phone) and desktop in the browser preview.
- Accessibility basics: semantic buttons, focus states, color is never the only signal (✓/✗ icons + text).
- Keep `revision/README.md` current (run, add content, deploy).
- Commits: title line only. Talk to the student in French. Ask before pushing, deploying, or any outward-facing action.

---

## 12. Milestones & progress checklist
Estimated sessions: **S1** = M0–M2, **S2** = M3, **S3** = M4, **S4** = M5, **S5** = M6, **S6** = M7. M8 = optional later. Tick items as they are completed (with date).

### M0 — Scaffold ✅ 2026-10-02
- [x] `revision/` tree, `pyproject.toml` (uv, deps: fastapi, uvicorn[standard], pydantic, pyyaml, fsrs, pypdfium2, typer; dev: pytest, httpx, ruff), Vite React-TS app with Tailwind, KaTeX, PWA plugin
- [x] `.gitignore` entries; `revision/README.md` (the `CLAUDE.md` pointer line to this spec already exists since 2026-10-02)
- **Done when:** `uv run revision --help` and `npm run dev` both work.

### M1 — Content model ✅ 2026-10-02
- [x] pydantic models + YAML loader + `revision content check` implementing all §4.2 rules
- [x] `content/course.yaml` with weeks 1–4 lectures (active) and the §8.5 theme vocabulary
- [x] 3–5 sample cards (one per type) in `content/cards/04a.yaml` / `content/exams/04a.yaml`
- [x] tests with good/bad fixtures
- **Done when:** check passes on samples and fails with clear messages on each bad fixture.

### M2 — Backend ✅ 2026-10-02
- [x] SQLite schema + migrations; content→items sync; FSRS wrapper; queue building for all modes/filters; grading; undo; suspend; reports; stats; source page rendering with cache + whitelist; export/backup CLI; static SPA serving
- [x] pytest suite green
- **Done when:** a full review session can be driven through the API (TestClient) for every card type and mode.

### M3 — Frontend
- [ ] Home, Review (all 4 types, previews, auto-grading UI, guessed toggle, source viewer, flag dialog, undo, session summary), Browse, Stats, Reports, Settings
- [ ] keyboard shortcuts + help overlay; mobile layout (375 px), safe areas, optional swipe; dark mode; PWA manifest/icons/service worker
- **Done when:** the student can do a real session on desktop and in a phone-sized viewport; KaTeX and images render; Lighthouse PWA installable.

### M4 — Exam index + content weeks 1–2
- [ ] `content/exam-index.yaml` covering all finals 2016–2025 and mock midterms (every MC/TF classified, open ones excluded)
- [ ] cards 01a, 01b, 01c, 02a (concept + unofficial exam-style) + official questions for these lectures
- **Done when:** content check passes; every new card visually checked in the app.

### M5 — Content week 3
- [ ] cards 03a, 03b, 03c, 03d (incl. §8.4 lasso extras) + official questions now unlockable

### M6 — Content week 4 + polish
- [ ] cards 04a, 04b + official questions (§8.3 list) + unofficial set
- [ ] end-to-end local QA with the student; fix reports
- **Done when:** the student validates the app locally with all week 1–4 content.

### M7 — VPS deployment & pipeline integration
- [ ] `deploy/` files + `deploy/VPS.md`; base setup & hardening; Tailscale; service; tailscale serve; backups timer; `update.sh`; `pull-backup.sh`
- [ ] migrate local progress; phone home-screen install
- [ ] `CLAUDE.md` + docs updated per §9
- **Done when:** §10.4 acceptance checks pass and a content update round-trip (Mac commit → push → update.sh) works.

### M8 — Later / optional
- [ ] Mock exam mode · [ ] exam-date mode · [ ] FSRS parameter optimization from the review log (`fsrs[optimizer]`, run on the Mac, store parameters in settings) once ≥ ~1000 reviews · [ ] open-question cards (self-graded, French answers allowed) if the student asks.

---

## 13. Session log
- 2026-10-02 — Spec written (course week 4; lectures 01a–04b caught up, 03d slides 10–12 in broad strokes only). Next: S1 (M0–M2).
- 2026-10-02 — **S1 done (M0–M2).** uv project (fastapi, fsrs 6.3.2, pypdfium2, pillow, tzdata…), Vite 8 + React 19 + Tailwind 4 + KaTeX + vite-plugin-pwa shell (placeholder page; `npm run build` OK), full backend (content validator, SQLite + migrations, FSRS wrapper, queue for study/filtered/exam/weak/drill, grading, undo, suspend, reports, stats, PDF page renderer + whitelist, backup/export CLI, SPA serving), 114 pytest tests green, ruff clean. 5 real sample cards for 04a (2 concept, 1 unofficial tf, official 2023 Q30 + 2025 Q24; pages verified — 2023 Q30 is p. 11 of the solutions PDF). Deviations documented inline (*Implemented (S1)* notes in §4.2, §5.2, §6, §7.1). `.claude/launch.json` has `revision-api` / `revision-ui`. Next: S2 = M3 (frontend); the bundle is 612 kB (KaTeX + markdown) → code-split in M3.
