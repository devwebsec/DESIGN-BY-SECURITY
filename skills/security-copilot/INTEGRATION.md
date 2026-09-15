# Security Copilot v4 + Design-by-Security integration

## Architecture

```text
DESIGN-BY-SECURITY (Architecture & Security Design Lifecycle)
        |
        ├─> Business / Assets / Data / Identities
        ├─> Architecture / Trust Boundaries / Attack Surface
        ├─> Threat Model / Attack Paths / Abuse Cases
        ├─> Security Requirements / Controls
        └─> Validation / Security Gate / Residual Risk
        |
        v
SECURITY COPILOT v4 (Operational Security Workflows)
        |
        ├─> SOC / TRIAGE / IR / DFIR
        ├─> HUNT / DETECTION / ATT&CK
        ├─> IOC / CTI / MALWARE
        ├─> ENDPOINT / NETWORK / CLOUD
        └─> DEVSECOPS / APPSEC / VULN
        |
        v
DETECT -> RESPOND -> LEARN
         |
         v (Feedback Loop)
      ROOT CAUSE -> SECURITY DEBT -> REQUIREMENT/CONTROL
         |
         v
      VALIDATION -> REDESIGN
```

## Separation of responsibility

Design-by-Security is the upstream architecture and security-design layer.
Security Copilot v4 remains the authoritative operational security skill.

**Design-by-Security owns:**
- Business and security objectives
- Asset, identity and data-flow modeling
- Trust boundaries and attack surface definition
- Threat modeling and attack paths
- Security requirements and control specifications
- Control validation and effectiveness criteria
- Security gates and residual-risk decisions
- Security architecture review and approval
- Redesign driven by operational findings

**Security Copilot v4 owns:**
- SOC triage and alert management
- Incident response and forensics (DFIR)
- Threat hunting and detection engineering
- IOC/CTI analysis and malware analysis
- Endpoint, network, and cloud security operations
- DevSecOps, AppSec, and vulnerability management
- Specialized playbooks and tactical response

## Hand-off Contract

The precise executable contract between these systems is formally defined in
[`DESIGN-BY-SECURITY-ADAPTER.md`](./DESIGN-BY-SECURITY-ADAPTER.md).

Refer to the adapter contract for:
- Input/output schemas at each integration boundary
- Validation rules for design-to-operations handoff
- Data structures for operational findings feedback
- Stage-specific acceptance criteria
- Error handling and escalation procedures

## Integration contract

A design task must progress through:

```
BUSINESS -> ASSETS -> ARCHITECTURE -> TRUST -> THREATS -> ATTACK PATHS 
    -> REQUIREMENTS -> CONTROLS -> VALIDATION -> GATE
```

An operational finding must be able to feed back into design through:

```
FINDING -> ROOT CAUSE -> SECURITY DEBT -> REQUIREMENT/CONTROL 
    -> VALIDATION -> REDESIGN
```

## Design Principles

### Avoid Product-First Selection

**Do not select a security product before the relevant security objective, threat,
requirement and control have been established.**

**Rationale**: Product-first thinking leads to:
- Tool misalignment with actual threats
- Over-engineered controls for non-existent threats
- Vendor lock-in without business justification
- Difficulty validating control effectiveness

**Correct decision order**: Objective → Threat → Requirement → Control → Product

### Composition Over Duplication

**Do not duplicate the complete Security Copilot prompt inside the
Design-by-Security prompt.** The integration is compositional:

- **Design-by-Security** focuses on *architecture* and *requirements*.
- **Security Copilot v4** focuses on *operational evidence* and *tactical response*.
- Each system calls the other at well-defined boundaries (see adapter contract).

This separation allows each system to evolve independently and makes the integration
testable, auditable, and maintainable.

### Security Gate Criteria

At the GATE stage, verify before proceeding to BUILD/DEPLOY:

- [ ] All identified threats are mapped to security requirements
- [ ] All security requirements have assigned controls (ownership defined)
- [ ] All controls have documented validation criteria and success measures
- [ ] Residual risk is assessed and acceptable per business objectives
- [ ] Operational feedback loops and telemetry are instrumented
- [ ] Incident response procedures reference design decisions and controls
- [ ] Design assumptions are documented (for future threat reviews)

## Integrated Lifecycle

```
DESIGN -> BUILD -> DEPLOY -> DETECT -> RESPOND -> LEARN -> REDESIGN
```

### Stage-by-stage responsibility

| Stage | Owner | Activity |
|-------|-------|----------|
| **DESIGN** | Design-by-Security | Architecture, threat modeling, control specification, gate approval |
| **BUILD** | Engineering + APPSEC | Implementation of controls per specification |
| **DEPLOY** | Engineering + OPS | Operational deployment; enable telemetry and monitoring |
| **DETECT** | Security Copilot v4 | SOC triage, alert detection, threat hunting |
| **RESPOND** | Security Copilot v4 | Incident response, containment, tactical remediation |
| **LEARN** | Security Copilot v4 | Root cause analysis, create security debt findings |
| **REDESIGN** | Design-by-Security | Evaluate findings, update threat model, revise controls, gate approval |

## Example: Operational Lesson Driving Design Change

**Scenario**: Security Copilot detects unauthenticated API endpoints in production

1. **DETECT/RESPOND** (Security Copilot v4)
   - Triage identifies public endpoints accepting data without authentication
   - Tactical mitigation: rate limiting, access logs

2. **LEARN** (Security Copilot v4)
   - Root cause analysis: Application shipped without authentication enforcement
   - Finding: "Missing authentication control on user-facing API endpoints"

3. **REDESIGN** (Design-by-Security)
   - Threat model review: Which threats did the missing control allow?
   - Requirement: "All user-facing APIs must enforce authentication per trust boundary"
   - Control: "API gateway enforces bearer token validation with scope-based access control"
   - Validation: "Automated tests; audit logs confirm token validation on every request"

4. **GATE** (Design-by-Security)
   - Confirm new control prevents the detected threat class
   - Update residual risk and design assumptions
   - Approve for BUILD/DEPLOY

5. **BUILD/DEPLOY** (Engineering)
   - Implement authentication control per specification
   - Deploy with telemetry enabled

---

## Related Documentation

- [**DESIGN-BY-SECURITY-ADAPTER.md**](./DESIGN-BY-SECURITY-ADAPTER.md) — Executable hand-off contract and schema definitions
- [**Threat Modeling Framework**](../../docs/threat-modeling.md) — Attack path and abuse case methodology
- **Security Copilot v4 Documentation** — Operational playbooks and detection engineering
- [**Control Validation Framework**](../../docs/control-validation.md) — How to measure control effectiveness

## FAQ

**Q: When should Design-by-Security revisit a threat model?**  
A: After any major architectural change, new operational finding (LEARN phase), or annually. Always before a security gate decision.

**Q: Can Security Copilot v4 create new security requirements?**  
A: No. Security Copilot identifies findings and debt; Design-by-Security creates or modifies requirements based on those findings and threat models.

**Q: What if an operational finding contradicts a control assumption?**  
A: Escalate to REDESIGN immediately. The threat model may be incomplete, or the control may have a gap. This is a gate re-evaluation.

**Q: How do we know a control is actually working?**  
A: Per the Validation stage: define measurable success criteria, implement automated checks, and report control status in operational metrics.
