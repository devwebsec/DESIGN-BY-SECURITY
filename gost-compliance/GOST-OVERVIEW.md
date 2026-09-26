# GOST R 56939-2024 — RBPO compliance/evidence overlay

This directory implements a **machine-checkable implementation and evidence overlay** for ГОСТ Р 56939-2024.

It is not a certification and does not by itself establish legal or regulatory compliance. Applicability, interpretation and evidence acceptance remain an organizational/legal responsibility.

## Regulatory boundary

For independently developed software intended for use in information systems, пункт 50 Приказа ФСТЭК России от 11.04.2025 №117 requires implementation of the measures provided by sections 4 and 5 of ГОСТ Р 56939-2024.

The repository therefore models:

```text
Приказ ФСТЭК №117 п.50
        ↓
ГОСТ Р 56939-2024 §§4–5
        ↓
25 processes in §5
        ↓
control → implementation → evidence → deterministic validation
```

## Exact §5 process catalogue

| ID | Process |
|---|---|
| 5.1 | Planning of secure-software-development processes |
| 5.2 | Employee training |
| 5.3 | Formation and presentation of software security requirements |
| 5.4 | Software configuration management |
| 5.5 | Deficiency and change-request management |
| 5.6 | Software architecture development, refinement and analysis |
| 5.7 | Threat modeling and attack-surface description |
| 5.8 | Coding rules |
| 5.9 | Source-code expertise/review |
| 5.10 | Static source-code analysis |
| 5.11 | Dynamic code analysis |
| 5.12 | Secure software build system |
| 5.13 | Secure build environment |
| 5.14 | Source-code access and integrity |
| 5.15 | Secret security |
| 5.16 | Composition analysis |
| 5.17 | Supply-chain malware checking |
| 5.18 | Functional testing |
| 5.19 | Non-functional testing |
| 5.20 | Security of release of production-ready software |
| 5.21 | Secure software delivery |
| 5.22 | Software support during operation |
| 5.23 | Vulnerability-information response |
| 5.24 | Vulnerability search during operation |
| 5.25 | Secure decommissioning |

The repository mapping is authoritative for process identity and evidence routing. The individual regulation documents are explanatory implementation overlays, not substitutes for the standard text.

## Evidence model

Every process has a machine-readable evidence contract. A control is not considered verified merely because an artifact file exists. The validation path is:

```text
NORMATIVE BASIS
 → CONTROL
 → IMPLEMENTATION
 → EXECUTION/REVIEW
 → EVIDENCE
 → INTEGRITY/TRACEABILITY
 → DETERMINISTIC VALIDATION
```

Where a requirement cannot be proven automatically, the evidence state remains unresolved or requires an authorized human decision; the LLM is not the normative PASS/FAIL authority.

## 5.11 and 5.12 boundaries

5.11 records the dynamic-analysis and fuzzing evidence required by the supplied standard text, including tool/method selection, targets, scenarios, failure handling, repeat analysis and reports.

5.12 records the secure build-system boundary. 5.13 separately covers the security of the build environment. These are intentionally distinct controls.

## Hard-fail principles

The validator hard-fails on missing required process evidence, broken cross-references, fabricated/unknown evidence presented as proof, unresolved critical design flaws, missing required retests, unanalysed fuzzing crashes and missing secure-build provenance/digests.

Validation baseline: repository main commit `9b8574022e88bac427dff6328f5c30fa1d4cee2b`; this branch adds deterministic process/artifact identity checks before merge.
