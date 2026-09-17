#!/usr/bin/env bash
set -euo pipefail

ROOT_INPUT="${1:-security-copilot}"
ROOT="$(realpath -m -- "$ROOT_INPUT")"
OUT="$(realpath -m -- "${ROOT_INPUT}.zip")"
PACKAGE_NAME="$(basename -- "$ROOT")"
ROOT_PARENT="$(dirname -- "$ROOT")"
OUT_PARENT="$(dirname -- "$OUT")"
ARCHIVE="${SECURITY_COPILOT_SKILL_ARCHIVE:-skills/security-copilot/security-copilot_v4.skill}"
TMP=""

cleanup() {
  [[ -n "$TMP" && -d "$TMP" ]] && rm -rf -- "$TMP"
}
trap cleanup EXIT

# Only remove the two package names expected by this builder. The parent must
# be the current workspace or a temporary directory; this prevents a caller
# from turning the builder into an arbitrary rm -rf primitive.
PWD_REAL="$(realpath -m -- "$PWD")"
TMP_BASE="$(realpath -m -- "${TMPDIR:-/tmp}")"
case "$PACKAGE_NAME" in
  security-copilot|package) ;;
  *) echo "ERROR: unexpected target name '$PACKAGE_NAME'" >&2; exit 1 ;;
esac
if [[ "$ROOT" == "/" || "$ROOT" == "$HOME" || "$ROOT" == "$PWD_REAL" || -L "$ROOT" ]]; then
  echo "ERROR: refusing unsafe build target: $ROOT" >&2
  exit 1
fi
if [[ "$ROOT_PARENT" != "$PWD_REAL" && "$ROOT_PARENT" != "$TMP_BASE" && "$ROOT_PARENT" != "$TMP_BASE"/* ]]; then
  echo "ERROR: build target must be under workspace or TMPDIR: $ROOT" >&2
  exit 1
fi
if [[ "$OUT_PARENT" != "$PWD_REAL" && "$OUT_PARENT" != "$TMP_BASE" && "$OUT_PARENT" != "$TMP_BASE"/* ]]; then
  echo "ERROR: output archive must be under workspace or TMPDIR: $OUT" >&2
  exit 1
fi

if [[ ! -f "$ARCHIVE" ]]; then
  echo "ERROR: skill archive not found: $ARCHIVE" >&2
  exit 2
fi
if ! unzip -t "$ARCHIVE" >/dev/null 2>&1; then
  echo "ERROR: invalid security-copilot_v4.skill archive: $ARCHIVE" >&2
  exit 3
fi

# Reject path traversal, absolute paths and Windows absolute/UNC paths before extraction.
if unzip -Z1 "$ARCHIVE" | grep -Eq '(^/|^[A-Za-z]:|^\\\\|(^|[\\/])\.\.([\\/]|$))'; then
  echo "ERROR: archive contains unsafe path entries" >&2
  exit 3
fi

TMP="$(mktemp -d)"
unzip -q "$ARCHIVE" -d "$TMP"
if [[ ! -f "$TMP/security-copilot/SKILL.md" ]]; then
  echo "ERROR: archive must contain security-copilot/SKILL.md" >&2
  exit 4
fi

rm -rf -- "$ROOT" "$OUT"
mkdir -p -- "$ROOT"
cp -a "$TMP/security-copilot/." "$ROOT/"

for f in \
  SKILL.md \
  references/adapters-and-specialized-engines.md \
  references/analysis-engines.md \
  references/available-modes.md \
  references/mode-orchestrator-and-triage.md \
  references/output-formats.md \
  references/playbooks.md \
  references/process-and-quality.md; do
  [[ -f "$ROOT/$f" ]] || { echo "ERROR: missing $ROOT/$f" >&2; exit 5; }
done

if [[ -f "design-by-security/DESIGN-BY-SECURITY-PROMPT.md" ]]; then
  mkdir -p "$ROOT/integrations"
  cp "design-by-security/DESIGN-BY-SECURITY-PROMPT.md" "$ROOT/integrations/DESIGN-BY-SECURITY-PROMPT.md"
fi
if [[ -f "skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" ]]; then
  mkdir -p "$ROOT/integrations"
  cp "skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md" "$ROOT/integrations/DESIGN-BY-SECURITY-ADAPTER.md"
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

( cd "$(dirname -- "$ROOT")" && zip -qr -- "$OUT" "$PACKAGE_NAME" )
if ! unzip -t "$OUT" >/dev/null 2>&1; then
  echo "ERROR: generated package failed archive integrity validation: $OUT" >&2
  exit 6
fi
for f in "$PACKAGE_NAME/SKILL.md" "$PACKAGE_NAME/integrations/README.md"; do
  if ! unzip -l "$OUT" "$f" | grep -Fq "$f"; then
    echo "ERROR: generated package missing $f" >&2
    exit 7
  fi
done

echo "Built: $OUT"
