# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: patterns
"""commons-lib/hardware/structure.py — the body and the hinge of a device.

Components (plan §2.3, Structure): `deck_shell`, `hinge_barrel`,
`hinge_relief`, `speaker_grille`. Each takes its OWN parameter dict, reads no
manifest global and knows no assembly, so any family can call it. Lifted
unchanged from `clamshell-dual-screen-handheld/main.py` (2026-11-01).

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import cadquery as cq


def deck_shell(p):
    """One rigid deck: a rounded-corner slab.

    CDG exposed: `device_envelope` (the closed outline another accessory mates
    to) and, for the lower deck, `cradle_seat` (the outer face a dock registers
    against).

    p: length, depth, thickness, center_y, center_z, corner_radius
    """
    return (
        cq.Workplane("XY")
        .box(p["length"], p["depth"], p["thickness"])
        .translate((0.0, p["center_y"], p["center_z"]))
        .edges("|Z")
        .fillet(p["corner_radius"])
    )


def hinge_barrel(p):
    """The knuckle run on the revolute axis.

    CDG exposed: `revolute_axis` and `mounting_surface` — the same two ids the
    commons' `hinge-hyperobject` cartridge declares, so a knuckle printed from
    either fits the other's pocket.

    The barrel is a HALF cylinder: the decks end at the hinge axis, so the barrel
    must too, or the closed envelope would exceed the device's published depth
    and the two decks would overlap when flat.

    p: barrel_radius, knuckle_length, knuckle_count, knuckle_pitch,
       knuckle_start_x, clip_span, clip_center_y
    """
    knuckle = (
        cq.Workplane("XY")
        .cylinder(p["knuckle_length"], p["barrel_radius"])
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((p["knuckle_start_x"], 0.0, 0.0))
    )
    run = linear_pattern(knuckle, p["knuckle_count"], p["knuckle_pitch"])
    clip = (
        cq.Workplane("XY")
        .box(p["clip_span"], p["clip_span"], p["clip_span"])
        .translate((0.0, p["clip_center_y"], 0.0))
    )
    return run.cut(clip)


def hinge_relief(p):
    """The pocket both decks give up so the barrel can turn.

    CDG consumed: `revolute_axis`. Radius is the barrel radius plus the running
    clearance; the span stops where the knuckles do, so outside it the rear face
    stays solid — which is where the shoulder triggers cut.

    p: relief_radius, relief_span
    """
    return (
        cq.Workplane("XY")
        .cylinder(p["relief_span"], p["relief_radius"])
        .rotate((0, 0, 0), (0, 1, 0), 90)
    )


def speaker_grille(p):
    """A row of vent holes.

    No upstream CDG id; a grille is a vented face, not a mating feature.
    ARCHETYPE THROUGHOUT — the registry does not describe grilles.

    p: count, first_center_x, center_y, hole_radius, pitch, recess_depth,
       cut_center_z
    """
    hole = (
        cq.Workplane("XY")
        .cylinder(p["recess_depth"], p["hole_radius"])
        .translate((p["first_center_x"], p["center_y"], p["cut_center_z"]))
    )
    return linear_pattern(hole, p["count"], p["pitch"])
