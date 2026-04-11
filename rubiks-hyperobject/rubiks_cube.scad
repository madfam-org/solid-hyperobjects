// rubiks_cube.scad — Parametric NxNxN Rubik's Cube
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// A fully parametric Rubik's puzzle cube using BOSL2 for rounding
// and primitive geometry. Supports 2x2 through 5x5, layer rotations,
// exploded views, and separate core/cubie rendering.

include <../../libs/BOSL2/std.scad>

/* [Puzzle Grid] */
// Grid size: 2=Pocket, 3=Standard, 4=Revenge, 5=Professor
N = is_undef(N) ? 3 : N;
// Overall cube dimension (mm)
size = is_undef(size) ? 57 : size;
// Gap between cubies (mm)
clearance = is_undef(clearance) ? 0.3 : clearance;

/* [Cubie Appearance] */
// Edge rounding on cubies (mm)
corner_rounding = is_undef(corner_rounding) ? 1.5 : corner_rounding;
// Face color inset depth (mm)
sticker_depth = is_undef(sticker_depth) ? 0.3 : sticker_depth;

/* [Layer Rotation] */
// Top layer rotation (degrees): 0, 90, 180, 270
rotate_top = is_undef(rotate_top) ? 0 : rotate_top;
// Front layer rotation (degrees): 0, 90, 180, 270
rotate_front = is_undef(rotate_front) ? 0 : rotate_front;
// Right layer rotation (degrees): 0, 90, 180, 270
rotate_right = is_undef(rotate_right) ? 0 : rotate_right;

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

/* ─── Standard Rubik's face colors ─── */

// Face colors indexed by face ID:
// 0=Top(white), 1=Bottom(yellow), 2=Front(red),
// 3=Back(orange), 4=Left(blue), 5=Right(green)
face_colors = [
    [1.0, 1.0, 1.0],   // 0: Top — White
    [1.0, 0.85, 0.0],   // 1: Bottom — Yellow
    [0.8, 0.0, 0.0],    // 2: Front — Red
    [1.0, 0.5, 0.0],    // 3: Back — Orange
    [0.0, 0.0, 0.8],    // 4: Left — Blue
    [0.0, 0.6, 0.0]     // 5: Right — Green
];

// Body color (black plastic)
body_color = [0.12, 0.12, 0.12];

/* ─── Modules ─── */

// Render a single face sticker on one side of a cubie.
// axis: 0=X, 1=Y, 2=Z
// sign: +1 or -1 (which face along that axis)
// fc: color as [r,g,b]
module face_sticker(axis, sign, fc) {
    sticker_size = cubie_size * 0.82;
    sticker_thick = sticker_depth;
    sticker_rounding = min(safe_rounding * 0.6, sticker_size / 2 - 0.01);

    // Position: offset from cubie center to just outside the face
    offset_dist = cubie_size / 2 + sticker_thick / 2 - 0.01;

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

// Render a single cubie at grid position (gx, gy, gz).
// Grid indices run from 0 to N-1.
module cubie(gx, gy, gz) {
    // Body
    color(body_color)
        cuboid([cubie_size, cubie_size, cubie_size],
               rounding=safe_rounding);

    // Stickers on exposed faces only
    // Top face: gz == N-1
    if (gz == N - 1)
        face_sticker(2, 1, face_colors[0]);
    // Bottom face: gz == 0
    if (gz == 0)
        face_sticker(2, -1, face_colors[1]);
    // Front face: gy == 0
    if (gy == 0)
        face_sticker(1, -1, face_colors[2]);
    // Back face: gy == N-1
    if (gy == N - 1)
        face_sticker(1, 1, face_colors[3]);
    // Left face: gx == 0
    if (gx == 0)
        face_sticker(0, -1, face_colors[4]);
    // Right face: gx == N-1
    if (gx == N - 1)
        face_sticker(0, 1, face_colors[5]);
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

                        // Determine layer rotation for this cubie
                        // Top layer: gz == N-1, rotate around Z
                        rot_z = (gz == N - 1) ? rotate_top : 0;
                        // Front layer: gy == 0, rotate around Y (negative for standard orientation)
                        rot_y = (gy == 0) ? -rotate_front : 0;
                        // Right layer: gx == N-1, rotate around X
                        rot_x = (gx == N - 1) ? rotate_right : 0;

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
