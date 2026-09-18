# GitHub Copilot repository instructions

## Scope

This repository implements the Design-by-Security validation contract and the Security Copilot v4 integration. The authoritative repository security gate is `.github/workflows/security-design-integration.yml`.

## Validation authority

For repository correctness, treat the following as authoritative:

1. Security Design Integration workflow.
2. Level 4 semantic validation.
3. Level 5+ mutation/metamorphic validation.
4. Level 6 property/graph fuzzing.
5. Level 7 graph invariant validation.
6. Level 8 GOST process/evidence overlay.
7. Builder and generated-package integrity checks.

GitHub Copilot, Advanced Security, Code Scanning agents, or other hosted AI review agents are external integrations. Their availability, model routing, and runtime errors must not be represented as failures of the Design-by-Security application unless the repository's own workflow reports a failure.

## Security behavior

- Never invent evidence, credentials, tokens, scan results, or execution results.
- Treat unknown data as unknown and preserve provenance.
- Do not weaken a hard-fail security invariant to make a check pass.
- Destructive actions require explicit human approval.
- Preserve the lifecycle: DESIGN -> BUILD -> DEPLOY -> DETECT -> RESPOND -> LEARN -> REDESIGN.
- Keep Design-by-Security and Security Copilot responsibilities separated through their adapters/contracts.

## Change discipline

Before proposing a change:

- inspect the existing contract and adapters;
- preserve backward compatibility unless a breaking change is explicitly required;
- validate shell and Python syntax;
- run the complete security-design integration pipeline;
- run the builder and verify package contents;
- report external GitHub/Copilot failures separately from repository failures.

## Do not configure private/internal model identifiers

Do not add GitHub Copilot internal routing identifiers (for example `sweagent-capi:*`) to repository configuration. Model availability is controlled by the GitHub-hosted service and is not part of this repository's application contract.
