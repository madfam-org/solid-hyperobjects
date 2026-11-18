"""
Cord Cut Jig — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

Two blocks that screw to a bench and cut cord, rope, cable or tube to the same
length every time. One holds the end; the other guides the blade. The length is
the distance between them on the bench, set once with a tape. The Common
Denominator Geometry is the cord: its diameter sizes the channel it lies in.

Parts (dispatched via `target_part`):
  * "anchor_peg" — a base with a round peg. The end loop, knot or fitting of
                   the cord hooks over the peg, so every piece starts at the
                   same point.
  * "cut_block"  — a block with a channel across its top that the cord lies in,
                   and a slot across the channel that guides a knife or a hot
                   knife straight down through it.

Frame, both parts: the bench is Z = 0 and the cord runs along X. The peg stands
on the origin; the blade slot of the cut block is the plane X = 0.

Construction: the anchor is ONE block as tall as the peg, cut down to the plate
everywhere but the peg; the cut block is ONE outline (with the channel in it)
extruded along the cord, then cut. Nothing is unioned.

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


CORD_D = float(PARAM(lambda: cord_d, 5.0))
SCREW_D = float(PARAM(lambda: screw_d, 4.5))
BASE_T = float(PARAM(lambda: base_t, 10.0))
PEG_D = float(PARAM(lambda: peg_d, 10.0))
PEG_H = float(PARAM(lambda: peg_h, 25.0))
BASE_L = float(PARAM(lambda: base_l, 70.0))
BASE_W = float(PARAM(lambda: base_w, 40.0))
BLOCK_L = float(PARAM(lambda: block_l, 60.0))
BLOCK_W = float(PARAM(lambda: block_w, 60.0))
BLOCK_H = float(PARAM(lambda: block_h, 25.0))
BLADE_W = float(PARAM(lambda: blade_w, 1.2))
PART = str(PARAM(lambda: target_part, "anchor_peg"))

EPS = 1.0                                   # through-cut overshoot
CHANNEL_CLR = 0.5                           # play of the cord in its channel, on the width


def screw_holes(points, height):
    return (cq.Workplane("XY").pushPoints(points).circle(SCREW_D / 2.0)
            .extrude(height + 2.0 * EPS).translate((0, 0, -EPS)))


def build_anchor_peg():
    """A plate with a peg: a block as tall as the peg, cut down to the plate everywhere but the peg."""
    top = BASE_T + PEG_H
    block = cq.Workplane("XY").box(BASE_L, BASE_W, top).translate((0, 0, top / 2.0))
    waste = cq.Workplane("XY").box(BASE_L + 2.0 * EPS, BASE_W + 2.0 * EPS, PEG_H + EPS).translate((0, 0, BASE_T + (PEG_H + EPS) / 2.0))
    waste = waste.cut(cq.Workplane("XY").circle(PEG_D / 2.0).extrude(PEG_H + 4.0 * EPS).translate((0, 0, BASE_T - EPS)))
    anchor = block.cut(waste)
    x = BASE_L / 2.0 - (SCREW_D + 4.0)
    return anchor.cut(screw_holes([(-x, 0.0), (x, 0.0)], BASE_T))


def build_cut_block():
    """A block with a square-bottomed channel along X and a blade slot across it at X = 0."""
    half_w = BLOCK_W / 2.0
    ch = (CORD_D + CHANNEL_CLR) / 2.0        # half-width of the channel
    depth = 0.75 * CORD_D                    # the cord sits three quarters into the block
    pts = [(-half_w, 0.0), (half_w, 0.0), (half_w, BLOCK_H), (ch, BLOCK_H), (ch, BLOCK_H - depth),
           (-ch, BLOCK_H - depth), (-ch, BLOCK_H), (-half_w, BLOCK_H)]
    block = (cq.Workplane("YZ").polyline(pts).close().extrude(BLOCK_L).translate((-BLOCK_L / 2.0, 0, 0)))
    slot_depth = depth + 2.0                 # the blade passes 2 mm below the cord
    block = block.cut(cq.Workplane("XY").box(BLADE_W, BLOCK_W + 2.0 * EPS, slot_depth + EPS)
                      .translate((0, 0, BLOCK_H - slot_depth + (slot_depth + EPS) / 2.0)))
    x = BLOCK_L / 2.0 - (SCREW_D + 4.0)
    y = half_w - (SCREW_D + 4.0)
    return block.cut(screw_holes([(-x, y), (x, -y)], BLOCK_H))


BUILDERS = {"anchor_peg": build_anchor_peg, "cut_block": build_cut_block}
result = BUILDERS.get(PART, build_anchor_peg)()
