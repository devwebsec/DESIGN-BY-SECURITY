# Security Copilot integration

This branch preserves the repository baseline and adds the Security Copilot v4 bundle plus the Design-by-Security master prompt.

## Canonical layout

- `skills/security-copilot/security-copilot_v4.skill` — original uploaded skill archive.
- `build-security-copilot.sh` — reproducible validation/unpack wrapper for the canonical bundle.
- `design-by-security/DESIGN-BY-SECURITY-PROMPT.md` — Design-by-Security master prompt.
- `AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md` — existing SOC Copilot 2.1 source.
- `DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md` — existing Design-by-Security master prompt.

The original repository files are not overwritten. Integration is isolated on `integrate/security-copilot-v4` pending review.
