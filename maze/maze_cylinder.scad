// Yantra4D wrapper — Maze Cylinder
// Maze wrapped onto a cylindrical shell.
//
// The maze comes from maze_kernel.scad, the shared deterministic kernel whose
// Python half is inlined in maze_cylinder.py: same 32-bit LCG, same
// backtracker, same cell and neighbour order, so this file and
// maze_cylinder.py render the SAME maze for the same seed. The field wraps in
// x, so it closes on itself and carries no east or west rim.
//
// Wall placement mirrors the CadQuery side exactly: one box per segment,
// rotated into the segment's direction on the unrolled surface, stood off at
// radius - wall_height/2 and swung round to the segment's mid-angle. The
// previous hull()-of-two-plates construction was a different solid and was
// half the reason the two engines disagreed.

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

// Match the CadQuery side's circular shell — see maze_coaster.scad for why the
// OpenSCAD default (30 facets) is not enough.
$fn = 180;

radius = diameter / 2;
maze_h = rows * cell_size;
maze_w = cols * cell_size;

grid = mz_grid(rows, cols, seed, true);
walls = mz_walls(grid, rows, cols, cell_size, true);

angle_per_unit = 360 / maze_w;

union() {
    // Cylinder base shell
    difference() {
        cylinder(h = maze_h + base_thickness, r = radius);
        translate([0, 0, base_thickness])
            cylinder(h = maze_h + 1, r = radius - base_thickness);
    }

    // Maze walls on the outer surface
    for (w = walls) {
        a1 = w[0][0] * angle_per_unit;
        a2 = w[1][0] * angle_per_unit;
        z1 = w[0][1] + base_thickness;
        z2 = w[1][1] + base_thickness;
        mid_a = (a1 + a2) / 2;
        mid_z = (z1 + z2) / 2;
        // Arc length of the segment's angular span, at the shell radius.
        arc = (a2 - a1) * PI * radius / 180;
        seg_len = norm([arc, z2 - z1]);
        if (seg_len >= 0.01) {
            rotate([0, 0, mid_a])
                translate([radius - wall_height / 2, 0, mid_z])
                    rotate([0, 0, 90 - atan2(z2 - z1, arc)])
                        cube([seg_len + 0.2, wall_thickness, wall_height],
                             center = true);
        }
    }
}
