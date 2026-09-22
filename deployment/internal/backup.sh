#!/usr/bin/env bash
set -euo pipefail

# Run on the Docker host. The named volume is exported without requiring
# access to the host filesystem path used by Docker.
BACKUP_DIR="${BACKUP_DIR:-/var/backups/security-copilot}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

cid="$(docker compose -f /opt/security-copilot/deployment/internal/docker-compose.yml ps -q security-copilot)"
if [[ -z "$cid" ]]; then
  echo "ERROR: security-copilot container is not running" >&2
  exit 1
fi

docker exec "$cid" python -c 'import sqlite3; db="/opt/security-copilot/data/security-copilot.db"; src=sqlite3.connect(db); dst=sqlite3.connect("/tmp/security-copilot-backup.db"); src.backup(dst); dst.close(); src.close()'
docker cp "$cid:/tmp/security-copilot-backup.db" "$BACKUP_DIR/security-copilot-$STAMP.db"
docker exec "$cid" rm -f /tmp/security-copilot-backup.db

sha256sum "$BACKUP_DIR/security-copilot-$STAMP.db" > "$BACKUP_DIR/security-copilot-$STAMP.db.sha256"
echo "Backup created: $BACKUP_DIR/security-copilot-$STAMP.db"
