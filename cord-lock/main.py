"""
Cord-Lock / Toggle Stopper — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A small toggle that locks drawstrings and cords on apparel, bags, and gear.
Single-piece, print-in-place designs that stay watertight: a spring toggle with
a printed compliant pincher that clamps the cord, a simple friction toggle with
a cord channel and a locking notch, and a squeeze cleat. Sized to the cord.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` and `math` are pre-injected globals.
  - Manifest parameters are injected as BARE globals (e.g. `cord_dia`).
  - Access them via PARAM(lambda: <name>, <default>) so the script also runs
    standalone / with any subset of params. Do NOT use globals()/eval/getattr —
    they are not in the sandbox's allowed builtins.
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


# ── Parameters ───────────────────────────────────────────────────────────────
cord_dia   = float(PARAM(lambda: cord_dia,   4.0))    # cord diameter (mm)
cords      = int(  PARAM(lambda: cords,         1))   # number of cords (1 or 2)
body_size  = float(PARAM(lambda: body_size, 14.0))    # nominal body size (mm)
wall       = float(PARAM(lambda: wall,       2.0))    # wall / rib thickness (mm)

lock_style = str(  PARAM(lambda: lock_style, "spring_button"))  # spring_button|twist|clam
target_part = str( PARAM(lambda: target_part, "spring_toggle"))  # spring_toggle|simple_toggle|cleat

# ── Safe clamps ──────────────────────────────────────────────────────────────
cords = 1 if cords < 2 else 2
cord_dia = max(1.0, min(cord_dia, body_size * 0.45))
body_size = max(cord_dia * 2.5 + 4.0, body_size)
wall = max(1.2, min(wall, body_size * 0.25))
hole_r = cord_dia / 2.0 + 0.3   # cord channel radius with a little clearance


# ── Helpers ──────────────────────────────────────────────────────────────────
def cord_offsets():
    """X positions of the cord channels (centered group)."""
    if cords == 2:
        s = cord_dia + wall
        return [-s / 2.0, s / 2.0]
    return [0.0]


def build_spring_toggle():
    """A single-piece spring toggle: a barrel body with a cord channel through
    it and a printed compliant tongue (a thin cantilever cut from the body by a
    U-slot) that presses across the channel. Squeeze the tongue to open the gap
    and slide the cord; release and the tongue's springiness pinches the cord.
    Everything is one continuous watertight solid — the slot is a cut, the tongue
    stays attached at its root."""
    h = body_size            # height (cord runs along Z)
    r = body_size / 2.0      # barrel radius

    body = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, h / 2.0))
        .cylinder(h, r)
    )

    # Cord channel(s) straight through along Z.
    for ox in cord_offsets():
        chan = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(ox, 0, h / 2.0))
            .cylinder(h + 2.0, hole_r)
        )
        body = body.cut(chan)

    # Compliant tongue: cut a U-shaped slot from the +Y side that frees a
    # cantilever beam. The beam's inner face bulges toward the channel so that
    # at rest it narrows the cord path (the pinch); flexing the beam outward
    # (pressing the exposed pad) widens it to release the cord.
    slot_w = max(wall * 0.9, 1.0)         # slot gap that defines the beam sides
    beam_t = max(wall, 1.4)               # beam thickness
    beam_reach = r * 0.85                 # how far down the beam the slot runs
    beam_half = (max(cord_dia, r * 0.7)) / 2.0 + slot_w

    # Two side cuts (parallel to Z) that free the beam left and right.
    for sx in (-1.0, 1.0):
        side = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(sx * (beam_half + slot_w / 2.0), r * 0.35, h / 2.0 + (h - beam_reach) / 2.0))
            .box(slot_w, r, beam_reach)
        )
        body = body.cut(side)

    # A back-relief slot behind the beam (between beam and barrel wall) so the
    # beam can flex outward — cut from +Y, leaving the beam attached only at its
    # lower root.
    relief = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, r * 0.5 + beam_t, h / 2.0 + (h - beam_reach) / 2.0 + beam_reach * 0.15))
        .box(2.0 * beam_half, wall, beam_reach * 0.8)
    )
    body = body.cut(relief)

    # Finger pad ridge on the beam's outer face for grip.
    pad = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, r - 0.4, h * 0.72))
        .box(2.0 * beam_half, 1.2, h * 0.22)
    )
    body = body.union(pad)

    # Soften the top/bottom rims (non-fatal).
    try:
        body = body.edges("|Z").fillet(min(0.8, wall * 0.4))
    except Exception:
        pass
    return body


def build_simple_toggle():
    """A friction toggle bead: a rounded body with a cord channel and a
    perpendicular locking notch. Threading the cord through the offset notch
    forces a bend that holds by friction (the classic barrel-bead cord stop).
    One continuous watertight solid."""
    h = body_size
    r = body_size / 2.0
    body = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, h / 2.0))
        .cylinder(h, r)
    )
    # Barrel-ends rounding for a bead look.
    try:
        body = body.edges(">Z or <Z").fillet(min(r * 0.4, r - 0.6))
    except Exception:
        pass

    # Main cord channel(s) along Z.
    for ox in cord_offsets():
        chan = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(ox, 0, h / 2.0))
            .cylinder(h + 2.0, hole_r)
        )
        body = body.cut(chan)

    # Locking friction slot: a shallow transverse channel across the mid-height
    # that the cord is threaded into to jam the run — offset in Y so the cord
    # kinks. Runs along X, open at both ends, radius = cord.
    lock = (
        cq.Workplane("YZ")
        .transformed(offset=cq.Vector(0, h / 2.0, 0))
        .cylinder(body_size + 2.0, hole_r)
    )
    lock = lock.translate((0, r * 0.35, 0))
    body = body.cut(lock)
    return body


def build_cleat():
    """A squeeze cleat: a flat block with a V-throat that pinches the cord when
    pulled into the narrow end, plus a mounting hole. The cord drops into the
    wide top of the V and jams at the bottom. One watertight solid."""
    w = body_size * 1.6
    d = body_size
    t = max(body_size * 0.5, cord_dia + 2.0 * wall)
    body = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, t / 2.0))
        .box(w, d, t)
    )

    # V-throat per cord: a wedge cut from the top narrowing downward so the cord
    # wedges and grips. Cut as a downward-tapering slot (lofted box → triangle).
    for ox in cord_offsets():
        top_gap = cord_dia * 1.8
        bot_gap = max(0.6, cord_dia * 0.55)   # narrower than the cord → pinches
        throat_pts = [
            (ox - top_gap / 2.0, t),
            (ox + top_gap / 2.0, t),
            (ox + bot_gap / 2.0, t * 0.25),
            (ox - bot_gap / 2.0, t * 0.25),
        ]
        throat = (
            cq.Workplane("XZ")
            .polyline(throat_pts)
            .close()
            .extrude(d + 2.0)
            .translate((0, (d + 2.0) / 2.0, 0))
        )
        body = body.cut(throat)

    # Mounting hole through the block (Y direction).
    #
    # It used to sit on the block centreline at z = t*0.15 with
    # r = max(1.6, cord_dia*0.4): at defaults that is z in [-0.40, 2.80], which
    # breaks through the block floor (z = 0) AND reaches the throat's bottom at
    # z = t*0.25 = 2.00, so throat and bore merged into one channel across the
    # full block depth and freed the slab below it (cleat rendered 2 bodies at
    # defaults and at preset tent_cleat).
    #
    # There is no room for it under the throat -- t*0.25 is ~2 mm -- but ~7.6 mm
    # of solid block each side of the throat group. Put the bore there, at
    # mid-height, bounded so it touches neither the throat nor an outer face.
    # The bore shrinks to whatever genuinely fits beside the throat; where the
    # throat group leaves less than a printable hole (wide cords at cords=2
    # with a thick wall) it is omitted entirely rather than emitted as a cutter
    # that would breach an outer face. A mounting hole is a convenience on this
    # part, so degrading it is preferable to rejecting the parameter set.
    offs = cord_offsets()
    throat_half = max(abs(o) for o in offs) + cord_dia * 1.8 / 2.0
    free = w / 2.0 - throat_half          # solid width beside the throat group
    hole_r = min(max(1.6, cord_dia * 0.4),
                 (free - 2.0 * wall) / 2.0,
                 (t - 2.0 * wall) / 2.0)
    if hole_r >= 0.8:
        mount_x = throat_half + wall + hole_r
        mount = (
            cq.Workplane("XZ")
            .transformed(offset=cq.Vector(mount_x, t / 2.0, 0))
            .cylinder(d + 2.0, hole_r)
        )
        body = body.cut(mount)
    return body


# ── Dispatch ─────────────────────────────────────────────────────────────────
if target_part == "cleat" or lock_style == "clam":
    result = build_cleat()
elif target_part == "simple_toggle" or lock_style == "twist":
    result = build_simple_toggle()
else:
    result = build_spring_toggle()
