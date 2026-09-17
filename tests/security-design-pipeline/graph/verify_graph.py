#!/usr/bin/env python3
"""Level-7 deterministic Security Graph Invariant Engine."""
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict
from pathlib import Path

GATES={"PASS","FAIL","CONDITIONAL"}

def load(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(d,dict) or not isinstance(d.get("nodes"),list) or not isinstance(d.get("edges"),list):
        raise ValueError("artifact must contain nodes[] and edges[]")
    return d

def verify(d):
    errors=[]; warnings=[]; nodes=d["nodes"]; edges=d["edges"]
    by={}
    for n in nodes:
        if not isinstance(n,dict) or not n.get("id"): errors.append("node_without_id"); continue
        if n["id"] in by: errors.append(f"duplicate_node_id:{n['id']}")
        by[n["id"]]=n
    out=defaultdict(list); inc=defaultdict(list)
    for e in edges:
        if not isinstance(e,dict): errors.append("invalid_edge"); continue
        s,t=e.get("source"),e.get("target")
        if s not in by or t not in by: errors.append(f"dangling_reference:{s}->{t}"); continue
        out[s].append(t); inc[t].append(s)
    typ=lambda i: by[i].get("type")
    critical=lambda n: str(n.get("criticality","")).upper()=="CRITICAL"
    for n in nodes:
        if n.get("type")=="asset" and critical(n) and not out[n["id"]]: errors.append(f"isolated_critical_asset:{n['id']}")
    for n in nodes:
        if n.get("type")!="threat" or not critical(n): continue
        tid=n["id"]; aps=[x for x in out[tid] if typ(x)=="attack_path"]
        if not aps: errors.append(f"critical_threat_without_attack_path:{tid}"); continue
        if not any(typ(x)=="detection" for x in out[tid]): warnings.append(f"critical_threat_without_direct_detection:{tid}")
        for ap in aps:
            reqs=[x for x in out[ap] if typ(x)=="requirement"]
            if not reqs: errors.append(f"attack_path_without_requirement:{ap}")
            for r in reqs:
                ctrls=[x for x in out[r] if typ(x)=="control"]
                if not ctrls: errors.append(f"requirement_without_control:{r}")
                for c in ctrls:
                    if not any(typ(x)=="validation" for x in out[c]): errors.append(f"control_without_validation:{c}")
    for n in nodes:
        if n.get("type")=="control" and not inc[n["id"]]: errors.append(f"orphan_control:{n['id']}")
        if n.get("type")=="validation" and str(n.get("status","")).upper()!="PASS" and d.get("security_gate")=="PASS": errors.append(f"pass_gate_with_failed_validation:{n['id']}")
        if n.get("type")=="response" and n.get("destructive") is True and n.get("human_approval_required") is not True: errors.append(f"destructive_action_without_human_approval:{n['id']}")
    if d.get("security_gate") not in GATES: errors.append(f"invalid_security_gate:{d.get('security_gate')}")
    lessons=[n for n in nodes if n.get("type") in {"root_cause","security_debt"}]
    redesign={n["id"] for n in nodes if n.get("type")=="redesign" and n.get("id")}
    if lessons and not redesign: errors.append("learn_without_redesign")
    if lessons and redesign and not any(t in redesign for s in out for t in out[s] if typ(s) in {"root_cause","security_debt"}): errors.append("learn_to_redesign_unreachable")
    ca=[n for n in nodes if n.get("type")=="asset" and critical(n)]
    ct=[n for n in nodes if n.get("type")=="threat" and critical(n)]
    metrics={"node_count":len(nodes),"edge_count":len(edges),"critical_asset_coverage":sum(bool(out[n["id"]]) for n in ca)/(len(ca) or 1),"critical_threat_attack_path_coverage":sum(any(typ(x)=="attack_path" for x in out[n["id"]]) for n in ct)/(len(ct) or 1)}
    return {"status":"PASS" if not errors else "FAIL","errors":errors,"warnings":warnings,"metrics":metrics}

def main():
    p=argparse.ArgumentParser(); p.add_argument("artifact"); p.add_argument("--report"); a=p.parse_args()
    try: r=verify(load(a.artifact))
    except Exception as e: r={"status":"FAIL","errors":[str(e)],"warnings":[],"metrics":{}}
    text=json.dumps(r,indent=2,ensure_ascii=False); print(text)
    if a.report: Path(a.report).write_text(text+"\n",encoding="utf-8")
    return 0 if r["status"]=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
