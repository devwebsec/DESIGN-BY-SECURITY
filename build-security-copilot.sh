#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-security-copilot}"
ARCHIVE="${SECURITY_COPILOT_SKILL_ARCHIVE:-skills/security-copilot/security-copilot_v4.skill}"
OUT="${ROOT}.zip"

rm -rf "$ROOT" "$OUT"
mkdir -p "$ROOT"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "ERROR: skill archive not found: $ARCHIVE" >&2
  exit 2
fi

if ! unzip -t "$ARCHIVE" >/dev/null 2>&1; then
  echo "ERROR: invalid security-copilot_v4.skill archive: $ARCHIVE" >&2
  echo "The original uploaded archive must be restored before packaging." >&2
  exit 3
fi

unzip -q "$ARCHIVE" -d .

if [[ ! -f "$ROOT/SKILL.md" ]]; then
  echo "ERROR: expected $ROOT/SKILL.md after extraction" >&2
  exit 4
fi

for f in references/adapters-and-specialized-engines.md references/analysis-engines.md references/available-modes.md references/mode-orchestrator-and-triage.md references/output-formats.md references/playbooks.md references/process-and-quality.md; do
  [[ -f "$ROOT/$f" ]] || { echo "ERROR: missing $ROOT/$f" >&2; exit 5; }
done

if [[ -f "design-by-security/DESIGN-BY-SECURITY-PROMPT.md" ]]; then
  mkdir -p "$ROOT/integrations"
  cp "design-by-security/DESIGN-BY-SECURITY-PROMPT.md" "$ROOT/integrations/DESIGN-BY-SECURITY-PROMPT.md"
fi

cat > "$ROOT/integrations/README.md" <<'DOC'
# Design-by-Security integration

Design-by-Security is the upstream architecture/security-design gate.
Security Copilot v4 is the downstream operational analysis engine.

Design-by-Security owns business/security objectives, assets, data flows,
trust boundaries, attack surface, threat modeling, attack paths, security
requirements, controls, validation, residual risk, security gates and
redesign decisions.

Security Copilot owns operational workflows such as SOC triage, incident
response, DFIR, hunting, detection engineering, IOC/CTI analysis, malware
analysis and specialized security playbooks.

Operational findings feed back into architecture as:
FINDING -> ROOT CAUSE -> SECURITY DEBT -> REQUIREMENT/CONTROL -> VALIDATION -> REDESIGN

The two prompts are deliberately not flattened into one monolithic prompt.
DOC

( cd . && zip -qr "$OUT" "$ROOT" )

echo "Built: $OUT"
