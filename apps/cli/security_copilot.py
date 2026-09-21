#!/usr/bin/env python3
"""CLI client for the Security Copilot server."""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_URL = os.getenv("SECURITY_COPILOT_URL", "http://127.0.0.1:8080")


def call(url: str, path: str, method: str = "GET", payload=None):
    headers = {"Accept": "application/json"}
    token = os.getenv("SECURITY_COPILOT_API_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload, ensure_ascii=False).encode()
    req = Request(url.rstrip("/") + path, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read())
        except Exception:
            detail = {"error": str(exc)}
        return exc.code, detail
    except URLError as exc:
        raise SystemExit(f"connection failed: {exc.reason}")


def main():
    parser = argparse.ArgumentParser(prog="security-copilot", description="Security Copilot server client")
    parser.add_argument("--url", default=DEFAULT_URL)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("projects")
    p = sub.add_parser("create", help="create a project from a JSON artifact")
    p.add_argument("name")
    p.add_argument("artifact", type=Path)
    p = sub.add_parser("analyze", help="run deterministic Design-by-Security validation")
    p.add_argument("project_id")
    args = parser.parse_args()

    if args.command == "health":
        code, out = call(args.url, "/health")
    elif args.command == "projects":
        code, out = call(args.url, "/api/v1/projects")
    elif args.command == "create":
        artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
        code, out = call(args.url, "/api/v1/projects", "POST", {"name": args.name, "artifact": artifact})
    else:
        code, out = call(args.url, f"/api/v1/projects/{args.project_id}/analyze", "POST", {})
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if 200 <= code < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
