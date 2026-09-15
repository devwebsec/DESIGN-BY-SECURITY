#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$ROOT/tests/security-design-pipeline"
SKILL_ARCHIVE="$ROOT/skills/security-copilot/security-copilot_v4.skill"

pass=0
fail=0

good() { printf 'PASS  %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL  %s\n' "$1"; fail=$((fail+1)); }

check_file() {
  local f="$1"
  [[ -f "$f" ]] && good "${f#$ROOT/}" || bad "${f#$ROOT/}"
}

check_contains() {
  local f="$1" pattern="$2" label
  label="${3:-${1#$ROOT/} contains [$2]}"
  if grep -Fq "$pattern" "$f"; then good "$label"; else bad "$label"; fi
}

run_tc() {
  local id="$1" file="$2"; shift 2
  local ok=1 pattern
  printf '\n--- %s ---\n' "$id"
  if [[ ! -f "$file" ]]; then
    bad "$id scenario file"
    printf 'TC RESULT: %s FAIL\n' "$id"
    return
  fi
  good "$id scenario file"
  for pattern in "$@"; do
    if grep -Fq "$pattern" "$file"; then
      good "$id: [$pattern]"
    else
      bad "$id: missing [$pattern]"
      ok=0
    fi
  done
  if (( ok )); then printf 'TC RESULT: %s PASS\n' "$id"; else printf 'TC RESULT: %s FAIL\n' "$id"; fi
}

printf '%s\n' '=== Security Design Pipeline Integration Test ==='
printf '%s\n' 'Repository contract: Design-by-Security ↔ Security Copilot v4'
printf '%s\n' ''

check_file "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md"
check_file "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md"
check_file "$ROOT/skills/security-copilot/security-copilot_v4.skill"
check_file "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md"
check_file "$ROOT/build-security-copilot.sh"
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" 'DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN'
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" 'Security Copilot'
check_contains "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" 'Detection-by-Design'

run_tc 'TC-001' "$TEST_DIR/TC-001-web-api.md" \
  'Trust boundaries' 'Attack surface' 'Critical attack path' 'Expected requirements' 'Expected controls' 'Security Copilot handoff'
run_tc 'TC-002' "$TEST_DIR/TC-002-identity-compromise.md" \
  'WHO→FROM WHERE→IDENTITY→RESOURCE→WHEN→PRIVILEGE→PURPOSE' 'blast radius' 'LATERAL MOVEMENT' 'Expected controls' 'Destructive actions require human approval' 'Security Copilot handoff'
run_tc 'TC-003' "$TEST_DIR/TC-003-supply-chain.md" \
  'SOURCE CODE → DEPENDENCIES → DEVELOPER → CI/CD → BUILD RUNNER → ARTIFACT → REGISTRY → DEPLOYMENT' 'malicious dependency' 'SBOM' 'provenance' 'artifact integrity/signing' 'Security Copilot handoff'
run_tc 'TC-004' "$TEST_DIR/TC-004-soc-feedback.md" \
  'DETECTION → TRIAGE → VALIDATION → CONTAINMENT → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN' 'root cause' 'security debt item' 'residual risk' 'redesign decision' 'Security Copilot handoff'

printf '\n--- Packaging gate ---\n'
if [[ -f "$SKILL_ARCHIVE" ]] && unzip -t "$SKILL_ARCHIVE" >/dev/null 2>&1; then
  good 'security-copilot_v4.skill archive integrity'
else
  bad 'security-copilot_v4.skill archive integrity (blocking integration gate)'
fi

printf '\nRESULT: %d passed, %d failed\n' "$pass" "$fail"
if (( fail > 0 )); then printf '%s\n' 'PIPELINE INTEGRATION: FAIL'; exit 1; fi
printf '%s\n' 'PIPELINE INTEGRATION: PASS'
