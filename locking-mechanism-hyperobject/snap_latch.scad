// Parametric Snap-Fit Latch — Engineered for AM
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
latch_width = 15;
hook_depth = 2;
spring_angle = 15;
wall_thickness = 2;
base_length = 40;
clearance = 0.3;
fn = 0;
cdg_mount_type = 0;
material_modulus = 1.5;
shrinkage_factor = 0.0;

// Derived
$fn = fn > 0 ? fn : $preview ? 32 : 64;

// Modulus tuning: stiffer material (higher modulus) gets thinner arm
modulus_modifier = pow(1.5 / max(material_modulus, 0.05), 0.3);
arm_length = base_length * 0.7;
arm_thickness = wall_thickness * 0.8 * modulus_modifier;
base_height = wall_thickness * 2.5;
fillet_r = arm_thickness * 1.5;

entry_angle = 35;
retention_angle = 85;

// render_mode: 0 = latch_arm, 1 = striker_plate

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

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {
if (render_mode == 0) {
    // --- Base Mount ---
    base_l = base_length - arm_length;
    translate([-base_l, 0, 0])
        cuboid([base_l, latch_width, base_height], anchor=BOTTOM+LEFT);

    // --- Cantilever Beam & Hook ---
    translate([0, 0, base_height/2 - arm_thickness/2])
    rotate([0, -spring_angle, 0]) {
        // Flexible Beam
        cuboid([arm_length, latch_width, arm_thickness], anchor=BOTTOM+LEFT);
        
        // Stress Relief Fillets at Root
        translate([0, 0, arm_thickness])
            prismoid(size1=[fillet_r*2, latch_width], size2=[0, latch_width], h=fillet_r, shift=[fillet_r,0], anchor=BOTTOM+LEFT);
        translate([0, 0, 0])
            rotate([180, 0, 0])
            prismoid(size1=[fillet_r*2, latch_width], size2=[0, latch_width], h=fillet_r, shift=[fillet_r,0], anchor=BOTTOM+LEFT);

        // Hook Profile
        hook_l = hook_depth / tan(entry_angle);
        retention_offset = hook_depth / tan(retention_angle);
        
        translate([arm_length, 0, arm_thickness])
        rotate([90,0,0])
        linear_extrude(height=latch_width, center=true)
        polygon([
            [0, 0],
            [-retention_offset, hook_depth],
            [hook_l, 0]
        ]);
        
        // Undercut Support
        translate([arm_length, 0, 0])
        rotate([90,0,0])
        linear_extrude(height=latch_width, center=true)
        polygon([
            [0, 0],
            [hook_l, 0],
            [0, -arm_thickness]
        ]);
    }
}

if (render_mode == 1) {
    // --- Striker Plate ---
    plate_l = base_length * 0.4;
    slot_w = latch_width + clearance * 2;
    plate_w = slot_w + wall_thickness * 2;
    slot_h = hook_depth + clearance;
    
    // Match resting Z height
    hook_z_rest = base_height/2 - arm_thickness/2 + arm_length * sin(spring_angle) + hook_depth;
    plate_h = hook_z_rest + wall_thickness * 2;
    
    translate([arm_length * cos(spring_angle), 0, 0])
    difference() {
        cuboid([plate_l, plate_w, plate_h], anchor=BOTTOM);
        
        // Hook Chamber (interference clearance match)
        translate([0, 0, hook_z_rest - slot_h])
        cuboid([plate_l + 0.1, slot_w, slot_h], anchor=BOTTOM);
        
        // Chamfer Entry
        translate([-plate_l/2, 0, plate_h])
        rotate([0, entry_angle, 0])
        cuboid([plate_l*1.5, slot_w, plate_h], anchor=BOTTOM);
    }
}
}
