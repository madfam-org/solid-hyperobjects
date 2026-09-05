"""
Keycap — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A single keycap for a mechanical keyboard switch: a hollow tapered shell with a
dished top, a skirt sized to the 19.05 mm key pitch, and a switch stem fused to
the underside of the keytop. Optional debossed legend.

This is an independent MADFAM implementation of published mechanical
interfaces — the 19.05 mm keyboard key pitch, the Cherry MX cross stem, the
Alps rectangular stem and the Box Cherry square stem. See NOTICE.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `profile_id`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.

Geometry order matters and is deliberate:
  blank loft -> fillet/chamfer the clean blank -> cut the dish -> shell from
  below -> fuse stem + ribs -> cut the legend. Filleting after the dish cut
  puts the fillet on a spline edge and fails; cutting the legend before the
  shell would leave the deboss floating in the cavity.
"""

import cadquery as cq
import math


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/vars())."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
profile_id       = int(  PARAM(lambda: profile_id,        0))    # 0 DCS 1 DSA 2 SA 3 OEM 4 Cherry
row_id           = int(  PARAM(lambda: row_id,            1))    # keyboard row 1..4
key_size_id      = int(  PARAM(lambda: key_size_id,       0))    # 0 1u, 1 1.25u, 2 1.5u, 3 2u
stem_type_id     = int(  PARAM(lambda: stem_type_id,      0))    # 0 Cherry MX, 1 Alps, 2 Box
legend_enabled   = bool( PARAM(lambda: legend_enabled, False))
legend_text      = str(  PARAM(lambda: legend_text,     "A"))
font_size        = float(PARAM(lambda: font_size,       6.0))
dish_depth       = float(PARAM(lambda: dish_depth,      1.0))
wall_thickness   = float(PARAM(lambda: wall_thickness,  3.0))
keytop_thickness = float(PARAM(lambda: keytop_thickness, 1.0))
stem_slop        = float(PARAM(lambda: stem_slop,      0.35))
fn               = int(  PARAM(lambda: fn,                0))    # tessellation hint; B-Rep is exact

target_part      = str(  PARAM(lambda: target_part, "keycap"))


# ── The interface standard ───────────────────────────────────────────────────
# Keyboard grid. A cap is made smaller than its cell by an inter-cap gap so
# adjacent caps clear each other: 1u = 19.05 - 2*0.5 = 18.05 mm.
KEY_PITCH = 19.05          # mm per 1u
INTER_CAP_GAP = 0.5        # mm per side

# Cherry MX cross socket. Nominal arm length / arm width; the socket is widened
# by half the printer-fit allowance on each nominal dimension.
MX_STEM_OD = 5.5           # cylindrical post outer diameter
MX_CROSS_LEN = 4.1
MX_CROSS_WIDE = 1.17

# Alps rectangular stem. NOTE the opposite sign convention: Alps *narrows* its
# socket by the full slop where Cherry widens by half. Both are as measured on
# real switches; the asymmetry is intentional, not a typo.
ALPS_OUTER_X = 4.5
ALPS_OUTER_Y = 3.2
ALPS_SOCKET_X = 3.2
ALPS_SOCKET_Y = 1.2

# Box Cherry: a square outer post carrying the same MX cross.
BOX_SIDE = 6.0
BOX_WALL = 1.5

# The gap between the top of the stem socket and the underside of the keytop.
SOCKET_HEADROOM = 0.5

# How far above the base the support ribs start, leaving the stem post's outer
# surface free where the switch housing meets it.
RIB_BASE_CLEAR = 3.5

KEY_UNITS = (1.0, 1.25, 1.5, 2.0)

# Profile families. `base` is the cap height at row 2 (where the row increment
# is zero); height = base + (row - 2) * ROW_STEP. `top_x`/`top_y` are the top
# face at 1u, `tilt` the top-plate tilt in degrees at row 2 (positive tilts the
# top toward the user), `dish` the dish cutter shape.
ROW_STEP = 0.5             # mm of height per row away from row 2
ROW_TILT_STEP = 2.0        # degrees of tilt per row away from row 2

PROFILES = (
    # id 0 — DCS: sculpted, cylindrical dish, medium taper
    {"base": 9.5,  "top_x": 12.4, "top_y": 14.3, "tilt": -3.0, "dish": "cyl"},
    # id 1 — DSA: uniform (flat, no row tilt), spherical dish
    {"base": 8.0,  "top_x": 13.0, "top_y": 13.0, "tilt":  0.0, "dish": "sph"},
    # id 2 — SA: tall, spherical dish, tilts away from the user
    {"base": 16.0, "top_x": 13.2, "top_y": 13.2, "tilt":  3.0, "dish": "sph"},
    # id 3 — OEM: sculpted, cylindrical dish, taller than DCS
    {"base": 11.9, "top_x": 12.6, "top_y": 14.0, "tilt": -4.0, "dish": "cyl"},
    # id 4 — Cherry: sculpted, low, cylindrical dish
    {"base": 9.4,  "top_x": 12.4, "top_y": 14.1, "tilt": -3.5, "dish": "cyl"},
)


def clampi(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


profile_id = clampi(profile_id, 0, len(PROFILES) - 1)
row_id = clampi(row_id, 1, 4)
key_size_id = clampi(key_size_id, 0, len(KEY_UNITS) - 1)
stem_type_id = clampi(stem_type_id, 0, 2)

PROFILE = PROFILES[profile_id]
UNITS = KEY_UNITS[key_size_id]

# ── Derived envelope ─────────────────────────────────────────────────────────
# The interface: X footprint = units * pitch - 2 * gap; Y footprint is always 1u.
bottom_x = UNITS * KEY_PITCH - 2.0 * INTER_CAP_GAP
bottom_y = KEY_PITCH - 2.0 * INTER_CAP_GAP

cap_height = PROFILE["base"] + (row_id - 2) * ROW_STEP

# The top face scales in X with the key size (a 2u cap has a 2u-wide top) and
# keeps the 1u proportion in Y.
top_x = PROFILE["top_x"] + (UNITS - 1.0) * KEY_PITCH
top_y = PROFILE["top_y"]

# Row shifts the tilt; DSA is uniform and stays flat at every row.
tilt_deg = 0.0 if PROFILE["tilt"] == 0.0 else PROFILE["tilt"] + (row_id - 2) * ROW_TILT_STEP

# Corner rounding of the silhouette. Kept modest so the 1u footprint measures
# 18.05 mm across the flats — the interface dimension.
BOTTOM_CORNER_R = 1.0
TOP_CORNER_R = 1.6

# Straight vertical wall at the base, so the measured footprint is the nominal
# one rather than a section through the taper.
BASE_BAND = 1.2

# How far inboard of the top face's rim the dish surface ends, so the dish cut
# never runs tangent to the filleted top edge.
DISH_RIM_INSET = 0.8

# Clamp the shell so a thick wall on a small cap cannot close the cavity out of
# existence (wall_thickness goes to 5 mm, half of a 1u cap's 18.05 mm).
max_wall = min(bottom_x, bottom_y) / 2.0 - 1.2
wall = max(0.8, min(wall_thickness, max_wall))
keytop = max(0.4, min(keytop_thickness, cap_height * 0.5))

OVERSHOOT = 20.0           # cutters run past the solid so no coincident faces


# ── Helpers ──────────────────────────────────────────────────────────────────
def blank_solid():
    """The tapered cap blank: a short prismatic base band, then a loft up to the
    top face, trimmed to height by a (possibly tilted) half-space.

    The base band matters: it is the interface. A cap that starts tapering (or
    chamfering) from z=0 measures narrower than its nominal footprint, and the
    footprint is exactly what must clear the neighbouring cap on the 19.05 mm
    grid. BASE_BAND mm of straight wall guarantees the measured silhouette is
    the nominal one.

    The trim plane is the sole author of the final height. It is placed, the
    result measured, and the plane re-placed by the shortfall — on the flat
    profiles as well as the tilted ones, because the top-edge fillet eats a
    tenth of a millimetre either way and the height rule is an acceptance
    criterion at +/-0.05 mm, not a consequence of a fillet radius.
    """
    rise = math.tan(math.radians(abs(tilt_deg))) * top_y
    band = min(BASE_BAND, cap_height * 0.15)
    r_top = min(0.6, keytop * 0.5, wall * 0.3)
    sign = 1.0 if tilt_deg > 0 else -1.0

    def blank():
        base = (
            cq.Workplane("XY")
            .placeSketch(cq.Sketch().rect(bottom_x, bottom_y).vertices().fillet(BOTTOM_CORNER_R))
            .extrude(band)
        )
        taper = (
            cq.Workplane("XY")
            .placeSketch(
                cq.Sketch()
                .rect(bottom_x, bottom_y)
                .vertices()
                .fillet(BOTTOM_CORNER_R)
                .moved(cq.Location(cq.Vector(0.0, 0.0, band))),
                cq.Sketch()
                .rect(top_x, top_y)
                .vertices()
                .fillet(TOP_CORNER_R)
                .moved(cq.Location(cq.Vector(0.0, 0.0, cap_height + rise))),
            )
            .loft()
        )
        wp = base.union(taper)
        # Soften the top perimeter HERE, on the untrimmed blank, where the edge
        # is a clean ruled loop. After the trim (or after the dish) the fillet
        # would land on a trimmed spline and OCCT fails it.
        if r_top > 0.05:
            try:
                wp = wp.edges(">Z").fillet(r_top)
            except Exception:
                pass
        return wp

    def trim(wp, z):
        cutter = cq.Workplane("XY").box(
            bottom_x + 4 * OVERSHOOT,
            bottom_y + 4 * OVERSHOOT,
            OVERSHOOT,
            centered=(True, True, False),
        )
        if rise > 0.005:
            cutter = cutter.rotate((0, 0, 0), (1, 0, 0), sign * abs(tilt_deg))
        return wp.cut(cutter.translate((0, 0, z)))

    z_plane = cap_height - (rise / 2.0 if rise > 0.005 else 0.0)
    wp = trim(blank(), z_plane)
    err = cap_height - wp.val().BoundingBox().zmax
    if abs(err) > 0.002:
        wp = trim(blank(), z_plane + err)
    return wp


def soften(wp):
    """Rounding pass on the clean blank, BEFORE the dish and the legend.

    The top perimeter is filleted inside blank_solid(), while the edge is still
    an untrimmed ruled loop; filleting a face a spherical dish has already
    carved puts the fillet on a spline edge and OCCT fails it. Nothing is
    rounded here on the base: the base silhouette IS the interface, and
    chamfering it would measure the cap narrower than the 19.05 mm grid allows.
    """
    return wp


def top_plane_z():
    """Mean height of the tilted top face.

    The tilt cut lowers the sunk edge by the full rise and leaves the raised
    edge at cap_height, so the FACE's mean height is cap_height - rise/2 — not
    cap_height, and not cap_height + rise/2. Getting this wrong puts the dish
    and legend cutters above the solid, where they remove nothing and every
    parameter that drives them reads as inert.
    """
    rise = math.tan(math.radians(abs(tilt_deg))) * top_y
    return cap_height - (rise / 2.0 if rise > 0.005 else 0.0)


def tilt_cutter(shape):
    """Rotate a cutter into the tilted top face's own frame."""
    if abs(tilt_deg) < 0.01:
        return shape
    sign = 1.0 if tilt_deg > 0 else -1.0
    return shape.rotate((0, 0, 0), (1, 0, 0), sign * abs(tilt_deg))


def cut_dish(wp):
    """One boolean cut for the top dish: a sphere for spherical-dish profiles,
    a cylinder laid across X for cylindrical-dish profiles.

    Only the depth is exposed; the radius follows from depth and the chord the
    top face spans, so the curvature stays gentle at shallow depths.
    """
    if dish_depth <= 0.001:
        return wp

    depth = min(dish_depth, max(0.05, keytop * 0.8 + cap_height * 0.15))
    z_top = top_plane_z()

    if PROFILE["dish"] == "sph":
        # Sphere through the rim of the top face: r = (c^2/4 + d^2) / (2d) with
        # c the chord across the top face diagonal.
        # Span the top face's inscribed circle, not its diagonal. A cutter sized
        # to the diagonal meets the top face exactly at the filleted rim and the
        # tangency there produces a sliver face: the export comes back
        # non-watertight and split in two. DISH_RIM_INSET keeps the dish's edge
        # inboard of the rounding.
        chord = max(2.0, min(top_x, top_y) - 2.0 * DISH_RIM_INSET)
        r = (chord * chord / 4.0 + depth * depth) / (2.0 * depth)
        # Rotate the sphere a quarter turn about X before placing it. A CadQuery
        # sphere is a surface of revolution with a POLE on its own axis; left
        # upright, that pole lands exactly on the dish axis and the mesher emits
        # a degenerate two-vertex triangle there. The B-Rep stays valid (one
        # solid, no sliver faces) but the exported STL comes back with a stray
        # zero-area face and reads as not watertight — which is how this was
        # found, and why the check is on the MESH and not only the solid.
        # Turning the poles onto the Y axis puts them outside the cut region and
        # the dish surface is then a pole-free patch. The dish is a sphere either
        # way: rotating a sphere changes only its parameterisation.
        cutter = tilt_cutter(
            cq.Workplane("XY")
            .sphere(r)
            .rotate((0, 0, 0), (1, 0, 0), 90.0)
            .translate((0.0, 0.0, -depth + r))
        ).translate((0.0, 0.0, z_top))
    else:
        # Cylinder across X: the dish runs the length of the key, curved in Y.
        chord = max(2.0, top_y - 2.0 * DISH_RIM_INSET)
        r = (chord * chord / 4.0 + depth * depth) / (2.0 * depth)
        cutter = tilt_cutter(
            cq.Workplane("YZ")
            .circle(r)
            .extrude(top_x / 2.0 + OVERSHOOT, both=True)
            .translate((0.0, 0.0, -depth + r))
        ).translate((0.0, 0.0, z_top))
    return wp.cut(cutter)


def shell_cavity():
    """The interior cavity, cut upward from the base.

    A second loft inset by `wall` from the outer silhouette, stopping
    `keytop` below the top so the keytop keeps its thickness. It overshoots
    downward past z=0 so the base opening has no coincident face.
    """
    in_bx = max(1.0, bottom_x - 2.0 * wall)
    in_by = max(1.0, bottom_y - 2.0 * wall)
    in_tx = max(0.8, top_x - 2.0 * wall)
    in_ty = max(0.8, top_y - 2.0 * wall)

    ceil_z = max(0.6, cap_height - keytop)

    # Extend the inner loft below z=0 by extruding the bottom section down.
    inner = (
        cq.Workplane("XY")
        .placeSketch(
            cq.Sketch().rect(in_bx, in_by).vertices().fillet(max(0.2, BOTTOM_CORNER_R * 0.5)),
            cq.Sketch()
            .rect(in_tx, in_ty)
            .vertices()
            .fillet(max(0.2, TOP_CORNER_R * 0.5))
            .moved(cq.Location(cq.Vector(0.0, 0.0, ceil_z))),
        )
        .loft()
    )
    skirt = (
        cq.Workplane("XY")
        .box(in_bx, in_by, OVERSHOOT, centered=(True, True, False))
        .translate((0.0, 0.0, -OVERSHOOT))
    )
    return inner.union(skirt)


def mx_cross_cutter(height):
    """The Cherry MX cross socket: two crossed slots, each nominal arm length by
    nominal arm width, widened by half the printer-fit allowance."""
    half = stem_slop / 2.0
    ln = MX_CROSS_LEN + half
    wd = MX_CROSS_WIDE + half
    a = cq.Workplane("XY").box(ln, wd, height, centered=(True, True, False))
    b = cq.Workplane("XY").box(wd, ln, height, centered=(True, True, False))
    return a.union(b)


def build_stem(ceil_z):
    """The switch stem, standing from z=0 up to the underside of the keytop.

    Returns (post, socket_cutter). The post is fused to the keytop's underside
    by construction: it runs the full height from the base to `ceil_z`, and the
    socket stops SOCKET_HEADROOM short of it so a solid cap of material closes
    the socket under the keytop.
    """
    post_h = max(1.0, ceil_z)
    # The socket stops SOCKET_HEADROOM below the top of the post, leaving a
    # solid plug of material under the keytop. On a thick-walled cap the cavity
    # ceiling tapers in over the post, and a socket that ran too close to the
    # top left only a thin ring there — which the ceiling then pinched off as a
    # loose fragment. Scale the headroom with the keytop so the plug is always
    # substantial.
    socket_h = max(0.5, post_h - max(SOCKET_HEADROOM, keytop * 0.5))

    if stem_type_id == 1:
        # Alps: rectangular post, rectangular socket NARROWED by the full slop.
        post = cq.Workplane("XY").box(
            ALPS_OUTER_X, ALPS_OUTER_Y, post_h, centered=(True, True, False)
        )
        sx = max(0.4, ALPS_SOCKET_X - stem_slop)
        sy = max(0.3, ALPS_SOCKET_Y - stem_slop)
        socket = cq.Workplane("XY").box(sx, sy, socket_h, centered=(True, True, False))
    elif stem_type_id == 2:
        # Box Cherry: square outer post, hollowed to a fixed wall, MX cross inside.
        post = cq.Workplane("XY").box(BOX_SIDE, BOX_SIDE, post_h, centered=(True, True, False))
        hollow = max(0.5, BOX_SIDE - 2.0 * BOX_WALL)
        socket = cq.Workplane("XY").box(hollow, hollow, socket_h, centered=(True, True, False))
        socket = socket.union(mx_cross_cutter(socket_h))
    else:
        # Cherry MX: cylindrical post with the cross socket.
        post = cq.Workplane("XY").circle(MX_STEM_OD / 2.0).extrude(post_h)
        socket = mx_cross_cutter(socket_h)

    return post, socket


def stem_ribs(ceil_z):
    """Support ribs joining the stem to the shell's inner wall.

    THE FIX for the baseline's printability defect. Without them the
    cylindrical stem stands free inside the shell and the exported mesh is two
    disjoint solids; a free-floating stem cannot be printed as one part.

    The ribs start at RIB_BASE_CLEAR above the base, not at z=0. That matters:
    the switch stem enters from below and its housing needs the post's
    cylindrical outer surface clear for the first few millimetres, and the
    5.5 mm outer diameter is an interface dimension that must stay measurable
    on a free surface. Ribs that ran to the base would merge post and shell
    into one blob and there would be no stem diameter left to verify.

    They are thin webs on the two axes, spanning the cavity, trimmed by the
    shell. They touch no interface surface.
    """
    rib_t = 1.2
    z0 = min(RIB_BASE_CLEAR, max(0.5, ceil_z * 0.4))
    rib_h = max(0.8, ceil_z - z0)
    a = cq.Workplane("XY").box(bottom_x, rib_t, rib_h, centered=(True, True, False))
    b = cq.Workplane("XY").box(rib_t, bottom_y, rib_h, centered=(True, True, False))
    return a.union(b).translate((0.0, 0.0, z0))


def cut_legend(wp):
    """Deboss the legend into the top face.

    A CUT, never an emboss — a raised legend on a keycap top would be
    unprintable without supports and would not wear well. `cq.text` depends on
    the host's font stack; if it is unavailable the cap ships with a plain top
    rather than failing the render.
    """
    if not legend_enabled:
        return wp
    txt = legend_text.strip()
    if not txt:
        return wp

    depth = min(0.6, max(0.2, keytop * 0.4))
    z_top = top_plane_z()
    # The glyph prism must START above the highest point of the top face and run
    # down PAST the deepest point of the dish, or a shallow prism sitting at the
    # nominal top height floats clear of a dished, tilted face and cuts nothing.
    head = dish_depth + 1.0
    run = head + depth + dish_depth

    try:
        glyph = (
            cq.Workplane("XY")
            .workplane(offset=head)
            .text(txt, font_size, -run, combine=False)
        )
        # Bring the glyph into the tilted top face's frame, then onto the face.
        glyph = tilt_cutter(glyph).translate((0.0, 0.0, z_top))
        cut = wp.cut(glyph)
        # A font that renders nothing (missing glyph) leaves the solid untouched;
        # that is a silent no-op, so only accept a cut that removed material.
        if cut.val().Volume() < wp.val().Volume() - 1e-6:
            return cut
        return wp
    except Exception:
        return wp


def largest_solid(wp):
    """Keep only the largest solid, and say so by construction.

    A boolean between a tapering cavity and a stem can leave a crumb: at
    corner-allmax (2u, 5 mm walls, Box stem) the post's wall above the socket
    was pinched off by the cavity ceiling as a 1.8 mm^3 fragment, and the export
    came back as two bodies. The fragment is not geometry anyone asked for — it
    is boolean debris — so it is dropped rather than shipped.

    This is a guard, not the fix: the socket depth below is what stops the
    fragment forming in the first place. The guard is here because ONE BODY is
    an acceptance criterion, and a criterion that depends on no boolean ever
    leaving debris across the whole parameter space is not one I can assert.
    """
    solids = wp.val().Solids()
    if len(solids) <= 1:
        return wp
    biggest = max(solids, key=lambda s: s.Volume())
    return cq.Workplane("XY").newObject([biggest])


def build_keycap():
    body = blank_solid()
    body = soften(body)
    body = cut_dish(body)

    ceil_z = max(0.6, cap_height - keytop)

    # Hollow the shell.
    cavity = shell_cavity()
    body = body.cut(cavity)

    # Fuse the stem and its ribs, then trim everything back inside the shell so
    # no rib or post can breach the outer surface or the keytop.
    post, socket = build_stem(ceil_z)
    interior = cavity.intersect(
        cq.Workplane("XY").box(
            bottom_x + 2 * OVERSHOOT,
            bottom_y + 2 * OVERSHOOT,
            OVERSHOOT,
            centered=(True, True, False),
        )
    )
    fill = post.union(stem_ribs(ceil_z)).intersect(interior)
    body = body.union(fill)

    # The socket is cut last of the stem work so the ribs cannot fill it.
    body = body.cut(socket)

    body = cut_legend(body)
    return largest_solid(body)


# ── Dispatch ─────────────────────────────────────────────────────────────────
result = build_keycap()
