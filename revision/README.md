# CS-433 Review — spaced-repetition app

Personal Anki-like app for EPFL CS-433 (FSRS scheduling, concept + exam cards, links to the slides).
Full specification, milestones and session log: [`SPEC.md`](SPEC.md).

## Run locally (Mac)

```bash
cd revision
uv sync
uv run revision content check            # validate all cards (also runs at app startup)
uv run revision serve --reload           # API on http://127.0.0.1:8433 (docs: /api/docs)
cd frontend && npm install && npm run dev   # UI on http://localhost:5173 (proxies /api, /files, /content-img)
```
Production-like: `npm run build` in `frontend/`, then `uv run revision serve` serves the built UI at http://127.0.0.1:8433/.
In the Claude desktop app, `.claude/launch.json` (repo root) has `revision-api` and `revision-ui` launchers.

Data (SQLite db, rendered-page cache, backups) goes to `revision/data/` (gitignored); override with `REVISION_DATA_DIR`.

## Other commands
```bash
uv run revision content check --db       # + list DB items whose card disappeared (orphans)
uv run revision reports list [--all]     # card reports flagged in the app (markdown) — process at the start of a content session
uv run revision reports resolve 3 --note "fixed formula"
uv run revision backup                   # online SQLite backup → data/backups/ (keeps 30)
uv run revision export -o dump.json      # full JSON dump
uv run pytest                            # backend tests
uv run ruff check backend && uv run ruff format --check backend
cd frontend && npm run typecheck && npm run lint
```

## Add content
1. Cards for lecture `<id>` go in `content/cards/<id>.yaml` (concept + unofficial `exam_style`), official past-exam
   questions in `content/exams/<id>.yaml`. Schema and writing rules: `SPEC.md` §4 and §8.
2. The lecture must be listed in `content/course.yaml`; themes come from its controlled vocabulary.
3. `uv run revision content check` must pass; with `serve --reload` the app reloads on YAML changes
   (or `POST /api/admin/reload`).
4. Check every new card in the app (rendering, KaTeX, source page), then commit (title-only message).

## Layout
```
backend/revision/   config, content (models+validator), db, scheduler (py-fsrs), queue, grading, reviews,
                    stats, sources (PDF→PNG), reports, settings, api, app, cli
backend/tests/      pytest suite (fake repo with generated PDFs in tmp_path)
frontend/           React + TS + Vite + Tailwind + KaTeX + PWA (M3)
content/            course.yaml, cards/, exams/, img/
deploy/             VPS files (M7)
```
