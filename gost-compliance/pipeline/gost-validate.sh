#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REG="$ROOT/regulations"
ART="$ROOT/artifacts"
MAP="$ROOT/GOST-MAPPING.yml"
OVERVIEW="$ROOT/GOST-OVERVIEW.md"

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

check_file "$OVERVIEW"
check_file "$MAP"
check_file "$REG/FSTEC-117-P50.md"
check_contains "$OVERVIEW" "ГОСТ Р 56939-2024 §§4–5" "GOST sections 4–5 boundary"
check_contains "$OVERVIEW" "5.25" "complete 25-process catalogue"
check_contains "$REG/FSTEC-117-P50.md" "пункт 50" "FSTEC №117 p.50 traceability"
check_contains "$REG/FSTEC-117-P50.md" "sections 4 and 5" "FSTEC p.50 sections 4 and 5"

# Exact process identity from the supplied GOST R 56939-2024 text.
python3 - "$MAP" "$REG" "$ART" <<'PY'
import re
import sys
from pathlib import Path

mapping, reg, art = map(Path, sys.argv[1:])
text = mapping.read_text(encoding='utf-8')

expected = {
    '5.1': ('planning', 'planning-status-analysis.yml'),
    '5.2': ('training', 'training-log.yml'),
    '5.3': ('security-requirements', 'requirements-registry.yml'),
    '5.4': ('configuration-management', 'configuration-items.yml'),
    '5.5': ('deficiency-management', 'defects-registry.yml'),
    '5.6': ('architecture', 'architecture.yml'),
    '5.7': ('threat-modeling', 'threat-model.yml'),
    '5.8': ('coding-rules', 'coding-rules.yml'),
    '5.9': ('code-review', 'code-review-log.yml'),
    '5.10': ('static-analysis', 'sast-tools.yml'),
    '5.11': ('dynamic-analysis', 'dynamic-analysis.yml'),
    '5.12': ('secure-build', 'secure-build.yml'),
    '5.13': ('build-environment-security', 'build-tools.yml'),
    '5.14': ('source-code-access-integrity', 'source-code-access.yml'),
    '5.15': ('secrets-security', 'secrets-inventory.yml'),
    '5.16': ('composition-analysis', 'dependencies-inventory.yml'),
    '5.17': ('supply-chain-malware-check', 'suppliers-registry.yml'),
    '5.18': ('functional-testing', 'functional-testing.yml'),
    '5.19': ('nonfunctional-testing', 'nonfunctional-testing.yml'),
    '5.20': ('release-security', 'release-security.yml'),
    '5.21': ('secure-delivery', 'secure-delivery.yml'),
    '5.22': ('support', 'support.yml'),
    '5.23': ('vulnerability-response', 'vulnerability-response.yml'),
    '5.24': ('vulnerability-search', 'vulnerability-search.yml'),
    '5.25': ('decommissioning', 'decommission-plan.yml'),
}

ids = re.findall(r'^  - id: "(5\.\d+)"$', text, re.M)
if ids != list(expected):
    raise SystemExit(f'process ID/order mismatch: {ids!r}')

blocks = re.split(r'(?=^  - id: "5\.\d+"$)', text, flags=re.M)
for block in blocks:
    m = re.search(r'^  - id: "(5\.\d+)"$.*?^    name: ([^\n]+)$.*?^    artifact: ([^\n]+)$', block, re.M | re.S)
    if not m:
        continue
    pid, name, artifact = m.groups()
    exp_name, exp_artifact = expected[pid]
    if name != exp_name or artifact != exp_artifact:
        raise SystemExit(f'{pid}: expected {exp_name}/{exp_artifact}, got {name}/{artifact}')
    artifact_path = art / artifact
    if not artifact_path.is_file() or artifact_path.stat().st_size == 0:
        raise SystemExit(f'{pid}: missing artifact {artifact}')
    artifact_text = artifact_path.read_text(encoding='utf-8')
    if not re.search(rf'^process: "{re.escape(pid)}"$', artifact_text, re.M):
        raise SystemExit(f'{pid}: artifact process identity missing or wrong: {artifact}')

# Every process has a regulation document whose first heading identifies the same process.
for pid in expected:
    n = pid.split('.')[1]
    files = sorted(reg.glob(f'{int(n):02d}-*.md'))
    if not files:
        raise SystemExit(f'{pid}: regulation document missing')
    if not any(re.search(rf'^# {re.escape(pid)}\b', p.read_text(encoding='utf-8'), re.M) for p in files):
        raise SystemExit(f'{pid}: regulation heading does not identify process')

print('PASS  exact 5.1–5.25 process identity, artifact routing and regulation traceability')
PY
pass=$((pass+1))

# Required artifacts that carry non-structural evidence contracts.
for f in \
  requirements-registry.yml defects-registry.yml training-log.yml configuration-items.yml \
  dependencies-inventory.yml suppliers-registry.yml fuzzing-targets.yml secrets-inventory.yml \
  sast-tools.yml build-tools.yml dynamic-analysis.yml secure-build.yml code-review-log.yml \
  planning-status-analysis.yml architecture.yml threat-model.yml coding-rules.yml source-code-access.yml \
  functional-testing.yml nonfunctional-testing.yml release-security.yml secure-delivery.yml support.yml \
  vulnerability-response.yml vulnerability-search.yml decommission-plan.yml; do
  check_file "$ART/$f"
done

# 5.11 dynamic-analysis contract.
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

# 5.12 secure build contract and separation from 5.13 build-environment security.
check_contains "$ART/secure-build.yml" 'source_revision_required: true' "5.12 source revision"
check_contains "$ART/secure-build.yml" 'artifact_digests_recorded: true' "5.12 artifact digest"
check_contains "$ART/secure-build.yml" 'provenance_required: true' "5.12 provenance"
check_contains "$ART/build-tools.yml" 'build_isolation_required: true' "5.13 build isolation"
check_contains "$ART/build-tools.yml" 'least_privilege_required: true' "5.13 least privilege"
check_contains "$ART/build-tools.yml" 'build_events_recorded: true' "5.13 audit events"

# Reference design chain must remain valid.
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

for section in dynamic_analysis fuzzing secure_build evidence; do
  check_contains "$EXAMPLE" "${section}:" "reference design section: $section"
done

printf '\nLEVEL 8 RESULT: %d passed, %d failed\n' "$pass" "$fail"
(( fail == 0 ))
