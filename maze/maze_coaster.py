"""Maze Coaster — Yantra4D Hyperobject Cartridge (CadQuery / B-Rep).

A flat circular coaster with the maze walls standing on its face, clipped to the disc.

The maze itself comes from the shared deterministic kernel below, which is
duplicated verbatim in maze_kernel.scad: same 32-bit LCG, same backtracker,
same cell and neighbour order, so the CadQuery and OpenSCAD engines render the
SAME maze for the same seed. Do not edit one copy without the other.
"""

import cadquery as cq
import math
import json
import argparse

# ─────────────────────────────────────────────────────────────────────────────
# Shared deterministic maze kernel — CadQuery side.
#
# This block is the Python half of a kernel whose OpenSCAD half lives in
# maze_kernel.scad. Both sides implement the SAME 32-bit LCG and the SAME
# iterative recursive backtracker, walking cells in the same order and
# neighbours in the same order, so `mz_grid(rows, cols, seed, x_wrapping)`
# returns bit-identical passage masks in either language and the two engines
# render the same maze. It is duplicated verbatim in the cartridge's three
# scripts because the render sandbox blocks `sys` and offers no import path to
# a sibling module; the OpenSCAD side, which has `use <>`, keeps one copy.
#
# Double-arithmetic contract — OpenSCAD has no integer type, so every value is
# an IEEE-754 double and is exact only below 2^53. The kernel is written to
# stay inside that budget on BOTH sides:
#   * the LCG multiply-add peaks at 1664525*(2^32-1)+1013904223 = 7.149e15,
#     which is 0.79 * 2^53 — exact, with headroom;
#   * the pick floor(s*n / 2^32) peaks at 4*(2^32-1) = 1.718e10 — exact;
#   * every reduction is an explicit % or floor. Nothing relies on bit
#     operations (OpenSCAD has none) or on integer division.
# Python's ints are arbitrary-precision, so Python is exact for free; the
# bound is what makes the OPENSCAD side reproduce these same values.
# ─────────────────────────────────────────────────────────────────────────────

MZ_M = 4294967296  # 2**32
MZ_A = 1664525     # Numerical Recipes multiplier
MZ_C = 1013904223  # Numerical Recipes increment

# Neighbour order, fixed and shared: 0=N(r-1) 1=S(r+1) 2=W(c-1) 3=E(c+1).
MZ_DR = (-1, 1, 0, 0)
MZ_DC = (0, 0, -1, 1)
# Passage bit flags, shared: 1=N 2=S 4=W 8=E.
MZ_BIT = (1, 2, 4, 8)
MZ_OPP = (2, 1, 8, 4)


def mz_next(s):
    """One step of the shared 32-bit LCG."""
    return (MZ_A * s + MZ_C) % MZ_M


def mz_seed(seed):
    """Fold the user seed twice so adjacent small seeds (1, 2, 3 ...) do not
    start out correlated in the low bits, which a bare LCG state would."""
    return mz_next(mz_next((int(seed) % MZ_M + MZ_M) % MZ_M))


def mz_grid(rows, cols, seed, x_wrapping=False):
    """Carve a perfect maze and return a flat rows*cols list of passage masks.

    An iterative recursive backtracker over an explicit stack: always work the
    cell on top of the stack, collect its unvisited neighbours in N,S,W,E
    order, draw ONE LCG value to pick among them, carve both sides of the wall
    and push; pop when there is no candidate. The PRNG is consumed exactly once
    per step that has a candidate — that discipline, plus the fixed neighbour
    order, is what makes the two languages agree.
    """
    n_cells = rows * cols
    grid = [0] * n_cells
    visited = [False] * n_cells
    visited[0] = True
    stack = [0]
    s = mz_seed(seed)

    while stack:
        here = stack[-1]
        r = here // cols
        c = here % cols
        cand = []
        for d in range(4):
            nr = r + MZ_DR[d]
            nc = c + MZ_DC[d]
            if x_wrapping:
                nc = (nc % cols + cols) % cols
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr * cols + nc]:
                cand.append(d)
        k = len(cand)
        if k:
            s = mz_next(s)
            idx = (s * k) // MZ_M
            if idx >= k:
                idx = k - 1
            d = cand[idx]
            nr = r + MZ_DR[d]
            nc = c + MZ_DC[d]
            if x_wrapping:
                nc = (nc % cols + cols) % cols
            there = nr * cols + nc
            grid[here] |= MZ_BIT[d]
            grid[there] |= MZ_OPP[d]
            visited[there] = True
            stack.append(there)
        else:
            stack.pop()
    return grid


def mz_walls(grid, rows, cols, cell_size, x_wrapping=False):
    """Turn a passage grid into wall segments, in a fixed, shared order.

    A wall stands on a cell's south and east side wherever that cell has no
    passage that way, and on the field's outer boundary. With x_wrapping the
    east and west edges are omitted — the field closes on itself, so there is
    no outside there. The emission order is part of the contract both engines
    honour: cells row-major, and within a cell south, east, north, west.
    """
    walls = []
    for r in range(rows):
        for c in range(cols):
            x = c * cell_size
            y = r * cell_size
            mask = grid[r * cols + c]
            # South side of this cell (its +y edge), and the field's south rim.
            if not (mask & 2) or r == rows - 1:
                walls.append(((x, y + cell_size), (x + cell_size, y + cell_size)))
            # East side (its +x edge), and the field's east rim — neither exists
            # on a wrapping field, where column cols-1 abuts column 0.
            if not x_wrapping and (not (mask & 8) or c == cols - 1):
                walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
            # North rim of the field.
            if r == 0:
                walls.append(((x, y), (x + cell_size, y)))
            # West rim of the field (absent when wrapping).
            if c == 0 and not x_wrapping:
                walls.append(((x, y), (x, y + cell_size)))
    return walls


def build(params):
    rows = int(params.get('rows', 10))
    cols = int(params.get('cols', 10))
    cell_size = float(params.get('cell_size', 5))
    wall_thickness = float(params.get('wall_thickness', 1.2))
    wall_height = float(params.get('wall_height', 3))
    base_thickness = float(params.get('base_thickness', 2))
    seed = int(params.get('seed', 123))
    diameter = float(params.get('diameter', 100))

    radius = diameter / 2.0
    maze_w = cols * cell_size
    maze_h = rows * cell_size

    # Circular base disc
    result = cq.Workplane("XY").circle(radius).extrude(base_thickness)

    # Generate maze walls, centered on origin
    grid = mz_grid(rows, cols, seed)
    walls = mz_walls(grid, rows, cols, cell_size)
    offset_x = -maze_w / 2.0
    offset_y = -maze_h / 2.0

    # Build walls clipped to circle
    # Collect the wall solids and fuse them into the base in ONE boolean.
    #
    # This used to be `result = result.union(wall)` inside the loop. Each union is a
    # full OCCT boolean rebuild of an ever-growing shape, so the cost is quadratic:
    # measured 113 s for 100 boxes against 1.9 s for the single fuse — 60x — and the
    # expert_cube preset (25x25) emits over 1300 walls. `fuse(*solids)` hands OCCT
    # the whole set at once and returns the identical solid (volumes agree exactly).
    wall_solids = []

    for (x1, y1), (x2, y2) in walls:
        wx1 = x1 + offset_x
        wy1 = y1 + offset_y
        wx2 = x2 + offset_x
        wy2 = y2 + offset_y

        # Skip walls outside circle
        mid_x = (wx1 + wx2) / 2.0
        mid_y = (wy1 + wy2) / 2.0
        if math.hypot(mid_x, mid_y) > radius - 1:
            continue

        dx = wx2 - wx1
        dy = wy2 - wy1
        length = math.hypot(dx, dy)
        if length < 0.01:
            continue
        cx = (wx1 + wx2) / 2.0
        cy = (wy1 + wy2) / 2.0
        angle = math.degrees(math.atan2(dy, dx))

        wall = (
            cq.Workplane("XY")
            .box(length, wall_thickness, wall_height)
            .rotate((0, 0, 0), (0, 0, 1), angle)
            .translate((cx, cy, base_thickness + wall_height / 2.0))
        )
        wall_solids.append(wall.val())

    if wall_solids:
        result = cq.Workplane(obj=result.val().fuse(*wall_solids))

    return result.clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)
    res = build(params)

    if args.out:
        cq.exporters.export(res, args.out)
