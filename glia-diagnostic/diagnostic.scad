include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
tool_type = "stethoscope_head"; // [stethoscope_head, otoscope_specula]
diaphragm_size_mm = 44;
speculum_size_mm = 4; // [2.5, 3, 4, 5]
render_mode = 0;

module stethoscope_head() {
    // Glia-style bell.
    //
    // Children of a BOSL2 attachable are placed in the parent's CENTRED frame,
    // not from its bottom face: for this 20 mm-tall bell the child origin is at
    // global z = 10. A bare `up(2)` therefore started the sound chamber at
    // z = 12 and a bare `up(18)` put the locking groove at z = 28, clear of the
    // part altogether. The bell came out very nearly solid — 24968 mm^3 against
    // diagnostic.py's 9918 mm^3, a stethoscope head with no sound chamber and
    // no groove for the diaphragm ring. position(BOTTOM) moves the child origin
    // to the bottom face without reorienting it, so the offsets below are the
    // distances from the bottom face that they read as.
    diff()
    cylinder(h=20, d=diaphragm_size_mm + 4, $fn=64) {
        // Hollow sound chamber
        tag("remove")
        position(BOTTOM)
        up(2)
        cylinder(h=18.1, d=diaphragm_size_mm, $fn=64);
        
        // Tube connector
        tag("keep")
        attach(RIGHT)
        cylinder(h=20, d=8, $fn=32);
        
        tag("remove")
        attach(RIGHT)
        down(1)
        cylinder(h=22, d=5, $fn=32); // Air channel
        
        // Locking groove for ring
        tag("remove")
        position(BOTTOM)
        up(18)
        difference() {
            cylinder(h=2, d=diaphragm_size_mm + 4.1, $fn=64);
            cylinder(h=2, d=diaphragm_size_mm, $fn=64);
        }
    }
}

module otoscope_specula() {
    // Standard speculum cone
    height = 30;
    base_d = 8;
    tip_d = speculum_size_mm;
    
    // Same rule as above: these children are measured from the cone's bottom
    // face, so they need position(BOTTOM). Without it the bore started 14.9 mm
    // up a 30 mm speculum and the snap ring floated 14.5 mm above its base — a
    // speculum with no channel through it.
    diff()
    cylinder(h=height, d1=base_d, d2=tip_d, $fn=64) {
        // Hollow channel
        tag("remove")
        position(BOTTOM)
        down(0.1)
        cylinder(h=height+0.2, d1=base_d-1.5, d2=tip_d-0.8, $fn=64);
        
        // Snap ring at base
        tag("keep")
        position(BOTTOM)
        down(0.5)
        cylinder(h=2, d=base_d+1, $fn=64);
    }
}

if (render_mode == 1 || (render_mode == 0 && tool_type == "stethoscope_head")) {
    stethoscope_head();
} else if (render_mode == 2 || (render_mode == 0 && tool_type == "otoscope_specula")) {
    otoscope_specula();
}
