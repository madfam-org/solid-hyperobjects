"""
Cable Spool — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A flanged drum that winds a cable, cord or rope and mounts on a shaft. The
Common Denominator Geometry is the pair every winding drive shares: the shaft
bore the drum locks to, and the drum the cable lays on (its diameter sets the
torque arm and the bend the cable has to survive).

Parts (dispatched via `target_part`):
  * "spool"     — the plain drum: two flanges, a through bore, an optional
                  keyway, and an anchor hole through one flange for the cable end.
  * "spool_hub" — the same drum with a hub boss on one side carrying two radial
                  set-screw holes at 90 degrees, for a plain or D-cut shaft.

The axis is Z, so the part prints flange-down without supports on the drum.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals; read them through PARAM()
    so the script also runs standalone with any subset of them.
  - Assign the final solid to a top-level name `result`.
"""

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


DRUM_D = float(PARAM(lambda: drum_d, 70.0))
DRUM_W = float(PARAM(lambda: drum_w, 60.0))
FLANGE_H = float(PARAM(lambda: flange_h, 15.0))
FLANGE_T = float(PARAM(lambda: flange_t, 5.0))
BORE = float(PARAM(lambda: bore, 19.0))
CABLE_D = float(PARAM(lambda: cable_d, 5.0))
ANCHOR = as_bool(PARAM(lambda: anchor, True))
KEYWAY = as_bool(PARAM(lambda: keyway, False))
KEY_W = float(PARAM(lambda: key_w, 6.0))
HUB_D = float(PARAM(lambda: hub_d, 40.0))
HUB_L = float(PARAM(lambda: hub_l, 16.0))
SETSCREW_D = float(PARAM(lambda: setscrew_dia, 5.0))
PART = str(PARAM(lambda: target_part, "spool"))

EPS = 1.0                                   # real overlap wherever two features join
LENGTH = DRUM_W + 2.0 * FLANGE_T            # overall length along the axis
DRUM_R = DRUM_D / 2.0
RIM_R = DRUM_R + FLANGE_H
BORE_R = min(BORE / 2.0, DRUM_R - 2.0)      # never break through the drum wall


def revolve_z(points):
    """Revolve a closed (radius, z) profile about the Z axis."""
    return cq.Workplane("XZ").polyline(points).close().revolve(360.0, (0, 0, 0), (0, 1, 0))


def drum():
    """Flanged drum with a through bore, flange-down on Z = 0."""
    return revolve_z([
        (BORE_R, 0.0), (RIM_R, 0.0), (RIM_R, FLANGE_T), (DRUM_R, FLANGE_T),
        (DRUM_R, LENGTH - FLANGE_T), (RIM_R, LENGTH - FLANGE_T), (RIM_R, LENGTH),
        (BORE_R, LENGTH),
    ])


def cut_keyway(body, top):
    """A square keyway along the whole bore, opening toward +Y."""
    depth = KEY_W / 2.0
    key = (cq.Workplane("XY").box(KEY_W, BORE_R + depth, top + 2.0 * EPS, centered=(True, False, False))
           .translate((0, 0, -EPS)))
    return body.cut(key)


def anchor_hole(side, z):
    """The anchor hole, centred in the flange height so it never touches the drum or the rim."""
    return (cq.Workplane("XY").cylinder(FLANGE_T + 2.0 * EPS, (CABLE_D + 1.0) / 2.0)
            .translate((side * (DRUM_R + FLANGE_H / 2.0), 0, z)))


def cut_anchor(body):
    """A hole through the top flange, beside the drum, to knot or crimp the cable end."""
    return body.cut(anchor_hole(1.0, LENGTH - FLANGE_T / 2.0))


def build_spool():
    body = drum()
    if KEYWAY:
        body = cut_keyway(body, LENGTH)
    return cut_anchor(body) if ANCHOR else body


def build_spool_hub():
    hub_r = max(HUB_D / 2.0, BORE_R + 3.0)
    hub = (cq.Workplane("XY").cylinder(HUB_L + EPS, hub_r)
           .translate((0, 0, LENGTH + (HUB_L - EPS) / 2.0)))
    body = drum().union(hub)
    bore_cut = (cq.Workplane("XY").cylinder(LENGTH + HUB_L + 2.0 * EPS, BORE_R)
                .translate((0, 0, (LENGTH + HUB_L) / 2.0)))
    body = body.cut(bore_cut)
    for angle in (0.0, 90.0):               # two set screws at 90 degrees
        screw = (cq.Workplane("XY").cylinder(hub_r + EPS, SETSCREW_D / 2.0)
                 .rotate((0, 0, 0), (0, 1, 0), 90)
                 .translate(((hub_r + EPS) / 2.0, 0, LENGTH + HUB_L / 2.0))
                 .rotate((0, 0, 0), (0, 0, 1), angle))
        body = body.cut(screw)
    if KEYWAY:
        body = cut_keyway(body, LENGTH + HUB_L)
    if ANCHOR:
        body = body.cut(anchor_hole(-1.0, FLANGE_T / 2.0))   # the hub side stays clear
    return body


if PART == "spool_hub":
    result = build_spool_hub()
else:
    result = build_spool()
