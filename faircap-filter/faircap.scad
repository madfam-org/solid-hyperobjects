include <../../libs/BOSL2/std.scad>
include <../../libs/BOSL2/threading.scad>

// Yantra4D Parameters
filter_type = "charcoal"; // [charcoal, ceramic, mesh, empty]
housing_od_mm = 40;
housing_length_mm = 80;

// CDG Constants from Reference PCO 1881
PCO_ID = 21.74; // Approx internal diameter
PCO_OD = 26.7;  // Thread major diameter
PCO_PITCH = 3.18;

// Built with a plain difference() against a Z-centred housing, matching
// faircap.py. The previous diff()/attach() version had two faults: the "hollow
// chamber" carried no tag("remove"), so it was unioned into the housing rather
// than bored out of it, and attach(TOP) followed by down(length/2) pushed that
// 75 mm cylinder to span z=40..115 instead of sitting inside the 80 mm body.
// The filter therefore rendered 115 mm tall and nearly solid — 131,650 mm3
// against the B-Rep's 22,655 — so the two engines disagreed by 83% on volume
// and 30% on height for the cartridge's default mode.
module faircap_filter() {
    difference() {
        cylinder(h=housing_length_mm, d=housing_od_mm, center=true, $fn=64);

        // Hollow chamber
        cylinder(h=housing_length_mm - 5, d=housing_od_mm - 4, center=true, $fn=64);

        // Flow output at Top
        translate([0, 0, housing_length_mm/2 - 5])
            cylinder(h=10, d=8, $fn=32);

        // PCO 1881 Interface (Female Thread) at Bottom
        translate([0, 0, -housing_length_mm/2 - 0.1])
            threaded_rod(
                d=PCO_OD,
                pitch=PCO_PITCH,
                l=15,
                internal=true,
                anchor=BOTTOM,
                $fn=64
            );
    }
    
    // Internal Structure based on type
    if (filter_type == "mesh") {
        up(5)
        cylinder(h=housing_length_mm-20, d=housing_od_mm-5, $fn=32)
        grid_2d(spacing=2, thickness=0.5); // Abstract mesh representation
    }
}

faircap_filter();
