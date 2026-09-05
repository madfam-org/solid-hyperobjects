"""
Gridfinity — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A faithful CORE re-authoring of the Gridfinity modular-storage standard in exact
B-Rep. Two parts share the canonical mating geometry so bins seat into baseplates:

  * "bin"       — a hollow storage bin: grid_x x grid_y cells of 42 mm pitch, the
                  standardized stacking-lip base profile under each cell, a body
                  up to grid_z x 7 mm, optional 6x2 mm magnet pockets on the
                  standard 26 mm square, and an optional front finger-scoop.
  * "baseplate" — a thin plate with a grid_x x grid_y array of sockets that are
                  the NEGATIVE of the bin base profile (same 42 mm pitch, matching
                  chamfer stack + a small print clearance), so bins snap in.

Canonical Gridfinity dimensions (modelled exactly):
  * Grid module        : 42.0 mm x 42.0 mm per unit
  * Vertical unit      : 7.0 mm
  * Cell corner radius : ~3.75 mm
  * Base / lip profile : bottom-up chamfer stack, per 42 mm footprint —
        0.8 mm chamfer (45 deg) -> 1.8 mm straight wall -> 2.15 mm chamfer (45 deg)
        total profile height = 4.75 mm.
  * Foot height        : 5.00 mm — the 4.75 mm chamfer stack plus a 0.25 mm
        straight riser at full cell width, which is where the body starts.
    This shared profile is what makes bins seat into baseplates and stack.

  The stacking lip is the SAME profile inverted at the rim: a recess swept
  around the whole bin footprint, widest at the rim and narrowing downward, so
  the per-cell feet of the bin above drop into it and self-centre. It is formed
  SUBTRACTIVELY, as part of the cavity cut, because building it additively would
  push the bin past grid_z * 7 mm and break the envelope.

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
BASE_H      = BASE_C1 + BASE_WALL + BASE_C2         # = 4.75 mm, the chamfer stack
BASE_RISER  = 0.25    # straight riser at full width above the chamfer stack
FOOT_H      = BASE_H + BASE_RISER                   # = 5.00 mm, the standard foot

# Baseplate socket clearance.  The standard's nominal is 0.25 mm DIAMETRAL, i.e.
# 0.125 mm per side: a foot topping out at 41.5 mm enters a 41.75 mm mouth.
SOCKET_CLEAR_SIDE = 0.125
SOCKET_CLEAR      = 2.0 * SOCKET_CLEAR_SIDE          # 0.25 mm nominal

# Stacking lip.  `bin` exposes the lip as a single boolean (`lip_enabled`), not
# as a style, so it always builds the standard's FULL recess — the whole 4.75 mm
# chamfer stack, the deepest and most positive of the styles.  LIP_HEADROOM is
# the top undersizing that lets the foot above drop in without binding; it is
# the same 0.8 mm the OpenSCAD `cup` mode defaults to, so a bin and a cup stack
# on one another.
LIP_H        = BASE_H
LIP_HEADROOM = 0.8

MAG_DIA     = 6.0     # magnet diameter (mm)
MAG_DEPTH   = 2.0     # magnet pocket depth (mm)
# Magnet centres sit on the standard's 26 mm square about each cell centre, i.e.
# +/-13.0 mm in X and Y — the same square the OpenSCAD modes and the cartridge's
# `magnet_socket_6x2` CDG interface declare, so a magnet drilled for one engine's
# part fits the other's.
MAG_PITCH   = 26.0    # magnet centres, square about the cell centre (mm)


# == Parameters ==============================================================
grid_x         = int(  PARAM(lambda: grid_x,          2))   # units in X
grid_y         = int(  PARAM(lambda: grid_y,          1))   # units in Y
grid_z         = int(  PARAM(lambda: grid_z,          3))   # height units (x7 mm)
wall           = float(PARAM(lambda: wall,          1.2))   # bin side-wall thickness
floor_th       = float(PARAM(lambda: floor_th,      1.2))   # floor thickness above base
enable_magnets = bool( PARAM(lambda: enable_magnets, False))  # 6x2 corner magnet holes
finger_scoop   = bool( PARAM(lambda: finger_scoop,  False))   # front finger ramp
lip_enabled    = bool( PARAM(lambda: lip_enabled,    True))   # top stacking lip

# The fallback matches the manifest's declared default (5.25), so a render with
# nothing injected builds the same plate the configurator's defaults describe.
bp_thickness   = float(PARAM(lambda: bp_thickness,  5.25))  # baseplate plate thickness

target_part    = str(  PARAM(lambda: target_part,  "bin"))  # "bin" | "baseplate"

# -- Clamps (keep geometry valid regardless of injected values) --------------
grid_x       = max(1, min(grid_x, 8))
grid_y       = max(1, min(grid_y, 8))
grid_z       = max(1, min(grid_z, 20))
wall         = max(0.6, min(wall, 3.0))
floor_th     = max(0.6, min(floor_th, 4.0))
# The plate must be at least as deep as the socket it hosts.  The socket is the
# 4.75 mm chamfer stack grown by the clearance; it opens at the plate's top face
# and its floor sits BASE_H below.  The manifest's declared minimum is 4.75 mm,
# so the clamp floor is exactly that — anything larger would silently refuse a
# value the manifest advertises as legal.
bp_thickness = max(BASE_H, min(bp_thickness, 10.0))


# == Geometry helpers ========================================================
def rr_wire(xsz, ysz, r, z):
    """A single closed rounded-rectangle wire (`xsz` by `ysz`, corner radius `r`)
    centred on the origin at height z. Sizes and radius are clamped safe.
    Returns a cq.Wire suitable for lofting."""
    xsz = max(0.4, xsz)
    ysz = max(0.4, ysz)
    r = max(0.05, min(r, min(xsz, ysz) / 2.0 - 0.05))
    sk = cq.Sketch().rect(xsz, ysz).vertices().fillet(r)
    face = sk._faces.Faces()[0]
    return face.outerWire().translate((0, 0, z))


def profile_prism(xsz, ysz, z0, shrink=0.0, with_riser=True):
    """The standardized Gridfinity chamfer stack swept around an xsz-by-ysz
    rounded rectangle, base at z0.

    A loft through four rounded-rectangle sections (bottom-up):
        z0                : narrowest       (after both chamfers)
        z0+C1             : end lower chamfer
        z0+C1+WALL        : end straight wall (still narrow)
        z0+C1+WALL+C2     : full width       (top of the chamfer stack, 4.75 mm)
    followed, when `with_riser`, by a straight prism at full width from 4.75 mm
    to FOOT_H = 5.00 mm.  That riser is what takes the foot to the standard's
    5.00 mm; without it the stack alone is 4.75 mm.

    `shrink` uniformly reduces every section on EACH SIDE; pass a NEGATIVE value
    to grow the profile (the baseplate socket is this same profile grown by the
    clearance, so the two can never drift apart).

    45-deg chamfers narrow the section by their height on each side:
        top Wt = size - 2*shrink ; mid Wm = Wt - 2*C2 ; bottom Wb = Wm - 2*C1
    Corner radii track the width so every fillet keeps a constant offset."""
    xt = xsz - 2.0 * shrink
    yt = ysz - 2.0 * shrink
    xm, ym = xt - 2.0 * BASE_C2, yt - 2.0 * BASE_C2
    xb, yb = xm - 2.0 * BASE_C1, ym - 2.0 * BASE_C1

    r_top = max(0.05, CELL_R - shrink)
    r_mid = max(0.05, r_top - BASE_C2)
    r_bot = max(0.05, r_mid - BASE_C1)

    wires = [
        rr_wire(xb, yb, r_bot, z0),
        rr_wire(xm, ym, r_mid, z0 + BASE_C1),
        rr_wire(xm, ym, r_mid, z0 + BASE_C1 + BASE_WALL),
        rr_wire(xt, yt, r_top, z0 + BASE_H),
    ]
    # Wrap the lofted Solid in a Workplane so callers get a uniform boolean API.
    solid = cq.Workplane("XY").add(cq.Solid.makeLoft(wires))
    if with_riser and BASE_RISER > 0:
        riser = (
            cq.Workplane("XY", origin=(0, 0, z0 + BASE_H))
            .add(cq.Solid.extrudeLinear(
                cq.Face.makeFromWires(rr_wire(xt, yt, r_top, z0 + BASE_H)),
                cq.Vector(0, 0, BASE_RISER)))
        )
        solid = solid.union(riser)
    return solid


def base_profile_solid(z0, shrink=0.0, with_riser=True):
    """One CELL's foot: the chamfer stack on a square CELL section, base at z0.
    The full 5.00 mm foot unless `with_riser` is cleared."""
    return profile_prism(CELL, CELL, z0, shrink=shrink, with_riser=with_riser)


def cell_centers():
    """Centre XY of every grid cell in the grid_x x grid_y footprint."""
    cx0 = -(grid_x - 1) * GRID_XY / 2.0
    cy0 = -(grid_y - 1) * GRID_XY / 2.0
    pts = []
    for ix in range(grid_x):
        for iy in range(grid_y):
            pts.append((cx0 + ix * GRID_XY, cy0 + iy * GRID_XY))
    return pts


def footprint_prism(z0, height, inset=0.0, clear=GRID_CLEAR):
    """A rounded-rect prism spanning the WHOLE grid footprint, base at z0.
    `inset` shrinks each side (used for the hollow cavity and wall offset).
    `clear` is the footprint rule: GRID_CLEAR (42*n - 0.5) for a bin, which
    leaves neighbouring bins room in a drawer, and 0 (42*n exactly) for a
    baseplate, whose plates butt against one another."""
    xsz = grid_x * GRID_XY - clear - 2.0 * inset
    ysz = grid_y * GRID_XY - clear - 2.0 * inset
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

    # 1) Per-cell standardized foot (the mating geometry) as one solid.
    #    FOOT_H tall: the 4.75 mm chamfer stack plus the 0.25 mm riser.
    solid = None
    for (cx, cy) in cell_centers():
        seg = base_profile_solid(0.0).translate((cx, cy, 0))
        solid = seg if solid is None else solid.union(seg)

    # 2) Body: full-footprint prism from the top of the feet to total height.
    body_h = max(0.5, total_h - FOOT_H)
    solid = solid.union(footprint_prism(FOOT_H, body_h))

    # 3) Hollow the interior, and with it cut the stacking lip.
    #
    #    The lip is NOT added on top — that would push the bin past
    #    grid_z * 7 mm. It is the top LIP_H of the interior shaped as the base
    #    profile INVERTED: widest at the rim, narrowing downward, the exact
    #    negative of a foot, so the feet of the bin above drop in and
    #    self-centre. Below the recess the cavity is a plain inset prism, and
    #    the two are unioned into ONE cutting tool so the void stays single.
    #
    #    The recess is inset from the bin's outer face by a full wall thickness
    #    (so the rim is a printable upstand) plus LIP_HEADROOM/2 per side (so
    #    the foot above drops in without binding).
    inner_floor = FOOT_H + floor_th
    cut_h = total_h - inner_floor
    lip = _lip_recess(total_h) if lip_enabled else None

    if cut_h > 0.2 or lip is not None:
        cavity = None
        if cut_h > 0.2:
            # When there is a lip the plain cavity stops at the recess floor and
            # overlaps it by 0.01 mm so the two boolean into one void; with no
            # lip it runs 1 mm proud of the rim, as before.
            if lip is not None:
                h = max(0.01, cut_h - LIP_H + 0.01)
            else:
                h = cut_h + 1.0
            cavity = footprint_prism(inner_floor, h, inset=wall)
        tool = cavity if lip is None else (
            lip if cavity is None else cavity.union(lip))
        if tool is not None:
            solid = solid.cut(tool)

    # 4) Optional finger-scoop ramp along the front (-Y) interior wall.
    if finger_scoop:
        solid = _add_finger_scoop(solid, inner_floor, total_h)

    # 5) Optional magnet pockets: 6x2 mm blind holes on each cell's 26 mm square.
    if enable_magnets:
        solid = _cut_magnets(solid)

    return solid


def _lip_recess(total_h):
    """The stacking-lip recess as a cutting tool, or None when it cannot fit.

    The base profile swept around the WHOLE bin footprint — the feet above are
    per-cell but they all land inside one perimeter recess — placed so its
    widest section lands exactly at the rim and clipped to the top LIP_H.
    Returns None (rim stays a plain wall) when the bin is too short to carry a
    recess above its floor, or too narrow for one to leave any material."""
    xsz = grid_x * GRID_XY - GRID_CLEAR
    ysz = grid_y * GRID_XY - GRID_CLEAR
    shrink = wall + LIP_HEADROOM / 2.0
    if total_h <= FOOT_H + floor_th + LIP_H + 0.5:
        return None
    if min(xsz, ysz) - 2.0 * shrink <= 2.0 * (BASE_C1 + BASE_C2) + 4.0:
        return None
    # Widest section at the rim: the stack's top face sits at total_h, so its
    # base sits BASE_H below. No riser — the riser is a foot feature.
    prof = profile_prism(xsz, ysz, total_h - BASE_H, shrink=shrink,
                         with_riser=False)
    # Keep only the top LIP_H of it; the styles differ by how much of the
    # profile the recess retains, measured down from the rim.
    clip = (
        cq.Workplane("XY", origin=(0, 0, total_h - LIP_H))
        .box(xsz + 2.0, ysz + 2.0, LIP_H + 0.02, centered=(True, True, False))
    )
    return prof.intersect(clip)


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
    off = MAG_PITCH / 2.0
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
    """A thin plate whose per-cell sockets are the NEGATIVE of the bin foot.

    The socket is the SAME `profile_prism` the foot is built from, grown by
    SOCKET_CLEAR_SIDE on every side — one function at two clearances, so the
    two can never drift apart.  A foot topping out at CELL = 41.5 mm therefore
    enters a mouth of 41.5 + 2*0.125 = 41.75 mm: 0.25 mm diametral clearance,
    the standard's nominal.

    The socket is cut with no riser and opens at the plate's top face, so it is
    BASE_H = 4.75 mm deep.  A foot is FOOT_H = 5.00 mm tall, and the extra
    0.25 mm is its full-width riser, which stands proud of the plate — exactly
    as the standard intends: the bin's body face lands 0.25 mm above the plate
    and the chamfer stack does the seating.

    The plate's own footprint is 42*n EXACTLY, not the bin's 42*n - 0.5: plates
    butt against one another with no gap, and a 41.75 mm socket mouth simply
    does not fit inside a 41.5 mm outline."""
    plate_h = bp_thickness
    plate = footprint_prism(0.0, plate_h, clear=0.0)

    sockets = None
    z_socket_base = plate_h - BASE_H
    for (cx, cy) in cell_centers():
        seg = base_profile_solid(z_socket_base, shrink=-SOCKET_CLEAR_SIDE,
                                 with_riser=False).translate((cx, cy, 0))
        sockets = seg if sockets is None else sockets.union(seg)

    if sockets is not None:
        plate = plate.cut(sockets)

    return plate


# == Dispatch =================================================================
if target_part == "baseplate":
    result = build_baseplate()
else:
    result = build_bin()
