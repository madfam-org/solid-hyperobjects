// Parametric Topological Interlock (Osteomorphic Blocks)
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

matrix_size = 3;
clearance = 0.3;
shrinkage_factor = 0.0;
fn = 0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;
block_s = 15;

render_mode = 0;

// Topological block with overlapping geometric denial tabs
module interlocking_block() {
    sz = block_s - clearance;
    difference() {
        union() {
            cuboid([sz, sz, sz], anchor=CENTER);
            // Positive interlocking tabs
            translate([sz/2, 0, 0]) cyl(d=sz/2, h=sz*0.6, orient=RIGHT, anchor=CENTER);
            translate([0, sz/2, 0]) cyl(d=sz/2, h=sz*0.6, orient=FRONT, anchor=CENTER);
        }
        // Negative receptor constraints
        translate([-sz/2, 0, 0]) cyl(d=sz/2 + clearance, h=sz*0.8, orient=RIGHT, anchor=CENTER);
        translate([0, -sz/2, 0]) cyl(d=sz/2 + clearance, h=sz*0.8, orient=FRONT, anchor=CENTER);
    }
}

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {

if (render_mode == 0) {
    // --- Matrix of Blocks ---
    for(x=[0:matrix_size-1]) {
        for(y=[0:matrix_size-1]) {
            translate([x*block_s, y*block_s, 0])
            interlocking_block();
        }
    }
}

if (render_mode == 1) {
    // --- Peripheral Framework ---
    // Constraints the matrix so blocks cannot slide apart laterally,
    // creating an infinitely locked planar geometry.
    frame_w = matrix_size * block_s + block_s;
    wall_t = 4;
    
    translate([-block_s/2, -block_s/2, -block_s/2])
    difference() {
        cuboid([frame_w + wall_t*2, frame_w + wall_t*2, block_s], anchor=BOTTOM+LEFT);
        
        // Hollow out center
        translate([wall_t, wall_t, -0.1])
        cuboid([frame_w, frame_w, block_s+1], anchor=BOTTOM+LEFT);
        
        // Inner receptor slots for the edge blocks
        for(x=[0:matrix_size-1]) {
            translate([wall_t + block_s/2 + x*block_s, wall_t, block_s/2])
            cyl(d=block_s/2 + clearance, h=block_s*0.8, orient=FRONT, anchor=CENTER);
            
            translate([wall_t, wall_t + block_s/2 + x*block_s, block_s/2])
            cyl(d=block_s/2 + clearance, h=block_s*0.8, orient=RIGHT, anchor=CENTER);
        }
    }
}

}
