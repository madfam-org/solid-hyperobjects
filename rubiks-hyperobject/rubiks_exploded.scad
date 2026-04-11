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

/* [Layer Rotation] */
rotate_top = is_undef(rotate_top) ? 0 : rotate_top;
rotate_front = is_undef(rotate_front) ? 0 : rotate_front;
rotate_right = is_undef(rotate_right) ? 0 : rotate_right;
rotate_bottom = is_undef(rotate_bottom) ? 0 : rotate_bottom;
rotate_back = is_undef(rotate_back) ? 0 : rotate_back;
rotate_left = is_undef(rotate_left) ? 0 : rotate_left;

/* [Middle Layer Rotations — X axis, layers 1-7] */
rotate_x_1 = is_undef(rotate_x_1) ? 0 : rotate_x_1;
rotate_x_2 = is_undef(rotate_x_2) ? 0 : rotate_x_2;
rotate_x_3 = is_undef(rotate_x_3) ? 0 : rotate_x_3;
rotate_x_4 = is_undef(rotate_x_4) ? 0 : rotate_x_4;
rotate_x_5 = is_undef(rotate_x_5) ? 0 : rotate_x_5;
rotate_x_6 = is_undef(rotate_x_6) ? 0 : rotate_x_6;
rotate_x_7 = is_undef(rotate_x_7) ? 0 : rotate_x_7;

/* [Middle Layer Rotations — Y axis, layers 1-7] */
rotate_y_1 = is_undef(rotate_y_1) ? 0 : rotate_y_1;
rotate_y_2 = is_undef(rotate_y_2) ? 0 : rotate_y_2;
rotate_y_3 = is_undef(rotate_y_3) ? 0 : rotate_y_3;
rotate_y_4 = is_undef(rotate_y_4) ? 0 : rotate_y_4;
rotate_y_5 = is_undef(rotate_y_5) ? 0 : rotate_y_5;
rotate_y_6 = is_undef(rotate_y_6) ? 0 : rotate_y_6;
rotate_y_7 = is_undef(rotate_y_7) ? 0 : rotate_y_7;

/* [Middle Layer Rotations — Z axis, layers 1-7] */
rotate_z_1 = is_undef(rotate_z_1) ? 0 : rotate_z_1;
rotate_z_2 = is_undef(rotate_z_2) ? 0 : rotate_z_2;
rotate_z_3 = is_undef(rotate_z_3) ? 0 : rotate_z_3;
rotate_z_4 = is_undef(rotate_z_4) ? 0 : rotate_z_4;
rotate_z_5 = is_undef(rotate_z_5) ? 0 : rotate_z_5;
rotate_z_6 = is_undef(rotate_z_6) ? 0 : rotate_z_6;
rotate_z_7 = is_undef(rotate_z_7) ? 0 : rotate_z_7;

/* [Face Colors] */
color_top = is_undef(color_top) ? "#FFFFFF" : color_top;
color_bottom = is_undef(color_bottom) ? "#FFD900" : color_bottom;
color_front = is_undef(color_front) ? "#CC0000" : color_front;
color_back = is_undef(color_back) ? "#FF8000" : color_back;
color_left = is_undef(color_left) ? "#0000CC" : color_left;
color_right = is_undef(color_right) ? "#009900" : color_right;

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
    color_top,      // 0: Top
    color_bottom,   // 1: Bottom
    color_front,    // 2: Front
    color_back,     // 3: Back
    color_left,     // 4: Left
    color_right     // 5: Right
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

                    // Layer rotation lookup arrays (indices 0..8, supporting up to 9x9)
                    z_rotations = [rotate_bottom, rotate_z_1, rotate_z_2, rotate_z_3, rotate_z_4, rotate_z_5, rotate_z_6, rotate_z_7, rotate_top];
                    y_rotations = [-rotate_front, rotate_y_1, rotate_y_2, rotate_y_3, rotate_y_4, rotate_y_5, rotate_y_6, rotate_y_7, rotate_back];
                    x_rotations = [-rotate_left, rotate_x_1, rotate_x_2, rotate_x_3, rotate_x_4, rotate_x_5, rotate_x_6, rotate_x_7, rotate_right];

                    rot_z = (gz < len(z_rotations)) ? z_rotations[gz] : 0;
                    rot_y = (gy < len(y_rotations)) ? y_rotations[gy] : 0;
                    rot_x = (gx < len(x_rotations)) ? x_rotations[gx] : 0;

                    translate([base_x + ex, base_y + ey, base_z + ez])
                        rotate([rot_x, rot_y, rot_z])
                            cubie(gx, gy, gz);
                }
}

if (show_core && (render_mode == 0 || render_mode == 2)) {
    core_mechanism();
}
