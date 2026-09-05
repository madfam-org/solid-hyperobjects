// Yantra4D wrapper — Maze Coaster
// Flat circular coaster with maze walls on top.
//
// The maze comes from maze_kernel.scad, the shared deterministic kernel whose
// Python half is inlined in maze_coaster.py: same 32-bit LCG, same backtracker,
// same cell and neighbour order, so this file and maze_coaster.py render the
// SAME maze for the same seed. Walls are boxes placed one per segment, exactly
// as the CadQuery side places them, rather than a 2D union — a swept polygon
// union and a set of boxes do not agree at the corners.

rows = 10;
cols = 10;
cell_size = 5;
wall_thickness = 1.2;
wall_height = 3;
base_thickness = 2;
seed = 123;
diameter = 100;
render_mode = 0;

use <maze_kernel.scad>

// Match the CadQuery side's circle. OpenSCAD's default $fa=12 tessellates a
// cylinder into 30 facets, whose inscribed Y-extent is 99.45 mm on a 100 mm
// disc — a 0.55 mm parity gap that has nothing to do with the maze. 180 facets
// put the chord error at 0.008 mm, under the exporter's own tolerance.
$fn = 180;

radius = diameter / 2;
maze_w = cols * cell_size;
maze_h = rows * cell_size;

grid = mz_grid(rows, cols, seed);
walls = mz_walls(grid, rows, cols, cell_size);

offset_x = -maze_w / 2;
offset_y = -maze_h / 2;

union() {
    // Base disc
    cylinder(h = base_thickness, r = radius);

    // Maze walls, each a box on the disc — skipped when its midpoint falls
    // outside the disc, the same test the CadQuery side applies.
    for (w = walls) {
        x1 = w[0][0] + offset_x;
        y1 = w[0][1] + offset_y;
        x2 = w[1][0] + offset_x;
        y2 = w[1][1] + offset_y;
        cx = (x1 + x2) / 2;
        cy = (y1 + y2) / 2;
        len_w = norm([x2 - x1, y2 - y1]);
        if (norm([cx, cy]) <= radius - 1 && len_w >= 0.01) {
            translate([cx, cy, base_thickness + wall_height / 2])
                rotate([0, 0, atan2(y2 - y1, x2 - x1)])
                    cube([len_w, wall_thickness, wall_height], center = true);
        }
    }
}
