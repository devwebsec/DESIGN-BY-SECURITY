# Integration Test Plan

## Level 1 — Structural

Verify repository paths, skill archive integrity, adapter presence and builder syntax.

## Level 2 — Contract

Verify architecture-to-operations and operations-to-architecture fields are present and no mandatory stage is skipped.

## Level 3 — Scenario

Execute TC-001 through TC-004 and verify expected artifacts and hard-fail conditions.

## Level 4 — Lifecycle

Verify the complete chain:

`DESIGN → BUILD → DEPLOY → DETECT → RESPOND → LEARN → REDESIGN`

A successful lifecycle test must demonstrate that an operational finding can create a concrete architecture change and a validation requirement.

## Level 5 — Regression

Any change to the master prompt, Security Copilot skill, adapters, orchestration logic or security gate must rerun the complete suite.

## Exit criteria

- all structural checks PASS;
- all contract checks PASS;
- all mandatory scenarios PASS;
- no hard-fail invariant is violated;
- no critical unknown is silently treated as a fact;
- lifecycle feedback reaches REDESIGN;
- production/destructive response remains human-approved.
