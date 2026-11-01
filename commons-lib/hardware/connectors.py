# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/connectors.py — openings a connector or a medium enters.

Components (plan §2.3, Connectors and seats): `port_receptacle`,
`cartridge_slot`. Each returns the cutting TOOL; the assembly cuts it from a
deck face. Each takes its OWN parameter dict, reads no manifest global and
knows no assembly. Lifted unchanged from
`clamshell-dual-screen-handheld/main.py` (2026-11-01).

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import cadquery as cq


def port_receptacle(p):
    """A connector opening in a deck face — rectangular or round.

    CDG exposed: `port_cutout`. One component serves the USB-C receptacle
    (`shape: "rect"`) and the 3.5 mm jack (`shape: "round"`, whose radius is half
    the connector's nominal diameter — the registry's own port kind).

    p: shape ("rect"|"round"), width, height, depth, radius,
       center_x, center_y, center_z
    """
    if p["shape"] == "round":
        return (
            cq.Workplane("XY")
            .cylinder(p["depth"], p["radius"])
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((p["center_x"], p["center_y"], p["center_z"]))
        )
    return (
        cq.Workplane("XY")
        .box(p["width"], p["depth"], p["height"])
        .translate((p["center_x"], p["center_y"], p["center_z"]))
    )


def cartridge_slot(p):
    """A game-cartridge mouth in a deck face.

    CDG exposed: `cartridge_slot`. ARCHETYPE THROUGHOUT: the registry's `ports[]`
    vocabulary has no game-card kind, so no preset sources this component's size
    or presence and it is never a device claim — the same standing as the speaker
    grille.

    p: width, height, depth, center_x, center_y, center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["width"], p["depth"], p["height"])
        .translate((p["center_x"], p["center_y"], p["center_z"]))
    )
