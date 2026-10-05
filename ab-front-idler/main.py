"""
A/B Front Idler — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A printed front idler for a CoreXY gantry whose two belts run stacked on two levels (a
Voron 2.4-class flying gantry): it sits flush on the front end of a gantry Y extrusion (a
2020 "C" extrusion carrying the MGN9 rail) and turns one belt through 180° on a stack of two
F695 flanged bearings (shim, F695, F695, shim) on an M5x40 SHCS. It is an ORIGINAL design
built to functional facts cited by page from the Voron 2.4r2 build guide (GPL-3.0; pp. 65
and 69: the A and B idlers' F695 stacks on M5x40 SHCS; pp. 91–93: the idlers flush with the
front ends of the C extrusions, on M5 screws into T-nuts; p. 88: the rail starts 25 mm from
that end) and from datasheets. No Voron geometry is copied, traced or derived.

The body is one piece: a floor on the C extrusion's top face and a block down its inner side
face, each fixed by an M5 screw into a T-nut at the extrusion's slot station (10 from its end)
and keyed into the slot; walls outboard and inboard of the belt; a roof the axle hangs from;
a front wall. The pocket is open to the back, where both runs of the belt leave.

Belt geometry (cited, see docs/README.md): the belt's teeth run on the stack, so its centre
sits one running radius plus the belt's teeth-side offset (13 / 2 + 1.014) from each run;
the two runs are those the XY joint and the A/B drive make (17.480 = 32 − 7.006 − 7.514
inboard of the rail centre). The default is the LEFT (B) idler on the low belt level, 22
above the C extrusion; `mirrored` builds the RIGHT (A) idler on the high level, 31.

Model frame: origin on the C extrusion's top face, on its centreline, at its front end face;
+x to the gantry's right, +y to the back (along the extrusion), +z up.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `stack_y`).
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
# F695 OD 13, flange 15 (NSK F695ZZ); stack = 1 mm DIN 988 shim + 2 × 4 mm F695 + shim.
F695_OD = 13.0
FLANGE_D = 15.0
STACK_H = 10.0
# GT2 2 mm belt (Pfeifer 2MR/PGGT2: B 1.52, T 0.76; SDP/SI Table 4: U 0.254).
TEETH_OFF = 0.76 + 0.254
BACK_OFF = 1.52 - 0.76 - 0.254
# ISO 4762 M5x40 SHCS: l 40. ISO 7380-1 M5 button head: dk 9.5.
AXLE_L = 40.0
M5_HEAD = 9.5
# MISUMI HFS5-2020: 20 square, 6 mm slot opening, 2 mm lips, slot centre 10 below the top
# face on the side face; Ø4.2 the hole MISUMI taps M5 (the axle's pilot).
PROFILE = 20.0
SLOT_LIP_T = 2.0
PILOT_D = 4.2
# Guide p. 88: the MGN9 rail starts 25 mm from the C extrusion's end.
RAIL_SETBACK = 25.0

# ── Conventions (labelled; not sourced facts) ────────────────────────────────
LOW, HIGH = 22.0, 31.0          # belt mid-planes above the C top (as xy-joint)
X_STACK = 32.0 - (F695_OD / 2.0 + BACK_OFF) - (F695_OD / 2.0 + TEETH_OFF)  # 17.480
STATION = 10.0                  # the C extrusion's slot station (extrusion-2020 default)
GRIP = 10.5                     # M5x16 head seat above the clamped face: 5.5 passes into the nut
ROOF_T = 5.0
WALL_CLEAR = 1.5                # walls clear the belt's back / teeth by at least this
HOLE_CLEAR = 0.25
TAB_W = 5.8
INBOARD = 32.0                  # inboard extent of the body from the rail centre

# ── Parameters ───────────────────────────────────────────────────────────────
stack_y = float(PARAM(lambda: stack_y, 16.0))     # stack axle from the extrusion's front end
mirrored = bool(PARAM(lambda: mirrored, False))   # the right (A) idler, high level
target_part = str(PARAM(lambda: target_part, "front_idler"))

stack_y = max(16.0, min(stack_y, 18.0))
z_belt = HIGH if mirrored else LOW
z_floor = z_belt - STACK_H / 2.0
z_roof = z_belt + STACK_H / 2.0
top = z_roof + ROOF_T
r_teeth = F695_OD / 2.0 + TEETH_OFF
x_outer = X_STACK - r_teeth            # the run toward the drive (9.966)
x_inner = X_STACK + r_teeth            # the run toward the XY joint (24.994)
x_wall_out = x_outer - BACK_OFF - WALL_CLEAR
x_wall_in = x_inner + TEETH_OFF + WALL_CLEAR
y_front_wall = stack_y - r_teeth - BACK_OFF - WALL_CLEAR
depth = RAIL_SETBACK - 1.0            # stops 1 mm short of the rail (guide p. 88)


def _box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def _cyl(p, d, axis, length):
    solid = cq.Solid.makeCylinder(d / 2.0, length, cq.Vector(*p), cq.Vector(*axis))
    return cq.Workplane("XY").add(solid)


def build_front_idler():
    half = PROFILE / 2.0
    # Floor on the C's top face, out over its inner side; the block down that side face.
    body = _box(-half, INBOARD, 0.0, depth, 0.0, z_floor)
    body = body.union(_box(half, INBOARD, 0.0, depth, -PROFILE, 0.5))
    # Walls outboard and inboard of the two runs, the front wall, and the roof.
    body = body.union(_box(-half, x_wall_out, 0.0, depth, z_floor - 0.5, z_roof + 0.5))
    body = body.union(_box(x_wall_in, INBOARD, 0.0, depth, z_floor - 0.5, z_roof + 0.5))
    body = body.union(_box(x_wall_out - 0.5, x_wall_in + 0.5, 0.0, y_front_wall,
                           z_floor - 0.5, z_roof + 0.5))
    body = body.union(_box(-half, INBOARD, 0.0, depth, z_roof, top))
    # Tongues in the top slot and in the inner side slot, along the extrusion.
    body = body.union(_box(-2.9, 2.9, 1.0, depth - 1.0, -SLOT_LIP_T, 0.5))
    body = body.union(_box(half - SLOT_LIP_T, half + 0.5, 1.0, depth - 1.0,
                           -half - 2.9, -half + 2.9))
    # Top screw: through the floor into the top-slot T-nut; counterbore and access from above.
    body = body.cut(_cyl((0.0, STATION, -SLOT_LIP_T - 1.0), 5.0 + 2 * HOLE_CLEAR, (0, 0, 1),
                         GRIP + SLOT_LIP_T + 2.0))
    body = body.cut(_cyl((0.0, STATION, GRIP), M5_HEAD + 1.0, (0, 0, 1), top - GRIP + 1.0))
    # Side screw: through the block into the side-slot T-nut; counterbore from the inboard face.
    body = body.cut(_cyl((half - SLOT_LIP_T - 1.0, STATION, -half), 5.0 + 2 * HOLE_CLEAR,
                         (1, 0, 0), GRIP + SLOT_LIP_T + 2.0))
    body = body.cut(_cyl((half + GRIP, STATION, -half), M5_HEAD + 1.0, (1, 0, 0),
                         INBOARD - half - GRIP + 1.0))
    # Axle: clearance through the roof, pilot below the floor for the tip.
    tip = top - AXLE_L
    body = body.cut(_cyl((X_STACK, stack_y, z_floor), 5.0 + 2 * HOLE_CLEAR, (0, 0, 1),
                         top - z_floor + 1.0))
    body = body.cut(_cyl((X_STACK, stack_y, tip - 0.5), PILOT_D, (0, 0, 1),
                         z_floor - tip + 1.0))
    if mirrored:
        body = body.mirror("YZ")
    return body


_dispatch = {"front_idler": build_front_idler}

result = _dispatch.get(target_part, build_front_idler)()
