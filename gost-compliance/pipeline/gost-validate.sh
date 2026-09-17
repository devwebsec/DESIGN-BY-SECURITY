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
  code-review-log.yml decommission-plan.yml planning-status-analysis.yml
)
for f in "${artifacts[@]}"; do check_file "$ART/$f"; done

# Contract sanity: exactly 25 process IDs and 25 mapping entries.
process_count=$(grep -Ec '^  - id: "5\.[0-9]+"$' "$MAP" || true)
artifact_count=$(grep -Ec '^    artifact:' "$MAP" || true)
[[ "$process_count" -eq 25 ]] || { echo "FAIL  expected 25 mapped processes, got $process_count" >&2; fail=$((fail+1)); }
[[ "$artifact_count" -eq 25 ]] || { echo "FAIL  expected 25 artifact mapping entries, got $artifact_count" >&2; fail=$((fail+1)); }

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

printf '\nLEVEL 8 RESULT: %d passed, %d failed\n' "$pass" "$fail"
(( fail == 0 ))
