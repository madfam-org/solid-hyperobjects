"""
A/B Drive — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A printed A/B drive unit for a CoreXY gantry whose two belts run stacked on two levels (a
Voron 2.4-class flying gantry). It joins the rear end of a gantry Y extrusion (a 2020 "C"
extrusion) to the rear gantry beam (the "E" extrusion), hangs a NEMA 17 under a motor plate
behind the extrusion's end, and carries three belt elements:

  - the motor's GT2 20T pulley, which drives this unit's belt;
  - a backside F695 stack (the belt's back on it) that wraps that belt round the pulley past
    the 108° that six teeth in mesh need (SDP/SI §13.3: at least 6 teeth in mesh and 60° of
    wrap on a loaded pulley; a 20-tooth pulley turns 18° per tooth);
  - a pass-through F695 stack (the belt's teeth on it) that turns the OTHER belt from the
    gantry side to the rear beam, on the other level.

It is an ORIGINAL design built to functional facts cited by page from the Voron 2.4r2 build
guide (GPL-3.0; pp. 73–80: the A and B drives, a NEMA 17 with a GT2 20T pulley and F695
stacks on M5x30 BHCS threaded into plastic; pp. 85–87: the rear E extrusion and the drives
on M5 T-nuts and M5x10 BHCS; p. 125: the stacked belt path) and from datasheets. No Voron
geometry is copied, traced or derived.

The default is the LEFT (B) drive: its pulley and backside stack on the low belt level (22
above the C extrusion), the pass-through stack on the high level (31). `mirrored` builds the
RIGHT (A) drive: x reflected and the levels swapped. Both hang the motor face at the same
height (z 10), so the pulley's seat on the shaft differs: 4 for the left, 13 for the right
(the pulley's belt mid-plane is 8 from its face A, a convention shared with the keystone's
gt2-pulley-20t-5mm).

Model frame: origin on the C extrusion's top face, on its centreline, at its REAR end face;
+x to the gantry's right, +y to the back (beyond the extrusion's end), +z up.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `mirrored`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr.
  - Assign the final solid to a top-level name `result`.
"""

import math

import cadquery as cq


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Cited facts ──────────────────────────────────────────────────────────────
# NEMA 17 (keystone nema-17-48mm: LDO, Nanotec): face 42.3, 4 × M3 on 31, pilot Ø22 × 2,
# M3 thread depth 4.5 min, shaft 24.
NEMA_FACE = 42.3
NEMA_BOLT = 31.0
NEMA_PILOT = 22.0
# GT2 20T pulley pitch diameter 12.73 (SDP/SI Table 33); flange Ø16 (Adafruit 1251).
PULLEY_R = 12.7324 / 2.0
PULLEY_FLANGE = 16.0
# F695 OD 13, flange 15 (NSK); stack 10 tall (1 mm DIN 988 shims, 4 mm F695).
F695_OD = 13.0
FLANGE_D = 15.0
STACK_H = 10.0
# GT2 2 mm belt: B 1.52, T 0.76 (Pfeifer 2MR/PGGT2), U 0.254 (SDP/SI Table 4).
TEETH_OFF = 0.76 + 0.254
BACK_OFF = 1.52 - 0.76 - 0.254
# ISO 7380-1 M5x30 BHCS (guide pp. 73, 77): l 30, head dk 9.5. ISO 7380-1 M5x10 (pp. 86–87).
AXLE_L = 30.0
M5_HEAD = 9.5
# MISUMI HFS5-2020: 20 profile, 6 mm slot, 2 mm lips; Ø4.2 the hole MISUMI taps M5.
PROFILE = 20.0
SLOT_LIP_T = 2.0
PILOT_D = 4.2

# ── Conventions (labelled; not sourced facts) ────────────────────────────────
LOW, HIGH = 22.0, 31.0                       # belt mid-planes above the C top
X_OUTER = 32.0 - (F695_OD / 2 + BACK_OFF) - 2 * (F695_OD / 2 + TEETH_OFF)  # 9.966: outer run
X_OTHER = 37.0 - PULLEY_R                    # 30.634: the other belt's run (xy-joint idler 37)
WRAP_DEG = 125.0                             # design wrap on the pulley (≥ 108°)
LEAD = 9.0                                   # straight span pulley → backside stack: keeps
                                             # the pulley's Ø16 and the F695's Ø15 flanges 0.6 apart
P_Y = 22.0                                   # pulley axis behind the C end (motor clears it)
MOTOR_FACE_Z = 10.0                          # motor face (plate underside)
PLATE_TOP = 17.0                             # plate top: the low stacks' floor (22 − 5)
BRIDGE_Z = 36.0                              # bridge underside: the high stacks' top
BRIDGE_T = 6.0                               # heads on z 42: M5x30 tips at z 12, 2 above the motor
E_END = 57.5                                 # rear beam end (E 340 between C centres ±227.5)
STATION = 10.0                               # slot stations, 10 from each extrusion's end
GRIP = 4.5                                   # M5x10 head seat above the clamped face
COL_R = 4.0
HOLE_CLEAR = 0.25
M3_CB = 6.5
TAB_W = 5.8

# ── Parameters ───────────────────────────────────────────────────────────────
mirrored = bool(PARAM(lambda: mirrored, False))   # the right (A) drive
target_part = str(PARAM(lambda: target_part, "ab_drive"))

z_pulley = HIGH if mirrored else LOW              # this unit's belt
z_pass = LOW if mirrored else HIGH                # the other belt
r_back = F695_OD / 2 + BACK_OFF
r_teeth = F695_OD / 2 + TEETH_OFF
P = (X_OUTER + PULLEY_R, P_Y)
_theta = math.radians(180.0 - WRAP_DEG)
Q = (P[0] + (PULLEY_R + r_back) * math.cos(_theta) + LEAD * math.sin(_theta),
     P[1] + (PULLEY_R + r_back) * math.sin(_theta) - LEAD * math.cos(_theta))
REAR_RUN_Y = Q[1] - r_back
S = (X_OTHER + r_teeth, REAR_RUN_Y - r_teeth)


def _box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def _cyl_z(x, y, d, z0, z1):
    solid = cq.Solid.makeCylinder(d / 2.0, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))
    return cq.Workplane("XY").add(solid)


def _columns(body, x, y, z_mid):
    lo, hi = z_mid - STACK_H / 2.0, z_mid + STACK_H / 2.0
    if lo > PLATE_TOP:
        body = body.union(_cyl_z(x, y, 2 * COL_R, PLATE_TOP - 0.5, lo))
    if hi < BRIDGE_Z:
        body = body.union(_cyl_z(x, y, 2 * COL_R, hi, BRIDGE_Z + 0.5))
    return body


def build_ab_drive():
    top = BRIDGE_Z + BRIDGE_T
    half = PROFILE / 2.0
    # Slab over the C's rear end and the E's end; the motor plate behind them.
    body = _box(-half, E_END + PROFILE, -PROFILE, 0.0, 0.0, PLATE_TOP)
    body = body.union(_box(-6.0, 46.0, -0.5, 44.0, MOTOR_FACE_Z, PLATE_TOP))
    # Tongues: in the C's top slot (along y) and the E's top slot (along x).
    body = body.union(_box(-TAB_W / 2, TAB_W / 2, -PROFILE + 1.0, -1.0, -SLOT_LIP_T, 0.5))
    body = body.union(_box(E_END + 1.5, E_END + PROFILE - 1.5, -half - TAB_W / 2,
                           -half + TAB_W / 2, -SLOT_LIP_T, 0.5))
    # Pillars, off every belt line and clear of the screw counterbores.
    for x0, x1, y0, y1 in ((-8.0, 5.0, -18.0, -2.0), (46.0, 56.0, -18.0, 9.0),
                           (-6.0, 5.0, 25.0, 33.0), (40.0, 46.0, 28.0, 42.0)):
        body = body.union(_box(x0, x1, y0, y1, PLATE_TOP - 0.5, BRIDGE_Z + 0.5))
    body = body.union(_box(-8.0, 56.0, -18.0, 44.0, BRIDGE_Z, top))
    # Clamp columns for the backside stack (this belt's level) and the pass-through stack.
    body = _columns(body, Q[0], Q[1], z_pulley)
    body = _columns(body, S[0], S[1], z_pass)
    # Motor: pilot and pulley through the plate, a pulley clearance in the bridge, M3 screws.
    body = body.cut(_cyl_z(P[0], P[1], NEMA_PILOT + 2.0, MOTOR_FACE_Z - 1.0, PLATE_TOP + 1.0))
    body = body.cut(_cyl_z(P[0], P[1], PULLEY_FLANGE + 4.0, BRIDGE_Z - 1.0, top + 1.0))
    for dx in (-NEMA_BOLT / 2, NEMA_BOLT / 2):
        for dy in (-NEMA_BOLT / 2, NEMA_BOLT / 2):
            x, y = P[0] + dx, P[1] + dy
            body = body.cut(_cyl_z(x, y, 3.0 + 2 * 0.2, MOTOR_FACE_Z - 1.0, PLATE_TOP + 1.0))
            body = body.cut(_cyl_z(x, y, M3_CB, PLATE_TOP - 3.5, PLATE_TOP + 1.0))
            body = body.cut(_cyl_z(x, y, 7.0, BRIDGE_Z - 1.0, top + 1.0))
    # C and E screws: through the slab into T-nuts, counterbored, open to the top.
    for x, y in ((0.0, -STATION), (E_END + STATION, -half)):
        body = body.cut(_cyl_z(x, y, 5.0 + 2 * HOLE_CLEAR, -SLOT_LIP_T - 1.0, GRIP + 1.0))
        body = body.cut(_cyl_z(x, y, M5_HEAD + 1.0, GRIP, top + 1.0))
    # Element axles: clearance through the bridge and columns, pilot into the plate.
    tip = top - AXLE_L
    for x, y in (Q, S):
        body = body.cut(_cyl_z(x, y, 5.0 + 2 * HOLE_CLEAR, PLATE_TOP, top + 1.0))
        body = body.cut(_cyl_z(x, y, PILOT_D, tip - 0.5, PLATE_TOP + 0.5))
    if mirrored:
        body = body.mirror("YZ")
    return body


_dispatch = {"ab_drive": build_ab_drive}

result = _dispatch.get(target_part, build_ab_drive)()
