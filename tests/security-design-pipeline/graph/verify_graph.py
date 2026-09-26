#!/usr/bin/env python3
"""Level 7 deterministic Security Graph Invariant Engine."""
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict
from pathlib import Path

ALLOWED_GATE = {"PASS", "FAIL", "CONDITIONAL"}
ALLOWED_REVIEW = {
    "APPROVE", "APPROVE_WITH_CONDITIONS", "REDESIGN_REQUIRED", "DO_NOT_APPROVE",
}


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
        raise ValueError("artifact must contain nodes[] and edges[]")
    return data


def verify(data):
    errors = []
    warnings = []
    nodes = data["nodes"]
    edges = data["edges"]
    ids = []
    by_id = {}
    for n in nodes:
        i = n.get("id") if isinstance(n, dict) else None
        if not i:
            errors.append("node_without_id")
            continue
        if i in by_id:
            errors.append(f"duplicate_node_id:{i}")
        by_id[i] = n
        ids.append(i)
    out = defaultdict(list)
    inc = defaultdict(list)
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s not in by_id or t not in by_id:
            errors.append(f"dangling_reference:{s}->{t}")
            continue
        out[s].append(t)
        inc[t].append(s)
    typ = lambda i: by_id[i].get("type")
    for n in nodes:
        i = n.get("id")
        if not i:
            continue
        if n.get("type") == "asset" and str(n.get("criticality", "")).upper() == "CRITICAL" and not out[i]:
            errors.append(f"isolated_critical_asset:{i}")
    for n in nodes:
        if n.get("type") != "threat" or str(n.get("criticality", "")).upper() != "CRITICAL":
            continue
        tid = n["id"]
        aps = [x for x in out[tid] if typ(x) == "attack_path"]
        if not aps:
            errors.append(f"critical_threat_without_attack_path:{tid}")
            continue
        if not any(typ(x) == "detection" for x in out[tid]):
            warnings.append(f"critical_threat_without_direct_detection:{tid}")
        for ap in aps:
            reqs = [x for x in out[ap] if typ(x) == "requirement"]
            if not reqs:
                errors.append(f"attack_path_without_requirement:{ap}")
            for r in reqs:
                ctrls = [x for x in out[r] if typ(x) == "control"]
                if not ctrls:
                    errors.append(f"requirement_without_control:{r}")
                for c in ctrls:
                    vals = [x for x in out[c] if typ(x) == "validation"]
                    if not vals:
                        errors.append(f"control_without_validation:{c}")
    for n in nodes:
        if n.get("type") == "control" and not inc[n["id"]]:
            errors.append(f"orphan_control:{n['id']}")
        if n.get("type") == "validation" and str(n.get("status", "")).upper() != "PASS":
            gate = data.get("security_gate")
            if isinstance(gate, dict) and gate.get("decision") == "PASS":
                errors.append(f"pass_gate_with_failed_validation:{n['id']}")
        if n.get("type") == "response" and n.get("destructive") is True and n.get("human_approval_required") is not True:
            errors.append(f"destructive_action_without_human_approval:{n['id']}")

    gate = data.get("security_gate")
    if not isinstance(gate, dict):
        errors.append("security_gate_must_be_object")
    else:
        decision = str(gate.get("decision", "")).upper()
        review = str(gate.get("review_outcome", "")).upper()
        if decision not in ALLOWED_GATE:
            errors.append(f"invalid_security_gate_decision:{decision}")
        if review and review not in ALLOWED_REVIEW:
            errors.append(f"invalid_review_outcome:{review}")
        if decision == "FAIL" and review in {"APPROVE", "APPROVE_WITH_CONDITIONS"}:
            errors.append(f"review_outcome_conflict:{decision}/{review}")
        if decision == "FAIL" and not gate.get("unresolved_critical_design_flaws"):
            errors.append("unresolved_critical_design_flaw:decision=FAIL without listed flaws")
        if review == "APPROVE_WITH_CONDITIONS" and not gate.get("residual_risk"):
            errors.append("approve_with_conditions_without_residual_risk")
        if review and review != "APPROVE" and not (gate.get("blocking_conditions") or gate.get("residual_risk")):
            errors.append(f"non_approve_without_conditions:{review}")
        if not gate.get("evidence_boundary"):
            errors.append("security_gate_missing_evidence_boundary")
        if gate.get("unresolved_critical_design_flaws"):
            errors.append("unresolved_critical_design_flaw:gate contains unresolved flaws")
        if gate.get("unknowns"):
            errors.append("unknown_presented_as_evidence:gate contains unresolved unknowns")

    if isinstance(gate, dict) and str(gate.get("decision", "")).upper() == "PASS" and any(
        n.get("type") == "validation" and str(n.get("status", "")).upper() != "PASS" for n in nodes
    ):
        errors.append("pass_gate_contains_failed_validation")
    lessons = [n for n in nodes if n.get("type") in {"root_cause", "security_debt"}]
    redesign = {n["id"] for n in nodes if n.get("type") == "redesign"}
    if lessons and not redesign:
        errors.append("learn_without_redesign")
    if lessons and redesign and not any(t in redesign for s in out for t in out[s] if typ(s) in {"root_cause", "security_debt"}):
        errors.append("learn_to_redesign_unreachable")
    critical_assets = [n for n in nodes if n.get("type") == "asset" and str(n.get("criticality", "")).upper() == "CRITICAL"]
    critical_threats = [n for n in nodes if n.get("type") == "threat" and str(n.get("criticality", "")).upper() == "CRITICAL"]
    metrics = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "critical_asset_coverage": sum(bool(out[n["id"]]) for n in critical_assets) / (len(critical_assets) or 1),
        "critical_threat_attack_path_coverage": sum(any(typ(x) == "attack_path" for x in out[n["id"]]) for n in critical_threats) / (len(critical_threats) or 1),
    }
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "warnings": warnings, "metrics": metrics}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("artifact")
    p.add_argument("--report")
    a = p.parse_args()
    try:
        result = verify(load(a.artifact))
    except Exception as e:
        result = {"status": "FAIL", "errors": [str(e)], "warnings": [], "metrics": {}}
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if a.report:
        Path(a.report).write_text(text + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
