#!/usr/bin/env python3
"""Deterministic Level-6 bounded graph/property fuzzer."""
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


def fail(msg: str) -> None:
    raise ValueError(msg)


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        fail("root must be an object")
    for key in REQUIRED:
        if key not in obj:
            fail(f"missing artifact: {key}")
    return obj


def ids(items, label):
    out = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            fail(f"{label}: every item requires id")
        if item["id"] in out:
            fail(f"{label}: duplicate id {item['id']}")
        out[item["id"]] = item
    return out


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

    for t in threats.values():
        refs(t.get("asset_ids", []), assets, f"threat {t['id']} asset_ids")
        if str(t.get("severity", "")).lower() == "critical":
            if not any(t["id"] in r.get("threat_ids", []) for r in reqs.values()):
                fail(f"critical_threat_without_requirement: {t['id']}")

    for p in paths.values():
        refs(p.get("threat_ids", []), threats, f"attack_path {p['id']} threat_ids")
        refs(p.get("detection_ids", []), detections, f"attack_path {p['id']} detection_ids")
        if str(p.get("severity", "")).lower() == "critical" and not p.get("detection_ids"):
            if not str(p.get("detection_gap", "")).strip():
                fail(f"critical_attack_path_without_detection_or_explicit_gap: {p['id']}")

    for r in reqs.values():
        refs(r.get("threat_ids", []), threats, f"requirement {r['id']} threat_ids")
        refs(r.get("validation_ids", []), vals, f"requirement {r['id']} validation_ids")
        if not r.get("validation_ids"):
            fail(f"requirement_without_validation: {r['id']}")

    for c in controls.values():
        refs(c.get("requirement_ids", []), reqs, f"control {c['id']} requirement_ids")
        refs(c.get("validation_ids", []), vals, f"control {c['id']} validation_ids")
        if not c.get("requirement_ids"):
            fail(f"control_without_requirement: {c['id']}")
        if not c.get("validation_ids"):
            fail(f"control_without_validation: {c['id']}")

    for v in vals.values():
        refs(v.get("requirement_ids", []), reqs, f"validation {v['id']} requirement_ids")
        refs(v.get("control_ids", []), controls, f"validation {v['id']} control_ids")
        if str(v.get("result", "")).lower() != "pass":
            fail(f"validation_not_passed: {v['id']}")

    for r in reqs.values():
        if not any(r["id"] in c.get("requirement_ids", []) for c in controls.values()):
            fail(f"requirement_without_control: {r['id']}")
        for vid in r.get("validation_ids", []):
            if r["id"] not in vals[vid].get("requirement_ids", []):
                fail(f"requirement_validation_mismatch: {r['id']} -> {vid}")

    for c in controls.values():
        for vid in c.get("validation_ids", []):
            if c["id"] not in vals[vid].get("control_ids", []):
                fail(f"control_validation_mismatch: {c['id']} -> {vid}")

    for det in detections.values():
        refs(det.get("attack_path_ids", []), paths, f"detection {det['id']} attack_path_ids")
        if not det.get("attack_path_ids"):
            fail(f"detection_without_attack_path: {det['id']}")

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

    for e in d.get("evidence", []):
        if not isinstance(e, dict) or not e.get("source"):
            fail("unknown_presented_as_evidence: evidence item has no source")
        if e["source"] not in vals and e["source"] not in controls and e["source"] not in reqs:
            fail(f"unknown_presented_as_evidence: invalid evidence source {e['source']}")

    for lesson in lessons.values():
        if not lesson.get("root_cause"):
            fail(f"lesson_without_root_cause: {lesson['id']}")
        if not lesson.get("security_debt"):
            fail(f"lesson_without_security_debt: {lesson['id']}")
        if not any(rd.get("source_lesson_id") == lesson["id"] for rd in redesign.values()):
            fail(f"incident_closed_without_root_cause_feedback: {lesson['id']}")

    for rd in redesign.values():
        if rd.get("source_lesson_id") not in lessons:
            fail(f"redesign references unknown lesson: {rd['id']}")


def mutation_operators():
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
    requested = int(sys.argv[2]) if len(sys.argv) == 3 else 100
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

    rng = random.Random(606)
    operators = mutation_operators()
    cases = []
    depths = {1: 0, 2: 0, 3: 0}

    # Guarantee every primitive operator is exercised first, then fill the bound
    # with deterministic compositions of 1..3 distinct operators.
    for name, op in operators:
        cases.append(([name], [op]))
        depths[1] += 1

    while len(cases) < requested:
        depth = rng.randint(1, 3)
        selected = rng.sample(operators, min(depth, len(operators)))
        cases.append(([name for name, _ in selected], [op for _, op in selected]))
        depths[depth] += 1

    rejected = 0
    for idx, (names, ops) in enumerate(cases[:requested], 1):
        obj = copy.deepcopy(base)
        for op in ops:
            op(obj)
        try:
            evaluate(obj)
        except Exception:
            rejected += 1
        else:
            print(f"FAIL  fuzz case {idx}: unexpectedly accepted ({' + '.join(names)})")
            return 1

    print(
        f"FUZZ RESULT: {rejected} rejected / {requested} generated; "
        f"depths=1:{depths[1]},2:{depths[2]},3:{depths[3]}"
    )
    return 0 if rejected == requested else 1


if __name__ == "__main__":
    raise SystemExit(main())
