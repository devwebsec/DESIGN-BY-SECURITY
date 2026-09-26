#!/usr/bin/env python3
"""Deterministic validation of the RBPO/GOST control matrix.

This validates repository traceability and evidence routing. It does not make a
legal compliance determination and does not replace qualified review.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "compliance" / "rbpo-control-matrix.yml"
GOST = ROOT / "gost-compliance" / "GOST-MAPPING.yml"
ART = ROOT / "gost-compliance" / "artifacts"

EXPECTED = [f"5.{i}" for i in range(1, 26)]

def fail(msg: str) -> None:
    print(f"FAIL  {msg}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    if not MATRIX.is_file() or MATRIX.stat().st_size == 0:
        fail("RBPO control matrix missing")
    if not GOST.is_file() or GOST.stat().st_size == 0:
        fail("GOST mapping missing")

    text = MATRIX.read_text(encoding="utf-8")
    gost = GOST.read_text(encoding="utf-8")

    if 'document: "ГОСТ Р 56939-2024"' not in text:
        fail("matrix standard identity missing")
    if 'document: "Приказ ФСТЭК России от 11.04.2025 №117"' not in text:
        fail("matrix FSTEC identity missing")
    if 'clause: "50"' not in text:
        fail("matrix FSTEC p.50 mapping missing")

    for pid in EXPECTED:
        if f'gost_process: "{pid}"' not in text:
            fail(f"matrix process {pid} missing")
        if f'id: RBPO-{pid}' not in text:
            fail(f"matrix control RBPO-{pid} missing")
        # Reuse the repository's canonical GOST process catalogue as the source
        # for the artifact route rather than silently inventing another catalogue.
        marker = f'  - id: "{pid}"'
        start = gost.find(marker)
        if start < 0:
            fail(f"canonical GOST process {pid} missing")
        block = gost[start:gost.find("\n  - id:", start + len(marker)) if gost.find("\n  - id:", start + len(marker)) >= 0 else len(gost)]
        artifact_line = next((line.strip() for line in block.splitlines() if line.strip().startswith("artifact:")), None)
        if not artifact_line:
            fail(f"canonical artifact route missing for {pid}")
        artifact = artifact_line.split(":", 1)[1].strip()
        if not (ART / artifact).is_file():
            fail(f"{pid}: evidence artifact missing: {artifact}")

    required_statuses = ["NOT_IMPLEMENTED", "IMPLEMENTED", "VERIFIED", "EFFECTIVE", "EXCEPTION"]
    for status in required_statuses:
        if f"  - {status}" not in text:
            fail(f"status missing: {status}")

    if "security_validation: non-blocking" not in text:
        fail("development non-blocking policy missing")
    if "security_gate: blocking" not in text:
        fail("release blocking policy missing")
    if "exception_requires_authorized_approval: true" not in text:
        fail("authorized exception approval policy missing")

    print(f"PASS  RBPO matrix: {len(EXPECTED)} controls mapped to canonical GOST artifacts")
    print("PASS  development security validation is explicitly non-blocking")
    print("PASS  release security gate is explicitly blocking")
    print("PASS  exception path requires authorized approval")

if __name__ == "__main__":
    main()
