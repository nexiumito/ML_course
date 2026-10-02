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
In the Claude desktop app, `.claude/launch.json` (repo root) has `revision-api` and `revision-ui` launchers
(and `revision-api-test`, which keeps its data in `revision/data/test/` — use it for UI tests so real progress is untouched).

Data (SQLite db, rendered-page cache, backups) goes to `revision/data/` (gitignored); override with `REVISION_DATA_DIR`.

## Production (VPS)
Runs on the VPS `ml-vps` (Ubuntu, systemd service `revision`, data in `/var/lib/revision`), reachable only over Tailscale at
`https://ml-vps.<tailnet>.ts.net/` (`tailscale serve`). The full setup runbook with the machine's details is kept **locally only**
(`deploy/VPS.md`, gitignored — ask the student if you need it). Day-to-day commands, from the Mac:
```bash
ssh elie@ml-vps '~/ML_course/revision/deploy/update.sh'          # deploy origin/main (content check before restart; FORCE=1 to redeploy)
# CLI on the live db — non-interactive ssh does not read ~/.bashrc, so pass the data dir explicitly:
ssh elie@ml-vps 'cd ~/ML_course/revision && REVISION_DATA_DIR=/var/lib/revision .venv/bin/revision reports list'
ssh elie@ml-vps 'cd ~/ML_course/revision && REVISION_DATA_DIR=/var/lib/revision .venv/bin/revision reports resolve 3 --note "…"'
ssh -t elie@ml-vps 'sudo systemctl start revision-backup'        # manual backup (daily timer at 03:30 keeps 30)
deploy/pull-backup.sh                                            # copy the latest backup into data/backups/
ssh elie@ml-vps 'journalctl -u revision -n 100 --no-pager'       # logs
```
Restore a db (on the VPS): `sudo systemctl stop revision`, remove `/var/lib/revision/revision.db-wal` and `-shm`,
`install -m 600 <file.db> /var/lib/revision/revision.db`, `sudo systemctl start revision`.

## Other commands
```bash
uv run revision content check --db       # + list DB items whose card disappeared (orphans)
uv run revision reports list [--all]     # card reports flagged in the app (markdown) — process at the start of a content session
uv run revision reports resolve 3 --note "fixed formula"
uv run revision backup                   # online SQLite backup → data/backups/ (keeps 30)
uv run revision export -o dump.json      # full JSON dump
uv run revision content mark-added       # exam-index: set status added for every official card that exists
uv run revision content dump-texts       # JSON lines of every shown text (input of `npm run check-math`)
uv run pytest                            # backend tests
uv run ruff check backend && uv run ruff format --check backend
cd frontend && npm run typecheck && npm run lint && npm test   # vitest
cd frontend && npm run check-math        # every card text through the app's KaTeX pipeline (fails on errors)
```

## Add content
1. Cards for lecture `<id>` go in `content/cards/<id>.yaml` (concept + unofficial `exam_style`), official past-exam
   questions in `content/exams/<id>.yaml`. Schema and writing rules: `SPEC.md` §4 and §8.
2. The lecture must be listed in `content/course.yaml`; themes come from its controlled vocabulary.
3. `uv run revision content check` must pass; with `serve --reload` the app reloads on YAML changes
   (or `POST /api/admin/reload`).
4. `npm run check-math`, then check every new card in the app at desktop **and 375 px** width: `/sheet?lecture=<id>&check=1`
   shows all cards of a lecture with answers plus an automatic layout check (see `SPEC.md` §8.2 rule 10b and §8.7).
5. Official questions: pick `pending` entries of `content/exam-index.yaml` whose lectures are active, write them in
   `content/exams/<lecture>.yaml`, run `uv run revision content mark-added`, then commit (title-only message).

## Layout
```
backend/revision/   config, content (models+validator), db, scheduler (py-fsrs), queue, grading, reviews,
                    stats, sources (PDF→PNG), reports, settings, api, app, cli
backend/tests/      pytest suite (fake repo with generated PDFs in tmp_path)
frontend/src/       React + TS + Vite + Tailwind + KaTeX + PWA
  api/              typed client + backend JSON types
  lib/              pure logic (math pre-processing, cloze marks, keys, shuffle, session spec) + vitest tests
  components/       Markdown (KaTeX), card parts, SourceViewer, ReportDialog, charts, UI kit, Layout
  pages/            Home, Review, Browse, CardPage, Stats, Reports, Settings
content/            course.yaml, cards/, exams/, img/
deploy/             VPS: systemd units, update.sh, pull-backup.sh (+ local-only runbook VPS.md, gitignored)
```
