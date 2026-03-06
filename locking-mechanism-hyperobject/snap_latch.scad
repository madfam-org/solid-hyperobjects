// Parametric Snap-Fit Latch — Cantilever beam with hook
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
latch_width = 15;
hook_depth = 2;
spring_angle = 30;
wall_thickness = 2;
base_length = 40;
clearance = 0.3;
fn = 0;

// Derived
$fn = fn > 0 ? fn : $preview ? 16 : 32;
arm_length = base_length * 0.6;
arm_thickness = wall_thickness * 0.6;
base_height = wall_thickness * 2;

// render_mode: 0 = latch_arm, 1 = striker_plate
render_mode = 0;

if (render_mode == 0) {
    // --- Latch Arm with cantilever and hook ---
    // Base mounting block
    cuboid([base_length * 0.4, latch_width, base_height], anchor=BOTTOM);

    // Cantilever arm — angled upward from base
    translate([base_length * 0.2, 0, base_height])
        rotate([0, -spring_angle, 0])
            cuboid([arm_length, latch_width, arm_thickness], anchor=BOTTOM+LEFT);

    // Hook at tip of cantilever
    hook_x = base_length * 0.2 + arm_length * cos(spring_angle);
    hook_z = base_height + arm_length * sin(spring_angle);
    translate([hook_x, 0, hook_z])
        cuboid([arm_thickness, latch_width, hook_depth + arm_thickness], anchor=TOP+LEFT);

    // Hook lip (catch overhang)
    translate([hook_x - hook_depth, 0, hook_z - hook_depth - arm_thickness])
        cuboid([hook_depth, latch_width, arm_thickness], anchor=BOTTOM+LEFT);
}

if (render_mode == 1) {
    // --- Striker Plate (receiving part) ---
    plate_width = latch_width + clearance * 2 + wall_thickness * 2;
    slot_height = hook_depth + clearance;
    plate_height = base_height + slot_height + wall_thickness;

    translate([0, 0, -base_height * 2])
        difference() {
            cuboid([base_length * 0.5, plate_width, plate_height], anchor=BOTTOM);
            // Slot for hook engagement
            translate([0, 0, plate_height - slot_height])
                cuboid([base_length * 0.3, latch_width + clearance * 2, slot_height + 0.1],
                       anchor=BOTTOM);
        }
}
