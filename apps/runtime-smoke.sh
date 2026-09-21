#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-18080}"
DB="$(mktemp /tmp/security-copilot-db.XXXXXX)"
rm -f "$DB"
export SECURITY_COPILOT_DB="$DB"
python3 apps/server/server.py > /tmp/security-copilot-runtime.log 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true; rm -f "$DB"' EXIT

for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/tmp/security-copilot-health.json 2>/dev/null; then
    grep -q '"status": "ok"' /tmp/security-copilot-health.json
    echo "PASS runtime health"
    break
  fi
  sleep 1
done

if ! kill -0 "$PID" 2>/dev/null; then
  echo "FAIL runtime process stopped"
  cat /tmp/security-copilot-runtime.log
  exit 1
fi

CREATE=$(curl -fsS -X POST "http://127.0.0.1:${PORT}/api/v1/projects" \
  -H 'Content-Type: application/json' \
  --data-binary @- <<'JSON'
{"name":"smoke-web-api-pass","artifact":{"intent":{"id":"INT-001"},"assets":[{"id":"A-001"}],"trust_boundaries":[],"threats":[],"attack_paths":[],"security_requirements":[],"controls":[],"detections":[],"validations":[],"security_gate":{"decision":"PASS","unresolved_critical_design_flaws":[],"unknowns":[]},"operational_handoff":{"response_owner":"SOC","human_approval_required_for_destructive_actions":true},"lessons_learned":[],"redesign":[]}}
JSON
)
PROJECT_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$CREATE")
ANALYSIS=$(curl -fsS -X POST "http://127.0.0.1:${PORT}/api/v1/projects/${PROJECT_ID}/analyze")
grep -q '"status": "PASS"' <<<"$ANALYSIS"
echo "PASS runtime API create/analyze PASS boundary"

FAIL_CREATE=$(curl -fsS -X POST "http://127.0.0.1:${PORT}/api/v1/projects" \
  -H 'Content-Type: application/json' \
  --data-binary @- <<'JSON'
{"name":"smoke-web-api-fail","artifact":{"intent":{"id":"INT-002"},"assets":[{"id":"A-002"}],"trust_boundaries":[],"threats":[{"id":"T-002","severity":"critical","asset_ids":["A-002"]}],"attack_paths":[],"security_requirements":[],"controls":[],"detections":[],"validations":[],"security_gate":{"decision":"PASS","unresolved_critical_design_flaws":[],"unknowns":[]},"operational_handoff":{"response_owner":"SOC","human_approval_required_for_destructive_actions":true},"lessons_learned":[],"redesign":[]}}
JSON
)
FAIL_PROJECT_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$FAIL_CREATE")
FAIL_ANALYSIS=$(curl -fsS -X POST "http://127.0.0.1:${PORT}/api/v1/projects/${FAIL_PROJECT_ID}/analyze")
grep -q '"status": "FAIL"' <<<"$FAIL_ANALYSIS"
echo "PASS runtime API create/analyze FAIL boundary"
