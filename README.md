# DESIGN-BY-SECURITY

## Security Architecture & Engineering Operating System

This repository implements the architecture described by the Design-by-Security presentation as an executable, testable security engineering operating model.

It combines two complementary planes:

- **Design-by-Security** — architecture-first security design, threat modeling, requirements, controls, validation and security gates.
- **Security Copilot v4** — operational SOC, IR, DFIR, hunting, detection and security-engineering analysis.

The planes are intentionally separated and connected by explicit adapters.

### Master operating model

```text
BUSINESS → SECURITY GOALS → ASSETS → DATA FLOWS → TRUST BOUNDARIES
→ ATTACK SURFACE → THREAT MODEL → ATTACK PATHS → REQUIREMENTS
→ CONTROLS → ARCHITECTURE → BUILD → VALIDATE → DEPLOY → DETECT
→ RESPOND → RECOVER → LEARN → REDESIGN
```

### Repository structure

```text
.
├── .github/workflows/security-design-integration.yml
├── design-by-security/
│   ├── DESIGN-BY-SECURITY-PROMPT.md
│   ├── DESIGN-BY-SECURITY-ADAPTER.md
│   └── INTEGRATION.md
├── skills/security-copilot/
│   ├── security-copilot_v4.skill
│   ├── DESIGN-BY-SECURITY-ADAPTER.md
│   └── INTEGRATION.md
├── tests/security-design-pipeline/
│   ├── TEST-PLAN.md
│   ├── EXPECTED-RESULTS.md
│   ├── pipeline-manifest.yml
│   ├── fixtures/expected-artifact-contract.md
│   ├── TC-001-web-api.md
│   ├── TC-002-identity-compromise.md
│   ├── TC-003-supply-chain.md
│   ├── TC-004-soc-feedback.md
│   ├── semantic/
│   ├── graph/
│   └── run-pipeline.sh
├── schemas/
│   └── security-design.schema.json
├── examples/
│   └── web-api/security-design.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ENGINE-CATALOG.md
│   └── SECURITY-DESIGN-CONTRACT.md
├── DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md
├── AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md
├── build-security-copilot.sh
├── LICENSE
└── SECURITY.md
```

## Design principles

Security is a design property, not a post-production patch.

The architecture process starts with business context and evidence, not technology selection. Critical attack paths must have prevention, detection, response and recovery coverage or an explicit detection gap. Unknowns are preserved as unknowns and never silently promoted to evidence.

Controls are assessed as:

`EXISTS → CONFIGURED → EFFECTIVE → TESTED`

Compliance mapping is not treated as proof of actual security.

## Feedback loop

Operational findings return to architecture through:

`OBSERVATION → FINDING → ROOT CAUSE → SECURITY DEBT / DESIGN FLAW → REQUIREMENT OR CONTROL CHANGE → VALIDATION → REDESIGN`

Destructive response actions require human authorization.

## Machine-readable contract

The canonical required artifact set is defined by `tests/security-design-pipeline/pipeline-manifest.yml`; a human-readable explanation is in `docs/SECURITY-DESIGN-CONTRACT.md`; the machine-readable artifact shape is in `schemas/security-design.schema.json`.

A reference web API artifact is available under `examples/web-api/`.

## Integration validation

Run locally with:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
```

The same gate runs in GitHub Actions for `main`, integration, hardening and audit branches and for pull requests targeting `main`.

## Presentation alignment

`docs/ARCHITECTURE.md` and `docs/ENGINE-CATALOG.md` translate the presentation into repository-level implementation responsibilities. The presentation's architecture is therefore represented by executable contracts, reference artifacts, adapters and CI gates rather than by documentation alone.
