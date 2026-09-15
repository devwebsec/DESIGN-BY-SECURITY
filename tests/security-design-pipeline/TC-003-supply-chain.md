# TC-003 — CI/CD and supply-chain compromise

## Input

A service is built by CI/CD from third-party dependencies and deployed to production. Artifact signing and provenance are not yet specified.

## Expected Design-by-Security output

Model:

`SOURCE CODE → DEPENDENCIES → DEVELOPER → CI/CD → BUILD RUNNER → ARTIFACT → REGISTRY → DEPLOYMENT`

Threats must include malicious dependency, dependency confusion, compromised maintainer, poisoned package, compromised runner, stolen pipeline token and tampered/unsigned artifact.

## Expected requirements

Requirements cover dependency governance, secrets isolation, protected source branches, build isolation, SBOM, provenance, artifact integrity/signing and deployment authorization.

## Gate

FAIL for an unresolved critical supply-chain integrity flaw or an artifact that cannot be validated before production deployment.

## Security Copilot handoff

Provide build/artifact identifiers, dependency context, provenance evidence, relevant telemetry and detection requirements for operational monitoring.
