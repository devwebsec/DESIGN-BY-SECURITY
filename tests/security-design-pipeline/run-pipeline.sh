#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$ROOT/tests/security-design-pipeline"
SKILL_ARCHIVE="$ROOT/skills/security-copilot/security-copilot_v4.skill"

pass=0
fail=0

check_file() {
  local f="$1"
  if [[ -f "$f" ]]; then
    printf 'PASS  %s\n' "${f#$ROOT/}"
    pass=$((pass+1))
  else
    printf 'FAIL  %s\n' "${f#$ROOT/}"
    fail=$((fail+1))
  fi
}

check_contains() {
  local f="$1"; shift
  local pattern="$1"
  if grep -Fq "$pattern" "$f"; then
    printf 'PASS  %s contains [%s]\n' "${f#$ROOT/}" "$pattern"
    pass=$((pass+1))
  else
    printf 'FAIL  %s missing [%s]\n' "${f#$ROOT/}" "$pattern"
    fail=$((fail+1))
  fi
}

printf '%s\n' '=== Security Design Pipeline Integration Test ==='
printf '%s\n' 'Repository contract: Design-by-Security ↔ Security Copilot v4'
printf '%s\n' ''

check_file "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md"
check_file "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md"
check_file "$ROOT/skills/security-copilot/security-copilot_v4.skill"
check_file "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md"
check_file "$ROOT/build-security-copilot.sh"

for tc in TC-001-web-api.md TC-002-identity-compromise.md TC-003-supply-chain.md TC-004-soc-feedback.md; do
  check_file "$TEST_DIR/$tc"
done

if [[ -f "$SKILL_ARCHIVE" ]] && unzip -t "$SKILL_ARCHIVE" >/dev/null 2>&1; then
  printf 'PASS  security-copilot_v4.skill archive integrity\n'
  pass=$((pass+1))
else
  printf 'FAIL  security-copilot_v4.skill archive integrity\n'
  fail=$((fail+1))
fi

check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" 'DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN'
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" 'Security Copilot'
check_contains "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" 'Detection-by-Design'
check_contains "$TEST_DIR/TC-004-soc-feedback.md" 'SECURITY DEBT'

printf '%s\n' ''
printf 'RESULT: %d passed, %d failed\n' "$pass" "$fail"

if (( fail > 0 )); then
  exit 1
fi

printf '%s\n' 'PIPELINE INTEGRATION: PASS'
