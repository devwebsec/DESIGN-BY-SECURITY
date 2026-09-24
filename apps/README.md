# Security Copilot Runtime

This directory contains the product/runtime boundary for the repository.

## Architecture

- `server/server.py` — dependency-free HTTP API and runtime boundary.
- `cli/security_copilot.py` — thin CLI client; it does not duplicate the engine.
- `deployment/docker/` — standalone single-node API deployment.
- `deployment/internal/` — recommended internal HTTPS deployment through Caddy.

The deterministic Design-by-Security validator remains the security decision engine. The API stores project artifacts and invokes that validator for analysis. AI/LLM providers are intentionally not hard-coded into the deterministic gate path.

## Run locally

From the repository root:

```bash
python3 apps/server/server.py
curl http://127.0.0.1:8080/health
```

## Standalone container

From the repository root:

```bash
cp .env.example .env
chmod 600 .env
# set a strong SECURITY_COPILOT_API_TOKEN

docker compose --env-file .env -f deployment/docker/docker-compose.yml up -d --build
```

The standalone Compose deployment enables bearer authentication and publishes the API on TCP/8080 for controlled development use. For an internal production-style deployment, use `deployment/internal/` so the API is not directly published.

## CLI

```bash
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 health
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 projects
python3 apps/cli/security_copilot.py --url http://127.0.0.1:8080 create web-api tests/security-design-pipeline/semantic/fixtures/valid-web-api.json
```

When authentication is enabled, provide `SECURITY_COPILOT_API_TOKEN` in the environment. The token is sent only as `Authorization: Bearer ...` and is never stored in the project artifact.
