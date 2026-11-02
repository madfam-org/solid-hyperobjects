# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: patterns
"""commons-lib/hardware/controls.py — the seats a device's controls sit in.

Components (plan §2.3, Controls): `d_pad`, `face_button`, `button_row`,
`analog_stick`, `shoulder_trigger`. Each returns the cutting TOOL, not the
control: the assembly cuts it from a deck. Each takes its OWN parameter dict,
reads no manifest global and knows no assembly. Lifted unchanged from
`clamshell-dual-screen-handheld/main.py` (2026-11-01).

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import cadquery as cq


def d_pad(p):
    """A four-way directional pad seat, as two crossed bars.

    CDG exposed: `dpad_seat`. A cross with rounded re-entrant corners needs a
    free-form profile (yantra4d lane G-NODES-1); two boxes is the honest L2 form
    and is identical in both engines.

    p: arm_length, arm_width, recess_depth, center_x, center_y, cut_center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["arm_length"], p["arm_width"], p["recess_depth"])
        .union(cq.Workplane("XY").box(p["arm_width"], p["arm_length"], p["recess_depth"]))
        .translate((p["center_x"], p["center_y"], p["cut_center_z"]))
    )


def face_button(p):
    """A ring of round button seats.

    CDG exposed: `button_seat` — one circular pocket; the ring is `count` of them
    on a circle of `circle_radius`. `spacing_deg` is its own value because the
    graph engine has no expressions: for an even ring it is 360 / count.

    p: count, spacing_deg, circle_radius, radius, recess_depth,
       center_x, center_y, cut_center_z
    """
    seat = (
        cq.Workplane("XY")
        .cylinder(p["recess_depth"], p["radius"])
        .translate((p["circle_radius"], 0.0, 0.0))
    )
    ring = polar_pattern(seat, p["count"], p["spacing_deg"])
    return ring.translate((p["center_x"], p["center_y"], p["cut_center_z"]))


def button_row(p):
    """A straight row of round button seats — start/select and the like.

    CDG exposed: `button_seat`, the same circular pocket `face_button` places on
    a circle. Two arrangements of one interface, not two interfaces.

    p: count, first_center_x, pitch_x, center_y, radius, recess_depth,
       cut_center_z
    """
    seat = (
        cq.Workplane("XY")
        .cylinder(p["recess_depth"], p["radius"])
        .translate((p["first_center_x"], p["center_y"], p["cut_center_z"]))
    )
    return linear_pattern(seat, p["count"], p["pitch_x"])


def analog_stick(p):
    """A row of analogue-stick seats.

    CDG exposed: `stick_seat` — a circular recess the stick's collar sits in.

    p: count, first_center_x, pitch_x, center_y, radius, recess_depth,
       cut_center_z
    """
    seat = (
        cq.Workplane("XY")
        .cylinder(p["recess_depth"], p["radius"])
        .translate((p["first_center_x"], p["center_y"], p["cut_center_z"]))
    )
    return linear_pattern(seat, p["count"], p["pitch_x"])


def shoulder_trigger(p):
    """A row of shoulder-trigger seats cut into the rear face.

    CDG exposed: `trigger_seat` — the same kind of pocket as `button_seat` but
    rectangular and on the rear face rather than the top. The cut straddles the
    rear face so it never presents a face coincident with the deck's.

    p: count, first_center_x, pitch_x, center_y, center_z, width, depth, height
    """
    seat = (
        cq.Workplane("XY")
        .box(p["width"], p["depth"], p["height"])
        .translate((p["first_center_x"], p["center_y"], p["center_z"]))
    )
    return linear_pattern(seat, p["count"], p["pitch_x"])
