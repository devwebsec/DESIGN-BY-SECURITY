# Design-by-Security integration

## Role in the system

Design-by-Security is the architecture-first control plane. It decides what
security properties the system must have and establishes the gates that must
be satisfied before deployment.

Security Copilot v4 is the operational security plane. It investigates,
detects, hunts, responds and produces operational evidence and lessons.

## Contract

```text
DESIGN
  BUSINESS -> ASSETS -> DATA -> IDENTITIES
  -> ARCHITECTURE -> TRUST BOUNDARIES -> ATTACK SURFACE
  -> THREATS -> ATTACK PATHS -> REQUIREMENTS -> CONTROLS
  -> VALIDATION -> SECURITY GATE

BUILD -> DEPLOY

DETECT -> RESPOND -> LEARN

REDESIGN
  <- operational findings
  <- detection gaps
  <- incident root causes
  <- control failures
  <- residual-risk changes
```

## Mandatory design outputs

For material systems produce, as applicable:

1. security objectives;
2. asset inventory and criticality;
3. data-flow and trust-boundary model;
4. attack-surface inventory;
5. threat model;
6. prioritized attack paths;
7. testable security requirements;
8. preventive/detective/respond/recover controls;
9. control failure and bypass analysis;
10. telemetry/detection requirements;
11. resilience and recovery requirements;
12. residual-risk assessment;
13. pre-production security-gate decision;
14. assumptions, unknowns and validation plan.

## Operational feedback

Security Copilot v4 findings are not treated as isolated SOC output. Each
material finding should be evaluated for architectural root cause and,
where appropriate, converted into a requirement, control change, security
debt item or redesign action.
