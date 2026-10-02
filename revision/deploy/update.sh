#!/usr/bin/env bash
# Update the revision app on the VPS (SPEC §10.6). Run as elie, e.g. from the Mac:
#   ssh elie@ml-vps '~/ML_course/revision/deploy/update.sh'
# Fetches origin/main (shallow), syncs Python deps, rebuilds the UI if revision/frontend/ changed, validates the content,
# then restarts the service. If any step or the content check fails, the previous commit is restored and the service is not
# restarted (the running process keeps the content it loaded at startup).
# Options (env): BRANCH (default main), FORCE=1 (redeploy even if already up to date).
# Needs: sudoers rule `elie ALL=(root) NOPASSWD: /usr/bin/systemctl restart revision` (see VPS.md).
set -euo pipefail

REPO="${REPO:-$HOME/ML_course}"
APP="$REPO/revision"
BRANCH="${BRANCH:-main}"
export PATH="$HOME/.local/bin:$PATH"
export REVISION_DATA_DIR=/var/lib/revision

log() { printf '\033[1m[update]\033[0m %s\n' "$*"; }

build_frontend() {
  log "building the frontend"
  (cd "$APP/frontend" && npm ci --no-audit --no-fund && npm run build)
}

# Bring the working tree to commit $1 (deps + UI); $2 = previous commit, to decide whether the UI must be rebuilt.
# Every step has an explicit `|| return 1`: `set -e` does not apply inside a function called from `if`.
deploy_tree() {
  local target="$1" prev="$2"
  git -C "$REPO" reset --hard --quiet "$target" || return 1
  (cd "$APP" && uv sync --frozen --no-dev --quiet) || return 1
  if [ ! -f "$APP/frontend/dist/index.html" ] || ! git -C "$REPO" diff --quiet "$prev" "$target" -- revision/frontend; then
    build_frontend || return 1
  fi
}

cd "$REPO"
old=$(git rev-parse HEAD)
log "fetching origin/$BRANCH"
git fetch --depth 1 --quiet origin "$BRANCH"
new=$(git rev-parse FETCH_HEAD)
if [ "$old" = "$new" ] && [ "${FORCE:-0}" != 1 ]; then
  log "already up to date ($(git log -1 --format='%h %s' "$old"))"
  exit 0
fi
log "$(git log -1 --format='%h %s' "$old") → $(git log -1 --format='%h %s' "$new")"

if ! deploy_tree "$new" "$old" || ! (cd "$APP" && .venv/bin/revision content check); then
  log "deploy or content check FAILED — restoring $(git log -1 --format=%h "$old"), service not restarted"
  deploy_tree "$old" "$new" || log "restore failed too — fix by hand (FORCE=1 BRANCH=… to redeploy)"
  exit 1
fi

log "restarting the service"
sudo systemctl restart revision
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8433/api/health >/dev/null 2>&1; then
    log "OK — $(curl -fsS http://127.0.0.1:8433/api/health)"
    exit 0
  fi
  sleep 1
done
log "service did not answer on /api/health within 30 s — check: journalctl -u revision -n 50"
exit 1
