# Internal production deployment

This directory is the reference deployment for `security-copilot.internal`.

## Topology

```text
Client
  |
  | HTTPS :443
  v
Caddy (internal CA)
  |
  | Docker network
  v
Security Copilot API :8080
  |
  v
Deterministic Design-by-Security engine
```

Only Caddy publishes host ports (`80` and `443`). The API is exposed only to the
Docker network. The Compose stack waits for the API healthcheck before starting
the gateway.

## Host prerequisites

- Linux host with Docker Engine and Docker Compose v2.
- DNS record resolving `security-copilot.internal` to the host.
- Firewall allowing only the intended internal clients to TCP/443 (and TCP/80
  if HTTP-to-HTTPS redirect is required).
- No host service already bound to TCP/80 or TCP/443.

## Install

```bash
sudo mkdir -p /opt/security-copilot
sudo chown "$USER":"$USER" /opt/security-copilot
cd /opt/security-copilot
git clone https://github.com/devwebsec/DESIGN-BY-SECURITY.git repo
cd repo
cp deployment/internal/.env.example deployment/internal/.env
```

Generate a token and put it in `deployment/internal/.env`:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

Do not commit `.env` or paste the token into logs.

## Deploy

```bash
cd /opt/security-copilot/repo
depLOY=deployment/internal/deploy.sh
chmod 750 "$depLOY"
"$depLOY"
```

The script builds the application image, starts the API and Caddy, and fails if
the API does not become healthy.

## systemd

Copy `security-copilot.service` to `/etc/systemd/system/`, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now security-copilot.service
sudo systemctl status security-copilot.service
```

If the repository is not located at `/opt/security-copilot/repo`, adjust
`WorkingDirectory` in the unit before enabling it.

## Verification

```bash
docker compose -f deployment/internal/docker-compose.yml ps
curl -kI https://security-copilot.internal/health
```

For clients to trust `tls internal`, install the Caddy internal CA root from
the gateway's `/data` volume into the organization's trust store. Do not
replace this with `curl -k` in production clients.

## Backup

The API database is stored in the named `security_copilot_data` volume. Use
`backup.sh` from a controlled host backup job:

```bash
chmod 750 deployment/internal/backup.sh
sudo BACKUP_DIR=/var/backups/security-copilot deployment/internal/backup.sh
```

Copy the resulting `.db` and `.sha256` files to a separate backup system and
apply the organization's retention and encryption policy.

## Updates

Pull the reviewed commit and redeploy:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
deployment/internal/deploy.sh
```

Do not edit the running container manually. Treat Git + reviewed CI as the
source of truth.

## Security boundary

The HTTP server is a runtime boundary only. Authentication and transport
controls do not replace the deterministic Design-by-Security validator. LLM or
provider integrations must remain outside the deterministic PASS/FAIL path.
