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
    } else {
        // Color mode: original colored sticker
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

    // Body — use difference() when sockets are enabled to subtract pockets
    if (show_sockets) {
        difference() {
            color(body_color)
                cuboid([cubie_size, cubie_size, cubie_size],
                       rounding=safe_rounding);

            // Subtract socket pockets from each exposed face
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
    } else {
        // No sockets — render body normally
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

// Central core mechanism: sphere + 6 axle cylinders.
module core_mechanism() {
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

// Full Rubik's cube assembly with layer rotations and explosion.
module rubiks_cube() {
    // Render cubies
    if (show_cubies && (render_mode == 0 || render_mode == 1)) {
        for (gx = [0 : N-1])
            for (gy = [0 : N-1])
                for (gz = [0 : N-1]) {
                    // Skip purely interior cubies (not visible)
                    if (gx == 0 || gx == N-1 ||
                        gy == 0 || gy == N-1 ||
                        gz == 0 || gz == N-1) {

                        // Base position in grid
                        base_x = grid_offset + gx * pitch;
                        base_y = grid_offset + gy * pitch;
                        base_z = grid_offset + gz * pitch;

                        // Explosion: move outward from center
                        ex = (explode_factor / 100) * base_x * 0.6;
                        ey = (explode_factor / 100) * base_y * 0.6;
                        ez = (explode_factor / 100) * base_z * 0.6;

                        // Layer rotation lookup arrays (indices 0..8, supporting up to 9x9)
                        // Z-axis: [bottom, z_1..z_7, top]
                        z_rotations = [rotate_bottom, rotate_z_1, rotate_z_2, rotate_z_3, rotate_z_4, rotate_z_5, rotate_z_6, rotate_z_7, rotate_top];
                        // Y-axis: [front(negated), y_1..y_7, back]
                        y_rotations = [-rotate_front, rotate_y_1, rotate_y_2, rotate_y_3, rotate_y_4, rotate_y_5, rotate_y_6, rotate_y_7, rotate_back];
                        // X-axis: [left(negated), x_1..x_7, right]
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

    // Render core
    if (show_core && (render_mode == 0 || render_mode == 2)) {
        core_mechanism();
    }
}

/* ─── Top-level render ─── */

if (is_library == 0) {
    rubiks_cube();
}
