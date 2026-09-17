#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────
# Security Design Pipeline Integration Test
#
# ИСТОРИЯ ИЗМЕНЕНИЙ
# v1 → v2:
#   [FIX-1] Добавлена функция check_dir() для проверки директорий.
#   [FIX-2] check_file "$SEMANTIC_NEGATIVE" → check_dir "$SEMANTIC_NEGATIVE"
#           (SEMANTIC_NEGATIVE — директория, check_file использует -f
#            и всегда возвращал FAIL, хотя evaluate.py обрабатывал её
#            корректно).
#   [FIX-3] Level 6 запускает $FUZZ_EVAL, а не $SEMANTIC_EVAL.
#           Ранее на Level 6 по ошибке вызывался evaluate.py с аргументом
#           100, что давало "FAIL no negative fixtures" — evaluate.py
#           воспринимал "100" как путь к директории фикстур и не находил
#           *.json.
# ─────────────────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$ROOT/tests/security-design-pipeline"
SKILL_ARCHIVE="$ROOT/skills/security-copilot/security-copilot_v4.skill"
MANIFEST="$TEST_DIR/pipeline-manifest.yml"
FIXTURE="$TEST_DIR/fixtures/expected-artifact-contract.md"
SEMANTIC_EVAL="$TEST_DIR/semantic/evaluate.py"
NEGATIVE_GEN="$TEST_DIR/semantic/generate-negative-fixtures.py"
MUTATION_EVAL="$TEST_DIR/semantic/mutate.py"
FUZZ_EVAL="$TEST_DIR/semantic/fuzz.py"
SEMANTIC_VALID="$TEST_DIR/semantic/fixtures/valid-web-api.json"
SEMANTIC_NEGATIVE="$TEST_DIR/semantic/fixtures/negative"
GRAPH_ENGINE="$TEST_DIR/graph/verify_graph.py"
GRAPH_VALID="$TEST_DIR/graph/valid-graph.json"
GRAPH_MUTATION="$TEST_DIR/graph/mutation-tests.py"

pass=0
fail=0
BUILD_TMP=""
cleanup() { [[ -n "$BUILD_TMP" && -d "$BUILD_TMP" ]] && rm -rf "$BUILD_TMP"; }
trap cleanup EXIT

good() { printf 'PASS  %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf 'FAIL  %s\n' "$1"; fail=$((fail+1)); }

check_file() {
  local f="$1"
  [[ -f "$f" ]] && good "${f#$ROOT/}" || bad "${f#$ROOT/}"
}

# [FIX-1] Проверка директорий (для fixtures/negative).
check_dir() {
  local d="$1"
  [[ -d "$d" ]] && good "${d#$ROOT/}" || bad "${d#$ROOT/}"
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
  if [[ ! -f "$file" ]]; then bad "$id scenario file"; printf 'TC RESULT: %s FAIL\n' "$id"; return; fi
  good "$id scenario file"
  for p in "$@"; do grep -Fq "$p" "$file" && good "$id: [$p]" || { bad "$id: missing [$p]"; ok=0; }; done
  (( ok )) && printf 'TC RESULT: %s PASS\n' "$id" || printf 'TC RESULT: %s FAIL\n' "$id"
}

printf '%s\n' '=== Security Design Pipeline Integration Test ==='
printf '%s\n\n' 'Repository contract: Design-by-Security ↔ Security Copilot v4'

for f in "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" "$ROOT/skills/security-copilot/security-copilot_v4.skill" "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" "$ROOT/build-security-copilot.sh" "$MANIFEST" "$FIXTURE" "$SEMANTIC_EVAL" "$NEGATIVE_GEN" "$MUTATION_EVAL" "$FUZZ_EVAL" "$SEMANTIC_VALID" "$GRAPH_ENGINE" "$GRAPH_VALID" "$GRAPH_MUTATION"; do check_file "$f"; done
check_dir "$SEMANTIC_NEGATIVE"
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" 'DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN'
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" 'Security Copilot'
check_contains "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" 'Detection-by-Design'

printf '\n--- Manifest / artifact contract ---\n'
for artifact in intent architecture assets data_flows trust_boundaries threat_model attack_paths security_requirements controls validation security_gate operational_handoff lessons_learned redesign; do check_contains "$MANIFEST" "  - $artifact" "manifest required artifact: $artifact"; done
for hard_fail in critical_threat_without_requirement requirement_without_validation critical_attack_path_without_detection_or_explicit_gap unresolved_critical_design_flaw unknown_presented_as_evidence destructive_action_without_human_approval incident_closed_without_root_cause_feedback; do check_contains "$MANIFEST" "  - $hard_fail" "manifest hard-fail: $hard_fail"; done
for stage in Intent Design Asset Data Threat Attack Requirements Controls Validate Gate Operate Learn Redesign; do check_contains "$FIXTURE" "| $stage |" "artifact contract stage: $stage"; done

run_tc 'TC-001' "$TEST_DIR/TC-001-web-api.md" 'Trust boundaries' 'Attack surface' 'Critical attack path' 'Expected requirements' 'Expected controls' 'Security Copilot handoff'
run_tc 'TC-002' "$TEST_DIR/TC-002-identity-compromise.md" 'WHO→FROM WHERE→IDENTITY→RESOURCE→WHEN→PRIVILEGE→PURPOSE' 'blast radius' 'LATERAL MOVEMENT' 'Expected controls' 'Destructive actions require human approval' 'Security Copilot handoff'
run_tc 'TC-003' "$TEST_DIR/TC-003-supply-chain.md" 'SOURCE CODE → DEPENDENCIES → DEVELOPER → CI/CD → BUILD RUNNER → ARTIFACT → REGISTRY → DEPLOYMENT' 'malicious dependency' 'SBOM' 'provenance' 'artifact integrity/signing' 'Security Copilot handoff'
run_tc 'TC-004' "$TEST_DIR/TC-004-soc-feedback.md" 'DETECTION → TRIAGE → VALIDATION → CONTAINMENT → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN' 'root cause' 'security debt item' 'residual risk' 'redesign decision' 'Security Copilot handoff'

printf '\n--- Level 4 semantic security design evaluation ---\n'
mkdir -p "$SEMANTIC_NEGATIVE"
rm -f "$SEMANTIC_NEGATIVE"/*.json
if python3 "$NEGATIVE_GEN" "$SEMANTIC_VALID" "$SEMANTIC_NEGATIVE" && python3 "$SEMANTIC_EVAL" "$SEMANTIC_VALID" "$SEMANTIC_NEGATIVE"; then good 'Level 4 semantic relationship validation'; else bad 'Level 4 semantic relationship validation'; fi

printf '\n--- Level 5+ mutation / metamorphic evaluation ---\n'
if python3 "$MUTATION_EVAL" "$SEMANTIC_VALID"; then good 'Level 5+ adversarial mutation rejection'; good 'Level 5+ metamorphic invariants'; else bad 'Level 5+ mutation / metamorphic evaluation'; fi

printf '\n--- Level 6 property / graph fuzzing ---\n'
# [FIX-3] Level 6 запускает $FUZZ_EVAL (не $SEMANTIC_EVAL).
if python3 "$FUZZ_EVAL" "$SEMANTIC_VALID" 100; then
  good 'Level 6 bounded graph/property fuzzing'
else
  bad 'Level 6 bounded graph/property fuzzing'
fi

printf '\n--- Level 7 Security Graph Invariant Engine ---\n'
if python3 "$GRAPH_ENGINE" "$GRAPH_VALID" --report "$TEST_DIR/graph/level7-report.json"; then good 'Level 7 graph invariant verification'; else bad 'Level 7 graph invariant verification'; fi
if python3 "$GRAPH_MUTATION"; then good 'Level 7 invariant mutation rejection'; else bad 'Level 7 invariant mutation rejection'; fi

printf '\n--- Packaging / builder gate ---\n'
if [[ -f "$SKILL_ARCHIVE" ]] && unzip -t "$SKILL_ARCHIVE" >/dev/null 2>&1; then good 'security-copilot_v4.skill archive integrity'; else bad 'security-copilot_v4.skill archive integrity (blocking integration gate)'; fi
bash -n "$ROOT/build-security-copilot.sh" && good 'build-security-copilot.sh syntax' || bad 'build-security-copilot.sh syntax'
BUILD_TMP="$(mktemp -d)"
if (cd "$ROOT" && SECURITY_COPILOT_SKILL_ARCHIVE="$SKILL_ARCHIVE" bash build-security-copilot.sh "$BUILD_TMP/package"); then good 'builder execution'; else bad 'builder execution'; fi
[[ -f "$BUILD_TMP/package.zip" ]] && unzip -t "$BUILD_TMP/package.zip" >/dev/null 2>&1 && good 'generated package integrity' || bad 'generated package integrity'
[[ -f "$BUILD_TMP/package/SKILL.md" ]] && good 'generated package contains SKILL.md' || bad 'generated package contains SKILL.md'
[[ -f "$BUILD_TMP/package/integrations/README.md" ]] && good 'generated package contains integration README' || bad 'generated package contains integration README'

printf '\nRESULT: %d passed, %d failed\n' "$pass" "$fail"
if (( fail > 0 )); then printf '%s\n' 'PIPELINE INTEGRATION: FAIL'; exit 1; fi
printf '%s\n' 'PIPELINE INTEGRATION: PASS'