include <BOSL2/std.scad>

// Yantra4D Parameters
tool_type = "stethoscope_head"; // [stethoscope_head, otoscope_specula]
diaphragm_size_mm = 44;
speculum_size_mm = 4; // [2.5, 3, 4, 5]
render_mode = 0;

// How far the tube connector is buried into the bell wall. Any positive value
// gives the union real overlap; 2 mm is comfortably inside the 2 mm wall
// without reaching the sound chamber.
_connector_overlap = 2;

module stethoscope_head() {
    // Glia-style bell -- built as one plain difference() mirroring
    // diagnostic.py's build_stethoscope() step for step.
    //
    // This module used to be a BOSL2 diff() with attachable children, which
    // caused both of the cartridge's stethoscope defects:
    //
    //  * Children of an attachable are placed in the parent's CENTRED frame,
    //    not from its bottom face, so a bare up(2)/up(18) put the sound
    //    chamber and the locking groove clear of the part.
    //  * diff() evaluates (parent - remove_children) + keep_children, so a
    //    tag("keep") child is unioned back AFTER every removal and no
    //    tag("remove") sibling can cut it. The tube connector was a keep
    //    child, so the air channel never bored it and the connector came out
    //    as a solid rod -- 390.18 mm^3 of the 416.16 mm^3 (4.51%) volume gap
    //    against diagnostic.py, which bores the connector through.
    //
    // Explicit translates in the global frame remove both classes of mistake
    // and make the two kernels' arithmetic directly comparable.
    outer_d = diaphragm_size_mm + 4;
    x_start = outer_d / 2 - _connector_overlap;

    difference() {
        union() {
            // Main body: z = 0 .. 20.
            cylinder(h=20, d=outer_d, $fn=64);

            // Tube connector on +X, axis at z = 10.
            //
            // Starting it at exactly x = outer_d/2 would leave it tangent to
            // the bell's cylindrical face, and the union of two tangent
            // solids is non-manifold (the render came back as two bodies: the
            // bell and a detached stub). Bury it _connector_overlap into the
            // wall -- enough overlap for the boolean, not enough to reach the
            // sound chamber -- and lengthen it to match so its far end still
            // sits at the same x and the part's dimensions do not move.
            translate([x_start, 0, 10])
                rotate([0, 90, 0])
                    cylinder(h=20 + _connector_overlap, d=8, $fn=32);
        }

        // Hollow sound chamber, leaving 2 mm of floor: z = 2 .. 20.1.
        translate([0, 0, 2])
            cylinder(h=18.1, d=diaphragm_size_mm, $fn=64);

        // Air channel down the connector, overshooting its buried end by 1 mm
        // so no cutter face is coincident with the bell wall.
        translate([x_start - 1, 0, 10])
            rotate([0, 90, 0])
                cylinder(h=21 + _connector_overlap, d=5, $fn=32);

        // Locking groove for the diaphragm retaining ring: an annulus from the
        // chamber wall out to the body wall, z = 18 .. 20.
        //
        // The +Z overshoot keeps the cutter's top face off the body's top
        // face; the radial EPS keeps the annulus's two cylindrical faces off
        // the body's outer face and the chamber's wall. Both are needed: two
        // faceted circles of the same nominal diameter but different facet
        // PHASE do not cancel, and previously left four knife-edge slivers
        // standing at z = 20, r = 22. diagnostic.py applies the same radial
        // EPS, so the two kernels remove the same annulus.
        translate([0, 0, 18])
            difference() {
                cylinder(h=2 + 0.1, d=outer_d + 0.2, $fn=64);
                cylinder(h=2 + 0.1, d=diaphragm_size_mm - 0.2, $fn=64);
            }
    }
}

module otoscope_specula() {
    // Standard speculum cone -- built as one plain difference() mirroring
    // diagnostic.py's build_otoscope() step for step.
    //
    // This module used to be a BOSL2 diff() with attachable children, which
    // caused the same two faults the stethoscope had:
    //
    //  * Children are placed in the parent's CENTRED frame, so the bore
    //    started 14.9 mm up a 30 mm speculum and the snap ring floated.
    //  * diff() evaluates (parent - remove_children) + keep_children, so the
    //    tag("keep") snap ring was unioned back AFTER the bore ran and the
    //    channel stopped dead at the ring -- 51.68 mm^3 of plug that
    //    diagnostic.py bores out, the whole of the 51.43 mm^3 (12.68%)
    //    volume parity gap.
    //
    // A plain difference() over an explicit union has neither problem, and
    // every extent below is diagnostic.py's own.
    height = 30;
    base_d = 8;
    tip_d = speculum_size_mm;

    difference() {
        union() {
            // Cone: z = 0 .. 30.
            cylinder(h=height, d1=base_d, d2=tip_d, $fn=64);

            // Snap ring at the base: z = -0.5 .. 1.5.
            translate([0, 0, -0.5])
                cylinder(h=2, d=base_d+1, $fn=64);
        }

        // Hollow channel: z = -0.1 .. 30.1, d1 = base_d-1.5 tapering to
        // tip_d-0.8 -- exactly diagnostic.py's extents, so the two kernels
        // remove the same volume. It runs through the snap ring, which is
        // what a speculum's channel does.
        translate([0, 0, -0.1])
            cylinder(h=height+0.2, d1=base_d-1.5, d2=tip_d-0.8, $fn=64);
    }
}

if (render_mode == 1 || (render_mode == 0 && tool_type == "stethoscope_head")) {
    stethoscope_head();
} else if (render_mode == 2 || (render_mode == 0 && tool_type == "otoscope_specula")) {
    otoscope_specula();
}
