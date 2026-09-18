# DESIGN-BY-SECURITY — Dependency Contract

## Scope

This repository is intentionally lightweight. The security-design pipeline is implemented with shell scripts, Python validation utilities, YAML/JSON contracts and a packaged Security Copilot skill. There is no application package manager or production service runtime in the repository.

## Runtime dependencies

| Dependency | Used by | Required capability | Verification |
|---|---|---|---|
| Bash | all `.sh` pipeline/build scripts | shell execution with `set -euo pipefail` | `bash -n` + execution |
| Python 3 | semantic/graph validators | standard-library validation/fuzz logic | `python3 -m py_compile` + execution |
| `zip` | `build-security-copilot.sh` | package creation | builder execution |
| `unzip` | builder | archive validation/extraction | builder integrity tests |
| Git | CI hygiene | diff/check repository state | `git diff --check`, `git grep` |
| GitHub Actions runner | CI only | Ubuntu execution environment | workflow run |

The Python validators must not silently acquire third-party runtime dependencies. If a future implementation adds one, it must be declared here and validated in CI.

## GitHub Actions dependencies

External actions are pinned to immutable commit SHAs in `.github/workflows/security-design-integration.yml`. The workflow currently uses:

- `actions/checkout` pinned to a v4 commit;
- `actions/upload-artifact` pinned to a v4.6.2 commit.

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

The supported local validation entry point is:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
```

The reproducible package build is:

```bash
bash build-security-copilot.sh
```

The CI workflow additionally performs shell/Python/JSON syntax validation and the GOST process/evidence gates.
