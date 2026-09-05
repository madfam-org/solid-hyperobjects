"""Clean-room acceptance harness for the `keyv2` cartridge.

Renders every recorded baseline variant through the platform's CadQuery runner
contract (the same `cq` / `math` globals and injected bare parameter names the
sandbox provides), then checks two different things two different ways:

  * TOPOLOGY on the exported mesh, with trimesh: watertight, one body, no
    inverted (negative-volume) body. `is_watertight` alone is not enough — the
    baseline's own defect was two watertight bodies, so the body count and the
    sign of each body's volume are checked explicitly.
  * INTERFACE DIMENSIONS on the exact B-Rep, not the mesh. A tessellated
    cylinder is an inscribed polygon and measures under its true diameter; at a
    chord tolerance fine enough to read 5.5 mm within 0.05 mm the STL runs to
    tens of megabytes and the section arithmetic dominates the runtime. The
    kernel already knows the exact dimension, so the interface checks read it
    from the solid's cross-sections and bounding box.

Run:
  <venv>/bin/python scripts/verify_baseline.py \
      --variants <pack>/VARIANTS.json \
      --measurements <pack>/MEASUREMENTS.json \
      --out <scratch dir>

Exit code 0 iff every variant passes. This script is a QA tool, not part of the
sandboxed cartridge: it uses the standard library freely.
"""

import argparse
import json
import math
import os
import sys
import tempfile

import cadquery as cq
import trimesh
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir


HERE = os.path.dirname(os.path.abspath(__file__))
CART = os.path.dirname(HERE)
MAIN = os.path.join(CART, "main.py")

# Interface expectations, from SPEC.md sections 2 and 4.
KEY_PITCH = 19.05
GAP = 0.5
UNITS = (1.0, 1.25, 1.5, 2.0)
PROFILE_BASE = (9.5, 8.0, 16.0, 11.9, 9.4)
MX_OD = 5.5
MX_CROSS_LEN = 4.1
MX_CROSS_WIDE = 1.17
ALPS_OUT = (4.5, 3.2)
ALPS_SOCK = (3.2, 1.2)
BOX_SIDE = 6.0
BOX_WALL = 1.5
TOL = 0.05


def render(params):
    """Execute main.py exactly as the runner does. Returns the solid, unexported.

    Export is deliberately NOT done here. `cq.exporters.export` attaches a
    triangulation to the shape, and OCCT's bounding-box routines then measure
    the DEFLECTED MESH rather than the exact surfaces — on this cap that reads
    19.86 mm where the footprint is 18.05 mm, and would fail every interface
    check for a reason that has nothing to do with the geometry. Measure the
    B-Rep first, export second.
    """
    src = open(MAIN, encoding="utf-8").read()
    g = {"__builtins__": __builtins__, "cq": cq, "math": math, "__name__": "__main__"}
    g.update(params)
    exec(src, g)  # noqa: S102 — the QA harness, mirroring cq_runner's exec
    result = g.get("result")
    if result is None:
        raise RuntimeError("script produced no `result`")
    return result, g


def measure_mesh(stl_path):
    m = trimesh.load(stl_path, process=True, force="mesh")
    bodies = m.split(only_watertight=False)
    neg = [b for b in bodies if b.is_watertight and b.volume < 0]
    return {
        "watertight": bool(m.is_watertight),
        "body_count": len(bodies),
        "negative_bodies": len(neg),
        "volume": float(m.volume),
        "bbox": [float(v) for v in m.extents],
    }


def brep_bbox(solid):
    """TIGHT bounding box of the exact solid.

    `Shape.BoundingBox()` returns OCCT's fast box, which inflates around NURBS
    and spline faces — on this cap it reads ~1.8 mm wide of the true footprint,
    which would silently fail every interface check. BRepBndLib.AddOptimal
    computes the tight box instead.
    """
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(solid.val().wrapped, box, True, False)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return [xmax - xmin, ymax - ymin, zmax - zmin]


def _section_wires(solid, pln):
    """Closed wires of the exact cross-section of `solid` by the plane `pln`."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds
    from OCP.TopoDS import TopoDS
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_WIRE
    from OCP.TopTools import TopTools_HSequenceOfShape

    face = BRepBuilderAPI_MakeFace(pln).Face()
    algo = BRepAlgoAPI_Section(solid.val().wrapped, face, False)
    algo.ComputePCurveOn1(True)
    algo.Approximation(True)
    algo.Build()
    edges = TopTools_HSequenceOfShape()
    exp = TopExp_Explorer(algo.Shape(), TopAbs_EDGE)
    while exp.More():
        edges.Append(exp.Current())
        exp.Next()
    wires = TopTools_HSequenceOfShape()
    ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(edges, 1e-6, False, wires)
    out = []
    for i in range(1, wires.Length() + 1):
        out.append(cq.Wire(TopoDS.Wire_s(wires.Value(i))))
    return out


def tight_wire_bbox(w):
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(w.wrapped, box, True, False)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return xmax - xmin, ymax - ymin


def slice_extents(solid, z):
    """XY extents of every closed loop in the exact cross-section at height z.

    Returns a list of (dx, dy), largest area first. Sectioning the B-Rep with a
    plane keeps circles as circles, so the stem's 5.5 mm outer diameter reads
    5.5 mm rather than the chord of an inscribed polygon.
    """
    # `Shape.intersect` against a plane is a full boolean and costs minutes on
    # this solid. `BRepAlgoAPI_Section` computes only the intersection curves,
    # which is what a cross-section is, and returns in milliseconds.
    sec = _section_wires(solid, gp_Pln(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1)))
    out = []
    for w in sec:
        out.append(tight_wire_bbox(w))
    out.sort(key=lambda t: t[0] * t[1], reverse=True)
    return out


def cross_arm_width(solid, z, arm_span):
    """Arm width of the cross socket, derived from the socket's enclosed area.

    Slicing a vertical plane through one arm sounds simpler, but the section of
    a solid by a plane that grazes a slot's own wall is numerically fragile and
    returned nothing here. The area is stable: a cross of span L and arm width
    W encloses 2*L*W - W^2, so W falls out of the quadratic

        W = L - sqrt(L^2 - A)

    taking the root below L (the other root is the degenerate one where the
    "cross" has swallowed its own bounding square). Returns 0.0 when the socket
    wire is not found, which fails the check rather than passing it silently.

    This is the check that says the socket is really a CROSS: the span check
    alone would pass on a plain square hole of the same width.
    """
    from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    wires = _section_wires(solid, gp_Pln(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1)))
    best = None
    for w in wires:
        dx, dy = tight_wire_bbox(w)
        # The socket wire: the smallest closed loop, inside the stem post.
        if max(dx, dy) <= arm_span + 0.2 and (best is None or max(dx, dy) < best[0]):
            best = (max(dx, dy), w)
    if best is None:
        return 0.0
    try:
        face = BRepBuilderAPI_MakeFace(best[1].wrapped).Face()
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        area = props.Mass()
    except Exception:
        return 0.0
    L = arm_span
    disc = L * L - area
    if disc < 0:
        return 0.0
    return L - math.sqrt(disc)


def socket_area(solid, z, arm_span):
    """Enclosed area of the socket loop at height z (0.0 when not found)."""
    from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    wires = _section_wires(solid, gp_Pln(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1)))
    best = None
    for w in wires:
        dx, dy = tight_wire_bbox(w)
        if max(dx, dy) <= arm_span + 0.2 and (best is None or max(dx, dy) < best[0]):
            best = (max(dx, dy), w)
    if best is None:
        return 0.0
    try:
        face = BRepBuilderAPI_MakeFace(best[1].wrapped).Face()
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        return props.Mass()
    except Exception:
        return 0.0


def interface_checks(solid, params):
    """(label, expected, measured, ok) for every interface dimension."""
    rows = []
    units = UNITS[int(params["key_size_id"])]
    prof = int(params["profile_id"])
    row = int(params["row_id"])
    stem = int(params["stem_type_id"])
    slop = float(params["stem_slop"])

    bb = brep_bbox(solid)

    # 1. Footprint — the key-pitch interface.
    exp_x = units * KEY_PITCH - 2 * GAP
    exp_y = KEY_PITCH - 2 * GAP
    rows.append(("footprint X", exp_x, bb[0], abs(bb[0] - exp_x) <= TOL))
    rows.append(("footprint Y", exp_y, bb[1], abs(bb[1] - exp_y) <= TOL))

    # 2. Cap height — base(profile) + (row - 2) * 0.5.
    exp_h = PROFILE_BASE[prof] + (row - 2) * 0.5
    rows.append(("cap height", exp_h, bb[2], abs(bb[2] - exp_h) <= TOL))

    # 3/4. Stem outer and socket, on the section 1.2 mm above the base (the
    #      height the baseline pack measured the stem at).
    loops = slice_extents(solid, 1.2)
    # The section has, largest first: the skirt's outer silhouette, the skirt's
    # inner wall (the cavity), then the stem's outer wall, then the socket void.
    # Drop the two skirt loops by size — the cavity is wider than any stem, and
    # the widest stem (Box, 6.0 mm) is well under half the 1u footprint.
    inner = [t for t in loops if max(t) <= 8.0]
    if inner:
        ox, oy = inner[0]
        if stem == 0:
            rows.append(("MX stem OD X", MX_OD, ox, abs(ox - MX_OD) <= TOL))
            rows.append(("MX stem OD Y", MX_OD, oy, abs(oy - MX_OD) <= TOL))
        elif stem == 1:
            rows.append(("Alps outer X", ALPS_OUT[0], ox, abs(ox - ALPS_OUT[0]) <= TOL))
            rows.append(("Alps outer Y", ALPS_OUT[1], oy, abs(oy - ALPS_OUT[1]) <= TOL))
        else:
            rows.append(("Box outer X", BOX_SIDE, ox, abs(ox - BOX_SIDE) <= TOL))
            rows.append(("Box outer Y", BOX_SIDE, oy, abs(oy - BOX_SIDE) <= TOL))

        if len(inner) > 1:
            sx, sy = inner[1]
            if stem in (0, 2):
                exp_c = MX_CROSS_LEN + slop / 2.0
                exp_w = MX_CROSS_WIDE + slop / 2.0
                rows.append(("MX cross arm span X", exp_c, sx, abs(sx - exp_c) <= TOL))
                rows.append(("MX cross arm span Y", exp_c, sy, abs(sy - exp_c) <= TOL))
                # Arm WIDTH: slice a vertical plane through one arm, offset from
                # the crossing, and read the socket's width there. The span
                # check above would pass on a plain square socket, so the width
                # is the check that says the cross is really a cross.
                if stem == 0:
                    # Cherry: the socket IS the bare cross, so its area gives
                    # the arm width directly.
                    w = cross_arm_width(solid, 1.2, exp_c)
                    rows.append(("MX cross arm width", exp_w, w, abs(w - exp_w) <= TOL))
                else:
                    # Box: the socket is the square hollow UNIONED with the
                    # cross (SPEC section 2). The cross-area formula assumes a
                    # bare cross and over-reports on that union, and the loop's
                    # SPAN is the cross's span either way, so neither says
                    # anything new here. Check the enclosed area against the
                    # union's own closed form instead:
                    #     square + cross - their overlap
                    #   = h^2 + (2*L*W - W^2) - (2*h*W - W^2)
                    # with h the square hollow, L the arm span, W the arm width.
                    h = BOX_SIDE - 2 * BOX_WALL
                    exp_area = h * h + 2 * exp_c * exp_w - 2 * h * exp_w
                    got_area = socket_area(solid, 1.2, exp_c)
                    rows.append(
                        ("Box socket area (mm2)", exp_area, got_area,
                         abs(got_area - exp_area) <= 0.15)
                    )
            else:
                ex = ALPS_SOCK[0] - slop
                ey = ALPS_SOCK[1] - slop
                rows.append(("Alps socket X", ex, sx, abs(sx - ex) <= TOL))
                rows.append(("Alps socket Y", ey, sy, abs(sy - ey) <= TOL))
        else:
            rows.append(("stem socket present", 1.0, 0.0, False))
    else:
        rows.append(("stem present", 1.0, 0.0, False))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--measurements", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--only", default=None, help="substring filter on variant name")
    args = ap.parse_args()

    variants = json.load(open(args.variants))
    baseline = json.load(open(args.measurements))["meshes"]
    outdir = args.out or tempfile.mkdtemp(prefix="c5_keyv2_")
    os.makedirs(outdir, exist_ok=True)

    failures = 0
    results = {}

    import time

    for name, v in variants.items():
        if args.only and args.only not in name:
            continue
        t0 = time.time()
        params = dict(v["parameters"])
        params["target_part"] = v["part"]
        stl = os.path.join(outdir, name + ".stl")
        try:
            solid, _ = render(params)
            # Interface dimensions FIRST, on the untriangulated B-Rep; the STL
            # export mutates the shape's cached triangulation and every later
            # bounding-box read would come from the mesh instead.
            iface = interface_checks(solid, params)
            cq.exporters.export(solid, stl, "STL")
        except Exception as exc:
            print(f"FAIL {name}: render error: {exc}")
            failures += 1
            continue

        meas = measure_mesh(stl)
        results[name] = dict(meas, interface=[list(r) for r in iface])
        base = baseline.get(name, {})

        iface_ok = all(r[3] for r in iface)
        ok = meas["watertight"] and meas["body_count"] == 1 and meas["negative_bodies"] == 0 and iface_ok
        if not ok:
            failures += 1
        print(
            f"{'ok  ' if ok else 'FAIL'} [{time.time() - t0:5.1f}s] {name:38} wt={meas['watertight']} "
            f"bodies={meas['body_count']}(base {base.get('body_count')}) "
            f"neg={meas['negative_bodies']} vol={meas['volume']:.2f}"
            f"(base {base.get('volume_mm3')}) "
            f"bbox={meas['bbox'][0]:.3f}x{meas['bbox'][1]:.3f}x{meas['bbox'][2]:.3f}"
            f"(base {base.get('bbox_size')})"
        )
        for label, exp, got, good in iface:
            print(f"   {'ok' if good else 'XX'}  {label:22} expected {exp:8.3f}  measured {got:8.3f}")

    a = results.get("keycap__keycap__defaults", {}).get("volume")
    b = results.get("keycap__keycap__legend_enabled-max", {}).get("volume")
    if a is not None and b is not None:
        differs = abs(a - b) > 1e-6
        print(f"\nlegend differs from no-legend: {differs} ({a:.4f} vs {b:.4f})")
        if not differs:
            failures += 1

    json.dump(results, open(os.path.join(outdir, "measured.json"), "w"), indent=1)
    print(f"\nvariants={len(results)} failures={failures} out={outdir}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
