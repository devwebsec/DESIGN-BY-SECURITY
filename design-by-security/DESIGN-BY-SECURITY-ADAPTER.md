# Design-by-Security ↔ Security Copilot v4 Adapter

## Purpose

This adapter defines the boundary between architecture/security-design reasoning and operational security analysis.

## Ownership

### Design-by-Security owns

- business and security objectives;
- assets and data classification;
- architecture and dependencies;
- data flows;
- trust boundaries;
- attack surface;
- threat model;
- attack paths;
- security requirements;
- control selection and control effectiveness;
- security validation;
- security gate;
- residual risk;
- security debt;
- redesign decisions.

### Security Copilot v4 owns

- SOC triage;
- incident response;
- DFIR;
- threat hunting;
- detection engineering;
- CTI/IOC analysis;
- malware analysis;
- operational AppSec/DevSecOps analysis;
- specialized security playbooks.

## Input contract to Security Copilot

```text
CASE_ID
OBJECTIVE
ENVIRONMENT
ASSETS
IDENTITIES
DATA_FLOWS
TRUST_BOUNDARIES
ATTACK_SURFACE
THREATS
ATTACK_PATHS
SECURITY_REQUIREMENTS
CONTROLS
TELEMETRY
KNOWN_EVIDENCE
ASSUMPTIONS
CONSTRAINTS
RISK_CONTEXT
APPROVED_ACTIONS
```

Unknown values must remain `UNKNOWN`; assumptions must be explicitly labeled.

## Output contract back to Design-by-Security

```text
FINDING_ID
CASE_ID
EVIDENCE
AFFECTED_ASSETS
AFFECTED_IDENTITIES
CONFIRMED_ATTACK_PATH
ATT&CK_MAPPING
DETECTION_STATUS
CONTROL_EFFECTIVENESS
ROOT_CAUSE
SECURITY_DEBT
REQUIREMENT_CHANGE
CONTROL_CHANGE
VALIDATION_REQUIRED
RESIDUAL_RISK
REDESIGN_RECOMMENDATION
```

## Routing rules

1. Architecture question → Design-by-Security.
2. Active/observed security event → Security Copilot.
3. Architecture weakness discovered during operations → return a structured finding to Design-by-Security.
4. Critical unresolved design flaw → `decision=FAIL`, `review_outcome=REDESIGN_REQUIRED`.
5. Production-impacting or destructive response → human approval required.

## End-to-end loop

`DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN`

The adapter is a contract, not a second monolithic prompt. It prevents duplication and preserves separation of concerns while allowing evidence and lessons learned to flow back into architecture.
