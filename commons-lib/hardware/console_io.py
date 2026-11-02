# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: console_shell
"""commons-lib/hardware/console_io.py — what a desktop device takes in and plugs into.

Components (plan §2.3, Media interfaces and Connectors): `media_cartridge_slot`
(the plan's `cartridge_slot`, consuming a `media_envelope`; renamed because
`connectors.cartridge_slot` already exists and module names may not collide),
`card_slot`, `disc_lid` + `disc_lid_seat`, `disc_tray` + `disc_tray_bay`,
`slot_loader`, `slot_door`, `slot_blank`, `slide_switch`, `controller_port`,
`port_row`.

Every component is built in a FACE FRAME (`console_shell.face_plane`): local X
along the face, local Y up the face, local +Z outward. A tool spans
`overshoot` outside the frame's plane to `depth` inside it, so no cut ends on a
face. Solids (a lid, a tray, a door) are returned already posed. Each takes its
OWN parameter dict, reads no manifest global and knows no assembly.

Opening sizes for connector kinds are ARCHETYPE constants (below): clearance
openings, never a connector's drawing. The keystone's standard parts
(`dsub-de9-female`, `hdmi-type-a-receptacle`, …) are the facts a later
revision reads once `SPEC_PIN` carries them.

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import math

import cadquery as cq

#: Controller-port clearance openings (width, height) in mm. Archetype.
CONTROLLER_PORT_OPENINGS = {
    "de9": (19.0, 10.5),
    "round_din": (13.0, 13.0),
    "proprietary": (16.0, 9.0),
    "usb_a": (13.4, 6.0),
}
#: Rear-panel clearance openings (shape, width, height) in mm, per kind. Archetype.
PORT_OPENINGS = {
    "rf_f": ("round", 9.5, 9.5), "rca": ("round", 8.5, 8.5),
    "multi_av": ("rect", 32.0, 7.0), "hdmi": ("rect", 15.0, 6.0),
    "cord": ("round", 7.0, 7.0), "barrel": ("round", 9.0, 9.0),
    "iec_c7": ("rect", 11.0, 6.5), "iec_c8": ("rect", 11.0, 6.5),
    "iec_c13": ("rect", 28.0, 20.0), "proprietary": ("rect", 12.0, 8.0),
    "ethernet": ("rect", 16.0, 13.5), "usb_a": ("rect", 13.4, 6.0),
    "expansion": ("rect", 40.0, 8.0),
}
#: Thickness of an optical disc (CD/DVD/BD, ISO/IEC 10149 and successors).
DISC_THICKNESS = 1.2


def _box_tool(plane, w, h, depth, overshoot, u=0.0, v=0.0):
    return (
        cq.Workplane(plane).workplane(offset=overshoot).center(u, v)
        .rect(w, h).extrude(-(depth + overshoot))
    )


def media_cartridge_slot(p):
    """A cartridge mouth sized from the medium it takes (the tool).

    CDG consumed: `media_envelope` (the `plug-in-media` family's shell width x
    thickness x insertion depth). CDG exposed: `media_slot` = that envelope plus
    `clearance` on every side; the cavity is `insert_depth + clearance` deep.

    p: frame, media_width, media_thickness, insert_depth, clearance, overshoot,
       extra_depth (the face's own variation over the footprint)
    """
    c = p["clearance"]
    return _box_tool(face_plane(p["frame"]), p["media_width"] + 2 * c,
                     p["media_thickness"] + 2 * c,
                     p["insert_depth"] + c + p["extra_depth"], p["overshoot"])


def card_slot(p):
    """A card slot (a HuCard-type monolithic card, a memory card): a thin mouth
    plus a finger scoop below it, one tool.

    CDG exposed: `media_slot` (card form).

    p: frame, card_width, card_thickness, insert_depth, clearance, scoop_radius,
       overshoot
    """
    plane = face_plane(p["frame"])
    c = p["clearance"]
    mouth = _box_tool(plane, p["card_width"] + 2 * c, p["card_thickness"] + 2 * c,
                      p["insert_depth"] + c, p["overshoot"])
    r = p["scoop_radius"]
    scoop = (
        cq.Workplane(plane).center(0.0, -(p["card_thickness"] / 2.0 + c + r * 0.6))
        .circle(r).extrude(-r * 0.5)
    )
    scoop = scoop.union(cq.Workplane(plane).center(
        0.0, -(p["card_thickness"] / 2.0 + c + r * 0.6)).circle(r).extrude(p["overshoot"]))
    return mouth.union(scoop)


def disc_lid_seat(p):
    """The recess a hinged disc lid closes into, plus the disc well (the tool).

    CDG exposed: `revolute_axis` (the lid's rear edge) — the id `hinge-hyperobject`
    declares. The well is `disc_diameter + 4` across.

    p: frame, lid_diameter, seat_depth, disc_diameter, well_depth, overshoot
    """
    plane = face_plane(p["frame"])
    seat = (
        cq.Workplane(plane).workplane(offset=p["overshoot"]).circle(p["lid_diameter"] / 2.0)
        .extrude(-(p["seat_depth"] + p["overshoot"]))
    )
    well = (
        cq.Workplane(plane).workplane(offset=-p["seat_depth"] + 0.5)
        .circle((p["disc_diameter"] + 4.0) / 2.0).extrude(-(p["well_depth"] + 0.5))
    )
    return seat.union(well)


def disc_lid(p):
    """A round hinged disc lid, posed at `angle` (0 closed, opening upward).

    CDG exposed: `revolute_axis` (local Y = +radius, the rear edge). The lid's top
    is `drop` below the frame plane when closed; `gap` is the running clearance.

    p: frame, lid_diameter, thickness, gap, drop, angle
    """
    plane = face_plane(p["frame"])
    r = p["lid_diameter"] / 2.0 - p["gap"]
    lid = (
        cq.Workplane(plane).workplane(offset=-p["drop"]).circle(r)
        .extrude(-(p["thickness"] - p["gap"]))
    )
    a = plane.toWorldCoords((0.0, r, -p["drop"]))
    b = plane.toWorldCoords((1.0, r, -p["drop"]))
    return lid.rotate(a.toTuple(), b.toTuple(), -p["angle"])


def disc_tray_bay(p):
    """The front opening and cavity a disc tray runs in (the tool).

    CDG exposed: `prismatic_axis` (the frame's normal).

    p: frame, width, height, depth, overshoot
    """
    return _box_tool(face_plane(p["frame"]), p["width"], p["height"], p["depth"],
                     p["overshoot"])


def disc_tray(p):
    """A disc tray, slid out by `extension` x `travel` along the frame normal.

    CDG exposed: `prismatic_axis`; carries a disc pocket on its top face.

    p: frame, width, height, depth, gap, disc_diameter, pocket_depth, extension,
       travel
    """
    plane = face_plane(p["frame"])
    g = p["gap"]
    w, h, d = p["width"] - 2 * g, p["height"] - 2 * g, p["depth"] - g
    tray = cq.Workplane(plane).rect(w, h).extrude(-d)
    # The pocket: a disc-sized cylinder standing on the tray's top face (local +Y).
    top = cq.Plane(origin=plane.toWorldCoords((0.0, h / 2.0, -d / 2.0)),
                   xDir=plane.xDir, normal=plane.yDir)
    pocket = (
        cq.Workplane(top).workplane(offset=1.0).circle((p["disc_diameter"] + 2.0) / 2.0)
        .extrude(-(p["pocket_depth"] + 1.0))
    )
    tray = tray.cut(pocket)
    move = plane.zDir.multiply(p["extension"] * p["travel"])
    return tray.translate(move.toTuple())


def slot_loader(p):
    """A slot-loading disc mouth: a bevelled lip over a disc-wide cavity (the tool).

    CDG exposed: `media_slot` (disc form).

    p: frame, disc_diameter, clearance, depth, overshoot
    """
    plane = face_plane(p["frame"])
    w = p["disc_diameter"] + 2 * p["clearance"]
    h = DISC_THICKNESS + 2 * p["clearance"]
    cavity = _box_tool(plane, w, h, p["depth"], p["overshoot"])
    lip = _box_tool(plane, w + 4.0, h + 2.0, 1.5, p["overshoot"])
    return cavity.union(lip)


def slot_door(p):
    """A hinged door (or a pair of flaps) over a media mouth, posed at `angle`.

    CDG exposed: `revolute_axis` along its +Y edge. `flaps` splits the plate down
    the middle with a groove that stops halfway through, so it stays ONE solid.

    p: frame, kind ("door"|"flaps"), width, height, margin, thickness, angle
    """
    plane = face_plane(p["frame"])
    w, h, t = p["width"] + 2 * p["margin"], p["height"] + 2 * p["margin"], p["thickness"]
    plate = cq.Workplane(plane).rect(w, h).extrude(t)
    if p["kind"] == "flaps":
        groove = (
            cq.Workplane(plane).workplane(offset=t + 1.0).rect(1.0, h + 2.0)
            .extrude(-(t / 2.0 + 1.0))
        )
        plate = plate.cut(groove)
    a = plane.toWorldCoords((0.0, h / 2.0, 0.0))
    b = plane.toWorldCoords((1.0, h / 2.0, 0.0))
    return plate.rotate(a.toTuple(), b.toTuple(), -p["angle"])


def slot_blank(p):
    """A blank that closes a mouth: a plug, with or without an outside flange.

    CDG consumed: `media_slot`. Without a flange it is a flush bay cover.

    p: frame, width, height, plug_depth, gap, flange, flange_margin,
       flange_thickness
    """
    plane = face_plane(p["frame"])
    g = p["gap"]
    plug = (
        cq.Workplane(plane).rect(p["width"] - 2 * g, p["height"] - 2 * g)
        .extrude(-p["plug_depth"])
    )
    if not p["flange"]:
        return plug
    m = p["flange_margin"]
    flange = (
        cq.Workplane(plane).workplane(offset=-0.2)
        .rect(p["width"] + 2 * m, p["height"] + 2 * m).extrude(p["flange_thickness"] + 0.2)
    )
    return plug.union(flange)


def slide_switch(p):
    """A row of slide-switch slots (the VCS-type console panel), one 2-D region
    extruded once (the tool).

    CDG exposed: `switch_seat`. Each slot runs along local Y.

    p: frame, count, pitch, length, width, depth, overshoot
    """
    plane = face_plane(p["frame"])
    n = int(p["count"])
    pts = [((i - (n - 1) / 2.0) * p["pitch"], 0.0) for i in range(n)]
    return (
        cq.Workplane(plane).workplane(offset=p["overshoot"]).pushPoints(pts)
        .slot2D(p["length"], p["width"], 90).extrude(-(p["depth"] + p["overshoot"]))
    )


def controller_port(p):
    """A row of controller-port openings of one kind (the tool).

    CDG exposed: `controller_port_face`. `de9` is a D-shaped trapezoid (the
    Atari/Sega joystick port; its facts are the keystone's `dsub-de9-female`),
    `round_din` a circle, `proprietary` and `usb_a` rectangles. Sizes are the
    archetype's clearance openings, CONTROLLER_PORT_OPENINGS.

    p: frame, kind, count, pitch, depth, overshoot
    """
    plane = face_plane(p["frame"])
    w, h = CONTROLLER_PORT_OPENINGS[p["kind"]]
    n = int(p["count"])
    wp = cq.Workplane(plane).workplane(offset=p["overshoot"])
    pts = [((i - (n - 1) / 2.0) * p["pitch"], 0.0) for i in range(n)]
    total = p["depth"] + p["overshoot"]
    if p["kind"] == "round_din":
        return wp.pushPoints(pts).circle(w / 2.0).extrude(-total)
    if p["kind"] == "de9":
        inset = h * math.tan(math.radians(10.0))
        out = None
        for x, y in pts:
            trap = (
                cq.Workplane(plane).workplane(offset=p["overshoot"])
                .polyline([(x - w / 2.0, y + h / 2.0), (x + w / 2.0, y + h / 2.0),
                           (x + w / 2.0 - inset, y - h / 2.0),
                           (x - w / 2.0 + inset, y - h / 2.0)]).close().extrude(-total)
            )
            out = trap if out is None else out.union(trap)
        return out
    return wp.pushPoints(pts).rect(w, h).extrude(-total)


def port_row(p):
    """A row of connector openings along a face, laid left to right (the tool).

    CDG exposed: `port_cutout`, one per opening. `items` are (shape, width,
    height) — PORT_OPENINGS rows, or any — placed from `start_u` with `gap`
    between them, all centred at height `v`. The cut reaches `depth` inside.

    p: frame (origin at the row's start), items, gap, depth, overshoot
    """
    plane = face_plane(p["frame"])
    out = None
    u = 0.0
    for shape, w, h in p["items"]:
        wp = cq.Workplane(plane).workplane(offset=p["overshoot"]).center(u + w / 2.0, 0.0)
        sk = wp.circle(w / 2.0) if shape == "round" else wp.rect(w, h)
        hole = sk.extrude(-(p["depth"] + p["overshoot"]))
        out = hole if out is None else out.union(hole)
        u += w + p["gap"]
    return out
