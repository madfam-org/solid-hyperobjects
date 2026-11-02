# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/disc_media.py — an optical or magnetic disc, and its shell.

Components (plan §2.3, Media interfaces): `revolved_disc`, `disc_shell_outline`,
`disc_shell_boss`, `disc_pocket`, `disc_window`, `disc_read_slot`,
`disc_shutter_track`, `disc_shutter_plate`. First used by `disc-media`
(2026-11-01); a console's `disc_tray` / `disc_lid`, a jewel or keep case's hub
and a caddy consume what these build.

THE FRAME, the keystone standard parts' own (`optical-disc-cd-120mm`,
`umd-cartridge`):

    disc   origin at the centre of the centre hole, on the read-out side; the disc
           lies in XY and +Z runs through it to the label side
    shell  origin at the centre of the shell's width x length bounding rectangle;
           the shell occupies z from 0 (the read-out face) upward; +Y points toward
           the edge nearest the disc ("top")

A disc is ONE revolved profile: drawn on Workplane("XZ") (local x = radius, local
y = global Z) and revolved about local (0, 1, 0), i.e. the global Z axis — the
commons' revolve-axis rule (an upright solid of revolution, never a fan). Every
cutter overshoots its face by DISC_OVERSHOOT.

Each component takes its OWN parameter dict, reads no manifest global and knows
no assembly. Inlined, never imported: `tools/inline_parts.py` copies this text
into every family `main.py` that declares it (ruling R2 on gate H8).
"""

import math

import cadquery as cq

#: Every cutter passes this far beyond the face it opens (the gotchas canon: >= 1 mm).
DISC_OVERSHOOT = 1.0
#: How far a fused feature (the shell's boss) bites into the solid it joins.
DISC_BITE = 0.2


def revolved_disc(p):
    """A disc: an annulus with an optional clamp-zone relief and stacking ring.

    CDG exposed: `centre_hole` and `outline` — the two interface ids the keystone's
    optical-disc standard parts declare, so a spindle, a tray or a case hub sized
    from the standard fits this disc. The body runs z = 0 (read-out side) to
    `thickness`. The clamp-zone relief lowers the label side between the clamp
    diameters by `clamp_relief`; the stacking ring stands `ring_height` proud of the
    label side from `clamp_outer` outward for `ring_width`. A zero relief, ring or
    hole is left out (no degenerate edge).

    p: diameter, hole, thickness, clamp_inner, clamp_outer, clamp_relief,
       ring_width, ring_height
    """
    r_out, r_hole, t = p["diameter"] / 2.0, max(p["hole"], 0.0) / 2.0, p["thickness"]
    rci, rco = p["clamp_inner"] / 2.0, p["clamp_outer"] / 2.0
    rel, rh = p["clamp_relief"], p["ring_height"]
    rri, rro = rco, rco + p["ring_width"]
    top = [(r_out, t)]
    if rh > 0:
        top += [(rro, t), (rro, t + rh), (rri, t + rh)]
        if rel > 0:
            top += [(rri, t - rel), (rci, t - rel), (rci, t)]
        else:
            top += [(rri, t)]
    elif rel > 0:
        top += [(rco, t), (rco, t - rel), (rci, t - rel), (rci, t)]
    top += [(r_hole, t)]
    pts = [(r_hole, 0.0), (r_out, 0.0)] + top
    return cq.Workplane("XZ").polyline(pts).close().revolve(360.0, (0, 0, 0), (0, 1, 0))


def disc_shell_outline(p):
    """The shell's plan outline extruded to its thickness.

    CDG exposed: `media_envelope` (with the boss). `rounded_rect` is a rectangle
    with rounded corners; `arched` is the UMD-type outline the ECMA-365 figure
    describes: a top arc about the disc (radius `top_arc_radius`, its crown on the
    top edge), straight sides, a shallower bottom arc (`bottom_arc_radius`, its
    lowest point on the bottom edge) and rounded bottom corners. The outline is
    one 2-D wire (lines and three-point arcs), so no tangent solids are booleaned.

    p: shape ("rounded_rect"|"arched"), width, length, thickness, corner_radius,
       top_arc_radius, bottom_arc_radius
    """
    w, length, t = p["width"], p["length"], p["thickness"]
    hw, hl = w / 2.0, length / 2.0
    if str(p["shape"]) == "arched":
        r1 = max(p["top_arc_radius"], hw)
        r2 = max(p["bottom_arc_radius"], hw + 0.01)
        y_top = (hl - r1) + math.sqrt(r1 * r1 - hw * hw)
        y_bot = (-hl + r2) - math.sqrt(r2 * r2 - hw * hw)
        body = (
            cq.Workplane("XY")
            .moveTo(hw, y_bot)
            .lineTo(hw, y_top)
            .threePointArc((0.0, hl), (-hw, y_top))
            .lineTo(-hw, y_bot)
            .threePointArc((0.0, -hl), (hw, y_bot))
            .close()
            .extrude(t)
        )
        r = p["corner_radius"]
        if r > 0.05:
            box = cq.selectors.BoxSelector((-hw - 1.0, -hl - 1.0, -1.0), (hw + 1.0, y_bot + 0.01, t + 1.0))
            body = body.edges("|Z").edges(box).fillet(r)
        return body
    body = cq.Workplane("XY").box(w, length, t).translate((0.0, 0.0, t / 2.0))
    r = min(p["corner_radius"], hw - 0.01, hl - 0.01)
    if r > 0.05:
        body = body.edges("|Z").fillet(r)
    return body


def disc_shell_boss(p):
    """A low circular boss on the shell's label face, about the disc centre.

    CDG exposed: `media_envelope` (it sets the shell's maximum thickness). It bites
    DISC_BITE into the face it stands on.

    p: diameter, height, center_y, face_z
    """
    span = p["height"] + DISC_BITE
    return (
        cq.Workplane("XY")
        .cylinder(span, p["diameter"] / 2.0)
        .translate((0.0, p["center_y"], p["face_z"] - DISC_BITE + span / 2.0))
    )


def disc_pocket(p):
    """The void the disc turns in: a cylinder about the disc centre. A cutter.

    p: diameter, height, center_y, center_z
    """
    return (
        cq.Workplane("XY")
        .cylinder(p["height"], p["diameter"] / 2.0)
        .translate((0.0, p["center_y"], p["center_z"]))
    )


def disc_window(p):
    """The label-side window that shows the disc: a rectangle cut from the pocket out.

    CDG exposed: `disc_window`. Runs from the pocket's mid-plane to DISC_OVERSHOOT
    beyond the highest face (`top_z`), so it always opens the pocket.

    p: width, length, center_y, from_z, top_z
    """
    span = p["top_z"] + DISC_OVERSHOOT - p["from_z"]
    return (
        cq.Workplane("XY")
        .box(p["width"], p["length"], span)
        .translate((0.0, p["center_y"], p["from_z"] + span / 2.0))
    )


def disc_read_slot(p):
    """The read-out face's openings: the spindle hole and the radial head slot.

    CDG exposed: `read_window` (where a drive's spindle and head reach the disc).
    Both run from DISC_OVERSHOOT below the read-out face (z = 0) to `to_z`.

    p: spindle_diameter, slot_width, slot_length, slot_center_y, disc_center_y, to_z
    """
    span = p["to_z"] + DISC_OVERSHOOT
    zc = -DISC_OVERSHOOT + span / 2.0
    spindle = (
        cq.Workplane("XY")
        .cylinder(span, p["spindle_diameter"] / 2.0)
        .translate((0.0, p["disc_center_y"], zc))
    )
    slot = (
        cq.Workplane("XY")
        .box(p["slot_width"], p["slot_length"], span)
        .translate((0.0, p["slot_center_y"], zc))
    )
    return spindle.union(slot)


def disc_shutter_track(p):
    """The shallow track the shutter slides in, cut into the read-out face. A cutter.

    It spans the closed shutter plus its full travel in +X.

    p: width (the plate's, closed), length, center_y, travel, depth
    """
    x0, x1 = -p["width"] / 2.0, p["width"] / 2.0 + p["travel"]
    span = p["depth"] + DISC_OVERSHOOT
    return (
        cq.Workplane("XY")
        .box(x1 - x0, p["length"], span)
        .translate(((x0 + x1) / 2.0, p["center_y"], -DISC_OVERSHOOT + span / 2.0))
    )


def disc_shutter_plate(p):
    """The shutter: a plate in the track over the head slot, slid `offset` in +X.

    CDG exposed: `media_shutter` (the door a drive's cam opens). It sits `lift`
    above the read-out face, inside the track, so it never shares a face with the
    shell.

    p: width, length, thickness, center_y, offset, lift
    """
    return (
        cq.Workplane("XY")
        .box(p["width"], p["length"], p["thickness"])
        .translate((p["offset"], p["center_y"], p["lift"] + p["thickness"] / 2.0))
    )
