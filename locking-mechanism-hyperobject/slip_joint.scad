// Parametric Friction Slip Joint
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

latch_width = 15;
material_modulus = 1.5;
shrinkage_factor = 0.0;
clearance = 0.3;
fn = 0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;

// Mechanics
modulus_modifier = pow(1.5 / max(material_modulus, 0.05), 0.3);
hinge_t = 2.5 * modulus_modifier;
pin_d = 4;

render_mode = 0;

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {

if(render_mode == 0) {
    // --- Housing with monolithic leaf spring ---
    difference() {
        cuboid([40, latch_width, 18], anchor=BOTTOM);
        
        // Blade motion slot
        cuboid([42, latch_width - hinge_t*2, 20], anchor=CENTER);
        
        // Rotary pivot hole (horizontal)
        translate([-10, 0, 9]) 
        rotate([90,0,0]) 
        teardrop(d=pin_d + clearance*2, h=latch_width+1);
    }
    
    // Solid base anchor for spring
    translate([-20, 0, 0])
    cuboid([5, latch_width - hinge_t*2 - clearance*2, 18], anchor=BOTTOM+LEFT);
    
    // Monolithic Leaf Spring (rides against the blade's flat detents)
    translate([-15, 0, 18 - hinge_t*0.5])
    cuboid([35, latch_width - hinge_t*2 - clearance*2, hinge_t], anchor=BOTTOM+LEFT);
}

if(render_mode == 1) {
    // --- Actuation Blade ---
    translate([0, 30, 0])
    difference() {
        union() {
            // Rotating cam hub (squared off to friction-seat against the leaf spring)
            cuboid([12, latch_width - hinge_t*2 - clearance*2, 12], anchor=CENTER);
            
            // Blade body
            translate([6, 0, 0])
            cuboid([30, latch_width - hinge_t*2 - clearance*2, 10], anchor=LEFT);
        }
        
        // Hinge pin integration
        rotate([90,0,0]) cyl(d=pin_d, h=latch_width);
    }
}

}
