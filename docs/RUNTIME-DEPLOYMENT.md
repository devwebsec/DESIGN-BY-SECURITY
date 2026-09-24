# Security Copilot Runtime Deployment

The repository contains a thin runtime boundary around the existing deterministic Design-by-Security engine. The runtime is intended to be deployed as an internal security-analysis service, not as a CI-only script.

## Runtime topology

```text
Web UI / CLI / REST
        |
      HTTPS
        |
 Caddy internal gateway :443
        |
 Security Copilot API :8080 (private network only)
        |
 deterministic Design-by-Security validator
```

The CLI is a client of the server. It must not implement a second security-decision path.

## Supported deployment

For the intended internal service deployment use `deployment/internal/`:

```bash
cd deployment/internal
cp .env.example .env
chmod 600 .env
# Set SECURITY_COPILOT_API_TOKEN to a high-entropy secret.
docker compose up -d --build
docker compose ps
```

Only the Caddy gateway publishes host ports 80/443. The API is exposed only to the Compose network and is not published directly to the host.

The expected service URL is:

```text
https://security-copilot.internal
```

Internal DNS must resolve that hostname to the deployment host. Caddy uses `tls internal` by default; managed clients should trust the Caddy internal CA rather than using `curl -k` in normal operation.

## API contract

### Health

`GET /health`

Health is intentionally unauthenticated so container/load-balancer health checks can operate without credentials.

### Projects

`GET /api/v1/projects`

`POST /api/v1/projects`

Request:

```json
{
  "name": "web-api",
  "artifact": { "...": "normalized security-design artifact" }
}
```

Project and artifact endpoints require bearer authentication.

### Analyze

`POST /api/v1/projects/{project_id}/analyze`

The endpoint invokes the repository's deterministic validator. A `PASS` means the artifact satisfied the current validator contract; it is not a claim that the real system is secure. A `FAIL` is returned as an analysis result and does not mean that the HTTP request itself failed.

## Authentication

The internal deployment requires:

```text
Authorization: Bearer <SECURITY_COPILOT_API_TOKEN>
```

The token is supplied through environment/secret management and is never stored in project artifacts or the SQLite database. The API compares bearer credentials without logging the token.

For local development, authentication can be disabled by omitting `SECURITY_COPILOT_REQUIRE_AUTH`; production/internal deployment must keep it enabled.

## Persistence

v0.1 uses SQLite for a zero-dependency, single-node deployment. The database lives in the `security_copilot_data` volume. SQLite WAL mode and a busy timeout are enabled for normal concurrent request handling.

The API contract does not expose SQLite-specific semantics, so PostgreSQL can be introduced later for multi-user/high-availability deployment without changing the CLI contract.

## Security boundary

The LLM/Copilot provider remains outside the deterministic security gate. AI output may enrich analysis and recommendations, but it must not silently convert an unknown into evidence or override a failing deterministic validation.

Destructive response actions require explicit human authorization in the deterministic contract.

## Operational hardening

Before exposing the service beyond a controlled internal network:

- use a strong secret from a secret manager;
- restrict TCP/443 to trusted corporate/VPN networks;
- distribute and rotate the trusted internal CA correctly;
- back up and protect `security_copilot_data`, `caddy_data` and `caddy_config`;
- add SSO/OIDC and RBAC before multi-user deployment;
- add centralized audit logging before handling sensitive incident data;
- replace `tls internal` with enterprise PKI when required;
- introduce PostgreSQL/Redis only when operational requirements justify them.

## Verification

Local runtime smoke test:

```bash
PORT=18080 bash apps/runtime-smoke.sh
```

The smoke test covers:

1. unauthenticated health;
2. rejection of protected API access without a bearer token;
3. authenticated project creation/listing;
4. deterministic `PASS` boundary;
5. deterministic `FAIL` boundary.

The Security Design Integration workflow runs the same runtime smoke test before the existing deterministic L4-L8 and builder validation gates.
