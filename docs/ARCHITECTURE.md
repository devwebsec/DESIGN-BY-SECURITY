# DESIGN-BY-SECURITY — Repository Architecture

This document is the implementation map for the Security Architecture & Engineering Operating System described in the presentation.

## 1. System boundary

The repository contains two deliberately separated planes:

- **Design-by-Security** — architecture and security-design control plane.
- **Security Copilot v4** — operational SOC / IR / DFIR / hunting / detection plane.

The planes exchange explicit artifacts through adapters. The operational skill remains authoritative for operational behavior; the design layer is the gate that must exist before production approval.

## 2. Master lifecycle

```text
BUSINESS
  ↓
SECURITY GOALS
  ↓
ASSETS
  ↓
DATA FLOWS
  ↓
TRUST BOUNDARIES
  ↓
ATTACK SURFACE
  ↓
THREAT MODEL
  ↓
ATTACK PATHS
  ↓
SECURITY REQUIREMENTS
  ↓
SECURITY CONTROLS
  ↓
ARCHITECTURE
  ↓
BUILD
  ↓
VALIDATE
  ↓
DEPLOY
  ↓
DETECT
  ↓
RESPOND
  ↓
RECOVER
  ↓
LEARN
  ↓
REDESIGN
```

## 3. Engines represented by the design contract

| Engine | Primary responsibility |
|---|---|
| Business / Intent | business objective, scope, assumptions |
| Asset | owner, value, classification, CIA, exposure, dependencies |
| Data Flow | source → identity → channel → processing → storage → destination |
| Trust Boundary | trust transitions and required controls |
| Attack Surface | entry/exit points, privileged paths, exposed interfaces |
| Threat Model | threats, abuse cases, impact, confidence |
| Attack Path | attack chain and critical-path coverage |
| Identity & Privilege | identity, authentication, authorization, privilege, blast radius |
| Data Security | lifecycle, classification, encryption, retention, deletion |
| Secrets | credentials, tokens, keys, certificates, rotation |
| Network | zone, source, destination, protocol, port, identity, purpose, control |
| Application / API | authn/authz, validation, session, business logic, abuse prevention |
| Cloud / Container | IAM, segmentation, public exposure, workload identity, runtime |
| DevSecOps | code → build → test → package → sign → deploy → runtime |
| Detection-by-Design | telemetry, detection, response, recovery for critical paths |
| Resilience | HA, backup, recovery, degradation and residual risk |
| Compliance / Audit | mapping evidence without treating compliance as proof of security |
| Validation | testable requirements, controls and evidence |
| Security Gate | approve / conditional / redesign / do not approve |
| Feedback / Redesign | finding → root cause → debt → requirement/control change → validation |

## 4. Evidence policy

Every material claim must be classified as one of:

- `CONFIRMED`
- `PROBABLE`
- `ASSUMPTION`
- `HYPOTHESIS`
- `UNKNOWN`
- `REQUIRES VALIDATION`
- `DESIGN RECOMMENDATION`

Unknown architecture must never be silently invented.

## 5. Control model

Controls are evaluated independently for:

```text
EXISTS → CONFIGURED → EFFECTIVE → TESTED
```

A control that merely exists is not evidence that the design is secure.

For critical attack paths the minimum model is:

```text
PREVENTION + DETECTION + RESPONSE + RECOVERY
```

Missing telemetry or detection is recorded as an explicit `DETECTION GAP`.

## 6. Operational feedback

The operational layer feeds design improvements through:

```text
OBSERVATION
 → FINDING
 → ROOT CAUSE
 → SECURITY DEBT / DESIGN FLAW
 → REQUIREMENT OR CONTROL CHANGE
 → VALIDATION
 → REDESIGN
```

Destructive response actions require human authorization. Incident closure requires root-cause feedback before the lifecycle can return to redesign.

## 7. Repository implementation

- `design-by-security/` contains architecture prompt, adapter and integration contract.
- `skills/security-copilot/` contains the reusable operational skill and reverse adapter.
- `tests/security-design-pipeline/` implements contract, semantic, mutation, fuzz and graph validation.
- `.github/workflows/security-design-integration.yml` is the CI gate.
- `build-security-copilot.sh` is the reproducible builder.
- `schemas/` contains machine-readable design artifacts.
- `examples/` contains reference security-design instances.
- `docs/` contains the human-readable operating model.

The presentation is therefore treated as an architecture specification, not as a decorative document.