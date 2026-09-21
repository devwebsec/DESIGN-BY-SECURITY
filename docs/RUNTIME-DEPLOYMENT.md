# Security Copilot Runtime Deployment

## Purpose

The repository now has a thin runtime layer around the existing deterministic Design-by-Security engines. The runtime is intended to be deployed like an internal security analysis service, not as a CI-only script.

## Interfaces

```text
                         Security Copilot Server
                                  |
                    +-------------+-------------+
                    |             |             |
                   Web          CLI           REST
                 (future)       client          API
                    |             |             |
                    +-------------+-------------+
                                  |
                         deterministic engine
                                  |
                    Design-by-Security validation
```

The CLI is a client. It must not fork the security decision logic into a second implementation.

## Single-node deployment

```bash
cp .env.example .env
# Replace SECURITY_COPILOT_API_TOKEN with a strong random value.

docker compose -f deployment/docker/docker-compose.yml up -d --build
curl http://127.0.0.1:8080/health
```

For an internal DNS name, place a TLS reverse proxy in front of port 8080 and publish only HTTPS. The application itself should remain on the internal network.

## API

### Health

`GET /health`

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

### Analyze

`POST /api/v1/projects/{project_id}/analyze`

The endpoint invokes the repository's deterministic validator. A `PASS` means the artifact satisfied the current validator contract; it is not a claim that the real system is secure.

## Authentication

When `SECURITY_COPILOT_API_TOKEN` is set, API requests require:

`Authorization: Bearer <token>`

The token is supplied through environment/secret management and is never stored in project artifacts or the SQLite database.

## Security boundary

The LLM/Copilot provider is deliberately outside the deterministic security gate. AI output can enrich analysis and recommendations, but it must not silently convert an unknown into evidence or override a failing deterministic validation.

## Persistence

v0.1 uses SQLite for a zero-dependency, auditable single-node deployment. The API contract does not expose SQLite-specific semantics, so a PostgreSQL backend can be introduced later for multi-user/high-availability deployment without changing the CLI contract.

## Production hardening before exposure

- terminate TLS at a reverse proxy;
- use a strong secret from a secret manager;
- restrict network access to trusted security/admin networks;
- back up the data volume;
- add SSO/OIDC and RBAC before multi-user deployment;
- add audit logging before handling sensitive incident data;
- add PostgreSQL/Redis only when operational requirements justify them.
