"""
Shaft Encoder Mount — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The two parts that turn the end of a shaft into an angle sensor. A magnetic
angle sensor reads one small magnet turning on the axis in front of it, so two
things have to be held: the magnet, centred on the end of the shaft, and the
sensor board, centred on the same axis a short gap away. The Common Denominator
Geometry is that axis and what sits on it: the shaft, the magnet and the
board's hole pattern.

Parts (dispatched via `target_part`):
  * "magnet_cap"    — a cap that slips onto the shaft end, with a pocket in its
                      outer face for a disc magnet and a set screw to hold it.
  * "sensor_bridge" — a bridge on two feet with a window on the axis. The board
                      is screwed on top with its chip looking down through the
                      window at the magnet.

Frame, cap: the shaft axis is Z; the open end of the shaft bore is Z = 0 and
the magnet pocket opens at the top. Frame, bridge: the mounting face is Z = 0,
the shaft axis is Z through the origin, and the feet are on X.

Construction: the cap is ONE profile revolved about the axis (bore, web and
pocket in a single wire); the bridge is ONE hat-shaped outline extruded along
Y. Both are then cut. Nothing is unioned, and both hollows of the cap are open.

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


SHAFT_D = float(PARAM(lambda: shaft_d, 8.0))
SHAFT_FIT = float(PARAM(lambda: shaft_fit, 0.1))
BORE_DEPTH = float(PARAM(lambda: bore_depth, 10.0))
MAGNET_D = float(PARAM(lambda: magnet_d, 6.0))
MAGNET_H = float(PARAM(lambda: magnet_h, 2.5))
MAGNET_FIT = float(PARAM(lambda: magnet_fit, 0.1))
WEB_T = float(PARAM(lambda: web_t, 1.5))
CAP_WALL = float(PARAM(lambda: cap_wall, 3.0))
SETSCREW = as_bool(PARAM(lambda: setscrew, True))
SET_D = float(PARAM(lambda: set_d, 3.0))
BOARD_PX = float(PARAM(lambda: board_px, 20.0))
BOARD_PY = float(PARAM(lambda: board_py, 14.0))
BOARD_HOLE_D = float(PARAM(lambda: board_hole_d, 2.7))
WINDOW_D = float(PARAM(lambda: window_d, 10.0))
STAND_H = float(PARAM(lambda: stand_h, 25.0))
LEG_SPAN = float(PARAM(lambda: leg_span, 50.0))
BRIDGE_D = float(PARAM(lambda: bridge_d, 24.0))
PLATE_T = float(PARAM(lambda: plate_t, 3.0))
FOOT_W = float(PARAM(lambda: foot_w, 12.0))
MOUNT_BOLT_D = float(PARAM(lambda: mount_bolt_d, 3.4))
PART = str(PARAM(lambda: target_part, "magnet_cap"))

EPS = 1.0                                   # through-cut overshoot


def build_magnet_cap():
    rs = (SHAFT_D + SHAFT_FIT) / 2.0         # shaft bore
    rm = (MAGNET_D + MAGNET_FIT) / 2.0       # magnet pocket
    ro = max(rs, rm) + CAP_WALL
    floor = BORE_DEPTH + WEB_T               # floor of the magnet pocket
    top = floor + MAGNET_H
    pts = [(rs, 0.0), (ro, 0.0), (ro, top), (rm, top), (rm, floor), (0.0, floor),
           (0.0, BORE_DEPTH), (rs, BORE_DEPTH)]
    cap = cq.Workplane("XY").polyline(pts).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    cap = cap.rotate((0, 0, 0), (1, 0, 0), 90)        # the profile's Y becomes Z
    if SETSCREW:
        screw = (cq.Workplane("YZ").circle(SET_D / 2.0).extrude(ro + EPS)
                 .translate((0, 0, BORE_DEPTH / 2.0)))
        cap = cap.cut(screw)
    return cap


def build_sensor_bridge():
    inner = LEG_SPAN / 2.0                   # inner face of a leg
    outer = inner + PLATE_T                  # outer face of a leg
    wide = outer + FOOT_W
    top = STAND_H + PLATE_T
    pts = [(-wide, 0.0), (-inner, 0.0), (-inner, STAND_H), (inner, STAND_H), (inner, 0.0), (wide, 0.0),
           (wide, PLATE_T), (outer, PLATE_T), (outer, top), (-outer, top), (-outer, PLATE_T), (-wide, PLATE_T)]
    bridge = (cq.Workplane("XZ").polyline(pts).close().extrude(BRIDGE_D)   # XZ extrudes toward -Y
              .translate((0, BRIDGE_D / 2.0, 0)))
    window = cq.Workplane("XY").circle(WINDOW_D / 2.0).extrude(PLATE_T + 2.0 * EPS).translate((0, 0, STAND_H - EPS))
    bridge = bridge.cut(window)
    ys = [0.0] if BOARD_PY < 1.0 else [-BOARD_PY / 2.0, BOARD_PY / 2.0]
    board = [(sx * BOARD_PX / 2.0, y) for sx in (-1.0, 1.0) for y in ys]
    bridge = bridge.cut(cq.Workplane("XY").pushPoints(board).circle(BOARD_HOLE_D / 2.0)
                        .extrude(PLATE_T + 2.0 * EPS).translate((0, 0, STAND_H - EPS)))
    feet = [(sx * (outer + FOOT_W / 2.0), 0.0) for sx in (-1.0, 1.0)]
    return bridge.cut(cq.Workplane("XY").pushPoints(feet).circle(MOUNT_BOLT_D / 2.0)
                      .extrude(PLATE_T + 2.0 * EPS).translate((0, 0, -EPS)))


BUILDERS = {"magnet_cap": build_magnet_cap, "sensor_bridge": build_sensor_bridge}
result = BUILDERS.get(PART, build_magnet_cap)()
