#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REG="$ROOT/regulations"
ART="$ROOT/artifacts"
MAP="$ROOT/GOST-MAPPING.yml"

pass=0
fail=0
check_file() {
  local f="$1"
  if [[ -s "$f" ]]; then
    printf 'PASS  %s\n' "${f#"$ROOT/"}"
    pass=$((pass+1))
  else
    printf 'FAIL  %s\n' "${f#"$ROOT/"}" >&2
    fail=$((fail+1))
  fi
}

check_contains() {
  local f="$1" pattern="$2" label="$3"
  if grep -Fq "$pattern" "$f"; then
    printf 'PASS  %s\n' "$label"
    pass=$((pass+1))
  else
    printf 'FAIL  %s\n' "$label" >&2
    fail=$((fail+1))
  fi
}

check_file "$ROOT/GOST-OVERVIEW.md"
check_file "$MAP"

for n in $(seq -w 1 25); do
  matches=("$REG/${n}-"*.md)
  if [[ -f "${matches[0]}" ]]; then
    check_file "${matches[0]}"
  else
    printf 'FAIL  missing regulation %s\n' "$n" >&2
    fail=$((fail+1))
  fi
done

artifacts=(
  requirements-registry.yml defects-registry.yml training-log.yml
  configuration-items.yml dependencies-inventory.yml suppliers-registry.yml
  fuzzing-targets.yml secrets-inventory.yml sast-tools.yml build-tools.yml
  dynamic-analysis.yml secure-build.yml code-review-log.yml decommission-plan.yml planning-status-analysis.yml
)
for f in "${artifacts[@]}"; do check_file "$ART/$f"; done

# Contract sanity: exactly 25 process IDs and 25 mapping entries.
process_count=$(grep -Ec '^  - id: "5\.[0-9]+"$' "$MAP" || true)
artifact_count=$(grep -Ec '^    artifact:' "$MAP" || true)
[[ "$process_count" -eq 25 ]] || { echo "FAIL  expected 25 mapped processes, got $process_count" >&2; fail=$((fail+1)); }
[[ "$artifact_count" -eq 25 ]] || { echo "FAIL  expected 25 artifact mapping entries, got $artifact_count" >&2; fail=$((fail+1)); }

# 5.11.3 implementation contract.
check_contains "$REG/11-dynamic-analysis.md" "## 2. Roles and responsibilities" "5.11 roles and responsibilities"
check_contains "$REG/11-dynamic-analysis.md" "## 3. Tool and method selection" "5.11 tool/method selection"
check_contains "$REG/11-dynamic-analysis.md" "## 4. Module selection" "5.11 module selection"
check_contains "$REG/11-dynamic-analysis.md" "## 5. Test scenarios" "5.11 test scenarios"
check_contains "$REG/11-dynamic-analysis.md" "## 6. Failure handling and remediation" "5.11 failure handling/remediation"
check_contains "$REG/11-dynamic-analysis.md" "## 7. Periodicity and repeat analysis" "5.11 periodicity/retest"
check_contains "$REG/11-dynamic-analysis.md" "## 8. Reports" "5.11 dynamic-analysis reports"
check_contains "$REG/11-dynamic-analysis.md" "## 9. Fuzzing reports" "5.11 fuzzing reports"
check_contains "$ART/dynamic-analysis.yml" "tool_selection_criteria:" "dynamic-analysis artifact tool criteria"
check_contains "$ART/dynamic-analysis.yml" "failure_handling:" "dynamic-analysis artifact failure handling"
check_contains "$ART/fuzzing-targets.yml" "duration_seconds" "fuzzing duration evidence"
check_contains "$ART/fuzzing-targets.yml" "unique_paths" "fuzzing unique-path evidence"
check_contains "$ART/fuzzing-targets.yml" "analyzed_crashes" "fuzzing crash-analysis evidence"

# 5.12.2 implementation contract.
check_contains "$REG/12-build.md" "## 2. Required build regulation" "5.12 build regulation"
check_contains "$REG/12-build.md" "## 3. Build system and environment" "5.12 build system/environment"
check_contains "$REG/12-build.md" "## 4. Transformation control" "5.12 transformation control"
check_contains "$ART/secure-build.yml" "source_revision_required: true" "secure-build source revision"
check_contains "$ART/secure-build.yml" "artifact_digest" "secure-build artifact digest"
check_contains "$ART/secure-build.yml" "provenance" "secure-build provenance"
check_contains "$ART/build-tools.yml" "runner_image" "build environment runner image"

# Cross-reference the repository reference design. A missing reference is a validation failure, not a skipped check.
EXAMPLE="$ROOT/../examples/web-api/security-design.yaml"
if [[ ! -f "$EXAMPLE" ]]; then
  echo "FAIL  missing reference design: $EXAMPLE" >&2
  fail=$((fail+1))
elif grep -q '^  - id: R-001$' "$EXAMPLE" && grep -q '^    requirement: R-001$' "$EXAMPLE"; then
  echo 'PASS  reference requirement/control/validation chain R-001'
  pass=$((pass+1))
else
  echo 'FAIL  broken reference requirement/control/validation chain' >&2
  fail=$((fail+1))
fi

# Reference design must expose the new contract blocks.
for section in dynamic_analysis fuzzing secure_build evidence; do
  check_contains "$EXAMPLE" "${section}:" "reference design section: $section"
done

printf '\nLEVEL 8 RESULT: %d passed, %d failed\n' "$pass" "$fail"
(( fail == 0 ))
