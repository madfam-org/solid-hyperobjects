// Yantra4D — Tolerance Calibration Comb
include <../../libs/BOSL2/std.scad>

shrinkage_factor = 0.0;
material_modulus = 1.5; // Unused geometric, but present for UI compatibility
fn = 0; $fn = fn > 0 ? fn : $preview ? 32 : 64;

render_mode = 0;

clearances = [0.05, 0.10, 0.20, 0.35, 0.50];
pin_w = 6;
pin_t = 6;
pin_l = 15;
pitch = 12;

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {

if(render_mode == 0) {
    // --- Comb Frame (Receiving Sockets) ---
    difference() {
        cuboid([pitch * len(clearances) + pitch/2, 20, 10], anchor=BOTTOM+LEFT);
        
        // Negative sockets scaled by exact clearance gaps
        for(i = [0 : len(clearances)-1]) {
            c = clearances[i];
            translate([pitch + i*pitch, 10, 5])
            cuboid([pin_w + c*2, 20 + 2, pin_t + c*2], anchor=CENTER);
            
            // Text label on top surface indicating clearance
            translate([pitch + i*pitch, 2, 10 - 0.5])
            rotate([0, 0, 90])
            linear_extrude(1)
            text(str(c), size=3, halign="center", valign="center");
        }
    }
}

if(render_mode == 1) {
    // --- Slider Tabs (Pins) ---
    translate([0, 30, 0])
    union() {
        cuboid([pitch * len(clearances) + pitch/2, 8, 10], anchor=BOTTOM+LEFT);
        for(i = [0 : len(clearances)-1]) {
            // These pins are strictly nominal geometry, leaving the variance fully on the socket block
            translate([pitch + i*pitch, 8, 5])
            cuboid([pin_w, pin_l, pin_t], anchor=BOTTOM+FRONT);
        }
    }
}

}
