// rubiks_exploded.scad — Exploded view of the Rubik's Cube
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// Standalone file that renders an exploded view of the cube.
// The explode_factor defaults to 100 when called without -D overrides.
//
// Usage:
//   openscad -o exploded.stl rubiks_exploded.scad
//   openscad -o exploded.stl -D "explode_factor=150" rubiks_exploded.scad

include <../../libs/BOSL2/std.scad>

/* [Puzzle Grid] */
N = is_undef(N) ? 3 : N;
size = is_undef(size) ? 57 : size;
clearance = is_undef(clearance) ? 0.3 : clearance;

/* [Cubie Appearance] */
corner_rounding = is_undef(corner_rounding) ? 1.5 : corner_rounding;
sticker_depth = is_undef(sticker_depth) ? 0.3 : sticker_depth;

/* [Exploded View] */
explode_factor = is_undef(explode_factor) ? 100 : explode_factor;

/* [Visibility] */
show_cubies = is_undef(show_cubies) ? true : show_cubies;
show_core = is_undef(show_core) ? true : show_core;

/* [Render Control] */
render_mode = is_undef(render_mode) ? 0 : render_mode;

/* ─── Derived constants (duplicated for standalone operation) ─── */

cubie_size = (size - (N + 1) * clearance) / N;
pitch = cubie_size + clearance;
grid_offset = -(N - 1) / 2 * pitch;
core_dia = size * 0.28;
axle_dia = cubie_size * 0.18;
axle_len = size * 0.48;
safe_rounding = min(corner_rounding, cubie_size / 2 - 0.01);

face_colors = [
    [1.0, 1.0, 1.0],
    [1.0, 0.85, 0.0],
    [0.8, 0.0, 0.0],
    [1.0, 0.5, 0.0],
    [0.0, 0.0, 0.8],
    [0.0, 0.6, 0.0]
];

body_color = [0.12, 0.12, 0.12];

/* ─── Modules (reused from rubiks_cube) ─── */

module face_sticker(axis, sign, fc) {
    sticker_size = cubie_size * 0.82;
    sticker_thick = sticker_depth;
    sticker_rounding = min(safe_rounding * 0.6, sticker_size / 2 - 0.01);
    offset_dist = cubie_size / 2 + sticker_thick / 2 - 0.01;

    color(fc)
    if (axis == 0) {
        translate([sign * offset_dist, 0, 0])
            rotate([0, 90, 0])
                cuboid([sticker_size, sticker_size, sticker_thick],
                       rounding=sticker_rounding, edges="Z");
    } else if (axis == 1) {
        translate([0, sign * offset_dist, 0])
            rotate([90, 0, 0])
                cuboid([sticker_size, sticker_size, sticker_thick],
                       rounding=sticker_rounding, edges="Z");
    } else {
        translate([0, 0, sign * offset_dist])
            cuboid([sticker_size, sticker_size, sticker_thick],
                   rounding=sticker_rounding, edges="Z");
    }
}

module cubie(gx, gy, gz) {
    color(body_color)
        cuboid([cubie_size, cubie_size, cubie_size],
               rounding=safe_rounding);

    if (gz == N - 1) face_sticker(2, 1, face_colors[0]);
    if (gz == 0)     face_sticker(2, -1, face_colors[1]);
    if (gy == 0)     face_sticker(1, -1, face_colors[2]);
    if (gy == N - 1) face_sticker(1, 1, face_colors[3]);
    if (gx == 0)     face_sticker(0, -1, face_colors[4]);
    if (gx == N - 1) face_sticker(0, 1, face_colors[5]);
}

module core_mechanism() {
    color([0.3, 0.3, 0.3]) {
        sphere(d=core_dia, $fn=32);
        rotate([0, 90, 0]) cyl(d=axle_dia, l=axle_len, $fn=24);
        rotate([90, 0, 0]) cyl(d=axle_dia, l=axle_len, $fn=24);
        cyl(d=axle_dia, l=axle_len, $fn=24);
    }
}

/* ─── Render ─── */

if (show_cubies && (render_mode == 0 || render_mode == 1)) {
    for (gx = [0 : N-1])
        for (gy = [0 : N-1])
            for (gz = [0 : N-1])
                if (gx == 0 || gx == N-1 ||
                    gy == 0 || gy == N-1 ||
                    gz == 0 || gz == N-1) {
                    base_x = grid_offset + gx * pitch;
                    base_y = grid_offset + gy * pitch;
                    base_z = grid_offset + gz * pitch;
                    ex = (explode_factor / 100) * base_x * 0.6;
                    ey = (explode_factor / 100) * base_y * 0.6;
                    ez = (explode_factor / 100) * base_z * 0.6;
                    translate([base_x + ex, base_y + ey, base_z + ez])
                        cubie(gx, gy, gz);
                }
}

if (show_core && (render_mode == 0 || render_mode == 2)) {
    core_mechanism();
}
