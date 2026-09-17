#!/usr/bin/env python3
"""Level 7 graph invariant mutation gate."""
from __future__ import annotations
import copy,json,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).parent; ENGINE=HERE/"verify_graph.py"; BASE=json.loads((HERE/"valid-graph.json").read_text())

def rejected(obj):
    with tempfile.NamedTemporaryFile("w",suffix=".json",delete=False) as f:
        json.dump(obj,f); name=f.name
    try:
        p=subprocess.run([sys.executable,str(ENGINE),name],capture_output=True,text=True)
        return p.returncode==1
    finally: Path(name).unlink(missing_ok=True)

cases=[]
def add(name,fn):
    x=copy.deepcopy(BASE); fn(x); cases.append((name,x))
add("isolated-critical-asset",lambda d:d["edges"].remove({"source":"A-001","target":"T-001"}))
add("critical-threat-no-attack-path",lambda d:d["edges"].remove({"source":"T-001","target":"AP-001"}))
add("attack-path-no-requirement",lambda d:d["edges"].remove({"source":"AP-001","target":"R-001"}))
add("requirement-no-control",lambda d:d["edges"].remove({"source":"R-001","target":"C-001"}))
add("control-no-validation",lambda d:d["edges"].remove({"source":"C-001","target":"V-001"}))
add("dangling-reference",lambda d:d["edges"].append({"source":"T-001","target":"NOPE"}))
add("duplicate-id",lambda d:d["nodes"].append(copy.deepcopy(d["nodes"][0])))
add("failed-validation-under-pass",lambda d:d["nodes"][5].update({"status":"FAIL"}))
add("destructive-without-hitl",lambda d:d["nodes"][-1].update({"human_approval_required":False}))
add("learn-without-redesign",lambda d:d["nodes"].pop(9))

bad=0
for name,obj in cases:
    ok=rejected(obj); print(("PASS" if ok else "FAIL"),name,"rejected" if ok else "accepted")
    bad += not ok
print(f"LEVEL 7 MUTATION RESULT: {len(cases)-bad} passed, {bad} failed")
raise SystemExit(1 if bad else 0)
