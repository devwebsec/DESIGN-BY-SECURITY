#!/usr/bin/env python3
"""Deterministic Level-6 bounded semantic/property fuzzer."""
from __future__ import annotations

import copy
import json
import random
import sys
from pathlib import Path

REQUIRED = [
    "intent", "assets", "trust_boundaries", "threats", "attack_paths",
    "security_requirements", "controls", "detections", "validations",
    "security_gate", "operational_handoff", "lessons_learned", "redesign",
]


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        fail("root must be an object")
    for key in REQUIRED:
        if key not in obj:
            fail(f"missing artifact: {key}")
    return obj


def ids(items, label):
    result = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            fail(f"{label}: every item requires id")
        if item["id"] in result:
            fail(f"{label}: duplicate id {item['id']}")
        result[item["id"]] = item
    return result


def refs(values, target, label):
    for value in values or []:
        if value not in target:
            fail(f"{label}: unknown reference {value}")


def evaluate(d: dict) -> None:
    assets = ids(d["assets"], "assets")
    threats = ids(d["threats"], "threats")
    paths = ids(d["attack_paths"], "attack_paths")
    reqs = ids(d["security_requirements"], "security_requirements")
    controls = ids(d["controls"], "controls")
    detections = ids(d["detections"], "detections")
    vals = ids(d["validations"], "validations")
    lessons = ids(d["lessons_learned"], "lessons_learned")
    redesign = ids(d["redesign"], "redesign")

    if bool(lessons) != bool(redesign):
        fail("learning_redesign_imbalance")

    for threat in threats.values():
        refs(threat.get("asset_ids", []), assets, f"threat {threat['id']} asset_ids")
        if str(threat.get("severity", "")).lower() == "critical" and not any(
            threat["id"] in req.get("threat_ids", []) for req in reqs.values()
        ):
            fail(f"critical_threat_without_requirement: {threat['id']}")

    for path in paths.values():
        refs(path.get("threat_ids", []), threats, f"attack_path {path['id']} threat_ids")
        refs(path.get("detection_ids", []), detections, f"attack_path {path['id']} detection_ids")
        if str(path.get("severity", "")).lower() == "critical" and not path.get("detection_ids") and not str(path.get("detection_gap", "")).strip():
            fail(f"critical_attack_path_without_detection_or_explicit_gap: {path['id']}")

    for req in reqs.values():
        refs(req.get("threat_ids", []), threats, f"requirement {req['id']} threat_ids")
        refs(req.get("validation_ids", []), vals, f"requirement {req['id']} validation_ids")
        if not req.get("validation_ids"):
            fail(f"requirement_without_validation: {req['id']}")
        if not any(req["id"] in c.get("requirement_ids", []) for c in controls.values()):
            fail(f"requirement_without_control: {req['id']}")
        for vid in req.get("validation_ids", []):
            if req["id"] not in vals[vid].get("requirement_ids", []):
                fail(f"requirement_validation_mismatch: {req['id']} -> {vid}")

    for control in controls.values():
        refs(control.get("requirement_ids", []), reqs, f"control {control['id']} requirement_ids")
        refs(control.get("validation_ids", []), vals, f"control {control['id']} validation_ids")
        if not control.get("requirement_ids"):
            fail(f"control_without_requirement: {control['id']}")
        if not control.get("validation_ids"):
            fail(f"control_without_validation: {control['id']}")
        for vid in control.get("validation_ids", []):
            if control["id"] not in vals[vid].get("control_ids", []):
                fail(f"control_validation_mismatch: {control['id']} -> {vid}")

    for validation in vals.values():
        refs(validation.get("requirement_ids", []), reqs, f"validation {validation['id']} requirement_ids")
        refs(validation.get("control_ids", []), controls, f"validation {validation['id']} control_ids")
        if str(validation.get("result", "")).lower() != "pass":
            fail(f"validation_not_passed: {validation['id']}")

    for detection in detections.values():
        refs(detection.get("attack_path_ids", []), paths, f"detection {detection['id']} attack_path_ids")
        if not detection.get("attack_path_ids"):
            fail(f"detection_without_attack_path: {detection['id']}")

    handoff = d["operational_handoff"]
    refs(handoff.get("attack_path_ids", []), paths, "operational_handoff attack_path_ids")
    refs(handoff.get("detection_ids", []), detections, "operational_handoff detection_ids")
    if not handoff.get("response_owner"):
        fail("operational_handoff missing response_owner")
    if handoff.get("human_approval_required_for_destructive_actions") is not True:
        fail("destructive_action_without_human_approval")

    gate = d["security_gate"]
    if str(gate.get("decision", "")).upper() != "PASS":
        fail("unresolved_critical_design_flaw: security_gate is not PASS")
    if gate.get("unresolved_critical_design_flaws"):
        fail("unresolved_critical_design_flaw: gate contains unresolved flaws")
    if gate.get("unknowns"):
        fail("unknown_presented_as_evidence: gate contains unresolved unknowns")

    for evidence in d.get("evidence", []):
        if not isinstance(evidence, dict) or not evidence.get("source"):
            fail("unknown_presented_as_evidence: evidence item has no source")
        if evidence["source"] not in vals and evidence["source"] not in controls and evidence["source"] not in reqs:
            fail(f"unknown_presented_as_evidence: invalid evidence source {evidence['source']}")

    for lesson in lessons.values():
        if not lesson.get("root_cause"):
            fail(f"lesson_without_root_cause: {lesson['id']}")
        if not lesson.get("security_debt"):
            fail(f"lesson_without_security_debt: {lesson['id']}")
        if not any(rd.get("source_lesson_id") == lesson["id"] for rd in redesign.values()):
            fail(f"incident_closed_without_root_cause_feedback: {lesson['id']}")

    for item in redesign.values():
        if item.get("source_lesson_id") not in lessons:
            fail(f"redesign references unknown lesson: {item['id']}")


def operators():
    return [
        ("remove critical threat requirement", lambda x: x["security_requirements"][0]["threat_ids"].clear()),
        ("remove requirement validation", lambda x: x["security_requirements"][0]["validation_ids"].clear()),
        ("remove critical path detection", lambda x: x["attack_paths"][0].update(detection_ids=[], detection_gap="")),
        ("duplicate threat id", lambda x: x["threats"].append(copy.deepcopy(x["threats"][0]))),
        ("invalid evidence", lambda x: x.setdefault("evidence", []).append({"source": "UNKNOWN-SOURCE"})),
        ("disable destructive HITL", lambda x: x["operational_handoff"].update(human_approval_required_for_destructive_actions=False)),
        ("remove lesson root cause", lambda x: x["lessons_learned"][0].update(root_cause="")),
        ("remove redesign feedback", lambda x: x["redesign"].clear()),
    ]


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: fuzz.py VALID.json [CASE_COUNT]", file=sys.stderr)
        return 2
    valid_path = Path(sys.argv[1])
    try:
        requested = int(sys.argv[2]) if len(sys.argv) == 3 else 100
    except ValueError:
        print("CASE_COUNT must be an integer", file=sys.stderr)
        return 2
    if requested < 1:
        print("CASE_COUNT must be >= 1", file=sys.stderr)
        return 2

    try:
        base = load(valid_path)
        evaluate(base)
    except Exception as exc:
        print(f"FAIL  valid: {valid_path.name}: {exc}")
        return 1
    print(f"PASS  valid: {valid_path.name}")

    ops = operators()
    rng = random.Random(606)
    cases = []
    for i in range(requested):
        if i < len(ops):
            selected = [ops[i]]
        else:
            selected = rng.sample(ops, rng.randint(1, min(3, len(ops))))
        cases.append(selected)

    rejected = 0
    for index, selected in enumerate(cases, 1):
        obj = copy.deepcopy(base)
        names = []
        for name, mutation in selected:
            names.append(name)
            mutation(obj)
        try:
            evaluate(obj)
        except Exception:
            rejected += 1
        else:
            print(f"FAIL  fuzz case {index}: unexpectedly accepted ({' + '.join(names)})")
            return 1

    print(f"FUZZ RESULT: {rejected} rejected / {requested} generated")
    return 0 if rejected == requested else 1


if __name__ == "__main__":
    raise SystemExit(main())
