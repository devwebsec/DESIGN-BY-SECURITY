#!/usr/bin/env python3
"""Level 5+ adversarial and metamorphic tests for the semantic evaluator.

The test suite starts from the known-good normalized artifact and applies
small, targeted mutations. Each security-critical mutation MUST be rejected;
benign transformations MUST remain accepted.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = Path(__file__).with_name("evaluate.py")


def load_evaluator():
    namespace = {}
    exec(EVALUATOR.read_text(encoding="utf-8"), namespace)
    return namespace["evaluate"]


def run_case(evaluate, base, name, mutate, should_pass):
    obj = copy.deepcopy(base)
    mutate(obj)
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / f"{name}.json"
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        try:
            evaluate(path)
            accepted = True
            reason = "accepted"
        except Exception as exc:
            accepted = False
            reason = str(exc)
    ok = accepted == should_pass
    state = "PASS" if ok else "FAIL"
    expectation = "accepted" if should_pass else "rejected"
    print(f"{state}  {name}: {reason}; expected {expectation}")
    return ok


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: mutate.py VALID.json", file=sys.stderr)
        return 2

    valid_path = Path(sys.argv[1])
    base = json.loads(valid_path.read_text(encoding="utf-8"))
    evaluate = load_evaluator()
    passed = 0
    total = 0

    cases = [
        ("mutation.critical-threat-unlinked",
         lambda d: d["security_requirements"][0]["threat_ids"].clear(), False),
        ("mutation.requirement-validation-removed",
         lambda d: d["security_requirements"][0]["validation_ids"].clear(), False),
        ("mutation.critical-path-detection-removed",
         lambda d: d["attack_paths"][0].update({"detection_ids": [], "detection_gap": ""}), False),
        ("mutation.gate-unresolved-flaw",
         lambda d: d["security_gate"].update({"unresolved_critical_design_flaws": ["FLAW-1"]}), False),
        ("mutation.evidence-source-invalid",
         lambda d: d["evidence"]["items"].append({"id": "E-BAD", "source": "UNKNOWN-SOURCE"}), False),
        ("mutation.destructive-action-approval-disabled",
         lambda d: d["operational_handoff"].update({"human_approval_required_for_destructive_actions": False}), False),
        ("mutation.lesson-root-cause-removed",
         lambda d: d["lessons_learned"][0].pop("root_cause", None), False),
        ("mutation.redesign-feedback-removed",
         lambda d: d["redesign"].clear(), False),
        ("mutation.duplicate-threat-id",
         lambda d: d["threats"].append(copy.deepcopy(d["threats"][0])), False),
        ("mutation.requirement-control-link-broken",
         lambda d: d["controls"][0]["requirement_ids"].clear(), False),
    ]

    metamorphic = [
        ("metamorphic.reorder-threats",
         lambda d: d["threats"].reverse(), True),
        ("metamorphic.reorder-requirements",
         lambda d: d["security_requirements"].reverse(), True),
        ("metamorphic.add-benign-metadata",
         lambda d: d.update({"test_metadata": {"purpose": "benign-mutation"}}), True),
    ]

    for name, mutate, expected in cases + metamorphic:
        total += 1
        if run_case(evaluate, base, name, mutate, expected):
            passed += 1

    print(f"MUTATION RESULT: {passed} passed, {total - passed} failed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
