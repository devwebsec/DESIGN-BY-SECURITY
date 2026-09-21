# DESIGN-BY-SECURITY — Dependency Contract

## Scope

This repository is intentionally lightweight. The security-design pipeline is implemented with shell scripts, Python validation utilities, YAML/JSON contracts and a packaged Security Copilot skill. The repository also contains a dependency-free Python runtime/API and thin CLI client; no third-party Python runtime packages are required by the v0.1 service.

## Runtime dependencies

| Dependency | Used by | Required capability | Verification |
|---|---|---|---|
| Bash | all `.sh` pipeline/build scripts | shell execution with `set -euo pipefail` | `bash -n` + execution |
| Python 3.12+ | runtime server, CLI and semantic/graph validators | standard-library HTTP, SQLite and validation logic | `python3 -m py_compile` + runtime smoke |
| `curl` | runtime smoke test | HTTP API verification | CI smoke execution |
| `zip` | `build-security-copilot.sh` | package creation | builder execution |
| `unzip` | builder | archive validation/extraction | builder integrity tests |
| Docker/Compose | single-node deployment and CI image validation | containerized runtime | `docker build` + deployment smoke |
| Git | CI hygiene | diff/check repository state | `git diff --check`, `git grep` |
| GitHub Actions runner | CI only | Ubuntu execution environment | workflow run |

The Python runtime must not silently acquire third-party dependencies. If a future implementation adds one, it must be declared here and validated in CI.

## GitHub Actions dependencies

External actions are pinned to immutable commit SHAs in `.github/workflows/security-design-integration.yml`. The workflow uses Node.js 24-compatible releases:

- `actions/checkout` pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1);
- `actions/upload-artifact` pinned to `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (v7.0.1).

Do not replace SHA pinning with floating major/minor tags in the security gate.

## Security Copilot skill package

`skills/security-copilot/security-copilot_v4.skill` is a packaged artifact, not a Python/Node dependency tree. The builder validates archive integrity, rejects unsafe archive paths, requires `security-copilot/SKILL.md`, and checks required reference files before producing the final package.

## Dependency integrity requirements

1. Every new executable dependency must have a declared minimum supported version or immutable CI/runtime source.
2. New third-party GitHub Actions must be pinned to a full commit SHA.
3. New package-manager dependencies require a lockfile and a CI installation/test step.
4. Security-sensitive dependencies must have a documented update and vulnerability-monitoring path.
5. Generated artifacts must not embed credentials, tokens or private configuration.
6. Dependency inventory must remain synchronized with `gost-compliance/artifacts/dependencies-inventory.yml` when applicable.

## Reproducibility

The supported local validation entry points are:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
PORT=18080 bash apps/runtime-smoke.sh
```

The reproducible package build is:

```bash
bash build-security-copilot.sh
```

The container image can be validated with:

```bash
docker build --file deployment/docker/Dockerfile --tag security-copilot:ci .
```

The CI workflow additionally performs shell/Python/JSON syntax validation, runtime authentication checks, container image validation, and the GOST process/evidence gates.
