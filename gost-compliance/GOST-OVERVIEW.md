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

## 5.11 Dynamic analysis boundary

The 5.11 overlay explicitly records the elements required by the supplied 5.11.3 excerpt:

- roles and responsibilities;
- tool-selection criteria, including fuzzing tools;
- dynamic-analysis methods;
- module/component selection criteria;
- failure handling and remediation;
- repeat-analysis criteria and periodicity;
- fuzzing completion criteria;
- tool name/version/compatibility/runtime parameters;
- selected modules and stable identifiers;
- per-module test scenarios with start/stop criteria;
- dynamic-analysis findings and processing-error results;
- fuzzing duration, abnormal terminations, unique paths and crash analysis.

The machine-readable contract lives in `examples/web-api/security-design.yaml`, `gost-compliance/artifacts/dynamic-analysis.yml` and `gost-compliance/artifacts/fuzzing-targets.yml`.

## 5.12 Secure build boundary

The 5.12 overlay records the build regulation and fixes the build-system/environment evidence boundary:

- source revision and dependency inputs;
- build system, runner and configuration;
- toolchain/environment versions;
- transformation controls;
- reproducibility inputs and commands;
- artifact digests;
- SBOM, provenance and release-signing state.

The machine-readable contract lives in `gost-compliance/artifacts/secure-build.yml` and `gost-compliance/artifacts/build-tools.yml`.

## Validation principle

```text
PROCESS → REQUIRED ARTIFACT → CROSS-REFERENCE → EVIDENCE → VALIDATION
```

A failed Level 8 validation returns the finding to Design-by-Security as `REDESIGN_REQUIRED`; it does not create a claim of compliance.
