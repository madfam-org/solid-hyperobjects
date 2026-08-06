"""
Microscope Slide Holder — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A parametric retention system for standard microscope slides. Re-authored in
CadQuery from the original OpenSCAD hyperobject. Three fabrication classes share
one Central Design Geometry (CDG): the standard slide pocket — a 25.4 x 76.2 mm
(1" x 3") slide, ~1 mm thick, per ISO 8037-1 / US "3x1" convention — plus a
per-side clearance so the printed slot accepts a real slide.

Modes (dispatched on `target_part`):
  - slide_box        : covered box holding N slides on edge in parallel slots,
                       with a matching snap-lip lid (slide_box_lid).
  - slide_tray       : flat tray with an array (cols x rows) of slide pockets,
                       each with a finger notch for removal.
  - staining_rack_cq : open frame that holds slides on edge for dipping in
                       reagent, with drainage crossbars instead of a solid floor.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` (cadquery) and `math` are pre-injected globals; imported here too so the
    module lints clean (ruff F821) and runs standalone.
  - Manifest parameters arrive as BARE globals (a param `wall` -> global `wall`).
    They are read through the PARAM(lambda: name, default) guard because the
    sandbox exposes neither globals() nor eval/getattr.
  - The final solid is assigned to the top-level name `result`.
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


# ── Standard slide table (length, width, thickness) in mm ────────────────────
# 0 = ISO 8037   76.0 x 26.0 x 1.0
# 1 = US "3x1"   76.2 x 25.4 x 1.0   <- the CDG default (1 in x 3 in)
# 2 = Petrographic 46.0 x 27.0 x 1.2
# 3 = Supa Mega  75.0 x 50.0 x 1.0
# 4 = Custom     -> custom_slide_* params
SLIDE_STANDARDS = [
    (76.0, 26.0, 1.0),
    (76.2, 25.4, 1.0),
    (46.0, 27.0, 1.2),
    (75.0, 50.0, 1.0),
]

# Density / pitch: rib (separator) width between adjacent slide slots (mm).
# 0 = archival (dense), 1 = working, 2 = staining, 3 = mailer (loose).
DENSITY_RIB_WIDTHS = [1.0, 1.5, 2.0, 3.0]


# ── Parameters ───────────────────────────────────────────────────────────────
slide_standard = int(PARAM(lambda: slide_standard, 1))          # 0..4
custom_slide_length = float(PARAM(lambda: custom_slide_length, 76.2))
custom_slide_width = float(PARAM(lambda: custom_slide_width, 25.4))
custom_slide_thickness = float(PARAM(lambda: custom_slide_thickness, 1.0))

num_slots = int(PARAM(lambda: num_slots, 20))                   # slide capacity
density = int(PARAM(lambda: density, 1))                        # 0..3 (box)

tolerance_xy = float(PARAM(lambda: tolerance_xy, 0.4))          # in-plane clearance
tolerance_z = float(PARAM(lambda: tolerance_z, 0.2))            # thickness clearance
wall = float(PARAM(lambda: wall, 2.0))                          # outer wall / floor

# tray layout
tray_columns = int(PARAM(lambda: tray_columns, 5))
tray_rows = int(PARAM(lambda: tray_rows, 2))
finger_notch = bool(PARAM(lambda: finger_notch, True))

# box lid
lid_snap = bool(PARAM(lambda: lid_snap, True))                 # snap lip on lid

# staining rack
handle = bool(PARAM(lambda: handle, True))
drainage_angle = float(PARAM(lambda: drainage_angle, 5.0))     # degrees
open_bottom = bool(PARAM(lambda: open_bottom, True))           # crossbars vs solid

target_part = str(PARAM(lambda: target_part, "slide_box"))


# ── Resolved slide geometry (the CDG) ────────────────────────────────────────
def resolve_slide():
    """Effective (length, width, thickness) for the active standard."""
    if 0 <= slide_standard < len(SLIDE_STANDARDS):
        return SLIDE_STANDARDS[slide_standard]
    length = max(1.0, custom_slide_length)
    width = max(1.0, custom_slide_width)
    thick = max(0.3, custom_slide_thickness)
    return (length, width, thick)


SLIDE_L, SLIDE_W, SLIDE_T = resolve_slide()

# The pocket / slot: real slide envelope + printable clearance.
SLOT_T = SLIDE_T + tolerance_z          # slot thickness (accepts the slide edge)
POCKET_L = SLIDE_L + tolerance_xy       # flat-pocket length
POCKET_W = SLIDE_W + tolerance_xy       # flat-pocket width

# Global capacity guard.
N = max(1, min(num_slots, 200))


# ── Helpers ──────────────────────────────────────────────────────────────────
def union_all(shapes):
    """Reduce a list of Workplanes/Solids into one union."""
    out = shapes[0]
    for s in shapes[1:]:
        out = out.union(s)
    return out


def box_array(points, sx, sy, sz, z_base):
    """One solid = a box (sx,sy,sz) placed at every (x,y) in `points`, base at
    z_base. Built with pushPoints/eachpoint so it is a SINGLE compound, making
    the later union/cut one boolean instead of N — a large speed win for combs
    and pocket grids."""
    zc = z_base + sz / 2.0
    return (
        cq.Workplane("XY")
        .pushPoints([(x, y) for (x, y) in points])
        .eachpoint(
            lambda loc: cq.Solid.makeBox(sx, sy, sz, cq.Vector(-sx / 2.0, -sy / 2.0, -sz / 2.0)).located(loc),
            useLocalCoordinates=False,
        )
        .translate((0, 0, zc))
    )


def cyl_array(points, radius, height, z_base):
    """One solid = a vertical cylinder placed at every (x,y) in `points`."""
    return (
        cq.Workplane("XY")
        .pushPoints([(x, y) for (x, y) in points])
        .eachpoint(
            lambda loc: cq.Solid.makeCylinder(radius, height, cq.Vector(0, 0, 0)).located(loc),
            useLocalCoordinates=False,
        )
        .translate((0, 0, z_base))
    )


def rib_width_for_density():
    if 0 <= density < len(DENSITY_RIB_WIDTHS):
        return DENSITY_RIB_WIDTHS[density]
    return DENSITY_RIB_WIDTHS[1]


# ─────────────────────────────────────────────────────────────────────────────
# MODE 1 — slide_box : N slides standing on edge in parallel slots + lid
# ─────────────────────────────────────────────────────────────────────────────
def _box_metrics():
    """Shared envelope math for base and lid so the lid always fits the base."""
    rib_w = rib_width_for_density()
    pitch = SLOT_T + rib_w                         # centre-to-centre slot spacing
    slot_depth = SLIDE_W * 0.6                     # how deep the slide sits in

    inner_x = N * pitch + rib_w                    # slot field width
    inner_y = SLIDE_L + tolerance_xy               # slot field length
    inner_z = slot_depth

    outer_x = inner_x + 2.0 * wall
    outer_y = inner_y + 2.0 * wall
    outer_z = inner_z + wall                       # + floor
    return {
        "rib_w": rib_w, "pitch": pitch, "slot_depth": slot_depth,
        "inner_x": inner_x, "inner_y": inner_y, "inner_z": inner_z,
        "outer_x": outer_x, "outer_y": outer_y, "outer_z": outer_z,
    }


def build_slide_box():
    """Solid box, hollowed, with a comb of slots cut into the interior so each
    slide stands on edge in its own slot. Slots run along Y (slide length)."""
    m = _box_metrics()
    outer_x, outer_y, outer_z = m["outer_x"], m["outer_y"], m["outer_z"]
    inner_x, inner_y = m["inner_x"], m["inner_y"]
    pitch, rib_w, slot_depth = m["pitch"], m["rib_w"], m["slot_depth"]

    body = cq.Workplane("XY").box(
        outer_x, outer_y, outer_z, centered=(True, True, False)
    )

    # Hollow interior (open top). Leave `wall` floor + `wall` sides.
    cavity = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, wall))
        .box(inner_x, inner_y, slot_depth + wall, centered=(True, True, False))
    )
    body = body.cut(cavity)

    # Slot comb: cut a thin channel per slide across the interior floor.
    # x positions are centres of each slot, symmetric about 0. Built as one
    # compound (box_array) so this is a single boolean cut.
    field_left = -inner_x / 2.0 + rib_w + SLOT_T / 2.0
    pts = [(field_left + i * pitch, 0.0) for i in range(N)]
    channels = box_array(pts, SLOT_T, inner_y + 2.0, slot_depth + 2.0,
                         wall - 1.0)
    body = body.cut(channels)

    # Label recess on the front outer wall (debossed flat).
    lbl_w = min(40.0, outer_x * 0.6)
    lbl_h = min(12.0, outer_z * 0.6)
    label = (
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(0, outer_z / 2.0, -outer_y / 2.0 - 0.001))
        .box(lbl_w, lbl_h, 0.8, centered=(True, True, False))
    )
    body = body.cut(label)

    # No top-rim fillet here: `>Z` would select every slot-channel top edge
    # (20+), and filleting them is slow and offers no functional benefit. The
    # comb slots stay crisp so slides drop in cleanly.
    return body


def build_slide_box_lid():
    """Tray-style lid that caps the box: a top plate + a downward skirt that
    slips over the box outer walls, with an optional inner snap lip."""
    m = _box_metrics()
    outer_x, outer_y = m["outer_x"], m["outer_y"]

    lid_clear = 0.3
    lid_wall = max(1.2, wall - 0.4)
    lid_h = 8.0

    # plate footprint = box outer + wall + clearance so the skirt clears it.
    skirt_out_x = outer_x + 2.0 * (lid_clear + lid_wall)
    skirt_out_y = outer_y + 2.0 * (lid_clear + lid_wall)

    plate = cq.Workplane("XY").box(
        skirt_out_x, skirt_out_y, wall, centered=(True, True, False)
    )

    skirt_outer = cq.Workplane("XY").box(
        skirt_out_x, skirt_out_y, lid_h, centered=(True, True, False)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .box(outer_x + 2.0 * lid_clear, outer_y + 2.0 * lid_clear, lid_h + 2.0,
             centered=(True, True, False))
    )
    skirt = skirt_outer.cut(skirt_inner).translate((0, 0, -lid_h))

    lid = plate.union(skirt)

    # Optional snap lip: a small inward ridge near the skirt bottom that clicks
    # under the box rim. Represented as a thin inward frame (robust + printable).
    if lid_snap:
        lip_out_x = outer_x + 2.0 * lid_clear
        lip_out_y = outer_y + 2.0 * lid_clear
        lip_frame_outer = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -lid_h + 1.0))
            .box(lip_out_x, lip_out_y, 1.2, centered=(True, True, False))
        )
        lip_frame_inner = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -lid_h + 1.0))
            .box(lip_out_x - 2.0, lip_out_y - 2.0, 3.2,
                 centered=(True, True, False))
        )
        lip = lip_frame_outer.cut(lip_frame_inner)
        lid = lid.union(lip)

    # Label recess on the lid top.
    lbl_w = min(50.0, skirt_out_x * 0.6)
    lbl_h = min(20.0, skirt_out_y * 0.3)
    label = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, wall - 0.4))
        .box(lbl_w, lbl_h, 0.6, centered=(True, True, False))
    )
    lid = lid.cut(label)
    return lid


# ─────────────────────────────────────────────────────────────────────────────
# MODE 2 — slide_tray : flat tray, cols x rows array of slide pockets
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_tray():
    """Flat tray with a grid of recessed slide-shaped pockets (slides lie flat).
    Each pocket has a finger notch cut through the floor for easy removal."""
    cols = max(1, min(tray_columns, 12))
    rows = max(1, min(tray_rows, 8))

    pocket_depth = SLIDE_T + tolerance_z + 1.0     # recess depth for a flat slide
    gap = wall                                     # wall between pockets

    cell_x = POCKET_W + gap
    cell_y = POCKET_L + gap
    body_x = cols * cell_x + gap
    body_y = rows * cell_y + gap
    body_z = pocket_depth + wall

    body = cq.Workplane("XY").box(
        body_x, body_y, body_z, centered=(True, True, False)
    )

    # Grid origin: bottom-left cell centre.
    x0 = -body_x / 2.0 + gap + POCKET_W / 2.0
    y0 = -body_y / 2.0 + gap + POCKET_L / 2.0

    finger_r = max(8.0, SLIDE_W * 0.35)

    centres = [(x0 + c * cell_x, y0 + r * cell_y)
               for c in range(cols) for r in range(rows)]

    pockets = box_array(centres, POCKET_W, POCKET_L, pocket_depth + 1.0, wall)
    body = body.cut(pockets)
    if finger_notch:
        notches = cyl_array(centres, finger_r, body_z + 2.0, -1.0)
        body = body.cut(notches)

    # Label recess on the front wall.
    lbl_w = min(40.0, body_x * 0.5)
    lbl_h = min(10.0, body_z * 0.6)
    label = (
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(0, body_z / 2.0, -body_y / 2.0 - 0.001))
        .box(lbl_w, lbl_h, 0.8, centered=(True, True, False))
    )
    body = body.cut(label)
    return body


# ─────────────────────────────────────────────────────────────────────────────
# MODE 3 — staining_rack_cq : slides on edge in an open frame for dipping
# ─────────────────────────────────────────────────────────────────────────────
def build_staining_rack():
    """Open, skeletonised frame that holds slides on edge for immersion in
    reagent. Two slotted rails (front + back) grip each slide; the bottom is
    open crossbars (fluid circulation) or a drainage-sloped solid floor."""
    rack_n = max(1, min(N, 60))
    min_rib = 2.0
    pitch = max(SLOT_T + min_rib, 5.0)             # >=5 mm pitch for staining

    slot_depth = SLIDE_W * 0.9                      # slides sit deep for dipping
    pillar = wall
    bar_w = 3.0
    bar_h = 2.5

    inner_x = rack_n * pitch + min_rib
    body_x = inner_x + 2.0 * pillar
    body_y = SLIDE_L + 2.0 * pillar + tolerance_xy
    rail_z = slot_depth + bar_h
    body_z = rail_z

    parts = []

    # Four corner pillars.
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = sx * (body_x / 2.0 - pillar / 2.0)
            py = sy * (body_y / 2.0 - pillar / 2.0)
            parts.append(
                cq.Workplane("XY")
                .transformed(offset=cq.Vector(px, py, 0))
                .box(pillar, pillar, body_z, centered=(True, True, False))
            )

    # Top perimeter rails (tie the pillars together at the top).
    top_z = body_z - bar_h
    parts.append(_bar(body_x, pillar, bar_h, 0, body_y / 2.0 - pillar / 2.0, top_z))
    parts.append(_bar(body_x, pillar, bar_h, 0, -(body_y / 2.0 - pillar / 2.0), top_z))
    parts.append(_bar(pillar, body_y, bar_h, body_x / 2.0 - pillar / 2.0, 0, top_z))
    parts.append(_bar(pillar, body_y, bar_h, -(body_x / 2.0 - pillar / 2.0), 0, top_z))

    # Bottom: open crossbars, or a solid drainage-sloped floor.
    if open_bottom:
        # perimeter bottom rails
        parts.append(_bar(body_x, pillar, bar_h, 0, body_y / 2.0 - pillar / 2.0, 0))
        parts.append(_bar(body_x, pillar, bar_h, 0, -(body_y / 2.0 - pillar / 2.0), 0))
        parts.append(_bar(pillar, body_y, bar_h, body_x / 2.0 - pillar / 2.0, 0, 0))
        parts.append(_bar(pillar, body_y, bar_h, -(body_x / 2.0 - pillar / 2.0), 0, 0))
        # two support crossbars at 1/3 and 2/3 span (Y)
        for frac in (-1.0 / 3.0, 1.0 / 3.0):
            parts.append(_bar(body_x, bar_w, bar_h, 0, frac * body_y / 2.0, 0))
    else:
        floor = _drainage_floor(body_x, body_y, wall, drainage_angle)
        parts.append(floor)

    # Slotted rib rails: comb of ribs on the front and back top rails so each
    # slide edge drops into its own slot. Each rail's ribs are one compound.
    field_left = -inner_x / 2.0 + min_rib + SLOT_T / 2.0
    for sign in (-1, 1):
        rail_y = sign * (body_y / 2.0 - pillar / 2.0)
        rib_pts = [
            (field_left + i * pitch - SLOT_T / 2.0 - min_rib / 2.0, rail_y)
            for i in range(rack_n + 1)
        ]
        parts.append(box_array(rib_pts, min_rib, pillar, slot_depth, bar_h))

    rack = union_all(parts)

    # Carrying handle: two uprights + a top crossbar spanning the frame.
    if handle:
        h_thick = 4.0
        h_rise = 15.0
        for sign in (-1, 1):
            hx = sign * (body_x / 2.0 - h_thick / 2.0)
            rack = rack.union(
                cq.Workplane("XY")
                .transformed(offset=cq.Vector(hx, 0, body_z))
                .box(h_thick, h_thick, h_rise, centered=(True, True, False))
            )
        rack = rack.union(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, body_z + h_rise - h_thick))
            .box(body_x, h_thick, h_thick, centered=(True, True, False))
        )

    return rack


def _bar(sx, sy, sz, cx, cy, cz):
    """Axis-aligned bar sized (sx,sy,sz), base at z=cz, centred in X/Y at (cx,cy)."""
    return (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(cx, cy, cz))
        .box(sx, sy, sz, centered=(True, True, False))
    )


def _drainage_floor(sx, sy, thick, angle_deg):
    """Solid floor whose top surface slopes by angle_deg along +Y for runoff."""
    drop = min(sy * 0.5, sy * abs(math.tan(math.radians(angle_deg))))
    # Wedge via a lofted / swept prism: build as a polygon extrusion on XZ,
    # then position. Simpler robust approach: box, then cut a sloped wedge.
    floor = cq.Workplane("XY").box(sx, sy, thick + drop, centered=(True, True, False))
    if drop > 0.05:
        # Cutting wedge: a big box rotated about X to shave the top into a ramp.
        cutter = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, thick))
            .transformed(rotate=cq.Vector(math.degrees(math.atan2(drop, sy)), 0, 0))
            .box(sx + 4.0, sy * 2.0, drop + thick + 5.0,
                 centered=(True, True, False))
        )
        floor = floor.cut(cutter)
    return floor


# ── Dispatch ─────────────────────────────────────────────────────────────────
_DISPATCH = {
    "slide_box": build_slide_box,
    "slide_box_lid": build_slide_box_lid,
    "slide_tray": build_slide_tray,
    "staining_rack_cq": build_staining_rack,
}

result = _DISPATCH.get(target_part, build_slide_box)()
