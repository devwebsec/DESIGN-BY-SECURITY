#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────
# ИСТОРИЯ ИЗМЕНЕНИЙ
# v1 → v2:
#   [FIX-1] Guard от rm -rf на критичных путях (/, $HOME, cwd, ..).
#   [FIX-2] Расширен regex traversal — покрывает Windows-пути
#           (C:\..., UNC \\server\..., обратные слеши).
#   [FIX-3] Post-build проверка содержимого через unzip -l вместо
#           unzip -p (последний возвращал 0 даже для отсутствующего файла).
#   [FIX-4] Grep в pre-extraction вынесен из set -e-чувствительного
#           контекста через явный if.
# ─────────────────────────────────────────────────────────────────────

ROOT_INPUT="${1:-security-copilot}"
ROOT="$(realpath -m "$ROOT_INPUT")"
OUT="$(realpath -m "${ROOT_INPUT}.zip")"
PACKAGE_NAME="$(basename "$ROOT")"
ARCHIVE="${SECURITY_COPILOT_SKILL_ARCHIVE:-skills/security-copilot/security-copilot_v4.skill}"
TMP=""

cleanup() {
  [[ -n "$TMP" && -d "$TMP" ]] && rm -rf "$TMP"
}
trap cleanup EXIT

# ─── [FIX-1] Guard от опасного rm -rf ───────────────────────────────
# Разрешаем удалять только каталоги с ожидаемыми именами и никогда —
# критические системные пути. Совместимо с вызовом из run-pipeline.sh,
# где ROOT_INPUT = "$BUILD_TMP/package" (basename = "package").
if [[ "$ROOT" == "/" ]] \
   || [[ "$ROOT" == "$HOME" ]] \
   || [[ "$ROOT" == "$PWD" ]] \
   || [[ "$ROOT" == "$PWD/" ]] \
   || [[ -z "$PACKAGE_NAME" ]] \
   || [[ "$PACKAGE_NAME" == "." ]] \
   || [[ "$PACKAGE_NAME" == ".." ]]; then
  echo "ERROR: refusing to remove critical path: $ROOT" >&2
  exit 1
fi

case "$PACKAGE_NAME" in
  security-copilot|package) : ;;  # разрешённые имена
  *)
    echo "ERROR: unexpected target name '$PACKAGE_NAME' (allowed: security-copilot, package)" >&2
    exit 1
    ;;
esac
# ────────────────────────────────────────────────────────────────────

rm -rf "$ROOT" "$OUT"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "ERROR: skill archive not found: $ARCHIVE" >&2
  exit 2
fi

if ! unzip -t "$ARCHIVE" >/dev/null 2>&1; then
  echo "ERROR: invalid security-copilot_v4.skill archive: $ARCHIVE" >&2
  exit 3
fi

# ─── [FIX-2] Traversal check: POSIX + Windows-стиль ─────────────────
# Ловит:
#   - абсолютные POSIX-пути      /etc/passwd
#   - абсолютные Windows-пути    C:\Windows\...
#   - UNC                        \\server\share\...
#   - parent traversal           ../../foo, ..\..\foo
# Явный `if ...; then` защищает от срабатывания set -e при exit=1 у grep.
if unzip -Z1 "$ARCHIVE" | grep -Eq '(^/|^[A-Za-z]:|^\\\\|(^|[\\/])\.\.([\\/]|$))'; then
  echo "ERROR: archive contains unsafe path entries" >&2
  exit 3
fi
# ────────────────────────────────────────────────────────────────────

TMP="$(mktemp -d)"
unzip -q "$ARCHIVE" -d "$TMP"

if [[ ! -f "$TMP/security-copilot/SKILL.md" ]]; then
  echo "ERROR: archive must contain security-copilot/SKILL.md" >&2
  exit 4
fi

mkdir -p "$ROOT"
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

( cd "$(dirname "$ROOT")" && zip -qr "$OUT" "$PACKAGE_NAME" )

if ! unzip -t "$OUT" >/dev/null 2>&1; then
  echo "ERROR: generated package failed archive integrity validation: $OUT" >&2
  exit 6
fi

# ─── [FIX-3] Post-build: проверка через unzip -l ─────────────────────
# unzip -p возвращает 0 даже для отсутствующего файла, поэтому
# используем unzip -l + grep, чтобы гарантированно убедиться в наличии.
for f in "$PACKAGE_NAME/SKILL.md" "$PACKAGE_NAME/integrations/README.md"; do
  if ! unzip -l "$OUT" "$f" | grep -Fq "$f"; then
    echo "ERROR: generated package missing $f" >&2
    exit 7
  fi
done
# ────────────────────────────────────────────────────────────────────

echo "Built: $OUT"
