// rubiks_sphere.scad — Parametric Rubik's Sphere Variant
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// A spherical Rubik's puzzle: the outer shell is a sphere divided into
// horizontal bands that can rotate independently. The interior holds
// a core mechanism identical to the cube variant.

include <../../libs/BOSL2/std.scad>

/* [Puzzle Grid] */
// Grid size (controls internal segment count)
N = 3;
// Overall sphere diameter (mm)
size = 57;
// Gap between bands (mm)
clearance = 0.3;

/* [Sphere Geometry] */
// Number of horizontal rotation bands
sphere_band_count = 4;

/* [Band Rotation] */
// Band 1 rotation (degrees): 0, 90, 180, 270
rotate_band_1 = 0;
// Band 2 rotation (degrees): 0, 90, 180, 270
rotate_band_2 = 0;
// Band 3 rotation (degrees): 0, 90, 180, 270
rotate_band_3 = 0;
// Band 4 rotation (degrees): 0, 90, 180, 270
rotate_band_4 = 0;

/* [Visibility] */
show_segments = true;
show_core = true;
show_bands = true;

/* [Render Control] */
// 0=all, 1=segments only, 2=core only, 3=bands only
render_mode = 0;

/* ─── Derived constants ─── */

sphere_r = size / 2;
band_height = size / sphere_band_count;
cut_thickness = clearance * 2;

// Core (same proportions as cube variant)
core_dia = size * 0.28;
axle_dia = size * 0.05;
axle_len = size * 0.48;

$fn = 48;

/* ─── Modules ─── */

// A single horizontal band of the sphere, between z_lo and z_hi.
module sphere_band(z_lo, z_hi, band_idx) {
    // Color bands with cycling hues
    band_colors = [
        [1.0, 1.0, 1.0],   // White
        [0.8, 0.0, 0.0],    // Red
        [0.0, 0.0, 0.8],    // Blue
        [0.0, 0.6, 0.0],    // Green
        [1.0, 0.85, 0.0],   // Yellow
        [1.0, 0.5, 0.0]     // Orange
    ];
    c = band_colors[band_idx % len(band_colors)];

    color(c)
    difference() {
        // Full sphere
        sphere(r=sphere_r);

        // Cut everything below z_lo
        if (z_lo > -sphere_r)
            translate([0, 0, z_lo - sphere_r - 0.01])
                cube([size + 2, size + 2, size], center=true);

        // Cut everything above z_hi
        if (z_hi < sphere_r)
            translate([0, 0, z_hi + sphere_r + 0.01])
                cube([size + 2, size + 2, size], center=true);

        // Inner cavity for core clearance
        sphere(r=core_dia / 2 + clearance);
    }
}

// Thin cut rings that visually separate the bands.
module band_cuts() {
    color([0.12, 0.12, 0.12])
    for (i = [1 : sphere_band_count - 1]) {
        z_cut = -sphere_r + i * band_height;
        translate([0, 0, z_cut])
            cyl(d=size + 1, l=cut_thickness, $fn=64);
    }
}

// Central core mechanism: sphere + 6 axle cylinders.
module core_mechanism() {
    color([0.3, 0.3, 0.3]) {
        sphere(d=core_dia, $fn=32);

        rotate([0, 90, 0])
            cyl(d=axle_dia, l=axle_len, $fn=24);
        rotate([90, 0, 0])
            cyl(d=axle_dia, l=axle_len, $fn=24);
        cyl(d=axle_dia, l=axle_len, $fn=24);
    }
}

// Full spherical Rubik's puzzle.
module rubiks_sphere() {
    // Render band segments
    if (show_segments && (render_mode == 0 || render_mode == 1)) {
        for (i = [0 : sphere_band_count - 1]) {
            z_lo = -sphere_r + i * band_height + (i > 0 ? clearance / 2 : 0);
            z_hi = -sphere_r + (i + 1) * band_height - (i < sphere_band_count - 1 ? clearance / 2 : 0);
            band_angle = (i == 0) ? rotate_band_1
                       : (i == 1) ? rotate_band_2
                       : (i == 2) ? rotate_band_3
                       : rotate_band_4;
            rotate([0, 0, band_angle])
                sphere_band(z_lo, z_hi, i);
        }
    }

    // Render band cut indicators
    if (show_bands && (render_mode == 0 || render_mode == 3)) {
        // Visual cut lines (do not affect geometry — for display only)
        % band_cuts();
    }

    // Render core
    if (show_core && (render_mode == 0 || render_mode == 2)) {
        core_mechanism();
    }
}

/* ─── Top-level render ─── */

rubiks_sphere();
