import cadquery as cq
import math
import json
import argparse
import random


def generate_maze_walls(rows, cols, cell_size, seed, x_wrapping=False):
    """Generate maze wall segments using recursive backtracker algorithm."""
    rng = random.Random(seed)
    grid = [[0] * cols for _ in range(rows)]

    visited = [[False] * cols for _ in range(rows)]
    stack = [(0, 0)]
    visited[0][0] = True

    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if x_wrapping:
                nc = nc % cols
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            nr, nc, dr, dc = rng.choice(neighbors)
            visited[nr][nc] = True
            if dr == -1:
                grid[r][c] |= 1
                grid[nr][nc] |= 2
            elif dr == 1:
                grid[r][c] |= 2
                grid[nr][nc] |= 1
            elif dc == -1:
                grid[r][c] |= 4
                grid[nr][nc] |= 8
            elif dc == 1:
                grid[r][c] |= 8
                grid[nr][nc] |= 4
            stack.append((nr, nc))
        else:
            stack.pop()

    walls = []
    for r in range(rows):
        for c in range(cols):
            x = c * cell_size
            y = r * cell_size
            if not (grid[r][c] & 2) and r < rows - 1:
                walls.append(((x, y + cell_size), (x + cell_size, y + cell_size)))
            elif r == rows - 1:
                walls.append(((x, y + cell_size), (x + cell_size, y + cell_size)))
            if not (grid[r][c] & 8):
                if not x_wrapping and c == cols - 1:
                    walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
                elif not x_wrapping and c < cols - 1:
                    walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
            if r == 0:
                walls.append(((x, y), (x + cell_size, y)))
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
    maze_h = rows * cell_size
    maze_w = cols * cell_size

    # Cylinder base shell
    outer = cq.Workplane("XY").circle(radius).extrude(maze_h + base_thickness)
    inner = cq.Workplane("XY").circle(radius - base_thickness).extrude(maze_h + 1).translate((0, 0, base_thickness))
    result = outer.cut(inner)

    # Generate walls and map onto cylinder surface
    walls = generate_maze_walls(rows, cols, cell_size, seed, x_wrapping=True)
    angle_per_unit = 360.0 / maze_w

    for (x1, y1), (x2, y2) in walls:
        a1 = x1 * angle_per_unit
        a2 = x2 * angle_per_unit
        z1 = y1 + base_thickness
        z2 = y2 + base_thickness

        # Place wall segment on outer surface using hull of two small boxes
        mid_a = (a1 + a2) / 2.0
        mid_z = (z1 + z2) / 2.0
        seg_len = math.hypot((a2 - a1) * math.pi * radius / 180.0, z2 - z1)
        if seg_len < 0.01:
            continue

        angle = math.degrees(math.atan2(z2 - z1, (a2 - a1) * math.pi * radius / 180.0))

        wall = (
            cq.Workplane("XY")
            .box(seg_len + 0.2, wall_thickness, wall_height)
            .rotate((0, 0, 0), (0, 0, 1), 90 - angle)
            .translate((radius - wall_height / 2.0, 0, mid_z))
            .rotate((0, 0, 0), (0, 0, 1), mid_a)
        )
        result = result.union(wall)

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
