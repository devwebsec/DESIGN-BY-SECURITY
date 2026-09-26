#!/usr/bin/env python3
"""Convert the canonical semantic artifact into the Level-7 security graph."""
from __future__ import annotations
import json
import sys
from pathlib import Path


def criticality(x: dict) -> str | None:
    value = x.get("criticality", x.get("severity"))
    if value is None:
        return None
    return str(value).upper()


def node(items, typ):
    result = []
    for x in items:
        n = {"id": x["id"], "type": typ}
        c = criticality(x)
        if c is not None:
            n["criticality"] = c
        if typ == "validation":
            result_value = str(x.get("result", x.get("status", ""))).upper()
            if result_value:
                n["status"] = result_value
        result.append(n)
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: from_semantic.py INPUT.json OUTPUT.json", file=sys.stderr)
        return 2

    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    required = [
        "assets", "threats", "attack_paths", "security_requirements",
        "controls", "validations", "detections", "lessons_learned", "redesign",
    ]
    missing = [k for k in required if not isinstance(d.get(k), list)]
    if missing:
        print("missing canonical collections: " + ", ".join(missing), file=sys.stderr)
        return 3

    nodes = []
    edges = []
    for key, typ in [
        ("assets", "asset"), ("threats", "threat"),
        ("attack_paths", "attack_path"), ("security_requirements", "requirement"),
        ("controls", "control"), ("validations", "validation"),
        ("detections", "detection"), ("lessons_learned", "root_cause"),
        ("redesign", "redesign"),
    ]:
        nodes += node(d[key], typ)

    response_id = "RESPONSE-001"
    handoff = d.get("operational_handoff", {})
    nodes.append({
        "id": response_id,
        "type": "response",
        "destructive": True,
        "human_approval_required": handoff.get("human_approval_required_for_destructive_actions") is True,
    })

    def add(source, target):
        edges.append({"source": source, "target": target})

    for x in d["threats"]:
        for asset_id in x.get("asset_ids", []):
            add(asset_id, x["id"])

    for x in d["attack_paths"]:
        for threat_id in x.get("threat_ids", []):
            add(threat_id, x["id"])
        for detection_id in x.get("detection_ids", []):
            add(x["id"], detection_id)

    attack_paths_by_threat = {}
    for ap in d["attack_paths"]:
        for threat_id in ap.get("threat_ids", []):
            attack_paths_by_threat.setdefault(threat_id, []).append(ap["id"])

    for x in d["security_requirements"]:
        for threat_id in x.get("threat_ids", []):
            for ap_id in attack_paths_by_threat.get(threat_id, []):
                add(ap_id, x["id"])

    for x in d["controls"]:
        for requirement_id in x.get("requirement_ids", []):
            add(requirement_id, x["id"])

    for x in d["validations"]:
        for control_id in x.get("control_ids", []):
            add(control_id, x["id"])

    for x in d["detections"]:
        for ap_id in x.get("attack_path_ids", []):
            if handoff.get("response_owner"):
                add(x["id"], response_id)

    for x in d["redesign"]:
        lesson_id = x.get("source_lesson_id")
        if lesson_id:
            add(lesson_id, x["id"])

    gate_obj = d.get("security_gate", {})
    if not isinstance(gate_obj, dict):
        print("security_gate must be an object", file=sys.stderr)
        return 4
    graph = {
        "security_gate": {
            "decision": str(gate_obj.get("decision", "")).upper(),
            "review_outcome": str(gate_obj.get("review_outcome", "")).upper() or None,
            "residual_risk": gate_obj.get("residual_risk"),
            "evidence_boundary": gate_obj.get("evidence_boundary"),
            "blocking_conditions": gate_obj.get("blocking_conditions", []),
            "unresolved_critical_design_flaws": gate_obj.get("unresolved_critical_design_flaws", []),
            "unknowns": gate_obj.get("unknowns", []),
        },
        "nodes": nodes,
        "edges": edges,
    }
    Path(sys.argv[2]).write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated canonical graph: {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
