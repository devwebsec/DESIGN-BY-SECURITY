# Security Engine Catalog

The repository architecture is organized around composable security-analysis engines. This catalog defines their responsibilities and evidence boundaries.

## Architecture engines

### Asset Engine
Determines critical assets, ownership, value, classification, CIA, dependencies, exposure and impact.

### Data Flow Engine
Models `SOURCE → IDENTITY → CHANNEL → PROCESSING → STORAGE → DESTINATION` and evaluates authentication, authorization, encryption, integrity, logging and validation.

### Trust Boundary Engine
Identifies trust transitions and asks what identity, authorization, protocol and control are required at each boundary.

### Attack Surface Engine
Enumerates public/private entry points, privileged paths, APIs, management interfaces, dependencies and external integrations.

### Threat Model Engine
Maps assets and boundaries to threats and abuse cases. Separates evidence from assumptions and hypotheses.

### Attack Path Engine
Builds attack chains and requires critical paths to have prevention, detection, response and recovery coverage or an explicit gap.

### Identity & Privilege Engine
Uses the model:

```text
WHO → FROM WHERE → IDENTITY → RESOURCE → WHEN → PRIVILEGE → PURPOSE
```

Authentication is not treated as authorization. Network reachability is not treated as authorization.

### Data Security Engine
Uses the lifecycle:

```text
CREATE → PROCESS → STORE → TRANSFER → BACKUP → ARCHIVE → DELETE
```

### Secrets Engine
Reviews passwords, API keys, tokens, certificates, private keys and service credentials for exposure, lifetime, permissions and rotation.

### Network Security Engine
Uses:

```text
ZONE → SOURCE → DESTINATION → PROTOCOL → PORT → IDENTITY → PURPOSE → CONTROL
```

### Application / API Engine
Reviews authentication, authorization, session management, validation, cryptography, business logic, dependency security, rate limiting and abuse prevention.

### Cloud / Container Engine
Reviews IAM, workload identity, segmentation, public exposure, storage, KMS, secrets, logging, management plane, backup, DR and runtime controls.

### DevSecOps Engine
Reviews:

```text
PLAN → CODE → BUILD → TEST → PACKAGE → SIGN → DEPLOY → RUNTIME → MONITOR
```

with threat modeling, SAST/DAST/IAST, SCA, secret scanning, IaC/container scanning, SBOM, signing, provenance and CI/CD access controls.

## Operational engines

### Detection Engineering
For each confirmed TTP define detection name, scenario, ATT&CK mapping, data sources, required fields, logic/query, false positives, tuning, severity, response and validation.

### Detection Gap
Separately records visibility, detection, correlation and response gaps. Absence of telemetry is not treated as evidence that an event did not occur.

### Root Cause
Separates root cause, initial access, exploit, persistence, contributing factors, detection failure and response failure.

### Hunting
After a significant finding, ask where the same IOC, identity, process, command, destination, persistence or TTP could exist elsewhere.

### Forensic Preservation
Before disruptive actions, consider evidence risk, business risk, security risk and reversibility. Active containment can take precedence when justified.

### Resilience
Evaluates blast radius, recovery dependencies, backup, failover, degradation and residual risk.

## Governance engines

### Requirements
Every critical threat must map to a security requirement.

### Controls
Every requirement must map to one or more controls.

### Validation
Every requirement/control chain must be testable and backed by evidence.

### Security Gate
Unresolved critical design flaws are blocking conditions. Compliance mapping is evidence of mapping, not proof of actual security.

### Feedback / Redesign
The lifecycle closes through:

```text
FINDING → ROOT CAUSE → SECURITY DEBT → REQUIREMENT/CONTROL CHANGE → VALIDATION → REDESIGN
```
