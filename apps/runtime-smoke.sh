#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-18080}"
python3 apps/server/server.py > /tmp/security-copilot-runtime.log 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/tmp/security-copilot-health.json 2>/dev/null; then
    grep -q '"status": "ok"' /tmp/security-copilot-health.json
    echo "PASS runtime health"
    exit 0
  fi
  sleep 1
done

echo "FAIL runtime health"
cat /tmp/security-copilot-runtime.log
exit 1
