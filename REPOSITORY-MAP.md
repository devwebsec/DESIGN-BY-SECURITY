# DESIGN-BY-SECURITY — Repository Map

This is the canonical navigation map for the repository.

## Root

- `README.md` — project entry point and operating model.
- `DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md` — master design prompt.
- `AI_SECURITY_COPILOT_2_1-*.md` — operational Security Copilot source material.
- `SECURITY-METRICS.md` — 12-axis measurement model and repository KPIs.
- `DEPENDENCIES.md` — runtime, CI and dependency integrity contract.
- `SECURITY.md` — security reporting and handling guidance.
- `build-security-copilot.sh` — reproducible Security Copilot package builder.

## Architecture plane

`design-by-security/` contains the architecture prompt, adapter and integration boundary.

## Operations plane

`skills/security-copilot/` contains the reusable Security Copilot v4 skill, references and adapter.

## Validation plane

`tests/security-design-pipeline/` contains the artifact contract, scenarios, semantic validation, mutation/metamorphic validation, bounded fuzzing and graph invariants.

## Machine-readable design

- `schemas/security-design.schema.json`
- `examples/web-api/security-design.yaml`

## Process / evidence overlay

`gost-compliance/` contains the 25-process mapping, process artifacts and validation/evidence scripts. It is an engineering traceability overlay; it is not a claim of regulatory certification.

## CI

`.github/workflows/security-design-integration.yml` is the integration gate. It validates repository hygiene, syntax, the Level 4–7 pipeline, the process overlay, evidence packaging and CI artifacts.

## Lifecycle

```text
DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN
```

Design-by-Security owns the architecture/design gate. Security Copilot v4 owns operational analysis. The adapters are the explicit boundary between the two.
