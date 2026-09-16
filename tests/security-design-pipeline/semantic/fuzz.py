#!/usr/bin/env python3
"""Level 6 deterministic property/graph fuzzing for the semantic evaluator.

The fuzzer generates bounded mutations from a known-good artifact and checks
security invariants. A fixed seed makes CI reproducible; every generated
security-breaking case MUST be rejected and every benign transformation MUST
remain accepted.
"""
from __future__ import annotations

import copy
import json
import random
import sys
import tempfile
from pathlib import Path

EVALUATOR = Path(__file__).with_name("evaluate.py")


def load_evaluator():
    namespace = {}
    exec(EVALUATOR.read_text(encoding="utf-8"), namespace)
    return namespace["evaluate"]


def accepted(evaluate, obj) -> bool:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "candidate.json"
        path.write_text(json.dumps(obj, sort_keys=True), encoding="utf-8")
        try:
            evaluate(path)
            return True
        except Exception:
            return False


def broken_mutations(base):
    """Return mutation functions that violate independent graph invariants."""
    return [
        lambda d: d["security_requirements"][0]["threat_ids"].clear(),
        lambda d: d["security_requirements"][0]["validation_ids"].clear(),
        lambda d: d["controls"][0]["requirement_ids"].clear(),
        lambda d: d["controls"][0]["validation_ids"].clear(),
        lambda d: d["validations"][0]["result"].__class__ and d["validations"][0].update({"result": "fail"}),
        lambda d: d["validations"][0]["control_ids"].clear(),
        lambda d: d["validations"][0]["requirement_ids"].clear(),
        lambda d: d["attack_paths"][0].update({"detection_ids": [], "detection_gap": ""}),
        lambda d: d["detections"][0]["attack_path_ids"].clear(),
        lambda d: d["security_gate"].update({"decision": "FAIL"}),
        lambda d: d["security_gate"].update({"unresolved_critical_design_flaws": ["FUZZ-FLAW"]}),
        lambda d: d["security_gate"].update({"unknowns": ["FUZZ-UNKNOWN"]}),
        lambda d: d["operational_handoff"].update({"human_approval_required_for_destructive_actions": False}),
        lambda d: d["lessons_learned"][0].pop("root_cause", None),
        lambda d: d["lessons_learned"][0].pop("security_debt", None),
        lambda d: d["redesign"][0].update({"source_lesson_id": "FUZZ-LESSON"}),
        lambda d: d["threats"].append(copy.deepcopy(d["threats"][0])),
        lambda d: d["security_requirements"][0]["validation_ids"].append("FUZZ-NONEXISTENT"),
        lambda d: d["controls"][0]["requirement_ids"].append("FUZZ-NONEXISTENT"),
        lambda d: d["evidence"].append({"id": "E-FUZZ", "source": "FUZZ-NONEXISTENT"}),
    ]


def benign_mutations(base):
    return [
        lambda d: d["threats"].reverse(),
        lambda d: d["security_requirements"].reverse(),
        lambda d: d["controls"].reverse(),
        lambda d: d["detections"].reverse(),
        lambda d: d.update({"fuzz_metadata": {"seed": 606, "benign": True}}),
    ]


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: fuzz.py VALID.json CASES", file=sys.stderr)
        return 2

    valid_path = Path(sys.argv[1])
    cases = int(sys.argv[2])
    base = json.loads(valid_path.read_text(encoding="utf-8"))
    evaluate = load_evaluator()
    seed = 606
    rng = random.Random(seed)

    if not accepted(evaluate, base):
        print("FAIL  Level 6 baseline is not accepted")
        return 1

    breakers = broken_mutations(base)
    benign = benign_mutations(base)
    passed = 0
    total = 0

    # Deterministically sample security-breaking mutations, including
    # repeated compositions so graph-edge failures are exercised in depth.
    for i in range(cases):
        obj = copy.deepcopy(base)
        count = 1 + (i % 3)
        for mutation in rng.sample(breakers, count):
            mutation(obj)
        total += 1
        if not accepted(evaluate, obj):
            passed += 1
        else:
            print(f"FAIL  fuzz-negative-{i:03d}: unexpectedly accepted")

    # Property checks: benign permutations/metadata must preserve acceptance.
    for i, mutation in enumerate(benign):
        obj = copy.deepcopy(base)
        mutation(obj)
        total += 1
        if accepted(evaluate, obj):
            passed += 1
        else:
            print(f"FAIL  fuzz-benign-{i:03d}: benign transformation rejected")

    print(f"LEVEL 6 RESULT: {passed} passed, {total - passed} failed; seed={seed}; negative_cases={cases}; benign_cases={len(benign)}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
