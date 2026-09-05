// Yantra4D NEMA Motor Mount
// Parametric motor bracket for NEMA 17/23/34 stepper motors
// Uses NopSCADlib dimensions for accurate motor hole patterns

include <../../libs/BOSL2/std.scad>

// --- Parameters (overridden by platform) ---
nema_size = 17;
wall_thickness = 4;
base_thickness = 5;
mounting_style = 0;  // 0 = flat plate, 1 = L-bracket
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 48;

// NEMA motor dimensions lookup
// [face_width, hole_spacing, shaft_hole_d, screw_d, body_length]
function nema_dims(size) =
    size == 17 ? [42.3, 31, 22, 3, 48] :
    size == 23 ? [56.4, 47.14, 38.1, 5.5, 56] :
    size == 34 ? [86.0, 69.6, 73, 5.5, 66] :
    [42.3, 31, 22, 3, 48];  // default to 17

dims = nema_dims(nema_size);
face_w = dims[0];
hole_spacing = dims[1];
shaft_hole_d = dims[2];
screw_d = dims[3];
body_len = dims[4];

plate_size = face_w + wall_thickness * 2;
bracket_height = mounting_style == 1 ? face_w : 0;

// Mounting base holes
mount_hole_d = 5;
mount_hole_spacing = plate_size - 10;

module motor_plate() {
    // The plate is anchored BOT, so it spans z = 0 .. base_thickness and its
    // mid-plane is at base_thickness/2. Every cutter below is `h =
    // base_thickness + 2, anchor=CENTER` — the usual "1 mm proud at each end"
    // through-cut — so it has to be centred on that mid-plane. Centring it on
    // z = 0 instead (which is what these cutters used to do) sank half of each
    // cylinder below the plate and left the top base_thickness/2 - 1 mm of
    // material uncut: the shaft bore and all eight screw holes were blind, and
    // the plate came out 7.4% heavier than mount.py's.
    difference() {
        // Base plate using BOSL2 cuboid
        cuboid([plate_size, plate_size, base_thickness], anchor=BOT);

        // Center shaft hole
        translate([0, 0, base_thickness/2])
            cylinder(d=shaft_hole_d + 1, h=base_thickness + 2, anchor=CENTER, $fn=$fn);

        // Motor screw holes (4 corners)
        for (x = [-1, 1], y = [-1, 1])
            translate([x * hole_spacing/2, y * hole_spacing/2, base_thickness/2])
                cylinder(d=screw_d + 0.3, h=base_thickness + 2, anchor=CENTER, $fn=24);

        // Mounting holes for attaching to surface
        for (x = [-1, 1], y = [-1, 1])
            translate([x * mount_hole_spacing/2, y * mount_hole_spacing/2, base_thickness/2])
                cylinder(d=mount_hole_d, h=base_thickness + 2, anchor=CENTER, $fn=24);
    }
}

module l_bracket() {
    motor_plate();

    // Vertical bracket wall using BOSL2 cuboid
    translate([0, -plate_size/2 + wall_thickness/2, (bracket_height + base_thickness)/2])
        difference() {
            cuboid([plate_size, wall_thickness, bracket_height + base_thickness], anchor=CENTER);
            // Lightening holes
            translate([0, 0, 0])
                xcyl(d=bracket_height * 0.5, l=plate_size + 2, $fn=$fn);
        }
}

// --- Render mode dispatch ---
if (render_mode == 0) {
    if (mounting_style == 0) {
        motor_plate();
    } else {
        l_bracket();
    }
}
// render_mode == 1: simplified NEMA motor reference body
if (render_mode == 1) {
    color("#34495e")
    translate([0, 0, base_thickness])
    union() {
        // Motor body (square with rounded edges approximated as cube)
        translate([0, 0, body_len/2])
            cube([face_w, face_w, body_len], center=true);

        // Front face plate (circular boss)
        cylinder(d=shaft_hole_d + 2, h=2, $fn=$fn);

        // Shaft
        translate([0, 0, -10])
            cylinder(d=5, h=10 + body_len + 5, $fn=$fn);
    }
}
