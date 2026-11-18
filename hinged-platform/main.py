"""
Hinged Platform — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A load-bearing panel that folds on a pin along one edge, and the block it turns
on: a fold-down platform, a step, a bench seat, a table leaf, a ramp or a
tailgate. The Common Denominator Geometry is the hinge line both parts share:
the panel thickness (which is also the barrel diameter), the pin, and the width
of the blocks the panel is notched for.

Parts (dispatched via `target_part`):
  * "panel"       — the platform. Its hinge edge is rounded about the pin and
                    notched where each block sits; a skid under the free edge
                    carries it to the floor when it is down.
  * "hinge_block" — one fixed block: a barrel the pin passes through, standing
                    on a flange that bolts down behind the hinge line.

With `lock` on, a second, smaller hole runs beside the pin: through the panel
from its side edge and through the barrel of each block. The two line up only
when the panel stands at 90 degrees, so a pull pin pushed in from the side
holds it folded.

Frame, both parts: the hinge axis is X through the origin. The panel lies flat
toward +Y with its mid-plane on Z = 0; folding turns +Y toward +Z. The block's
mounting face is Z = -axis_h and its flange reaches toward -Y. A block drawn in
this frame sits in the panel's notch as modelled.

Construction: each part is ONE outline (with the round of the hinge edge or of
the barrel as an arc of the same wire) extruded along X, then cut. Nothing is
unioned, so no round ever shares a surface with a flat.

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


PANEL_T = float(PARAM(lambda: panel_t, 30.0))
PIN_D = float(PARAM(lambda: pin_d, 8.0))
BLOCK_W = float(PARAM(lambda: block_w, 50.0))
LOCK = as_bool(PARAM(lambda: lock, False))
LOCK_D = float(PARAM(lambda: lock_d, 5.0))
PANEL_W = float(PARAM(lambda: panel_w, 600.0))
PANEL_L = float(PARAM(lambda: panel_l, 800.0))
BLOCKS = int(round(float(PARAM(lambda: blocks, 2))))
BLOCK_INSET = float(PARAM(lambda: block_inset, 80.0))
SIDE_GAP = float(PARAM(lambda: side_gap, 1.0))
SKID_H = float(PARAM(lambda: skid_h, 30.0))
SKID_D = float(PARAM(lambda: skid_d, 40.0))
AXIS_H = float(PARAM(lambda: axis_h, 30.0))
FLANGE_L = float(PARAM(lambda: flange_l, 50.0))
FLANGE_T = float(PARAM(lambda: flange_t, 8.0))
BOLT_D = float(PARAM(lambda: bolt_d, 6.5))
PART = str(PARAM(lambda: target_part, "panel"))

EPS = 1.0                                   # through-cut overshoot
BORE_CLR = 0.4                              # running clearance of a bore on its pin, on the diameter
R = PANEL_T / 2.0                           # barrel radius: the panel is as thick as the barrel
LOCK_R = (PIN_D / 2.0 + R) / 2.0            # lock hole axis, midway between the pin bore and the barrel surface


def extrude_x(points, arc, x0, x1):
    """Extrude a closed (y, z) outline from x0 to x1; `arc` = (index, mid) makes the
    segment that starts at points[index] an arc through `mid`."""
    wp = cq.Workplane("YZ").moveTo(*points[0])
    for i in range(1, len(points)):
        if arc and arc[0] == i - 1:
            wp = wp.threePointArc(arc[1], points[i])
        else:
            wp = wp.lineTo(*points[i])
    if arc and arc[0] == len(points) - 1:
        return wp.threePointArc(arc[1], points[0]).close().extrude(x1 - x0).translate((x0, 0, 0))
    return wp.close().extrude(x1 - x0).translate((x0, 0, 0))


def box(x, y, z, cx=0.0, cy=0.0, cz=0.0):
    return cq.Workplane("XY").box(x, y, z).translate((cx, cy, cz))


def hole_x(d, y, z, x0, x1):
    """A cylinder along X at (y, z) from x0 to x1."""
    return cq.Workplane("YZ").circle(d / 2.0).extrude(x1 - x0).translate((x0, y, z))


def block_centres():
    """X of each hinge block: the outer two `block_inset` from the side edges, the rest evenly between."""
    n = max(2, BLOCKS)
    first = -PANEL_W / 2.0 + BLOCK_INSET
    step = (PANEL_W - 2.0 * BLOCK_INSET) / (n - 1)
    return [first + i * step for i in range(n)]


def build_panel():
    if SKID_H > 0.5:                         # the skid is part of the outline: one wire, no union
        pts = [(0.0, -R), (PANEL_L - SKID_D, -R), (PANEL_L - SKID_D, -R - SKID_H),
               (PANEL_L, -R - SKID_H), (PANEL_L, R), (0.0, R)]
    else:
        pts = [(0.0, -R), (PANEL_L, -R), (PANEL_L, R), (0.0, R)]
    panel = extrude_x(pts, (len(pts) - 1, (-R, 0.0)), -PANEL_W / 2.0, PANEL_W / 2.0)
    notch_w = BLOCK_W + 2.0 * SIDE_GAP
    reach = R + SIDE_GAP + 1.0               # the barrel turns inside the notch
    for cx in block_centres():
        panel = panel.cut(box(notch_w, R + EPS + reach, PANEL_T + 2.0 * EPS, cx=cx, cy=(reach - R - EPS) / 2.0))
    panel = panel.cut(hole_x(PIN_D + BORE_CLR, 0.0, 0.0, -PANEL_W / 2.0 - EPS, PANEL_W / 2.0 + EPS))
    if LOCK:                                 # from the side edge into the first block's notch and 6 mm past it
        x_end = block_centres()[0] + notch_w / 2.0 + 6.0
        panel = panel.cut(hole_x(LOCK_D + BORE_CLR, LOCK_R, 0.0, -PANEL_W / 2.0 - EPS, x_end))
    return panel


def build_hinge_block():
    axis = max(AXIS_H, FLANGE_T + 2.0)
    reach = max(FLANGE_L, R + 2.0)
    pts = [(-reach, -axis), (R, -axis), (R, 0.0), (-R, 0.0), (-R, -axis + FLANGE_T), (-reach, -axis + FLANGE_T)]
    block = extrude_x(pts, (2, (0.0, R)), -BLOCK_W / 2.0, BLOCK_W / 2.0)
    block = block.cut(hole_x(PIN_D + BORE_CLR, 0.0, 0.0, -BLOCK_W / 2.0 - EPS, BLOCK_W / 2.0 + EPS))
    if LOCK:
        block = block.cut(hole_x(LOCK_D + BORE_CLR, 0.0, LOCK_R, -BLOCK_W / 2.0 - EPS, BLOCK_W / 2.0 + EPS))
    by = -(R + reach) / 2.0                  # the bolts sit mid-way along the flange behind the barrel
    xs = [-BLOCK_W / 4.0, BLOCK_W / 4.0] if BLOCK_W >= 4.0 * BOLT_D else [0.0]
    bolts = (cq.Workplane("XY").pushPoints([(x, by) for x in xs]).circle(BOLT_D / 2.0)
             .extrude(FLANGE_T + 2.0 * EPS).translate((0, 0, -axis - EPS)))
    return block.cut(bolts)


BUILDERS = {"panel": build_panel, "hinge_block": build_hinge_block}
result = BUILDERS.get(PART, build_panel)()
