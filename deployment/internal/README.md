# Internal Security Copilot deployment

This topology exposes the Security Copilot API only through the Caddy HTTPS gateway.

```text
Client / CLI
    |
  HTTPS :443
    |
  Caddy
    |
  private Compose network
    |
  Security Copilot :8080
    |
  deterministic Design-by-Security validator
```

## Deploy

```bash
cd deployment/internal
cp .env.example .env
chmod 600 .env
# edit .env and replace the placeholder token

docker compose config
# optional before startup: docker compose pull

docker compose up -d --build
docker compose ps
```

The API container has no published host port. Only TCP/80 and TCP/443 are published by Caddy.

## DNS and TLS

Resolve `security-copilot.internal` to the deployment host. Caddy uses its internal CA (`tls internal`). Managed clients must trust the Caddy root CA; do not use `curl -k` as an operational workaround.

For enterprise PKI, replace `tls internal` with the approved certificate/key configuration.

## Authentication

All `/api/v1/*` endpoints require:

```text
Authorization: Bearer <SECURITY_COPILOT_API_TOKEN>
```

`GET /health` remains unauthenticated for service health checks.

Never commit `.env` or a real token. Rotate the token through the organization's secret-management process.

## Persistence

SQLite data is stored in the named `security_copilot_data` volume. Caddy state is stored in `caddy_data` and `caddy_config`. Back up all three volumes according to the organization's recovery requirements.

## Verification

```bash
docker compose config
docker compose ps
curl --fail https://security-copilot.internal/health
```
