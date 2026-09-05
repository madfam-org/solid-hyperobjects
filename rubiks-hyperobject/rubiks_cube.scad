// rubiks_cube.scad — Parametric NxNxN Rubik's Cube
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// A fully parametric Rubik's puzzle cube using BOSL2 for rounding
// and primitive geometry. Supports 2x2 through 9x9, layer rotations
// (including middle layers), exploded views, and separate core/cubie rendering.

include <../../libs/BOSL2/std.scad>

/* [Puzzle Grid] */
// Grid size: 2=Pocket, 3=Standard, 4=Revenge, 5=Professor ... 9x9
N = is_undef(N) ? 3 : N; // [2:1:9]
// Overall cube dimension (mm)
size = is_undef(size) ? 57 : size;
// Gap between cubies (mm)
clearance = is_undef(clearance) ? 0.3 : clearance;

/* [Cubie Appearance] */
// Edge rounding on cubies (mm)
corner_rounding = is_undef(corner_rounding) ? 1.5 : corner_rounding;
// Face color inset depth (mm)
sticker_depth = is_undef(sticker_depth) ? 0.3 : sticker_depth;
// Sticker style: "color" or "tactile"
sticker_style = is_undef(sticker_style) ? "color" : sticker_style;

/* [Layer Rotation] */
// Top layer rotation (degrees): 0, 90, 180, 270
rotate_top = is_undef(rotate_top) ? 0 : rotate_top;
// Front layer rotation (degrees): 0, 90, 180, 270
rotate_front = is_undef(rotate_front) ? 0 : rotate_front;
// Right layer rotation (degrees): 0, 90, 180, 270
rotate_right = is_undef(rotate_right) ? 0 : rotate_right;
// Bottom layer rotation (degrees): 0, 90, 180, 270
rotate_bottom = is_undef(rotate_bottom) ? 0 : rotate_bottom;
// Back layer rotation (degrees): 0, 90, 180, 270
rotate_back = is_undef(rotate_back) ? 0 : rotate_back;
// Left layer rotation (degrees): 0, 90, 180, 270
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

/* [CDG Insert System] */
// Show insert pockets on cubie faces
show_sockets = is_undef(show_sockets) ? false : show_sockets;
// Depth of insert pocket (mm)
insert_pocket_depth = is_undef(insert_pocket_depth) ? 1.5 : insert_pocket_depth;
// Alignment pin diameter (mm)
insert_pin_dia = is_undef(insert_pin_dia) ? 1.0 : insert_pin_dia;
// Alignment pin protrusion (mm)
insert_pin_height = is_undef(insert_pin_height) ? 1.0 : insert_pin_height;

/* [Notation Overlay] */
// Show U/D/F/B/L/R on center cubies
show_notation = is_undef(show_notation) ? false : show_notation;

/* [Mechanism Detail] */
// "decorative" = simple sphere + axles, "functional" = printable mechanism
mechanism_detail = is_undef(mechanism_detail) ? "decorative" : mechanism_detail;
// Compression spring diameter (mm)
spring_dia = is_undef(spring_dia) ? 5 : spring_dia;
// Spring cavity length (mm)
spring_length = is_undef(spring_length) ? 8 : spring_length;
// Axle screw diameter (mm, M3 default)
screw_dia = is_undef(screw_dia) ? 3 : screw_dia;
// Internal clearance for moving parts (mm)
mechanism_clearance = is_undef(mechanism_clearance) ? 0.2 : mechanism_clearance;

/* [Anti-Pop Torpedoes (DaYan 2011)] */
torpedo_length = is_undef(torpedo_length) ? 3 : torpedo_length;
torpedo_thickness = is_undef(torpedo_thickness) ? 0.8 : torpedo_thickness;
enable_torpedoes = is_undef(enable_torpedoes) ? false : enable_torpedoes;

/* [Corner Cutting (DaYan 2010)] */
corner_cut_angle = is_undef(corner_cut_angle) ? 35 : corner_cut_angle;
track_bevel = is_undef(track_bevel) ? 1 : track_bevel;
enable_corner_cutting = is_undef(enable_corner_cutting) ? false : enable_corner_cutting;

/* [Magnets (2016+)] */
magnet_dia = is_undef(magnet_dia) ? 3 : magnet_dia;
magnet_depth = is_undef(magnet_depth) ? 1.5 : magnet_depth;
enable_magnets = is_undef(enable_magnets) ? false : enable_magnets;
// Corner-core magnets (Gan 2018)
core_magnet_dia = is_undef(core_magnet_dia) ? 4 : core_magnet_dia;
core_magnet_depth = is_undef(core_magnet_depth) ? 2 : core_magnet_depth;
enable_core_magnets = is_undef(enable_core_magnets) ? false : enable_core_magnets;

/* [Maglev Tensioning (2020s)] */
enable_maglev = is_undef(enable_maglev) ? false : enable_maglev;
maglev_ring_dia = is_undef(maglev_ring_dia) ? 6 : maglev_ring_dia;
maglev_ring_height = is_undef(maglev_ring_height) ? 2 : maglev_ring_height;
maglev_gap = is_undef(maglev_gap) ? 1.5 : maglev_gap;

/* [Exploded View] */
// Explosion percentage: 0=assembled, 100=fully exploded, 200=max
explode_factor = is_undef(explode_factor) ? 0 : explode_factor;

/* [Visibility] */
show_cubies = is_undef(show_cubies) ? true : show_cubies;
show_core = is_undef(show_core) ? true : show_core;

/* [Render Control] */
// 0=all, 1=cubies only, 2=core only
render_mode = is_undef(render_mode) ? 0 : render_mode;

// Guard for library includes
is_library = is_undef(is_library) ? 0 : is_library;

/* ─── Derived constants ─── */

// Size of each individual cubie
cubie_size = (size - (N + 1) * clearance) / N;

// Half the grid extent for centering
half_extent = size / 2;

// Core sphere radius (used by maglev, core magnets)
core_radius = cubie_size * 0.45;

// Pitch: center-to-center distance between adjacent cubies
pitch = cubie_size + clearance;

// Offset to center the grid at origin: position of cubie [0,0,0] center
grid_offset = -(N - 1) / 2 * pitch;

// Core sphere diameter (fraction of total size)
core_dia = size * 0.28;

// Axle cylinder parameters
axle_dia = cubie_size * 0.18;
axle_len = size * 0.48;

// Safe rounding: cannot exceed half cubie size
safe_rounding = min(corner_rounding, cubie_size / 2 - 0.01);

/* [Face Colors] */
// Top face color (hex string)
color_top = is_undef(color_top) ? "#FFFFFF" : color_top;
// Bottom face color (hex string)
color_bottom = is_undef(color_bottom) ? "#FFD900" : color_bottom;
// Front face color (hex string)
color_front = is_undef(color_front) ? "#CC0000" : color_front;
// Back face color (hex string)
color_back = is_undef(color_back) ? "#FF8000" : color_back;
// Left face color (hex string)
color_left = is_undef(color_left) ? "#0000CC" : color_left;
// Right face color (hex string)
color_right = is_undef(color_right) ? "#009900" : color_right;

/* ─── Face color array (derived from parameters) ─── */

// Face colors indexed by face ID:
// 0=Top, 1=Bottom, 2=Front, 3=Back, 4=Left, 5=Right
face_colors = [
    color_top,      // 0: Top
    color_bottom,   // 1: Bottom
    color_front,    // 2: Front
    color_back,     // 3: Back
    color_left,     // 4: Left
    color_right     // 5: Right
];

// Body color (black plastic)
body_color = [0.12, 0.12, 0.12];

/* ─── Modules ─── */

// Render raised tactile dots on one face of a cubie.
// face_index: 0=Top(1 dot), 1=Bottom(2 dots), 2=Front(3 dots),
//             3=Back(4 dots), 4=Left(5 dots), 5=Right(6 dots)
module tactile_dots(face_index) {
    dot_r = cubie_size * 0.06;
    dot_h = sticker_depth * 2;
    spread = cubie_size * 0.2;  // dot spacing from center

    color([0.85, 0.85, 0.85])
    if (face_index == 0) {
        // Top: 1 dot center
        sphere(r=dot_r, $fn=16);
    } else if (face_index == 1) {
        // Bottom: 2 dots vertical
        for (dy = [-1, 1])
            translate([0, dy * spread, 0])
                sphere(r=dot_r, $fn=16);
    } else if (face_index == 2) {
        // Front: 3 dots diagonal
        for (k = [-1, 0, 1])
            translate([k * spread, k * spread, 0])
                sphere(r=dot_r, $fn=16);
    } else if (face_index == 3) {
        // Back: 4 dots square
        for (dx = [-1, 1])
            for (dy = [-1, 1])
                translate([dx * spread * 0.7, dy * spread * 0.7, 0])
                    sphere(r=dot_r, $fn=16);
    } else if (face_index == 4) {
        // Left: 5 dots X pattern
        sphere(r=dot_r, $fn=16);
        for (dx = [-1, 1])
            for (dy = [-1, 1])
                translate([dx * spread, dy * spread, 0])
                    sphere(r=dot_r, $fn=16);
    } else {
        // Right: 6 dots 2x3 grid
        for (dx = [-1, 1])
            for (dy = [-1, 0, 1])
                translate([dx * spread * 0.7, dy * spread, 0])
                    sphere(r=dot_r, $fn=16);
    }
}

// Render raised stripe pattern on one face.
// face_index determines stripe count: 1-6 stripes per face.
module stripe_pattern(face_index) {
    sticker_s = cubie_size * 0.78;
    stripe_count = face_index + 1;
    stripe_h = sticker_depth * 1.5;
    stripe_w = sticker_s / (stripe_count * 2 + 1);
    for (i = [0 : stripe_count - 1]) {
        y_pos = -sticker_s/2 + stripe_w + i * (sticker_s / stripe_count);
        translate([0, y_pos, 0])
            cube([sticker_s * 0.8, stripe_w * 0.7, stripe_h], center=true);
    }
}

// Render raised checkerboard pattern on one face.
// face_index determines grid density: 2x2 to 4x4.
module checker_pattern(face_index) {
    sticker_s = cubie_size * 0.78;
    grid_n = (face_index < 2) ? 2 : (face_index < 4) ? 3 : 4;
    cell = sticker_s / grid_n;
    checker_h = sticker_depth * 1.5;
    for (gx = [0 : grid_n - 1])
        for (gy = [0 : grid_n - 1])
            if ((gx + gy) % 2 == 0)
                translate([
                    -sticker_s/2 + cell/2 + gx * cell,
                    -sticker_s/2 + cell/2 + gy * cell,
                    0
                ])
                    cube([cell * 0.85, cell * 0.85, checker_h], center=true);
}

// Render concentric square pattern on one face.
// face_index determines ring count: 1-3 rings.
module concentric_pattern(face_index) {
    sticker_s = cubie_size * 0.78;
    ring_count = min(face_index + 1, 3);
    ring_h = sticker_depth * 1.5;
    ring_w = sticker_depth * 0.8;
    for (i = [0 : ring_count - 1]) {
        ring_size = sticker_s * (1 - i * 0.3);
        difference() {
            cube([ring_size, ring_size, ring_h], center=true);
            cube([ring_size - ring_w * 2, ring_size - ring_w * 2, ring_h + 1], center=true);
        }
    }
}

// Render a single face sticker on one side of a cubie.
// axis: 0=X, 1=Y, 2=Z
// sign: +1 or -1 (which face along that axis)
// fc: color as [r,g,b]
// face_index: 0-5 face identifier (used for tactile dot pattern)
module face_sticker(axis, sign, fc, face_index=0) {
    sticker_size = cubie_size * 0.82;
    sticker_thick = sticker_depth;
    sticker_rounding = min(safe_rounding * 0.6, sticker_size / 2 - 0.01);

    // Position: offset from cubie center to just outside the face
    offset_dist = cubie_size / 2 + sticker_thick / 2 - 0.01;

    if (sticker_style == "tactile") {
        // Tactile mode: raised dot patterns instead of colored stickers
        // Still render a dark base sticker for contrast
        color(body_color)
        if (axis == 0) {
            translate([sign * offset_dist, 0, 0])
                rotate([0, 90, 0])
                    cuboid([sticker_size, sticker_size, sticker_thick],
                           rounding=sticker_rounding,
                           edges="Z");
        } else if (axis == 1) {
            translate([0, sign * offset_dist, 0])
                rotate([90, 0, 0])
                    cuboid([sticker_size, sticker_size, sticker_thick],
                           rounding=sticker_rounding,
                           edges="Z");
        } else {
            translate([0, 0, sign * offset_dist])
                cuboid([sticker_size, sticker_size, sticker_thick],
                       rounding=sticker_rounding,
                       edges="Z");
        }

        // Render raised dots on top of the sticker
        dot_offset = cubie_size / 2 + sticker_thick;
        if (axis == 0) {
            translate([sign * dot_offset, 0, 0])
                rotate([0, sign * 90, 0])
                    tactile_dots(face_index);
        } else if (axis == 1) {
            translate([0, sign * dot_offset, 0])
                rotate([sign * -90, 0, 0])
                    tactile_dots(face_index);
        } else {
            translate([0, 0, sign * dot_offset])
                rotate([sign > 0 ? 0 : 180, 0, 0])
                    tactile_dots(face_index);
        }
    } else if (sticker_style == "stripes" || sticker_style == "checkers" || sticker_style == "concentric") {
        // Pattern modes: colored base sticker + raised pattern overlay
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
        // Raised pattern on top
        dot_offset = cubie_size / 2 + sticker_thick;
        pattern_module = sticker_style;
        color(body_color)
        if (axis == 0) {
            translate([sign * dot_offset, 0, 0])
                rotate([0, sign * 90, 0]) {
                    if (pattern_module == "stripes") stripe_pattern(face_index);
                    else if (pattern_module == "checkers") checker_pattern(face_index);
                    else concentric_pattern(face_index);
                }
        } else if (axis == 1) {
            translate([0, sign * dot_offset, 0])
                rotate([sign * -90, 0, 0]) {
                    if (pattern_module == "stripes") stripe_pattern(face_index);
                    else if (pattern_module == "checkers") checker_pattern(face_index);
                    else concentric_pattern(face_index);
                }
        } else {
            translate([0, 0, sign * dot_offset])
                rotate([sign > 0 ? 0 : 180, 0, 0]) {
                    if (pattern_module == "stripes") stripe_pattern(face_index);
                    else if (pattern_module == "checkers") checker_pattern(face_index);
                    else concentric_pattern(face_index);
                }
        }
    } else {
        // Color mode (default): original colored sticker
        color(fc)
        if (axis == 0) {
            translate([sign * offset_dist, 0, 0])
                rotate([0, 90, 0])
                    cuboid([sticker_size, sticker_size, sticker_thick],
                           rounding=sticker_rounding,
                           edges="Z");
        } else if (axis == 1) {
            translate([0, sign * offset_dist, 0])
                rotate([90, 0, 0])
                    cuboid([sticker_size, sticker_size, sticker_thick],
                           rounding=sticker_rounding,
                           edges="Z");
        } else {
            translate([0, 0, sign * offset_dist])
                cuboid([sticker_size, sticker_size, sticker_thick],
                       rounding=sticker_rounding,
                       edges="Z");
        }
    }
}

// Render a CDG socket pocket (negative shape) for one cubie face.
// cubie_s: the cubie edge length
module cubie_socket(cubie_s) {
    pocket_size = cubie_s * 0.78;
    // Rectangular pocket
    cube([pocket_size, pocket_size, insert_pocket_depth * 2], center=true);
    // Two alignment pin holes (diagonal corners)
    pin_offset = pocket_size * 0.35;
    for (pos = [[-pin_offset, -pin_offset], [pin_offset, pin_offset]]) {
        translate([pos[0], pos[1], 0])
            cylinder(r=insert_pin_dia/2 + 0.1, h=insert_pocket_depth * 3, center=true, $fn=16);
    }
}

// Render an embossed notation letter on a face.
// letter: single character string (U/D/F/B/L/R)
module notation_letter(letter) {
    notation_depth = 0.3;
    notation_size = cubie_size * 0.4;
    linear_extrude(notation_depth)
        text(letter, size=notation_size, halign="center", valign="center",
             font="Liberation Sans:style=Bold");
}

// Render a single cubie at grid position (gx, gy, gz).
// Grid indices run from 0 to N-1.
module cubie(gx, gy, gz) {
    // Determine center cubie status (exactly one axis at extremity, others in middle)
    is_center_z = (gz == 0 || gz == N-1) && (gx > 0 && gx < N-1) && (gy > 0 && gy < N-1);
    is_center_y = (gy == 0 || gy == N-1) && (gx > 0 && gx < N-1) && (gz > 0 && gz < N-1);
    is_center_x = (gx == 0 || gx == N-1) && (gy > 0 && gy < N-1) && (gz > 0 && gz < N-1);

    // Count exposed faces to classify cubie type (center=1, edge=2, corner=3)
    exposed_count = (gx == 0 || gx == N-1 ? 1 : 0)
                  + (gy == 0 || gy == N-1 ? 1 : 0)
                  + (gz == 0 || gz == N-1 ? 1 : 0);

    // Determine the primary face axis/sign for center cubies
    // (used by center_cubie_internal to orient track and spring cavity)
    _center_axis = (gx == 0 || gx == N-1) ? 0 : ((gy == 0 || gy == N-1) ? 1 : 2);
    _center_sign = (_center_axis == 0) ? (gx == N-1 ? 1 : -1)
                 : (_center_axis == 1) ? (gy == N-1 ? 1 : -1)
                 : (gz == N-1 ? 1 : -1);

    // Body — difference() subtracts sockets and/or functional mechanism internals
    _need_diff = show_sockets || mechanism_detail == "functional";

    if (_need_diff) {
        difference() {
            color(body_color)
                cuboid([cubie_size, cubie_size, cubie_size],
                       rounding=safe_rounding);

            // Socket pockets (when enabled)
            if (show_sockets) {
                // Top face: gz == N-1
                if (gz == N - 1)
                    translate([0, 0, cubie_size/2])
                        cubie_socket(cubie_size);
                // Bottom face: gz == 0
                if (gz == 0)
                    translate([0, 0, -cubie_size/2])
                        cubie_socket(cubie_size);
                // Front face: gy == 0
                if (gy == 0)
                    translate([0, -cubie_size/2, 0])
                        rotate([90, 0, 0])
                            cubie_socket(cubie_size);
                // Back face: gy == N-1
                if (gy == N - 1)
                    translate([0, cubie_size/2, 0])
                        rotate([90, 0, 0])
                            cubie_socket(cubie_size);
                // Left face: gx == 0
                if (gx == 0)
                    translate([-cubie_size/2, 0, 0])
                        rotate([0, 90, 0])
                            cubie_socket(cubie_size);
                // Right face: gx == N-1
                if (gx == N - 1)
                    translate([cubie_size/2, 0, 0])
                        rotate([0, 90, 0])
                            cubie_socket(cubie_size);
            }

            // Functional mechanism internal geometry (when enabled)
            if (mechanism_detail == "functional") {
                if (exposed_count == 1) {
                    // Center cubie — T-track, spring cavity, screw hole
                    center_cubie_internal(_center_axis, _center_sign);
                } else if (exposed_count == 2) {
                    // Edge cubie — spherical pocket + sliding feet
                    edge_cubie_internal();
                } else if (exposed_count == 3) {
                    // Corner cubie — larger spherical pocket + retention feet
                    corner_cubie_internal();
                }
            }
        }
    } else {
        // No sockets, no functional mechanism — render body normally
        color(body_color)
            cuboid([cubie_size, cubie_size, cubie_size],
                   rounding=safe_rounding);
    }

    // Stickers on exposed faces only
    // Top face: gz == N-1
    if (gz == N - 1)
        face_sticker(2, 1, face_colors[0], face_index=0);
    // Bottom face: gz == 0
    if (gz == 0)
        face_sticker(2, -1, face_colors[1], face_index=1);
    // Front face: gy == 0
    if (gy == 0)
        face_sticker(1, -1, face_colors[2], face_index=2);
    // Back face: gy == N-1
    if (gy == N - 1)
        face_sticker(1, 1, face_colors[3], face_index=3);
    // Left face: gx == 0
    if (gx == 0)
        face_sticker(0, -1, face_colors[4], face_index=4);
    // Right face: gx == N-1
    if (gx == N - 1)
        face_sticker(0, 1, face_colors[5], face_index=5);

    // Notation overlay on center cubies (requires N >= 3)
    if (show_notation && N >= 3) {
        notation_offset = cubie_size / 2 + 0.01;

        // Top center → "U"
        if (is_center_z && gz == N - 1)
            translate([0, 0, notation_offset])
                notation_letter("U");
        // Bottom center → "D"
        if (is_center_z && gz == 0)
            translate([0, 0, -notation_offset])
                rotate([180, 0, 0])
                    notation_letter("D");
        // Front center → "F"
        if (is_center_y && gy == 0)
            translate([0, -notation_offset, 0])
                rotate([90, 0, 0])
                    rotate([0, 0, 180])
                        notation_letter("F");
        // Back center → "B"
        if (is_center_y && gy == N - 1)
            translate([0, notation_offset, 0])
                rotate([-90, 0, 0])
                    notation_letter("B");
        // Left center → "L"
        if (is_center_x && gx == 0)
            translate([-notation_offset, 0, 0])
                rotate([0, -90, 0])
                    notation_letter("L");
        // Right center → "R"
        if (is_center_x && gx == N - 1)
            translate([notation_offset, 0, 0])
                rotate([0, 90, 0])
                    notation_letter("R");
    }
}

// Central core mechanism: sphere + 6 axle cylinders (decorative).
module core_decorative() {
    color([0.3, 0.3, 0.3]) {
        // Central sphere
        sphere(d=core_dia, $fn=32);

        // Axle cylinders along +/-X, +/-Y, +/-Z
        // X axis
        rotate([0, 90, 0])
            cyl(d=axle_dia, l=axle_len, $fn=24);
        // Y axis
        rotate([90, 0, 0])
            cyl(d=axle_dia, l=axle_len, $fn=24);
        // Z axis
        cyl(d=axle_dia, l=axle_len, $fn=24);
    }
}

// Functional core mechanism with screw posts and spring cavities.
// Designed for actual 3D printing with M3 hardware.
module core_functional() {
    core_r = cubie_size * 0.45;
    screw_r = screw_dia / 2;
    post_length = cubie_size * 0.4;
    post_r = screw_r + 1.5;

    color([0.3, 0.3, 0.3]) {
        // Solid core sphere with axle through-holes
        difference() {
            sphere(r=core_r, $fn=32);

            // 6 axle through-holes for M3 screws
            // X axis
            rotate([0, 90, 0])
                cylinder(r=screw_r + mechanism_clearance, h=core_r*3, center=true, $fn=16);
            // Y axis
            rotate([90, 0, 0])
                cylinder(r=screw_r + mechanism_clearance, h=core_r*3, center=true, $fn=16);
            // Z axis
            cylinder(r=screw_r + mechanism_clearance, h=core_r*3, center=true, $fn=16);
        }

        // 6 axle posts — screw into core, springs sit on these
        // +X post
        translate([core_r, 0, 0])
            rotate([0, 90, 0])
                _axle_post(post_r, post_length, screw_r);
        // -X post
        translate([-core_r, 0, 0])
            rotate([0, -90, 0])
                _axle_post(post_r, post_length, screw_r);
        // +Y post
        translate([0, core_r, 0])
            rotate([-90, 0, 0])
                _axle_post(post_r, post_length, screw_r);
        // -Y post
        translate([0, -core_r, 0])
            rotate([90, 0, 0])
                _axle_post(post_r, post_length, screw_r);
        // +Z post
        translate([0, 0, core_r])
            _axle_post(post_r, post_length, screw_r);
        // -Z post
        translate([0, 0, -core_r])
            rotate([180, 0, 0])
                _axle_post(post_r, post_length, screw_r);
    }
}

// Helper: single axle post with screw hole (rendered upward along Z).
module _axle_post(post_r, post_length, screw_r) {
    difference() {
        cylinder(r=post_r, h=post_length, $fn=16);
        // Screw hole through the post
        translate([0, 0, -0.5])
            cylinder(r=screw_r + mechanism_clearance, h=post_length + 1, $fn=16);
    }
}

// Internal geometry for center cubies (1 exposed face).
// Subtractive shape: call inside difference() on cubie body.
// face_axis: 0=X, 1=Y, 2=Z; face_sign: +1 or -1
module center_cubie_internal(face_axis, face_sign) {
    spring_cavity_r = spring_dia / 2 + mechanism_clearance;
    spring_cavity_h = spring_length + 2;
    track_width = cubie_size * 0.3;
    track_depth = cubie_size * 0.15;

    // T-track rail slot on opposite (internal) face — allows adjacent cubies to slide
    // Orient the track perpendicular to the exposed face axis
    if (face_axis == 2) {
        // Z-exposed: track on internal -Z/+Z face
        translate([0, 0, -face_sign * cubie_size / 2])
            cube([track_width, cubie_size * 0.8, track_depth * 2], center=true);
    } else if (face_axis == 1) {
        translate([0, -face_sign * cubie_size / 2, 0])
            cube([track_width, track_depth * 2, cubie_size * 0.8], center=true);
    } else {
        translate([-face_sign * cubie_size / 2, 0, 0])
            cube([track_depth * 2, track_width, cubie_size * 0.8], center=true);
    }

    // Spring cavity (axle-aligned, opens toward core)
    if (face_axis == 2) {
        translate([0, 0, -face_sign * cubie_size / 2])
            cylinder(r=spring_cavity_r, h=spring_cavity_h, center=true, $fn=16);
    } else if (face_axis == 1) {
        translate([0, -face_sign * cubie_size / 2, 0])
            rotate([90, 0, 0])
                cylinder(r=spring_cavity_r, h=spring_cavity_h, center=true, $fn=16);
    } else {
        translate([-face_sign * cubie_size / 2, 0, 0])
            rotate([0, 90, 0])
                cylinder(r=spring_cavity_r, h=spring_cavity_h, center=true, $fn=16);
    }

    // Screw through-hole along the face axis
    if (face_axis == 2) {
        cylinder(r=screw_dia / 2 + mechanism_clearance, h=cubie_size * 2, center=true, $fn=16);
    } else if (face_axis == 1) {
        rotate([90, 0, 0])
            cylinder(r=screw_dia / 2 + mechanism_clearance, h=cubie_size * 2, center=true, $fn=16);
    } else {
        rotate([0, 90, 0])
            cylinder(r=screw_dia / 2 + mechanism_clearance, h=cubie_size * 2, center=true, $fn=16);
    }
}

// ── Anti-Pop Torpedo fin (DaYan 2011) ──
// Extends from each side of an edge piece, slides under adjacent corners.
// Called additively (not in difference) on edge cubies.
module torpedo_fin(direction) {
    if (enable_torpedoes) {
        fin_w = torpedo_thickness;
        fin_l = torpedo_length;
        fin_h = cubie_size * 0.3;
        translate([direction * (cubie_size / 2 - 0.1), 0, -cubie_size / 2 + fin_h / 2])
            cube([fin_w, fin_l, fin_h], center=true);
    }
}

// Torpedo slot in corner cubies — groove where the torpedo fin slides.
module torpedo_slot() {
    if (enable_torpedoes) {
        slot_w = torpedo_thickness + mechanism_clearance * 2;
        slot_l = torpedo_length + mechanism_clearance * 2;
        slot_h = cubie_size * 0.35;
        // Slots on each internal face where an edge torpedo would engage
        for (angle = [0, 90, 180, 270]) {
            rotate([0, 0, angle])
                translate([cubie_size / 2 - 0.5, 0, -cubie_size / 2 + slot_h / 2])
                    cube([slot_w + 1, slot_l, slot_h], center=true);
        }
    }
}

// ── Corner Cutting bevels (DaYan 2010) ──
// Beveled entries on T-track rails allow misaligned turning.
module corner_cut_bevel(track_w, track_d, axis) {
    if (enable_corner_cutting) {
        bevel = track_bevel;
        // Add chamfered entries at both ends of the track slot
        for (end_sign = [-1, 1]) {
            if (axis == 0) {
                translate([0, end_sign * track_w * 0.4, 0])
                    rotate([0, 0, 45])
                        cube([bevel, bevel, track_d * 2], center=true);
            } else if (axis == 1) {
                translate([end_sign * track_w * 0.4, 0, 0])
                    rotate([0, 0, 45])
                        cube([bevel, bevel, track_d * 2], center=true);
            } else {
                translate([end_sign * track_w * 0.4, 0, 0])
                    rotate([45, 0, 0])
                        cube([track_d * 2, bevel, bevel], center=true);
            }
        }
    }
}

// ── Magnet cavities (2016+) ──
// Cylindrical pocket for a neodymium disc magnet.
module magnet_cavity() {
    if (enable_magnets) {
        cylinder(d=magnet_dia, h=magnet_depth + 0.2, $fn=20);
    }
}

// Edge magnet cavities — 2 magnets per edge (one toward each adjacent corner).
module edge_magnet_cavities() {
    if (enable_magnets) {
        mag_offset = cubie_size / 2 - magnet_depth / 2;
        // Magnets on the two internal faces (toward corners)
        for (angle = [45, -45]) {
            rotate([0, 0, angle])
                translate([mag_offset, 0, 0])
                    rotate([0, 90, 0])
                        magnet_cavity();
        }
    }
}

// Corner magnet cavities — 3 magnets per corner (one toward each adjacent edge).
module corner_magnet_cavities() {
    if (enable_magnets) {
        mag_offset = cubie_size / 2 - magnet_depth / 2;
        // Magnets on the three internal faces
        for (axis = [0, 1, 2]) {
            if (axis == 0) {
                translate([0, 0, -mag_offset])
                    magnet_cavity();
            } else if (axis == 1) {
                translate([0, -mag_offset, 0])
                    rotate([90, 0, 0])
                        magnet_cavity();
            } else {
                translate([-mag_offset, 0, 0])
                    rotate([0, 90, 0])
                        magnet_cavity();
            }
        }
    }
}

// Core-corner magnet cavities (Gan 2018) — on the core sphere at 8 corner positions.
module core_corner_magnet_cavities() {
    if (enable_core_magnets) {
        core_r = cubie_size * 0.45;
        for (dx = [-1, 1])
            for (dy = [-1, 1])
                for (dz = [-1, 1]) {
                    dir = [dx, dy, dz] / norm([dx, dy, dz]);
                    translate(dir * core_r)
                        rotate([0, acos(dz), atan2(dy, dx)])
                            cylinder(d=core_magnet_dia, h=core_magnet_depth, $fn=16);
                }
    }
}

// ── Maglev ring magnets (2020s) ──
// Ring magnet on center post — replaces spring.
module maglev_rings(post_length) {
    if (enable_maglev) {
        ring_r = maglev_ring_dia / 2;
        ring_ir = screw_dia / 2 + 0.5;  // inner radius (screw clearance)
        // Fixed ring at core end
        translate([0, 0, 0])
            difference() {
                cylinder(r=ring_r, h=maglev_ring_height, $fn=20);
                translate([0, 0, -0.5])
                    cylinder(r=ring_ir, h=maglev_ring_height + 1, $fn=16);
            }
        // Floating ring (pushed by repulsion)
        translate([0, 0, maglev_ring_height + maglev_gap])
            difference() {
                cylinder(r=ring_r, h=maglev_ring_height, $fn=20);
                translate([0, 0, -0.5])
                    cylinder(r=ring_ir, h=maglev_ring_height + 1, $fn=16);
            }
    }
}

// Internal geometry for edge cubies (2 exposed faces).
// Subtractive shape: spherical pocket that rides on core surface + foot slots.
module edge_cubie_internal() {
    rail_r = cubie_size * 0.45 + mechanism_clearance;
    foot_width = cubie_size * 0.25;
    foot_depth = cubie_size * 0.12;
    foot_length = cubie_size * 0.6;

    // Inner spherical pocket — rides on core surface
    sphere(r=rail_r, $fn=24);

    // Two sliding feet (oriented for T-track engagement at 0 and 90 deg)
    for (angle = [0, 90]) {
        rotate([0, 0, angle])
            translate([0, 0, -cubie_size / 2 + foot_depth / 2])
                cube([foot_width, foot_length, foot_depth], center=true);
    }

    // Magnet cavities (2016+ magnetic cubes)
    edge_magnet_cavities();
}

// Internal geometry for corner cubies (3 exposed faces).
// Subtractive shape: larger spherical pocket + three angled feet.
module corner_cubie_internal() {
    pocket_r = cubie_size * 0.45 + mechanism_clearance * 2;
    foot_size = cubie_size * 0.15;

    // Spherical pocket — rides on core with extra clearance
    sphere(r=pocket_r, $fn=24);

    // Three angled retention feet
    for (dx = [-1, 1]) {
        for (dy = [-1, 1]) {
            translate([dx * cubie_size * 0.3, dy * cubie_size * 0.3, -cubie_size / 2])
                cube([foot_size, foot_size, foot_size * 0.8], center=true);
        }
    }

    // Magnet cavities (2016+ magnetic cubes)
    corner_magnet_cavities();

    // Torpedo slots (DaYan 2011 anti-pop)
    torpedo_slot();
}

// Dispatches to decorative or functional core.
module core_mechanism() {
    if (mechanism_detail == "functional") {
        difference() {
            core_functional();
            // Subtract core-corner magnet cavities (Gan 2018)
            core_corner_magnet_cavities();
        }
        // Add maglev ring magnets on center posts (2020s)
        if (enable_maglev) {
            post_length = cubie_size * 0.4;
            for (axis = [0, 1, 2]) {
                for (sign = [-1, 1]) {
                    if (axis == 0)
                        translate([sign * (core_radius + 0.5), 0, 0])
                            rotate([0, sign * 90, 0])
                                maglev_rings(post_length);
                    else if (axis == 1)
                        translate([0, sign * (core_radius + 0.5), 0])
                            rotate([sign * -90, 0, 0])
                                maglev_rings(post_length);
                    else
                        translate([0, 0, sign * (core_radius + 0.5)])
                            rotate([sign > 0 ? 0 : 180, 0, 0])
                                maglev_rings(post_length);
                }
            }
        }
    } else {
        core_decorative();
    }
}

// Shared grid traversal: positions and rotates a child at each visible cubie location.
module for_each_cubie() {
    for (gx = [0 : N-1])
        for (gy = [0 : N-1])
            for (gz = [0 : N-1]) {
                if (gx == 0 || gx == N-1 ||
                    gy == 0 || gy == N-1 ||
                    gz == 0 || gz == N-1) {

                    base_x = grid_offset + gx * pitch;
                    base_y = grid_offset + gy * pitch;
                    base_z = grid_offset + gz * pitch;

                    ex = (explode_factor / 100) * base_x * 0.6;
                    ey = (explode_factor / 100) * base_y * 0.6;
                    ez = (explode_factor / 100) * base_z * 0.6;

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
}

// Render stickers for a single face across all cubies.
// face_id: 0=top, 1=bottom, 2=front, 3=back, 4=left, 5=right
module face_stickers_layer(face_id) {
    fc = face_colors[face_id];
    for (gx = [0 : N-1])
        for (gy = [0 : N-1])
            for (gz = [0 : N-1]) {
                if (gx == 0 || gx == N-1 ||
                    gy == 0 || gy == N-1 ||
                    gz == 0 || gz == N-1) {

                    base_x = grid_offset + gx * pitch;
                    base_y = grid_offset + gy * pitch;
                    base_z = grid_offset + gz * pitch;
                    ex = (explode_factor / 100) * base_x * 0.6;
                    ey = (explode_factor / 100) * base_y * 0.6;
                    ez = (explode_factor / 100) * base_z * 0.6;

                    z_rotations = [rotate_bottom, rotate_z_1, rotate_z_2, rotate_z_3, rotate_z_4, rotate_z_5, rotate_z_6, rotate_z_7, rotate_top];
                    y_rotations = [-rotate_front, rotate_y_1, rotate_y_2, rotate_y_3, rotate_y_4, rotate_y_5, rotate_y_6, rotate_y_7, rotate_back];
                    x_rotations = [-rotate_left, rotate_x_1, rotate_x_2, rotate_x_3, rotate_x_4, rotate_x_5, rotate_x_6, rotate_x_7, rotate_right];

                    rot_z = (gz < len(z_rotations)) ? z_rotations[gz] : 0;
                    rot_y = (gy < len(y_rotations)) ? y_rotations[gy] : 0;
                    rot_x = (gx < len(x_rotations)) ? x_rotations[gx] : 0;

                    translate([base_x + ex, base_y + ey, base_z + ez])
                        rotate([rot_x, rot_y, rot_z]) {
                            if (face_id == 0 && gz == N-1) face_sticker(2, 1, fc, face_index=0);
                            if (face_id == 1 && gz == 0)   face_sticker(2, -1, fc, face_index=1);
                            if (face_id == 2 && gy == 0)   face_sticker(1, -1, fc, face_index=2);
                            if (face_id == 3 && gy == N-1) face_sticker(1, 1, fc, face_index=3);
                            if (face_id == 4 && gx == 0)   face_sticker(0, -1, fc, face_index=4);
                            if (face_id == 5 && gx == N-1) face_sticker(0, 1, fc, face_index=5);
                        }
                }
            }
}

// Full Rubik's cube assembly with layer rotations and explosion.
// render_mode: 0=all, 1=cubies+stickers, 2=core,
//              3=top stickers, 4=bottom, 5=front, 6=back, 7=left, 8=right
module rubiks_cube() {
    // Render cubies (body only when face-split modes 3-8 are active)
    if (show_cubies && (render_mode == 0 || render_mode == 1)) {
        for_each_cubie();
    }

    // Render individual face sticker layers (render_modes 3-8)
    if (render_mode == 3) face_stickers_layer(0);  // Top
    if (render_mode == 4) face_stickers_layer(1);  // Bottom
    if (render_mode == 5) face_stickers_layer(2);  // Front
    if (render_mode == 6) face_stickers_layer(3);  // Back
    if (render_mode == 7) face_stickers_layer(4);  // Left
    if (render_mode == 8) face_stickers_layer(5);  // Right

    // Render core
    if (show_core && (render_mode == 0 || render_mode == 2)) {
        core_mechanism();
    }
}

/* ─── Top-level render ─── */

if (is_library == 0) {
    // Shift entire cube into the positive quadrant (X+, Y+, Z+)
    translate([half_extent, half_extent, half_extent])
        rubiks_cube();
}
