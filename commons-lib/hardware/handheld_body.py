# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/handheld_body.py — the one-piece body of a slab handheld.

Components (plan §2.3, Structure, Media interfaces, Connectors and seats):
`slab_body` (`device_envelope`, `cradle_seat`), `media_slot` (consumes
`media_envelope`, exposes `media_slot`), `media_proxy`, `battery_bay` and
`battery_door` (`battery_bay`, sized from the AA/AAA standard parts),
`side_rail` (`rail`), `kickstand` + `kickstand_recess` (`revolute_axis`),
`edge_port` (`port_cutout` on a top or bottom edge), `rear_recess`,
`half_space` (the front/rear shell split). Every one takes its OWN parameter
dict, reads no manifest global and knows no assembly. First authored for
`slab-handheld` (2026-11-01).

THE FRAME every component here assumes (a device held face-on):

    X  across the face, centred on x = 0          (the maker's "width")
    Z  up the face; the device stands on z = 0    (the maker's "height")
    Y  through the device; the face is the plane y = 0, the rear is +Y
                                                    (the maker's "depth")

Tools built in the XY convention of `displays` and `controls` (a box whose Z
extent is the recess depth) are turned onto the face with `face_tool`.

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import math

import cadquery as cq

#: Every cutter here runs at least this far past the face it opens through.
HANDHELD_OVERSHOOT = 1.0
#: A span larger than any handheld: the half-space boxes and the crown cylinder.
HANDHELD_FAR = 2000.0


def face_tool(shape):
    """Turn an XY-convention tool onto the front face (a +90 degree turn about X).

    A tool built at (cx, cy, cz) lands at (cx, -cz, cy): pass the face position
    as (center_x, center_y) and minus the tool's Y centre as `cut_center_z`.
    """
    return shape.rotate((0, 0, 0), (1, 0, 0), 90)


def face_cut_center(depth):
    """`cut_center_z` for a face recess `depth` deep with the overshoot in front."""
    return -(depth - HANDHELD_OVERSHOOT) / 2.0


def slab_depth(p):
    """The thickness of the face slab: the whole depth unless grips carry the rest."""
    if p["grip_count"] > 0:
        return min(p["face_depth"], p["depth"])
    return p["depth"]


def slab_bottom(p):
    """Where the slab's lower edge sits: grips may drop below it to z = 0."""
    return p["grip_drop"] if p["grip_count"] > 0 else 0.0


def rear_y(p, x):
    """The crowned rear surface's y at a distance |x| from the centre line.

    The crown is a circular arc across X whose sagitta at the side faces is
    `back_crown`; with no crown the rear is the plane y = slab_depth.
    """
    d = slab_depth(p)
    s = p["back_crown"]
    if s <= 0:
        return d
    hw = p["width"] / 2.0
    radius = (hw * hw + s * s) / (2.0 * s)
    x = min(abs(x), hw)
    return d - radius + math.sqrt(radius * radius - x * x)


def slab_body(p):
    """The device body: a rounded face slab, a crowned back, optional rear grips.

    CDG exposed: `device_envelope` (its bounding box is the published
    width x depth x height, grips included) and `cradle_seat` (the bottom edge
    and the rear, which a stand, a dock or a mount registers against).

    The slab is a box with its face outline rounded (`corner_radius`), cut once
    by a crown cylinder; each grip is a separate rounded block fused once, deep
    into the slab (branch-first union order, never a coincident join only).

    p: width, height, depth, face_depth, corner_radius, back_crown,
       grip_count (0 or 2), grip_width, grip_length, grip_drop, grip_radius,
       grip_front_y
    """
    w, h = p["width"], p["height"]
    d = slab_depth(p)
    z0 = slab_bottom(p)
    body = (
        cq.Workplane("XY")
        .box(w, d, h - z0)
        .translate((0.0, d / 2.0, z0 + (h - z0) / 2.0))
        .edges("|Y")
        .fillet(p["corner_radius"])
    )
    s = p["back_crown"]
    if s > 0:
        hw = w / 2.0
        radius = (hw * hw + s * s) / (2.0 * s)
        crown = (
            cq.Workplane("XY")
            .cylinder(h + 2.0 * HANDHELD_OVERSHOOT, radius)
            .translate((0.0, d - radius, h / 2.0))
        )
        body = body.intersect(crown)
    if p["grip_count"] > 0:
        gw, gl = p["grip_width"], p["grip_length"]
        gy = p["grip_front_y"]
        gd = p["depth"] - gy
        for side in (-1.0, 1.0):
            grip = (
                cq.Workplane("XY")
                .box(gw, gd, gl)
                .translate((side * (w / 2.0 - gw / 2.0), gy + gd / 2.0, gl / 2.0))
                .edges("|Y")
                .fillet(p["grip_radius"])
            )
            body = body.union(grip)
    return body


def half_space(p):
    """A box filling everything in front of (or behind) the shell seam.

    The front and rear shells are the carved body intersected with these; the
    seam is the plane y = seam_y, never a face of any feature.

    p: side ("front"|"rear"), seam_y
    """
    far = HANDHELD_FAR
    y = p["seam_y"] - far / 2.0 if p["side"] == "front" else p["seam_y"] + far / 2.0
    return cq.Workplane("XY").box(far, far, far).translate((0.0, y, 0.0))


def media_slot(p):
    """The cavity a plug-in medium enters, as a cutting tool.

    CDG consumed: `media_envelope` (plug-in-media's plain outer hull, X width,
    Z height, Y thickness); exposed: `media_slot`. The cavity is the medium's
    envelope plus `clearance` on every side, `insert_depth` deep.

      slot_top    a mouth in the top edge, closed behind (centre_y given)
      slot_bottom a mouth in the bottom edge (face_z is the bottom's z)
      cart_rear   a notch open through the top edge AND the rear: the medium's
                  back stands at `open_y`, the shallowest rear point over it
      umd_rear    a bay in the rear face; the medium lies flat in it

    p: kind, width, height, thickness, clearance, insert_depth, center_x,
       center_y, center_z, face_z, open_y, back_y
    """
    c, ov = p["clearance"], HANDHELD_OVERSHOOT
    w, t = p["width"] + 2.0 * c, p["thickness"] + 2.0 * c
    kind = p["kind"]
    if kind == "umd_rear":
        y0, y1 = p["open_y"] - p["thickness"] - c, p["back_y"] + ov
        return (
            cq.Workplane("XY")
            .box(w, y1 - y0, p["height"] + 2.0 * c)
            .translate((p["center_x"], (y0 + y1) / 2.0, p["center_z"]))
        )
    if kind == "slot_bottom":
        z0, z1 = -ov, p["face_z"] + p["insert_depth"] + c
    else:
        z0, z1 = p["face_z"] - p["insert_depth"] - c, p["face_z"] + ov
    if kind == "cart_rear":
        y0, y1 = p["open_y"] - t, p["back_y"] + ov
    else:
        y0, y1 = p["center_y"] - t / 2.0, p["center_y"] + t / 2.0
    return (
        cq.Workplane("XY")
        .box(w, y1 - y0, z1 - z0)
        .translate((p["center_x"], (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    )


def media_proxy(p):
    """The medium's envelope, placed in its `media_slot` (a fit proxy, not media).

    `insert` 1 is seated (a `clearance` gap on every side, so it never touches
    the body); 0 is withdrawn just clear of the mouth along the insertion axis.

    p: the `media_slot` dict plus insert
    """
    c = p["clearance"]
    w, hgt, t = p["width"], p["height"], p["thickness"]
    kind = p["kind"]
    if kind == "umd_rear":
        out = (1.0 - p["insert"]) * (t + 2.0)
        y0 = p["open_y"] - t + out
        return (
            cq.Workplane("XY")
            .box(w, t, hgt)
            .translate((p["center_x"], y0 + t / 2.0, p["center_z"]))
        )
    travel = (1.0 - p["insert"]) * (p["insert_depth"] + 2.0)
    if kind == "slot_bottom":
        z_mid = p["face_z"] + p["insert_depth"] - hgt / 2.0 - travel
    else:
        z_mid = p["face_z"] - p["insert_depth"] + hgt / 2.0 + travel
    if kind == "cart_rear":
        y_mid = p["open_y"] - c - t / 2.0
    else:
        y_mid = p["center_y"]
    return (
        cq.Workplane("XY")
        .box(w, t, hgt)
        .translate((p["center_x"], y_mid, z_mid))
    )


def cell_bay_size(p):
    """(bay_width X, bay_height Z, bay_depth Y) for `count` cylindrical cells.

    The cell figures are the keystone standard parts' maximum diameter and
    height (`cell-aa`, `cell-aaa`). axis "x": each cell lies across X and they
    stack up Z; axis "z": each stands up Z and they sit side by side in X.

    p: diameter, length, count, axis, clearance
    """
    dia, ln, n, c = p["diameter"], p["length"], p["count"], p["clearance"]
    along = ln + 2.0 * c
    across = n * (dia + c) + c
    depth = dia + c
    if p["axis"] == "z":
        return across, along, depth
    return along, across, depth


def battery_bay(p):
    """The door recess and the cell trough behind it, as one cutting tool.

    CDG exposed: `battery_bay`. The door recess is the bay footprint plus
    `door_lip` all round, `door_thickness` deep from `open_y` (the shallowest
    rear point over it); the trough is `bay_depth` deeper still. A bay_depth of
    0 leaves the recess alone: the cover of a service opening.

    p: bay_width, bay_height, bay_depth, door_lip, door_thickness,
       center_x, center_z, open_y, back_y
    """
    lip, dt = p["door_lip"], p["door_thickness"]
    y_door = p["open_y"] - dt
    y1 = p["back_y"] + HANDHELD_OVERSHOOT
    tool = (
        cq.Workplane("XY")
        .box(p["bay_width"] + 2.0 * lip, y1 - y_door, p["bay_height"] + 2.0 * lip)
        .translate((p["center_x"], (y_door + y1) / 2.0, p["center_z"]))
    )
    if p["bay_depth"] > 0:
        y0 = y_door - p["bay_depth"]
        trough = (
            cq.Workplane("XY")
            .box(p["bay_width"], y_door - y0 + 0.5, p["bay_height"])
            .translate((p["center_x"], (y0 + y_door + 0.5) / 2.0, p["center_z"]))
        )
        tool = tool.union(trough)
    return tool


def battery_door(p):
    """The door that closes a `battery_bay`, seated in its recess.

    It is the recess less `door_clearance` on every side and below, so it never
    touches the body; its outer face is the rear's shallowest point.

    p: bay_width, bay_height, door_lip, door_thickness, door_clearance,
       center_x, center_z, open_y
    """
    lip, dt, dc = p["door_lip"], p["door_thickness"], p["door_clearance"]
    w = p["bay_width"] + 2.0 * lip - 2.0 * dc
    h = p["bay_height"] + 2.0 * lip - 2.0 * dc
    t = dt - dc
    return (
        cq.Workplane("XY")
        .box(w, t, h)
        .translate((p["center_x"], p["open_y"] - t / 2.0, p["center_z"]))
    )


def side_rail(p):
    """The two attachment grooves in the side faces, as one cutting tool.

    CDG exposed: `rail` — what a detachable controller half slides along
    (`controller_attach` "rail") or seats against (a shallow pad for
    "magnetic"). An L2 rectangular groove, not the maker's profile.

    p: length, width, depth, center_y, center_z, half_width
    """
    ov = HANDHELD_OVERSHOOT
    span = p["depth"] + ov
    tool = None
    for side in (-1.0, 1.0):
        x = side * (p["half_width"] - p["depth"] + span / 2.0)
        groove = (
            cq.Workplane("XY")
            .box(span, p["width"], p["length"])
            .translate((x, p["center_y"], p["center_z"]))
        )
        tool = groove if tool is None else tool.union(groove)
    return tool


def kickstand_recess(p):
    """The pocket in the rear the closed kickstand lies in.

    p: width, height, thickness, clearance, center_x, top_z, hinge_y, back_y
    """
    c = p["clearance"]
    y0 = p["hinge_y"] - p["thickness"] / 2.0 - c
    y1 = p["back_y"] + HANDHELD_OVERSHOOT
    z0, z1 = p["top_z"] - p["height"] - c, p["top_z"] + c
    return (
        cq.Workplane("XY")
        .box(p["width"] + 2.0 * c, y1 - y0, z1 - z0)
        .translate((p["center_x"], (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    )


def kickstand(p):
    """A kickstand plate on a hinge barrel, turned out by `angle` degrees.

    CDG exposed: `revolute_axis` (the barrel, parallel to X through
    (hinge_y, top_z)). 0 lies closed in its recess; a positive angle swings the
    lower edge out behind the device. The barrel's radius is half the plate
    plus `bite`, more than the recess clearance, so it fuses into the body
    above the recess at every angle: one body with the rear shell.

    p: width, height, thickness, bite, center_x, top_z, hinge_y, angle
    """
    t = p["thickness"]
    plate = (
        cq.Workplane("XY")
        .box(p["width"], t, p["height"])
        .translate((p["center_x"], p["hinge_y"], p["top_z"] - p["height"] / 2.0))
    )
    barrel = (
        cq.Workplane("XY")
        .cylinder(p["width"], t / 2.0 + p["bite"])
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((p["center_x"], p["hinge_y"], p["top_z"]))
    )
    axis_a = (0.0, p["hinge_y"], p["top_z"])
    axis_b = (1.0, p["hinge_y"], p["top_z"])
    return plate.union(barrel).rotate(axis_a, axis_b, p["angle"])


def edge_port(p):
    """A connector opening in the top or bottom edge, as a cutting tool.

    CDG exposed: `port_cutout`. `shape` "rect" (width across X, height across Y)
    or "round" (radius); it bores `depth` into the body from the edge at
    `face_z`, from below every grip for the bottom edge.

    p: shape, edge ("top"|"bottom"), width, height, radius, depth,
       center_x, center_y, face_z
    """
    ov = HANDHELD_OVERSHOOT
    if p["edge"] == "bottom":
        z0, z1 = -ov, p["face_z"] + p["depth"]
    else:
        z0, z1 = p["face_z"] - p["depth"], p["face_z"] + ov
    if p["shape"] == "round":
        tool = cq.Workplane("XY").cylinder(z1 - z0, p["radius"])
    else:
        tool = cq.Workplane("XY").box(p["width"], p["height"], z1 - z0)
    return tool.translate((p["center_x"], p["center_y"], (z0 + z1) / 2.0))


def rear_recess(p):
    """A rectangular pocket in the rear (a rear button seat), as a cutting tool.

    CDG exposed: `button_seat` on the rear. It runs `depth` in from `open_y`
    and out past `back_y`, so it opens through a grip as readily as the slab.

    p: width, height, depth, center_x, center_z, open_y, back_y
    """
    y0, y1 = p["open_y"] - p["depth"], p["back_y"] + HANDHELD_OVERSHOOT
    return (
        cq.Workplane("XY")
        .box(p["width"], y1 - y0, p["height"])
        .translate((p["center_x"], (y0 + y1) / 2.0, p["center_z"]))
    )
