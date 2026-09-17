# DESIGN-BY-SECURITY

## Security Architecture & Engineering Operating System

This repository combines two complementary layers:

- **Design-by-Security** — architecture-first security design, threat modeling, security requirements, controls, validation and security gates.
- **Security Copilot v4** — operational SOC, IR, DFIR, hunting, detection, IOC/CTI, malware and security-engineering analysis.

### Operating model

```text
DESIGN -> BUILD -> DEPLOY -> DETECT -> RESPOND -> LEARN -> REDESIGN
```

### Repository structure

```text
.
├── .github/workflows/
│   └── security-design-integration.yml
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
│   └── run-pipeline.sh
├── DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md
├── AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md
├── build-security-copilot.sh
├── LICENSE
└── SECURITY.md
```

## Design principle

Do not bolt security onto an already-defined architecture. Start with:

`BUSINESS -> ASSETS -> DATA -> IDENTITIES -> ARCHITECTURE -> TRUST BOUNDARIES -> ATTACK SURFACE -> THREATS -> ATTACK PATHS -> REQUIREMENTS -> CONTROLS -> VALIDATION`

The operational layer then closes the loop:

`DETECT -> RESPOND -> LEARN -> REDESIGN`

The Design-by-Security layer and Security Copilot v4 are intentionally kept
separate so that the operational skill remains authoritative and reusable,
while architecture acts as the security-design gate.

## Integration validation

The integration manifest defines the lifecycle, required artifacts and hard-fail
conditions. The executable pipeline validates repository structure, the adapter
contract, scenario contracts, skill archive integrity and actual builder execution.

Run locally with:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
```

The same pipeline runs in GitHub Actions for pushes to `main`/`integrate/**`/
`hardening/**` and pull requests targeting `main`.
