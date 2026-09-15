# Security Copilot v4 + Design-by-Security integration

## Architecture

```text
DESIGN-BY-SECURITY
        |
        +--> Business / Assets / Data / Identities
        |
        +--> Architecture / Trust Boundaries / Attack Surface
        |
        +--> Threat Model / Attack Paths / Abuse Cases
        |
        +--> Security Requirements / Controls
        |
        +--> Validation / Security Gate / Residual Risk
        |
        v
SECURITY COPILOT v4
        |
        +--> SOC / TRIAGE / IR / DFIR
        +--> HUNT / DETECTION / ATT&CK
        +--> IOC / CTI / MALWARE
        +--> ENDPOINT / NETWORK / CLOUD
        +--> DEVSECOPS / APPSEC / VULN
        |
        v
DETECT -> RESPOND -> LEARN -> REDESIGN
```

## Separation of responsibility

Design-by-Security is the upstream architecture and security-design layer.
Security Copilot v4 remains the authoritative operational security skill.

Design-by-Security owns:
- business and security objectives;
- asset, identity and data-flow modeling;
- trust boundaries and attack surface;
- threat modeling and attack paths;
- security requirements;
- security controls and control validation;
- security gates and residual-risk decisions;
- security architecture review;
- redesign driven by operational findings.

Security Copilot v4 owns operational workflows such as SOC triage, incident
response, DFIR, threat hunting, detection engineering, IOC/CTI analysis,
malware analysis and specialized playbooks.

The executable hand-off contract is documented in
`skills/security-copilot/DESIGN-BY-SECURITY-ADAPTER.md`.

## Integration contract

A design task must progress through:

`BUSINESS -> ASSETS -> ARCHITECTURE -> TRUST -> THREATS -> ATTACK PATHS -> REQUIREMENTS -> CONTROLS -> VALIDATION -> GATE`

An operational finding must be able to feed back into design through:

`FINDING -> ROOT CAUSE -> SECURITY DEBT -> REQUIREMENT/CONTROL -> VALIDATION -> REDESIGN`

Do not select a security product before the relevant security objective,
threat, requirement and control have been established.

Do not duplicate the complete Security Copilot prompt inside the
Design-by-Security prompt. The integration is compositional: architecture
controls the security design lifecycle; Security Copilot supplies operational
security analysis and feedback.

## Integrated lifecycle

`DESIGN -> BUILD -> DEPLOY -> DETECT -> RESPOND -> LEARN -> REDESIGN`

At the DESIGN and GATE stages, use the Design-by-Security prompt.
At DETECT/RESPOND/LEARN operational stages, use Security Copilot v4 modes,
playbooks and output contracts. Feed validated operational lessons back into
DESIGN and REDESIGN.
