# TC-001 — Internet-facing API

## Input

A public API receives authenticated user requests and accesses a business database. The design does not yet define authorization boundaries, logging requirements or failure behavior.

## Expected Design-by-Security output

- Assets: API, user identities, database, business data, signing/secrets material.
- Trust boundaries: Internet→API gateway, gateway→service, service→database.
- Attack surface: authentication, authorization, API endpoints, file/input handling, secrets, exposed management plane.
- Threats: credential abuse, broken object-level authorization, injection, SSRF where applicable, secret compromise, abuse/rate exhaustion.
- Critical attack path: compromised identity → API authorization weakness → unauthorized data access.

## Expected requirements

Each material threat must produce a unique requirement with owner, control and validation criteria. Requirements such as “improve security” are invalid.

## Expected controls

Preventive: strong authentication, authorization policy, input/schema validation, secret management, network policy.

Detective: authentication/API logs, authorization failures, anomalous access, relevant WAF/application/SIEM telemetry.

Response/recovery: account/session containment, credential rotation, evidence preservation and recovery path.

## Gate

FAIL if critical authorization or authentication design flaws remain unresolved. PASS only when the control and validation chain is complete or an explicitly accepted residual risk is documented.

## Security Copilot handoff

Provide asset, identity, attack-path, telemetry and threat context to the operational engine. Do not repeat the entire architecture prompt as an operational instruction.
