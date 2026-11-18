"""
Index Pin — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A pull pin: the loose half of a pin-and-hole adjustment. The shank passes
through a guide and into one of a row of holes, a collar stops it at the right
depth, and a grip lets a hand pull it out again. The Common Denominator
Geometry is the shank every such pin shares: its diameter, the fit it leaves in
the hole and the length it engages.

Parts (dispatched via `target_part`):
  * "pull_pin" — shank, collar and a round knob with a waist for the fingers;
                 optionally a cross hole in the knob for a lanyard or a ring.
  * "tee_pin"  — the same shank and collar under a T-handle, for a pin that is
                 pulled against friction or with a gloved hand.

Either pin can carry a cross hole near the tip for a spring clip, which keeps a
pin that passes right through from working out.

Frame: the pin axis is Z. The underside of the collar is Z = 0; the shank runs
down to Z = -engage_l and the grip stands above the collar.

Construction: the shank, the collar and the grip are ONE profile revolved about
the axis, so no two coaxial cylinders are ever fused. The T-handle is a bar
across the top of the stem, which ends inside it. Cross holes are cut through.

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


PIN_D = float(PARAM(lambda: pin_d, 10.0))
FIT = float(PARAM(lambda: fit, 0.2))
ENGAGE_L = float(PARAM(lambda: engage_l, 30.0))
TIP_CHAMFER = float(PARAM(lambda: tip_chamfer, 1.0))
COLLAR_D = float(PARAM(lambda: collar_d, 18.0))
COLLAR_T = float(PARAM(lambda: collar_t, 4.0))
GRIP_D = float(PARAM(lambda: grip_d, 26.0))
GRIP_H = float(PARAM(lambda: grip_h, 22.0))
LANYARD = as_bool(PARAM(lambda: lanyard, False))
LANYARD_D = float(PARAM(lambda: lanyard_d, 3.0))
HANDLE_L = float(PARAM(lambda: handle_l, 60.0))
HANDLE_D = float(PARAM(lambda: handle_d, 12.0))
HANDLE_RISE = float(PARAM(lambda: handle_rise, 16.0))
CLIP_HOLE = as_bool(PARAM(lambda: clip_hole, False))
CLIP_D = float(PARAM(lambda: clip_d, 2.0))
CLIP_OFFSET = float(PARAM(lambda: clip_offset, 6.0))
PART = str(PARAM(lambda: target_part, "pull_pin"))

EPS = 1.0                                   # through-cut overshoot
RP = max(1.0, (PIN_D - FIT) / 2.0)          # shank radius: the nominal hole less the fit
RC = max(COLLAR_D / 2.0, RP + 0.5)          # the collar always stands proud of the shank
CHAMFER = min(max(TIP_CHAMFER, 0.0), RP - 0.5)


def revolve_z(profile):
    """Revolve a closed (radius, z) profile about the pin axis."""
    body = cq.Workplane("XY").polyline(profile).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    return body.rotate((0, 0, 0), (1, 0, 0), 90)      # the profile's Y becomes Z


def cross_hole(d, z, length):
    """A hole along X through the axis at height z."""
    return (cq.Workplane("YZ").circle(d / 2.0).extrude(length)
            .translate((-length / 2.0, 0, z)))


def shank_profile():
    """The shank and the collar, from the tip up to the top of the collar, as (radius, z)."""
    pts = [(0.0, -ENGAGE_L)]
    if CHAMFER > 0.05:
        pts += [(RP - CHAMFER, -ENGAGE_L), (RP, -ENGAGE_L + CHAMFER)]
    else:
        pts.append((RP, -ENGAGE_L))
    return pts + [(RP, 0.0), (RC, 0.0), (RC, COLLAR_T)]


def with_clip(body):
    if not CLIP_HOLE:
        return body
    z = -ENGAGE_L + min(max(CLIP_OFFSET, CLIP_D), ENGAGE_L - CLIP_D)
    return body.cut(cross_hole(CLIP_D, z, 2.0 * RP + 2.0 * EPS))


def build_pull_pin():
    rg = max(GRIP_D / 2.0, RP + 1.0)
    rn = max(RP, 0.55 * rg)                           # the waist the fingers hook under
    if abs(rn - RC) < 0.05:
        rn -= 0.5
    neck_h = 0.3 * GRIP_H
    flare = min(rg - rn, 0.3 * GRIP_H)
    top = COLLAR_T + GRIP_H
    pts = shank_profile() + [(rn, COLLAR_T), (rn, COLLAR_T + neck_h), (rg, COLLAR_T + neck_h + flare),
                             (rg, top), (0.0, top)]
    pin = revolve_z(pts)
    if LANYARD:
        head_mid = (COLLAR_T + neck_h + flare + top) / 2.0
        pin = pin.cut(cross_hole(LANYARD_D, head_mid, 2.0 * rg + 2.0 * EPS))
    return with_clip(pin)


def build_tee_pin():
    rh = HANDLE_D / 2.0
    rs = max(1.5, min(max(RP, 3.0), rh - 1.0))        # the stem ends inside the handle bar
    if abs(rs - RC) < 0.05:
        rs -= 0.5
    axis_z = COLLAR_T + max(HANDLE_RISE, rh + 1.0)
    pts = shank_profile() + [(rs, COLLAR_T), (rs, axis_z), (0.0, axis_z)]
    pin = revolve_z(pts)
    bar = (cq.Workplane("YZ").circle(rh).extrude(HANDLE_L).translate((-HANDLE_L / 2.0, 0, axis_z)))
    return with_clip(pin.union(bar))


BUILDERS = {"pull_pin": build_pull_pin, "tee_pin": build_tee_pin}
result = BUILDERS.get(PART, build_pull_pin)()
