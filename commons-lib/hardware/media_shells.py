# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/media_shells.py — a contact-edge medium: shell, board, cuts.

Components (plan §2.3, Media interfaces and Connectors): `media_shell_outer`,
`media_shell_cavity`, `contact_window`, `contact_pocket`, `edge_connector_board`,
`label_recess`, `grip_ridges`, `keying_notches`, `shutter_outline`,
`pass_through_mouth`, plus the pose helper `media_place`. First used by
`plug-in-media` (2026-11-01); a `home-console` `media_slot`, a `keep-case`
pocket and `media-caddy` consume the envelope these build.

THE CANONICAL FRAME every component here is written in:

    X  across the contact edge, centred on x = 0
    Y  through the shell, centred on y = 0 (the front, label face is -Y)
    Z  away from the contact edge: the contact edge is z = 0, the far edge z = height

`media_place` turns that frame into the family's (a contact edge on the label's
bottom, top or side edge) and applies the insertion travel. Every cutter returned
here overshoots the face it opens by MEDIA_OVERSHOOT, so no cut ends on a face.

Each component takes its OWN parameter dict, reads no manifest global and knows
no assembly. Inlined, never imported: `tools/inline_parts.py` copies this text
into every family `main.py` that declares it (ruling R2 on gate H8).
"""

import cadquery as cq

#: Every cutter passes this far beyond the face it opens (the gotchas canon: >= 1 mm).
MEDIA_OVERSHOOT = 1.0
#: How far a fused feature (a pad, a tongue) bites into the solid it joins.
MEDIA_BITE = 0.2
#: How far a contact pad stands proud of its board.
MEDIA_PAD_PROUD = 0.04


def _rounded_slab(width, height, thickness, radius):
    """A width x thickness x height slab standing on z = 0, its four |Y edges rounded."""
    slab = cq.Workplane("XY").box(width, thickness, height).translate((0.0, 0.0, height / 2.0))
    r = min(radius, width / 2.0 - 0.01, height / 2.0 - 0.01)
    if r > 0.05:
        slab = slab.edges("|Y").fillet(r)
    return slab


def media_shell_outer(p):
    """The shell's outer hull: a rounded slab, plus a thicker grip band at the far edge.

    CDG exposed: `media_envelope` — the fit surface a console's media slot, a keep
    case's pocket and a media caddy consume (plus their own clearance). The band
    shares the slab's outline exactly, so the hull is the slab's outline at
    max(thickness, grip_thickness) through the band and nothing else.

    p: width, height, thickness, corner_radius, grip_thickness, grip_height
       (grip_thickness <= thickness, or grip_height <= 0, means no band)
    """
    w, h, t = p["width"], p["height"], p["thickness"]
    hull = _rounded_slab(w, h, t, p["corner_radius"])
    gt, gh = p["grip_thickness"], p["grip_height"]
    if gt > t and gh > 0:
        band = _rounded_slab(w, h, gt, p["corner_radius"]).intersect(
            cq.Workplane("XY")
            .box(w + 2.0 * MEDIA_OVERSHOOT, gt + 2.0 * MEDIA_OVERSHOOT, gh + MEDIA_OVERSHOOT)
            .translate((0.0, 0.0, h - gh / 2.0 + MEDIA_OVERSHOOT / 2.0))
        )
        hull = hull.union(band).clean()
    return hull


def media_shell_cavity(p):
    """The void a hollow shell keeps for its board: the hull offset inward by the wall.

    No CDG id: it is what `edge_connector_board` lives in. Its corners are rounded
    concentrically with the hull's (radius minus wall), so the wall is uniform and a
    sharp inner corner can never break through a rounded outer one.

    p: width, height, thickness, wall, corner_radius
    """
    wall = p["wall"]
    w, h, t = p["width"] - 2.0 * wall, p["height"] - 2.0 * wall, p["thickness"] - 2.0 * wall
    return _rounded_slab(w, h, t, p["corner_radius"] - wall).translate((0.0, 0.0, wall))


def contact_window(p):
    """The opening in a hollow shell's contact edge that exposes the board's edge.

    CDG exposed: `edge_connector` (the mouth a slot's connector enters). It is cut
    through the cavity's thickness only, so the walls either side stay whole.

    p: width, depth (into the shell, from the contact edge), thickness (in Y)
    """
    span = p["depth"] + MEDIA_OVERSHOOT
    return (
        cq.Workplane("XY")
        .box(p["width"], p["thickness"], span)
        .translate((0.0, 0.0, span / 2.0 - MEDIA_OVERSHOOT))
    )


def contact_pocket(p):
    """A monolithic card's contact field: a shallow pocket in the back face at the edge.

    CDG exposed: `edge_connector`. Open at the contact edge and at the back face.

    p: width, depth (from the contact edge), recess (into the back face), face_y
    """
    span_z = p["depth"] + MEDIA_OVERSHOOT
    span_y = p["recess"] + MEDIA_OVERSHOOT
    return (
        cq.Workplane("XY")
        .box(p["width"], span_y, span_z)
        .translate((0.0, p["face_y"] - p["recess"] + span_y / 2.0, span_z / 2.0 - MEDIA_OVERSHOOT))
    )


def edge_connector_board(p):
    """The board: a main panel, a tongue that reaches the contact edge, and contact pads.

    CDG exposed: `edge_connector` (the contact fingers a slot's connector grips).
    The tongue bites MEDIA_BITE into the panel; each pad bites MEDIA_BITE into the
    tongue and stands MEDIA_PAD_PROUD proud of it, so the board is one body. All pads
    on one face are one 2-D region extruded once. A panel with top <= bottom is left
    out (a card's contact plate is a tongue alone).

    p: thickness, center_y,
       panel_width, panel_bottom, panel_top,
       tongue_width, tongue_bottom, tongue_top,
       front_contacts, back_contacts, pitch, pad_length, pad_inset
    """
    t, cy = p["thickness"], p["center_y"]

    def plate(width, bottom, top):
        return (
            cq.Workplane("XY")
            .box(width, t, top - bottom)
            .translate((0.0, cy, (top + bottom) / 2.0))
        )

    board = plate(p["tongue_width"], p["tongue_bottom"], p["tongue_top"])
    if p["panel_top"] > p["panel_bottom"]:
        board = plate(p["panel_width"], p["panel_bottom"], p["panel_top"]).union(board)
    z0 = p["tongue_bottom"] + p["pad_inset"] + p["pad_length"] / 2.0
    for count, side in ((p["front_contacts"], -1.0), (p["back_contacts"], 1.0)):
        if count <= 0 or p["pad_length"] <= 0:
            continue
        pts = [((i - (count - 1) / 2.0) * p["pitch"], z0) for i in range(count)]
        # Workplane("XZ") extrudes toward -Y, so each face starts from its outer side.
        start = cy + t / 2.0 + MEDIA_PAD_PROUD if side > 0 else cy - t / 2.0 + MEDIA_BITE
        pads = (
            cq.Workplane("XZ", origin=(0.0, start, 0.0))
            .pushPoints(pts)
            .rect(0.6 * p["pitch"], p["pad_length"])
            .extrude(MEDIA_BITE + MEDIA_PAD_PROUD)
        )
        board = board.union(pads)
    return board


def label_recess(p):
    """A label recess in one face: a flat pocket the label sits in. Never artwork.

    CDG exposed: `label_recess` (what a label printer or a die-cut label is sized to).
    The cutter runs from `depth` below the face to MEDIA_OVERSHOOT beyond the
    THICKEST face (`outer_y`), so where it crosses a grip band it cuts the band down
    to the same floor instead of leaving a closed void.

    p: width, height, depth, center_x, center_z, face_y (signed: -T/2 front, +T/2
       back), outer_y (signed, |outer_y| >= |face_y|)
    """
    side = 1.0 if p["face_y"] > 0 else -1.0
    inner = p["face_y"] - side * p["depth"]
    outer = p["outer_y"] + side * MEDIA_OVERSHOOT
    return (
        cq.Workplane("XY")
        .box(p["width"], abs(outer - inner), p["height"])
        .translate((p["center_x"], (inner + outer) / 2.0, p["center_z"]))
    )


def grip_ridges(p):
    """Generic grip grooves across both faces near the far edge. Not a maker's pattern.

    No CDG id (a grip is a surface, not a mating feature). Every groove of a face is
    one 2-D region extruded once; grooves run the full width and out of both sides.

    p: count, pitch, depth, groove_width, first_z (the groove nearest the far edge),
       width (shell), face_y (the |y| of the face they are cut in)
    """
    pts = [(0.0, p["first_z"] - i * p["pitch"]) for i in range(p["count"])]
    span = p["depth"] + MEDIA_OVERSHOOT
    out = None
    for start in (p["face_y"] + MEDIA_OVERSHOOT, -p["face_y"] + p["depth"]):
        grooves = (
            cq.Workplane("XZ", origin=(0.0, start, 0.0))
            .pushPoints(pts)
            .rect(p["width"] + 2.0 * MEDIA_OVERSHOOT, p["groove_width"])
            .extrude(span)
        )
        out = grooves if out is None else out.union(grooves)
    return out


def keying_notches(p):
    """Rectangular keying notches in the side edges, through the whole thickness.

    CDG exposed: `media_key` (what a slot's key tab registers against). One notch is
    cut in the -X edge; two cut both edges.

    p: count (1|2), width (along Z), depth (into the shell, along X), offset (from the
       contact edge to the notch's near side), shell_width, thickness (the thickest)
    """
    out = None
    for side in ((-1.0,) if p["count"] == 1 else (-1.0, 1.0)):
        span = p["depth"] + MEDIA_OVERSHOOT
        cut = (
            cq.Workplane("XY")
            .box(span, p["thickness"] + 2.0 * MEDIA_OVERSHOOT, p["width"])
            .translate((
                side * (p["shell_width"] / 2.0 - p["depth"] + span / 2.0),
                0.0,
                p["offset"] + p["width"] / 2.0,
            ))
        )
        out = cut if out is None else out.union(cut)
    return out


def shutter_outline(p):
    """A shutter door's outline: a closed rectangular groove in the back face.

    CDG exposed: `media_shutter` (the door a slot's cam opens). The door itself is
    the shell material the ring encloses: a fit envelope, not a moving part.

    p: width, height, bottom (from the contact edge), gap (groove width), depth,
       face_y (the back face, > 0)
    """
    cz = p["bottom"] + p["height"] / 2.0
    start = p["face_y"] + MEDIA_OVERSHOOT
    return (
        cq.Workplane("XZ", origin=(0.0, start, 0.0))
        .center(0.0, cz)
        .rect(p["width"] + 2.0 * p["gap"], p["height"] + 2.0 * p["gap"])
        .rect(p["width"], p["height"])
        .extrude(p["depth"] + MEDIA_OVERSHOOT)
    )


def pass_through_mouth(p):
    """The slot in the far edge that takes a second medium (a lock-on, a pass-through).

    CDG exposed: `pass_through_slot` (it CONSUMES another medium's `media_envelope`).

    p: width, thickness, depth (down from the far edge), shell_height
    """
    span = p["depth"] + MEDIA_OVERSHOOT
    return (
        cq.Workplane("XY")
        .box(p["width"], p["thickness"], span)
        .translate((0.0, 0.0, p["shell_height"] - p["depth"] + span / 2.0))
    )


def media_place(shape, p):
    """Turn the canonical frame into the family's, then apply the insertion travel.

    Not a component (no CDG id): the pose. `insertion_edge` names the label edge
    that carries the contacts. "bottom" is the canonical frame. "top" turns it 180
    degrees about Y. "side" turns it -90 degrees about Y, so the contact edge lands
    on +X, and the canonical shell was built `height` wide and `width` tall. Y is
    never turned, so the label face stays -Y. `travel` moves the shell along its
    insertion direction (toward the contact edge), for a kit's insert pose.

    p: insertion_edge ("bottom"|"top"|"side"), width, height (the family's, final),
       travel
    """
    edge, h, travel = str(p["insertion_edge"]), p["height"], p["travel"]
    if edge == "top":
        shape = shape.rotate((0.0, 0.0, h / 2.0), (0.0, 1.0, h / 2.0), 180.0)
        return shape.translate((0.0, 0.0, travel))
    if edge == "side":
        hc = p["width"]
        shape = shape.rotate((0.0, 0.0, hc / 2.0), (0.0, 1.0, hc / 2.0), -90.0)
        return shape.translate((travel, 0.0, h / 2.0 - hc / 2.0))
    return shape.translate((0.0, 0.0, -travel))
