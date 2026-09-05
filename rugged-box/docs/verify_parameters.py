"""Prove resizing: three widths -> three different shell widths, and every
declared parameter changes the mesh (the regression SPEC.md section 5 asks for)."""
import sys, os, math, json, hashlib
sys.path.insert(0,"/Users/aldoruizluna/labspace/.stab-clones/y4d-s3/packages/commons-sandbox/src")
import cadquery as cq, trimesh
from commons_sandbox import build_sandbox_builtins, read_script
CART="/Users/aldoruizluna/labspace/.stab-clones/c4-rugged-box/commons/rugged-box"
S=os.path.join(CART,"main.py")
MAN=json.load(open(os.path.join(CART,"project.json")))
DEF={p["id"]:p["default"] for p in MAN["parameters"]}
PARAMS={p["id"]:p for p in MAN["parameters"]}

def build(pv, part, mode=""):
    g={"__builtins__":build_sandbox_builtins("x"),"cq":cq,"math":math,"__file__":S,"__name__":"__main__"}
    g.update(pv); g["target_part"]=part; g["mode"]=mode
    exec(read_script(S), g)
    return g["result"]

def stats(shape, tmp="_r.stl"):
    cq.exporters.export(shape, tmp, "STL")
    m=trimesh.load(tmp, process=True, force="mesh")
    h=hashlib.sha256(open(tmp,'rb').read()).hexdigest()[:12]
    return {"bbox":[round(float(v),3) for v in m.extents],
            "vol":round(float(m.volume),2),"bodies":len(m.split(only_watertight=False)),
            "wt":bool(m.is_watertight),"sha":h}

if sys.argv[1]=="resize":
    print("RESIZING PROOF - internalBoxWidthXMm 20 / 100 / 300, mode bottom")
    print("%-8s %-28s %-12s" % ("width","shell bbox (x,y,z)","volume"))
    for w in (20,100,300):
        p=dict(DEF); p["internalBoxWidthXMm"]=w
        st=stats(build(p,"bottom"))
        print("%-8s %-28s %-12s wt=%s bodies=%d" % (w, st["bbox"], st["vol"], st["wt"], st["bodies"]))
elif sys.argv[1]=="params":
    print("PARAMETER EFFECTIVENESS - each declared parameter perturbed from its default")
    base={}
    def sig(pv, part, mode=""):
        return stats(build(pv,part,mode))["sha"]
    # choose the cheapest (mode,part) that the parameter declares
    order=["gasket","latches","feet","top","bottom"]
    results=[]
    for pid, meta in PARAMS.items():
        modes=meta["modes"]
        part=None
        for cand in order:
            if cand in modes or (cand=="bottom" and "bottom" in modes) :
                part=cand; break
        if part is None: part="bottom"
        d=meta["default"]
        if meta["type"]=="checkbox": alt = (not d)
        elif meta["type"]=="select": alt=[o["value"] for o in meta["options"] if o["value"]!=d][0]
        else:
            alt = meta["max"] if abs(meta["max"]-d)>abs(meta["min"]-d) else meta["min"]
        p0=dict(DEF); p1=dict(DEF); p1[pid]=alt
        s0=sig(p0,part); s1=sig(p1,part)
        ok = s0!=s1
        results.append((pid,part,d,alt,ok))
        print("%-4s %-36s part=%-8s %s -> %s" % ("ok" if ok else "INERT", pid, part, d, alt), flush=True)
    bad=[r for r in results if not r[4]]
    print("\n%d/%d parameters change the mesh; INERT: %s" % (len(results)-len(bad), len(results), [b[0] for b in bad]))
