// Parametric Over-Center Linkage Lock — Engineered for AM
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
lever_length = 30;
over_center_offset = 2; // Distance past geometric center for snapping
wall_thickness = 2.5;
latch_width = 15;
base_length = 40;
clearance = 0.3; // Nominal sliding fit
fn = 0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;

// Mechanics
pin_d = wall_thickness * 1.5;
joint_w = latch_width - wall_thickness * 2 - clearance * 2;

render_mode = 0;

if (render_mode == 0) {
    // --- Base & Lever Assembly ---
    // Base Mount
    difference() {
        cuboid([base_length/2, latch_width, pin_d*2.5], anchor=BOTTOM+RIGHT);
        
        // Pivot Slot
        translate([0, 0, pin_d*1.5])
        cuboid([pin_d*4, joint_w + clearance*2, pin_d*4], anchor=CENTER);
        
        // Pivot Teardrop Hole (horizontal layer strength)
        translate([0, 0, pin_d*1.5])
        rotate([90,0,0])
        teardrop(d=pin_d + clearance*2, h=latch_width+1);
    }
    
    // Base Pin
    translate([0, 0, pin_d*1.5])
    rotate([90,0,0])
    cyl(d=pin_d, h=latch_width, rounding=pin_d*0.1);

    // Actuation Lever
    rotate([0, -15, 0]) {
        difference() {
            union() {
                // Pivot barrel
                translate([0, 0, pin_d*1.5])
                rotate([90,0,0])
                cyl(d=pin_d*2, h=joint_w);
                
                // Lever Body
                translate([0, 0, pin_d*1.5])
                cuboid([lever_length, joint_w, wall_thickness], anchor=LEFT);
            }
            // Link attachment slot
            link_pivot_x = lever_length * 0.4;
            translate([link_pivot_x, 0, pin_d*1.5 + over_center_offset])
            cuboid([pin_d*3, joint_w - wall_thickness*2 + clearance*2, pin_d*4], anchor=CENTER);
        }
        
        // Link attachment pin
        link_pivot_x = lever_length * 0.4;
        translate([link_pivot_x, 0, pin_d*1.5 + over_center_offset])
        rotate([90,0,0])
        cyl(d=pin_d, h=joint_w);

        // Tensile Link Arm (connects past singularity point)
        translate([link_pivot_x, 0, pin_d*1.5 + over_center_offset])
        rotate([0, 20, 0])
        difference() {
            union() {
                link_w = joint_w - wall_thickness*2;
                // Base barrel
                rotate([90,0,0])
                cyl(d=pin_d*2, h=link_w);
                
                // Arm body
                cuboid([lever_length*0.7, link_w, wall_thickness], anchor=LEFT);
                
                // Hook loop
                translate([lever_length*0.7, 0, 0])
                rotate([90,0,0])
                cyl(d=pin_d*2, h=link_w);
            }
            // Clearance hole for connecting pin
            rotate([90,0,0])
            teardrop(d=pin_d + clearance*2, h=latch_width);
        }
    }
}

if (render_mode == 1) {
    // --- Hook Catch ---
    catch_offset_x = lever_length * 0.8;
    
    translate([catch_offset_x, 0, 0])
    difference() {
        cuboid([base_length/3, latch_width, pin_d*2.5], anchor=BOTTOM);
        
        // Hook undercut geometry (retention angle)
        translate([-base_length/6, 0, pin_d*1.8])
        rotate([0, 75, 0])
        cuboid([pin_d*2, latch_width+1, pin_d*3], anchor=CENTER);
    }
}
