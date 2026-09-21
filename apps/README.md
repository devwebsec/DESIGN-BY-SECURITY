# Security Copilot Runtime

This directory adds the first product/runtime layer to the repository.

## Architecture

- `server/server.py` — dependency-free HTTP API and runtime boundary.
- `cli/security_copilot.py` — thin CLI client; it does not duplicate the engine.
- `deployment/docker/` — single-node deployment for an internal installation.

The deterministic Design-by-Security validator remains the security decision engine. The API stores project artifacts and invokes that validator for analysis. AI/LLM providers are intentionally not hard-coded into the gate path.

## Run locally

```bash
python3 apps/server/server.py
```

Then:

```bash
curl http://127.0.0.1:8080/health
```

## Run as a service

```bash
cp .env.example .env
# set a strong SECURITY_COPILOT_API_TOKEN

docker compose -f deployment/docker/docker-compose.yml up -d --build
```

The initial runtime is deliberately small and auditable. PostgreSQL, Redis, Web UI and LLM providers can be introduced behind the same API contract without making the deterministic security gate depend on an AI provider.

## CLI

```bash
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 health
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 projects
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 create web-api tests/security-design-pipeline/semantic/fixtures/valid-web-api.json
```

The API token, when enabled, is passed as `Authorization: Bearer ...` and is never stored in the project artifact.
