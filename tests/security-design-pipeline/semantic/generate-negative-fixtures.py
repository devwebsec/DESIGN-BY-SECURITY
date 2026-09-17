#!/usr/bin/env python3
"""Generate deterministic Level-4 negative fixtures from the canonical valid artifact."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path

if len(sys.argv) != 3:
    print("usage: generate-negative-fixtures.py VALID.json OUT_DIR", file=sys.stderr)
    raise SystemExit(2)

valid = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
base = json.loads(valid.read_text(encoding="utf-8"))

cases = {
    "critical-threat-without-requirement.json": lambda d: d["security_requirements"][0]["threat_ids"].clear(),
    "requirement-without-validation.json": lambda d: d["security_requirements"][0]["validation_ids"].clear(),
    "critical-path-without-detection-or-gap.json": lambda d: d["attack_paths"][0].update({"detection_ids": [], "detection_gap": ""}),
    "unresolved-critical-design-flaw.json": lambda d: d["security_gate"].update({"unresolved_critical_design_flaws": ["FLAW-1"]}),
    "unknown-presented-as-evidence.json": lambda d: d.setdefault("evidence", []).append({"id":"E-BAD","source":"UNKNOWN-SOURCE"}),
    "destructive-action-without-human-approval.json": lambda d: d["operational_handoff"].update({"human_approval_required_for_destructive_actions": False}),
    "incident-without-root-cause.json": lambda d: d["lessons_learned"][0].pop("root_cause", None),
    "broken-redesign-feedback.json": lambda d: d["redesign"][0].update({"source_lesson_id":"UNKNOWN-LESSON"}),
    "duplicate-threat-id.json": lambda d: d["threats"].append(copy.deepcopy(d["threats"][0])),
    "requirement-control-link-broken.json": lambda d: d["controls"][0]["requirement_ids"].clear(),
}

for name, mutate in cases.items():
    obj = copy.deepcopy(base); mutate(obj)
    (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"generated {len(cases)} negative fixtures in {out}")
