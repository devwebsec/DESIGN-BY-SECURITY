# DESIGN-BY-SECURITY

## Security Architecture & Engineering Operating System

This repository implements the architecture described by the Design-by-Security presentation as an executable, testable security engineering operating model.

It combines two complementary planes:

- **Design-by-Security** — architecture-first security design, threat modeling, requirements, controls, validation and security gates.
- **Security Copilot v4** — operational SOC, IR, DFIR, hunting, detection and security-engineering analysis.

The planes are intentionally separated and connected by explicit adapters.

### Master operating model

```text
BUSINESS → SECURITY GOALS → ASSETS → DATA FLOWS → TRUST BOUNDARIES
→ ATTACK SURFACE → THREAT MODEL → ATTACK PATHS → REQUIREMENTS
→ CONTROLS → ARCHITECTURE → BUILD → VALIDATE → DEPLOY → DETECT
→ RESPOND → RECOVER → LEARN → REDESIGN
```

### Repository structure

```text
.
├── apps/                         # runtime server + thin CLI client
├── deployment/docker/            # single-node deployment
├── .github/workflows/            # CI/security verification boundary
├── design-by-security/           # design plane + adapters
├── skills/security-copilot/      # Security Copilot skill
├── tests/security-design-pipeline/# L4 → L7 deterministic verification
├── schemas/                      # machine-readable contracts
├── examples/                     # reference artifacts
├── gost-compliance/              # process/evidence overlay
├── docs/                         # architecture, contracts, runtime docs
├── DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md
├── AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md
├── SECURITY-METRICS.md
├── DEPENDENCIES.md
├── REPOSITORY-MAP.md
├── build-security-copilot.sh
├── LICENSE
└── SECURITY.md
```

Use `REPOSITORY-MAP.md` as the canonical navigation map. `SECURITY-METRICS.md` defines the 12-axis measurement model and repository KPIs. `DEPENDENCIES.md` defines the runtime and CI dependency contract.

## Runtime deployment

The repository now includes a thin server/API and CLI boundary so the solution can be deployed as an internal service, analogous to the deployment model of a security analysis platform.

```text
https://security-copilot.internal
            │
            ▼
   Security Copilot API
            │
            ▼
 Design-by-Security engine
```

The CLI is a client of the same API:

```bash
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 health
```

Single-node deployment:

```bash
cp .env.example .env
# set SECURITY_COPILOT_API_TOKEN

docker compose -f deployment/docker/docker-compose.yml up -d --build
```

See `docs/RUNTIME-DEPLOYMENT.md` for the API contract and hardening requirements.

## Design principles

Security is a design property, not a post-production patch.

The architecture process starts with business context and evidence, not technology selection. Critical attack paths must have prevention, detection, response and recovery coverage or an explicit detection gap. Unknowns are preserved as unknowns and never silently promoted to evidence.

Controls are assessed as:

`EXISTS → CONFIGURED → EFFECTIVE → TESTED`

Compliance mapping is not treated as proof of actual security.

## Feedback loop

Operational findings return to architecture through:

`OBSERVATION → FINDING → ROOT CAUSE → SECURITY DEBT / DESIGN FLAW → REQUIREMENT OR CONTROL CHANGE → VALIDATION → REDESIGN`

Destructive response actions require human authorization.

## Machine-readable contract

The canonical required artifact set is defined by `tests/security-design-pipeline/pipeline-manifest.yml`; a human-readable explanation is in `docs/SECURITY-DESIGN-CONTRACT.md`; the machine-readable artifact shape is in `schemas/security-design.schema.json`.

A reference web API artifact is available under `examples/web-api/`.

## Integration validation

Run locally with:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
```

Runtime smoke test:

```bash
PORT=18080 bash apps/runtime-smoke.sh
```

For the process/evidence overlay:

```bash
bash gost-compliance/pipeline/gost-validate.sh
bash gost-compliance/pipeline/evidence-package.sh ./evidence-output/package
```

The same gates run in GitHub Actions for `main`, integration, hardening and audit branches and for pull requests targeting `main`.

## Presentation alignment

`docs/ARCHITECTURE.md`, `docs/ENGINE-CATALOG.md`, `docs/PRESENTATION-MAP.md` and `REPOSITORY-MAP.md` translate the presentation into repository-level implementation responsibilities. The presentation's architecture is therefore represented by executable contracts, reference artifacts, adapters, measurements, runtime interfaces and CI gates rather than by documentation alone.
