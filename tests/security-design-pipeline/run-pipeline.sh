#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$ROOT/tests/security-design-pipeline"
SKILL_ARCHIVE="$ROOT/skills/security-copilot/security-copilot_v4.skill"
MANIFEST="$TEST_DIR/pipeline-manifest.yml"
FIXTURE="$TEST_DIR/fixtures/expected-artifact-contract.md"
SEMANTIC_EVAL="$TEST_DIR/semantic/evaluate.py"
MUTATION_EVAL="$TEST_DIR/semantic/mutate.py"
FUZZ_EVAL="$TEST_DIR/semantic/fuzz.py"
SEMANTIC_VALID="$TEST_DIR/semantic/fixtures/valid-web-api.json"
SEMANTIC_NEGATIVE="$TEST_DIR/semantic/fixtures/negative"
GRAPH_ADAPTER="$TEST_DIR/graph/from_semantic.py"
GRAPH_ENGINE="$TEST_DIR/graph/verify_graph.py"
GRAPH_VALID="$TEST_DIR/graph/valid-graph.json"
GRAPH_MUTATION="$TEST_DIR/graph/mutation-tests.py"

pass=0
fail=0
BUILD_TMP=""
GRAPH_TMP=""
cleanup() {
  [[ -n "$BUILD_TMP" && -d "$BUILD_TMP" ]] && rm -rf -- "$BUILD_TMP"
  [[ -n "$GRAPH_TMP" && -f "$GRAPH_TMP" ]] && rm -f -- "$GRAPH_TMP"
}
trap cleanup EXIT

good(){ printf 'PASS  %s\n' "$1"; pass=$((pass+1)); }
bad(){ printf 'FAIL  %s\n' "$1"; fail=$((fail+1)); }
check_file(){ [[ -f "$1" ]] && good "${1#$ROOT/}" || bad "${1#$ROOT/}"; }
check_dir(){ [[ -d "$1" ]] && good "${1#$ROOT/}" || bad "${1#$ROOT/}"; }
check_contains(){ local f="$1" p="$2" label="${3:-${1#$ROOT/} contains [$2]}"; grep -Fq "$p" "$f" && good "$label" || bad "$label"; }
run_tc(){
  local id="$1" file="$2"; shift 2; local ok=1 p
  printf '\n--- %s ---\n' "$id"
  if [[ ! -f "$file" ]]; then bad "$id scenario file"; printf 'TC RESULT: %s FAIL\n' "$id"; return; fi
  good "$id scenario file"
  for p in "$@"; do grep -Fq "$p" "$file" && good "$id: [$p]" || { bad "$id: missing [$p]"; ok=0; }; done
  (( ok )) && printf 'TC RESULT: %s PASS\n' "$id" || printf 'TC RESULT: %s FAIL\n' "$id"
}

printf '%s\n' '=== Security Design Pipeline Integration Test ==='
printf '%s\n\n' 'Repository contract: Design-by-Security ↔ Security Copilot v4'

for f in "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" "$ROOT/skills/security-copilot/security-copilot_v4.skill" "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" "$ROOT/build-security-copilot.sh" "$MANIFEST" "$FIXTURE" "$SEMANTIC_EVAL" "$MUTATION_EVAL" "$FUZZ_EVAL" "$SEMANTIC_VALID" "$GRAPH_ADAPTER" "$GRAPH_ENGINE" "$GRAPH_VALID" "$GRAPH_MUTATION"; do check_file "$f"; done
check_dir "$SEMANTIC_NEGATIVE"
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-PROMPT.md" 'DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN'
check_contains "$ROOT/design-by-security/DESIGN-BY-SECURITY-ADAPTER.md" 'Security Copilot'
check_contains "$ROOT/skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" 'Detection-by-Design'

printf '\n--- Manifest / artifact contract ---\n'
for artifact in intent architecture assets data_flows trust_boundaries threat_model attack_paths security_requirements controls validation security_gate operational_handoff lessons_learned redesign; do check_contains "$MANIFEST" "  - $artifact" "manifest required artifact: $artifact"; done
for hard_fail in critical_threat_without_requirement requirement_without_validation critical_attack_path_without_detection_or_explicit_gap unresolved_critical_design_flaw unknown_presented_as_evidence destructive_action_without_human_approval incident_closed_without_root_cause_feedback; do check_contains "$MANIFEST" "  - $hard_fail" "manifest hard-fail: $hard_fail"; done
for stage in Intent Design Asset Data Threat Attack Requirements Controls Validate Gate Operate Learn Redesign; do check_contains "$FIXTURE" "| $stage |" "artifact contract stage: $stage"; done

# The manifest is intentionally JSON-compatible YAML. Verify the actual canonical
# semantic artifact contains every manifest artifact, not merely the words in the manifest.
if python3 - "$MANIFEST" "$SEMANTIC_VALID" <<'PY'
import json,sys
manifest=json.load(open(sys.argv[1],encoding='utf-8'))
artifact=json.load(open(sys.argv[2],encoding='utf-8'))
missing=[]
for key in manifest['required_artifacts']:
    actual='validations' if key=='validation' else key
    if actual not in artifact:
        missing.append(key)
if missing:
    raise SystemExit('missing canonical artifact fields: '+', '.join(missing))
PY
then good 'canonical artifact satisfies manifest required_artifacts'; else bad 'canonical artifact satisfies manifest required_artifacts'; fi

run_tc 'TC-001' "$TEST_DIR/TC-001-web-api.md" 'Trust boundaries' 'Attack surface' 'Critical attack path' 'Expected requirements' 'Expected controls' 'Security Copilot handoff'
run_tc 'TC-002' "$TEST_DIR/TC-002-identity-compromise.md" 'WHO→FROM WHERE→IDENTITY→RESOURCE→WHEN→PRIVILEGE→PURPOSE' 'blast radius' 'LATERAL MOVEMENT' 'Expected controls' 'Destructive actions require human approval' 'Security Copilot handoff'
run_tc 'TC-003' "$TEST_DIR/TC-003-supply-chain.md" 'SOURCE CODE → DEPENDENCIES → DEVELOPER → CI/CD → BUILD RUNNER → ARTIFACT → REGISTRY → DEPLOYMENT' 'malicious dependency' 'SBOM' 'provenance' 'artifact integrity/signing' 'Security Copilot handoff'
run_tc 'TC-004' "$TEST_DIR/TC-004-soc-feedback.md" 'DETECTION → TRIAGE → VALIDATION → CONTAINMENT → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN' 'root cause' 'security debt item' 'residual risk' 'redesign decision' 'Security Copilot handoff'

printf '\n--- Level 4 semantic security design evaluation ---\n'
if python3 "$SEMANTIC_EVAL" "$SEMANTIC_VALID" "$SEMANTIC_NEGATIVE"; then good 'Level 4 semantic relationship validation'; else bad 'Level 4 semantic relationship validation'; fi

printf '\n--- Level 5+ mutation / metamorphic evaluation ---\n'
if python3 "$MUTATION_EVAL" "$SEMANTIC_VALID"; then good 'Level 5+ adversarial mutation rejection'; good 'Level 5+ metamorphic invariants'; else bad 'Level 5+ mutation / metamorphic evaluation'; fi

printf '\n--- Level 6 property / graph fuzzing ---\n'
if python3 "$FUZZ_EVAL" "$SEMANTIC_VALID" 100; then good 'Level 6 bounded graph/property fuzzing'; else bad 'Level 6 bounded graph/property fuzzing'; fi

printf '\n--- Level 7 Security Graph Invariant Engine ---\n'
GRAPH_TMP="$(mktemp)"
if python3 "$GRAPH_ADAPTER" "$SEMANTIC_VALID" "$GRAPH_TMP" && python3 "$GRAPH_ENGINE" "$GRAPH_TMP"; then good 'Level 7 canonical graph verification'; else bad 'Level 7 canonical graph verification'; fi
if python3 "$GRAPH_ENGINE" "$GRAPH_VALID" >/dev/null; then good 'Level 7 reference graph verification'; else bad 'Level 7 reference graph verification'; fi
if python3 "$GRAPH_MUTATION"; then good 'Level 7 invariant mutation rejection'; else bad 'Level 7 invariant mutation rejection'; fi

printf '\n--- Packaging / builder gate ---\n'
if [[ -f "$SKILL_ARCHIVE" ]] && unzip -t "$SKILL_ARCHIVE" >/dev/null 2>&1; then good 'security-copilot_v4.skill archive integrity'; else bad 'security-copilot_v4.skill archive integrity (blocking integration gate)'; fi
if bash -n "$ROOT/build-security-copilot.sh"; then good 'build-security-copilot.sh syntax'; else bad 'build-security-copilot.sh syntax'; fi
BUILD_TMP="$(mktemp -d)"
if (cd "$ROOT" && SECURITY_COPILOT_SKILL_ARCHIVE="$SKILL_ARCHIVE" bash build-security-copilot.sh "$BUILD_TMP/package"); then good 'builder execution'; else bad 'builder execution'; fi
[[ -f "$BUILD_TMP/package.zip" ]] && unzip -t "$BUILD_TMP/package.zip" >/dev/null 2>&1 && good 'generated package integrity' || bad 'generated package integrity'
[[ -f "$BUILD_TMP/package/SKILL.md" ]] && good 'generated package contains SKILL.md' || bad 'generated package contains SKILL.md'
[[ -f "$BUILD_TMP/package/integrations/README.md" ]] && good 'generated package contains integration README' || bad 'generated package contains integration README'

printf '\nRESULT: %d passed, %d failed\n' "$pass" "$fail"
if (( fail > 0 )); then printf '%s\n' 'PIPELINE INTEGRATION: FAIL'; exit 1; fi
printf '%s\n' 'PIPELINE INTEGRATION: PASS'
