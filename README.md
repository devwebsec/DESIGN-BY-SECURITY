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
├── deployment/internal/         # internal HTTPS deployment (Caddy + API)
├── deployment/docker/            # API container image / single-node image
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

The runtime is deployable as an internal service:

```text
https://security-copilot.internal
            │
            ▼
     Caddy HTTPS gateway
            │
            ▼
   Security Copilot API
            │
            ▼
 Design-by-Security engine
```

The API container is **not** published directly by the internal deployment. Only the gateway publishes TCP/80 and TCP/443. The API requires bearer authentication; `/health` remains intentionally unauthenticated for health checks.

### Internal deployment

```bash
cd deployment/internal
cp .env.example .env
chmod 600 .env
# set SECURITY_COPILOT_API_TOKEN to a strong random secret

docker compose up -d --build
docker compose ps
```

The expected URL is `https://security-copilot.internal`. See `deployment/internal/README.md` and `docs/RUNTIME-DEPLOYMENT.md` for DNS, internal CA trust, persistence and operational hardening.

The CLI is a client of the same API:

```bash
SECURITY_COPILOT_URL=https://security-copilot.internal \
SECURITY_COPILOT_API_TOKEN='<token>' \
python3 apps/cli/security_copilot.py health
```

For local development, the server can still be started directly on `127.0.0.1`/a development port, but an externally reachable deployment should use the internal HTTPS gateway.

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
