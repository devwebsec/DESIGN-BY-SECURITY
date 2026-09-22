# Internal Security Copilot deployment

This stack exposes the Security Copilot runtime as an internal HTTPS service:

`Web UI / CLI / REST -> Caddy HTTPS gateway -> Security Copilot API -> deterministic Design-by-Security engine`

The API container is not published directly to the host. Only ports 80/443 are exposed by the gateway. The API keeps bearer authentication enabled.

## Prerequisites

- Docker Engine with Compose v2
- internal DNS record resolving `security-copilot.internal` to the deployment host
- network policy/firewall allowing clients to reach TCP/443
- a deployment host with persistent storage for the SQLite volume

## First deployment

```bash
cd deployment/internal
cp .env.example .env
chmod 600 .env
# Replace SECURITY_COPILOT_API_TOKEN with a random high-entropy value.
docker compose up -d --build
docker compose ps
```

The API should remain reachable only through the gateway. Verify locally on the host:

```bash
curl -k https://security-copilot.internal/health
```

Expected response contains:

```json
{"status":"ok","service":"security-copilot","version":"0.1"}
```

## Internal CA trust

The gateway uses Caddy's internal CA (`tls internal`). This is intentional for a private service where the deployment team controls client trust. Install the Caddy root CA on managed clients rather than using `curl -k` in normal operation.

To inspect the generated CA material:

```bash
docker compose exec gateway caddy list-certificates
```

The persistent `caddy_data` volume must be backed up and protected because it contains the gateway's certificate state and private CA material.

## API authentication

Keep the bearer token out of Git. The runtime requires:

```text
Authorization: Bearer <SECURITY_COPILOT_API_TOKEN>
```

Health is intentionally unauthenticated for load balancer/container health checks. Project and analysis endpoints require authentication.

## Operational checks

```bash
docker compose ps
docker compose logs --tail=100 gateway
docker compose logs --tail=100 security-copilot
curl -k https://security-copilot.internal/health
```

For a functional API check, use the repository CLI with the service URL and token.

## Production notes

- Do not publish port `8080` from the API container.
- Do not commit `.env` or real API tokens.
- Restrict TCP/443 to trusted corporate/VPN networks.
- Prefer a centrally managed DNS record and backup policy for the persistent volumes.
- For enterprise PKI, replace `tls internal` with a certificate issued by the organization's CA and mount the certificate/key into the gateway.
- This deployment does not turn the LLM/provider into the deterministic security decision-maker; the existing deterministic validator remains the PASS/FAIL boundary.
