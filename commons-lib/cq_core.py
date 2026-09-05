"""commons-lib/cq_core.py — CDG helper geometry for the solid commons (CadQuery).

Original author:  Innovaciones MADFAM
Originally published under AGPL-3.0 in madfam-org/yantra4d as
                  libs/cq_core/__init__.py and libs/yantra4d/cdg_interfaces.py.
Relicensed by the rights holder (Innovaciones MADFAM) under CERN-OHL-W-2.0
                  on 2026-09-05, per operator ruling G11.
SPDX-License-Identifier: CERN-OHL-W-2.0

Why this file exists
--------------------
`fasteners` and `framing-hyperobject` used to reach OUTSIDE this repository for
AGPL-3.0 platform code at render time. Ruling G11 relicenses exactly the helpers
those two cartridges use, so a CERN-OHL-W-2.0 commons is self-contained.

How cartridges consume it
-------------------------
NOT by importing it. The CadQuery render sandbox
(`packages/commons-sandbox/src/commons_sandbox/core.py`) blocks `sys`, `os` and
`importlib` outright, so a cartridge script cannot import a sibling module by
any means — which is exactly why the old `sys.path` hack failed to render at
all. Every commons cartridge is therefore a self-contained script, and the two
cartridges here keep their own inline copy of the helper they need:

    framing-hyperobject/framing.py :: cdg_french_cleat   <- cdg_french_cleat below

This file is the licensed, canonical text those inline copies are kept in sync
with, and it is directly runnable/testable outside the sandbox.

Scope: ONLY the helper the two cartridges actually use. `fasteners` does not
appear here: its `bolt.py::create_thread` is a clean rewrite (a single revolved
sawtooth profile, watertight by construction) and shares no code with the
platform's helical-sweep `create_thread`, so nothing of it needed relicensing.
"""

import math

import cadquery as cq


def cdg_french_cleat(length=100, height=30, depth=15, angle=45):
    """A standardized French Cleat profile, extruded along +Y and centered."""
    rad = math.radians(angle)
    pts = [
        (0, 0),
        (depth, 0),
        (depth, height),
        (depth - (height * math.tan(rad)), height),
    ]
    cleat = cq.Workplane("YZ").polyline(pts).close().extrude(length)
    return cleat.translate((-length / 2, -height / 2, 0)).clean()
