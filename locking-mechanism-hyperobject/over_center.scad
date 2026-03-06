// Parametric Over-Center Linkage Lock
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
lever_length = 30;
over_center_offset = 2;
wall_thickness = 2;
latch_width = 15;
base_length = 40;
clearance = 0.3;
fn = 0;

// Derived
$fn = fn > 0 ? fn : $preview ? 16 : 32;
pivot_r = wall_thickness;
link_thickness = wall_thickness * 0.8;
base_height = wall_thickness * 2;
pivot_height = base_height + lever_length * 0.3;

// render_mode: 0 = lever_assembly, 1 = hook_catch
render_mode = 0;

if (render_mode == 0) {
    // --- Base plate with pivot post ---
    cuboid([base_length, latch_width, base_height], anchor=BOTTOM);

    // Pivot post (rear)
    translate([-base_length * 0.3, 0, base_height])
        cyl(r=pivot_r, h=latch_width + wall_thickness, orient=RIGHT, anchor=CENTER);

    // Lever arm from pivot
    translate([-base_length * 0.3, 0, base_height]) {
        // Main lever
        cuboid([link_thickness, latch_width * 0.8, lever_length], anchor=BOTTOM);

        // Link arm — connects lever to hook, offset past center
        translate([over_center_offset, 0, lever_length])
            cuboid([lever_length * 0.5, latch_width * 0.6, link_thickness], anchor=BOTTOM+LEFT);
    }

    // Handle grip at top of lever
    translate([-base_length * 0.3, 0, base_height + lever_length])
        cuboid([wall_thickness * 3, latch_width, wall_thickness], anchor=BOTTOM);
}

if (render_mode == 1) {
    // --- Hook catch (mating part) ---
    catch_height = pivot_height + wall_thickness;

    translate([base_length * 0.6, 0, 0]) {
        // Catch base
        cuboid([base_length * 0.3, latch_width, base_height], anchor=BOTTOM);

        // Hook post
        translate([0, 0, base_height])
            cuboid([wall_thickness, latch_width * 0.6, catch_height - base_height],
                   anchor=BOTTOM);

        // Hook lip
        translate([-wall_thickness, 0, catch_height - wall_thickness])
            cuboid([wall_thickness * 2, latch_width * 0.6, wall_thickness], anchor=BOTTOM);
    }
}
