# GOST R 56939-2024 — Security Development Process Overlay

This directory implements a **machine-checkable process overlay** for the software-development lifecycle referenced by the Design-by-Security presentation.

It is not a legal certification and does not by itself establish regulatory compliance. Actual applicability, interpretation and evidence acceptance require qualified organizational/legal review.

## 25-process model

The overlay is grouped into three lifecycle areas:

- **Planning (5.1–5.5):** planning, training, requirements, configuration, deficiencies.
- **Implementation (5.6–5.21):** architecture, threat modeling, coding, review, analysis/testing, build, secrets, dependencies, supply chain, release and delivery.
- **Operation (5.22–5.25):** maintenance, vulnerability response, security monitoring/hunting and decommissioning.

Each process has:

1. a human-readable regulation/checklist;
2. a machine-readable artifact template where applicable;
3. validation references in `GOST-MAPPING.yml`;
4. explicit hard-fail semantics where a missing artifact creates a material design-control gap.

## Validation principle

```text
PROCESS → REQUIRED ARTIFACT → CROSS-REFERENCE → EVIDENCE → VALIDATION
```

A failed Level 8 validation returns the finding to Design-by-Security as `REDESIGN_REQUIRED`; it does not create a claim of compliance.
