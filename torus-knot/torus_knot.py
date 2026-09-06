"""
Torus Knot Sculpture — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A (p,q) torus knot swept as a solid tube: the curve winds p times around the
torus axis and q times around the tube centre, producing trefoils, cinquefoils
and Solomon's-seal forms from two integers.

Modes:
  - sculpture : the whole knot as a single closed tube.

Watertight strategy:
  OCC's `sweep(isFrenet=True)` along a closed 3-D spline does NOT survive this
  curve — the pipe surface self-overlaps at the high-curvature lobes and the
  exported shell comes back open (and with an inflated volume, because the
  overlapping skin is counted twice). So the tube is built explicitly instead:
  a parallel-transport frame is carried along the curve, a ring of points is
  placed at each station, and the resulting quad strip is triangulated and sewn
  into a single closed B-rep solid.

  The frame is transported rather than Frenet-derived because a Frenet frame
  flips at every inflection point of the knot, which would tear the tube. The
  residual twist after one full loop is measured and redistributed across the
  stations so ring 0 and ring N-1 close onto each other seam-free.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` pre-injected; params arrive as bare globals.
  - Read each via PARAM(lambda: name, default). No globals()/eval/getattr.
  - Assign the final solid to `result`.
"""

import cadquery as cq
import math

from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_Sewing,
)
from OCP.gp import gp_Pnt
from OCP.TopoDS import TopoDS


def PARAM(getter, default):
    """Injected global if present else default; `except` catches the unbound-name
    NameError the sandbox raises (globals()/NameError are hidden)."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
target_part = str(PARAM(lambda: target_part, "sculpture"))
# "sculpture" ("knot" kept as a legacy alias)

p            = int(PARAM(lambda: p, 2))                     # longitudinal windings
q            = int(PARAM(lambda: q, 3))                     # meridional windings
tube_radius  = float(PARAM(lambda: tube_radius, 4.0))       # tube cross-section (mm)
torus_radius = float(PARAM(lambda: torus_radius, 30.0))     # major radius (mm)
segments     = int(PARAM(lambda: segments, 120))            # stations along the curve
scale_factor = float(PARAM(lambda: scale_factor, 1.0))      # global scale

# Clamp to sane ranges so extreme UI values still build watertight.
p            = max(1, min(p, 7))
q            = max(2, min(q, 11))
tube_radius  = max(1.0, min(tube_radius, 12.0))
torus_radius = max(15.0, min(torus_radius, 60.0))
segments     = max(40, min(segments, 300))
scale_factor = max(0.5, min(scale_factor, 2.0))

# Cross-section facets.
#
# 24, not 20, because that is what the OpenSCAD side uses. `torus_knot.scad`
# sweeps `circle_profile(tube_radius, $fn)` with `$fn = fn > 0 ? fn : 24`, so a
# default render there is a 24-gon tube; a 20-gon here is a different solid.
# Both kernels inscribe their polygon in the same circle, so the mismatch shows
# up as the difference between the two apothems, r*(cos(pi/24) - cos(pi/20)) =
# 0.0150 mm per side at the default tube_radius=4 — and, accumulated across the
# knot's lobes, 0.066788 mm of AABB at the defaults and the `trefoil` preset and
# 0.130051 mm at `thick_trefoil` (tube_radius=8, where the per-side error
# doubles). Aligning the counts takes those to 0.016 mm and 0.032 mm.
#
# `fn` is a platform render knob, not a manifest parameter, so it cannot be read
# here; 24 is the .scad's own default and the number every render uses.
SIDES = 24


# ── Curve ────────────────────────────────────────────────────────────────────
def torus_knot_path(p, q, torus_r, segments, scale):
    """Points along a (p,q) torus knot — the standard parametric curve.

        x(t) = (R + r*cos(q*t)) * cos(p*t)
        y(t) = (R + r*cos(q*t)) * sin(p*t)
        z(t) =       r*sin(q*t)

    with major radius R = torus_radius * scale_factor and minor radius
    r = 0.4 * R, matching `torus_knot.scad` term for term. The README names the
    OpenSCAD file as the side that "computes the standard parametric
    torus-knot curve", so that is the standard both kernels are held to.

    The previous form here used R = torus_r/3 * 2 and r = torus_r/3 (a 20/10
    knot against the standard's 30/12) and negated z, which put the two kernels
    22.98 mm apart on the AABB and mirrored the knot's chirality.
    """
    _R = torus_r * scale
    _r = _R * 0.4
    pts = []
    for i in range(segments):
        t = i * 2 * math.pi / segments
        radial = _R + _r * math.cos(q * t)
        x = radial * math.cos(p * t)
        y = radial * math.sin(p * t)
        z = _r * math.sin(q * t)
        pts.append((x, y, z))
    return pts


# ── Small vector helpers (no numpy dependency in the sandbox) ────────────────
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(a):
    m = math.sqrt(_dot(a, a))
    if m < 1e-12:
        return (0.0, 0.0, 1.0)
    return (a[0] / m, a[1] / m, a[2] / m)


def _rotate(v, axis, ang):
    """Rodrigues rotation of v about a unit axis."""
    c, s = math.cos(ang), math.sin(ang)
    return _add(
        _add(_mul(v, c), _mul(_cross(axis, v), s)),
        _mul(axis, _dot(axis, v) * (1.0 - c)),
    )


def _tube_mesh(path, radius, sides):
    """Closed tube around `path` as (vertices, triangles).

    Carries a parallel-transport normal along the curve, then redistributes the
    residual twist so the last ring meets the first without a tear.
    """
    n = len(path)

    # Central-difference tangents (the path is a closed loop).
    tangents = []
    for i in range(n):
        tangents.append(_norm(_sub(path[(i + 1) % n], path[(i - 1) % n])))

    # Seed a normal perpendicular to the first tangent.
    ref = (0.0, 0.0, 1.0)
    if abs(_dot(tangents[0], ref)) > 0.9:
        ref = (1.0, 0.0, 0.0)
    normals = [_norm(_cross(tangents[0], ref))]

    # Transport it: rotate by the angle between consecutive tangents.
    for i in range(1, n):
        t_prev, t_cur = tangents[i - 1], tangents[i]
        v = _cross(t_prev, t_cur)
        s = math.sqrt(_dot(v, v))
        prev = normals[-1]
        if s < 1e-12:
            cur = prev
        else:
            cur = _rotate(prev, _mul(v, 1.0 / s), math.atan2(s, _dot(t_prev, t_cur)))
        # Re-orthogonalise against drift.
        cur = _norm(_sub(cur, _mul(t_cur, _dot(cur, t_cur))))
        normals.append(cur)

    # Residual twist after one loop, snapped to a whole number of facets so the
    # seam can be closed by an index shift instead of a geometric fudge.
    b0 = _cross(tangents[0], normals[0])
    residual = math.atan2(_dot(normals[-1], b0), _dot(normals[-1], normals[0]))
    shift = int(round(residual * sides / (2.0 * math.pi)))
    correction = (2.0 * math.pi * shift / sides - residual) / (n - 1)

    verts = []
    for i in range(n):
        t_i = tangents[i]
        nrm = _rotate(normals[i], t_i, correction * i)
        bnm = _cross(t_i, nrm)
        for j in range(sides):
            a = 2.0 * math.pi * j / sides
            offset = _add(_mul(nrm, radius * math.cos(a)), _mul(bnm, radius * math.sin(a)))
            verts.append(_add(path[i], offset))

    tris = []
    wrap = shift % sides
    for i in range(n):
        nxt = (i + 1) % n
        # Only the closing band needs the twist shift applied.
        roll = wrap if nxt == 0 else 0
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = nxt * sides + (j + roll) % sides
            d = nxt * sides + (j + 1 + roll) % sides
            tris.append((a, b, d))
            tris.append((a, d, c))
    return verts, tris


def _sew_solid(verts, tris):
    """Sew a triangle soup into one closed B-rep solid.

    Sewing (rather than dropping faces into a bare shell) merges the coincident
    edges, so the result is a topologically valid solid and STEP export works.
    """
    pnts = [gp_Pnt(float(v[0]), float(v[1]), float(v[2])) for v in verts]
    sew = BRepBuilderAPI_Sewing(1e-6)
    for tri in tris:
        poly = BRepBuilderAPI_MakePolygon()
        for idx in tri:
            poly.Add(pnts[idx])
        poly.Close()
        sew.Add(BRepBuilderAPI_MakeFace(poly.Wire()).Face())
    sew.Perform()
    shell = TopoDS.Shell_s(sew.SewedShape())
    return cq.Solid(BRepBuilderAPI_MakeSolid(shell).Solid())


def build_sculpture():
    path = torus_knot_path(p, q, torus_radius, segments, scale_factor)
    verts, tris = _tube_mesh(path, tube_radius, SIDES)
    return cq.Workplane("XY").newObject([_sew_solid(verts, tris)])


# ── Dispatch ─────────────────────────────────────────────────────────────────
# This cartridge has exactly one part, so every accepted id maps to the same
# body and there is no fallback branch to fall through. "knot" is the pre-1.1
# part id, kept so older saved designs still resolve.
if target_part not in ("sculpture", "knot"):
    raise ValueError(
        "unknown target_part %r — this cartridge builds only 'sculpture'" % target_part
    )

result = build_sculpture()
