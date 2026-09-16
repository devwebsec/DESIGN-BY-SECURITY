#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$ROOT/tests/security-design-pipeline"
SKILL_ARCHIVE="$ROOT/skills/security-copilot/security-copilot_v4.skill"
MANIFEST="$TEST_DIR/pipeline-manifest.yml"
FIXTURE="$TEST_DIR/fixtures/expected-artifact-contract.md"

pass=0
fail=0

cleanup() {
  [[ -n "${BUILD_TMP:-}" && -d "$BUILD_TMP" ]] && rm -rf "$BUILD_TMP"
}
trap cleanup EXIT

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
check_file "$MANIFEST"
check_file "$FIXTURE"
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" 'DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN'
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" 'Security Copilot'
check_contains "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" 'Detection-by-Design'

printf '\n--- Manifest / artifact contract ---\n'
for artifact in intent architecture assets data_flows trust_boundaries threat_model attack_paths security_requirements controls validation security_gate operational_handoff lessons_learned redesign; do
  check_contains "$MANIFEST" "  - $artifact" "manifest required artifact: $artifact"
done
for hard_fail in critical_threat_without_requirement requirement_without_validation critical_attack_path_without_detection_or_explicit_gap unresolved_critical_design_flaw unknown_presented_as_evidence destructive_action_without_human_approval incident_closed_without_root_cause_feedback; do
  check_contains "$MANIFEST" "  - $hard_fail" "manifest hard-fail: $hard_fail"
done
for stage in Intent Design Asset Data Threat Attack Requirements Controls Validate Gate Operate Learn Redesign; do
  check_contains "$FIXTURE" "| $stage |" "artifact contract stage: $stage"
done

run_tc 'TC-001' "$TEST_DIR/TC-001-web-api.md" \
  'Trust boundaries' 'Attack surface' 'Critical attack path' 'Expected requirements' 'Expected controls' 'Security Copilot handoff'
run_tc 'TC-002' "$TEST_DIR/TC-002-identity-compromise.md" \
  'WHO→FROM WHERE→IDENTITY→RESOURCE→WHEN→PRIVILEGE→PURPOSE' 'blast radius' 'LATERAL MOVEMENT' 'Expected controls' 'Destructive actions require human approval' 'Security Copilot handoff'
run_tc 'TC-003' "$TEST_DIR/TC-003-supply-chain.md" \
  'SOURCE CODE → DEPENDENCIES → DEVELOPER → CI/CD → BUILD RUNNER → ARTIFACT → REGISTRY → DEPLOYMENT' 'malicious dependency' 'SBOM' 'provenance' 'artifact integrity/signing' 'Security Copilot handoff'
run_tc 'TC-004' "$TEST_DIR/TC-004-soc-feedback.md" \
  'DETECTION → TRIAGE → VALIDATION → CONTAINMENT → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN' 'root cause' 'security debt item' 'residual risk' 'redesign decision' 'Security Copilot handoff'

printf '\n--- Packaging / builder gate ---\n'
if [[ -f "$SKILL_ARCHIVE" ]] && unzip -t "$SKILL_ARCHIVE" >/dev/null 2>&1; then
  good 'security-copilot_v4.skill archive integrity'
else
  bad 'security-copilot_v4.skill archive integrity (blocking integration gate)'
fi

if bash -n "$ROOT/build-security-copilot.sh"; then
  good 'build-security-copilot.sh syntax'
else
  bad 'build-security-copilot.sh syntax'
fi

BUILD_TMP="$(mktemp -d)"
if (cd "$ROOT" && SECURITY_COPILOT_SKILL_ARCHIVE="$SKILL_ARCHIVE" bash build-security-copilot.sh "$BUILD_TMP/package"); then
  good 'builder execution'
else
  bad 'builder execution'
fi
if [[ -f "$BUILD_TMP/package.zip" ]] && unzip -t "$BUILD_TMP/package.zip" >/dev/null 2>&1; then
  good 'generated package integrity'
else
  bad 'generated package integrity'
fi
if [[ -f "$BUILD_TMP/package/SKILL.md" ]]; then
  good 'generated package contains SKILL.md'
else
  bad 'generated package contains SKILL.md'
fi
if [[ -f "$BUILD_TMP/package/integrations/README.md" ]]; then
  good 'generated package contains integration README'
else
  bad 'generated package contains integration README'
fi

printf '\nRESULT: %d passed, %d failed\n' "$pass" "$fail"
if (( fail > 0 )); then printf '%s\n' 'PIPELINE INTEGRATION: FAIL'; exit 1; fi
printf '%s\n' 'PIPELINE INTEGRATION: PASS'
