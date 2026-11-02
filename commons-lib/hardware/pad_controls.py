# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: pad_body
"""commons-lib/hardware/pad_controls.py — a two-handed controller's controls.

Components (plan §2.3, Controls), each taking its OWN parameter dict:

  pad_face_layout      a face-button cluster's positions: row, diagonal, diamond,
                       arc_2x3, big_a                                (`button_seat`)
  pad_round_seats      round seats sunk below the crown                (`button_seat`)
  pad_octagon_seat     an octagonal stick gate                         (`stick_seat`)
  pad_round_caps       round button caps standing on the crown
  pad_cross_cap        a cross D-pad cap                               (`dpad_seat`)
  pad_stick            an analogue stick: shaft + convex or concave cap, tilted
  pad_box              an axis-aligned block (bumper caps, trigger seats)
  pad_trigger_blade    an analogue trigger blade on its hinge          (`trigger_seat`)
  pad_grille           a speaker grille: ONE 2-D region, extruded once
  pad_door_seam        a battery door's seam groove: ONE ring region

Seats are cutting TOOLS; caps are the controls themselves (the `controls` part). A
seat's floor is `pad_crown_top(x, y) - recess`, read from the same crown function the
body is built from, and every top cutter runs to `thickness + 1` (overshoot), so a
control sits on the surface whatever the body plan. The seats `commons-lib/hardware/
controls.py` already provides (`d_pad`, `face_button`, `analog_stick`,
`shoulder_trigger`) are reused by the family as they are; this module adds what they
do not cover.

NO GLYPHS, NO SYMBOLS (ruling R3). A cap is a plain cylinder, cross or block; no
marking, no shape borrowed from any maker's buttons. ARCHETYPE THROUGHOUT.

Inlined, never imported (ruling R2 on gate H8).
"""

import math

import cadquery as cq

#: The diagonal arrangement is a row rising one half-pitch per button.
PAD_DIAGONAL_DEG = 26.565
#: arc_2x3: how far the end buttons of each row sag, in pitches.
PAD_ARC_SAG = 0.15
#: big_a: the first button's radius scale, and the arc the others share.
PAD_BIG_A_SCALE = 1.5
PAD_BIG_A_ARC_DEG = 200.0
#: Sticks: shaft radius and cap thickness as fractions of the cap.
PAD_STICK_SHAFT = 0.35
PAD_STICK_CAP = 0.35


def pad_rotate_xy(x, y, deg):
    a = math.radians(deg)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def pad_face_layout(p):
    """A face cluster as [(x, y, radius)], absolute.

    The rules (ours): `row` steps `spacing` along X; `diagonal` is that row rising
    one half-pitch per button; `diamond` puts `count` on a ring of radius `spacing`
    starting on +X; `arc_2x3` is two rows (ceil/floor of count/2) one pitch apart,
    their ends sagging PAD_ARC_SAG pitch; `big_a` puts the first button, at
    PAD_BIG_A_SCALE x radius, in the centre and the rest on an arc above-left of it.
    Every arrangement then turns by `tilt_deg` about the cluster centre.

    p: arrangement, count, spacing, radius, tilt_deg, center_x, center_y
    """
    n, s, r = int(p["count"]), p["spacing"], p["radius"]
    kind = p["arrangement"]
    pts = []
    if n <= 0:
        return pts
    if kind in ("row", "diagonal"):
        for i in range(n):
            pts.append(pad_rotate_xy((i - (n - 1) / 2.0) * s, 0.0,
                            PAD_DIAGONAL_DEG if kind == "diagonal" else 0.0) + (r,))
    elif kind == "arc_2x3":
        top = (n + 1) // 2
        for row, m, y0 in ((0, top, s / 2.0), (1, n - top, -s / 2.0)):
            for i in range(m):
                u = i - (m - 1) / 2.0
                pts.append((u * s, y0 - PAD_ARC_SAG * s * u * u, r))
    elif kind == "big_a":
        pts.append((0.0, 0.0, r * PAD_BIG_A_SCALE))
        m = n - 1
        ring = s + r * (PAD_BIG_A_SCALE - 1.0)
        step = min(60.0, PAD_BIG_A_ARC_DEG / max(m, 1))
        for j in range(m):
            a = math.radians(135.0 + (j - (m - 1) / 2.0) * step)
            pts.append((ring * math.cos(a), ring * math.sin(a), r))
    else:  # diamond
        for i in range(n):
            a = math.radians(360.0 * i / n)
            pts.append((s * math.cos(a), s * math.sin(a), r))
    out = []
    for x, y, rr in pts:
        x, y = pad_rotate_xy(x, y, p["tilt_deg"])
        out.append((p["center_x"] + x, p["center_y"] + y, rr))
    return out


def pad_round_seats(p):
    """Round seats, each sunk `recess` below the crown at its own centre.

    CDG exposed: `button_seat`. One cutter per seat, from the crown minus `recess`
    to thickness + 1 (overshoot past any point of the surface).

    p: crown (the pad_crown_* dict), buttons [(x, y, r)], recess
    """
    c = p["crown"]
    z_hi = c["thickness"] + 1.0
    out = None
    for x, y, r in p["buttons"]:
        z_lo = pad_crown_top(c, x, y) - p["recess"]
        seat = (cq.Workplane("XY").workplane(offset=z_lo).center(x, y)
                .circle(r).extrude(z_hi - z_lo))
        out = seat if out is None else out.union(seat)
    return out


def pad_octagon_seat(p):
    """An octagonal stick gate: a regular octagon across `radius` (inscribed circle).

    CDG exposed: `stick_seat`. The flat-to-flat span is 2 x radius, so a round
    and an octagonal gate of one radius clear the same shaft sweep.

    p: crown, center_x, center_y, radius, recess
    """
    c = p["crown"]
    z_lo = pad_crown_top(c, p["center_x"], p["center_y"]) - p["recess"]
    circ = p["radius"] / math.cos(math.pi / 8.0)
    return (cq.Workplane("XY").workplane(offset=z_lo).center(p["center_x"], p["center_y"])
            .transformed(rotate=(0, 0, 22.5)).polygon(8, 2.0 * circ)
            .extrude(c["thickness"] + 1.0 - z_lo))


def pad_round_caps(p):
    """Round caps [Solid], each from its seat floor + clearance to `height` above the
    crown at its own centre, `clearance` narrower than its seat.

    p: crown, buttons [(x, y, r)], floor_z (None: each seat's own crown - recess),
       recess, clearance, height
    """
    c = p["crown"]
    caps = []
    for x, y, r in p["buttons"]:
        top = pad_crown_top(c, x, y)
        base = (top - p["recess"] if p["floor_z"] is None else p["floor_z"]) + p["clearance"]
        caps.append(cq.Workplane("XY").workplane(offset=base).center(x, y)
                    .circle(r - p["clearance"]).extrude(top + p["height"] - base).val())
    return caps


def pad_cross_cap(p):
    """A cross D-pad cap: two crossed bars, `clearance` inside the `d_pad` seat.

    p: center_x, center_y, arm_length, arm_width, z0, z1, clearance
    """
    cl, h = p["clearance"], p["z1"] - p["z0"]
    a = cq.Workplane("XY").box(p["arm_length"] - 2 * cl, p["arm_width"] - 2 * cl, h)
    b = cq.Workplane("XY").box(p["arm_width"] - 2 * cl, p["arm_length"] - 2 * cl, h)
    return a.union(b).translate((p["center_x"], p["center_y"], (p["z0"] + p["z1"]) / 2.0)).val()


def pad_stick(p):
    """An analogue stick: a shaft and a cap, tilted about its pivot. Returns a Solid.

    The cap is a frustum (convex: narrowing to 0.7 x radius on top) or a disc with
    a conical dish (concave), PAD_STICK_CAP x height thick; its top stands `height`
    above the crown at the stick's centre. The shaft is PAD_STICK_SHAFT x radius and
    stands on the seat floor + clearance. `tilt_deg` turns the whole stick about the
    X axis through its pivot, half a shaft radius above the shaft's foot.

    p: center_x, center_y, floor_z, surface_z, radius, height, cap, tilt_deg, clearance
    """
    x, y, r = p["center_x"], p["center_y"], p["radius"]
    cap_t = PAD_STICK_CAP * p["height"]
    top = p["surface_z"] + p["height"]
    foot = p["floor_z"] + p["clearance"]
    rs = PAD_STICK_SHAFT * r
    shaft = cq.Solid.makeCylinder(rs, top - cap_t + 0.2 - foot, cq.Vector(x, y, foot))
    if p["cap"] == "concave":
        cap = cq.Solid.makeCylinder(r, cap_t, cq.Vector(x, y, top - cap_t))
        dish = 0.3 * cap_t
        cap = cap.cut(cq.Solid.makeCone(0.35 * r, 0.85 * r, dish + 0.5,
                                        cq.Vector(x, y, top - dish)))
    else:
        cap = cq.Solid.makeCone(r, 0.7 * r, cap_t, cq.Vector(x, y, top - cap_t))
    stick = shaft.fuse(cap).clean()
    pivot = cq.Vector(x, y, foot + rs / 2.0)
    return stick.rotate(pivot, pivot + cq.Vector(1, 0, 0), p["tilt_deg"])


def pad_box(p):
    """An axis-aligned block from its six bounds. Returns a Workplane.

    p: x0, x1, y0, y1, z0, z1
    """
    return (cq.Workplane("XY")
            .box(p["x1"] - p["x0"], p["y1"] - p["y0"], p["z1"] - p["z0"])
            .translate(((p["x0"] + p["x1"]) / 2.0, (p["y0"] + p["y1"]) / 2.0,
                        (p["z0"] + p["z1"]) / 2.0)))


def pad_trigger_blade(p):
    """An analogue trigger blade on its hinge. Returns a Solid.

    CDG consumed: `trigger_seat` (the notch `shoulder_trigger` cuts in the rear
    corner). The blade lies against the notch's inner wall, hinged along X at its
    outer top edge; `angle_deg` swings its foot outward (+Y), 0 = seated. Every point
    of the blade is below and inboard of the hinge, so no angle drives it up into
    the body.

    p: center_x, width, y_inner, notch_top, length, thickness, clearance, angle_deg
    """
    cl = p["clearance"]
    y0 = p["y_inner"] + cl
    zh = p["notch_top"] - cl
    blade = pad_box({"x0": p["center_x"] - p["width"] / 2.0 + cl,
                     "x1": p["center_x"] + p["width"] / 2.0 - cl,
                     "y0": y0, "y1": y0 + p["thickness"],
                     "z0": zh - p["length"], "z1": zh}).val()
    hinge = cq.Vector(0.0, y0 + p["thickness"], zh)
    return blade.rotate(hinge, hinge + cq.Vector(1, 0, 0), p["angle_deg"])


def pad_grille(p):
    """A speaker grille: `rows` x `cols` holes on a hexagonal pitch, ONE region.

    No CDG id (a vented face is not a mating feature). All holes are one sketch,
    extruded once and cut once (the vent-field rule).

    p: center_x, center_y, rows, cols, pitch, hole_radius, z_lo, z_hi
    """
    pts = []
    rows, cols, s = int(p["rows"]), int(p["cols"]), p["pitch"]
    for j in range(rows):
        m = cols - (j % 2)
        for i in range(m):
            pts.append((p["center_x"] + (i - (m - 1) / 2.0) * s,
                        p["center_y"] + (j - (rows - 1) / 2.0) * s * 0.866))
    return (cq.Workplane("XY").workplane(offset=p["z_lo"]).pushPoints(pts)
            .circle(p["hole_radius"]).extrude(p["z_hi"] - p["z_lo"]))


def pad_door_seam(p):
    """A battery door's seam: a rectangular ring groove, ONE region cut from below.

    CDG exposed: `battery_bay` (its door outline). `groove` wide.

    p: center_x, center_y, width, length, groove, z_lo, z_hi
    """
    g = p["groove"]
    return (cq.Workplane("XY").workplane(offset=p["z_lo"]).center(p["center_x"], p["center_y"])
            .rect(p["width"], p["length"]).rect(p["width"] - 2 * g, p["length"] - 2 * g)
            .extrude(p["z_hi"] - p["z_lo"]))
