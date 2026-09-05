// mechanism.scad — Standalone functional mechanism view
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// Renders the internal mechanism: core with screw posts and spring cavities,
// plus one representative of each cubie type (center, edge, corner) in an
// exploded layout for print verification.
//
// Usage:
//   openscad -o mechanism.stl mechanism.scad
//   openscad -o mechanism.stl -D "render_mode=1" mechanism.scad   # core only
//   openscad -o mechanism.stl -D "render_mode=2" mechanism.scad   # center cubie
//   openscad -o mechanism.stl -D "render_mode=3" mechanism.scad   # edge cubie
//   openscad -o mechanism.stl -D "render_mode=4" mechanism.scad   # corner cubie

include <BOSL2/std.scad>

/* [Puzzle Grid] */
N = is_undef(N) ? 3 : N;
size = is_undef(size) ? 57 : size;
clearance = is_undef(clearance) ? 0.3 : clearance;

/* [Cubie Appearance] */
corner_rounding = is_undef(corner_rounding) ? 1.5 : corner_rounding;
sticker_depth = is_undef(sticker_depth) ? 0.3 : sticker_depth;
sticker_style = is_undef(sticker_style) ? "color" : sticker_style;

/* [Mechanism Parameters] */
spring_dia = is_undef(spring_dia) ? 5 : spring_dia;
spring_length = is_undef(spring_length) ? 8 : spring_length;
screw_dia = is_undef(screw_dia) ? 3 : screw_dia;
mechanism_clearance = is_undef(mechanism_clearance) ? 0.2 : mechanism_clearance;

/* [Render Control] */
// 0=all exploded, 1=core only, 2=center cubie, 3=edge cubie, 4=corner cubie
render_mode = is_undef(render_mode) ? 0 : render_mode;

/* [CDG Insert System] */
show_sockets = is_undef(show_sockets) ? false : show_sockets;
insert_pocket_depth = is_undef(insert_pocket_depth) ? 1.5 : insert_pocket_depth;
insert_pin_dia = is_undef(insert_pin_dia) ? 1.0 : insert_pin_dia;
insert_pin_height = is_undef(insert_pin_height) ? 1.0 : insert_pin_height;

/* [Face Colors] */
color_top = is_undef(color_top) ? "#FFFFFF" : color_top;
color_bottom = is_undef(color_bottom) ? "#FFD900" : color_bottom;
color_front = is_undef(color_front) ? "#CC0000" : color_front;
color_back = is_undef(color_back) ? "#FF8000" : color_back;
color_left = is_undef(color_left) ? "#0000CC" : color_left;
color_right = is_undef(color_right) ? "#009900" : color_right;

// Include the main cube as a library.
//
// `include` inlines rubiks_cube.scad into THIS file's scope, and OpenSCAD resolves a
// variable to its LAST assignment in the resulting text — so every setting this view
// makes BEFORE the include is silently overwritten by rubiks_cube.scad's own
// `x = is_undef(x) ? default : x` line (OpenSCAD prints one "was assigned ... but was
// overwritten" warning per variable). That is why the mechanism view's own settings
// now come AFTER the include, where they win. The one that mattered most was
// `is_library`: overwritten back to 0, rubiks_cube.scad's own top-level `if
// (is_library == 0)` block ran as well, so every mechanism render also contained the
// entire cube — 9 stray sticker plates in mechanism_edge, and the whole 26-cubie grid
// in the other parts.
//
// Parameters the platform passes with -D are unaffected: a command-line -D wins over
// every in-file assignment, so presets still drive N, size, mechanism_detail and the
// rest.
include <rubiks_cube.scad>

/* ---- Mechanism-view settings — MUST come after the include (see note above) ---- */

// Suppress rubiks_cube.scad's own top-level render; this file draws the pieces.
is_library = 1;

// Visibility — all on for mechanism view
show_cubies = true;
show_core = true;

// No notation letters in the mechanism view
show_notation = false;

// Layer rotations — all zero (irrelevant for mechanism view)
rotate_top = 0; rotate_front = 0; rotate_right = 0;
rotate_bottom = 0; rotate_back = 0; rotate_left = 0;
rotate_x_1 = 0; rotate_x_2 = 0; rotate_x_3 = 0; rotate_x_4 = 0;
rotate_x_5 = 0; rotate_x_6 = 0; rotate_x_7 = 0;
rotate_y_1 = 0; rotate_y_2 = 0; rotate_y_3 = 0; rotate_y_4 = 0;
rotate_y_5 = 0; rotate_y_6 = 0; rotate_y_7 = 0;
rotate_z_1 = 0; rotate_z_2 = 0; rotate_z_3 = 0; rotate_z_4 = 0;
rotate_z_5 = 0; rotate_z_6 = 0; rotate_z_7 = 0;
explode_factor = 0;

/* ---- Derived layout spacing ---- */
spacing = cubie_size * 2.0;  // gap between exploded pieces

/* ---- Render ---- */

// Core mechanism (always functional)
if (render_mode == 0 || render_mode == 1) {
    core_functional();
}

// Center cubie — top-face center (grid position: middle X, middle Y, top Z)
if (render_mode == 0 || render_mode == 2) {
    _cx = (N >= 3) ? 1 : 0;
    _cy = (N >= 3) ? 1 : 0;
    _cz = N - 1;
    translate(render_mode == 0 ? [0, 0, spacing] : [0, 0, 0])
        cubie(_cx, _cy, _cz);
}

// Edge cubie — top-front edge (grid position: middle X, front Y, top Z)
if (render_mode == 0 || render_mode == 3) {
    _ex = (N >= 3) ? 1 : 0;
    _ey = 0;
    _ez = N - 1;
    translate(render_mode == 0 ? [spacing, 0, spacing * 0.5] : [0, 0, 0])
        cubie(_ex, _ey, _ez);
}

// Corner cubie — top-front-right corner (grid position: right X, front Y, top Z)
if (render_mode == 0 || render_mode == 4) {
    _ox = N - 1;
    _oy = 0;
    _oz = N - 1;
    translate(render_mode == 0 ? [-spacing, 0, spacing * 0.5] : [0, 0, 0])
        cubie(_ox, _oy, _oz);
}
