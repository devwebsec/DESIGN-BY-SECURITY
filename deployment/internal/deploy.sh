#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/deployment/internal"

if [[ ! -f .env ]]; then
  echo "ERROR: deployment/internal/.env is missing" >&2
  echo "Copy .env.example to .env and set SECURITY_COPILOT_API_TOKEN." >&2
  exit 1
fi

set -a
. ./.env
set +a

: "${SECURITY_COPILOT_API_TOKEN:?SECURITY_COPILOT_API_TOKEN must be set}"

# Build and start the complete internal stack. The gateway only starts after
# the API healthcheck reports healthy.
docker compose --env-file .env up -d --build

echo "Waiting for API health..."
for _ in $(seq 1 30); do
  if docker compose --env-file .env ps --status running security-copilot | grep -q security-copilot; then
    if docker compose --env-file .env exec -T security-copilot python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=2)' >/dev/null 2>&1; then
      echo "Security Copilot API: healthy"
      docker compose --env-file .env ps
      exit 0
    fi
  fi
  sleep 2
done

echo "ERROR: Security Copilot API did not become healthy" >&2
docker compose --env-file .env logs --tail=100 security-copilot gateway >&2
exit 1
