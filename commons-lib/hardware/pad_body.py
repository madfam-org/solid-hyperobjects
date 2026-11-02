# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: structure
"""commons-lib/hardware/pad_body.py — the body of a two-handed controller.

Components (plan §2.3, Structure, the gamepad `shell_body`):

  pad_crown_top / pad_crown_bottom   the ONE analytic crown z(x, y) (helpers)
  pad_crown_dome                     the solid under (or over) that crown
  pad_grip_layout / pad_grip         the tapered grips of a body plan
  pad_body                           bridge + grips, crowned: `device_envelope`,
                                     `grip_envelope`
  pad_rail                           a Joy-Con-type T rail on a half's inner face: `rail`
  pad_magnet_pockets                 the magnet pockets of a magnetic half: `magnetic_seat`

THE CROWN. Every point of the top surface is

    z_top(x, y)    = thickness - top_crown    * max(0, q - PAD_CROWN_FLAT)
    z_bottom(x, y) = floor     + bottom_crown * max(0, q - PAD_CROWN_FLAT)
    q              = (x / span_x)^2 + ((y - center_y) / span_y)^2

so the body and every control seat read the same function, and a seat sunk to
`z_top - recess` sits on the surface whatever the body plan. The dome is a loft of
the crown's own level sets (similar ellipses) down from a small flat — never a
sphere, so there is no pole (gotcha 1). The bottom crown applies to the bridge
only; grips stand on the flat plane z = 0, and `floor` lifts the bridge's
underside by the grip drop.

ARCHETYPE THROUGHOUT. No outline here is fitted to any product: the planform is a
rounded-rectangle bridge plus 0, 2 or 3 grips, each the hull of a root and a tip
circle, and the five body plans are written rules (`pad_grip_layout`).

Each component takes its OWN parameter dict and reads no manifest global.
Inlined, never imported (ruling R2 on gate H8).
"""

import math

import cadquery as cq

#: q below which the crown is flat — the small flat every dome is lofted to.
PAD_CROWN_FLAT = 0.02
#: Normalised level-set radii the dome loft passes through between the flat and its
#: last section (a planform point never lies beyond r = sqrt(2)).
PAD_DOME_RADII = (0.3, 0.55, 0.8, 1.05, 1.3, 1.6, 2.0)
#: Each level set is a periodic spline through this many points of its ellipse,
#: starting at PAD_DOME_SEAM_DEG. An exact (periodic) ellipse puts its seam on the
#: major axis, which a grip or the split plane then crosses edge-on: the fuse comes
#: out invalid. 100 degrees keeps the seam off the split plane and every grip.
PAD_DOME_POINTS = 24
PAD_DOME_SEAM_DEG = 100.0
#: The crescent body plan bites a circle out of the bridge's front edge.
PAD_CRESCENT_RADIUS = 0.42      # of bridge_width
PAD_CRESCENT_BITE = 0.30        # of bridge_depth
#: How far a T rail stands off its half's inner face, and the magnet pockets.
PAD_RAIL_HEIGHT = 2.0
PAD_MAGNET_RADIUS = 3.0
PAD_MAGNET_DEPTH = 2.0


def pad_crown_q(c, x, y):
    """The crown's normalised radius squared. c: span_x, span_y, center_y."""
    return (x / c["span_x"]) ** 2 + ((y - c["center_y"]) / c["span_y"]) ** 2


def pad_crown_top(c, x, y):
    """z of the top surface at (x, y). c: thickness, top_crown, span_x, span_y, center_y."""
    return c["thickness"] - c["top_crown"] * max(0.0, pad_crown_q(c, x, y) - PAD_CROWN_FLAT)


def pad_crown_bottom(c, x, y):
    """z of the bridge's underside at (x, y). c: floor, bottom_crown, span_x, span_y, center_y."""
    return c["floor"] + c["bottom_crown"] * max(0.0, pad_crown_q(c, x, y) - PAD_CROWN_FLAT)


def pad_crown_dome(c, side):
    """The solid below the top crown (`side` "top") or above the bottom one ("bottom").

    No CDG id: a construction solid the body is intersected with. A loft of the
    crown's level sets, each an ellipse span_x*r by span_y*r at the z the crown
    function gives for r, from the small flat to a section past the body (z = -1
    for the top dome, thickness + 1 for the bottom one). Returns None for a crown
    under 0.05 mm, which is flat. Each section is a periodic spline through
    PAD_DOME_POINTS points of its ellipse (see PAD_DOME_SEAM_DEG).

    c: thickness, floor, top_crown, bottom_crown, span_x, span_y, center_y
    """
    if side == "top":
        k, z0, z_end, sign = c["top_crown"], c["thickness"], -1.0, -1.0
    else:
        k, z0, z_end, sign = c["bottom_crown"], c["floor"], c["thickness"] + 1.0, 1.0
    if k < 0.05:
        return None
    r0 = math.sqrt(PAD_CROWN_FLAT)
    r_end = math.sqrt(PAD_CROWN_FLAT + abs(z_end - z0) / k)
    radii = [r0] + [r for r in PAD_DOME_RADII if r0 + 0.05 < r < r_end - 0.05] + [r_end]
    wires = []
    seam = math.radians(PAD_DOME_SEAM_DEG)
    for r in radii:
        z = z0 + sign * k * (r * r - PAD_CROWN_FLAT)
        pts = [cq.Vector(c["span_x"] * r * math.cos(seam + 2.0 * math.pi * i / PAD_DOME_POINTS),
                         c["center_y"] + c["span_y"] * r
                         * math.sin(seam + 2.0 * math.pi * i / PAD_DOME_POINTS), z)
               for i in range(PAD_DOME_POINTS)]
        wires.append(cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)]))
    return cq.Workplane("XY").add(cq.Solid.makeLoft(wires))


def pad_grip_count(p):
    """How many grips a body plan draws: none for a brick, else `grip_count`."""
    return 0 if p["outline"] == "brick" else int(p["grip_count"])


def pad_grip_layout(p):
    """The grips of a body plan as (root_x, root_y, root_r, tip_x, tip_y, tip_r).

    The written rules (they are ours, and they are the only source of an outline):
      * the side grips root at (±grip_root_x, grip_root_y) and run grip_length
        at grip_splay_deg outward from straight down (-Y), tapering from
        grip_root_radius to grip_tip_radius;
      * a dogbone's grips are end lobes: one circle of grip_tip_radius at the root;
      * a third grip (grip_count 3) roots on the centreline against the bridge's
        front edge and runs straight down, center_grip_offset longer than the sides.

    p: outline, grip_count, grip_root_x, grip_root_y, grip_length, grip_splay_deg,
       grip_root_radius, grip_tip_radius, center_grip_offset, bridge_depth
    """
    n = pad_grip_count(p)
    out = []
    if n < 2:
        return out
    s = math.radians(p["grip_splay_deg"])
    length = p["grip_length"]
    for side in (-1.0, 1.0):
        rx, ry = side * p["grip_root_x"], p["grip_root_y"]
        if p["outline"] == "dogbone":
            out.append((rx, ry, p["grip_tip_radius"], rx, ry, p["grip_tip_radius"]))
        else:
            out.append((rx, ry, p["grip_root_radius"],
                        rx + side * length * math.sin(s), ry - length * math.cos(s),
                        p["grip_tip_radius"]))
    if n >= 3:
        cy = -p["bridge_depth"] / 2.0 + p["grip_root_radius"]
        out.append((0.0, cy, p["grip_root_radius"],
                    0.0, cy - length - p["center_grip_offset"], p["grip_tip_radius"]))
    return out


def pad_grip(p):
    """One tapered grip: the hull of its root and tip circles, extruded z0 .. z0+height.

    CDG exposed: `grip_envelope` (with the bridge). A grip whose circles nest is the
    larger circle alone.

    p: root_x, root_y, root_radius, tip_x, tip_y, tip_radius, z0, height
    """
    rx, ry, r1 = p["root_x"], p["root_y"], p["root_radius"]
    tx, ty, r2 = p["tip_x"], p["tip_y"], p["tip_radius"]
    dx, dy = tx - rx, ty - ry
    dist = math.hypot(dx, dy)
    base = cq.Workplane("XY").workplane(offset=p["z0"])
    if dist <= abs(r1 - r2) + 0.05:
        cx, cy, r = (rx, ry, r1) if r1 >= r2 else (tx, ty, r2)
        return base.center(cx, cy).circle(r).extrude(p["height"])
    ang = math.atan2(dy, dx)
    a = math.acos((r1 - r2) / dist)

    def on(cx, cy, r, t):
        return (cx + r * math.cos(t), cy + r * math.sin(t))

    return (
        base.moveTo(*on(rx, ry, r1, ang + a))
        .lineTo(*on(tx, ty, r2, ang + a))
        .threePointArc(on(tx, ty, r2, ang), on(tx, ty, r2, ang - a))
        .lineTo(*on(rx, ry, r1, ang - a))
        .threePointArc(on(rx, ry, r1, ang + math.pi), on(rx, ry, r1, ang + a))
        .close()
        .extrude(p["height"])
    )


def pad_body(p):
    """The crowned body of a two-handed controller, or its cavity when inset > 0.

    CDG exposed: `device_envelope` and `grip_envelope` — the closed solid a stand,
    mount or travel case takes as its controller. Built as the gotchas canon asks:
    straight prisms with flat bottoms (the bridge from `floor`, the grips from 0),
    the grips unioned branch-first and then onto the bridge they bite into, then ONE
    intersection with each crown dome. `inset` offsets everything inward (planform,
    top, floors) so the same rules cut a shell's cavity.

    p: thickness, floor, top_crown, bottom_crown, span_x, span_y, center_y,
       outline, bridge_width, bridge_depth, bridge_corner_radius, grip_count,
       grip_root_x, grip_root_y, grip_length, grip_splay_deg, grip_root_radius,
       grip_tip_radius, center_grip_offset, inset
    """
    t = p["inset"]
    top = p["thickness"] - t
    floor = p["floor"] + t
    bw, bd = p["bridge_width"] - 2.0 * t, p["bridge_depth"] - 2.0 * t
    rc = min(max(p["bridge_corner_radius"] - t, 0.5), min(bw, bd) / 2.0 - 0.1)
    bridge = deck_shell({
        "length": bw, "depth": bd, "thickness": top - floor, "center_y": 0.0,
        "center_z": (top + floor) / 2.0, "corner_radius": rc,
    })
    if p["outline"] == "crescent":
        r = PAD_CRESCENT_RADIUS * p["bridge_width"]
        yc = -p["bridge_depth"] / 2.0 - r + PAD_CRESCENT_BITE * p["bridge_depth"]
        bridge = bridge.cut(
            cq.Workplane("XY").workplane(offset=floor - 1.0).center(0.0, yc)
            .circle(r + t).extrude(top - floor + 2.0))
    crown = {"thickness": top, "floor": floor, "top_crown": p["top_crown"],
             "bottom_crown": p["bottom_crown"], "span_x": p["span_x"],
             "span_y": p["span_y"], "center_y": p["center_y"]}
    under = pad_crown_dome(crown, "bottom")
    if under is not None:
        bridge = bridge.intersect(under)
    grips = None
    for rx, ry, r1, tx, ty, r2 in pad_grip_layout(p):
        if min(r1, r2) - t < 0.5:
            continue
        g = pad_grip({"root_x": rx, "root_y": ry, "root_radius": r1 - t,
                      "tip_x": tx, "tip_y": ty, "tip_radius": r2 - t,
                      "z0": t, "height": top - t})
        grips = g if grips is None else grips.union(g)
    body = bridge if grips is None else grips.union(bridge)
    over = pad_crown_dome(crown, "top")
    if over is not None:
        body = body.intersect(over)
    return body


def pad_rail(p):
    """A Joy-Con-type T rail standing on a split half's inner face.

    CDG exposed: `rail` — the male slide a tablet's side slot (or a grip) consumes.
    It runs along Y, centred on (center_y, center_z), and stands PAD_RAIL_HEIGHT
    off the face at x = side*PAD_RAIL_HEIGHT toward x = 0: a stem half the rail's
    width, then a flange its full width. The stem bites 0.2 mm into the half.

    p: side (-1 left, +1 right), length, width, center_y, center_z
    """
    h = PAD_RAIL_HEIGHT
    s = p["side"]
    stem = (cq.Workplane("XY").box(h / 2.0 + 0.4, p["length"], p["width"] / 2.0)
            .translate((s * h * 0.75, p["center_y"], p["center_z"])))
    flange = (cq.Workplane("XY").box(h / 2.0, p["length"], p["width"])
              .translate((s * h / 4.0, p["center_y"], p["center_z"])))
    return stem.union(flange)


def pad_magnet_pockets(p):
    """Two magnet pockets in a split half's inner face (x = 0).

    CDG exposed: `magnetic_seat` — where a magnetic half registers on its partner.
    Each cutter starts 1 mm outside the face (overshoot) and sinks PAD_MAGNET_DEPTH.

    p: side (-1 left, +1 right), pitch, center_y, center_z
    """
    out = None
    for dy in (-p["pitch"] / 2.0, p["pitch"] / 2.0):
        pocket = (cq.Workplane("YZ").circle(PAD_MAGNET_RADIUS).extrude(PAD_MAGNET_DEPTH + 1.0)
                  .translate((-1.0 if p["side"] > 0 else -PAD_MAGNET_DEPTH,
                              p["center_y"] + dy, p["center_z"])))
        out = pocket if out is None else out.union(pocket)
    return out
