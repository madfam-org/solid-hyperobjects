"""
Book-Fold Phone — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

The archetype: two rigid half-frames that meet at a fold axis running along the
LONG edge, one continuous display folded inward across both of them, and a
second display on the outside of one half. One continuous `fold_angle` turns the
camera half about the fold axis: 0 closed, 180 open.

WHY THE GEOMETRY IS BUILT THE WAY IT IS
---------------------------------------
Three decisions carry the whole model, and each is checkable against published
numbers rather than chosen for looks:

1. **The fold axis is the X axis through the ORIGIN, in the middle of the gap.**
   The graph engine's `rotate` node turns about the origin and nothing else, so
   anchoring there is what lets the fold be one node with no compensating
   translate. Putting the axis in the MIDDLE OF THE GAP is what makes the gap
   disappear when the device opens: the cover half sits at
   z in [-(gap/2 + t), -gap/2] and the camera half at [+gap/2, +(gap/2 + t)], and
   a 180 degree turn about that axis lands the camera half in the cover half's
   own z band. Closed depth is therefore `2t + gap` and open depth is `t` —
   which is exactly what every manufacturer in this family publishes.

2. **The half thickness IS the published open depth; the gap is what is left
   over.** `gap = closed.depth - 2 x open.depth`. Both inputs are the
   manufacturer's, so the split of the closed thickness is not an archetype
   guess the way the clamshell's 45/55 deck split had to be. The numbers it
   produces track the hardware's own history: 1.9 mm on the first Galaxy Fold,
   3.2 mm on the Z Fold3, 0.1-0.9 mm on the current generation.

3. **The two halves are different widths, and both come from published
   numbers.** `camera_half_width = open.width - closed.width`. A book fold
   closes because one half is slightly narrower than the other; that difference
   is the whole reason the closed width is not simply half the open width.

Everything else follows: the crease relief is a cylinder ON the fold axis, so it
is invariant under the fold and can be cut before the rotate; the hinge leaf is
that same cylinder, smaller by a running clearance and clipped to the cover
half's own band, so it is inside the envelope at every angle.

COMPOSITION — a device is a hyperobject of hyperobjects
------------------------------------------------------
A display, a hinge, a lens window, a button, a port, a card tray: each is a
hyperobject in its own right that feeds into this one. Each is built here by its
own function taking its OWN parameter dict, so it can be lifted into its own
cartridge without a rewrite: nothing below reads a manifest global from inside a
component, and no component knows what assembly it is part of. The assembly
functions (`cover_half_part`, `camera_half_part`, `hinge_part`) are the only code
that maps this manifest's parameters onto those dicts.

    component               CDG interface it exposes / consumes
    ---------------------   ---------------------------------------------------
    frame_half              exposes device_envelope, cradle_seat
    foldable_display        exposes crease_region; consumes fold_axis
    display_panel           exposes display_recess (the cover display)
    hinge_foldable          exposes fold_axis; consumes crease_region
    lens_window             exposes lens_aperture
    system_button_cluster   exposes button_seat
    port_receptacle         exposes port_cutout
    card_slot               exposes card_slot
    speaker_grille          a vented face; no upstream id yet

The manifest's `composition` block carries the same table for machines. The
vocabulary is Telesia's DEVICE_GEOMETRY.md 3.1; gate H8 there is what will rule
how a component cartridge feeds an assembly cartridge, and until it does a
component lives here as a function that already carries the id it will export.

This is a FAMILY, not a product. Named presets carry published dimensions from
Telesia's device-geometry registry with a provenance line; every other number is
an archetype default that is ours, and NOTICE says which is which. No logos, no
trade dress, no surface detail beyond what published dimensions imply.

Frame (stated again in docs/README.md, because manufacturers in this family
label the long axis "width" — Apple's iPhone Duo page says so outright — and the
registry records their labels literally):

    X  hinge_axis_length   the LONG axis. The fold axis is the X axis through
                           the origin. Registry `dimensions_mm.closed.height`,
                           which equals `open.height` on every device that
                           publishes both.
    Y  the folding axis    the cover half runs from the fold at y = 0 to its
                           opening edge at y = cover_half_width; the camera half
                           does the same and then turns.
    Z  half_thickness      registry `dimensions_mm.open.depth`. The gap
                           mid-plane — where the two inner faces face each other
                           when closed — is z = 0.

Parts (dispatched on `target_part`):
  - cover_half  : the half that carries the cover display, the side buttons and
                  every opening in the end face.
  - camera_half : the half that carries the camera island, already turned by
                  `fold_angle`.
  - hinge       : the leaf that turns inside the crease relief.

Graph twin: `bookfold.graph.json` builds the same three parts from the same
parameters using the nineteen graph-engine node types, with each component's
nodes grouped under a component-slug prefix. Sub-graph reuse — yantra4d lane
G-CLUSTERS — is what would let the twin REFERENCE a component cartridge instead
of duplicating its nodes; until it lands the twin inlines them.

Sandbox contract (apps/api/services/engine/cq_runner.py):
  - `cq` (cadquery) and `math` are pre-injected globals; imported here too so the
    module lints clean (ruff F821) and runs standalone.
  - Manifest parameters arrive as BARE globals (a param `half_thickness` ->
    global `half_thickness`). They are read through the PARAM(lambda: name,
    default) guard because the sandbox exposes neither globals() nor
    eval/getattr.
  - The final solid is assigned to the top-level name `result`.
"""

import math  # noqa: F401 — injected by the sandbox; imported so the file runs standalone

import cadquery as cq


# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.

    `except Exception` catches the NameError raised for an unbound param name
    (the sandbox does not expose globals()/NameError directly).
    """
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
# Every default below is the archetype's own, generated by Telesia's
# scripts/device-presets.py from BOOKFOLD_ARCHETYPE_BASE + BOOKFOLD_ARCHETYPE_RULES.
# They describe no product. Device values arrive as presets.

# L0 — envelope and the fold
hinge_axis_length = float(PARAM(lambda: hinge_axis_length, 156.0))
cover_half_width = float(PARAM(lambda: cover_half_width, 74.0))
camera_half_width = float(PARAM(lambda: camera_half_width, 72.0))
half_thickness = float(PARAM(lambda: half_thickness, 4.7))
corner_radius = float(PARAM(lambda: corner_radius, 6.0))
fold_angle = float(PARAM(lambda: fold_angle, 135.0))
cover_half_center_y = float(PARAM(lambda: cover_half_center_y, 37.0))
cover_half_center_z = float(PARAM(lambda: cover_half_center_z, -2.65))
camera_half_center_y = float(PARAM(lambda: camera_half_center_y, 36.0))
camera_half_center_z = float(PARAM(lambda: camera_half_center_z, 2.65))

# L0 — the hinge. `hinge_leaf_radius` is `hinge_cavity_radius` less the
# archetype's 0.3 mm running clearance; the graph engine has no expressions, so
# the two are independent parameters the generator keeps in step (lane G-EXPR).
hinge_cavity_radius = float(PARAM(lambda: hinge_cavity_radius, 2.415))
hinge_cavity_span = float(PARAM(lambda: hinge_cavity_span, 146.64))
hinge_leaf_radius = float(PARAM(lambda: hinge_leaf_radius, 2.115))
hinge_leaf_span = float(PARAM(lambda: hinge_leaf_span, 146.04))
hinge_clip_span = float(PARAM(lambda: hinge_clip_span, 400.0))
hinge_clip_center_y = float(PARAM(lambda: hinge_clip_center_y, -200.0))

# L1 — displays. The inner display is ONE panel across both halves, so it has a
# span on each; the split is unequal whenever the halves are.
inner_display_width = float(PARAM(lambda: inner_display_width, 151.0))
inner_display_cover_span = float(PARAM(lambda: inner_display_cover_span, 71.5))
inner_display_camera_span = float(PARAM(lambda: inner_display_camera_span, 69.5))
inner_display_cover_center_y = float(PARAM(lambda: inner_display_cover_center_y, 35.75))
inner_display_camera_center_y = float(PARAM(lambda: inner_display_camera_center_y, 34.75))
inner_display_cover_cut_center_z = float(PARAM(lambda: inner_display_cover_cut_center_z, -0.7))
inner_display_camera_cut_center_z = float(PARAM(lambda: inner_display_camera_cut_center_z, 0.7))
cover_display_width = float(PARAM(lambda: cover_display_width, 151.0))
cover_display_height = float(PARAM(lambda: cover_display_height, 69.0))
cover_display_center_y = float(PARAM(lambda: cover_display_center_y, 37.0))
cover_display_cut_center_z = float(PARAM(lambda: cover_display_cut_center_z, -4.6))
display_recess_depth = float(PARAM(lambda: display_recess_depth, 0.8))

# L2 — the camera island. A RECESS, never a raised bump: see lens_window().
lens_island_width = float(PARAM(lambda: lens_island_width, 30.24))
lens_island_height = float(PARAM(lambda: lens_island_height, 30.24))
lens_island_depth = float(PARAM(lambda: lens_island_depth, 0.6))
lens_island_center_x = float(PARAM(lambda: lens_island_center_x, 56.88))
lens_island_center_y = float(PARAM(lambda: lens_island_center_y, 21.12))
lens_island_cut_center_z = float(PARAM(lambda: lens_island_cut_center_z, 4.7))
lens_count = int(PARAM(lambda: lens_count, 3))
lens_radius = float(PARAM(lambda: lens_radius, 3.9312))
lens_depth = float(PARAM(lambda: lens_depth, 1.8))
lens_first_center_x = float(PARAM(lambda: lens_first_center_x, 47.736))
lens_pitch_x = float(PARAM(lambda: lens_pitch_x, 9.072))
lens_center_y = float(PARAM(lambda: lens_center_y, 21.12))
lens_cut_center_z = float(PARAM(lambda: lens_cut_center_z, 4.1))

# L2 — the side buttons, on the cover half's opening edge.
button_count = int(PARAM(lambda: button_count, 2))
button_width = float(PARAM(lambda: button_width, 14.0))
button_seat_depth = float(PARAM(lambda: button_seat_depth, 2.0))
button_height = float(PARAM(lambda: button_height, 2.0))
button_first_center_x = float(PARAM(lambda: button_first_center_x, 7.72))
button_pitch_x = float(PARAM(lambda: button_pitch_x, 22.0))
button_center_y = float(PARAM(lambda: button_center_y, 74.0))
button_center_z = float(PARAM(lambda: button_center_z, -2.65))

# L2 — the end face. The presence flags exist because the registry knows, per
# device, which connectors the manufacturer lists: a Galaxy Z Fold7 preset must
# not grow a card tray Samsung does not list. The graph twin cannot read them
# (no branching) — see docs/research/book-fold-archetype.md.
usb_c_present = bool(PARAM(lambda: usb_c_present, True))
usb_c_width = float(PARAM(lambda: usb_c_width, 8.6))
usb_c_height = float(PARAM(lambda: usb_c_height, 2.8))
usb_c_depth = float(PARAM(lambda: usb_c_depth, 10.0))
usb_c_center_x = float(PARAM(lambda: usb_c_center_x, -78.0))
usb_c_center_y = float(PARAM(lambda: usb_c_center_y, 37.0))
usb_c_center_z = float(PARAM(lambda: usb_c_center_z, -2.65))
card_slot_present = bool(PARAM(lambda: card_slot_present, True))
card_slot_width = float(PARAM(lambda: card_slot_width, 12.5))
card_slot_height = float(PARAM(lambda: card_slot_height, 2.0))
card_slot_depth = float(PARAM(lambda: card_slot_depth, 8.0))
card_slot_center_x = float(PARAM(lambda: card_slot_center_x, -78.0))
card_slot_center_y = float(PARAM(lambda: card_slot_center_y, 16.28))
card_slot_center_z = float(PARAM(lambda: card_slot_center_z, -2.65))
speaker_hole_count = int(PARAM(lambda: speaker_hole_count, 5))
speaker_hole_radius = float(PARAM(lambda: speaker_hole_radius, 0.7))
speaker_hole_depth = float(PARAM(lambda: speaker_hole_depth, 6.0))
speaker_center_x = float(PARAM(lambda: speaker_center_x, -78.0))
speaker_first_center_y = float(PARAM(lambda: speaker_first_center_y, 54.3))
speaker_pitch_y = float(PARAM(lambda: speaker_pitch_y, 3.0))
speaker_center_z = float(PARAM(lambda: speaker_center_z, -2.65))

target_part = str(PARAM(lambda: target_part, "cover_half"))


# ── Shared pattern helper ────────────────────────────────────────────────────
# Mirrors the graph engine's emission exactly, including the `range(1, count)`
# shape, so a count of 1 is one copy and the two engines agree body for body.

def linear_pattern(shape, count, dx, dy=0.0, dz=0.0):
    """Union `count` copies of `shape` stepped by (dx, dy, dz)."""
    out = shape
    for i in range(1, count):
        out = out.union(shape.translate((dx * i, dy * i, dz * i)))
    return out


# ═════════════════════════════════════════════════════════════════════════════
# COMPONENTS — each is its own hyperobject. Each takes its own dict; none reads
# a manifest global; each is buildable standalone.
# ═════════════════════════════════════════════════════════════════════════════

def frame_half(p):
    """One rigid half-frame: a slab rounded on its OPENING edge only.

    CDG exposed: `device_envelope` (the closed outline another accessory mates
    to) and `cradle_seat` (the outer face a dock or stand registers against).

    Only the two vertical edges at the opening edge are rounded. A book fold's
    SPINE is straight in plan — its rounding is in section, in the hinge cover —
    and a fillet there would put a notch in the crease where the inner display
    crosses it. A sectioned spine is a free-form profile (yantra4d lane
    G-NODES-1); a square one is the honest L0 form and is identical in both
    engines.

    p: length, width, thickness, center_y, center_z, corner_radius
    """
    return (
        cq.Workplane("XY")
        .box(p["length"], p["width"], p["thickness"])
        .translate((0.0, p["center_y"], p["center_z"]))
        .edges("|Z and >Y")
        .fillet(p["corner_radius"])
    )


def foldable_display(p):
    """One half's portion of the inward-folding display, as a recess tool.

    CDG exposed: `crease_region` — the strip of the panel that bends, which is
    the part of this recess nearest the fold axis and which sizes the relief the
    hinge must give it.
    CDG consumed: `fold_axis` — the tool runs FROM the fold axis outward
    (`span` from y = 0), because the panel is one continuous sheet whose halves
    are only separable at that axis.

    The solid returned is the TOOL: the assembly cuts it from a half-frame, so
    the same component serves both halves unchanged. It is deliberately a plain
    rectangle: a display with rounded corners, or the teardrop section the panel
    actually takes when folded, both need a free-form profile (G-NODES-1).

    p: width, span, recess_depth, center_y, cut_center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["width"], p["span"], p["recess_depth"])
        .translate((0.0, p["center_y"], p["cut_center_z"]))
    )


def display_panel(p):
    """A rigid display's active area as a recess tool — here, the cover display.

    CDG exposed: `display_recess` — the bounded flat area the panel occupies.
    The same component the clamshell cartridge factors out, with the same id, so
    a cover display and a clamshell deck display are one part in two assemblies.

    p: width, height, recess_depth, center_x, center_y, cut_center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["width"], p["height"], p["recess_depth"])
        .translate((p["center_x"], p["center_y"], p["cut_center_z"]))
    )


def hinge_foldable(p):
    """The teardrop fold: the crease relief, and the leaf that turns inside it.

    CDG exposed: `fold_axis` — the X axis through the origin, in the middle of
    the gap between the two half-frames.
    CDG consumed: `crease_region` — the relief radius is sized so the folding
    panel's bend has room; the gap the two halves stand apart by IS that bend's
    height, and it is `closed.depth - 2 x open.depth`, both published.

    Two roles, one component, because they are the same cylinder on the same
    axis at two radii:

      `clip` false -> the RELIEF, cut from both halves. A cylinder centred on the
        fold axis is invariant under the fold, so cutting it before the rotate
        and after it give the same solid — which is why the twin can cut it
        early and still agree.
      `clip` true  -> the LEAF, the printed hinge. The same cylinder less the
        running clearance, with everything at y < 0 cut away (or the closed width
        would exceed the published figure) and then intersected with the cover
        half's own z band (or it would stand proud of the open face). What
        survives is inside the published envelope at EVERY fold angle.

    A real free-stop teardrop hinge is a multi-link mechanism whose section is
    not circular: that is L3, and it needs a free-form profile (G-NODES-1) and a
    bounded revolve (G-NODES-2). No published source describes one for any device
    in this family, so modelling it would be invention, not resolution.

    p: radius, span, clip, clip_span, clip_center_y, slab_length,
       slab_thickness, slab_center_z
    """
    body = (
        cq.Workplane("XY")
        .cylinder(p["span"], p["radius"])
        .rotate((0, 0, 0), (0, 1, 0), 90)
    )
    if not p.get("clip"):
        return body
    keep = (
        cq.Workplane("XY")
        .box(p["clip_span"], p["clip_span"], p["clip_span"])
        .translate((0.0, p["clip_center_y"], 0.0))
    )
    band = (
        cq.Workplane("XY")
        .box(p["slab_length"], p["clip_span"], p["slab_thickness"])
        .translate((0.0, 0.0, p["slab_center_z"]))
    )
    return body.cut(keep).intersect(band)


def lens_window(p):
    """The camera island and its lens apertures, as one recess tool.

    CDG exposed: `lens_aperture` — the bounded openings a lens stack sits behind.

    A RECESS, not a raised bump, and the reason is provenance rather than taste:
    every depth published in this family EXCLUDES the camera bump, and no
    manufacturer publishes the bump's height. Raising an island would invent a
    dimension AND push the model past the envelope it is verified against. The
    island is therefore sunk into the outer face and the apertures are sunk
    deeper still, from the same face, in one tool each.

    p: island_width, island_height, island_depth, island_center_x,
       island_center_y, island_cut_center_z, count, radius, depth,
       first_center_x, pitch_x, center_y, cut_center_z
    """
    island = (
        cq.Workplane("XY")
        .box(p["island_width"], p["island_height"], p["island_depth"])
        .translate((p["island_center_x"], p["island_center_y"],
                    p["island_cut_center_z"]))
    )
    lens = (
        cq.Workplane("XY")
        .cylinder(p["depth"], p["radius"])
        .translate((p["first_center_x"], p["center_y"], p["cut_center_z"]))
    )
    return island.union(linear_pattern(lens, p["count"], p["pitch_x"]))


def system_button_cluster(p):
    """A row of seats for the power and volume keys, in a frame's opening edge.

    CDG exposed: `button_seat` — one rectangular pocket; the cluster is `count`
    of them at `pitch_x`. The same id the clamshell's round `face_button` and
    `button_row` expose: one interface, three arrangements across two families.

    The tool straddles the edge rather than sitting flush against it, so the cut
    never presents a face coincident with the frame's and it bites exactly half
    of `seat_depth` into real material.

    p: count, width, seat_depth, height, first_center_x, pitch_x, center_y,
       center_z
    """
    seat = (
        cq.Workplane("XY")
        .box(p["width"], p["seat_depth"], p["height"])
        .translate((p["first_center_x"], p["center_y"], p["center_z"]))
    )
    return linear_pattern(seat, p["count"], p["pitch_x"])


def port_receptacle(p):
    """A connector opening in a frame's end face.

    CDG exposed: `port_cutout`. Sized to clear a USB-C receptacle (the plug is
    8.34 x 2.56 mm nominal); like the button cluster it straddles the face it
    opens, so it bites half of `depth`.

    p: width, height, depth, center_x, center_y, center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["depth"], p["width"], p["height"])
        .translate((p["center_x"], p["center_y"], p["center_z"]))
    )


def card_slot(p):
    """A SIM-tray mouth in a frame's end face.

    CDG exposed: `card_slot`. Present only where the registry lists a `sim`
    port; an eSIM-only device (the iPhone Duo says so outright) has none, and
    that is a SOURCED absence, not a gap in the data. The tray's own dimensions
    are archetype: no manufacturer publishes them.

    p: width, height, depth, center_x, center_y, center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["depth"], p["width"], p["height"])
        .translate((p["center_x"], p["center_y"], p["center_z"]))
    )


def speaker_grille(p):
    """A row of vent holes in an end face.

    No upstream CDG id; a grille is a vented face, not a mating feature.
    ARCHETYPE THROUGHOUT — the registry does not describe grilles.

    p: count, hole_radius, hole_depth, center_x, first_center_y, pitch_y,
       center_z
    """
    hole = (
        cq.Workplane("XY")
        .cylinder(p["hole_depth"], p["hole_radius"])
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((p["center_x"], p["first_center_y"], p["center_z"]))
    )
    return linear_pattern(hole, p["count"], 0.0, p["pitch_y"], 0.0)


# ═════════════════════════════════════════════════════════════════════════════
# ASSEMBLY — the only code that maps this manifest's parameters onto component
# dicts. Everything above is portable; everything below is this cartridge.
# ═════════════════════════════════════════════════════════════════════════════

def _crease_relief():
    return hinge_foldable({
        "radius": hinge_cavity_radius,
        "span": hinge_cavity_span,
        "clip": False,
        "clip_span": hinge_clip_span,
        "clip_center_y": hinge_clip_center_y,
        "slab_length": hinge_axis_length,
        "slab_thickness": half_thickness,
        "slab_center_z": cover_half_center_z,
    })


def cover_half_part():
    solid = frame_half({
        "length": hinge_axis_length, "width": cover_half_width,
        "thickness": half_thickness,
        "center_y": cover_half_center_y, "center_z": cover_half_center_z,
        "corner_radius": corner_radius,
    })
    solid = solid.cut(_crease_relief())
    solid = solid.cut(foldable_display({
        "width": inner_display_width, "span": inner_display_cover_span,
        "recess_depth": display_recess_depth,
        "center_y": inner_display_cover_center_y,
        "cut_center_z": inner_display_cover_cut_center_z,
    }))
    solid = solid.cut(display_panel({
        "width": cover_display_width, "height": cover_display_height,
        "recess_depth": display_recess_depth,
        "center_x": 0.0, "center_y": cover_display_center_y,
        "cut_center_z": cover_display_cut_center_z,
    }))
    if button_count > 0:
        solid = solid.cut(system_button_cluster({
            "count": button_count, "width": button_width,
            "seat_depth": button_seat_depth, "height": button_height,
            "first_center_x": button_first_center_x,
            "pitch_x": button_pitch_x, "center_y": button_center_y,
            "center_z": button_center_z,
        }))
    if usb_c_present:
        solid = solid.cut(port_receptacle({
            "width": usb_c_width, "height": usb_c_height, "depth": usb_c_depth,
            "center_x": usb_c_center_x, "center_y": usb_c_center_y,
            "center_z": usb_c_center_z,
        }))
    if card_slot_present:
        solid = solid.cut(card_slot({
            "width": card_slot_width, "height": card_slot_height,
            "depth": card_slot_depth,
            "center_x": card_slot_center_x, "center_y": card_slot_center_y,
            "center_z": card_slot_center_z,
        }))
    if speaker_hole_count > 0:
        solid = solid.cut(speaker_grille({
            "count": speaker_hole_count, "hole_radius": speaker_hole_radius,
            "hole_depth": speaker_hole_depth, "center_x": speaker_center_x,
            "first_center_y": speaker_first_center_y,
            "pitch_y": speaker_pitch_y, "center_z": speaker_center_z,
        }))
    return solid


def camera_half_part():
    solid = frame_half({
        "length": hinge_axis_length, "width": camera_half_width,
        "thickness": half_thickness,
        "center_y": camera_half_center_y, "center_z": camera_half_center_z,
        "corner_radius": corner_radius,
    })
    solid = solid.cut(_crease_relief())
    solid = solid.cut(foldable_display({
        "width": inner_display_width, "span": inner_display_camera_span,
        "recess_depth": display_recess_depth,
        "center_y": inner_display_camera_center_y,
        "cut_center_z": inner_display_camera_cut_center_z,
    }))
    solid = solid.cut(lens_window({
        "island_width": lens_island_width, "island_height": lens_island_height,
        "island_depth": lens_island_depth,
        "island_center_x": lens_island_center_x,
        "island_center_y": lens_island_center_y,
        "island_cut_center_z": lens_island_cut_center_z,
        "count": lens_count, "radius": lens_radius, "depth": lens_depth,
        "first_center_x": lens_first_center_x, "pitch_x": lens_pitch_x,
        "center_y": lens_center_y, "cut_center_z": lens_cut_center_z,
    }))
    # The fold. The fold axis IS the X axis through the origin, in the middle of
    # the gap, so the whole half turns about it with no compensating translation:
    # 0 closed, 180 open, and at 180 the gap has closed itself.
    return solid.rotate((0, 0, 0), (1, 0, 0), fold_angle)


def hinge_part():
    return hinge_foldable({
        "radius": hinge_leaf_radius,
        "span": hinge_leaf_span,
        "clip": True,
        "clip_span": hinge_clip_span,
        "clip_center_y": hinge_clip_center_y,
        "slab_length": hinge_axis_length,
        "slab_thickness": half_thickness,
        "slab_center_z": cover_half_center_z,
    })


BUILDERS = {
    "cover_half": cover_half_part,
    "camera_half": camera_half_part,
    "hinge": hinge_part,
}

result = BUILDERS.get(target_part, cover_half_part)()
