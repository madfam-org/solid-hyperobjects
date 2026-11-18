"""
Tube End Plug — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A plug for the open end of a square or rectangular tube: a flange that covers
the end and an insert that enters the tube. It closes a cut tube against water,
dirt and a careless hand, and with a bolt seat it turns the end of the tube
into a place to bolt something on: a crossbar, a foot, a caster, a bracket. The
Common Denominator Geometry is the tube's own section: its outside, its wall
and the fit the insert leaves inside it.

Part (dispatched via `target_part`):
  * "plug" — flange and insert in one piece. Without the bolt seat the insert
             is a hollow skirt; with it the insert is solid, drilled on the
             axis and pocketed on its inner end for a hex nut, so a bolt put in
             from outside draws the plug and whatever it holds onto the tube.

Frame: the tube axis is Z. The end of the tube is the plane Z = 0; the flange
stands above it and the insert goes down into the tube.

Construction: ONE block the size of the flange, from which the material round
the insert is cut away, then the hollow or the bolt seat. Nothing is unioned.
The corners of the insert are chamfered to clear the rounded inside corners of
real tube. Every hollow is open to the inside of the tube.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals; read them through PARAM()
    so the script also runs standalone with any subset of them.
  - Assign the final solid to a top-level name `result`.
"""

import math

import cadquery as cq


def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


def as_bool(v):
    return str(v).strip().lower() in ("1", "true", "yes", "on")


TUBE_W = float(PARAM(lambda: tube_w, 50.0))
TUBE_D = float(PARAM(lambda: tube_d, 50.0))
TUBE_WALL = float(PARAM(lambda: tube_wall, 3.0))
FIT = float(PARAM(lambda: fit, 0.3))
CORNER_C = float(PARAM(lambda: corner_c, 3.0))
FLANGE_T = float(PARAM(lambda: flange_t, 4.0))
INSERT_L = float(PARAM(lambda: insert_l, 20.0))
SKIRT_WALL = float(PARAM(lambda: skirt_wall, 3.0))
BOLT_SEAT = as_bool(PARAM(lambda: bolt_seat, False))
BOLT_D = float(PARAM(lambda: bolt_d, 8.5))
NUT_AF = float(PARAM(lambda: nut_af, 13.0))
NUT_H = float(PARAM(lambda: nut_h, 6.5))
PART = str(PARAM(lambda: target_part, "plug"))

EPS = 1.0                                   # through-cut overshoot


def chamfered(a, b, c):
    """A rectangle of half-sizes (a, b) with corners cut by c, as a closed list of points."""
    if c < 0.05:
        return [(-a, -b), (a, -b), (a, b), (-a, b)]
    return [(-a + c, -b), (a - c, -b), (a, -b + c), (a, b - c), (a - c, b), (-a + c, b), (-a, b - c), (-a, -b + c)]


def prism(points, z0, z1):
    return cq.Workplane("XY").polyline(points).close().extrude(z1 - z0).translate((0, 0, z0))


def build_plug():
    a = max(2.0, TUBE_W / 2.0 - TUBE_WALL - FIT)       # half-sizes of the insert
    b = max(2.0, TUBE_D / 2.0 - TUBE_WALL - FIT)
    c = min(max(CORNER_C, 0.0), min(a, b) - 1.0)
    plug = prism(chamfered(TUBE_W / 2.0, TUBE_D / 2.0, 0.0), -INSERT_L, FLANGE_T)
    ring = prism(chamfered(TUBE_W / 2.0 + EPS, TUBE_D / 2.0 + EPS, 0.0), -INSERT_L - EPS, 0.0)
    ring = ring.cut(prism(chamfered(a, b, c), -INSERT_L - 2.0 * EPS, EPS))
    plug = plug.cut(ring)                    # what is left under the flange is the insert
    if BOLT_SEAT:
        plug = plug.cut(cq.Workplane("XY").circle(BOLT_D / 2.0)
                        .extrude(INSERT_L + FLANGE_T + 2.0 * EPS).translate((0, 0, -INSERT_L - EPS)))
        depth = min(NUT_H, INSERT_L - 2.0)
        if depth > 0.5:
            across = NUT_AF / math.cos(math.radians(30.0))      # across corners
            plug = plug.cut(cq.Workplane("XY").polygon(6, across).extrude(depth + EPS)
                            .translate((0, 0, -INSERT_L - EPS)))
    else:
        ia, ib = a - SKIRT_WALL, b - SKIRT_WALL
        if ia > 1.0 and ib > 1.0:            # too small to hollow: the insert stays solid
            ic = max(0.0, c - SKIRT_WALL * 0.4)
            plug = plug.cut(prism(chamfered(ia, ib, min(ic, min(ia, ib) - 0.5)), -INSERT_L - EPS, 0.0))
    return plug


result = build_plug()
