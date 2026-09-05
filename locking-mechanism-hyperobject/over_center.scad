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
cdg_mount_type = 0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;

// Mechanics
pin_d = wall_thickness * 1.5;
// Every one of these is a DERIVED width that must stay positive. At
// preset:battery_cover (latch_width = 8, wall_thickness = 2.5) the unfloored
// expressions went negative -- joint_w 2.40, link_w -2.60, the link slot -2.00
// -- so the difference() inside the rotated lever block produced nothing, the
// rotate() received an empty child and OpenSCAD failed the whole render:
//   "rotate(a = [0, -15, 0], v = undef) ... over_center.scad, line 69 ...
//    Current top level object is empty."
// Floored here, once, so the lever degrades to a thin-but-real link instead of
// vanishing.
_min_w = 0.8;
joint_w = max(_min_w, latch_width - wall_thickness * 2 - clearance * 2);
link_w  = max(_min_w, joint_w - wall_thickness * 2);
slot_w  = max(_min_w, joint_w - wall_thickness * 2 + clearance * 2);


module apply_cdg(base_x) {
    if (cdg_mount_type == 1) { // M3 Hex Nut Trap
        difference() {
            union() {
                children();
                translate([-base_x/2 - 8, 0, 0]) cuboid([16, 15, 5], anchor=BOTTOM);
                translate([base_x/2 + 8, 0, 0]) cuboid([16, 15, 5], anchor=BOTTOM);
            }
            translate([-base_x/2 - 8, 0, 0]) cyl(d=3.4, h=15);
            translate([-base_x/2 - 8, 0, 2]) cyl(d=6.2, h=10, $fn=6);
            translate([base_x/2 + 8, 0, 0]) cyl(d=3.4, h=15);
            translate([base_x/2 + 8, 0, 2]) cyl(d=6.2, h=10, $fn=6);
        }
    } else if (cdg_mount_type == 2) { // Gridfinity 42mm
        union() {
            children();
            translate([0, 0, -4.5]) prismoid(size1=[41.5, 41.5], size2=[42, 42], h=4.5, anchor=BOTTOM);
        }
    } else {
        children();
    }
}

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
            cuboid([pin_d*3, slot_w, pin_d*4], anchor=CENTER);
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
