# Canonical Security Design Contract

This is the human-readable contract behind `tests/security-design-pipeline/pipeline-manifest.yml`.

## Required artifacts

1. `intent` — business objective, scope, assumptions and constraints.
2. `architecture` — components, dependencies and security-relevant decisions.
3. `assets` — critical assets, owners, classification, CIA, exposure and impact.
4. `data_flows` — source, identity, channel, processing, storage and destination.
5. `trust_boundaries` — trust transitions and controls.
6. `threat_model` — threats, abuse cases, impact and confidence.
7. `attack_paths` — attack chains, criticality and coverage.
8. `security_requirements` — testable security requirements.
9. `controls` — preventive, detective, responsive and recovery controls.
10. `validation` — tests and evidence proving requirements and controls.
11. `security_gate` — blocking findings, residual risk and decision.
12. `operational_handoff` — telemetry, detections and response context.
13. `lessons_learned` — observations and root causes from operation.
14. `redesign` — concrete changes that return lessons to architecture.

## Mandatory relationships

```text
THREAT → REQUIREMENT → CONTROL → VALIDATION
ATTACK PATH → DETECTION or EXPLICIT GAP
LESSON → ROOT CAUSE → REDESIGN
DESTRUCTIVE RESPONSE → HUMAN APPROVAL
```

## Blocking conditions

A design is rejected when:

- a critical threat has no requirement;
- a requirement has no validation;
- a critical attack path has neither detection nor an explicit gap;
- a critical design flaw remains unresolved;
- unknown information is presented as evidence;
- a destructive action lacks human approval;
- an incident is closed without root-cause feedback.

## Decision semantics

The design gate can emit:

- `APPROVE`
- `APPROVE_WITH_CONDITIONS`
- `REDESIGN_REQUIRED`
- `DO_NOT_APPROVE`

The decision must state the evidence boundary, residual risk and blocking conditions.
