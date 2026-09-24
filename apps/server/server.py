#!/usr/bin/env python3
"""Minimal dependency-free Security Copilot server."""
from __future__ import annotations

import hmac
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("SECURITY_COPILOT_DB", ROOT / "data" / "security-copilot.db"))
API_TOKEN = os.getenv("SECURITY_COPILOT_API_TOKEN", "")
REQUIRE_AUTH = os.getenv("SECURITY_COPILOT_REQUIRE_AUTH", "false").lower() in {"1", "true", "yes", "on"}
HOST = os.getenv("SECURITY_COPILOT_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
MAX_BODY_BYTES = 10 * 1024 * 1024
MAX_PROJECT_NAME = 200

if REQUIRE_AUTH and not API_TOKEN:
    raise SystemExit("SECURITY_COPILOT_REQUIRE_AUTH is enabled but SECURITY_COPILOT_API_TOKEN is not set")

sys.path.insert(0, str(ROOT / "tests" / "security-design-pipeline" / "semantic"))
try:
    from evaluate import evaluate
except Exception as exc:  # pragma: no cover
    evaluate = None
    IMPORT_ERROR = str(exc)
else:
    IMPORT_ERROR = None


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS projects ("
        "id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL, "
        "updated_at TEXT NOT NULL, artifact TEXT NOT NULL)"
    )
    return conn


def analyze_artifact(artifact: dict) -> dict:
    if evaluate is None:
        raise RuntimeError(f"validator import failed: {IMPORT_ERROR}")
    import tempfile
    from pathlib import Path as _Path

    with tempfile.TemporaryDirectory() as tmp:
        p = _Path(tmp) / "artifact.json"
        p.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            evaluate(p)
            return {"status": "PASS", "errors": []}
        except Exception as exc:
            return {"status": "FAIL", "errors": [str(exc)]}


class Handler(BaseHTTPRequestHandler):
    server_version = "SecurityCopilot/0.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def auth(self) -> bool:
        if not REQUIRE_AUTH:
            return True
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {API_TOKEN}"
        return hmac.compare_digest(supplied, expected)

    def send_json(self, status: int, obj: dict):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        if status == 401:
            self.send_header("WWW-Authenticate", 'Bearer realm="security-copilot"')
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length) if raw_length is not None else 0
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length < 0:
            raise ValueError("invalid Content-Length")
        if length > MAX_BODY_BYTES:
            raise OverflowError("request body exceeds 10 MiB")
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("application/json"):
            raise TypeError("Content-Type must be application/json")
        return json.loads(self.rfile.read(length) or b"{}")

    def require_auth_or_return(self) -> bool:
        if self.auth():
            return True
        self.send_json(401, {"error": "unauthorized"})
        return False

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self.send_json(200, {"status": "ok", "service": "security-copilot", "version": "0.1"})
            return
        if not self.require_auth_or_return():
            return
        if path == "/api/v1/projects":
            with db() as conn:
                rows = conn.execute(
                    "SELECT id,name,created_at,updated_at FROM projects ORDER BY updated_at DESC"
                ).fetchall()
            self.send_json(200, {"projects": [dict(r) for r in rows]})
            return
        if path.startswith("/api/v1/projects/"):
            pid = path.split("/")[-1]
            with db() as conn:
                row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
            if not row:
                self.send_json(404, {"error": "project_not_found"})
                return
            self.send_json(
                200,
                {
                    "id": row["id"],
                    "name": row["name"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "artifact": json.loads(row["artifact"]),
                },
            )
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        if path == "/health":
            self.send_json(200, {"status": "ok"})
            return
        if not self.require_auth_or_return():
            return

        if path == "/api/v1/projects":
            try:
                body = self.read_json()
            except OverflowError as exc:
                self.send_json(413, {"error": "request_too_large", "detail": str(exc)})
                return
            except Exception as exc:
                self.send_json(400, {"error": "invalid_json", "detail": str(exc)})
                return
            if not isinstance(body, dict):
                self.send_json(400, {"error": "request_body_must_be_object"})
                return
            name = str(body.get("name", "")).strip()
            artifact = body.get("artifact")
            if not name or len(name) > MAX_PROJECT_NAME or not isinstance(artifact, dict):
                self.send_json(
                    400,
                    {"error": "name and object artifact are required; name must be 1-200 characters"},
                )
                return
            pid = str(uuid.uuid4())
            ts = now()
            with db() as conn:
                conn.execute(
                    "INSERT INTO projects VALUES (?,?,?,?,?)",
                    (pid, name, ts, ts, json.dumps(artifact, ensure_ascii=False)),
                )
            self.send_json(201, {"id": pid, "name": name, "created_at": ts, "updated_at": ts})
            return

        parts = path.split("/")
        if len(parts) == 6 and parts[:4] == ["", "api", "v1", "projects"] and parts[5] == "analyze":
            pid = parts[4]
            with db() as conn:
                row = conn.execute("SELECT artifact FROM projects WHERE id=?", (pid,)).fetchone()
            if not row:
                self.send_json(404, {"error": "project_not_found"})
                return
            try:
                result = analyze_artifact(json.loads(row["artifact"]))
            except RuntimeError as exc:
                self.send_json(503, {"error": "validator_unavailable", "detail": str(exc)})
                return
            self.send_json(200, {"project_id": pid, "analysis": result, "timestamp": now()})
            return
        self.send_json(404, {"error": "not_found"})

    def do_PUT(self):
        self.send_json(405, {"error": "method_not_allowed"})

    def do_DELETE(self):
        self.send_json(405, {"error": "method_not_allowed"})

    def do_PATCH(self):
        self.send_json(405, {"error": "method_not_allowed"})


def main() -> int:
    print(f"Security Copilot server listening on {HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
