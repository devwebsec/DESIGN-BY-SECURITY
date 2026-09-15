# Integration Test / Security Design Pipeline

This suite validates the integration contract between **Design-by-Security** and **Security Copilot v4**.

## Objective

Prove that a security-design request can move through the complete operating loop without collapsing architecture, operational analysis, detection and response into one monolithic prompt:

`DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN`

## Test contract

The pipeline must produce, at minimum:

1. intent and scope;
2. assets, identities and data flows;
3. trust boundaries and attack surface;
4. threat model and prioritized attack paths;
5. security requirements with validation criteria;
6. preventive, detective, responsive and recovery controls;
7. security gate decision;
8. telemetry and detection requirements;
9. SOC/IR handoff context;
10. residual risk and security debt;
11. lessons learned;
12. redesign actions linked back to requirements/controls.

## Required invariants

- **No product-first design:** controls are derived from threats and requirements.
- **Evidence discipline:** unknowns are explicitly marked; assumptions are not presented as facts.
- **Identity-first:** privileged identity and blast radius are analyzed for critical paths.
- **Detection-by-design:** critical threats have telemetry and a detection strategy or an explicit detection gap.
- **Validation-by-design:** requirements are testable.
- **Human approval:** destructive containment or production-impacting actions require approval.
- **Compliance separation:** compliance mapping does not substitute for security analysis.
- **Feedback loop:** operational findings can create security debt, requirement/control changes and redesign work.

## Test cases

- `TC-001-web-api.md` — Internet-facing API: trust boundaries, BOLA/authz, secrets, logging and detection.
- `TC-002-identity-compromise.md` — compromised privileged identity: attack path, blast radius, containment and recovery.
- `TC-003-supply-chain.md` — CI/CD and dependency compromise: provenance, artifact integrity and deployment gate.
- `TC-004-soc-feedback.md` — SOC finding converted into architectural redesign.

## Execution model

Each test follows:

`INPUT → TRIAGE → DESIGN → THREAT MODEL → REQUIREMENTS → CONTROLS → VALIDATION → GATE → OPERATIONAL HANDOFF → LEARN → REDESIGN`

A test passes only when the expected artifacts and invariants are satisfied. A missing mandatory artifact is a **FAIL**, not an implicit assumption.
