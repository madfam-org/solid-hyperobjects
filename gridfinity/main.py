"""
Gridfinity — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A faithful CORE re-authoring of the Gridfinity modular-storage standard in exact
B-Rep. Two parts share the canonical mating geometry so bins seat into baseplates:

  * "bin"       — a hollow storage bin: grid_x x grid_y cells of 42 mm pitch, the
                  standardized stacking-lip base profile under each cell, a body
                  up to grid_z x 7 mm, optional 6x2 mm corner magnet holes and an
                  optional front finger-scoop.
  * "baseplate" — a thin plate with a grid_x x grid_y array of sockets that are
                  the NEGATIVE of the bin base profile (same 42 mm pitch, matching
                  chamfer stack + a small print clearance), so bins snap in.

Canonical Gridfinity dimensions (modelled exactly):
  * Grid module        : 42.0 mm x 42.0 mm per unit
  * Vertical unit      : 7.0 mm
  * Cell corner radius : ~3.75 mm
  * Base / lip profile : bottom-up chamfer stack, per 42 mm footprint —
        0.8 mm chamfer (45 deg) -> 1.8 mm straight wall -> 2.15 mm chamfer (45 deg)
        total profile height ~= 4.75 mm.
    This shared profile is what makes bins seat into baseplates and stack.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  * `cq` (cadquery) and `math` are PRE-INJECTED globals — used directly.
  * Manifest parameters arrive as BARE globals (a param id `grid_x` -> `grid_x`).
  * Read them via the PARAM() guard below (globals()/eval/getattr are NOT in the
    sandbox's allowed builtins).
  * The final solid is assigned to a top-level name `result`.
"""


import cadquery as cq

# -- Sandbox-safe parameter access -------------------------------------------
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/NameError directly)."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# == Canonical Gridfinity constants ==========================================
GRID_XY     = 42.0    # grid module (mm) per unit in X and Y
GRID_Z      = 7.0     # vertical unit (mm)
GRID_CLEAR  = 0.5     # gap between adjacent 42 mm cells -> body cell = 41.5 mm
CELL_R      = 3.75    # cell corner radius (mm), Gridfinity standard
CELL        = GRID_XY - GRID_CLEAR                  # body cell footprint = 41.5 mm

# Standardized base (stacking-lip) profile, bottom-up.  Each 45-deg chamfer
# narrows the footprint by its own height on every side.
BASE_C1     = 0.8     # lower chamfer height (45 deg)
BASE_WALL   = 1.8     # middle straight vertical wall
BASE_C2     = 2.15    # upper chamfer height (45 deg)
BASE_H      = BASE_C1 + BASE_WALL + BASE_C2         # ~= 4.75 mm

SOCKET_CLEAR = 0.25   # baseplate socket clearance vs the bin base (per side)

MAG_DIA     = 6.0     # magnet diameter (mm)
MAG_DEPTH   = 2.0     # magnet pocket depth (mm)
MAG_INSET   = 8.0     # magnet centre inset from each cell corner (mm)


# == Parameters ==============================================================
grid_x         = int(  PARAM(lambda: grid_x,          2))   # units in X
grid_y         = int(  PARAM(lambda: grid_y,          1))   # units in Y
grid_z         = int(  PARAM(lambda: grid_z,          3))   # height units (x7 mm)
wall           = float(PARAM(lambda: wall,          1.2))   # bin side-wall thickness
floor_th       = float(PARAM(lambda: floor_th,      1.2))   # floor thickness above base
enable_magnets = bool( PARAM(lambda: enable_magnets, False))  # 6x2 corner magnet holes
finger_scoop   = bool( PARAM(lambda: finger_scoop,  False))   # front finger ramp
lip_enabled    = bool( PARAM(lambda: lip_enabled,    True))   # top stacking lip

bp_thickness   = float(PARAM(lambda: bp_thickness,  4.75))  # baseplate plate thickness

target_part    = str(  PARAM(lambda: target_part,  "bin"))  # "bin" | "baseplate"

# -- Clamps (keep geometry valid regardless of injected values) --------------
grid_x       = max(1, min(grid_x, 8))
grid_y       = max(1, min(grid_y, 8))
grid_z       = max(1, min(grid_z, 20))
wall         = max(0.6, min(wall, 3.0))
floor_th     = max(0.6, min(floor_th, 4.0))
bp_thickness = max(BASE_H + 0.5, min(bp_thickness, 10.0))


# == Geometry helpers ========================================================
def rr_wire(size, r, z):
    """A single closed rounded-rectangle wire (square `size`, corner radius `r`)
    centred on the origin at height z. Radius is clamped safe.  Returns a cq.Wire
    suitable for lofting."""
    size = max(0.4, size)
    r = max(0.05, min(r, size / 2.0 - 0.05))
    sk = cq.Sketch().rect(size, size).vertices().fillet(r)
    face = sk._faces.Faces()[0]
    return face.outerWire().translate((0, 0, z))


def base_profile_solid(z0, shrink=0.0):
    """The standardized Gridfinity base profile for ONE cell, base at z0.

    A loft through four rounded-rectangle sections (bottom-up):
        z0                : narrowest       (after both chamfers)
        z0+C1             : end lower chamfer
        z0+C1+WALL        : end straight wall (still narrow)
        z0+C1+WALL+C2     : full cell width  (top of profile)
    `shrink` uniformly reduces every section's width; pass a NEGATIVE value to
    grow the profile (used to enlarge the baseplate socket by a clearance).

    45-deg chamfers narrow the footprint by their height on each side:
        top width Wt = CELL - shrink ; mid Wm = Wt - 2*C2 ; bottom Wb = Wm - 2*C1
    Corner radii track the width so every fillet keeps a constant offset."""
    wt = CELL - shrink
    wm = wt - 2.0 * BASE_C2
    wb = wm - 2.0 * BASE_C1

    r_top = CELL_R
    r_mid = max(0.2, CELL_R - BASE_C2)
    r_bot = max(0.2, CELL_R - BASE_C2 - BASE_C1)

    wires = [
        rr_wire(wb, r_bot, z0),
        rr_wire(wm, r_mid, z0 + BASE_C1),
        rr_wire(wm, r_mid, z0 + BASE_C1 + BASE_WALL),
        rr_wire(wt, r_top, z0 + BASE_C1 + BASE_WALL + BASE_C2),
    ]
    # Wrap the lofted Solid in a Workplane so callers get a uniform boolean API.
    return cq.Workplane("XY").add(cq.Solid.makeLoft(wires))


def cell_centers():
    """Centre XY of every grid cell in the grid_x x grid_y footprint."""
    cx0 = -(grid_x - 1) * GRID_XY / 2.0
    cy0 = -(grid_y - 1) * GRID_XY / 2.0
    pts = []
    for ix in range(grid_x):
        for iy in range(grid_y):
            pts.append((cx0 + ix * GRID_XY, cy0 + iy * GRID_XY))
    return pts


def footprint_prism(z0, height, inset=0.0):
    """A rounded-rect prism spanning the WHOLE grid footprint, base at z0.
    `inset` shrinks each side (used for the hollow cavity and wall offset)."""
    xsz = grid_x * GRID_XY - GRID_CLEAR - 2.0 * inset
    ysz = grid_y * GRID_XY - GRID_CLEAR - 2.0 * inset
    xsz = max(0.5, xsz)
    ysz = max(0.5, ysz)
    r = max(0.05, min(CELL_R - inset, min(xsz, ysz) / 2.0 - 0.05))
    wp = (
        cq.Workplane("XY", origin=(0, 0, z0))
        .box(xsz, ysz, height, centered=(True, True, False))
    )
    if r > 0.05:
        try:
            wp = wp.edges("|Z").fillet(r)
        except Exception:
            pass
    return wp


# == Bin ======================================================================
def build_bin():
    total_h = grid_z * GRID_Z

    # 1) Per-cell standardized base profile (the mating geometry) as one solid.
    solid = None
    for (cx, cy) in cell_centers():
        seg = base_profile_solid(0.0).translate((cx, cy, 0))
        solid = seg if solid is None else solid.union(seg)

    # 2) Body: full-footprint prism from the top of the base to total height.
    body_h = max(0.5, total_h - BASE_H)
    solid = solid.union(footprint_prism(BASE_H, body_h))

    # 3) Optional top stacking lip: a shallow copy of the base profile at the top
    #    rim so bins stack on one another (its outer face mirrors the base).
    if lip_enabled and total_h > BASE_H + 1.0:
        lip = None
        for (cx, cy) in cell_centers():
            seg = base_profile_solid(0.0).translate((cx, cy, total_h - BASE_H))
            lip = seg if lip is None else lip.union(seg)
        solid = solid.union(lip)

    # 4) Hollow the interior: subtract an inset prism, leaving `wall` sides and
    #    `floor_th` above the solid base block, open at the top.
    inner_floor = BASE_H + floor_th
    cut_h = total_h - inner_floor + 1.0
    if cut_h > 0.2:
        cavity = footprint_prism(inner_floor, cut_h, inset=wall)
        solid = solid.cut(cavity)

    # 5) Optional finger-scoop ramp along the front (-Y) interior wall.
    if finger_scoop:
        solid = _add_finger_scoop(solid, inner_floor, total_h)

    # 6) Optional magnet holes: 6x2 mm blind pockets at each cell's four corners.
    if enable_magnets:
        solid = _cut_magnets(solid)

    return solid


def _add_finger_scoop(solid, inner_floor, total_h):
    xsz = grid_x * GRID_XY - GRID_CLEAR - 2.0 * wall
    scoop_r = min(12.0, (total_h - inner_floor) * 0.9, (grid_y * GRID_XY) * 0.35)
    if scoop_r < 2.0:
        return solid
    y_inner_front = -(grid_y * GRID_XY - GRID_CLEAR) / 2.0 + wall
    cyl = (
        cq.Workplane("YZ", origin=(0, y_inner_front + scoop_r, inner_floor + scoop_r))
        .circle(scoop_r)
        .extrude(xsz / 2.0, both=True)
    )
    try:
        solid = solid.cut(cyl)
    except Exception:
        pass
    return solid


def _cut_magnets(solid):
    holes = None
    off = CELL / 2.0 - MAG_INSET
    for (cx, cy) in cell_centers():
        for sx in (-1, 1):
            for sy in (-1, 1):
                h = (
                    cq.Workplane("XY", origin=(cx + sx * off, cy + sy * off, 0))
                    .circle(MAG_DIA / 2.0)
                    .extrude(MAG_DEPTH)
                )
                holes = h if holes is None else holes.union(h)
    if holes is not None:
        try:
            solid = solid.cut(holes)
        except Exception:
            pass
    return solid


# == Baseplate ================================================================
def build_baseplate():
    """A thin plate whose per-cell sockets are the NEGATIVE of the bin base
    profile (grown by SOCKET_CLEAR so the bin seats without binding)."""
    plate_h = bp_thickness
    plate = footprint_prism(0.0, plate_h)

    # Socket = base profile grown by clearance, embedded so its top rim sits at
    # plate_h; the bin base (BASE_H tall) nests flush into it.
    sockets = None
    z_socket_base = plate_h - BASE_H
    for (cx, cy) in cell_centers():
        seg = base_profile_solid(z_socket_base, shrink=-2.0 * SOCKET_CLEAR).translate((cx, cy, 0))
        sockets = seg if sockets is None else sockets.union(seg)

    if sockets is not None:
        plate = plate.cut(sockets)

    return plate


# == Dispatch =================================================================
if target_part == "baseplate":
    result = build_baseplate()
else:
    result = build_bin()
