"""
Index Carriage — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A sleeve that slides on a rectangular column and locks at a height with an index
pin: the pin passes through a guide boss on the sleeve into one of a row of holes
in the column. Below the boss the sleeve carries a yoke: two ears with a cross
bore, to hang a block, a hook or an arm from a pivot pin. The Common Denominator
Geometry is the pair every such carriage shares: the column section it rides on,
and the pin that fixes it.

Part:
  * "carriage" — the sleeve with its pin boss and its yoke, one body.

Frame: the column runs along Z and the sleeve is centred on the origin. The pin
boss and the yoke are on the front face (+Y), the boss above the yoke.

Every feature added to the sleeve is let into its wall by half the wall thickness,
so each join is a real overlap, and none of them sits flush with the top or the
bottom of the sleeve.

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


COLUMN_W = float(PARAM(lambda: column_w, 50.0))
COLUMN_D = float(PARAM(lambda: column_d, 50.0))
SLIDE_CLR = float(PARAM(lambda: slide_clr, 0.5))
SLEEVE_WALL = float(PARAM(lambda: sleeve_wall, 6.0))
SLEEVE_H = float(PARAM(lambda: sleeve_h, 100.0))
PIN_D = float(PARAM(lambda: pin_d, 10.0))
BOSS_L = float(PARAM(lambda: boss_l, 18.0))
EAR_H = float(PARAM(lambda: ear_h, 50.0))
EAR_T = float(PARAM(lambda: ear_t, 8.0))
YOKE_GAP = float(PARAM(lambda: yoke_gap, 28.0))
EAR_REACH = float(PARAM(lambda: ear_reach, 34.0))
PIVOT_D = float(PARAM(lambda: pivot_d, 8.0))

EPS = 1.0                                   # through-cut overshoot
PIN_FIT = 0.4                               # diametral clearance of the pin in its bore
BOSS_WALL = 6.0                             # boss wall around the pin bore
EYE_WALL = 6.0                              # ear wall around the pivot bore
EDGE = 3.0                                  # boss and yoke stay this far from the sleeve ends
OPEN_W = COLUMN_W + 2.0 * SLIDE_CLR         # the opening the column passes through
OPEN_D = COLUMN_D + 2.0 * SLIDE_CLR
SLEEVE_W = OPEN_W + 2.0 * SLEEVE_WALL
SLEEVE_D = OPEN_D + 2.0 * SLEEVE_WALL
FRONT = SLEEVE_D / 2.0                      # the front face
SEAT = FRONT - SLEEVE_WALL / 2.0            # added features start here, inside the wall
BOSS_D = PIN_D + 2.0 * BOSS_WALL
BOSS_Z = SLEEVE_H / 2.0 - EDGE - BOSS_D / 2.0
EAR_Z = -SLEEVE_H / 2.0 + EDGE + EAR_H / 2.0


def cyl_y(d, y0, y1, x=0.0, z=0.0):
    """A cylinder along Y from y0 to y1, centred on (x, z)."""
    return (cq.Workplane("XY").cylinder(y1 - y0, d / 2.0)
            .rotate((0, 0, 0), (1, 0, 0), 90).translate((x, (y0 + y1) / 2.0, z)))


def sleeve():
    """The sleeve with its pin boss and the pin bore through boss and wall."""
    body = cq.Workplane("XY").box(SLEEVE_W, SLEEVE_D, SLEEVE_H)
    body = body.cut(cq.Workplane("XY").box(OPEN_W, OPEN_D, SLEEVE_H + 2.0 * EPS))
    body = body.union(cyl_y(BOSS_D, SEAT, FRONT + BOSS_L, z=BOSS_Z))
    return body.cut(cyl_y(PIN_D + PIN_FIT, FRONT - SLEEVE_WALL - EPS, FRONT + BOSS_L + EPS, z=BOSS_Z))


def ear(x_centre):
    """One yoke ear: full height at the sleeve, tapering on two tangents to a round eye."""
    eye_r = PIVOT_D / 2.0 + EYE_WALL
    half = max(EAR_H / 2.0, eye_r)
    cy = FRONT + EAR_REACH
    # Upper tangent from the corner at the sleeve face (-EAR_REACH, half), seen from
    # the eye centre, to the eye circle; the lower one mirrors it.
    dist = math.hypot(EAR_REACH, half)
    theta = math.atan2(half, -EAR_REACH) - math.acos(min(1.0, eye_r / dist))
    ty, tz = eye_r * math.cos(theta), eye_r * math.sin(theta)
    z = EAR_Z
    return (cq.Workplane("YZ", origin=(x_centre, 0, 0))
            .moveTo(SEAT, z - half).lineTo(SEAT, z + half).lineTo(FRONT, z + half)
            .lineTo(cy + ty, z + tz)
            .threePointArc((cy + eye_r, z), (cy + ty, z - tz))
            .lineTo(FRONT, z - half).close()
            .extrude(EAR_T / 2.0, both=True))


def build_carriage():
    body = sleeve()
    for side in (-1.0, 1.0):
        body = body.union(ear(side * (YOKE_GAP + EAR_T) / 2.0))
    pivot = (cq.Workplane("XY").cylinder(YOKE_GAP + 2.0 * EAR_T + 2.0 * EPS, PIVOT_D / 2.0)
             .rotate((0, 0, 0), (0, 1, 0), 90).translate((0, FRONT + EAR_REACH, EAR_Z)))
    return body.cut(pivot)


result = build_carriage()
