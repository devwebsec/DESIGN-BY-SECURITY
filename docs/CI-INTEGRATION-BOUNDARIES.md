# CI Integration Boundaries

## Purpose

The repository contains two different classes of validation:

### Repository-owned security gate

`.github/workflows/security-design-integration.yml` runs on the repository's own runner and validates the Design-by-Security ↔ Security Copilot contract, including Level 4 through Level 8 and the Builder/evidence package.

A failure in this workflow is a repository validation failure.

### GitHub-hosted security/AI integrations

GitHub Advanced Security, Copilot Code Scanning agents, and Copilot review services execute outside the repository application runtime. They may use service-side model routing and service configuration that is not declared by this repository.

A service-side error such as `400 The requested model is not supported` is an external integration failure. It is not evidence that the repository's Security Design pipeline failed.

## Operational rule

Keep the repository-owned gate independently runnable through `workflow_dispatch`. Do not weaken its assertions or add `continue-on-error` merely to mask failures from an external GitHub service.

If an external GitHub AI/security check fails:

1. inspect its own job log;
2. identify whether the failure is service/model/configuration related;
3. verify the repository-owned Security Design Integration run separately;
4. fix GitHub/org/repository Copilot configuration when the failure is external;
5. never encode private GitHub model-routing identifiers into repository code or workflows.

## Expected final evidence

A final repository verification should record both results independently:

- `Security Design Integration`: repository-owned PASS/FAIL.
- External GitHub Copilot/Advanced Security checks: PASS/FAIL with their own failure reason.

Only the first is authoritative for the Design-by-Security application contract.
