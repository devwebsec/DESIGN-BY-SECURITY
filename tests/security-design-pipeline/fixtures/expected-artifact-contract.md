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
| Gate | decision | PASS / FAIL / REDESIGN REQUIRED + rationale |
| Operate | SOC/IR handoff | telemetry, identity, asset, threat, attack-path context |
| Learn | lessons learned | finding, root cause, control effectiveness |
| Redesign | change set | debt, requirement/control change, validation |

## Hard-fail conditions

- critical threat without a requirement;
- requirement without validation;
- critical attack path without prevention/detection/response/recovery strategy;
- critical detection gap hidden as a PASS;
- unknown treated as confirmed evidence;
- unresolved critical design flaw allowed through the security gate;
- incident closed without addressing a known architectural root cause;
- destructive response proposed without human approval.
