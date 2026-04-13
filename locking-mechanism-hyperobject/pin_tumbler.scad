// Parametric Pin-Tumbler Core — Engineered for AM
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
clearance = 0.3; // Nominal transition fit
num_pins = 5;
shrinkage_factor = 0.0;
fn = 0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;

plug_d = 12;
stator_d = 20;
core_l = 10 + num_pins * 6;
pin_d = 2.5;
pin_pitch = 6;
key_gap = 1.5;

render_mode = 0;

// Pseudo-random bitting based on index
function bitting(i) = 2.0 + (i % 3) * 1.5;

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {

if (render_mode == 0) {
    // --- Cylinder Plug ---
    difference() {
        cyl(d=plug_d - clearance, h=core_l, orient=RIGHT, anchor=LEFT);
        
        // Keyway channel
        translate([0, 0, -plug_d/4])
        cuboid([core_l+1, key_gap, plug_d], anchor=CENTER);
        
        // Pin chambers along shear line
        for (i=[0:num_pins-1]) {
            translate([6 + i*pin_pitch, 0, plug_d/2])
            cyl(d=pin_d + clearance*1.5, h=plug_d*0.8, anchor=TOP);
        }
    }
}

if (render_mode == 1) {
    // --- Stator (Housing) ---
    difference() {
        cyl(d=stator_d, h=core_l, orient=RIGHT, anchor=LEFT);
        
        // Internal plug bore
        cyl(d=plug_d + clearance, h=core_l+1, orient=RIGHT, anchor=LEFT);
        
        // Driver pin / spring chambers
        for (i=[0:num_pins-1]) {
            translate([6 + i*pin_pitch, 0, plug_d/2 - clearance])
            cyl(d=pin_d + clearance*1.5, h=stator_d, anchor=BOTTOM);
        }
    }
}

if (render_mode == 2) {
    // --- Keys and Pins ---
    // Key Blade & Bow
    translate([0, 0, -plug_d]) {
        difference() {
            // Raw Blade
            cuboid([core_l, key_gap - clearance, plug_d*0.8], anchor=LEFT);
            
            // Generate exact bitting cuts 
            for (i=[0:num_pins-1]) {
                // bitting maps to depth removed from top of key
                cut_depth = plug_d*0.4 - bitting(i); 
                translate([6 + i*pin_pitch, 0, plug_d*0.4])
                rotate([0, 90, 0])
                cyl(d1=pin_d*1.5, d2=0.1, h=cut_depth*2, anchor=BOTTOM);
            }
        }
        
        // Key Bow (handle)
        translate([0, 0, 0])
        cyl(d=stator_d, h=key_gap - clearance, orient=RIGHT, anchor=RIGHT);
    }
    
    // Print-in-place horizontal pins (prevents Z-shear breakage)
    for (i=[0:num_pins-1]) {
        translate([i*10, plug_d*1.5, 0]) {
            // Key pin (contacts key)
            cyl(d=pin_d, h=bitting(i), orient=RIGHT);
            // Driver pin (contacts spring)
            translate([0, pin_d*2, 0])
            cyl(d=pin_d, h=3, orient=RIGHT);
        }
    }
}

}
