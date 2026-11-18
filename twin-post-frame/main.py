"""
Twin-Post Frame — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The two fixed members that hold a pair of parallel posts standing: a floor base
with a socket for each post, and a crossbar that ties their tops. Together with
two posts they make a freestanding portal: a rack, a stand, a gantry, a rail
for clothes or tools. The Common Denominator Geometry is what both members
share: the section of the post and the distance between the two.

Parts (dispatched via `target_part`):
  * "base"     — two rails joined by a rear and a front member. Each rail has a
                 socket the post stands in and a bolt hole up through its floor;
                 four holes at the corners take levelling feet.
  * "crossbar" — a bar across the two post tops, with a bolt hole down into
                 each and, optionally, a shallow pocket that caps the post.
                 With the arm mount on, two blind holes in its front face take
                 the bolts of a hanging accessory: an arm, a sign, a hook rail.

Frame, base: the floor is Z = 0, the two posts stand at X = -spacing/2 and
+spacing/2 on the line Y = 0, the rear of the base is toward -Y. Frame,
crossbar: its underside is Z = 0 and the posts meet it on the same two points.

Construction: the base is ONE outline (the outer rectangle with the window
between the rails as an inner wire) extruded once, then cut. The crossbar is a
box, cut. Nothing is unioned. Each socket and each cap is a blind pocket open
to one face, so no body holds a sealed void.

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


SPACING = float(PARAM(lambda: spacing, 600.0))
POST_W = float(PARAM(lambda: post_w, 50.0))
POST_D = float(PARAM(lambda: post_d, 50.0))
FIT = float(PARAM(lambda: fit, 0.6))
BOLT_D = float(PARAM(lambda: bolt_d, 8.5))
BASE_DEPTH = float(PARAM(lambda: base_depth, 500.0))
POST_Y = float(PARAM(lambda: post_y, 200.0))
RAIL_MARGIN = float(PARAM(lambda: rail_margin, 20.0))
RAIL_H = float(PARAM(lambda: rail_h, 50.0))
REAR_D = float(PARAM(lambda: rear_d, 100.0))
FRONT_D = float(PARAM(lambda: front_d, 60.0))
SOCKET_DEPTH = float(PARAM(lambda: socket_depth, 10.0))
FOOT_BOLT_D = float(PARAM(lambda: foot_bolt_d, 8.5))
BAR_H = float(PARAM(lambda: bar_h, 50.0))
BAR_MARGIN = float(PARAM(lambda: bar_margin, 6.0))
CAP_DEPTH = float(PARAM(lambda: cap_depth, 5.0))
ARM_MOUNT = as_bool(PARAM(lambda: arm_mount, False))
ARM_BOLT_SPAN = float(PARAM(lambda: arm_bolt_span, 60.0))
ARM_HOLE_D = float(PARAM(lambda: arm_hole_d, 6.8))
ARM_MOUNT_DROP = float(PARAM(lambda: arm_mount_drop, 30.0))
PART = str(PARAM(lambda: target_part, "base"))

EPS = 1.0                                   # through-cut overshoot
POSTS = (-SPACING / 2.0, SPACING / 2.0)


def box(x, y, z, cx=0.0, cy=0.0, cz=0.0):
    return cq.Workplane("XY").box(x, y, z).translate((cx, cy, cz))


def holes_z(points, d, z0, z1):
    """Vertical cylinders at (x, y) points from z0 to z1."""
    return (cq.Workplane("XY").pushPoints(points).circle(d / 2.0)
            .extrude(z1 - z0).translate((0, 0, z0)))


def post_pockets(z0, z1):
    """A pocket per post, the post section plus the fit, between two heights."""
    pocket = None
    for px in POSTS:
        p = box(POST_W + 2.0 * FIT, POST_D + 2.0 * FIT, z1 - z0, cx=px, cz=(z0 + z1) / 2.0)
        pocket = p if pocket is None else pocket.union(p)
    return pocket


def build_base():
    rail_w = POST_W + 2.0 * RAIL_MARGIN
    span = SPACING + rail_w
    y_rear, y_front = -POST_Y, BASE_DEPTH - POST_Y
    mid_y = (y_rear + y_front) / 2.0
    win_w = SPACING - rail_w                 # the window between the rails
    win_d = BASE_DEPTH - REAR_D - FRONT_D
    outline = cq.Workplane("XY").center(0, mid_y).rect(span, BASE_DEPTH)
    if win_w > 1.0 and win_d > 1.0:
        win_y = (y_rear + REAR_D + y_front - FRONT_D) / 2.0
        outline = outline.center(0, win_y - mid_y).rect(win_w, win_d)
    base = outline.extrude(RAIL_H)
    depth = min(SOCKET_DEPTH, RAIL_H - 2.0)
    base = base.cut(post_pockets(RAIL_H - depth, RAIL_H + EPS))
    base = base.cut(holes_z([(px, 0.0) for px in POSTS], BOLT_D, -EPS, RAIL_H + EPS))
    inset = max(10.0, FOOT_BOLT_D)
    fx = span / 2.0 - rail_w / 2.0           # on the rail centre line, clear of the socket in Y
    feet = [(sx * fx, y) for sx in (-1.0, 1.0) for y in (y_rear + inset, y_front - inset)]
    return base.cut(holes_z(feet, FOOT_BOLT_D, -EPS, RAIL_H + EPS))


def build_crossbar():
    length = SPACING + POST_W + 2.0 * BAR_MARGIN
    depth = POST_D + 2.0 * BAR_MARGIN
    bar = box(length, depth, BAR_H, cz=BAR_H / 2.0)
    cap = min(CAP_DEPTH, BAR_H - 2.0)
    if cap > 0.2 and BAR_MARGIN >= 1.0:
        bar = bar.cut(post_pockets(-EPS, cap))
    bar = bar.cut(holes_z([(px, 0.0) for px in POSTS], BOLT_D, -EPS, BAR_H + EPS))
    if ARM_MOUNT:                            # two blind holes in the front face (+Y), open to it
        reach = min(20.0, depth - 3.0)
        z = BAR_H - ARM_MOUNT_DROP
        for sx in (-1.0, 1.0):
            hole = (cq.Workplane("XZ").circle(ARM_HOLE_D / 2.0).extrude(reach + EPS)     # XZ extrudes toward -Y
                    .translate((sx * ARM_BOLT_SPAN / 2.0, depth / 2.0 + EPS, z)))
            bar = bar.cut(hole)
    return bar


BUILDERS = {"base": build_base, "crossbar": build_crossbar}
result = BUILDERS.get(PART, build_base)()
