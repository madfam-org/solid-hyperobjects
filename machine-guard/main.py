"""
Machine Guard — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A fixed guard that bolts over a moving or hot part of a machine and keeps hands
out. The Common Denominator Geometry is what every fixed guard shares: the
envelope of the thing it covers, the gap it keeps from it, the openings it has
to leave, and the feet it is bolted down by.

Parts (dispatched via `target_part`):
  * "drum_hood" — an arch over a rotating drum, spool, pulley or roller. It
                  follows the rim at a fixed gap and comes straight down to two
                  bolted feet. One end can be closed by a wall (a drum overhung
                  on a shaft); left open, the hood is a tunnel between the two
                  supports that carry the drum. A slot lets a cable or a belt
                  leave the drum.
  * "box_cover" — a five-sided cover over a drive, a coupling, a resistor or a
                  terminal row, with vent slots in the top and a notch in one
                  end wall for a shaft or a cable.

Frame: the mounting face is Z = 0 and the guard stands on it. The drum axis is
on X at height `axis_h`, centred on the origin; the box cover is centred on the
origin too. The feet run along X on both sides (+Y and -Y).

Every opening the guard leaves is held under a finger gap by the manifest: the
gap to the drum, the cable slot and the vent slots.

Construction: each part is ONE outline (feet, walls and top in a single closed
wire) extruded along X, then cut: the cavity, the slot, the vents, the notch
and the bolt holes. Nothing is unioned, so no two faces share a surface. Every
cavity is open at the mounting face, so no body holds a sealed void.

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


DRUM_D = float(PARAM(lambda: drum_d, 100.0))
DRUM_W = float(PARAM(lambda: drum_w, 70.0))
AXIS_H = float(PARAM(lambda: axis_h, 75.0))
GAP = float(PARAM(lambda: gap, 4.0))
END_CLEAR = float(PARAM(lambda: end_clear, 3.0))
END_WALL = as_bool(PARAM(lambda: end_wall, True))
CABLE_SLOT = as_bool(PARAM(lambda: cable_slot, True))
SLOT_W = float(PARAM(lambda: slot_w, 8.0))
SLOT_LEN = float(PARAM(lambda: slot_len, 60.0))
SLOT_ANGLE = float(PARAM(lambda: slot_angle, 50.0))
INNER_W = float(PARAM(lambda: inner_w, 160.0))
INNER_D = float(PARAM(lambda: inner_d, 120.0))
INNER_H = float(PARAM(lambda: inner_h, 60.0))
VENT_COUNT = int(round(float(PARAM(lambda: vent_count, 8))))
VENT_W = float(PARAM(lambda: vent_w, 6.0))
NOTCH = as_bool(PARAM(lambda: notch, True))
NOTCH_W = float(PARAM(lambda: notch_w, 20.0))
NOTCH_H = float(PARAM(lambda: notch_h, 12.0))
WALL = float(PARAM(lambda: wall, 3.0))
FOOT_W = float(PARAM(lambda: foot_w, 16.0))
FOOT_T = float(PARAM(lambda: foot_t, 4.0))
BOLT_D = float(PARAM(lambda: bolt_d, 5.5))
PART = str(PARAM(lambda: target_part, "drum_hood"))

EPS = 1.0                                   # through-cut overshoot
VENT_MARGIN = 8.0                           # solid top left at each end of a vent slot
VENT_LAND = 2.0                             # least solid between two vent slots


def extrude_x(points, arc, x0, x1):
    """Extrude a closed (y, z) outline from x0 to x1.

    `points` are joined by straight lines; `arc`, when given, is (index, mid): the
    segment that starts at points[index] is an arc through `mid` instead.
    """
    wp = cq.Workplane("YZ").moveTo(*points[0])
    for i in range(1, len(points)):
        if arc and arc[0] == i - 1:
            wp = wp.threePointArc(arc[1], points[i])
        else:
            wp = wp.lineTo(*points[i])
    return wp.close().extrude(x1 - x0).translate((x0, 0, 0))


def box(x, y, z, cx=0.0, cy=0.0, cz=0.0):
    return cq.Workplane("XY").box(x, y, z).translate((cx, cy, cz))


def foot_holes(body, half_len, row_y):
    """Bolt holes through both feet: two near the ends, one more per 200 mm of length."""
    inset = max(BOLT_D, FOOT_W / 2.0)
    reach = half_len - inset
    count = max(2, int((2.0 * half_len) // 200.0) + 1)
    if reach < BOLT_D:                      # too short for two holes in a row: one in the middle
        xs = [0.0]
    else:
        xs = [-reach + 2.0 * reach * i / (count - 1) for i in range(count)]
    pts = [(x, sy * row_y) for x in xs for sy in (-1.0, 1.0)]
    holes = (cq.Workplane("XY").pushPoints(pts).circle(BOLT_D / 2.0)
             .extrude(FOOT_T + 2.0 * EPS).translate((0, 0, -EPS)))
    return body.cut(holes)


def build_drum_hood():
    """Arch over a drum on X: rim gap all round, straight walls down to two feet."""
    r_in = DRUM_D / 2.0 + GAP
    r_out = r_in + WALL
    axis = max(AXIS_H, FOOT_T + 2.0)        # the walls must rise above the feet
    half = DRUM_W / 2.0 + END_CLEAR         # the feet pattern is centred on the drum
    x0, x1 = -half, half + (WALL if END_WALL else 0.0)
    wide = r_out + FOOT_W
    outer = [(-wide, 0.0), (wide, 0.0), (wide, FOOT_T), (r_out, FOOT_T), (r_out, axis),
             (-r_out, axis), (-r_out, FOOT_T), (-wide, FOOT_T)]
    hood = extrude_x(outer, (4, (0.0, axis + r_out)), x0, x1)
    inner = [(-r_in, -EPS), (r_in, -EPS), (r_in, axis), (-r_in, axis)]
    hood = hood.cut(extrude_x(inner, (2, (0.0, axis + r_in)), x0 - EPS, half if END_WALL else x1 + EPS))
    if CABLE_SLOT:
        length = min(SLOT_LEN, DRUM_W)
        angle = min(max(SLOT_ANGLE, 0.0), 80.0)
        slot = box(length, SLOT_W, WALL + 6.0, cz=r_in + WALL / 2.0)
        slot = slot.rotate((0, 0, 0), (1, 0, 0), -angle).translate((0, 0, axis))
        hood = hood.cut(slot)
    return foot_holes(hood, half, r_out + FOOT_W / 2.0)


def build_box_cover():
    """Five-sided cover: vent slots across the top, a notch in the -X end wall."""
    half_w = INNER_W / 2.0 + WALL
    half_d = INNER_D / 2.0 + WALL
    top = INNER_H + WALL
    wide = half_d + FOOT_W
    outer = [(-wide, 0.0), (wide, 0.0), (wide, FOOT_T), (half_d, FOOT_T), (half_d, top),
             (-half_d, top), (-half_d, FOOT_T), (-wide, FOOT_T)]
    cover = extrude_x(outer, None, -half_w, half_w)
    cover = cover.cut(box(INNER_W, INNER_D, INNER_H + EPS, cz=(INNER_H - EPS) / 2.0))
    count = min(max(VENT_COUNT, 0), int(INNER_W // (VENT_W + VENT_LAND)))
    vent_len = INNER_D - 2.0 * VENT_MARGIN
    if count > 0 and vent_len > VENT_W:
        pitch = INNER_W / (count + 1.0)
        pts = [(-INNER_W / 2.0 + pitch * (i + 1), 0.0) for i in range(count)]
        vents = (cq.Workplane("XY").pushPoints(pts).rect(VENT_W, vent_len)
                 .extrude(WALL + 2.0 * EPS).translate((0, 0, INNER_H - EPS)))
        cover = cover.cut(vents)
    if NOTCH:
        width = min(NOTCH_W, INNER_D - 8.0)
        height = min(NOTCH_H, INNER_H - 4.0)
        cover = cover.cut(box(WALL + 2.0 * EPS, width, height + EPS,
                              cx=-(INNER_W / 2.0 + WALL / 2.0), cz=(height - EPS) / 2.0))
    return foot_holes(cover, half_w, half_d + FOOT_W / 2.0)


BUILDERS = {"drum_hood": build_drum_hood, "box_cover": build_box_cover}
result = BUILDERS.get(PART, build_drum_hood)()
