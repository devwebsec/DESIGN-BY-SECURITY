# DESIGN-BY-SECURITY — Security Measurements

## Purpose

This file is the root-level measurement contract for the Design-by-Security operating model. It turns the presentation's 12-axis review model into measurable, repeatable evidence without pretending that a score alone proves security.

## 12 review axes

| # | Axis | What is measured | Evidence examples |
|---:|---|---|---|
| 01 | Architecture | component and trust-boundary completeness | architecture artifact, DFD, review record |
| 02 | Identity | authentication and identity assurance | identity model, auth requirements, validation |
| 03 | Network | segmentation and controlled communications | flows, zones, firewall/control evidence |
| 04 | Application | API/application security controls | requirements, tests, findings |
| 05 | Data | classification, protection and lifecycle | data-flow/classification evidence |
| 06 | Privilege | least privilege and blast-radius control | role model, privileged paths, validation |
| 07 | Segmentation | isolation between trust zones and critical assets | boundary model, control tests |
| 08 | Detection | telemetry and detection coverage | telemetry map, detection tests, gaps |
| 09 | Response | containment and response readiness | playbooks, approved actions, exercises |
| 10 | Resilience | recovery, backup, HA and degradation handling | recovery tests, RTO/RPO evidence |
| 11 | Supply Chain | dependency, provenance and artifact integrity | SBOM, dependency inventory, provenance/signing evidence |
| 12 | Validation | requirements/control testability and evidence quality | validation records, CI gates, evidence package |

## Measurement method

Each axis is evaluated from evidence, not from narrative confidence. For every control use:

`EXISTS → CONFIGURED → EFFECTIVE → TESTED`

For each critical attack path use:

`PREVENTION + DETECTION + RESPONSE + RECOVERY`

An unavailable measurement is recorded as `UNKNOWN` or `REQUIRES VALIDATION`; it is never silently converted to a positive result.

## Score handling

The presentation defines a 12 × 10 review model (`/120`) and gate bands. This repository treats that number as a review aid, **not** as proof of security and not as a substitute for hard-fail invariants.

Hard-fail conditions in `tests/security-design-pipeline/pipeline-manifest.yml` override any aggregate score. A project with an unresolved critical design flaw, broken requirement/validation chain, missing critical-path detection coverage, unknown presented as evidence, or unauthorized destructive action must not be approved merely because an aggregate score is high.

## Required measurement record

```yaml
measurement:
  axis: Detection
  subject: AP-001
  status: TESTED
  value: 1.0
  unit: coverage_ratio
  evidence:
    - detection-test-001
  timestamp: YYYY-MM-DD
  owner: security
  notes: "Critical attack path has telemetry and validated detection."
```

## Minimum repository KPIs

- contract validation: `0` failed hard-fail invariants
- Level 4 semantic validation: all valid fixtures accepted; all negative fixtures rejected
- Level 5+ mutation testing: all expected-invalid mutations rejected; benign metamorphic mutations accepted
- Level 6 fuzzing: generated invalid cases rejected within configured bounds
- Level 7 graph invariants: `critical_asset_coverage = 1.0` and `critical_threat_attack_path_coverage = 1.0` for the reference graph
- Builder: archive integrity and required package contents pass
- Evidence: validation logs and evidence package produced by CI

## Interpretation

Measurements answer **what was tested and what evidence exists**. They do not establish absence of all vulnerabilities. Security decisions remain tied to the documented threat model, residual risk, evidence quality and hard-fail gates.
