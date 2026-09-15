# TC-004 — SOC finding → architectural redesign

## Input

SOC reports a recurring attack path that was technically detected and contained, but the root architectural weakness remains.

## Expected flow

`DETECTION → TRIAGE → VALIDATION → CONTAINMENT → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN`

## Expected outputs

- incident/evidence summary;
- affected assets and identities;
- confirmed attack path;
- detection/control effectiveness assessment;
- root cause;
- security debt item;
- new or changed security requirement;
- control remediation;
- validation test;
- residual risk after remediation;
- redesign decision.

## Gate

FAIL if the incident is closed operationally while the known architectural root cause has no owner, requirement/control change or validation path.

## Security Copilot handoff

Operational analysis remains in Security Copilot. Architecture changes are returned to Design-by-Security as structured findings rather than as an unbounded prompt continuation.
