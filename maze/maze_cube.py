import cadquery as cq
import math
import json
import argparse
import random


def generate_maze_walls(rows, cols, cell_size, seed):
    """Generate maze wall segments using recursive backtracker algorithm."""
    rng = random.Random(seed)
    grid = [[0] * cols for _ in range(rows)]
    walls = []

    # Recursive backtracker
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
            # Mark passage in grid (bit flags: 1=N, 2=S, 4=W, 8=E)
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

    # Convert grid to wall segments
    for r in range(rows):
        for c in range(cols):
            x = c * cell_size
            y = r * cell_size
            # South wall
            if not (grid[r][c] & 2) and r < rows - 1:
                walls.append(((x, y + cell_size), (x + cell_size, y + cell_size)))
            elif r == rows - 1:
                walls.append(((x, y + cell_size), (x + cell_size, y + cell_size)))
            # East wall
            if not (grid[r][c] & 8) and c < cols - 1:
                walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
            elif c == cols - 1:
                walls.append(((x + cell_size, y), (x + cell_size, y + cell_size)))
            # North border
            if r == 0:
                walls.append(((x, y), (x + cell_size, y)))
            # West border
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

    maze_w = cols * cell_size
    maze_h = rows * cell_size

    # Base plate
    result = cq.Workplane("XY").box(maze_w, maze_h, base_thickness).translate((maze_w / 2, maze_h / 2, base_thickness / 2))

    # Maze walls
    walls = generate_maze_walls(rows, cols, cell_size, seed)
    for (x1, y1), (x2, y2) in walls:
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length < 0.01:
            continue
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
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
