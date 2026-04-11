// insert.scad — CDG Insert Tile for Rubik's Cube cubies
// Yantra4D Hyperobject — CERN-OHL-W-2.0
//
// Renders a single insert tile that snaps into the cubie socket pockets.
// Print one per exposed face, in the desired face color.
//
// Usage:
//   openscad -o insert.stl insert.scad
//   openscad -o insert_5x5.stl -D "N=5" -D "size=80" insert.scad

include <../../libs/BOSL2/std.scad>

/* [Puzzle Grid] */
N = is_undef(N) ? 3 : N;
size = is_undef(size) ? 57 : size;
clearance = is_undef(clearance) ? 0.3 : clearance;

/* [Insert Dimensions] */
insert_pocket_depth = is_undef(insert_pocket_depth) ? 1.5 : insert_pocket_depth;
insert_pin_dia = is_undef(insert_pin_dia) ? 1.0 : insert_pin_dia;
insert_pin_height = is_undef(insert_pin_height) ? 1.0 : insert_pin_height;
corner_rounding = is_undef(corner_rounding) ? 1.5 : corner_rounding;

/* [Render Control] */
render_mode = is_undef(render_mode) ? 0 : render_mode;

/* --- Derived --- */
cubie_size = (size - (N + 1) * clearance) / N;
pocket_size = cubie_size * 0.78;

/* --- Module --- */

// Insert tile: flat plate that fits into the socket pocket
module insert_tile() {
    insert_clearance = 0.15;
    tile_size = pocket_size - insert_clearance * 2;
    tile_thick = insert_pocket_depth - 0.2;

    union() {
        // Base plate with rounded edges
        cuboid([tile_size, tile_size, tile_thick],
               rounding=corner_rounding * 0.3, edges="Z",
               anchor=BOTTOM);

        // Two alignment pins (matching socket holes at diagonal corners)
        pin_offset = pocket_size * 0.35;
        for (pos = [[-pin_offset, -pin_offset], [pin_offset, pin_offset]]) {
            translate([pos[0], pos[1], tile_thick])
                cylinder(r=insert_pin_dia/2 - 0.05, h=insert_pin_height, $fn=16);
        }
    }
}

/* --- Top-level render --- */
insert_tile();
