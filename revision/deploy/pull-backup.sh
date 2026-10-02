#!/usr/bin/env bash
# On the Mac: copy the latest VPS backup into revision/data/backups/ (off-box copy, SPEC §10.5). Goes over Tailscale.
#   revision/deploy/pull-backup.sh [user@host]      (default elie@ml-vps)
# To make a fresh backup first: ssh elie@ml-vps 'sudo systemctl start revision-backup'
set -euo pipefail

HOST="${1:-elie@ml-vps}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/data/backups"
mkdir -p "$DEST"
latest=$(ssh "$HOST" 'ls -1 /var/lib/revision/backups/revision-*.db 2>/dev/null | sort | tail -n 1')
if [ -z "$latest" ]; then
  echo "no backup found on $HOST" >&2
  exit 1
fi
scp -q "$HOST:$latest" "$DEST/"
echo "→ $DEST/$(basename "$latest")"
