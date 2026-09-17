#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y-%m-%d-%H%M%S)"
OUT="${1:-$REPO_ROOT/evidence-package-$STAMP}"
PARENT="$(dirname "$OUT")"
ZIP="$PARENT/$(basename "$OUT").zip"

rm -rf "$OUT" "$ZIP" "$ZIP.sha256"
mkdir -p "$OUT/gost-compliance/pipeline" "$OUT/gost-compliance/regulations" "$OUT/gost-compliance/artifacts" "$OUT/reports" "$OUT/metadata" "$OUT/examples/web-api"
cp "$REPO_ROOT/gost-compliance/GOST-OVERVIEW.md" "$OUT/gost-compliance/"
cp "$REPO_ROOT/gost-compliance/GOST-MAPPING.yml" "$OUT/gost-compliance/"
cp -R "$REPO_ROOT/gost-compliance/regulations/." "$OUT/gost-compliance/regulations/"
cp -R "$REPO_ROOT/gost-compliance/artifacts/." "$OUT/gost-compliance/artifacts/"
cp "$REPO_ROOT/examples/web-api/security-design.yaml" "$OUT/examples/web-api/"
cp "$REPO_ROOT/gost-compliance/pipeline/gost-validate.sh" "$OUT/gost-compliance/pipeline/"
cp "$REPO_ROOT/gost-compliance/pipeline/evidence-package.sh" "$OUT/gost-compliance/pipeline/"

if git -C "$REPO_ROOT" rev-parse HEAD >/dev/null 2>&1; then
  commit=$(git -C "$REPO_ROOT" rev-parse HEAD)
  status=$(git -C "$REPO_ROOT" status --porcelain)
else
  commit=UNKNOWN
  status=UNKNOWN
fi

printf '{\n  "git_commit": "%s",\n  "git_status_clean": %s,\n  "generated_utc": "%s"\n}\n' "$commit" "$([[ -z "$status" ]] && echo true || echo false)" "$STAMP" > "$OUT/metadata/manifest.json"

bash "$OUT/gost-compliance/pipeline/gost-validate.sh" > "$OUT/reports/validation-$STAMP.log"

( cd "$OUT" && find . -type f ! -path './metadata/checksums.sha256' -print0 | sort -z | xargs -0 sha256sum > metadata/checksums.sha256 )
( cd "$PARENT" && zip -qr "$ZIP" "$(basename "$OUT")" )
sha256sum "$ZIP" > "$ZIP.sha256"
printf '%s\n' "$ZIP"
