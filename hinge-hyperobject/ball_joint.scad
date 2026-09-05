// ball_joint.scad — Print-in-Place Ball-and-Socket Joint
// Inner sphere with stem, outer socket shell with opening
// Requires adequate clearance for print-in-place articulation

include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
socket_diameter = 15;   // mm — inner diameter of the socket
clearance       = 0.4;  // mm — gap between ball and socket
hinge_width     = 30;   // mm — width of mounting base
leaf_length     = 30;   // mm — length of stem/base plate
fn              = 0;    // quality override

$fn = fn > 0 ? fn : $preview ? 32 : 64;

ball_r       = socket_diameter / 2;
socket_r     = ball_r + clearance;
shell_t      = max(2, ball_r * 0.3);   // socket wall thickness
socket_outer = socket_r + shell_t;
stem_d       = ball_r * 0.6;           // stem connecting ball to base
opening_angle = 55;                     // socket opening half-angle (degrees)
base_h       = 3;                       // base plate thickness

module ball_joint() {
    // --- Ball with stem ---
    // Ball sphere
    translate([0, 0, socket_outer])
        sphere(r=ball_r);

    // Stem from ball down to base
    translate([0, 0, socket_outer/2])
        cyl(d=stem_d, h=socket_outer, anchor=BOTTOM);

    // Base plate for ball side
    translate([0, -leaf_length/2 - socket_outer, base_h/2])
        cuboid([hinge_width, leaf_length, base_h]);

    // Bridge from base to stem
    translate([0, -socket_outer/2, base_h/2])
        cuboid([stem_d, socket_outer, base_h]);

    // --- Socket shell ---
    translate([0, 0, socket_outer])
    difference() {
        sphere(r=socket_outer);
        sphere(r=socket_r);
        // Opening at top for print-in-place and articulation
        translate([0, 0, socket_outer/2])
            cyl(d=socket_outer * 2 * sin(opening_angle),
                h=socket_outer,
                anchor=BOTTOM);
    }

    // Socket mounting base
    translate([0, leaf_length/2 + socket_outer, base_h/2])
        cuboid([hinge_width, leaf_length, base_h]);

    // Bridge from socket to its base
    translate([0, socket_outer/2, base_h/2])
        cuboid([hinge_width * 0.4, socket_outer, base_h]);
}

ball_joint();
