"""
Faircap Water Filter — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

An open-source, print-at-home water filter that screws onto a standard PET
bottle neck (PCO-1881) and houses a filter medium — activated charcoal, a
hollow-fiber membrane, or a ceramic disc. Screw the cap onto a bottle of raw
water, invert, and drink filtered water from the nozzle. Water sovereignty from
plastic waste: the bottle is the vessel, the printed thread is the connector.

The two Common-Denominator-Geometry (CDG) interfaces:
  1. INPUT  — a real PCO-1881 *female* helical thread that mates the bottle neck.
  2. MEDIUM — a cylindrical housing chamber with retaining ledges that seats the
              filter disc/element (shared bore between the cap and the housing).

Parts (dispatched on `target_part`):
  - "cap"             — the piece that screws on the bottle: female PCO-1881
                        thread, a drink nozzle you sip from, and an internal
                        seat ledge that retains the filter medium.
  - "housing"         — a cartridge chamber that holds the medium: female thread
                        at the inlet, an outlet boss, and internal seat ledges.
  - "membrane_holder" — a slim disc holder / seat that carries a hollow-fiber or
                        ceramic element and drops into the housing bore.

Thread strategy (verified watertight + fast, ~1-6 s per render):
  PET necks are short, so we sweep a trapezoidal profile along a genuine
  `makeHelix` path for only ~1.5 turns. The rib's ROOT radius is pushed a little
  way into the surrounding wall material (the `overlap`), so the union with the
  bore wall is a clean volumetric boolean instead of a fragile tangent kiss —
  that is what keeps the mesh watertight. (A rib whose root sits exactly on the
  bore surface tessellates into cracks; overlapping it fixes that.)

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `housing_od`).
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


# ── PCO-1881 bottle-neck finish (nominal geometry) ───────────────────────────
# The ubiquitous soda / water-bottle finish. Short single-start thread. These
# nominal figures make the mating interface dimensionally real; printed threads
# add the user `clearance` on top. (Same values as the bottle-thread cartridge
# so a Faircap cap and a bottle-thread cap are interchangeable on the neck.)
PCO1881_MAJOR_D = 27.4   # thread major (outer) diameter, mm
PCO1881_PITCH = 2.7      # thread pitch, mm
PCO1881_TURNS = 1.5      # engagement turns (a touch over one for a secure grab)


# ── Parameters ───────────────────────────────────────────────────────────────
target_part = str(PARAM(lambda: target_part, "cap"))       # cap | housing | membrane_holder
filter_type = str(PARAM(lambda: filter_type, "charcoal"))  # charcoal | membrane | ceramic

housing_od = float(PARAM(lambda: housing_od, 40.0))        # housing outer diameter (mm)
housing_length = float(PARAM(lambda: housing_length, 80.0))  # housing length (mm)
wall = float(PARAM(lambda: wall, 2.6))                     # radial wall thickness (mm)
clearance = float(PARAM(lambda: clearance, 0.4))          # printed-thread fit slop, per side (mm)
nozzle_bore = float(PARAM(lambda: nozzle_bore, 6.0))      # drink-nozzle inner bore (mm)
nozzle_len = float(PARAM(lambda: nozzle_len, 16.0))       # drink-nozzle length above cap (mm)
seat_lip = float(PARAM(lambda: seat_lip, 2.4))           # inward retaining ledge width (mm)

# Clamp inputs to sane ranges so extreme UI values still build watertight.
housing_od = max(30.0, min(housing_od, 60.0))
housing_length = max(40.0, min(housing_length, 150.0))
wall = max(1.6, min(wall, 6.0))
clearance = max(0.0, min(clearance, 1.0))
nozzle_bore = max(2.0, min(nozzle_bore, 16.0))
nozzle_len = max(6.0, min(nozzle_len, 40.0))
seat_lip = max(1.0, min(seat_lip, 5.0))


# ── Thread primitive (inlined — imports of repo libs are blocked in sandbox) ──
def _helix_path(pitch, height):
    """A helical wire centered on Z. Radius ~0 so the swept profile (already at
    the target radius in its own plane) traces the true helix."""
    return cq.Wire.makeHelix(pitch=pitch, height=height, radius=1e-6)


def female_thread(bore_r, pitch, thread_h, thr_depth, overlap):
    """Internal (female) helical rib. Ridges point INWARD from the bore wall to
    grab a male bottle thread. Root radius = bore_r + overlap so the rib bites
    into the wall material (clean, watertight union). Crest at bore_r - thr_depth."""
    root_r = bore_r + overlap
    crest_r = max(0.5, bore_r - thr_depth)
    prof = (
        cq.Workplane("XZ")
        .polyline([
            (root_r, -pitch * 0.32),
            (crest_r, -pitch * 0.14),
            (crest_r, pitch * 0.14),
            (root_r, pitch * 0.32),
        ])
        .close()
    )
    rib = prof.sweep(_helix_path(pitch, thread_h), isFrenet=True)
    # Nudge up half a pitch so the rib starts inside the wall, not at the open rim.
    return rib.translate((0, 0, pitch * 0.5))


def neck_bore_r():
    """Radius of the female thread bore = male major Ø plus clearance per side."""
    return (PCO1881_MAJOR_D + 2.0 * clearance) / 2.0


def neck_ring(base_th, ring_h):
    """A short cylindrical collar carrying the PCO-1881 female thread, opening at
    z=0. Returns (solid, total_h, outer_d, bore_r). `base_th` closes the TOP with
    a disk (a through channel is bored by the caller when the collar must pass
    liquid); `ring_h` is how tall the threaded barrel is above any base."""
    bore_r = neck_bore_r()
    thr_depth = 0.55 * PCO1881_PITCH
    overlap = min(0.6, wall * 0.35 + 0.2)
    thread_h = PCO1881_PITCH * PCO1881_TURNS
    barrel_h = max(ring_h, thread_h + 1.5)

    outer_d = PCO1881_MAJOR_D + 2.0 * clearance + 2.0 * wall
    total_h = barrel_h + base_th

    body = cq.Workplane("XY").circle(outer_d / 2.0).extrude(total_h)
    # Hollow the bore from the bottom up to (but not through) the closing base.
    bore = cq.Workplane("XY").circle(bore_r).extrude(barrel_h + 0.6)
    body = body.cut(bore)
    body = body.union(female_thread(bore_r, PCO1881_PITCH, thread_h, thr_depth, overlap))
    return body, total_h, outer_d, bore_r


# ── Filter-medium internals ──────────────────────────────────────────────────
def seat_ring(inner_r, outer_r, z, h):
    """An annular ledge (washer) that narrows the bore to `inner_r` so the filter
    disc rests on it and cannot fall through. One clean revolve-free extrude."""
    disk = cq.Workplane("XY").circle(outer_r).extrude(h).translate((0, 0, z))
    hole = cq.Workplane("XY").circle(inner_r).extrude(h + 2.0).translate((0, 0, z - 1.0))
    return disk.cut(hole)


def perforated_disk(radius, thickness, hole_r, ring_count, z):
    """A retaining grille: a thin disk perforated with concentric rings of holes
    so water flows through but the granular/ceramic medium is retained. Built as
    disk minus a polar array of bores (bounded boolean count → stays fast)."""
    disk = cq.Workplane("XY").circle(radius).extrude(thickness).translate((0, 0, z))
    holes = []
    for ri in range(1, ring_count + 1):
        rr = radius * ri / (ring_count + 1)
        n = max(4, int(6 * ri))
        try:
            ring = (
                cq.Workplane("XY")
                .polarArray(radius=rr, startAngle=0, angle=360, count=n)
                .circle(hole_r)
                .extrude(thickness + 2.0)
                .translate((0, 0, z - 1.0))
            )
            holes.append(ring)
        except Exception:
            pass  # a degenerate ring is skipped, never fatal
    for h in holes:
        disk = disk.cut(h)
    return disk


# ── Part builders ────────────────────────────────────────────────────────────
def build_cap():
    """The bottle-mounted cap: PCO-1881 female thread at the base, a drink nozzle
    on top, and an internal seat ledge that retains the filter medium.

    Screws onto a bottle of raw water; invert to drink filtered water from the
    nozzle. Liquid path: bottle → threaded bore → past the filter seat → nozzle."""
    # Collar (threaded barrel) with a closed shoulder that carries the nozzle.
    top_th = max(1.8, wall)
    collar, collar_h, collar_od, bore_r = neck_ring(base_th=top_th, ring_h=0.0)

    shoulder_z = collar_h  # top face of the closed collar

    # Drink nozzle: a tapered tube rising from the shoulder.
    n_bore = min(nozzle_bore, collar_od - 4.0 * wall) / 2.0
    n_bore = max(1.0, n_bore)
    noz_wall = max(1.4, wall - 0.6)
    base_or = min(collar_od / 2.0 - 0.6, n_bore + noz_wall + 3.0)
    tip_or = n_bore + noz_wall
    nozzle = (
        cq.Workplane("XY")
        .circle(base_or)
        .workplane(offset=nozzle_len)
        .circle(tip_or)
        .loft(combine=True)
        .translate((0, 0, shoulder_z))
    )
    body = collar.union(nozzle)

    # Bore the drink channel through the nozzle AND the shoulder into the bore.
    channel = (
        cq.Workplane("XY")
        .circle(n_bore)
        .extrude(nozzle_len + top_th + 2.0)
        .translate((0, 0, shoulder_z - top_th - 1.0))
    )
    body = body.cut(channel)

    # Internal retaining seat: an annular ledge just above the thread that holds
    # the filter disc/medium against the flow, leaving the nozzle bore open.
    seat_inner = max(n_bore + 0.6, bore_r - seat_lip)
    seat = seat_ring(seat_inner, bore_r + 0.4, z=max(0.5, collar_h - top_th - 1.6), h=1.6)
    body = body.union(seat)

    try:
        body = body.clean()
    except Exception:
        pass
    return body


def build_housing():
    """A stand-alone filter cartridge chamber sized by `housing_od` /
    `housing_length`. Female PCO-1881 thread at the inlet (bottom) so it screws
    onto a bottle, a hollow medium chamber in the middle, retaining seat ledges
    top and bottom, and a reduced outlet boss on top."""
    od = housing_od
    length = housing_length
    bore_r = neck_bore_r()

    # Outer shell.
    body = cq.Workplane("XY").circle(od / 2.0).extrude(length)

    # Medium chamber: hollowed from inside, leaving `wall` all round and a floor
    # web / ceiling web so the two ends stay closed except for the ports.
    chamber_r = od / 2.0 - wall
    chamber_r = max(bore_r + 0.5, chamber_r)
    end_web = max(2.0, wall)
    chamber = (
        cq.Workplane("XY")
        .circle(chamber_r)
        .extrude(length - 2.0 * end_web)
        .translate((0, 0, end_web))
    )
    body = body.cut(chamber)

    # Inlet: female PCO-1881 thread cut/added into the bottom end web + a through
    # port so bottle water enters. Build the threaded collar and fuse it into the
    # bottom, then open the inlet port.
    thr_depth = 0.55 * PCO1881_PITCH
    overlap = min(0.6, wall * 0.35 + 0.2)
    thread_h = PCO1881_PITCH * PCO1881_TURNS
    inlet_port = cq.Workplane("XY").circle(bore_r).extrude(end_web + 1.0).translate((0, 0, -0.5))
    body = body.cut(inlet_port)
    body = body.union(
        female_thread(bore_r, PCO1881_PITCH, min(thread_h, end_web + 0.2), thr_depth, overlap)
    )

    # Outlet boss on the top end: a short reduced spigot with a bore so filtered
    # water leaves (and downstream parts / tubing can attach).
    out_bore = max(1.5, min(nozzle_bore, od - 4.0 * wall) / 2.0)
    boss_or = out_bore + max(1.6, wall)
    boss_h = max(5.0, nozzle_len * 0.5)
    boss = (
        cq.Workplane("XY")
        .circle(boss_or)
        .extrude(boss_h)
        .translate((0, 0, length))
    )
    body = body.union(boss)
    out_channel = (
        cq.Workplane("XY")
        .circle(out_bore)
        .extrude(boss_h + end_web + 2.0)
        .translate((0, 0, length - end_web - 1.0))
    )
    body = body.cut(out_channel)

    # Retaining seats: perforated grilles top & bottom of the chamber keep the
    # medium in while passing water. (charcoal/ceramic → grille; membrane → the
    # membrane_holder part carries the element, so a light single grille suffices.)
    grille_hole = 1.4 if filter_type != "membrane" else 2.0
    rings = 3 if chamber_r > 12.0 else 2
    bottom_grille = perforated_disk(
        chamber_r - 0.3, 1.6, grille_hole, rings, z=end_web + 0.2
    )
    top_grille = perforated_disk(
        chamber_r - 0.3, 1.6, grille_hole, rings, z=length - end_web - 1.8
    )
    body = body.union(bottom_grille).union(top_grille)

    try:
        body = body.clean()
    except Exception:
        pass
    return body


def build_membrane_holder():
    """A slim disc holder / seat that carries a hollow-fiber or ceramic filter
    element and drops into the housing (or cap) bore. A shallow cup: a perforated
    floor the element sits on, a short retaining wall, and a rim lip that lands on
    the housing seat ledge so it self-locates."""
    bore_r = neck_bore_r()
    cup_or = bore_r - 0.4          # slides into the bore with a little slack
    cup_or = max(6.0, cup_or)
    rim_or = cup_or + 1.4          # rim lip overhangs to rest on a seat ledge
    floor_th = 1.8
    wall_h = max(6.0, min(housing_length * 0.18, 22.0))
    holder_wall = max(1.4, wall - 0.8)

    # Outer cup wall (ring) + rim lip at the base.
    outer = cq.Workplane("XY").circle(cup_or).extrude(wall_h)
    inner = (
        cq.Workplane("XY")
        .circle(cup_or - holder_wall)
        .extrude(wall_h)
        .translate((0, 0, floor_th))
    )
    body = outer.cut(inner)
    rim = seat_ring(cup_or - 0.2, rim_or, z=0.0, h=floor_th)
    body = body.union(rim)

    # Perforated floor so water passes through the seated element.
    floor_grille = perforated_disk(
        cup_or - holder_wall - 0.2, floor_th, 1.4,
        3 if cup_or > 11.0 else 2, z=0.0,
    )
    body = body.union(floor_grille)

    # For a ceramic element, add a central standoff post so the disc is held off
    # the floor and water reaches its full underside.
    if filter_type == "ceramic":
        post = (
            cq.Workplane("XY")
            .circle(max(1.4, cup_or * 0.12))
            .extrude(max(2.0, wall_h * 0.35))
            .translate((0, 0, floor_th))
        )
        body = body.union(post)

    try:
        body = body.clean()
    except Exception:
        pass
    return body


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "housing":
    result = build_housing()
elif target_part == "membrane_holder":
    result = build_membrane_holder()
else:
    result = build_cap()
