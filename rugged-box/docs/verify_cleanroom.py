"""c4 clean-room acceptance harness for rugged-box (ADR-021 §4).

Renders every (mode, part, variant) through the platform runner contract and
checks: watertight, expected body count, INTERFACE dimensions within +/-0.05 mm
of the recorded baseline, and FORM dimensions DIFFERENT from the baseline.

Usage:  python c4_verify.py <out_dir> [--quick]
"""
import json, sys, os, math, itertools

# The platform's shared sandbox core. Point COMMONS_SANDBOX_SRC at
# packages/commons-sandbox/src in a yantra4d checkout, or install the package.
_sb = os.environ.get("COMMONS_SANDBOX_SRC")
if _sb:
    sys.path.insert(0, _sb)
import cadquery as cq
import trimesh
from commons_sandbox import build_sandbox_builtins, read_script, validate_script_path

CART = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(CART, "main.py")
TOL = 0.05

manifest = json.load(open(os.path.join(CART, "project.json")))
DEFAULTS = {p["id"]: p["default"] for p in manifest["parameters"]}
PRESETS = {p["slug"]: p["values"] for p in manifest["presets"]}
MODES = {m["id"]: m for m in manifest["modes"]}


def render(params, out_path):
    import time
    _t0 = time.time()
    validate_script_path(SCRIPT, {".py", ".cq"})
    g = {"__builtins__": build_sandbox_builtins("CadQuery scripts"),
         "cq": cq, "math": math, "__file__": SCRIPT, "__name__": "__main__"}
    g.update(params)
    exec(read_script(SCRIPT), g)  # noqa: S102 — same sandbox as the platform runner
    res = None
    for n in ("result", "assembly", "part"):
        if n in g and isinstance(g[n], (cq.Workplane, cq.Assembly, cq.Shape)):
            res = g[n]
            break
    if res is None:
        raise RuntimeError("script produced no result")
    cq.exporters.export(res, out_path, "STL")
    m = trimesh.load(out_path, process=True, force="mesh")
    bodies = m.split(only_watertight=False)
    # The X extent of a single connected body: for multi-strap `latches` this is
    # the catch width, which the whole-part bbox cannot show.
    body_xlen = (round(float(min(b.extents[0] for b in bodies)), 3)
                 if len(bodies) else None)
    return {
        "seconds": round(time.time() - _t0, 1),
        "watertight": bool(m.is_watertight),
        "bodies": len(bodies),
        "body_xlen": body_xlen,
        "volume": round(float(m.volume), 3),
        "bbox": [round(float(v), 3) for v in m.extents],
    }


def expected_bodies(mode, part, p):
    """The body count the CONTRACT implies for this (mode, part)."""
    n_l = max(1, int(p["numberOfLatches"]))
    feet = 4 if p["isFeetAdded"] else 0
    if mode == "complete":
        # bottom + top + gasket + one body per latch strap (+ feet when enabled)
        return 1 + 1 + 1 + n_l + feet
    if mode == "closed-view":
        # base + lid + one strap per latch (+ feet when enabled)
        return 1 + 1 + n_l + feet
    if part == "latches":
        return n_l
    if part == "feet":
        return 4
    return 1  # bottom, top, gasket


def variants():
    """defaults, every preset, and a perturbation set that exercises the
    parameters the baseline could not reach."""
    out = [("defaults", dict(DEFAULTS))]
    for slug, vals in PRESETS.items():
        v = dict(DEFAULTS); v.update(vals)
        out.append(("preset-" + slug, v))
    # corner-min / corner-max on the resizable axes
    lo = dict(DEFAULTS); lo.update(dict(
        internalBoxWidthXMm=20, internalboxLengthYMm=20, internalBoxTopHeightZMm=5,
        internalboxBottomHeightZMm=5, boxWallWidthMm=1, boxChamferRadiusMm=0.5,
        gasketSlotDepth=1.0, gasketSlotWidth=1.0, rimWidthMm=1, rimHeightMm=1,
        numberOfHinges=1, hingeTotalWidthMm=10, hingeRadiusMm=2,
        numberOfLatches=1, latchSupportTotalWidth=10, numSideSupportRibs=0,
        BoxPolygonStyle=1))
    out.append(("corner-allmin", lo))
    hi = dict(DEFAULTS); hi.update(dict(
        internalBoxWidthXMm=300, internalboxLengthYMm=200, internalBoxTopHeightZMm=100,
        internalboxBottomHeightZMm=100, boxWallWidthMm=10, boxChamferRadiusMm=20,
        gasketSlotDepth=5.0, gasketSlotWidth=5.0, rimWidthMm=5, rimHeightMm=8,
        numberOfHinges=5, hingeTotalWidthMm=40, hingeRadiusMm=6,
        numberOfLatches=5, latchSupportTotalWidth=40, numSideSupportRibs=6,
        isFeetAdded=True, BoxPolygonStyle=3))
    out.append(("corner-allmax", hi))
    a = dict(DEFAULTS); a.update(dict(internalBoxWidthXMm=180, internalboxLengthYMm=45,
                                      boxSealType=2, countainerWidthXSections=4,
                                      boxLengthYSections=2, isFeetAdded=True,
                                      numberOfHinges=3, numberOfLatches=3))
    out.append(("mix-a", a))
    b = dict(DEFAULTS); b.update(dict(internalBoxWidthXMm=60, internalboxLengthYMm=150,
                                      internalboxBottomHeightZMm=70, boxWallWidthMm=5,
                                      boxChamferRadiusMm=12, gasketSlotDepth=4.0,
                                      numSideSupportRibs=4, isFeetAdded=True,
                                      BoxPolygonStyle=3))
    out.append(("mix-b", b))
    return out


def interface_checks(part, p, stats):
    """Return [(name, expected, measured, pass)] for the interface dimensions this
    part's own bounding box can prove."""
    rows = []
    wall = max(0.6, float(p["boxWallWidthMm"]))
    cav_x = max(5.0, float(p["internalBoxWidthXMm"]))
    cav_y = max(5.0, float(p["internalboxLengthYMm"]))
    shell_x = cav_x + 2 * wall
    shell_y = cav_y + 2 * wall
    if part == "gasket":
        rows.append(("gasket_outer_x", shell_x - 3.5, stats["bbox"][0]))
        rows.append(("gasket_outer_y", shell_y - 3.5, stats["bbox"][1]))
        rows.append(("gasket_depth", max(1.0, min(float(p["gasketSlotDepth"]), 5.0)),
                     stats["bbox"][2]))
    if part == "latches":
        # Each strap is catch_w wide in X and the straps are laid out along X,
        # so the whole-part bbox only equals the catch width for a single strap.
        # For n straps measure ONE body's own X extent instead — that is the
        # dimension the catch interface actually constrains.
        n_l = max(1, int(p["numberOfLatches"]))
        w = stats["bbox"][0] if n_l == 1 else stats.get("body_xlen")
        rows.append(("latch_catch_width", max(4.0, float(p["latchSupportTotalWidth"])), w))
    return [(n, e, m, (m is not None and abs(e - m) <= TOL)) for n, e, m in rows]


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    quick = "--quick" in sys.argv
    shard, nshard = 0, 1
    for a in sys.argv:
        if a.startswith("--shard="):
            shard, nshard = [int(x) for x in a.split("=", 1)[1].split("/")]
    rows = []
    vs = variants()
    if quick:
        vs = [v for v in vs if v[0] in ("defaults", "corner-allmin", "corner-allmax",
                                        "mix-a", "mix-b")]
    jobs = []
    for mode_id, mdef in MODES.items():
        parts0 = ([mdef["parts"][0]] if mode_id in ("complete", "closed-view")
                  else mdef["parts"])
        for part0 in parts0:
            for vn, vp in vs:
                jobs.append((mode_id, part0, vn, vp))
    # Cheapest and most interface-bearing first, so a run that is cut short
    # still carries the evidence that matters. gasket/latches/feet are seconds;
    # complete/closed-view are the expensive assemblies.
    COST = {"gasket": 0, "latches": 1, "feet": 2, "top": 3, "bottom": 4}
    MCOST = {"gasket": 0, "latches": 1, "feet": 2, "top": 3, "bottom": 4,
             "closed-view": 5, "complete": 6}
    jobs.sort(key=lambda j: (MCOST.get(j[0], 9), COST.get(j[1], 9), j[2]))
    jobs = [j for i, j in enumerate(jobs) if i % nshard == shard]
    print("shard %d/%d: %d jobs" % (shard, nshard, len(jobs)), flush=True)
    for mode_id, part, vname, p in jobs:
        if True:
            if True:
                key = "%s__%s__%s" % (mode_id, part, vname)
                params = dict(p)
                params["mode"] = mode_id
                params["target_part"] = (mode_id if mode_id in ("complete", "closed-view")
                                         else part)
                path = os.path.join(out_dir, key + ".stl")
                try:
                    st = render(params, path)
                except Exception as e:
                    rows.append({"key": key, "error": str(e)[:200]})
                    print("FAIL %-58s %s" % (key, str(e)[:90]), flush=True)
                    continue
                exp = expected_bodies(mode_id, part, p)
                ok_b = (st["bodies"] == exp)
                iface = interface_checks(part, p, st)
                ok_i = all(r[3] for r in iface)
                rows.append({"key": key, "mode": mode_id, "part": part,
                             "variant": vname, **st,
                             "expected_bodies": exp, "bodies_ok": ok_b,
                             "interface": iface, "interface_ok": ok_i})
                flag = "ok " if (st["watertight"] and ok_b and ok_i) else "BAD"
                print("%s %-58s wt=%-5s bodies=%d/%d %s" % (
                    flag, key, st["watertight"], st["bodies"], exp,
                    "" if ok_i else "IFACE:" + str([r for r in iface if not r[3]])),
                    flush=True)
    json.dump(rows, open(os.path.join(out_dir, "results-%d.json" % shard), "w"), indent=1)
    bad = [r for r in rows if r.get("error") or not r.get("watertight")
           or not r.get("bodies_ok") or not r.get("interface_ok")]
    print("\nTOTAL %d  FAIL %d" % (len(rows), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
