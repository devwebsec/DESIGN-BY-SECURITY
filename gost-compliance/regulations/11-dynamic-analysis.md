# 5.11 Dynamic Analysis — implementation regulation

> This document is an implementation overlay for the supplied ГОСТ Р 56939-2024 requirements. It is not a certification or legal compliance determination.

## 1. Scope

Dynamic analysis is performed when the selected software component, interface, runtime or threat model requires runtime validation. The design artifact records the decision and the evidence required to reproduce it.

## 2. Roles and responsibilities — 5.11.3.1

- **Owner:** security engineer — owns the regulation and applicability decision.
- **Executor:** QA/Security team — executes DAST and fuzzing campaigns.
- **Reviewer:** security architect — reviews scope, findings and exceptions.
- **Defect owner:** development team — remediates confirmed defects.

Responsibilities, selected tools, methods, target modules, failure handling, remediation, retest criteria and periodicity are recorded in `dynamic_analysis` and `fuzzing`.

## 3. Tool and method selection — 5.11.3.1–5.11.3.2

Tool selection criteria:

1. compatibility with the target module, protocol and runtime;
2. deterministic configuration and reproducible execution;
3. machine-readable results and stable identifiers;
4. ability to preserve crash/reproducer evidence;
5. support for targeted retest and regression execution.

The artifact records tool name, version, type, compatibility and runtime parameters. The framework does not treat an unavailable or failed tool as a security PASS.

## 4. Module selection — 5.11.3.3

The framework selects modules using explicit criteria:

- trust-boundary crossing or externally exposed components;
- high/critical-risk components;
- security-sensitive interfaces;
- modules changed since the previous baseline;
- components implicated by a new threat, vulnerability or incident.

Each selected module has a stable module identifier and repository/component location.

## 5. Test scenarios — 5.11.3.4

Every scenario records:

- module identifier;
- tool identifier;
- tool parameters;
- start criteria;
- stop criteria;
- expected result and evidence location.

## 6. Failure handling and remediation — 5.11.3.1

Tool crash, target crash, hang, timeout, environment failure or processing error is recorded as a test event. Evidence is preserved before cleanup where operationally possible.

A processing failure does **not** become PASS by absence of findings. The responsible team either restores the test environment, changes the method/tool under the documented selection criteria, or records an explicit exception.

Confirmed findings follow:

`finding → defect → fix → targeted retest → regression → closure`

A security-relevant fix requires a targeted retest; a regression test is added when the defect is suitable for repeat detection.

## 7. Periodicity and repeat analysis — 5.11.3.1

Baseline cadence is recorded per project. The reference framework uses:

- DAST: each release;
- regression dynamic analysis: weekly;
- fuzzing: nightly and each release;
- targeted retest: after the relevant fix;
- additional analysis: after material security changes, new attack paths or incident-driven scope changes.

The actual cadence is a project decision and must be recorded rather than assumed.

## 8. Reports — 5.11.3.5

Dynamic-analysis reports record tool triggers, findings, processing errors, remediation references and retest references. Processing errors requiring abnormal termination, timeout or other handling are retained as evidence.

## 9. Fuzzing reports — 5.11.3.6

Each fuzzing campaign records:

- duration;
- number of abnormal/crash terminations;
- unique execution paths or equivalent coverage metric available from the tool;
- crash analysis results;
- corpus and reproducer references;
- tool and version;
- target module;
- campaign result.

A crash without analysis is not a completed campaign. A critical crash blocks PASS unless it is fixed/retested or explicitly handled through the security gate.

## 10. Evidence

Primary artifact: `gost-compliance/artifacts/dynamic-analysis.yml`.

Fuzzing evidence is additionally represented by `gost-compliance/artifacts/fuzzing-targets.yml`. The evidence package records hashes for generated reports and artifacts.
