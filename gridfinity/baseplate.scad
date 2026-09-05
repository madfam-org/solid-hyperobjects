// ============================================================================
// baseplate.scad — Gridfinity baseplate, OpenSCAD engine, mode `baseplate_scad`.
//
// CLEAN-ROOM PROVENANCE
//   Authored by Innovaciones MADFAM for the MADFAM Open Commons Hyperobjects
//   collection under CERN-OHL-W-2.0, from the publicly documented Gridfinity
//   specification (gridfinity.xyz, Zack Freedman / Voidstar Lab) and from a
//   recorded measurement baseline of this cartridge's own manifest contract.
//   No prior Gridfinity implementation — in this repository's history, in any
//   archived satellite, or upstream — was read or consulted while writing it.
//   No third-party library is used: every primitive is an OpenSCAD
//   builtin. See ../NOTICE.
//
//   Standard implemented: 42 mm grid module, plate footprint 42*n exactly (no
//   clearance subtracted — plates butt against one another), one socket per
//   cell whose surface is the NEGATIVE of the bin's base profile grown by the
//   0.25 mm nominal clearance (0.125 mm per side), 5 mm plate thickness,
//   6 x 2 mm magnet cavities on 26 mm centres, M3 screw clearance.
//
// ONE SHARED PROFILE. The socket is `gf_foot_profile` grown by the clearance —
// the same function the bin's foot is built from — so the two mate by
// construction and cannot drift apart. A foot topping out at 41.5 mm enters a
// 41.75 mm socket mouth; adjacent sockets keep a 0.25 mm rib between them and
// 0.125 mm to the plate edge, so no two cutters ever meet edge-on.
// ============================================================================

include <gridfinity_std.scad>

// -- Manifest parameters (injected with -D by the platform) ------------------
width_units           = 2;      // grid units in X            [1 .. 6]
depth_units           = 2;      // grid units in Y            [1 .. 6]
bp_enable_magnets     = 0;      // 6 x 2 mm magnet cavities under each socket
bp_enable_screws      = 0;      // M3 screw holes through the plate corners
bp_corner_radius      = 3.75;   // radius of the PLATE outline  [0 .. 10]
bp_reduced_wall       = -1;     // -1 = full height, else the wall height (mm)
bp_reduced_wall_taper = 0;      // taper the reduced wall's top edge
fn                    = 0;      // 0 = auto (32)

$fn = gf_fn(fn);

// -- Derived ------------------------------------------------------------------
nx = max(1, min(6, round(width_units)));
ny = max(1, min(6, round(depth_units)));

plate_x = nx * GF_PITCH;        // 42*n exactly — plates butt, bins do not
plate_y = ny * GF_PITCH;
plate_h = GF_FOOT_H;            // 5.0 mm: the socket passes clean through

// The plate outline follows bp_corner_radius. The SOCKET corner radius does
// NOT: it is fixed by the standard at 3.75 mm plus the clearance, because a
// socket wider at the corners than a foot stops accepting a standard bin.
// (The baseline drove both from this one parameter; that is a defect this
// re-creation does not reproduce — see docs/CLEANROOM-VERIFICATION.md.)
plate_r = max(0, min(10, bp_corner_radius));

// Reduced wall: -1 keeps the full 5 mm plate. Any other value lowers the
// material BETWEEN the sockets to that height, leaving the sockets themselves
// full depth — a lighter plate that still seats a bin. It is clamped so the
// socket's own upper chamfer is never cut away.
rw_min = GF_C1 + GF_WALL;                       // 2.6 mm, keep at least this
reduced = bp_reduced_wall >= 0;
rw = reduced ? max(rw_min, min(plate_h, bp_reduced_wall)) : plate_h;

// ============================================================================
// Sockets — the negative of the bin foot, grown by the clearance
//
// With no magnets or screws the socket passes CLEAN THROUGH the 5 mm plate, as
// the standard has it: nothing sits under a bin's foot. Asking for magnets or
// screws needs material there to host them, so the socket is then raised onto a
// `mag_floor` mm floor. The plate's outside dimensions never change — the
// envelope is 42*n x 42*n x 5.0 either way — and the socket's mating surface is
// the same profile at the same clearance, only shortened at the bottom, where
// nothing mates.
// ============================================================================
mag_floor = (bp_enable_magnets > 0 || bp_enable_screws > 0) ? GF_MAG_H + 0.6 : 0;

module bp_sockets() {
    for (ix = [0 : nx - 1], iy = [0 : ny - 1])
        translate([gf_cell_x(ix, nx), gf_cell_y(iy, ny), mag_floor])
            // The riser is included so the socket reaches the plate's top face:
            // profile 4.75 mm + riser 0.25 mm = the full 5 mm thickness.
            gf_foot_profile(grow = GF_SOCKET_CLEAR);
}

// ============================================================================
// Reduced wall — lower the inter-socket material, optionally tapered
//
// The cut is everything above `rw` EXCEPT a collar around each socket that
// keeps the socket's full rim. With the taper on, the collar's outer edge is
// chamfered down to the reduced height instead of standing square.
// ============================================================================
module bp_reduced_cut() {
    if (reduced && rw < plate_h - 0.01) {
        collar = 1.6;   // material kept around each socket mouth
        difference() {
            translate([0, 0, rw])
                gf_rrect(plate_x + 2, plate_y + 2, plate_h - rw + 0.01, 0.01);
            for (ix = [0 : nx - 1], iy = [0 : ny - 1])
                translate([gf_cell_x(ix, nx), gf_cell_y(iy, ny), rw - 0.01])
                    if (bp_reduced_wall_taper > 0)
                        // taper: the collar falls away from the socket rim
                        hull() {
                            gf_rrect(GF_CELL + 2 * GF_SOCKET_CLEAR + 2 * collar,
                                     GF_CELL + 2 * GF_SOCKET_CLEAR + 2 * collar,
                                     0.001, GF_R + GF_SOCKET_CLEAR + collar);
                            translate([0, 0, plate_h - rw + 0.02])
                                gf_rrect(GF_CELL + 2 * GF_SOCKET_CLEAR,
                                         GF_CELL + 2 * GF_SOCKET_CLEAR,
                                         0.001, GF_R + GF_SOCKET_CLEAR);
                        }
                    else
                        gf_rrect(GF_CELL + 2 * GF_SOCKET_CLEAR + 2 * collar,
                                 GF_CELL + 2 * GF_SOCKET_CLEAR + 2 * collar,
                                 plate_h - rw + 0.03,
                                 GF_R + GF_SOCKET_CLEAR + collar);
        }
    }
}

// ============================================================================
// Magnet cavities and screw holes
//
// The magnets sit in the plate's underside, directly beneath the bin's own
// magnet sockets, so a bin with magnets is held down by the plate's. Screws
// pass clean through, coaxial with them.
// ============================================================================
module bp_mag_screw() {
    if (bp_enable_magnets > 0 || bp_enable_screws > 0)
        for (ix = [0 : nx - 1], iy = [0 : ny - 1])
            for (o = gf_mag_offsets())
                translate([gf_cell_x(ix, nx) + o[0],
                           gf_cell_y(iy, ny) + o[1], 0]) {
                    if (bp_enable_magnets > 0)
                        translate([0, 0, -0.01])
                            cylinder(d = GF_MAG_D, h = GF_MAG_H + 0.01);
                    if (bp_enable_screws > 0)
                        translate([0, 0, -0.01])
                            cylinder(d = GF_SCREW_D, h = plate_h + 0.02);
                }
}

// ============================================================================
// Assembly
// ============================================================================
difference() {
    gf_rrect(plate_x, plate_y, plate_h, plate_r);
    bp_sockets();
    bp_reduced_cut();
    bp_mag_screw();
}
