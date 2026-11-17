"""
Pulley Block — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

An enclosed housing for a cable or rope sheave. Two cheeks cover the sides of the
sheave and a rim guard follows its edge at a fixed gap, open only at the mouth
where the two legs of the cable enter and leave. The Common Denominator Geometry
is the pocket every block shares (the sheave it houses, the gap it keeps around
it and the axle it carries) plus the way the block meets the structure.

Parts (dispatched via `target_part`):
  * "block"       — the hanging block: a lug above the guard with a pivot bore
                    parallel to the axle, so the block swings in a yoke or a shackle.
  * "block_fixed" — the same guard under a mounting plate with a bolt hole at
                    each end, for a beam, a wall or a bench.

Frame: the axle is on X, the mouth opens toward -Z and the attachment is at +Z.
The body is a prism along X, so it prints lying on one cheek.

The guard covers the rim wherever the cable does not have to pass. The mouth is
derived, not chosen: it is just wide enough for two parallel legs leaving a
sheave of the declared diameter (a wrap of 180 degrees or more).

Construction: each part is ONE outline (guard circle plus attachment) extruded
across the block width, then cut. Nothing is unioned, so no two faces ever share
a surface, and every cut passes clean through the material it removes.

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


SHEAVE_D = float(PARAM(lambda: sheave_d, 90.0))
SHEAVE_W = float(PARAM(lambda: sheave_w, 16.0))
RIM_GAP = float(PARAM(lambda: rim_gap, 4.0))
SIDE_GAP = float(PARAM(lambda: side_gap, 1.5))
WALL = float(PARAM(lambda: wall, 4.0))
AXLE_D = float(PARAM(lambda: axle_d, 8.0))
PIVOT_D = float(PARAM(lambda: pivot_d, 8.0))
LUG_RISE = float(PARAM(lambda: lug_rise, 12.0))
MOUNT_BOLT_D = float(PARAM(lambda: mount_bolt_d, 5.5))
PLATE_T = float(PARAM(lambda: plate_t, 6.0))
PART = str(PARAM(lambda: target_part, "block"))

EPS = 1.0                                   # through-cut overshoot
SHEAVE_R = SHEAVE_D / 2.0
IN_R = SHEAVE_R + RIM_GAP                   # guard inner radius: the rim gap all round
OUT_R = IN_R + WALL
IN_W = SHEAVE_W + 2.0 * SIDE_GAP            # pocket width between the cheeks
OUT_W = IN_W + 2.0 * WALL
# Half-angle of the mouth, measured from -Z. The chord it opens at the guard's
# inner surface is the sheave diameter plus half the rim gap on each side.
MOUTH_HALF = math.asin(min(0.999, (SHEAVE_R + RIM_GAP / 2.0) / IN_R))


def on_circle(radius, angle):
    """A point at `angle` from -Z (positive toward +Y) on a circle about the axle, as (y, z)."""
    return (radius * math.sin(angle), -radius * math.cos(angle))


def outline(points_up):
    """Extrude the guard circle plus an attachment outline across the block width.

    `points_up` runs over the top from the +Y side to the -Y side; both ends lie on
    the guard circle, and the circle's lower arc closes the outline.
    """
    wire = cq.Workplane("YZ").moveTo(*points_up[0])
    for kind, *pts in points_up[1:]:
        wire = wire.lineTo(*pts[0]) if kind == "line" else wire.threePointArc(pts[0], pts[1])
    wire = wire.threePointArc((0.0, -OUT_R), points_up[0][0:2]).close()
    return wire.extrude(OUT_W / 2.0, both=True)


def cut_pocket(body):
    """Cut the sheave pocket and the mouth in one tool, between the cheeks only."""
    far = OUT_R + 2.0 * EPS
    tool = (cq.Workplane("YZ").moveTo(*on_circle(IN_R, MOUTH_HALF))
            .threePointArc((0.0, IN_R), on_circle(IN_R, -MOUTH_HALF))
            .lineTo(*on_circle(far, -MOUTH_HALF))
            .threePointArc((0.0, -far), on_circle(far, MOUTH_HALF))
            .close().extrude(IN_W / 2.0, both=True))
    return body.cut(tool)


def bore_x(body, d, z):
    """A through bore parallel to the axle at height z."""
    tool = (cq.Workplane("XY").cylinder(OUT_W + 2.0 * EPS, d / 2.0)
            .rotate((0, 0, 0), (0, 1, 0), 90).translate((0, 0, z)))
    return body.cut(tool)


def chord_z(half_width):
    """Height at which a vertical line at y = half_width meets the guard circle."""
    return math.sqrt(OUT_R ** 2 - half_width ** 2)


def build_block():
    """Hanging block: a rounded lug with a pivot bore parallel to the axle."""
    lug_r = min(PIVOT_D / 2.0 + max(WALL, 4.0), 0.8 * OUT_R)
    pivot_z = OUT_R + LUG_RISE
    body = outline([
        (lug_r, chord_z(lug_r)),
        ("line", (lug_r, pivot_z)),
        ("arc", (0.0, pivot_z + lug_r), (-lug_r, pivot_z)),
        ("line", (-lug_r, chord_z(lug_r))),
    ])
    body = bore_x(cut_pocket(body), AXLE_D, 0.0)
    return bore_x(body, PIVOT_D, pivot_z)


def build_block_fixed():
    """Fixed block: a mounting plate over the guard with one bolt hole at each end."""
    neck = 0.6 * OUT_R
    tab = 3.0 * MOUNT_BOLT_D
    half = OUT_R + tab
    top = OUT_R + PLATE_T
    body = outline([
        (neck, chord_z(neck)),
        ("line", (neck, OUT_R)),
        ("line", (half, OUT_R)),
        ("line", (half, top)),
        ("line", (-half, top)),
        ("line", (-half, OUT_R)),
        ("line", (-neck, OUT_R)),
        ("line", (-neck, chord_z(neck))),
    ])
    body = bore_x(cut_pocket(body), AXLE_D, 0.0)
    for side in (-1.0, 1.0):
        hole = (cq.Workplane("XY").cylinder(PLATE_T + 2.0 * EPS, MOUNT_BOLT_D / 2.0)
                .translate((0, side * (OUT_R + tab / 2.0), top - PLATE_T / 2.0)))
        body = body.cut(hole)
    return body


if PART == "block_fixed":
    result = build_block_fixed()
else:
    result = build_block()
