"""
DIN Rail Clip — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A snap-on clip for standard top-hat DIN rail (the spine of industrial control
panels — it carries breakers, relays, PLCs and power supplies). The clip presents
a flat mount face with a device bolt pattern on top and grabs the two rolled lips
of the rail from behind with a pair of hooks.

Why a compliant mechanism (the design intent that matters):
  Printed PLA/PETG snap clips that rely on the *material* bending fail over time
  from creep and fatigue — a plastic tab held under permanent flexure slowly
  yields and loses grip. This clip instead grips through a COMPLIANT MECHANISM:
  one hook is rigid (a fixed reference face) and the opposite hook is carried on a
  cantilever SPRING BEAM. The beam is a slender, folded flexure that stores energy
  in bending only while you snap it over the lip; at rest it returns to shape, so
  the working load lives in the geometry, not in a permanently strained wall. Beam
  thickness (`spring_thickness`) is the stiffness lever: thinner = easier snap /
  softer grip, thicker = firmer hold.

CDG interfaces:
  • DIN TS35 Rail Profile (`rail`, DIN EN 60715) — the rail cross-section the hooks
    engage, selected by `rail_standard` (TS35 35×7.5, TS35-15 deep, TS15 mini).
  • Compliant Spring Hook (`snap`, internal) — the sprung cantilever hook whose
    stiffness is set by `spring_thickness`.
  • Device Bolt Pattern (`bolt_pattern`, M3/M4/M5) — the screw holes on the mount
    face that carry your device, set by `bolt_spacing` + `bolt_size`.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `mount_width`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
  - Assign the final solid to a top-level name `result`.
"""

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


# ── DIN rail standards (DIN EN 60715) ────────────────────────────────────────
# span  : outer width across the two lips (the catch-to-catch dimension, mm)
# depth : how far the top-hat stands off the panel (mm)
# lip   : how far each rolled lip turns back inward — the hook's grip depth (mm)
# thick : nominal rail sheet thickness (mm)
_RAILS = {
    "TS35":    {"span": 35.0, "depth": 7.5,  "lip": 5.0, "thick": 1.0},
    "TS35-15": {"span": 35.0, "depth": 15.0, "lip": 5.0, "thick": 1.5},
    "TS15":    {"span": 15.0, "depth": 5.5,  "lip": 4.0, "thick": 1.0},
}

# Gridfinity constants (for the gridfinity_clip crossover) — 42 mm module.
_GF_PITCH = 42.0
_GF_POCKET = 42.0     # top of the receiving pocket
_GF_POCKET_BOT = 37.2  # bottom of the receiving pocket (pitch - 4.8 chamfer sweep)
_GF_LIP_H = 4.4        # stacking-lip / pocket depth engaged


# ── Parameters ───────────────────────────────────────────────────────────────
rail_standard   = str(  PARAM(lambda: rail_standard, "TS35"))     # TS35 | TS35-15 | TS15
mount_width     = float(PARAM(lambda: mount_width,    40.0))      # plate width across rail (X, mm)
bolt_spacing    = float(PARAM(lambda: bolt_spacing,   20.0))      # centre-to-centre of screw holes (mm)
bolt_size       = int(  PARAM(lambda: bolt_size,         1))      # 0=M3, 1=M4, 2=M5
spring_thickness = float(PARAM(lambda: spring_thickness, 2.0))    # compliant beam thickness (stiffness, mm)
plate_thickness = float(PARAM(lambda: plate_thickness,  4.0))     # mount-plate thickness (Z, mm)

target_part = str(PARAM(lambda: target_part, "clip"))  # clip | gridfinity_clip | clip_wide

# ── Clamp to sane ranges so extreme UI values still build watertight ─────────
if rail_standard not in _RAILS:
    rail_standard = "TS35"
rail = _RAILS[rail_standard]
RAIL_SPAN = rail["span"]
RAIL_DEPTH = rail["depth"]
LIP_GRIP = rail["lip"]

BOLT_D = {0: 3.4, 1: 4.5, 2: 5.5}.get(bolt_size, 4.5)  # clearance holes M3/M4/M5

mount_width = max(RAIL_SPAN + 8.0, min(mount_width, 200.0))
bolt_spacing = max(6.0, min(bolt_spacing, mount_width - 8.0))
spring_thickness = max(1.0, min(spring_thickness, 6.0))
plate_thickness = max(2.5, min(plate_thickness, 10.0))

# ── Fixed geometry of the clip back (the part that hugs the rail) ─────────────
RAIL_AXIS = 24.0                 # length of the clip along the rail (Y, mm)
HOOK_LEN = RAIL_AXIS             # hooks run the full clip length
JAW_H = RAIL_DEPTH + 2.5         # how far the hook walls drop below the plate
HOOK_WALL = 2.6                  # thickness of the fixed hook wall
CATCH = min(LIP_GRIP - 1.0, 3.0) # how far each hook curls inward to catch a lip
CATCH = max(1.5, CATCH)
CLEAR = 0.35                     # snap-fit clearance so it seats without force at rest


# ── Helpers ──────────────────────────────────────────────────────────────────
def _extrude_profile_xz(pts, length):
    """Close a list of (x, z) points into a wire on the XZ plane and extrude it
    `length` centred on Y=0 — a watertight prism running along the rail.

    NOTE: the XZ workplane's extrude normal is −Y, so a one-sided `.extrude()`
    would push the prism entirely to negative Y (off the plate). `both=True` with
    half-length grows it symmetrically ±length/2 about Y=0, which is what the plate
    (also centred on Y) needs so the hooks fuse into it."""
    return (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .extrude(length / 2.0, both=True)
    )


def _mount_plate(width):
    """Flat mount plate centred on the origin, spanning `width` in X and
    RAIL_AXIS in Y, sitting just above the rail (base of plate at z=0)."""
    plate = (
        cq.Workplane("XY")
        .box(width, RAIL_AXIS, plate_thickness, centered=(True, True, False))
    )
    try:
        plate = plate.edges("|Z").fillet(min(3.0, width / 6.0))
    except Exception:
        pass
    return plate


def _fixed_hook():
    """Rigid hook on the +X side: a thick L-wall that drops below the plate and
    curls inward to sit behind one rail lip. This is the fixed reference jaw. The
    profile top reaches UP to `plate_thickness` so it overlaps the plate volume and
    fuses into a single connected solid (touching only at z=0 would leave two
    disjoint bodies)."""
    x_in = RAIL_SPAN / 2.0 - CLEAR         # inner wall face (against the rail lip edge)
    x_wall = RAIL_SPAN / 2.0 + HOOK_WALL   # outer surface of the hook wall
    x_catch = x_in - CATCH                 # curl tip (reaches back under the lip)
    # Profile (looking along -Y): overlap into the plate, down the outside, curl in
    # under the lip, step back to the rail slot face, up to the plate underside.
    pts = [
        (x_catch, plate_thickness),        # top inner, overlapping into the plate
        (x_wall,  plate_thickness),        # top outer, into the plate
        (x_wall, -JAW_H),                  # down the outside wall
        (x_catch, -JAW_H),                 # bottom, curled inward (the catch)
        (x_catch, -JAW_H + HOOK_WALL),     # catch top face
        (x_in,   -JAW_H + HOOK_WALL),      # step toward the rail
        (x_in,    0.0),                    # up the inside (rail slot face)
        (x_catch, 0.0),                    # back in at the plate underside
    ]
    return _extrude_profile_xz(pts, HOOK_LEN)


def _spring_hook():
    """COMPLIANT sprung hook on the -X side. Instead of a stiff wall, the hook is
    carried on a slender cantilever beam that folds down from the plate: it flexes
    outward (−X) as it rides over the lip, then springs back to grip. The bend
    energy lives in the beam geometry, so the wall is never held in permanent
    strain (no creep). `spring_thickness` sets the beam stiffness.

    Traced as an OUTER path (root → out over the lip → down the outside → curl in
    under the lip) plus an INNER return path offset inward by one thickness `t`.
    Keeping the vertical leg the outermost x on both edges makes the outline a
    simple, non-self-intersecting polygon, so the extruded beam stays watertight."""
    t = spring_thickness
    x_lip = -RAIL_SPAN / 2.0               # this rail lip's outer catch line
    x_out = x_lip - CLEAR                  # outer surface of the beam's vertical leg
    x_root_in = x_lip + 7.0                # beam root anchor (inboard, fuses to plate)
    x_catch = x_out + CATCH                # curl tip reaches back UNDER the lip

    outer = [
        (x_root_in, plate_thickness),      # root top — overlaps into the plate
        (x_out,     plate_thickness),      # reach out over the lip at plate top
        (x_out, -JAW_H),                   # down the OUTSIDE of the lip (outermost x)
        (x_catch, -JAW_H),                 # curl inward under the lip (the catch)
    ]
    inner = [
        (x_catch, -JAW_H + t),             # catch inner face
        (x_out + t, -JAW_H + t),           # inner corner of the vertical leg
        (x_out + t, plate_thickness - t - 3.0),  # up the inside, stop below plate top
        (x_root_in, plate_thickness - t - 3.0),  # back toward the root
    ]
    beam = _extrude_profile_xz(outer + inner, HOOK_LEN)

    # A relief slot at the root concentrates the bend into a living-hinge flexure
    # (so the fold flexes, not the whole plate corner).
    relief = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x_root_in, 0.0, plate_thickness - 1.0))
        .box(2.0, RAIL_AXIS + 2.0, 2.2, centered=(True, True, True))
    )
    try:
        beam = beam.cut(relief)
    except Exception:
        pass
    return beam


def _bolt_holes(part, spacing, rows_y=None):
    """Drill a symmetric pair (or grid) of clearance screw holes through the plate
    from the top face. `spacing` is centre-to-centre in X; `rows_y` optionally adds
    a second pair offset in Y (for wider multi-device plates)."""
    ys = rows_y if rows_y else [0.0]
    for y in ys:
        for x in (-spacing / 2.0, spacing / 2.0):
            hole = (
                cq.Workplane("XY")
                .transformed(offset=cq.Vector(x, y, -1.0))
                .cylinder(plate_thickness + 4.0, BOLT_D / 2.0, centered=True)
            )
            part = part.cut(hole)
    return part


# ── Part builders ─────────────────────────────────────────────────────────────
def build_clip():
    """Standalone DIN clip: flat mount face + a device bolt pair, one fixed hook
    and one compliant sprung hook."""
    body = _mount_plate(mount_width)
    body = body.union(_fixed_hook())
    body = body.union(_spring_hook())
    body = _bolt_holes(body, bolt_spacing)
    try:
        body = body.clean()
    except Exception:
        pass
    return body


def build_gridfinity_clip():
    """DIN clip whose top face is a Gridfinity-compatible receiving pocket (42 mm
    module): a Gridfinity bin drops into the clip, putting the whole Gridfinity
    ecosystem onto DIN rail. The clip keeps the same compliant grip below."""
    # One 42 mm cell footprint on top, tall enough to hold a pocket + the rail hooks.
    cell = _GF_PITCH
    top_h = plate_thickness + _GF_LIP_H
    base = (
        cq.Workplane("XY")
        .box(cell, cell, top_h, centered=(True, True, False))
    )
    try:
        base = base.edges("|Z").fillet(3.6)  # Gridfinity outer corner radius ~3.75
    except Exception:
        pass

    # Receiving pocket: a downward taper (42 top → 37.2 bottom) cut from the top
    # face, so a Gridfinity base foot seats and locates in it.
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=top_h)
        .rect(_GF_POCKET, _GF_POCKET)
        .workplane(offset=-_GF_LIP_H)
        .rect(_GF_POCKET_BOT, _GF_POCKET_BOT)
        .loft(combine=True)
    )
    body = base.cut(pocket)

    # Reuse the compliant grip on the underside. The gridfinity base is 42 mm wide,
    # which comfortably spans a 35 mm rail (and is clamped ≥ span+8 above).
    body = body.union(_fixed_hook())
    body = body.union(_spring_hook())
    try:
        body = body.clean()
    except Exception:
        pass
    return body


def build_clip_wide():
    """Wider multi-device clip strip: an elongated mount plate carrying several
    screw-hole pairs, with the hooks and the compliant spring running the full
    width so one clip can hang a row of small modules from a single rail."""
    wide = max(mount_width, RAIL_SPAN + 40.0)
    body = _mount_plate(wide)

    # Multiple bolt pairs across the strip (two rows in Y for real device patterns).
    n_pairs = max(2, int(wide // 35.0))
    step = wide / n_pairs
    for k in range(n_pairs):
        cx = -wide / 2.0 + step / 2.0 + k * step
        for y in (-RAIL_AXIS / 4.0, RAIL_AXIS / 4.0):
            for x in (cx - bolt_spacing / 2.0, cx + bolt_spacing / 2.0):
                # keep holes inside the plate
                if abs(x) > wide / 2.0 - 4.0:
                    continue
                hole = (
                    cq.Workplane("XY")
                    .transformed(offset=cq.Vector(x, y, -1.0))
                    .cylinder(plate_thickness + 4.0, BOLT_D / 2.0, centered=True)
                )
                body = body.cut(hole)

    # Hooks reference the rail span (35 mm), centred, regardless of plate width.
    body = body.union(_fixed_hook())
    body = body.union(_spring_hook())
    try:
        body = body.clean()
    except Exception:
        pass
    return body


# ── Dispatch ─────────────────────────────────────────────────────────────────
_dispatch = {
    "clip": build_clip,
    "gridfinity_clip": build_gridfinity_clip,
    "clip_wide": build_clip_wide,
}

result = _dispatch.get(target_part, build_clip)()
