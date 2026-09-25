#!/usr/bin/env python3
"""Dependency-free contract validator for the security-design artifact.

This is intentionally deterministic: it validates the security-design contract
without an LLM and without requiring a third-party JSON Schema package.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_REQUIRED = {
    "intent", "architecture", "assets", "data_flows", "trust_boundaries",
    "threat_model", "attack_paths", "security_requirements", "controls",
    "validation", "security_gate", "operational_handoff", "lessons_learned",
    "redesign", "dynamic_analysis", "fuzzing", "secure_build", "evidence",
}

DA_REQUIRED = {
    "regulation", "roles", "tool_selection", "methods", "module_selection",
    "failure_handling", "remediation", "periodicity", "tools", "modules",
    "scenarios", "reports",
}

FUZZ_REQUIRED = {"campaigns", "periodicity", "completion_criteria", "reports"}
BUILD_REQUIRED = {
    "regulation", "build_system", "source_integrity", "transformations",
    "environment", "reproducibility", "artifacts", "gate",
}
EVIDENCE_REQUIRED = {"manifest", "items"}


def require_keys(obj: object, keys: set[str], label: str) -> list[str]:
    if not isinstance(obj, dict):
        return [f"{label}: expected object"]
    return [f"{label}: missing {key}" for key in sorted(keys - obj.keys())]


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/security-design-pipeline/semantic/fixtures/valid-web-api.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"FAIL contract JSON load: {exc}")
        return 1

    errors: list[str] = []
    errors.extend(require_keys(data, ROOT_REQUIRED, "root"))
    errors.extend(require_keys(data.get("dynamic_analysis"), DA_REQUIRED, "dynamic_analysis"))
    errors.extend(require_keys(data.get("fuzzing"), FUZZ_REQUIRED, "fuzzing"))
    errors.extend(require_keys(data.get("secure_build"), BUILD_REQUIRED, "secure_build"))
    errors.extend(require_keys(data.get("evidence"), EVIDENCE_REQUIRED, "evidence"))

    da = data.get("dynamic_analysis", {})
    if isinstance(da, dict):
        errors.extend(require_keys(da.get("roles"), {"owner", "executor", "reviewer", "defect_owner"}, "dynamic_analysis.roles"))
        errors.extend(require_keys(da.get("failure_handling"), {"events", "procedure"}, "dynamic_analysis.failure_handling"))
        errors.extend(require_keys(da.get("remediation"), {"procedure", "retest_required"}, "dynamic_analysis.remediation"))
        errors.extend(require_keys(da.get("periodicity"), {"dast", "regression"}, "dynamic_analysis.periodicity"))
        for idx, scenario in enumerate(da.get("scenarios", [])):
            errors.extend(require_keys(scenario, {"id", "module_id", "tool_id", "parameters", "start_criteria", "stop_criteria"}, f"dynamic_analysis.scenarios[{idx}]"))

    for idx, campaign in enumerate(data.get("fuzzing", {}).get("campaigns", []) if isinstance(data.get("fuzzing"), dict) else []):
        errors.extend(require_keys(campaign, {"id", "module_id", "tool_id", "corpus", "seed_strategy", "parameters", "duration_limit_seconds", "crash_handling", "stop_criteria"}, f"fuzzing.campaigns[{idx}]"))

    build = data.get("secure_build", {})
    if isinstance(build, dict):
        errors.extend(require_keys(build.get("build_system"), {"name", "version", "runner", "configuration", "source_revision"}, "secure_build.build_system"))
        errors.extend(require_keys(build.get("source_integrity"), {"source_revision_required", "dependency_lock_required", "checksums_required"}, "secure_build.source_integrity"))
        errors.extend(require_keys(build.get("reproducibility"), {"inputs_recorded", "tool_versions_recorded", "commands_recorded", "artifact_digests_recorded"}, "secure_build.reproducibility"))
        errors.extend(require_keys(build.get("artifacts"), {"output", "digest", "signature", "sbom", "provenance"}, "secure_build.artifacts"))

    evidence = data.get("evidence", {})
    if isinstance(evidence, dict) and not isinstance(evidence.get("items"), list):
        errors.append("evidence.items: expected array")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    print(f"PASS contract validation: {path}")
    print("PASS root + dynamic_analysis + fuzzing + secure_build + evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
