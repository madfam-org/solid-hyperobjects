// Parametric Compliant Bistable Locking Mechanism — Engineered for AM
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
latch_width = 15;
wall_thickness = 2;
base_length = 40;
hook_depth = 2;
clearance = 0.3;
fn = 0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;

// Mechanics for Elastomeric/PP/PETG Printing
hinge_t = 0.8; 
hinge_l = 1.5;

render_mode = 0;

if (render_mode == 0) {
    // --- Rigid Outer Frame Constraint ---
    base_h = wall_thickness * 3;
    
    difference() {
        cuboid([base_length, latch_width, base_h], anchor=BOTTOM);
        // Interior relief channel
        translate([0, 0, wall_thickness])
        cuboid([base_length - wall_thickness*2, latch_width+1, base_h], anchor=BOTTOM);
    }
    
    // --- Compliant Bistable Energy Beam ---
    arch_len = base_length - wall_thickness*2 - hinge_l*2;
    arch_h = arch_len * 0.15; // Deflection height barrier
    
    // Left living hinge
    translate([-arch_len/2 - hinge_l/2, 0, base_h/2])
    cuboid([hinge_l, latch_width, hinge_t], anchor=CENTER);
    
    // Right living hinge
    translate([arch_len/2 + hinge_l/2, 0, base_h/2])
    cuboid([hinge_l, latch_width, hinge_t], anchor=CENTER);
    
    // Continuous Sine Arch (Euler Mode)
    steps = 40;
    for(i=[0:steps-1]) {
        t0 = i/steps;
        t1 = (i+1)/steps;
        
        x0 = -arch_len/2 + (arch_len) * t0;
        x1 = -arch_len/2 + (arch_len) * t1;
        z0 = arch_h * sin(t0 * 180);
        z1 = arch_h * sin(t1 * 180);
        
        hull() {
            translate([x0, 0, base_h/2 + z0])
            cuboid([arch_len/steps*0.6, latch_width, wall_thickness*0.6], anchor=CENTER);
            translate([x1, 0, base_h/2 + z1])
            cuboid([arch_len/steps*0.6, latch_width, wall_thickness*0.6], anchor=CENTER);
        }
    }
    
    // --- Actuation Catch & Hook ---
    translate([0, 0, base_h/2 + arch_h])
    union() {
        // Actuator boss
        cuboid([wall_thickness*2, latch_width*0.6, wall_thickness*1.5], anchor=BOTTOM);
        // Hook
        translate([0, 0, wall_thickness*1.5])
        prismoid(size1=[wall_thickness*2, latch_width*0.6], size2=[wall_thickness, latch_width*0.6], h=hook_depth, shift=[wall_thickness/2, 0], anchor=BOTTOM);
    }
    
    // --- Yield Limit Stop ---
    // Mathematically positioned to prevent irreversible plastic deformation of the beam
    stop_h = (base_h/2) - arch_h*0.5; 
    translate([0, 0, wall_thickness])
    cuboid([wall_thickness*3, latch_width, max(0.5, stop_h)], anchor=BOTTOM);
}
