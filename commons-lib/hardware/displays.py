# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/displays.py — display windows.

Components (plan §2.3, Displays and optics): `display_panel` (the plan's
`display_window`). It returns the cutting TOOL; the assembly cuts it from a
deck. It takes its OWN parameter dict, reads no manifest global and knows no
assembly. Lifted unchanged from `clamshell-dual-screen-handheld/main.py`
(2026-11-01).

Inlined, never imported: `tools/inline_parts.py` copies this text into every
family `main.py` that declares it (ruling R2 on gate H8).
"""

import cadquery as cq


def display_panel(p):
    """A display's active area as a recess tool.

    CDG exposed: `display_recess` — the bounded flat area the panel occupies.
    The solid returned is the TOOL: the assembly cuts it from a deck, so the
    same component serves the upper and lower decks unchanged.

    p: width, height, recess_depth, center_x, center_y, cut_center_z
    """
    return (
        cq.Workplane("XY")
        .box(p["width"], p["height"], p["recess_depth"])
        .translate((p["center_x"], p["center_y"], p["cut_center_z"]))
    )
