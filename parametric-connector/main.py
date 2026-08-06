"""
Parametric Pipe/Tube Connector — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A disaster-relief / scavenged-material structural connector. It joins cylindrical
commodities — PVC pipe, bamboo, wooden dowels — at a defined topology. The user
measures the OUTER diameter of whatever material is locally available and enters
it (`pipe_od`); the connector NODE is generated to fit. Each arm is a cylindrical
SOCKET (bore = pipe_od + clearance, seated `insertion_depth` deep) on a stub that
radiates from a central hub. Optional pin/screw through-holes fix each pipe; a
heavy-load option thickens the walls and adds internal gusset ribs for shelter
frames and geodesic domes.

Modes (dispatch on `target_part`, one solid each):
  - "elbow"       2-way bend, `elbow_angle` variable (90° default; open it up for
                  geodesic / dome struts).
  - "tee"         3-way flat T (two collinear arms + one perpendicular).
  - "corner_3way" 3-way orthogonal 3D corner (X+, Y+, Z+) for box / cube frames.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `pipe_od`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

import math

import cadquery as cq


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/NameError directly)."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
pipe_od         = float(PARAM(lambda: pipe_od,         21.3))  # MEASURED pipe/dowel OD (mm)
wall            = float(PARAM(lambda: wall,             3.0))  # socket wall thickness (mm)
insertion_depth = float(PARAM(lambda: insertion_depth, 20.0))  # how deep the pipe seats (mm)
clearance       = float(PARAM(lambda: clearance,        0.5))  # bore slip fit vs pipe_od (mm)
elbow_angle     = float(PARAM(lambda: elbow_angle,     90.0))  # angle between the two elbow arms (deg)
heavy_load      = bool( PARAM(lambda: heavy_load,     False))  # thicker wall + internal gusset ribs
pin_holes       = bool( PARAM(lambda: pin_holes,      False))  # cross through-holes for a fixing pin/screw
pin_dia         = float(PARAM(lambda: pin_dia,          4.0))  # pin / screw shank diameter (mm)

target_part     = str(  PARAM(lambda: target_part,  "elbow"))  # elbow | tee | corner_3way

# ── Derived + safe clamps ────────────────────────────────────────────────────
pipe_od    = max(6.0, pipe_od)
clearance  = max(0.1, min(clearance, 2.0))
# Heavy-load frames want a stiffer socket: bump the effective wall.
wall_eff   = wall * (1.35 if heavy_load else 1.0)
wall_eff   = max(2.0, wall_eff)

bore_d     = pipe_od + clearance            # socket inner diameter (slip fit)
bore_r     = bore_d / 2.0
socket_od  = pipe_od + 2.0 * wall_eff       # socket outer diameter
socket_r   = socket_od / 2.0
# Arm length = seat depth + a closed back so the tube bottoms out on solid material.
back       = max(2.0, wall_eff)
arm_len    = max(6.0, insertion_depth) + back

# Hub: a solid core the arms grow out of. Radius a touch larger than the socket
# so every arm root fully overlaps the hub (a clean, gap-free boolean union).
hub_r      = socket_r + max(1.5, wall_eff * 0.5)

pin_dia    = max(1.5, min(pin_dia, bore_d - 1.0))
elbow_angle = max(20.0, min(elbow_angle, 160.0))


# ── Helpers ──────────────────────────────────────────────────────────────────
def _hub():
    """Solid hub the arms grow out of: a chamfered cube centered at the origin,
    sized to circumscribe every arm root. A polyhedral hub is deliberate — a
    sphere's curved surface intersecting orthogonal socket cylinders leaves
    razor-thin tessellation slivers at the exact-tangency seams (non-watertight
    STL), whereas planar hub faces union and cut cleanly. The 45° edge chamfers
    round the corners for print/handling and add material where arms splay."""
    side = hub_r * 2.0
    cham = hub_r * 0.35
    hub = cq.Workplane("XY").box(side, side, side)
    try:
        hub = hub.edges().chamfer(cham)
    except Exception:
        pass  # chamfer can fail on tight geometry — a plain cube is still valid
    return hub


def _socket_arm():
    """One socket arm as a Z-up solid rooted at the origin:
    a stub cylinder (socket_od) growing from inside the hub out to arm_len, bored
    from the open (far) end to seat the pipe insertion_depth deep, with a solid
    back plug. Optional internal gusset ribs (heavy_load) and a cross pin hole.
    The root is sunk to z = -hub_r so it fully overlaps the hub for a solid union.
    Returns (arm_solid, bore_cut) — the bore is returned separately so the caller
    cuts ALL bores AFTER unioning every arm, keeping each socket a clean opening."""
    z0 = -hub_r                      # bury the root deep inside the hub
    top = arm_len                    # open mouth height (z)
    body = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, (z0 + top) / 2.0))
        .cylinder(top - z0, socket_r)
    )

    # Internal gusset ribs: three thin fins inside the wall annulus that stiffen a
    # loaded joint without blocking the bore (they sit between bore_r and socket_r).
    if heavy_load:
        rib_h = min(insertion_depth * 0.6, arm_len - back - 1.0)
        rib_h = max(3.0, rib_h)
        rib_t = max(1.2, wall_eff * 0.5)
        rib_r = (bore_r + socket_r) / 2.0
        for k in range(3):
            ang = math.radians(120.0 * k)
            fin = (
                cq.Workplane("XY")
                .transformed(offset=cq.Vector(0, 0, back + rib_h / 2.0))
                .transformed(rotate=cq.Vector(0, 0, math.degrees(ang)))
                .box(socket_od, rib_t, rib_h, centered=(True, True, True))
                .translate((rib_r * math.cos(ang), rib_r * math.sin(ang), 0))
            )
            body = body.union(fin)

    # Socket bore: cut from the OPEN end down, leaving a `back`-thick solid plug so
    # the pipe bottoms out. Cut a hair past the mouth so the opening is clean.
    bore = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, back + (arm_len - back + 1.0) / 2.0))
        .cylinder(arm_len - back + 1.0, bore_r)
    )

    # Cross through-hole for a fixing pin/screw, near the mouth so it clamps the
    # seated pipe. Piercing both walls; cut with the bore (after union).
    if pin_holes:
        pin_z = arm_len - min(insertion_depth * 0.5, arm_len - back - 1.0)
        pin_z = max(back + pin_dia, pin_z)
        pin = (
            cq.Workplane("XZ")
            .transformed(offset=cq.Vector(0, pin_z, 0))
            .cylinder(socket_od + 2.0, pin_dia / 2.0)
        )
        bore = bore.union(pin)

    return body, bore


def _place(solid, rx=0.0, ry=0.0, rz=0.0):
    """Rotate a Z-up solid about the origin so its axis points along a new
    direction (Euler-ish: apply Z, then Y, then X rotations about the origin)."""
    out = solid
    if rz:
        out = out.rotate((0, 0, 0), (0, 0, 1), rz)
    if ry:
        out = out.rotate((0, 0, 0), (0, 1, 0), ry)
    if rx:
        out = out.rotate((0, 0, 0), (1, 0, 0), rx)
    return out


def _assemble(placements):
    """Union the hub with every placed arm body, THEN cut every placed bore.
    Cutting bores last guarantees a through-hole/socket never gets back-filled by
    a later arm's solid body."""
    body = _hub()
    bores = []
    for (rx, ry, rz) in placements:
        arm, bore = _socket_arm()
        body = body.union(_place(arm, rx, ry, rz))
        bores.append(_place(bore, rx, ry, rz))
    for b in bores:
        body = body.cut(b)
    return body


# ── Part builders ────────────────────────────────────────────────────────────
def build_elbow():
    """2-way bend. Arm A points +Z; arm B is swung `elbow_angle` away from it in
    the X–Z plane. At 90° it is a right-angle elbow; open the angle for the
    shallow bends of a geodesic dome or a splayed leg."""
    a = 180.0 - elbow_angle   # rotate arm B about Y so the angle between arms == elbow_angle
    return _assemble([
        (0.0, 0.0, 0.0),      # +Z
        (0.0, a,   0.0),      # swung into the X–Z plane
    ])


def build_tee():
    """3-way flat T: two collinear arms (+Z and -Z) plus one perpendicular arm
    (+X). The classic in-line branch fitting."""
    return _assemble([
        (0.0,   0.0, 0.0),    # +Z
        (180.0, 0.0, 0.0),    # -Z
        (0.0,   90.0, 0.0),   # +X
    ])


def build_corner_3way():
    """3-way orthogonal 3D corner: one arm on each of +X, +Y, +Z. The vertex of a
    cube / box frame or shelving structure."""
    return _assemble([
        (0.0,   0.0,  0.0),   # +Z
        (0.0,   90.0, 0.0),   # +X
        (-90.0, 0.0,  0.0),   # +Y
    ])


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "tee":
    result = build_tee()
elif target_part == "corner_3way":
    result = build_corner_3way()
else:
    result = build_elbow()
