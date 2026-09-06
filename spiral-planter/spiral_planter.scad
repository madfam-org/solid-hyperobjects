// Yantra4D Spiral Planter
// Uses dotSCAD archimedean_spiral for wall path generation
// Creates a planter with spiral-textured walls and optional drainage

use <dotSCAD/src/archimedean_spiral.scad>
use <dotSCAD/src/archimedean_spiral_extrude.scad>

// --- Parameters (overridden by platform) ---
turns = 3;
spacing = 8;
wall_thickness = 2;
base_diameter = 60;
height = 80;
drainage = true;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 48;

base_r = base_diameter / 2;
top_r = base_r + turns * spacing;
drainage_hole_d = 5;
drainage_count = 4;

// Inner-wall taper: the radius the hollow gains per mm of height. The hollow
// spans z = wall_thickness .. height, so its slope is measured over THAT span
// (not over `height`), which is what puts the rim wall at exactly
// `wall_thickness`.
_inner_slope = (top_r - base_r) / (height - wall_thickness);
_cut_over = 1;  // cut overshoot past the rim (mm)

// Outer wall with spiral texture
module planter_body() {
    difference() {
        // Outer tapered cylinder with spiral groove
        cylinder(h=height, r1=base_r, r2=top_r, $fn=$fn);

        // Inner hollow.
        //
        // The cut cone has to overshoot the RIM without changing its taper, and
        // must not touch the floor. This used to read `h = height + 1` while
        // keeping the end radii `base_r - wall_thickness` -> `top_r -
        // wall_thickness`: that spreads the same radius span over 81 mm instead
        // of the 78 mm the hollow actually occupies, so the cone is FLATTER than
        // the outer wall and falls short of it by a widening margin. At the
        // defaults the rim wall came out 2.889 mm against the declared 2.000 mm,
        // and the shell carried 15.3 % more material than spiral_planter.py's,
        // which lands the wall at exactly `wall_thickness` at every height.
        //
        // Extend it past the rim ALONG ITS OWN SLOPE instead. The base stays at
        // z = wall_thickness: overshooting downward as well would bore straight
        // through the floor the drainage holes are cut in.
        translate([0, 0, wall_thickness])
            cylinder(h=height - wall_thickness + _cut_over,
                     r1=base_r - wall_thickness,
                     r2=top_r - wall_thickness + _inner_slope * _cut_over,
                     $fn=$fn);

        // Spiral groove on exterior
        for (i = [0 : turns * 36 - 1]) {
            angle = i * 10;
            z = i / (turns * 36) * height;
            r = base_r + (top_r - base_r) * (z / height);
            translate([r * cos(angle), r * sin(angle), z])
                sphere(d=wall_thickness * 0.6);
        }
    }
}

// Drainage holes in the base
module drainage_holes() {
    if (drainage) {
        for (i = [0 : drainage_count - 1]) {
            angle = i * 360 / drainage_count;
            translate([base_r * 0.5 * cos(angle), base_r * 0.5 * sin(angle), -1])
                cylinder(d=drainage_hole_d, h=wall_thickness + 2, $fn=24);
        }
    }
}

// Saucer / drip tray
module saucer() {
    difference() {
        cylinder(h=8, r=top_r + 5, $fn=$fn);
        translate([0, 0, 2])
            cylinder(h=7, r=top_r + 3, $fn=$fn);
    }
}

module planter() {
    difference() {
        planter_body();
        drainage_holes();
    }
}

// --- Render mode dispatch ---
if (render_mode == 0) {
    planter();
} else if (render_mode == 1) {
    saucer();
}
