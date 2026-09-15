#!/usr/bin/env bash
# Integration wrapper for the canonical Security Copilot v4 skill bundle.
# The original self-contained builder remains preserved as an uploaded artifact;
# this wrapper validates that the bundled skill archive exists and can be unpacked.
set -euo pipefail
ROOT="security-copilot"
ARCHIVE="skills/security-copilot/security-copilot_v4.skill"
rm -rf "$ROOT"
unzip -q "$ARCHIVE" -d .
test -f "$ROOT/SKILL.md"
for f in references/adapters-and-specialized-engines.md references/analysis-engines.md references/available-modes.md references/mode-orchestrator-and-triage.md references/output-formats.md references/playbooks.md references/process-and-quality.md; do test -f "$ROOT/$f"; done
echo "Security Copilot skill validated: $ROOT"
