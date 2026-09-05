// cubie.scad — Single cubie for individual printing
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// Renders a single corner cubie (position [0,0,N-1]) at the origin.
// Useful for printing individual replacement pieces.
//
// Usage:
//   openscad -o cubie.stl cubie.scad
//   openscad -o cubie_5x5.stl -D "N=5" -D "size=80" cubie.scad

include <../../libs/BOSL2/std.scad>

/* [Puzzle Grid] */
N = is_undef(N) ? 3 : N;
size = is_undef(size) ? 57 : size;
clearance = is_undef(clearance) ? 0.3 : clearance;

/* [Cubie Appearance] */
corner_rounding = is_undef(corner_rounding) ? 1.5 : corner_rounding;
sticker_depth = is_undef(sticker_depth) ? 0.3 : sticker_depth;

/* [Face Colors] */
color_top = is_undef(color_top) ? "#FFFFFF" : color_top;
color_bottom = is_undef(color_bottom) ? "#FFD900" : color_bottom;
color_front = is_undef(color_front) ? "#CC0000" : color_front;
color_back = is_undef(color_back) ? "#FF8000" : color_back;
color_left = is_undef(color_left) ? "#0000CC" : color_left;
color_right = is_undef(color_right) ? "#009900" : color_right;

/* ─── Derived constants ─── */

cubie_size = (size - (N + 1) * clearance) / N;
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

/* ─── Modules ─── */

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

/* ─── Render: single corner cubie with 3 colored faces ─── */

cubie(0, 0, N - 1);
