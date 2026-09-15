# TC-002 — Privileged identity compromise

## Input

A privileged administrator identity is suspected to be compromised. The environment contains directory services, servers and sensitive data.

## Expected Design-by-Security output

Model WHO→FROM WHERE→IDENTITY→RESOURCE→WHEN→PRIVILEGE→PURPOSE.

Identify direct and transitive access, privileged paths, blast radius and recovery dependencies.

Expected attack chain:

`INITIAL ACCESS → CREDENTIAL ACCESS → DISCOVERY → LATERAL MOVEMENT → PRIVILEGED ACCESS → DATA/BUSINESS IMPACT`

## Expected controls

Preventive: phishing-resistant MFA where applicable, least privilege, PAM/JIT/JEA, segmentation and restricted management planes.

Detective: authentication, privilege-use, endpoint and network telemetry mapped to evidence-supported ATT&CK techniques.

Response: disable/isolate identity, revoke sessions/tokens, rotate credentials, preserve evidence and verify recovery. Destructive actions require human approval.

## Gate

FAIL if the architecture cannot contain the compromised identity or reconstruct the incident timeline.

## Security Copilot handoff

Handoff must include identity context, affected assets, observed evidence, attack path, detection state and approved response options.
