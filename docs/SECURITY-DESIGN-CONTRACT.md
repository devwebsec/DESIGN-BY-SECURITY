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
11. `security_gate` — machine verdict, human review outcome, evidence boundary, blocking conditions and residual risk.
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

The security gate has **two orthogonal fields**:

### `decision` — machine verdict

Emitted by the deterministic validator (`evaluate.py`, `verify_graph.py`).

- `PASS` — artifact satisfies the validator contract.
- `FAIL` — artifact violates one or more hard-fail conditions.
- `CONDITIONAL` — artifact satisfies non-critical conditions but has unresolved warnings.

`PASS` is **not** a claim that the real system is secure. It is a claim that the artifact satisfies the validator contract.

### `review_outcome` — human decision

Emitted by the security architect after reviewing the artifact and its context.

- `APPROVE` — approve for production.
- `APPROVE_WITH_CONDITIONS` — approve with documented residual risk; requires `residual_risk`.
- `REDESIGN_REQUIRED` — block until critical design flaw is resolved.
- `DO_NOT_APPROVE` — reject by policy.

### Rules

- `decision: FAIL` **cannot** have `review_outcome: APPROVE` or `APPROVE_WITH_CONDITIONS`.
- `decision: FAIL` requires `unresolved_critical_design_flaws`.
- `review_outcome: APPROVE_WITH_CONDITIONS` **requires** `residual_risk`.
- `review_outcome != APPROVE` **requires** `blocking_conditions` or `residual_risk`.
- `evidence_boundary` is **always required**.
- `unresolved_critical_design_flaws` and `unknowns` remain hard-fail evidence conditions; they cannot be hidden by a review outcome.

### Canonical YAML shape

```yaml
security_gate:
  decision: PASS | FAIL | CONDITIONAL
  review_outcome: APPROVE | APPROVE_WITH_CONDITIONS | REDESIGN_REQUIRED | DO_NOT_APPROVE
  residual_risk: {}
  evidence_boundary: {}
  blocking_conditions: []
  unresolved_critical_design_flaws: []
  unknowns: []
```

### What this replaces

This replaces the previous single-field model where different value sets were used across components. See P0-1 in the remediation roadmap.
