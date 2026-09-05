// Yantra4D wrapper — Maze Cube
// Square maze on a rectangular base plate with raised walls.
//
// The maze comes from maze_kernel.scad, the shared deterministic kernel whose
// Python half is inlined in maze_cube.py: same 32-bit LCG, same backtracker,
// same cell and neighbour order, so this file and maze_cube.py render the SAME
// maze for the same seed.

rows = 10;
cols = 10;
cell_size = 5;
wall_thickness = 1.2;
wall_height = 3;
base_thickness = 2;
seed = 123;
render_mode = 0;

use <maze_kernel.scad>

maze_w = cols * cell_size;
maze_h = rows * cell_size;

grid = mz_grid(rows, cols, seed);
walls = mz_walls(grid, rows, cols, cell_size);

union() {
    // Base plate
    cube([maze_w, maze_h, base_thickness]);

    // Maze walls, each a box on the plate — placed exactly as the CadQuery
    // side places them.
    for (w = walls) {
        x1 = w[0][0];
        y1 = w[0][1];
        x2 = w[1][0];
        y2 = w[1][1];
        cx = (x1 + x2) / 2;
        cy = (y1 + y2) / 2;
        len_w = norm([x2 - x1, y2 - y1]);
        if (len_w >= 0.01) {
            translate([cx, cy, base_thickness + wall_height / 2])
                rotate([0, 0, atan2(y2 - y1, x2 - x1)])
                    cube([len_w, wall_thickness, wall_height], center = true);
        }
    }
}
