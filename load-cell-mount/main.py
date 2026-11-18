"""
Load Cell Mount — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The two printed or machined parts a bar load cell needs to become a measuring
point. A bar (bending beam) load cell is a short metal bar with two bolt holes
at each end: one end is fixed, the load is applied to the other, and the bar
must be free to bend between them. The Common Denominator Geometry is the bar's
own interface: its width, and for each end the pitch of its pair of holes and
their distance from the end. The two ends are declared separately, because on
many bars they differ.

Parts (dispatched via `target_part`):
  * "base"         — a base plate with a riser the fixed end bolts onto, so the
                     bar stands clear of the plate, and an overload stop under
                     the live end that the bar meets before it is damaged.
  * "load_bracket" — a yoke that bolts onto the live end and carries a cross
                     axle between two ears: the seat for a sheave, a roller, a
                     rod end or a hook.

Frame, base: the bar lies along X, centred on the origin, fixed end toward -X;
the plate sits on Z = 0. Frame, bracket: its seating face is Z = 0 (it sits on
the bar), the two bolts are on X about the origin and the axle is along Y.

Construction: the base is a plate with two pads let 1 mm into it, so each join
is a real overlap of flat faces, never a touching face. The bracket is ONE
channel outline extruded along X, then cut. Every hole passes clean through.

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


BEAM_L = float(PARAM(lambda: beam_l, 80.0))
BEAM_W = float(PARAM(lambda: beam_w, 12.7))
HOLE_PITCH = float(PARAM(lambda: hole_pitch, 15.0))
END_MARGIN = float(PARAM(lambda: end_margin, 5.0))
FIXED_BOLT_D = float(PARAM(lambda: fixed_bolt_d, 5.5))
RISER_H = float(PARAM(lambda: riser_h, 6.0))
STOP_GAP = float(PARAM(lambda: stop_gap, 1.0))
BASE_T = float(PARAM(lambda: base_t, 8.0))
BASE_MARGIN = float(PARAM(lambda: base_margin, 14.0))
MOUNT_BOLT_D = float(PARAM(lambda: mount_bolt_d, 5.5))
LIVE_PITCH = float(PARAM(lambda: live_pitch, 15.0))
LIVE_MARGIN = float(PARAM(lambda: live_margin, 5.0))
LIVE_BOLT_D = float(PARAM(lambda: live_bolt_d, 5.5))
PAD_T = float(PARAM(lambda: pad_t, 5.0))
YOKE_GAP = float(PARAM(lambda: yoke_gap, 18.0))
EAR_T = float(PARAM(lambda: ear_t, 5.0))
AXLE_D = float(PARAM(lambda: axle_d, 8.0))
AXLE_H = float(PARAM(lambda: axle_h, 22.0))
PART = str(PARAM(lambda: target_part, "base"))

EPS = 1.0                                   # through-cut overshoot and pad overlap
SEAT_L = 2.0 * END_MARGIN + HOLE_PITCH      # length of the bar the fixed pair of holes takes
PAD_L = 2.0 * LIVE_MARGIN + LIVE_PITCH      # length of the bar the live pair of holes takes


def box(x, y, z, cx=0.0, cy=0.0, cz=0.0):
    return cq.Workplane("XY").box(x, y, z).translate((cx, cy, cz))


def holes_z(points, d, z0, z1):
    """Vertical cylinders at (x, y) points from z0 to z1."""
    return (cq.Workplane("XY").pushPoints(points).circle(d / 2.0)
            .extrude(z1 - z0).translate((0, 0, z0)))


def build_base():
    """Plate, riser under the fixed end, overload stop under the live end."""
    length = BEAM_L + 2.0 * BASE_MARGIN
    width = BEAM_W + 2.0 * BASE_MARGIN
    pad_w = BEAM_W + 2.0
    top = BASE_T + RISER_H
    seat_x = -BEAM_L / 2.0 + SEAT_L / 2.0
    base = box(length, width, BASE_T, cz=BASE_T / 2.0)
    base = base.union(box(SEAT_L, pad_w, RISER_H + EPS, cx=seat_x, cz=BASE_T - EPS + (RISER_H + EPS) / 2.0))
    stop_h = RISER_H - STOP_GAP
    if stop_h >= 0.5:
        stop_l = max(END_MARGIN, 4.0)
        base = base.union(box(stop_l, pad_w, stop_h + EPS, cx=BEAM_L / 2.0 - stop_l / 2.0,
                              cz=BASE_T - EPS + (stop_h + EPS) / 2.0))
    fixed = [(seat_x - HOLE_PITCH / 2.0, 0.0), (seat_x + HOLE_PITCH / 2.0, 0.0)]
    base = base.cut(holes_z(fixed, FIXED_BOLT_D, -EPS, top + EPS))
    head_depth = min(FIXED_BOLT_D, BASE_T - 2.0)      # the heads sink into the underside
    if head_depth > 0.5:
        base = base.cut(holes_z(fixed, min(1.8 * FIXED_BOLT_D, HOLE_PITCH - 1.0, BEAM_W + 1.0), -EPS, head_depth))
    mx, my = length / 2.0 - BASE_MARGIN / 2.0, width / 2.0 - BASE_MARGIN / 2.0
    corners = [(sx * mx, sy * my) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    return base.cut(holes_z(corners, MOUNT_BOLT_D, -EPS, BASE_T + EPS))


def build_load_bracket():
    """Channel on the live end: a pad with two bolt holes, two ears with an axle bore."""
    ei = YOKE_GAP / 2.0                      # inner face of an ear
    eo = ei + EAR_T                          # outer face of an ear
    hp = max(BEAM_W / 2.0, eo)               # half-width of the pad
    top = AXLE_H + AXLE_D / 2.0 + max(4.0, AXLE_D / 2.0)
    pts = [(-hp, 0.0), (hp, 0.0)]
    if hp - eo > 0.01:                       # a bar wider than the yoke: the pad steps out past the ears
        pts += [(hp, PAD_T), (eo, PAD_T)]
    pts += [(eo, top), (ei, top), (ei, PAD_T), (-ei, PAD_T), (-ei, top), (-eo, top)]
    if hp - eo > 0.01:
        pts += [(-eo, PAD_T), (-hp, PAD_T)]
    wp = cq.Workplane("YZ").polyline(pts).close()
    bracket = wp.extrude(PAD_L).translate((-PAD_L / 2.0, 0, 0))
    bolts = [(-LIVE_PITCH / 2.0, 0.0), (LIVE_PITCH / 2.0, 0.0)]
    bracket = bracket.cut(holes_z(bolts, LIVE_BOLT_D, -EPS, PAD_T + EPS))
    axle = (cq.Workplane("XZ").circle(AXLE_D / 2.0).extrude(2.0 * eo + 2.0 * EPS)
            .translate((0, eo + EPS, AXLE_H)))
    return bracket.cut(axle)


BUILDERS = {"base": build_base, "load_bracket": build_load_bracket}
result = BUILDERS.get(PART, build_base)()
