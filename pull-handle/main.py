"""
Pull Handle — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The part of a cable or a cord that a hand holds: a grip the cord passes through,
and a bar for two hands. It ends a pull cord on a starter, a resistance band, a
tow line, a blind, a kite line or a cable machine. The Common Denominator
Geometry is the grip itself: the diameter a hand closes round, and the flanges
at its ends that keep the hand on it.

Parts (dispatched via `target_part`):
  * "grip" — a tube with a flange at each end and a bore along its axis for the
             cord, strap or tie rod it is hung by. An optional pocket in its
             side takes a small module: a switch, a sensor, a tag.
  * "bar"  — a solid bar for two hands, flanged at the ends, with one or two
             cross holes for the eye bolts or the pin it is pulled by.

Frame: the axis of the grip is X, centred on the origin. The pocket of the grip
and the entry of the bar's cross holes face +Z.

Construction: each part is ONE profile revolved about its axis, so the flanges
and the grip are never fused from separate cylinders. The pocket and the cross
holes are cut. The pocket is open to the surface.

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


GRIP_D = float(PARAM(lambda: grip_d, 32.0))
FLANGE_H = float(PARAM(lambda: flange_h, 6.0))
FLANGE_T = float(PARAM(lambda: flange_t, 6.0))
GRIP_L = float(PARAM(lambda: grip_l, 130.0))
CORD_D = float(PARAM(lambda: cord_d, 10.0))
POCKET = as_bool(PARAM(lambda: pocket, False))
POCKET_L = float(PARAM(lambda: pocket_l, 30.0))
POCKET_W = float(PARAM(lambda: pocket_w, 14.0))
POCKET_DEPTH = float(PARAM(lambda: pocket_depth, 3.0))
BAR_L = float(PARAM(lambda: bar_l, 500.0))
EYE_D = float(PARAM(lambda: eye_d, 8.5))
EYE_SPACING = float(PARAM(lambda: eye_spacing, 100.0))
PART = str(PARAM(lambda: target_part, "grip"))

EPS = 1.0                                   # through-cut overshoot
RG = GRIP_D / 2.0
RF = RG + max(FLANGE_H, 0.0)


def revolve_x(profile):
    """Revolve a closed (x, radius) profile about the X axis."""
    return cq.Workplane("XY").polyline(profile).close().revolve(360.0, (0, 0, 0), (1, 0, 0))


def body_profile(half, r_bore):
    """Grip between two flanges, from the bore (or the axis) out, as (x, radius)."""
    end = half + FLANGE_T
    if RF - RG < 0.1:                        # no flange: a plain cylinder of the full length
        return [(-end, r_bore), (end, r_bore), (end, RG), (-end, RG)]
    return [(-end, r_bore), (end, r_bore), (end, RF), (half, RF), (half, RG),
            (-half, RG), (-half, RF), (-end, RF)]


def build_grip():
    rb = min(max(CORD_D / 2.0, 1.0), RG - 2.0)
    grip = revolve_x(body_profile(GRIP_L / 2.0, rb))
    if POCKET:
        depth = min(POCKET_DEPTH, RG - rb - 1.0)
        tool = (cq.Workplane("XY").box(POCKET_L, POCKET_W, depth + RG)
                .translate((0, 0, RG - depth + (depth + RG) / 2.0)))
        grip = grip.cut(tool)
    return grip


def build_bar():
    bar = revolve_x(body_profile(BAR_L / 2.0, 0.0))
    xs = [0.0] if EYE_SPACING < 1.0 else [-EYE_SPACING / 2.0, EYE_SPACING / 2.0]
    eyes = (cq.Workplane("XY").pushPoints([(x, 0.0) for x in xs]).circle(EYE_D / 2.0)
            .extrude(2.0 * RF + 2.0 * EPS).translate((0, 0, -RF - EPS)))
    return bar.cut(eyes)


BUILDERS = {"grip": build_grip, "bar": build_bar}
result = BUILDERS.get(PART, build_grip)()
