// living_hinge.scad — Parametric Living Hinge
// Two flat leaves connected by a thin flexible web
// Best printed in PLA (short-term) or TPU (high-cycle)

include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
hinge_width     = 30;    // mm — total width of the hinge
hinge_thickness = 0.6;   // mm — flexible web thickness
leaf_length     = 30;    // mm — length of each leaf
bend_angle      = 90;    // degrees — visualization bend angle
fn              = 0;     // quality override

$fn = fn > 0 ? fn : $preview ? 24 : 48;

leaf_h = 3;  // leaf plate thickness

module living_hinge() {
    web_len = max(hinge_thickness, 0.3);

    // Bottom leaf — flat on build plate
    translate([0, -web_len/2 - leaf_length/2, leaf_h/2])
        cuboid([hinge_width, leaf_length, leaf_h]);

    // Thin flexible web connecting the two leaves
    translate([0, 0, leaf_h/2])
        cuboid([hinge_width, web_len, leaf_h]);

    // Top leaf — rotated to show bend angle
    translate([0, web_len/2, leaf_h])
        rotate([-(180 - bend_angle), 0, 0])
        translate([0, leaf_length/2, -leaf_h/2])
            cuboid([hinge_width, leaf_length, leaf_h]);
}

living_hinge();
