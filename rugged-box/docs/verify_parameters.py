"""Verification harness for rugged-box (ADR-021 §4).

Proves resizing — three widths give three different shell widths — and that every
declared parameter changes the mesh — a manifest that advertises a parameter
that never reaches the geometry is dishonest. See docs/CLEANROOM-VERIFICATION.md."""
import sys, os, math, json, hashlib, tempfile
# The platform's shared sandbox core. Point COMMONS_SANDBOX_SRC at
# packages/commons-sandbox/src in a yantra4d checkout, or install the package.
_sb = os.environ.get("COMMONS_SANDBOX_SRC")
if _sb:
    sys.path.insert(0, _sb)
import cadquery as cq, trimesh
from commons_sandbox import build_sandbox_builtins, read_script
CART=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=os.path.join(CART,"main.py")
MAN=json.load(open(os.path.join(CART,"project.json")))
DEF={p["id"]:p["default"] for p in MAN["parameters"]}
PARAMS={p["id"]:p for p in MAN["parameters"]}

def build(pv, part, mode=""):
    g={"__builtins__":build_sandbox_builtins("x"),"cq":cq,"math":math,"__file__":S,"__name__":"__main__"}
    g.update(pv); g["target_part"]=part; g["mode"]=mode
    exec(read_script(S), g)
    return g["result"]

def stats(shape, tmp=None):
    # Write the scratch mesh beside the harness output, never into the cartridge.
    tmp = tmp or os.path.join(tempfile.gettempdir(), "y4d_rugged_box_probe.stl")
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
    print("Each parameter is tested against the part it is supposed to drive, not the")
    print("cheapest part that merely lists it: a gasket ring legitimately does not")
    print("change when the lid gets deeper, and scoring that as INERT would be wrong.")
    print()
    def sig(pv, part, mode=""):
        return stats(build(pv, part, mode))["sha"]
    # The part each parameter must visibly change. Chosen from what the parameter
    # physically drives, cheapest such part first.
    PART = {
      "internalBoxWidthXMm":"gasket", "internalboxLengthYMm":"gasket",
      "internalBoxTopHeightZMm":"top", "internalboxBottomHeightZMm":"bottom",
      "boxWallWidthMm":"gasket", "boxChamferRadiusMm":"gasket",
      "boxSealType":"bottom",
      "gasketSlotWidth":"bottom", "gasketSlotDepth":"gasket",
      "rimWidthMm":"gasket", "rimHeightMm":"top",
      "numSideSupportRibs":"bottom", "supportRibThickness":"bottom",
      "supportRibWidth":"bottom",
      "countainerWidthXSections":"bottom", "boxLengthYSections":"bottom",
      "numCountainerWidthXSectionsToSkip":"bottom",
      "numBoxLengthYSectionsToSkip":"bottom",
      "numberOfHinges":"bottom", "hingeTotalWidthMm":"bottom",
      "hingeRadiusMm":"bottom", "hingeCenterOffsetMm":"bottom",
      "numberOfLatches":"latches", "latchSupportTotalWidth":"latches",
      "latchCenterOffsetMm":"bottom", "latchClipCutoutAngle":"latches",
      "latchOpenerLengthMultiplier":"latches",
      "isFeetAdded":"bottom", "feetwidthMm":"feet", "feetLengthMm":"feet",
      "boxGapMm":"feet", "BoxPolygonStyle":"latches",
    }
    # Some parameters only bite when a companion is enabled (feet exist only when
    # isFeetAdded, dividers need more than one section to skip).
    EXTRA = {
      "feetwidthMm":{"isFeetAdded":True}, "feetLengthMm":{"isFeetAdded":True},
      "boxGapMm":{"isFeetAdded":True},
      "numCountainerWidthXSectionsToSkip":{"countainerWidthXSections":4},
      "numBoxLengthYSectionsToSkip":{"boxLengthYSections":4},
    }
    results=[]
    for pid, meta in PARAMS.items():
        part = PART[pid]
        d = meta["default"]
        if meta["type"]=="checkbox": alt = (not d)
        elif meta["type"]=="select": alt=[o["value"] for o in meta["options"] if o["value"]!=d][0]
        else:
            alt = meta["max"] if abs(meta["max"]-d)>abs(meta["min"]-d) else meta["min"]
        base=dict(DEF); base.update(EXTRA.get(pid,{}))
        p0=dict(base); p1=dict(base); p1[pid]=alt
        s0=sig(p0,part,part); s1=sig(p1,part,part)
        ok = s0!=s1
        results.append((pid,part,d,alt,ok))
        print("%-5s %-36s part=%-8s %s -> %s" % ("ok" if ok else "INERT", pid, part, d, alt), flush=True)
    bad=[r for r in results if not r[4]]
    print()
    print("%d/%d parameters change the mesh" % (len(results)-len(bad), len(results)))
    if bad: print("INERT: %s" % [b[0] for b in bad])
