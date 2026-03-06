// Parametric Compliant Bistable Locking Mechanism
// Yantra4D — Locking Mechanism Hyperobject
include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
latch_width = 15;
wall_thickness = 2;
base_length = 40;
hook_depth = 2;
clearance = 0.3;
fn = 0;

// Derived
$fn = fn > 0 ? fn : $preview ? 16 : 32;
beam_thickness = wall_thickness * 0.5;
base_height = wall_thickness * 2;
beam_length = base_length * 0.7;
arch_height = base_length * 0.2;

// render_mode: 0 = compliant_body
render_mode = 0;

if (render_mode == 0) {
    // --- Base plate ---
    cuboid([base_length, latch_width, base_height], anchor=BOTTOM);

    // --- Left anchor pillar ---
    translate([-base_length * 0.35, 0, base_height])
        cuboid([wall_thickness, latch_width, arch_height * 0.5], anchor=BOTTOM);

    // --- Right anchor pillar ---
    translate([base_length * 0.35, 0, base_height])
        cuboid([wall_thickness, latch_width, arch_height * 0.5], anchor=BOTTOM);

    // --- Compliant curved beam (bistable arch) ---
    // Approximated as a series of segments forming a cosine arch
    beam_steps = 20;
    beam_start_x = -beam_length / 2;
    pillar_top = base_height + arch_height * 0.5;

    translate([0, 0, pillar_top])
        for (i = [0 : beam_steps - 1]) {
            x0 = beam_start_x + i * (beam_length / beam_steps);
            x1 = beam_start_x + (i + 1) * (beam_length / beam_steps);
            t0 = i / beam_steps;
            t1 = (i + 1) / beam_steps;
            z0 = arch_height * sin(t0 * 180);
            z1 = arch_height * sin(t1 * 180);
            hull() {
                translate([x0, 0, z0])
                    cuboid([beam_length / beam_steps * 0.3, latch_width, beam_thickness],
                           anchor=CENTER);
                translate([x1, 0, z1])
                    cuboid([beam_length / beam_steps * 0.3, latch_width, beam_thickness],
                           anchor=CENTER);
            }
        }

    // --- Hook catch at beam apex ---
    translate([0, 0, pillar_top + arch_height])
        cuboid([wall_thickness, latch_width * 0.6, hook_depth + beam_thickness],
               anchor=BOTTOM);

    // Hook lip
    translate([hook_depth / 2, 0, pillar_top + arch_height])
        cuboid([hook_depth, latch_width * 0.6, beam_thickness], anchor=BOTTOM);
}
