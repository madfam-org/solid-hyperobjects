// ============================================================================
// cup.scad — Gridfinity storage bin, OpenSCAD engine, mode `cup`.
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
//   Standard implemented: 42 mm grid module, 7 mm height unit, the
//   0.8 / 1.8 / 2.15 mm base-profile chamfer stack, 0.5 mm bin clearance per
//   pitch, 3.75 mm corner radius, the stacking lip as the inverse of the base
//   profile, 6 x 2 mm magnet sockets on 26 mm centres, M3 screw clearance.
//
// EVERY DECLARED PARAMETER IS LIVE. The manifest advertises dividers, a lip
// style, a label shelf, a finger ramp, a sliding-lid rail, a wall pattern, a
// tapered corner, an efficient floor, magnets and screws; all of them cut or
// add real geometry here.
// ============================================================================

include <gridfinity_std.scad>

// -- Manifest parameters (injected with -D by the platform) ------------------
width_units          = 2;    // grid units in X            [1 .. 6]
depth_units          = 1;    // grid units in Y            [1 .. 6]
height_units         = 3;    // height units of 7 mm       [1 .. 10]
cup_wall_thickness   = 0;    // side wall, 0 = auto by height  [0 .. 3]
cup_floor_thickness  = 0.7;  // solid floor above the bed  [0.4 .. 2]
vertical_chambers    = 1;    // compartments along Y       [1 .. 6]
horizontal_chambers  = 1;    // compartments along X       [1 .. 6]
lip_style_id         = 0;    // 0 normal, 1 reduced, 2 minimum, 3 none
headroom             = 0.8;  // top undersizing for stacking  [0 .. 2]
efficient_floor_id   = 0;    // 0 off, 1 on, 2 rounded, 3 smooth
fingerslide_enabled  = 0;    // front access ramp
label_enabled        = 0;    // rear label shelf
sliding_lid_enabled  = 0;    // rail groove for a sliding lid
wallpattern_enabled  = 0;    // decorative wall relief
wallpattern_style_id = 0;    // 0 hexgrid, 1 grid, 2 voronoi, 3 brick
tapered_corner_id    = 0;    // 0 none, 1 rounded, 2 chamfered
tapered_corner_size  = 10;   // corner taper radius / size  [5 .. 20]
enable_screws        = 0;    // M3 screw holes through the feet
enable_magnets       = 0;    // 6 x 2 mm magnet sockets in the feet
fn                   = 0;    // 0 = auto (32)

$fn = gf_fn(fn);

// -- Derived ------------------------------------------------------------------
nx = max(1, min(6, round(width_units)));
ny = max(1, min(6, round(depth_units)));
nz = max(1, min(10, round(height_units)));

body_x = gf_body_x(nx);          // 42*nx - 0.5
body_y = gf_body_y(ny);          // 42*ny - 0.5
total_h = nz * GF_ZUNIT;         // exactly 7 * nz — the envelope gate

// Wall thickness: 0 means "auto by height", which scales from 0.95 mm on a
// one-unit bin to 1.6 mm on a ten-unit one, clamped to the manifest range.
auto_wall = min(1.6, 0.95 + 0.075 * (nz - 1));
wall = cup_wall_thickness > 0
     ? max(0.8, min(3.0, cup_wall_thickness))
     : auto_wall;

floor_th = max(0.4, min(2.0, cup_floor_thickness));

// The cavity floor sits `floor_th` above the top of the foot. The baseline put
// it at a fixed 5.6 mm; here it tracks the parameter honestly, which is what
// "Floor Thickness" means, and at the 0.7 mm default it lands at 5.7 mm.
cavity_z = GF_FOOT_H + floor_th;

// Lip geometry. The rim carries a RECESS whose surface is the base profile, so
// the foot of the bin above lands in it and self-centres: the two tapers meet,
// the upper bin's outer wall stays flush with this one's, and the stack does
// not rock. The style sets how much of the profile the recess keeps, measured
// down from the rim:
//   0 normal   the full 4.75 mm profile — the deepest, most positive location
//   1 reduced  2.95 mm — the upper chamfer plus the straight section
//   2 minimum  2.15 mm — the upper chamfer only, a shallow catch
//   3 none     no recess; the rim is a plain wall and bins do not stack
lip_h = lip_style_id == 0 ? GF_PROFILE_H
      : lip_style_id == 1 ? GF_C2 + GF_WALL
      : lip_style_id == 2 ? GF_C2
      : 0;

// Headroom undersizes the recess so the foot above drops in without binding.
head = max(0, min(2.0, headroom));

// The recess is inset from the cell by a full wall thickness so the rim is a
// printable upstand, and by half the headroom again so the foot above clears
// it. `lip_shrink` is that inset per side, fed to gf_foot_profile as a
// negative growth.
lip_shrink = wall + head / 2;
has_lip = lip_style_id < 3
        && total_h > GF_FOOT_H + lip_h + 0.5
        && min(body_x, body_y) - 2 * lip_shrink > 2 * (GF_C1 + GF_C2) + 4;

// Chambers
ncx = max(1, min(6, round(horizontal_chambers)));   // divisions along X
ncy = max(1, min(6, round(vertical_chambers)));     // divisions along Y
div_t = max(0.8, wall);                             // divider thickness

inner_x = body_x - 2 * wall;
inner_y = body_y - 2 * wall;
inner_r = max(0.01, GF_R - wall);

taper_sz = max(5, min(20, tapered_corner_size));

// ============================================================================
// Footprint-wide base profile
//
// The stacking lip runs around the WHOLE bin, not around each cell: the feet of
// the bin above are per-cell, but they all drop inside one perimeter recess.
// This is the base profile's chamfer stack swept around the bin footprint
// rather than a cell, so the recess taper matches a foot's taper exactly.
// `grow` widens every section on each side; pass a negative value to inset.
// ============================================================================
module gf_footprint_profile(x, y, grow = 0, with_riser = true) {
    w_top_x = x + 2 * grow;      w_top_y = y + 2 * grow;
    w_mid_x = w_top_x - 2 * GF_C2;   w_mid_y = w_top_y - 2 * GF_C2;
    w_bot_x = w_mid_x - 2 * GF_C1;   w_bot_y = w_mid_y - 2 * GF_C1;

    r_top = max(0.01, GF_R + grow);
    r_mid = max(0.01, r_top - GF_C2);
    r_bot = max(0.01, r_mid - GF_C1);

    hull() {
        gf_rrect(w_bot_x, w_bot_y, 0.001, r_bot);
        translate([0, 0, GF_C1]) gf_rrect(w_mid_x, w_mid_y, 0.001, r_mid);
    }
    translate([0, 0, GF_C1]) gf_rrect(w_mid_x, w_mid_y, GF_WALL, r_mid);
    translate([0, 0, GF_C1 + GF_WALL]) hull() {
        gf_rrect(w_mid_x, w_mid_y, 0.001, r_mid);
        translate([0, 0, GF_C2]) gf_rrect(w_top_x, w_top_y, 0.001, r_top);
    }
    if (with_riser)
        translate([0, 0, GF_PROFILE_H]) gf_rrect(w_top_x, w_top_y, GF_RISER, r_top);
}

// ============================================================================
// Feet — the mating geometry, one per cell
// ============================================================================
module cup_feet() {
    for (ix = [0 : nx - 1], iy = [0 : ny - 1])
        translate([gf_cell_x(ix, nx), gf_cell_y(iy, ny), 0])
            gf_foot_profile();
}

// ============================================================================
// Body — the full-footprint prism above the feet
// ============================================================================
module cup_body() {
    translate([0, 0, GF_FOOT_H])
        gf_rrect(body_x, body_y, max(0.01, total_h - GF_FOOT_H), GF_R);
}

// ============================================================================
// The solid blank — feet plus body, before anything is cut out
//
// Note where the stacking lip is NOT: it is formed SUBTRACTIVELY, by cup_cavity
// below. The blank is solid to its full height and the cavity cut leaves the
// base profile standing at the rim. Building the lip additively instead would
// push the bin past 7*nz and break the envelope.
// ============================================================================
module cup_blank() {
    union() {
        cup_feet();
        cup_body();
    }
}

// ============================================================================
// Cavity — the interior, cut from the rim down to the floor
//
// Without a lip the cavity is a plain inset prism.
//
// With a lip, the top `lip_h` of the interior is the NEGATIVE of the base
// profile swept around the whole footprint: the recess the feet of the bin
// above drop into. Placing the profile so its widest section lands at the rim
// gives a recess that is widest at the top and narrows going down — the inverse
// of a foot — so a stacked bin seats and self-centres. Below that recess the
// cavity is a plain inset prism, and the two are unioned into ONE cutting tool
// so the interior stays a single void.
// ============================================================================
module cup_cavity() {
    cav_h = total_h - cavity_z;
    if (cav_h > 0.05) {
        if (has_lip) {
            union() {
                // the lip recess: the top `lip_h` of the base profile
                // swept around the footprint, widest section at the rim
                intersection() {
                    translate([0, 0, total_h - GF_PROFILE_H])
                        gf_footprint_profile(body_x, body_y,
                                             grow = -lip_shrink,
                                             with_riser = false);
                    translate([0, 0, total_h - lip_h])
                        gf_rrect(body_x + 2, body_y + 2, lip_h + 0.02, 0.01);
                }
                // the main cavity, from the floor up to the recess. It reaches
                // 0.01 mm into the recess so the two make one void.
                translate([0, 0, cavity_z])
                    gf_rrect(inner_x, inner_y,
                             max(0.01, cav_h - lip_h + 0.01), inner_r);
            }
        } else {
            translate([0, 0, cavity_z])
                gf_rrect(inner_x, inner_y, cav_h + 0.01, inner_r);
        }
    }
}

// ============================================================================
// Efficient floor — material saving under the cavity
//   0 off      flat floor at cavity_z
//   1 on       a chamfered relief per cell, 45 deg
//   2 rounded  a filleted relief per cell
//   3 smooth   a shallow dished relief per cell
// The relief never breaches the 0.4 mm minimum wall above the foot.
// ============================================================================
module cup_efficient_floor() {
    if (efficient_floor_id > 0 && total_h > cavity_z + 1.0) {
        depth = min(cavity_z - GF_PROFILE_H - 0.4,
                    efficient_floor_id == 3 ? 1.6 : 2.4);
        if (depth > 0.2)
            for (ix = [0 : nx - 1], iy = [0 : ny - 1])
                translate([gf_cell_x(ix, nx), gf_cell_y(iy, ny), cavity_z - depth])
                    if (efficient_floor_id == 1)
                        // chamfered pyramid frustum
                        hull() {
                            gf_rrect(GF_CELL - 2 * wall - 2 * depth,
                                     GF_CELL - 2 * wall - 2 * depth, 0.001, 1);
                            translate([0, 0, depth])
                                gf_rrect(GF_CELL - 2 * wall,
                                         GF_CELL - 2 * wall, 0.001, GF_R - wall);
                        }
                    else if (efficient_floor_id == 2)
                        // rounded: a sphere-capped relief
                        intersection() {
                            gf_rrect(GF_CELL - 2 * wall, GF_CELL - 2 * wall,
                                     depth, GF_R - wall);
                            translate([0, 0, depth])
                                scale([1, 1, depth / ((GF_CELL - 2 * wall) / 2)])
                                    sphere(r = (GF_CELL - 2 * wall) / 2);
                        }
                    else
                        // smooth: a shallow dish
                        intersection() {
                            gf_rrect(GF_CELL - 2 * wall, GF_CELL - 2 * wall,
                                     depth, GF_R - wall);
                            translate([0, 0, depth])
                                scale([1, 1, depth / ((GF_CELL - 2 * wall) / 1.4)])
                                    sphere(r = (GF_CELL - 2 * wall) / 1.4);
                        }
    }
}

// ============================================================================
// Dividers — real internal walls splitting the cavity into compartments.
// A divider slab is centred on its plane and spans from the cavity floor to
// the underside of the lip (or the rim, when there is no lip).
// ============================================================================
module cup_divider_walls() {
    top_z = has_lip ? total_h - lip_h : total_h;
    h = top_z - cavity_z;
    if (h > 0.2) {
        if (ncx > 1)
            for (i = [1 : ncx - 1])
                translate([-inner_x / 2 + i * inner_x / ncx, 0, cavity_z + h / 2])
                    cube([div_t, inner_y, h], center = true);
        if (ncy > 1)
            for (j = [1 : ncy - 1])
                translate([0, -inner_y / 2 + j * inner_y / ncy, cavity_z + h / 2])
                    cube([inner_x, div_t, h], center = true);
    }
}

// ============================================================================
// Label shelf — an overhanging ledge along the rear (+Y) interior wall, the
// surface a printed or written label sits on.
// ============================================================================
module cup_label_shelf() {
    top_z = has_lip ? total_h - lip_h : total_h;
    depth = min(12, inner_y / 3);
    th = min(1.2, max(0.6, wall));
    if (top_z - cavity_z > th + 1.0 && depth > 2)
        translate([0, inner_y / 2 - depth / 2, top_z - th / 2])
            cube([inner_x, depth, th], center = true);
}

// ============================================================================
// Finger slide — a concave ramp filling the interior's front-bottom corner, so
// contents can be swept up the front wall and out. It is MATERIAL ADDED inside
// the cavity: a prism running the interior width, its cross-section the corner
// left over when a cylinder of radius r is removed from an r x r square.
// Clipped to the interior so it can never touch the envelope.
// ============================================================================
module cup_fingerslide() {
    top_z = has_lip ? total_h - lip_h : total_h;
    r = min(min(14, inner_y / 2.2), top_z - cavity_z - 0.6);
    if (r > 1.5)
        intersection() {
            // the interior volume, so the ramp cannot escape the cavity
            translate([0, 0, cavity_z])
                gf_rrect(inner_x, inner_y, top_z - cavity_z, inner_r);
            // the ramp: extrude the corner cross-section along X
            translate([0, -inner_y / 2, cavity_z])
                rotate([0, 90, 0])
                    linear_extrude(height = inner_x + 2, center = true)
                        difference() {
                            // local x is -Z(world), local y is +Y(world)
                            // 0.2 mm of overlap into the floor and the front
                            // wall, so the ramp meets them through material
                            // rather than on a tangent line
                            polygon([[0.2, -0.2], [-r, -0.2],
                                     [-r, r], [0.2, r]]);
                            translate([-r, r]) circle(r = r);
                        }
        }
}

// ============================================================================
// Sliding-lid rail — a pair of grooves in the interior side walls just under
// the rim, into which a flat lid slides.
// ============================================================================
module cup_sliding_lid_rail() {
    top_z = has_lip ? total_h - lip_h : total_h;
    gw = 1.6;   // groove width (Z)
    gd = 1.2;   // groove depth (into the wall)
    z = top_z - 1.0 - gw / 2;
    if (z > cavity_z + 1.0)
        for (s = [-1, 1])
            translate([0, s * (inner_y / 2 + gd / 2 - 0.001), z])
                cube([inner_x + 0.2, gd + 0.01, gw], center = true);
}

// ============================================================================
// Wall pattern — a decorative relief milled into the four side walls. The
// relief is cut only partway through, never breaching the wall: it removes
// `wall - 0.4` mm, leaving a 0.4 mm membrane.
//   0 hexgrid  1 grid  2 voronoi (a jittered hex, deterministic)  3 brick
// ============================================================================
module cup_wallpattern_cell(style, s) {
    if (style == 0 || style == 2)
        circle(r = s * 0.52, $fn = 6);
    else if (style == 1)
        square([s * 0.78, s * 0.78], center = true);
    else
        square([s * 1.35, s * 0.55], center = true);
}

module cup_wallpattern_field(len, hgt, style) {
    s = style == 3 ? 7 : 6;
    dx = style == 3 ? s * 1.55 : s * 1.06;
    dy = style == 3 ? s * 0.75 : s * 0.92;
    ncols = max(1, floor(len / dx) + 1);
    nrows = max(1, floor(hgt / dy) + 1);
    for (r = [0 : nrows - 1], c = [0 : ncols - 1]) {
        // hex/brick rows are offset by half a step; "voronoi" adds a
        // deterministic jitter so no two cells are alike.
        off = (style == 1) ? 0 : ((r % 2) * dx / 2);
        jx = style == 2 ? (((r * 7 + c * 13) % 11) - 5) * 0.16 : 0;
        jy = style == 2 ? (((r * 5 + c * 17) % 11) - 5) * 0.16 : 0;
        translate([-len / 2 + c * dx + off + jx, -hgt / 2 + r * dy + jy])
            cup_wallpattern_cell(style, s);
    }
}

module cup_wallpattern() {
    depth = max(0.0, wall - 0.4);
    top_z = has_lip ? total_h - lip_h : total_h;
    // The relief occupies the wall between the floor and the rim, keeping a
    // 1.5 mm solid margin at each end so the pattern never undercuts the floor
    // or weakens the lip.
    band_lo = cavity_z + 1.5;
    band_hi = top_z - 1.5;
    hgt = band_hi - band_lo;
    style = max(0, min(3, round(wallpattern_style_id)));
    if (depth > 0.15 && hgt > 3) {
        // long walls (normal to Y)
        for (s = [-1, 1])
            translate([0, s * (body_y / 2 - depth / 2 + 0.001), (band_lo + band_hi) / 2])
                rotate([90, 0, 0])
                    linear_extrude(height = depth + 0.01, center = true)
                        intersection() {
                            cup_wallpattern_field(body_x - 2 * GF_R - 4, hgt, style);
                            square([body_x - 2 * GF_R - 4, hgt], center = true);
                        }
        // short walls (normal to X)
        for (s = [-1, 1])
            translate([s * (body_x / 2 - depth / 2 + 0.001), 0, (band_lo + band_hi) / 2])
                rotate([90, 0, 90])
                    linear_extrude(height = depth + 0.01, center = true)
                        intersection() {
                            cup_wallpattern_field(body_y - 2 * GF_R - 4, hgt, style);
                            square([body_y - 2 * GF_R - 4, hgt], center = true);
                        }
    }
}

// ============================================================================
// Tapered corner — the front-left vertical corner of the body is relieved so a
// hand can reach in past it. 1 = rounded, 2 = chamfered.
// ============================================================================
module cup_tapered_corner() {
    if (tapered_corner_id > 0) {
        t = min(taper_sz, min(body_x, body_y) / 2 - 1);
        if (t > 1)
            translate([-body_x / 2, -body_y / 2, GF_FOOT_H - 0.01])
                linear_extrude(height = total_h - GF_FOOT_H + 0.02)
                    difference() {
                        square([t, t], center = false);
                        if (tapered_corner_id == 1)
                            translate([t, t]) circle(r = t);
                        else
                            polygon([[t, 0], [0, t], [t, t]]);
                    }
    }
}

// ============================================================================
// Magnet sockets and screw holes — in the underside of every foot, 6 x 2 mm on
// a 26 mm square, M3 clearance coaxial with them.
// ============================================================================
module cup_mag_screw() {
    if (enable_magnets > 0 || enable_screws > 0)
        for (ix = [0 : nx - 1], iy = [0 : ny - 1])
            for (o = gf_mag_offsets())
                translate([gf_cell_x(ix, nx) + o[0], gf_cell_y(iy, ny) + o[1], 0]) {
                    if (enable_magnets > 0)
                        translate([0, 0, -0.01])
                            cylinder(d = GF_MAG_D, h = GF_MAG_H + 0.01);
                    if (enable_screws > 0)
                        translate([0, 0, -0.01])
                            cylinder(d = GF_SCREW_D, h = cavity_z + 0.02);
                }
}

// ============================================================================
// Assembly
// ============================================================================
difference() {
    union() {
        difference() {
            cup_blank();
            cup_cavity();
            cup_efficient_floor();
        }
        if (ncx > 1 || ncy > 1) cup_divider_walls();
        if (label_enabled > 0) cup_label_shelf();
        if (fingerslide_enabled > 0) cup_fingerslide();
    }
    if (sliding_lid_enabled > 0) cup_sliding_lid_rail();
    if (wallpattern_enabled > 0) cup_wallpattern();
    if (tapered_corner_id > 0) cup_tapered_corner();
    cup_mag_screw();
}
