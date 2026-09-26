# Expected artifact contract

The integrated pipeline is considered structurally valid only when these artifacts can be represented for a test case.

| Stage | Required artifact | Minimum content |
|---|---|---|
| Intent | scope | objective, environment, constraints |
| Design | architecture model | components, dependencies, trust boundaries |
| Asset | asset register | owner, value, exposure, impact |
| Data | data-flow model | source, identity, channel, processing, storage, destination |
| Threat | threat register | threat, evidence/assumption, affected asset |
| Attack | attack paths | initial access, escalation, movement, impact |
| Requirements | security requirements | REQ-ID, threat, control, owner, validation, priority |
| Controls | control matrix | prevent, detect, respond, recover, failure mode |
| Validate | validation plan | test, evidence, expected result |
| Dynamic Analysis | dynamic analysis record | roles, tool/version, method, modules, scenarios, failure handling, remediation, periodicity, retest |
| Fuzzing | fuzzing campaign/report | tool/version, module, corpus, duration, crashes, unique paths, crash analysis, completion criteria |
| Secure Build | secure build record | build system, environment, source/dependencies, transformations, reproducibility, digest, SBOM, provenance |
| Evidence | evidence manifest | source reference, path, SHA-256, timestamp, report/artifact linkage |
| Gate | decision + review_outcome | PASS/FAIL/CONDITIONAL + APPROVE/APPROVE_WITH_CONDITIONS/REDESIGN_REQUIRED/DO_NOT_APPROVE + evidence_boundary |
| Operate | SOC/IR handoff | telemetry, identity, asset, threat, attack-path context |
| Learn | lessons learned | finding, root cause, control effectiveness |
| Redesign | change set | debt, requirement/control change, validation |

## Gate semantics

The machine validator emits `decision`:

- `PASS` — artifact satisfies the validator contract;
- `FAIL` — one or more hard-fail conditions remain;
- `CONDITIONAL` — non-critical conditions remain unresolved.

The security architect records `review_outcome` independently:

- `APPROVE`;
- `APPROVE_WITH_CONDITIONS` — requires `residual_risk`;
- `REDESIGN_REQUIRED`;
- `DO_NOT_APPROVE`.

`decision: FAIL` cannot be paired with `APPROVE` or `APPROVE_WITH_CONDITIONS`. `evidence_boundary` is mandatory for every gate.

## Hard-fail conditions

- critical threat without a requirement;
- requirement without validation;
- critical attack path without prevention/detection/response/recovery strategy;
- critical detection gap hidden as a PASS;
- unknown treated as confirmed evidence;
- unresolved critical design flaw allowed through the security gate;
- incident closed without addressing a known architectural root cause;
- destructive response proposed without human approval;
- dynamic-analysis processing error presented as PASS;
- required retest omitted after a security-relevant fix;
- fuzzing crash left without analysis/reproducer handling;
- secure-build provenance missing;
- secure-build artifact digest missing.
