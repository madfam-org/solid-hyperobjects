# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""commons-lib/hardware/patterns.py — the pattern helpers the components share.

Not components: no CDG id, no parameter dict. `structure` and `controls` place
their seats and knuckles with these, so a family that inlines either gets this
module first (each of those declares `# requires: patterns`).

Both mirror the graph engine's emission exactly, including the `range(1, count)`
shape, so a count of 1 is one copy and the two engines agree body for body.
Lifted unchanged from `clamshell-dual-screen-handheld/main.py` (2026-11-01).
They only call methods on the shapes they are given, so they import nothing.
"""


def linear_pattern(shape, count, dx):
    """Union `count` copies of `shape` stepped by `dx` in X."""
    out = shape
    for i in range(1, count):
        out = out.union(shape.translate((dx * i, 0.0, 0.0)))
    return out


def polar_pattern(shape, count, angle):
    """Union `count` copies of `shape` spun about Z through the origin.

    The graph node spins about the origin and nothing else, so a cluster is
    always built at the origin and translated into place afterwards.
    """
    out = shape
    for i in range(1, count):
        out = out.union(shape.rotate((0, 0, 0), (0, 0, 1), angle * i))
    return out
