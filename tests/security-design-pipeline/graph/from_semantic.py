#!/usr/bin/env python3
"""Convert the canonical normalized semantic artifact into the Level-7 graph."""
from __future__ import annotations
import json,sys
from pathlib import Path

def node(items, typ):
    return [{"id":x["id"],"type":typ,**({"criticality":x.get("criticality")} if "criticality" in x else {}),**({"status":"PASS"} if typ=="validation" and str(x.get("result","")).lower()=="pass" else {})} for x in items]

def main():
    if len(sys.argv)!=3:
        print("usage: from_semantic.py INPUT.json OUTPUT.json",file=sys.stderr); return 2
    d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    nodes=[]; edges=[]
    nodes += node(d["assets"],"asset")
    nodes += node(d["threats"],"threat")
    nodes += node(d["attack_paths"],"attack_path")
    nodes += node(d["security_requirements"],"requirement")
    nodes += node(d["controls"],"control")
    nodes += node(d["validations"],"validation")
    nodes += node(d["detections"],"detection")
    nodes += node(d["lessons_learned"],"root_cause")
    nodes += node(d["redesign"],"redesign")
    response_id="RESPONSE-001"
    nodes.append({"id":response_id,"type":"response","destructive":True,"human_approval_required":d["operational_handoff"].get("human_approval_required_for_destructive_actions") is True})
    def add(s,t): edges.append({"source":s,"target":t})
    for x in d["threats"]:
        for a in x.get("asset_ids",[]): add(a,x["id"])
    for x in d["attack_paths"]:
        for t in x.get("threat_ids",[]): add(t,x["id"])
        for det in x.get("detection_ids",[]): add(x["id"],det)
    for x in d["security_requirements"]:
        for t in x.get("threat_ids",[]):
            for ap in d["attack_paths"]:
                if t in ap.get("threat_ids",[]): add(ap["id"],x["id"])
    for x in d["controls"]:
        for r in x.get("requirement_ids",[]): add(r,x["id"])
    for x in d["validations"]:
        for c in x.get("control_ids",[]): add(c,x["id"])
    for x in d["detections"]:
        for ap in x.get("attack_path_ids",[]):
            if d["operational_handoff"].get("response_owner"): add(x["id"],response_id)
    for x in d["redesign"]:
        lesson=x.get("source_lesson_id")
        if lesson: add(lesson,x["id"])
    graph={"security_gate":str(d["security_gate"].get("decision","" )).upper(),"nodes":nodes,"edges":edges}
    Path(sys.argv[2]).write_text(json.dumps(graph,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Generated canonical graph: {sys.argv[2]}")
    return 0
if __name__=="__main__": raise SystemExit(main())
