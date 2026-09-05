// ============================================================================
// lid.scad — Gridfinity bin lid, OpenSCAD engine, mode `lid`.
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
// WHAT THIS LID DOES THAT THE BASELINE'S DID NOT
//   The baseline lid was a featureless flat plate: no recess, no rim, no
//   magnets, and its four declared parameters changed nothing. It could not
//   retain on a bin. This one has a real fit recess.
//
//   The lid's footprint is 42*n - 1.0 mm, i.e. 0.25 mm inset per side relative
//   to the bin it covers (42*n - 0.5). That inset is the ONLY fit dimension the
//   standard and the measured baseline together supply, so it is what the fit
//   is built from: the lid drops INSIDE the bin's stacking-lip recess, and a
//   step machined into the lid's underside registers against the lip's inner
//   face. Plate thickness stays 2.0 mm and the footprint rule is unchanged, so
//   the envelope is identical to the baseline's at every variant; the recess is
//   cut into that envelope, never added outside it.
// ============================================================================

include <gridfinity_std.scad>

// -- Manifest parameters (injected with -D by the platform) ------------------
width_units         = 2;     // grid units in X            [1 .. 6]
depth_units         = 1;     // grid units in Y            [1 .. 6]
lid_include_magnets = 1;     // 6 x 2 mm magnet cavities in the underside
lid_efficient_floor = 0.7;   // membrane left under the relief  [0.4 .. 2]
lid_type_id         = 0;     // 0 default, 1 flat, 2 halfpitch, 3 efficient
fn                  = 0;     // 0 = auto (32)

$fn = gf_fn(fn);

// -- Derived ------------------------------------------------------------------
nx = max(1, min(6, round(width_units)));
ny = max(1, min(6, round(depth_units)));

// Footprint rule 42*n - 1.0: 0.25 mm inset per side vs the bin's 42*n - 0.5.
lid_x = nx * GF_PITCH - GF_LID_CLEAR;
lid_y = ny * GF_PITCH - GF_LID_CLEAR;
lid_h = 2.0;                 // plate thickness, the baseline envelope

floor_th = max(0.4, min(2.0, lid_efficient_floor));

// -- Lid types ----------------------------------------------------------------
//   0 default    a registration step around the underside: the lid seats
//                inside the bin's stacking-lip recess and cannot slide off.
//   1 flat       no step — the plain plate, for a bin whose lip is disabled
//                (lip_style_id = 3) or for use as a divider shim.
//   2 halfpitch  the step, plus a half-pitch alignment ridge across the middle
//                of the underside, which drops between two bins pushed
//                together so one lid spans both.
//   3 efficient  the step, plus a relief pocket per cell in the TOP face that
//                leaves `lid_efficient_floor` of membrane — a lighter lid.
has_step  = lid_type_id != 1;
has_ridge = lid_type_id == 2;
has_relief = lid_type_id == 3;

// The registration step. Its outer face sits at the lid footprint; it is
// recessed `step_in` from the edge and `step_h` deep into the underside, so
// what remains standing is a spigot that enters the bin's lip recess.
step_in = 1.6;
step_h  = min(0.9, lid_h - 0.6);

// ============================================================================
// Registration step — cut a rebate around the underside perimeter
// ============================================================================
module lid_step() {
    if (has_step && step_h > 0.1)
        difference() {
            translate([0, 0, -0.01])
                gf_rrect(lid_x + 0.02, lid_y + 0.02, step_h + 0.01, GF_R);
            gf_rrect(lid_x - 2 * step_in, lid_y - 2 * step_in,
                     step_h + 0.4, max(0.01, GF_R - step_in));
        }
}

// ============================================================================
// Half-pitch alignment ridge — a rib across the underside on the cell boundary
// ============================================================================
module lid_ridge() {
    if (has_ridge) {
        rw = 2.0;                       // rib width
        rh = min(0.8, lid_h - 0.8);     // rib depth into the underside
        if (rh > 0.1) {
            // ribs on every internal cell boundary in X
            if (nx > 1)
                for (i = [1 : nx - 1])
                    translate([-lid_x / 2 + i * lid_x / nx, 0, -0.01])
                        cube([rw, lid_y + 0.02, rh + 0.01], center = true);
            if (ny > 1)
                for (j = [1 : ny - 1])
                    translate([0, -lid_y / 2 + j * lid_y / ny, -0.01])
                        cube([lid_x + 0.02, rw, rh + 0.01], center = true);
            // a single centre rib when the lid is one cell either way, so the
            // parameter is never silently inert
            if (nx == 1 && ny == 1)
                translate([0, 0, -0.01])
                    cube([lid_x + 0.02, rw, rh + 0.01], center = true);
        }
    }
}

// ============================================================================
// Efficient relief — pocket the TOP face per cell, leaving a membrane
// ============================================================================
module lid_relief() {
    if (has_relief) {
        depth = lid_h - floor_th;
        if (depth > 0.15)
            for (ix = [0 : nx - 1], iy = [0 : ny - 1])
                translate([gf_cell_x(ix, nx), gf_cell_y(iy, ny),
                           lid_h - depth])
                    gf_rrect(GF_CELL - 6, GF_CELL - 6, depth + 0.01, GF_R);
    }
}

// ============================================================================
// Magnet cavities — in the underside, on the standard 26 mm square, so the lid
// is held to a bin whose own feet carry magnets.
//
// Their depth is capped so a 2 mm plate is never perforated: a 6 x 2 mm magnet
// needs 2 mm, which is the whole plate, so the pocket is limited to leave at
// least 0.4 mm of material and the lid still holds on the magnet's face.
// ============================================================================
module lid_magnets() {
    if (lid_include_magnets > 0) {
        d = min(GF_MAG_H, lid_h - 0.4);
        if (d > 0.15)
            for (ix = [0 : nx - 1], iy = [0 : ny - 1])
                for (o = gf_mag_offsets())
                    translate([gf_cell_x(ix, nx) + o[0],
                               gf_cell_y(iy, ny) + o[1], -0.01])
                        cylinder(d = GF_MAG_D, h = d + 0.01);
    }
}

// ============================================================================
// Assembly
// ============================================================================
difference() {
    gf_rrect(lid_x, lid_y, lid_h, GF_R);
    lid_step();
    lid_ridge();
    lid_relief();
    lid_magnets();
}
