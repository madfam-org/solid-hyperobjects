// pin_hinge.scad — Parametric Multi-Knuckle Pin Hinge
// Interleaving knuckle cylinders around a central pin
// Print-in-place with clearance gap between knuckles

include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
hinge_width   = 30;    // mm — total width along hinge axis
leaf_length   = 30;    // mm — length of each leaf plate
pin_diameter  = 4;     // mm — hinge pin diameter
clearance     = 0.4;   // mm — gap between knuckles
num_knuckles  = 4;     // number of knuckle segments
fn            = 0;     // quality override

$fn = fn > 0 ? fn : $preview ? 24 : 48;

leaf_h        = 3;     // leaf plate thickness
knuckle_od    = pin_diameter * 2.5;  // knuckle outer diameter
knuckle_gap   = clearance;           // gap between adjacent knuckles

// Compute knuckle segment width
knuckle_w     = (hinge_width - (num_knuckles - 1) * knuckle_gap) / num_knuckles;

module leaf_plate(side) {
    // side: -1 = left leaf, +1 = right leaf
    translate([0, side * (leaf_length/2 + knuckle_od/2), leaf_h/2])
        cuboid([hinge_width, leaf_length, leaf_h]);
}

module knuckle(x_pos) {
    translate([x_pos, 0, 0])
        rotate([0, 90, 0])
        difference() {
            cyl(d=knuckle_od, h=knuckle_w, anchor=BOTTOM);
            cyl(d=pin_diameter + clearance, h=knuckle_w + 1, anchor=BOTTOM);
        }
}

module pin_hinge() {
    // Left leaf plate
    leaf_plate(-1);

    // Right leaf plate
    leaf_plate(1);

    // Knuckle barrel — alternating left/right
    start_x = -hinge_width/2 + knuckle_w/2;
    for (i = [0 : num_knuckles - 1]) {
        x = start_x + i * (knuckle_w + knuckle_gap);
        side = (i % 2 == 0) ? -1 : 1;

        // Knuckle cylinder
        knuckle(x);

        // Bridge connecting knuckle to its leaf
        translate([x, side * knuckle_od/2, leaf_h/2])
            cuboid([knuckle_w, knuckle_od/2, leaf_h]);
    }

    // Central pin (full length, slightly smaller for clearance)
    rotate([0, 90, 0])
        cyl(d=pin_diameter, h=hinge_width, anchor=CENTER);
}

pin_hinge();
