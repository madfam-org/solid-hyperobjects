import cadquery as cq
import math
import json
import argparse
import random


def generate_maze_walls(rows, cols, cell_size, seed):
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
            if not (grid[r][c] & 8) and c < cols - 1:
                walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
            elif c == cols - 1:
                walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
            if r == 0:
                walls.append(((x, y), (x + cell_size, y)))
            if c == 0:
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
    walls = generate_maze_walls(rows, cols, cell_size, seed)
    offset_x = -maze_w / 2.0
    offset_y = -maze_h / 2.0

    # Build walls clipped to circle
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
