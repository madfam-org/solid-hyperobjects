"""
XY Joint — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A printed XY joint for a CoreXY gantry whose two belts run stacked on two levels (a
Voron 2.4-class "flying gantry"). It rides an MGN9H block on the gantry's Y rail, carries the
end of the X beam (a 2020 extrusion hung under it) and turns both belts through 90°: one on a
GT2 20-tooth toothed idler, the other on a stack of two F695 flanged bearings. It is an
ORIGINAL design built to functional facts cited by page from the Voron 2.4r2 build guide
(GPL-3.0; pp. 97–100: an F695 stack and a GT2 20T idler, each on an M5x40 SHCS screwed into
plastic; p. 125: the belts stacked, the crossing omitted) and from datasheets. No Voron
geometry is copied, traced or derived.

The body is one piece:
  - a plate on the MGN9H block (four M3 screws, HIWIN B 15 × C 16);
  - an inboard block whose underside sits on the X beam's top face, keyed into its slot and
    held by two M5 screws into T-nuts;
  - a bridge above both belt levels, on four pillars placed off every belt line, from which
    the two M5x40 axles hang into pilots in the block;
  - columns that clamp each stack between the floor and the bridge at its belt level.

Belt geometry (all cited, see docs/README.md):
  - the toothed idler's centre sits one GT2 20T pitch radius (12.73 / 2) behind the belt
    line, the F695 stack's one running radius plus the belt's back-side offset
    (13 / 2 + 0.506) in front of it: the belt's back runs on the stack, its teeth on the idler;
  - the low belt mid-plane is 12 above the block top (22 above the C extrusion), the high one
    21 (31); mirrored, the stack and the idler swap levels, because the other hand's joint
    turns the other belt on each (the CoreXY loop's convex and reflex corners).

Model frame: origin at the centre of the MGN9H block's top face (the joint's mounting face);
+x to the gantry's right, +y to the back, +z up. The default is the LEFT joint: the inboard
side is +x. `mirrored` builds the RIGHT joint by reflecting x and swapping the belt levels.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `idler_width`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr.
  - Assign the final solid to a top-level name `result`.
"""

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
# HIWIN MG series, MGN9H: W 20, L 39.9, B 15 (across), C 16 (along), M3; H 10 (the C
# extrusion's top to this face).
BLOCK_W = 20.0
HOLE_B = 15.0
HOLE_C = 16.0
# GT2 20T pitch diameter 12.73 (SDP/SI Table 33); F695 OD 13 (NSK F695ZZ); GT2 2 mm belt:
# B 1.52, T 0.76 (Pfeifer 2MR/PGGT2), U 0.254 (SDP/SI Table 4) -> back-side offset 0.506.
IDLER_R = 12.7324 / 2.0
STACK_R = 13.0 / 2.0 + (1.52 - 0.76 - 0.254)
# The F695 + shim stack: shim 1 + F695 4 + F695 4 + shim 1 (DIN 988 1 mm; NSK B 4).
STACK_H = 10.0
# ISO 4762 M5x40 SHCS (Keller & Kalmbach 240912540): l 40; ISO 7380-1 M5 head dk 9.5.
AXLE_L = 40.0
M5_HEAD = 9.5
# MISUMI HFS5: 6 mm slot opening, 2 mm lips; Ø4.2 the hole MISUMI taps M5 (pilot).
SLOT_LIP_T = 2.0
PILOT_D = 4.2
# MISUMI HNTAP5-5 T-nut: 15 long (the two beam nuts must not overlap).
TNUT_L = 15.0

# ── Conventions (labelled; not sourced facts) ────────────────────────────────
LOW, HIGH = 12.0, 21.0      # belt mid-planes above this face (22 / 31 above the C top)
FLOOR_T = 6.0               # plate/floor thickness above the block top
BLOCK_DROP = 10.0           # inboard block reaches down to the C extrusion's top plane
BRIDGE_Z = 26.0             # bridge underside: the high stack's top (21 + 5)
BRIDGE_T = 5.0              # bridge thickness: heads seat at z 31
X_STACK, X_IDLER = 32.0, 36.0   # inboard distance of the two axles from the rail centre
BEAM_END = 12.5             # X beam end, inboard of the rail centre
BEAM_A, BEAM_B = 22.5, 44.0     # beam screws: station 10 from its end; second 21.5 further
COL_R = 4.0                 # Ø8 clamp columns (bear on the shim's / idler's inner face)
HOLE_CLEAR = 0.25           # per side: Ø5.5 for M5, Ø3.4 for M3 (house clearances)
M3_CB = 6.5                 # M3 socket-head counterbore Ø, 3.5 deep
TAB_W = 5.8                 # tongue width in the 6 mm slot (as corner-idler-bracket)
INNER = 60.0                # inboard end of the body

# ── Parameters ───────────────────────────────────────────────────────────────
idler_width = float(PARAM(lambda: idler_width, 9.0))    # toothed idler, flange to flange
mirrored = bool(PARAM(lambda: mirrored, False))          # the right-hand joint
target_part = str(PARAM(lambda: target_part, "xy_joint"))

idler_width = max(6.0, min(idler_width, 10.0))
z_stack = HIGH if mirrored else LOW
z_idler = LOW if mirrored else HIGH
Y_STACK = -STACK_R          # front side of the belt line (y = 0)
Y_IDLER = IDLER_R           # back side


def _box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def _cyl_z(x, y, d, z0, z1):
    solid = cq.Solid.makeCylinder(d / 2.0, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))
    return cq.Workplane("XY").add(solid)


def _columns(body, x, y, z_mid, height):
    """Clamp columns under and over a part of `height` centred on z_mid."""
    lo, hi = z_mid - height / 2.0, z_mid + height / 2.0
    if lo > FLOOR_T:
        body = body.union(_cyl_z(x, y, 2 * COL_R, FLOOR_T - 0.5, lo))
    if hi < BRIDGE_Z:
        body = body.union(_cyl_z(x, y, 2 * COL_R, hi, BRIDGE_Z + 0.5))
    return body


def build_xy_joint():
    top = BRIDGE_Z + BRIDGE_T
    # Plate on the block, and the inboard block down to the C's top plane (under it, the beam).
    body = _box(-BLOCK_W / 2.0, BLOCK_W / 2.0 + 1.0, -20.0, 20.0, 0.0, FLOOR_T)
    body = body.union(_box(BLOCK_W / 2.0 + 0.5, INNER, -20.0, 20.0, -BLOCK_DROP, FLOOR_T))
    # Tongue in the beam's top slot, along the beam.
    body = body.union(_box(BEAM_END + 1.5, BEAM_B + 8.0, -TAB_W / 2.0, TAB_W / 2.0,
                           -BLOCK_DROP - SLOT_LIP_T, -BLOCK_DROP + 0.5))
    # Pillars, off every belt line: over the block (outboard of the outer run at x ≈ 10)
    # and at the inboard end (clear of the belt line y 0).
    for y0, y1 in ((12.0, 18.0), (-18.0, -12.0)):
        body = body.union(_box(-8.0, 6.0, y0, y1, FLOOR_T - 0.5, BRIDGE_Z + 0.5))
    for y0, y1 in ((5.0, 17.0), (-17.0, -5.0)):
        body = body.union(_box(INNER - 10.0, INNER - 2.0, y0, y1, FLOOR_T - 0.5, BRIDGE_Z + 0.5))
    # Bridge above both belt levels.
    body = body.union(_box(-8.0, INNER - 2.0, -18.0, 18.0, BRIDGE_Z, top))
    # Clamp columns at each belt level.
    body = _columns(body, X_STACK, Y_STACK, z_stack, STACK_H)
    body = _columns(body, X_IDLER, Y_IDLER, z_idler, idler_width)
    # MGN9H screws: clearance through the plate, counterbored, with key access in the bridge.
    for sx in (-HOLE_B / 2.0, HOLE_B / 2.0):
        for sy in (-HOLE_C / 2.0, HOLE_C / 2.0):
            body = body.cut(_cyl_z(sx, sy, 3.0 + 2 * 0.2, -1.0, FLOOR_T + 1.0))
            body = body.cut(_cyl_z(sx, sy, M3_CB, FLOOR_T - 3.5, FLOOR_T + 1.0))
            body = body.cut(_cyl_z(sx, sy, 7.0, BRIDGE_Z - 1.0, top + 1.0))
    # Beam screws: Ø5.5 through block and tongue, counterbored from the floor; access holes.
    for x in (BEAM_A, BEAM_B):
        body = body.cut(_cyl_z(x, 0.0, 5.0 + 2 * HOLE_CLEAR, -BLOCK_DROP - 3.0, FLOOR_T + 1.0))
        body = body.cut(_cyl_z(x, 0.0, M5_HEAD + 1.0, -BLOCK_DROP + 4.5, FLOOR_T + 1.0))
        body = body.cut(_cyl_z(x, 0.0, M5_HEAD + 1.0, BRIDGE_Z - 1.0, top + 1.0))
    # Axles: clearance through the bridge and columns, pilot in the block for the tip.
    tip = top - AXLE_L
    for x, y in ((X_STACK, Y_STACK), (X_IDLER, Y_IDLER)):
        body = body.cut(_cyl_z(x, y, 5.0 + 2 * HOLE_CLEAR, FLOOR_T, top + 1.0))
        body = body.cut(_cyl_z(x, y, PILOT_D, tip - 0.5, FLOOR_T + 0.5))
    if mirrored:
        body = body.mirror("YZ")
    return body


_dispatch = {"xy_joint": build_xy_joint}

result = _dispatch.get(target_part, build_xy_joint)()
