#!/usr/bin/env python3
"""Deterministic semantic validator for normalized Design-by-Security artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = [
    "intent", "assets", "trust_boundaries", "threats", "attack_paths",
    "security_requirements", "controls", "detections", "validations",
    "security_gate", "operational_handoff", "lessons_learned", "redesign",
]

ALLOWED_DECISIONS = {"PASS", "FAIL", "CONDITIONAL"}
ALLOWED_REVIEW_OUTCOMES = {
    "APPROVE", "APPROVE_WITH_CONDITIONS", "REDESIGN_REQUIRED", "DO_NOT_APPROVE",
}


def fail(msg: str) -> None:
    raise ValueError(msg)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        obj = json.load(fh)
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


def evidence_items(raw):
    """Accept the v1 list form and the v1.1 object-with-items form."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("items"), list):
        return raw["items"]
    fail("evidence must be an array or an object containing items")


def evaluate(source: Path | dict) -> None:
    """Validate a semantic artifact from a JSON path or an already-loaded object."""
    d = load(source) if isinstance(source, Path) else source
    if not isinstance(d, dict):
        fail("root must be an object")
    for key in REQUIRED:
        if key not in d:
            fail(f"missing artifact: {key}")

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
        fail("learning_redesign_imbalance: lessons_learned and redesign must be both empty or both populated")

    for t in threats.values():
        refs(t.get("asset_ids", []), assets, f"threat {t['id']} asset_ids")
        if str(t.get("severity", "")).lower() == "critical":
            linked = [r for r in reqs.values() if t["id"] in r.get("threat_ids", [])]
            if not linked:
                fail(f"critical_threat_without_requirement: {t['id']}")

    for p in paths.values():
        refs(p.get("threat_ids", []), threats, f"attack_path {p['id']} threat_ids")
        refs(p.get("detection_ids", []), detections, f"attack_path {p['id']} detection_ids")
        if str(p.get("severity", "")).lower() == "critical" and not p.get("detection_ids"):
            gap = str(p.get("detection_gap", "")).strip()
            if not gap:
                fail(f"critical_attack_path_without_detection_or_explicit_gap: {p['id']}")

    for r in reqs.values():
        refs(r.get("threat_ids", []), threats, f"requirement {r['id']} threat_ids")
        refs(r.get("validation_ids", []), vals, f"requirement {r['id']} validation_ids")
        if not r.get("validation_ids"):
            fail(f"requirement_without_validation: {r['id']}")

    for c in controls.values():
        refs(c.get("requirement_ids", []), reqs, f"control {c['id']} requirement_ids")
        refs(c.get("validation_ids", []), vals, f"control {c['id']} validation_ids")

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
    handoff = d["operational_handoff"]
    refs(handoff.get("attack_path_ids", []), paths, "operational_handoff attack_path_ids")
    refs(handoff.get("detection_ids", []), detections, "operational_handoff detection_ids")
    if not handoff.get("response_owner"):
        fail("operational_handoff missing response_owner")
    if handoff.get("human_approval_required_for_destructive_actions") is not True:
        fail("destructive_action_without_human_approval")

    gate = d["security_gate"]
    if not isinstance(gate, dict):
        fail("security_gate_must_be_object")

    decision = str(gate.get("decision", "")).upper()
    if decision not in ALLOWED_DECISIONS:
        fail(f"invalid_security_gate_decision: {decision!r}")

    review = str(gate.get("review_outcome", "")).upper()
    if review and review not in ALLOWED_REVIEW_OUTCOMES:
        fail(f"invalid_review_outcome: {review!r}")

    # Machine gate rules.
    if decision == "FAIL" and review in {"APPROVE", "APPROVE_WITH_CONDITIONS"}:
        fail(f"review_outcome_conflict: decision=FAIL cannot have review_outcome={review}")

    if decision == "FAIL" and not gate.get("unresolved_critical_design_flaws"):
        fail("unresolved_critical_design_flaw: decision=FAIL without listed flaws")

    if gate.get("unresolved_critical_design_flaws"):
        fail("unresolved_critical_design_flaw: gate contains unresolved flaws")

    if gate.get("unknowns"):
        fail("unknown_presented_as_evidence: gate contains unresolved unknowns")

    # Human review rules.
    if review == "APPROVE_WITH_CONDITIONS" and not gate.get("residual_risk"):
        fail("approve_with_conditions_without_residual_risk")

    if review and review != "APPROVE" and not (
        gate.get("blocking_conditions") or gate.get("residual_risk")
    ):
        fail(f"non_approve_without_conditions: review_outcome={review}")

    # Evidence boundary — always required.
    if not gate.get("evidence_boundary"):
        fail("security_gate_missing_evidence_boundary")

    for e in evidence_items(d.get("evidence")):
        if not isinstance(e, dict) or not e.get("source"):
            fail("unknown_presented_as_evidence: evidence item has no source")
        source = e["source"]
        if source not in vals and source not in controls and source not in reqs:
            fail(f"unknown_presented_as_evidence: invalid evidence source {source}")

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


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: evaluate.py VALID.json NEGATIVE_DIR", file=sys.stderr)
        return 2
    valid = Path(sys.argv[1])
    negative_dir = Path(sys.argv[2])
    try:
        evaluate(valid)
        print(f"PASS  valid: {valid.name}")
    except Exception as exc:
        print(f"FAIL  valid: {valid.name}: {exc}")
        return 1
    negatives = sorted(negative_dir.glob("*.json"))
    if not negatives:
        print("FAIL  no negative fixtures")
        return 1
    failed_as_expected = 0
    for path in negatives:
        try:
            evaluate(path)
        except Exception as exc:
            failed_as_expected += 1
            print(f"PASS  negative: {path.name}: rejected ({exc})")
        else:
            print(f"FAIL  negative: {path.name}: unexpectedly accepted")
    print(f"SEMANTIC RESULT: {1 + failed_as_expected} passed, {len(negatives) - failed_as_expected} failed")
    return 0 if failed_as_expected == len(negatives) else 1


if __name__ == "__main__":
    raise SystemExit(main())
