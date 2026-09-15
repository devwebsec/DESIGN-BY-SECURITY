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
├── .github/workflows/blank.yml
├── AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md
├── DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md
├── design-by-security/
│   └── DESIGN-BY-SECURITY-PROMPT.md
├── build-security-copilot.sh
├── skills/
│   └── security-copilot/
│       ├── security-copilot_v4.skill
│       └── INTEGRATION.md
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

See `skills/security-copilot/INTEGRATION.md` for the integration contract.
