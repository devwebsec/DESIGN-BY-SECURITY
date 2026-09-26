# Design-by-Security adapter for Security Copilot v4

This adapter defines the boundary between architecture-first security design and the operational Security Copilot skill.

## Invocation

Use the Design-by-Security layer when the primary task is to design, review, modify or approve an architecture, component, data flow, identity model, network topology, API, application, cloud deployment, CI/CD pipeline or security control.

Use Security Copilot v4 when the primary task is operational: SOC triage, incident response, DFIR, threat hunting, detection engineering, IOC/CTI, malware analysis or operational security investigation.

If a task spans both, run the architecture stage first and hand its outputs to the operational stage.

## Required hand-off from Design-by-Security

The architecture layer should provide, where applicable:

- business/security objectives;
- assets and owners;
- data classification and critical data flows;
- identities and privileged paths;
- components and dependencies;
- trust boundaries;
- attack surface;
- threat scenarios and abuse cases;
- attack paths;
- security requirements;
- selected controls;
- residual risks;
- required telemetry and detection points;
- containment/recovery capabilities;
- security-gate decision and review outcome.

## Operational context

Security Copilot receives architecture context as structured input rather than importing the full architecture prompt into every operational case.

Use the upstream context fields:

- CASE_ID
- ASSETS
- IDENTITIES
- TRUST_BOUNDARIES
- ATTACK_SURFACE
- THREATS
- ATTACK_PATHS
- SECURITY_REQUIREMENTS
- CONTROLS
- TELEMETRY
- EVIDENCE
- ASSUMPTIONS
- CONSTRAINTS

## Detection-by-Design rule

For each critical attack path, evaluate:

`PREVENTION + DETECTION + RESPONSE + RECOVERY`

If telemetry or detection is absent, report an explicit `DETECTION GAP`.

## Feedback rule

Operational findings must be capable of returning:

`FINDING → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN`

## Evidence discipline

Never turn an assumption into evidence. ATT&CK mappings require supporting evidence. Unknown data stays unknown.

## Response safety

Containment options may be proposed, but destructive or production-impacting actions require human approval.

## Operational hand-off back to design

Security Copilot findings must be converted into design feedback:

```text
OBSERVATION
   -> FINDING
   -> ROOT CAUSE
   -> SECURITY DEBT / DESIGN FLAW
   -> REQUIREMENT OR CONTROL CHANGE
   -> VALIDATION
   -> REDESIGN
```

## Guardrails

1. Do not duplicate the complete v4 skill here.
2. Do not silently alter v4 modes, playbooks or output contracts.
3. Do not treat a detection as a substitute for a missing preventive control when the architecture can remove the attack path.
4. Do not treat compliance mapping as proof of actual security.
5. Do not approve a critical unresolved design flaw merely because compensating detection exists.
6. Preserve uncertainty and evidence boundaries.
7. Destructive operational actions remain subject to human authorization.
8. A critical unresolved design flaw routes as `decision=FAIL` and `review_outcome=REDESIGN_REQUIRED`.

## Lifecycle

```text
DESIGN
  -> BUILD
  -> DEPLOY
  -> DETECT
  -> RESPOND
  -> LEARN
  -> REDESIGN
       ^
       |
       +---- Security Copilot operational findings
```
