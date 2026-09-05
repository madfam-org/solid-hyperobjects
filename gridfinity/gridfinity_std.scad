// ============================================================================
// gridfinity_std.scad — shared Gridfinity geometry for the OpenSCAD-engine
// modes of the `gridfinity` cartridge (cup / baseplate_scad / lid).
//
// CLEAN-ROOM PROVENANCE
//   Authored by Innovaciones MADFAM for the MADFAM Open Commons Hyperobjects
//   collection under CERN-OHL-W-2.0. Written from the publicly documented
//   Gridfinity specification (gridfinity.xyz, Zack Freedman / Voidstar Lab)
//   and from a recorded measurement baseline of the cartridge's own manifest
//   contract. No prior implementation of Gridfinity — in this repository, in
//   any archived satellite, or upstream — was read, consulted or copied while
//   writing this file. See ../NOTICE and docs/CLEANROOM-VERIFICATION.md.
//
// THE STANDARD IMPLEMENTED HERE
//   Grid module      42.0 mm in X and Y; one "unit" of footprint.
//   Height unit       7.0 mm in Z.
//   Bin footprint    42*n - 0.5 mm  (0.5 mm total clearance per pitch, so
//                    neighbouring bins in a drawer do not bind).
//   Corner radius     3.75 mm at the widest point of the profile.
//   Base profile     a three-step chamfer stack, bottom-up:
//                        0.80 mm chamfer at 45 deg
//                        1.80 mm straight wall
//                        2.15 mm chamfer at 45 deg
//                    = 4.75 mm; each 45 deg chamfer narrows the section by its
//                    own height on every side, so for a 41.5 mm cell the
//                    sections are 35.6 / 37.2 / 37.2 / 41.5 mm.
//   Foot height       5.00 mm: the 4.75 mm profile plus a 0.25 mm straight
//                    riser at full width, which is where the body starts.
//   Stacking lip     the same profile repeated at the top of a bin, so the
//                    foot of the bin above nests into it.
//   Socket clearance 0.25 mm nominal (0.125 mm per side), so a foot topping
//                    out at 41.5 mm enters a 41.75 mm socket mouth and the
//                    sockets of adjacent cells keep a 0.25 mm rib between them.
//   Magnet socket     6 mm dia x 2 mm deep, on a 26 x 26 mm square about the
//                    cell centre.
//   Screw hole       M3 clearance (3.4 mm), coaxial with the magnet sockets.
// ============================================================================

// No library include. Every primitive this cartridge needs — a rounded
// rectangle, a hull between two sections, a cylinder — is an OpenSCAD builtin,
// so the three modes render with nothing on OPENSCADPATH. BOSL2 (BSD-2-Clause)
// is available in the commons at libs/BOSL2 and would have been permitted, but
// declaring a dependency this code does not use would be a false statement
// about what it needs.

// -- Canonical constants -----------------------------------------------------
GF_PITCH        = 42.0;   // grid module, X and Y
GF_ZUNIT        =  7.0;   // height unit
GF_CLEAR        =  0.5;   // total bin clearance per pitch
GF_CELL         = GF_PITCH - GF_CLEAR;   // 41.5 mm, the bin's per-cell width
GF_R            =  3.75;  // corner radius at the widest section

GF_C1           =  0.80;  // lower chamfer height (45 deg)
GF_WALL         =  1.80;  // middle straight section
GF_C2           =  2.15;  // upper chamfer height (45 deg)
GF_PROFILE_H    = GF_C1 + GF_WALL + GF_C2;   // 4.75 mm
GF_RISER        =  0.25;  // straight riser above the profile
GF_FOOT_H       = GF_PROFILE_H + GF_RISER;   // 5.00 mm

GF_SOCKET_CLEAR =  0.125; // per side; 0.25 mm nominal diametral clearance

GF_MAG_D        =  6.0;   // magnet diameter
GF_MAG_H        =  2.0;   // magnet depth
GF_MAG_PITCH    = 26.0;   // magnet centres, square about the cell centre
GF_SCREW_D      =  3.4;   // M3 clearance

GF_LID_CLEAR    =  1.0;   // total lid clearance per pitch -> 42*n - 1.0

// Resolve the manifest's `fn` parameter. The manifest documents 0 as "auto";
// auto is 32, the value the platform's other rounded cartridges use.
function gf_fn(fn) = fn > 0 ? fn : 32;

// -- Rounded-rectangle prism -------------------------------------------------
// A prism of size [x, y] and height h, base at z = 0, centred in X and Y, with
// vertical edges filleted to radius r. r is clamped so it can never exceed half
// the shorter side.
module gf_rrect(x, y, h, r) {
    rr = max(0.01, min(r, min(x, y) / 2 - 0.001));
    linear_extrude(height = max(0.001, h))
        offset(r = rr) offset(r = -rr)
            square([max(0.02, x), max(0.02, y)], center = true);
}

// -- The base profile as a solid of revolution-free extrusion ----------------
// One cell's foot, base at z = 0, built as four stacked sections. `grow` widens
// every section on each side (used to make the baseplate socket, which is this
// same profile enlarged by the clearance).
//
//   z 0.00 .. 0.80   chamfer: (top - 2*C2 - 2*C1) -> (top - 2*C2)
//   z 0.80 .. 2.60   straight at (top - 2*C2)
//   z 2.60 .. 4.75   chamfer: (top - 2*C2) -> top
//   z 4.75 .. 5.00   straight at top
//
// The corner radius tracks the width so the fillet keeps a constant offset from
// the corner: r shrinks by the same amount the section does.
module gf_foot_profile(grow = 0, with_riser = true) {
    w_top = GF_CELL      + 2 * grow;
    w_mid = w_top - 2 * GF_C2;
    w_bot = w_mid - 2 * GF_C1;

    r_top = GF_R          + grow;
    r_mid = max(0.01, r_top - GF_C2);
    r_bot = max(0.01, r_mid - GF_C1);

    // lower chamfer
    hull() {
        gf_rrect(w_bot, w_bot, 0.001, r_bot);
        translate([0, 0, GF_C1]) gf_rrect(w_mid, w_mid, 0.001, r_mid);
    }
    // straight middle
    translate([0, 0, GF_C1]) gf_rrect(w_mid, w_mid, GF_WALL, r_mid);
    // upper chamfer
    translate([0, 0, GF_C1 + GF_WALL]) hull() {
        gf_rrect(w_mid, w_mid, 0.001, r_mid);
        translate([0, 0, GF_C2]) gf_rrect(w_top, w_top, 0.001, r_top);
    }
    // riser to the full 5 mm foot height
    if (with_riser)
        translate([0, 0, GF_PROFILE_H]) gf_rrect(w_top, w_top, GF_RISER, r_top);
}

// -- Grid helpers ------------------------------------------------------------
// Centre of cell (ix, iy) in a nx x ny grid, the whole grid centred on origin.
function gf_cell_x(ix, nx) = (ix - (nx - 1) / 2) * GF_PITCH;
function gf_cell_y(iy, ny) = (iy - (ny - 1) / 2) * GF_PITCH;

// The bin's overall footprint.
function gf_body_x(nx) = nx * GF_PITCH - GF_CLEAR;
function gf_body_y(ny) = ny * GF_PITCH - GF_CLEAR;

// The four magnet/screw centres of one cell, relative to the cell centre.
function gf_mag_offsets() = [
    [-GF_MAG_PITCH / 2, -GF_MAG_PITCH / 2],
    [ GF_MAG_PITCH / 2, -GF_MAG_PITCH / 2],
    [-GF_MAG_PITCH / 2,  GF_MAG_PITCH / 2],
    [ GF_MAG_PITCH / 2,  GF_MAG_PITCH / 2],
];
