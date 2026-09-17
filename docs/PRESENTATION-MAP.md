# Presentation → Repository Implementation Map

The supplied presentation is treated as the target architecture. This map prevents the repository from becoming a collection of disconnected prompts.

| Presentation concept | Repository implementation |
|---|---|
| Design-by-Security OS | `design-by-security/` + root master prompt |
| Security Copilot v4 | `skills/security-copilot/` |
| Design → Build → Deploy → Detect → Respond → Learn → Redesign | `tests/security-design-pipeline/pipeline-manifest.yml` |
| Asset / Data Flow / Trust Boundary / Threat / Attack Path | design prompt + artifact contract + graph tests |
| Requirements → Controls → Validation → Gate | semantic validator + hard-fail conditions |
| Detection-by-Design | Design ↔ Copilot adapters + critical-path gate |
| Feedback / Root Cause / Security Debt / Redesign | TC-004 + semantic invariants |
| Human-in-the-Loop | destructive-action hard-fail + operational contract |
| Mode / Command separation | Security Copilot v4 skill |
| DevSecOps security lifecycle | Copilot DevSecOps engine + supply-chain scenario |
| GOST R 56939-2024 overlay | `gost-compliance/` |
| 25 secure-development processes | `gost-compliance/regulations/01..25` |
| 13 machine-readable artifacts | `gost-compliance/artifacts/` |
| Level 8 validation | `gost-compliance/pipeline/gost-validate.sh` |
| Audit evidence package | `gost-compliance/pipeline/evidence-package.sh` |
| Evidence / commit binding | package `metadata/manifest.json` + SHA-256 manifests |

## Validation hierarchy

```text
L1  Structural / repository hygiene
L2  Manifest / contract
L3  Scenario contracts
L4  Semantic relationships
L5  Mutation / metamorphic
L6  Bounded property / graph fuzzing
L7  Security Graph invariants
L8  GOST process overlay
```

Level 8 is a **process/evidence overlay**, not a statement that the repository or an organization is legally certified. Its purpose is to make required process evidence explicit and machine-checkable.
