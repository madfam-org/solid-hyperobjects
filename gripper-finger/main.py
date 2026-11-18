"""
Gripper Finger — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A finger for a parallel-jaw gripper: the part that bolts onto the moving jaw of
a robot gripper, a bench vice or a clamp and actually touches the workpiece. A
gripper is bought; its fingers are made for each part it has to hold. The
Common Denominator Geometry is the jaw's own mounting pattern (two bolts in a
line) and the face that grips.

Part (dispatched via `target_part`):
  * "finger" — a bar that bolts to the jaw by its root and reaches forward. Its
               gripping face is flat, or carries a V notch that centres a round
               body; two extra holes near the tip can take a bolted-on pad.

Frame: the finger reaches along +X from its root at X = 0. The gripping face is
the plane Y = 0 (the workpiece is toward -Y) and the back, which seats on the
jaw, is Y = finger_t. The finger stands from Z = 0 to Z = finger_h; the notch
runs along Z.

Construction: ONE outline (the bar seen from above, with the notch in it)
extruded along Z, then drilled. Nothing is unioned.

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


REACH = float(PARAM(lambda: reach, 80.0))
FINGER_T = float(PARAM(lambda: finger_t, 16.0))
FINGER_H = float(PARAM(lambda: finger_h, 30.0))
JAW_PITCH = float(PARAM(lambda: jaw_pitch, 20.0))
JAW_BOLT_D = float(PARAM(lambda: jaw_bolt_d, 5.5))
ROOT_MARGIN = float(PARAM(lambda: root_margin, 8.0))
VEE = as_bool(PARAM(lambda: vee, True))
VEE_X = float(PARAM(lambda: vee_x, 58.0))
VEE_W = float(PARAM(lambda: vee_w, 24.0))
VEE_DEPTH = float(PARAM(lambda: vee_depth, 8.0))
PAD_HOLES = as_bool(PARAM(lambda: pad_holes, False))
PAD_SPAN = float(PARAM(lambda: pad_span, 16.0))
PAD_BOLT_D = float(PARAM(lambda: pad_bolt_d, 3.4))
PART = str(PARAM(lambda: target_part, "finger"))

EPS = 1.0                                   # through-cut overshoot


def holes_y(points, d):
    """Cylinders along Y through the finger at (x, z) points."""
    tool = None
    for x, z in points:
        c = (cq.Workplane("XZ").circle(d / 2.0).extrude(FINGER_T + 2.0 * EPS)      # XZ extrudes toward -Y
             .translate((x, FINGER_T + EPS, z)))
        tool = c if tool is None else tool.union(c)
    return tool


def build_finger():
    pts = [(0.0, 0.0)]
    if VEE:
        half = VEE_W / 2.0
        depth = min(VEE_DEPTH, FINGER_T - 2.0)
        pts += [(VEE_X - half, 0.0), (VEE_X, depth), (VEE_X + half, 0.0)]
    pts += [(REACH, 0.0), (REACH, FINGER_T), (0.0, FINGER_T)]
    finger = cq.Workplane("XY").polyline(pts).close().extrude(FINGER_H)
    mid = FINGER_H / 2.0
    finger = finger.cut(holes_y([(ROOT_MARGIN, mid), (ROOT_MARGIN + JAW_PITCH, mid)], JAW_BOLT_D))
    if PAD_HOLES:
        x = REACH - max(6.0, PAD_BOLT_D + 3.0)
        finger = finger.cut(holes_y([(x, mid - PAD_SPAN / 2.0), (x, mid + PAD_SPAN / 2.0)], PAD_BOLT_D))
    return finger


result = build_finger()
