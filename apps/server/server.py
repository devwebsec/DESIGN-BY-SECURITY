#!/usr/bin/env python3
"""Minimal dependency-free Security Copilot server.

The server is intentionally thin: deterministic Design-by-Security validation remains
in the repository's existing engine/tests, while this API provides a stable runtime
boundary for Web UI, CLI and integrations.
"""
from __future__ import annotations

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
PORT = int(os.getenv("PORT", "8080"))

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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, artifact TEXT NOT NULL)")
    return conn


def analyze_artifact(artifact: dict) -> dict:
    if evaluate is None:
        return {"status": "error", "error": f"validator import failed: {IMPORT_ERROR}"}
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
        if not API_TOKEN:
            return True
        return self.headers.get("Authorization", "") == f"Bearer {API_TOKEN}"

    def send_json(self, status: int, obj: dict):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 10 * 1024 * 1024:
            raise ValueError("request body exceeds 10 MiB")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self.send_json(200, {"status": "ok", "service": "security-copilot", "version": "0.1"})
            return
        if not self.auth():
            self.send_json(401, {"error": "unauthorized"})
            return
        if path == "/api/v1/projects":
            with db() as conn:
                rows = conn.execute("SELECT id,name,created_at,updated_at FROM projects ORDER BY updated_at DESC").fetchall()
            self.send_json(200, {"projects": [dict(r) for r in rows]})
            return
        if path.startswith("/api/v1/projects/"):
            pid = path.split("/")[-1]
            with db() as conn:
                row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
            if not row:
                self.send_json(404, {"error": "project_not_found"})
                return
            self.send_json(200, {"id": row["id"], "name": row["name"], "created_at": row["created_at"], "updated_at": row["updated_at"], "artifact": json.loads(row["artifact"])})
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        if path == "/health":
            self.send_json(200, {"status": "ok"})
            return
        if not self.auth():
            self.send_json(401, {"error": "unauthorized"})
            return
        try:
            body = self.read_json()
        except Exception as exc:
            self.send_json(400, {"error": "invalid_json", "detail": str(exc)})
            return

        if path == "/api/v1/projects":
            name = str(body.get("name", "")).strip()
            artifact = body.get("artifact")
            if not name or not isinstance(artifact, dict):
                self.send_json(400, {"error": "name and object artifact are required"})
                return
            pid = str(uuid.uuid4())
            ts = now()
            with db() as conn:
                conn.execute("INSERT INTO projects VALUES (?,?,?,?,?)", (pid, name, ts, ts, json.dumps(artifact, ensure_ascii=False)))
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
            result = analyze_artifact(json.loads(row["artifact"]))
            self.send_json(200, {"project_id": pid, "analysis": result, "timestamp": now()})
            return
        self.send_json(404, {"error": "not_found"})


def main() -> int:
    print(f"Security Copilot server listening on 0.0.0.0:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
