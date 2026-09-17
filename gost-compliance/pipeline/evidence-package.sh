#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y-%m-%d-%H%M%S)"
OUT="${1:-$REPO_ROOT/evidence-package-$STAMP}"
ZIP="$REPO_ROOT/evidence-package-$STAMP.zip"

rm -rf "$OUT"
mkdir -p "$OUT/regulations" "$OUT/artifacts" "$OUT/pipeline" "$OUT/reports" "$OUT/metadata"
cp "$REPO_ROOT/gost-compliance/GOST-OVERVIEW.md" "$OUT/"
cp "$REPO_ROOT/gost-compliance/GOST-MAPPING.yml" "$OUT/"
cp -R "$REPO_ROOT/gost-compliance/regulations/." "$OUT/regulations/"
cp -R "$REPO_ROOT/gost-compliance/artifacts/." "$OUT/artifacts/"
cp "$REPO_ROOT/gost-compliance/pipeline/gost-validate.sh" "$OUT/pipeline/"
cp "$REPO_ROOT/gost-compliance/pipeline/evidence-package.sh" "$OUT/pipeline/"

if git -C "$REPO_ROOT" rev-parse HEAD >/dev/null 2>&1; then
  commit=$(git -C "$REPO_ROOT" rev-parse HEAD)
  status=$(git -C "$REPO_ROOT" status --porcelain)
else
  commit=UNKNOWN
  status=UNKNOWN
fi

printf '{\n  "git_commit": "%s",\n  "git_status_clean": %s,\n  "generated_utc": "%s"\n}\n' "$commit" "$([[ -z "$status" ]] && echo true || echo false)" "$STAMP" > "$OUT/metadata/manifest.json"

( cd "$OUT" && find . -type f -print0 | sort -z | xargs -0 sha256sum > metadata/checksums.sha256 )
( cd "$(dirname "$OUT")" && zip -qr "$ZIP" "$(basename "$OUT")" )
printf '%s\n' "$ZIP"
sha256sum "$ZIP" > "$ZIP.sha256"
