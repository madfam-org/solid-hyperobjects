"""
Winch Cradle — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The frame of a direct-drive winch: a base, a plate the motor bolts onto by its
face, and a second plate that carries the far end of the shaft, with room for a
drum between them. The Common Denominator Geometry is the motor's own face (the
pilot it centres on and the bolt circle that holds it) and the drum the cradle
has to clear.

Parts (dispatched via `target_part`):
  * "cradle"          — base, motor plate and outboard plate: a U. The shaft is
                        carried at both ends.
  * "cradle_overhung" — base and motor plate only: an L. The drum hangs on the
                        motor's own bearings.

Frame: the mounting face is Z = 0. The shaft axis is on X at height `axis_h`.
The motor sits outside the plate at -X and its shaft enters through the pilot
bore; the outboard plate is at +X. The cradle is centred on the origin in X
and Y.

Construction: ONE outline (the U or the L, seen from the side) extruded across
the width, then cut: the pilot, the bolt circle, the outboard bore and the
mounting holes. Nothing is unioned.

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


PILOT_D = float(PARAM(lambda: pilot_d, 60.0))
BOLT_CIRCLE = float(PARAM(lambda: bolt_circle, 75.0))
BOLT_D = float(PARAM(lambda: bolt_d, 5.5))
BOLT_COUNT = int(round(float(PARAM(lambda: bolt_count, 4))))
DRUM_D = float(PARAM(lambda: drum_d, 100.0))
DRUM_W = float(PARAM(lambda: drum_w, 70.0))
END_GAP = float(PARAM(lambda: end_gap, 10.0))
AXIS_H = float(PARAM(lambda: axis_h, 75.0))
PLATE_T = float(PARAM(lambda: plate_t, 8.0))
PLATE_MARGIN = float(PARAM(lambda: plate_margin, 10.0))
BEARING_D = float(PARAM(lambda: bearing_d, 22.0))
MOUNT_BOLT_D = float(PARAM(lambda: mount_bolt_d, 6.5))
PART = str(PARAM(lambda: target_part, "cradle"))
OUTBOARD = PART != "cradle_overhung"

EPS = 1.0                                   # through-cut overshoot
SIDE = BOLT_CIRCLE + BOLT_D + 2.0 * PLATE_MARGIN      # the plates are square on the bolt circle
INNER = DRUM_W + 2.0 * END_GAP              # clear length between the plates
LENGTH = INNER + 2.0 * PLATE_T
TOP = AXIS_H + SIDE / 2.0


def hole_x(d, y, z, x0, x1):
    """A cylinder along X at (y, z) from x0 to x1."""
    return cq.Workplane("YZ").circle(d / 2.0).extrude(x1 - x0).translate((x0, y, z))


def build_cradle():
    h, t = LENGTH / 2.0, PLATE_T
    if OUTBOARD:
        pts = [(-h, 0.0), (h, 0.0), (h, TOP), (h - t, TOP), (h - t, t), (-h + t, t), (-h + t, TOP), (-h, TOP)]
    else:
        pts = [(-h, 0.0), (h, 0.0), (h, t), (-h + t, t), (-h + t, TOP), (-h, TOP)]
    cradle = (cq.Workplane("XZ").polyline(pts).close().extrude(SIDE)       # XZ extrudes toward -Y
              .translate((0, SIDE / 2.0, 0)))
    x0, x1 = -h - EPS, -h + t + EPS
    cradle = cradle.cut(hole_x(PILOT_D, 0.0, AXIS_H, x0, x1))
    n = max(3, BOLT_COUNT)
    for i in range(n):                       # half a step off the vertical: no bolt at the very bottom
        a = math.radians(360.0 * (i + 0.5) / n - 90.0)
        cradle = cradle.cut(hole_x(BOLT_D, BOLT_CIRCLE / 2.0 * math.cos(a),
                                   AXIS_H + BOLT_CIRCLE / 2.0 * math.sin(a), x0, x1))
    if OUTBOARD:
        cradle = cradle.cut(hole_x(BEARING_D, 0.0, AXIS_H, h - t - EPS, h + EPS))
    inset = MOUNT_BOLT_D + 4.0
    mx, my = INNER / 2.0 - inset, SIDE / 2.0 - inset
    xs = [-mx, mx] if mx > MOUNT_BOLT_D else [0.0]
    pts = [(x, sy * my) for x in xs for sy in (-1.0, 1.0)]
    mounts = (cq.Workplane("XY").pushPoints(pts).circle(MOUNT_BOLT_D / 2.0)
              .extrude(t + 2.0 * EPS).translate((0, 0, -EPS)))
    return cradle.cut(mounts)


result = build_cradle()
