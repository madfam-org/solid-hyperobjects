// rubiks_cube.scad — Parametric NxNxN Rubik's Cube
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// A fully parametric Rubik's puzzle cube using BOSL2 for rounding
// and primitive geometry. Supports 2x2 through 9x9, layer rotations
// (including middle layers), exploded views, and separate core/cubie rendering.

include <BOSL2/std.scad>

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

// How far a face-venting cutter is pushed past the surface it opens through.
// A cutter that stops exactly ON the face produces a coincident-face contact rather
// than an opening, sealing the cavity behind it into an inverted shell. The vent has
// to clear the sticker plate as well: a sticker sits on the face and reaches
// `sticker_depth - 0.01` beyond it, and it is part of the difference() minuend, so a
// cut that stops short of its outer surface is re-sealed by the sticker. Everything
// this adds lies outside the cubie body, so the printed pocket is unchanged.
vent_overshoot = sticker_depth + 0.5;

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

    // Position: offset from cubie center to just outside the face.
    //
    // How far the sticker stands PROUD of the face is clamped to less than half
    // the inter-cubie gap. A sticker seated flush stands `sticker_thick - 0.01`
    // proud (0.29 mm at the defaults) against a `clearance` of 0.3 mm, so two
    // stickers FACING each other across a gap interpenetrate by 0.28 mm and the
    // two cubies fuse into one body. In the solved cube every sticker points
    // outward and nothing faces anything, which is why this only shows up once a
    // layer is turned: at `checkerboard` (all six faces at 90 deg) exactly two
    // pairs come to face each other and `cubies` rendered 25 bodies instead of
    // N*N*N - (N-2)^3 = 26. Sinking the sticker instead of clamping it would
    // change every solved render; clamping changes only the turned ones, and
    // only by the 0.04 mm the sticker is pulled back at the defaults.
    max_proud = max(0, clearance / 2 - 0.02);
    proud = min(sticker_thick - 0.01, max_proud);
    offset_dist = cubie_size / 2 - sticker_thick / 2 + proud;

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
        // Sit the overlay on the sticker's OUTER face, which the clamp above may
        // have pulled back; `cubie_size/2 + sticker_thick` assumed the unclamped
        // seating and would push the raised pattern back across the gap.
        dot_offset = offset_dist + sticker_thick / 2;
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
        // Sit the overlay on the sticker's OUTER face, which the clamp above may
        // have pulled back; `cubie_size/2 + sticker_thick` assumed the unclamped
        // seating and would push the raised pattern back across the gap.
        dot_offset = offset_dist + sticker_thick / 2;
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

// Stickers on the exposed faces of the cubie at grid position (gx, gy, gz).
// Kept as its own module so it can be unioned INTO the difference() minuend in
// cubie() — see the note there.
module cubie_stickers(gx, gy, gz) {
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

    // Body — difference() subtracts sockets and/or functional mechanism internals.
    //
    // The stickers are part of the MINUEND, not a separate union member added after
    // the difference. A sticker plate sits 0.01 mm proud of the face it covers, so a
    // sticker unioned onto a finished body re-seals every pocket that opens through
    // that face: at mechanism_detail="functional" the bottom-layer cubies' retention
    // feet and spherical pockets vent through -Z, and the bottom sticker capped them
    // into closed cavities, which OpenSCAD exports as inverted (negative-volume)
    // shells. Cutting the cavities out of body+stickers together keeps those vents
    // open, so every cubie is one positive watertight solid.
    _need_diff = show_sockets || mechanism_detail == "functional";

    if (_need_diff) {
        difference() {
            union() {
                color(body_color)
                    cuboid([cubie_size, cubie_size, cubie_size],
                           rounding=safe_rounding);
                cubie_stickers(gx, gy, gz);
            }

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
        // No sockets, no functional mechanism — render body plus stickers normally
        color(body_color)
            cuboid([cubie_size, cubie_size, cubie_size],
                   rounding=safe_rounding);
        cubie_stickers(gx, gy, gz);
    }

    // Anti-pop torpedo fins on the EDGE pieces (DaYan 2011).
    //
    // `torpedo_slot()` was already cut into every corner piece, but `torpedo_fin()`
    // — the fin that slides into that slot — was dead code, so `enable_torpedoes`
    // only ever removed material and never added the mating half. The fins are
    // additive, so they sit outside the difference() above, and only on the two
    // internal +/-X faces the edge piece presents to its neighbouring corners —
    // the same frame `edge_cubie_internal()` and `edge_magnet_cavities()` use.
    //
    // A fin reaches `cubie_size/2 - 0.1 + torpedo_thickness/2` from the cubie
    // centre, i.e. `torpedo_thickness/2 - 0.1` proud of the face. The manifest's
    // own constraint keeps `torpedo_length` inside the cubie, but nothing bounded
    // the proud height against `clearance`, so at the slider's 1.5 mm maximum a
    // fin stood 0.65 mm proud into a 0.3 mm gap and fused the edge to its
    // neighbour. Seat the fin so it never crosses half the gap; it still engages,
    // because the corner's slot is cut `mechanism_clearance` oversize and reaches
    // 0.5 mm INTO the corner.
    if (mechanism_detail == "functional" && enable_torpedoes && exposed_count == 2) {
        color(body_color)
        for (direction = [-1, 1])
            torpedo_fin(direction);
    }

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

    // Where each post's base plane has to sit for the post to actually MEET the core.
    // Seating it at core_r makes the post tangent to the sphere at a single axis
    // point: its whole rim is outside the sphere, so the union is seven disconnected
    // bodies (one sphere, six posts) — a core that would fall apart off the plate.
    // Backing the base off by the chord depth of a post_r circle on the sphere buries
    // the entire rim, so the six posts and the sphere fuse into one solid.
    post_seat = (post_r < core_r)
        ? sqrt(core_r * core_r - post_r * post_r) - 0.01
        : 0;

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
        translate([post_seat, 0, 0])
            rotate([0, 90, 0])
                _axle_post(post_r, post_length + (core_r - post_seat), screw_r);
        // -X post
        translate([-post_seat, 0, 0])
            rotate([0, -90, 0])
                _axle_post(post_r, post_length + (core_r - post_seat), screw_r);
        // +Y post
        translate([0, post_seat, 0])
            rotate([-90, 0, 0])
                _axle_post(post_r, post_length + (core_r - post_seat), screw_r);
        // -Y post
        translate([0, -post_seat, 0])
            rotate([90, 0, 0])
                _axle_post(post_r, post_length + (core_r - post_seat), screw_r);
        // +Z post
        translate([0, 0, post_seat])
            _axle_post(post_r, post_length + (core_r - post_seat), screw_r);
        // -Z post
        translate([0, 0, -post_seat])
            rotate([180, 0, 0])
                _axle_post(post_r, post_length + (core_r - post_seat), screw_r);
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
    // The flared mouths ride with the slot: `corner_cut_bevel` is part of the same
    // subtractive shape, so both are cut out of the cubie in one difference().
    track_len = cubie_size * 0.8;
    if (face_axis == 2) {
        // Z-exposed: track on internal -Z/+Z face
        translate([0, 0, -face_sign * cubie_size / 2]) {
            cube([track_width, track_len, track_depth * 2], center=true);
            corner_cut_bevel(track_width, track_depth, track_len, 2);
        }
    } else if (face_axis == 1) {
        translate([0, -face_sign * cubie_size / 2, 0]) {
            cube([track_width, track_depth * 2, track_len], center=true);
            corner_cut_bevel(track_width, track_depth, track_len, 1);
        }
    } else {
        translate([-face_sign * cubie_size / 2, 0, 0]) {
            cube([track_depth * 2, track_width, track_len], center=true);
            corner_cut_bevel(track_width, track_depth, track_len, 0);
        }
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
        // Seat the fin so it stands at most half the inter-cubie gap proud of the
        // face. `cubie_size/2 - 0.1` was authored against a 0.8 mm default fin and
        // leaves `fin_w/2 - 0.1` outside the cubie — 0.65 mm at the slider's 1.5 mm
        // maximum, against a `clearance` of 0.3 mm, which would fuse the edge to
        // its neighbour the moment the fin was actually built.
        max_proud = max(0, clearance / 2 - 0.02);
        proud = min(fin_w / 2 - 0.1, max_proud);
        translate([direction * (cubie_size / 2 - fin_w / 2 + proud), 0,
                   -cubie_size / 2 + fin_h / 2])
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
// Beveled entries on the T-track rail: the mouth at each END of the slot is
// flared out by `track_bevel` at `corner_cut_angle`, so a cubie arriving on a
// layer that is still a few degrees out of line cams into the track instead of
// jamming on its square lip. That flare is what "corner cutting" means.
//
// This module used to be dead code — nothing called it, so `enable_corner_cutting`
// changed no geometry at all (`presets[15]`, `[16]` and `[17]` all rendered the
// identical 84721.94 mm3). It also could not have worked as written: it placed
// its cutters at +/-track_w*0.4, which is 0.4 of the track's WIDTH and lands
// INSIDE the slot rather than at its mouths; it hard-coded 45 deg and ignored
// `corner_cut_angle` entirely; and its `axis` argument did not follow the
// face_axis convention its only plausible caller uses.
//
// Re-authored as a wedge per mouth. `run` is how far along the track the flare
// reaches for a `track_bevel` of lateral opening at `corner_cut_angle`; the
// wedge is an extruded right triangle so the flare grows linearly from nothing
// at `run` inside the mouth to `track_bevel` at the lip.
//
//   face_axis  track long axis   cross-section
//     2 (Z)         Y             X = width, Z = depth
//     1 (Y)         Z             X = width, Y = depth
//     0 (X)         Z             Y = width, X = depth
//
// `track_len` is the slot's own length, so the mouths move with the cubie.

// One mouth flare, in the track's own frame: along-track is Y, across-track is X,
// depth is Z. A triangle per wall, mirrored to both walls, extruded through the
// depth. Defined at file scope because OpenSCAD does not accept a module
// definition inside an `if` block.
module _track_mouth(track_w, track_d, half, bevel, run, end_sign) {
    for (side = [-1, 1]) {
        translate([side * track_w / 2, end_sign * half, 0])
            // `track_d * 2`, the SLOT's own depth, not more: the slot cube is
            // `track_depth * 2` deep and seated on the face, so it reaches
            // track_depth into the cubie. A deeper flare gouges past the slot
            // floor and separates material — at `track_d * 4` the centre cubies
            // split and `cubies` rendered 30 bodies instead of 26.
            linear_extrude(height = track_d * 2, center = true)
                polygon([[0, 0],
                         [side * bevel, 0],
                         [0, -end_sign * run]]);
    }
}

module corner_cut_bevel(track_w, track_d, track_len, face_axis) {
    if (enable_corner_cutting) {
        bevel = track_bevel;
        // At corner_cut_angle from the track wall: opening `bevel` over `run`.
        run = bevel / tan(corner_cut_angle);
        half = track_len / 2;

        for (end_sign = [-1, 1]) {
            if (face_axis == 2) {
                // Track runs along Y, depth along Z — the mouth frame as authored.
                _track_mouth(track_w, track_d, half, bevel, run, end_sign);
            } else if (face_axis == 1) {
                // Track runs along Z, width along X, depth along Y:
                // rotate([90,0,0]) sends the mouth frame's along-track Y to Z and
                // its depth Z to -Y, leaving width on X. Correct.
                rotate([90, 0, 0])
                    _track_mouth(track_w, track_d, half, bevel, run, end_sign);
            } else {
                // Track runs along Z, width along Y, depth along X.
                //
                // `rotate([90,0,0]) rotate([0,0,90])` composes to Rx(90)*Rz(90),
                // which sends width to Z, along-track to -X and depth to -Y — the
                // flare landed across the slot instead of at its mouths and carved
                // four enclosed voids in the two +/-X centre cubies, which OpenSCAD
                // exported as NEGATIVE-volume shells (-3.9845 mm3 each; `cubies`
                // came out 30 bodies instead of 26). `rotate([90,0,90])` is the
                // single rotation that sends width to Y, along-track to Z and depth
                // to X, which is the frame this branch's slot actually uses.
                rotate([90, 0, 90])
                    _track_mouth(track_w, track_d, half, bevel, run, end_sign);
            }
        }
    }
}

// ── Magnet cavities (2016+) ──
// Cylindrical pocket for a neodymium disc magnet.
// The extra `vent_overshoot` is the part that lies outside the face the pocket is
// seated on; the recess left in the printed part is magnet_depth + 0.2 deep, as
// before.
module magnet_cavity() {
    if (enable_magnets) {
        cylinder(d=magnet_dia, h=magnet_depth + 0.2 + vent_overshoot, $fn=20);
    }
}

// Edge magnet cavities — 2 magnets per edge (one toward each adjacent corner).
//
// The pockets sit on the +X and -X faces, the two the edge piece presents to its
// neighbouring corners. They used to be placed at +/-45 deg, aimed into the material
// between two faces: at that angle the cubie boundary is cubie_size/2*sqrt(2) away,
// so a magnet_depth-deep pocket ended inside solid plastic — an enclosed void with no
// way to insert a magnet, which OpenSCAD exports as an inverted shell. Seated on a
// face and cut inward, each pocket is the open, press-fit recess the design means.
module edge_magnet_cavities() {
    if (enable_magnets) {
        for (dir = [-1, 1])
            translate([dir * (cubie_size / 2 + vent_overshoot), 0, 0])
                rotate([0, -dir * 90, 0])
                    magnet_cavity();
    }
}

// Corner magnet cavities — 3 magnets per corner (one toward each adjacent edge).
//
// One pocket per internal face (-X, -Y, -Z), cut inward FROM that face. The previous
// placement started the cylinder at cubie_size/2 - magnet_depth/2 and extruded it
// further inward, so the pocket stopped magnet_depth short of the surface and was a
// sealed void rather than an insertable recess.
module corner_magnet_cavities() {
    if (enable_magnets) {
        // -Z face
        translate([0, 0, -(cubie_size / 2 + vent_overshoot)])
            magnet_cavity();
        // -Y face
        translate([0, -(cubie_size / 2 + vent_overshoot), 0])
            rotate([-90, 0, 0])
                magnet_cavity();
        // -X face
        translate([-(cubie_size / 2 + vent_overshoot), 0, 0])
            rotate([0, 90, 0])
                magnet_cavity();
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

// Opens a spherical socket of radius `r` onto the cubie's internal faces.
//
// A socket whose radius is smaller than cubie_size/2 breaks no face on its own, so
// the sphere alone is a fully enclosed void: not printable (no way to get the core
// in), and exported by OpenSCAD as an inverted, negative-volume shell. `dirs` names
// the internal directions as a [x, y, z] vector of -1 / 0 / +1; for each nonzero
// component this cuts a channel of the socket's own radius out through that face, so
// the socket is genuinely open where the core enters and the piece stays one solid.
module socket_mouth(r, dirs) {
    // Reach past the face (and past any sticker sitting on it) so the mouth is a real
    // opening rather than a coincident-face contact.
    reach = cubie_size / 2 + vent_overshoot;
    for (axis = [0, 1, 2]) {
        d = dirs[axis];
        if (d != 0) {
            if (axis == 0)
                translate([d * reach / 2, 0, 0])
                    rotate([0, 90, 0])
                        cylinder(r=r, h=reach, center=true, $fn=24);
            else if (axis == 1)
                translate([0, d * reach / 2, 0])
                    rotate([90, 0, 0])
                        cylinder(r=r, h=reach, center=true, $fn=24);
            else
                translate([0, 0, d * reach / 2])
                    cylinder(r=r, h=reach, center=true, $fn=24);
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

    // Inner spherical pocket — rides on core surface. Like the corner socket it is
    // smaller than the cubie half-width, so it needs an explicit mouth onto the
    // internal faces; see socket_mouth(). edge_magnet_cavities() below already treats
    // -Z and -X/-Y as this piece's internal sides, and the mouth follows that frame.
    sphere(r=rail_r, $fn=24);
    socket_mouth(rail_r, [0, 0, -1]);

    // Two sliding feet (oriented for T-track engagement at 0 and 90 deg).
    // The slot is deepened by `vent_overshoot` past the -Z face: the design depth is
    // foot_depth, but a cutter whose bottom face is COPLANAR with the cubie face cuts
    // a zero-thickness opening, which leaves the spherical pocket sealed and exported
    // as an inverted shell. The overshoot is outside the cubie, so the printed part
    // keeps exactly the foot_depth pocket it declares.
    for (angle = [0, 90]) {
        rotate([0, 0, angle])
            translate([0, 0, -cubie_size / 2 + foot_depth / 2 - vent_overshoot / 2])
                cube([foot_width, foot_length, foot_depth + vent_overshoot],
                     center=true);
    }

    // Magnet cavities (2016+ magnetic cubes)
    edge_magnet_cavities();
}

// Internal geometry for corner cubies (3 exposed faces).
// Subtractive shape: larger spherical pocket + three angled feet.
module corner_cubie_internal() {
    pocket_r = cubie_size * 0.45 + mechanism_clearance * 2;
    foot_size = cubie_size * 0.15;

    // Spherical pocket — rides on core with extra clearance.
    //
    // The pocket has to OPEN onto the three internal faces: it is the socket the core
    // sits in, so a corner piece is slid on from the inside. pocket_r (0.45*cubie_size
    // + 2*mechanism_clearance) is smaller than cubie_size/2, so the bare sphere breaks
    // no face and is a fully enclosed void — unprintable, and exported as an inverted
    // shell. socket_mouth() below cuts that sphere out to each internal face, which is
    // both the printable shape and a single positive solid.
    sphere(r=pocket_r, $fn=24);
    socket_mouth(pocket_r, [-1, -1, -1]);

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
