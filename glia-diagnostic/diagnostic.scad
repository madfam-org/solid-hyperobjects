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
        
        // Tube connector.
        //
        // `attach(RIGHT)` lands the connector's base flush on the bell's outer
        // cylindrical face -- tangent, with zero overlap. The union of two
        // tangent solids is non-manifold: the render came back as TWO bodies,
        // the bell and a detached 20x8x8 stub from x=24 to x=44.
        // diagnostic.py:36-41 already avoids this by extruding the connector
        // from the CENTRE of the bell so the boolean has real overlap to work
        // with, and says so. Do the same here: start the connector `overlap`
        // inside the wall and lengthen it to match, so its far end still sits
        // at the same x and the part's dimensions do not move.
        tag("keep")
        attach(RIGHT)
        down(_connector_overlap)
        cylinder(h=20 + _connector_overlap, d=8, $fn=32);

        // Air channel, bored the full length of the lengthened connector.
        tag("remove")
        attach(RIGHT)
        down(1 + _connector_overlap)
        cylinder(h=22 + _connector_overlap, d=5, $fn=32);
        
        // Locking groove for ring.
        //
        // The cutter has to overshoot the bell's top face, not stop flush with
        // it. `up(18) cylinder(h=2)` ended at exactly z = 20, coplanar with the
        // 20 mm body top, and the coplanar-face boolean left a detached shard
        // behind: the render came out as TWO bodies with genus -1 and a stray
        // pair of vertices at z = 19.9876, r = 21.999. That shard is also the
        // whole of the 1.987578 mm parity gap against diagnostic.py, which
        // measures a clean 18.0 mm.
        //
        // Overshoot by EPS in +Z and on the outer radius so no face of the
        // cutter is coincident with a face of the body. The inner radius is
        // the groove's real dimension and stays exact.
        // The groove's inner wall is the sound chamber's wall -- both are at
        // d = diaphragm_size_mm. Two faceted circles of the same nominal
        // diameter but different facet PHASE do not cancel: they crossed and
        // left four knife-edge slivers standing at z = 20, r = 22. Pull the
        // groove's inner cutter in by EPS so the annulus reaches past the
        // chamber wall and the rim comes off cleanly. The groove's own
        // dimension is set by the chamber, which is unchanged.
        tag("remove")
        position(BOTTOM)
        up(18)
        difference() {
            cylinder(h=2 + 0.1, d=diaphragm_size_mm + 4.2, $fn=64);
            cylinder(h=2 + 0.1, d=diaphragm_size_mm - 0.2, $fn=64);
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
