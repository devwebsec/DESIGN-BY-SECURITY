#!/usr/bin/env python3
"""Deterministic Level-6 bounded semantic/property fuzzer."""
from __future__ import annotations

import copy
import importlib.util
import json
import random
import sys
from pathlib import Path

_EVAL_PATH = Path(__file__).with_name("evaluate.py")
_SPEC = importlib.util.spec_from_file_location("semantic_evaluate", _EVAL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to load semantic evaluator")
_SEMANTIC = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SEMANTIC)
load = _SEMANTIC.load
evaluate = _SEMANTIC.evaluate


def operators():
    return [
        ("remove critical threat requirement", lambda x: x["security_requirements"][0]["threat_ids"].clear()),
        ("remove requirement validation", lambda x: x["security_requirements"][0]["validation_ids"].clear()),
        ("remove critical path detection", lambda x: x["attack_paths"][0].update(detection_ids=[], detection_gap="")),
        ("duplicate threat id", lambda x: x["threats"].append(copy.deepcopy(x["threats"][0]))),
        ("invalid evidence", lambda x: x["evidence"]["items"].append({"source": "UNKNOWN-SOURCE"})),
        ("disable destructive HITL", lambda x: x["operational_handoff"].update(human_approval_required_for_destructive_actions=False)),
        ("remove lesson root cause", lambda x: x["lessons_learned"][0].update(root_cause="")),
        ("remove redesign feedback", lambda x: x["redesign"].clear()),
        ("invalid gate decision", lambda x: x["security_gate"].update(decision="REVIEW")),
        ("fail with approving review", lambda x: x["security_gate"].update(decision="FAIL", review_outcome="APPROVE", unresolved_critical_design_flaws=["F-001"])),
        ("conditional approval without residual risk", lambda x: x["security_gate"].update(decision="PASS", review_outcome="APPROVE_WITH_CONDITIONS", residual_risk=None)),
        ("non-approve without conditions", lambda x: x["security_gate"].update(decision="PASS", review_outcome="DO_NOT_APPROVE", residual_risk=None, blocking_conditions=[])),
        ("missing evidence boundary", lambda x: x["security_gate"].pop("evidence_boundary", None)),
        ("fail without unresolved flaw", lambda x: x["security_gate"].update(decision="FAIL", review_outcome="REDESIGN_REQUIRED", unresolved_critical_design_flaws=[])),
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
