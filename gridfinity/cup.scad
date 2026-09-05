// Yantra4D Gridfinity Cup - BOSL2 Implementation
include <../../libs/BOSL2/std.scad>

width_units = 2;
depth_units = 1;
height_units = 3;
cup_floor_thickness = 0.7;
fn = 0;
$fa = 6; $fs = 0.4; $fn = fn > 0 ? fn : 32;

pitch = 42;
zpitch = 7;
corner_radius = 3.75;

// Gridfinity base profile. The foot tapers from foot_bottom at the print bed up
// to foot_top where it meets the body; foot_top is pitch minus the 0.5 grid
// clearance, so feet on adjacent cells leave a groove instead of meeting.
base_h = 5;
foot_bottom = 39.2;
foot_top = pitch - 0.5;
wall = 1.2;
// Solid web sealing the groove between adjacent cells. Without it the interior
// cavity spans the groove and the bin is open to the outside between cells.
web = 0.6;

// The base used to be carved out of a full-height box by subtracting one
// prismoid per cell that grew to the full 42 mm cell footprint. At the top of
// that taper the cutters covered the entire cross section, so the solid was
// pinched into two volumes meeting at a plane: OpenSCAD reported "Volumes: 2"
// and refused to call the result 2-manifold, and the same construction in
// cup.py produced non-manifold edges through OCCT as well. It also cut away the
// floor and part of the walls, which is why the old part measured far lighter
// than a Gridfinity bin of its size — it was not printable.
//
// The feet are built as positive geometry instead and unioned into the body,
// overlapping it slightly so the union dissolves the shared plane rather than
// leaving coincident faces. The interior is then removed in one pass, shelling
// the feet and the bin together, and overshoots the top so the bin is open
// rather than a sealed void.
module gridfinity_cup() {
    total_w = width_units * pitch - 0.5;
    total_d = depth_units * pitch - 0.5;
    total_h = height_units * zpitch;
    body_h = total_h - base_h;

    difference() {
        union() {
            for (x = [0:width_units-1], y = [0:depth_units-1])
                translate([(x - (width_units-1)/2) * pitch,
                           (y - (depth_units-1)/2) * pitch, 0])
                    prismoid(size1=[foot_bottom, foot_bottom],
                             size2=[foot_top, foot_top],
                             h=base_h + 0.1,
                             rounding1=corner_radius, rounding2=corner_radius,
                             anchor=BOT);

            up(base_h)
                cuboid([total_w, total_d, body_h],
                       p1=[-total_w/2, -total_d/2, 0],
                       rounding=corner_radius, edges="Z");
        }

        up(cup_floor_thickness) union() {
            for (x = [0:width_units-1], y = [0:depth_units-1])
                translate([(x - (width_units-1)/2) * pitch,
                           (y - (depth_units-1)/2) * pitch, 0])
                    prismoid(size1=[foot_bottom - 2*wall, foot_bottom - 2*wall],
                             size2=[foot_top - 2*wall, foot_top - 2*wall],
                             h=base_h + web,
                             rounding1=corner_radius, rounding2=corner_radius,
                             anchor=BOT);

            up(base_h + web - cup_floor_thickness)
                cuboid([total_w - 2*wall, total_d - 2*wall, body_h + 1],
                       p1=[-(total_w - 2*wall)/2, -(total_d - 2*wall)/2, 0],
                       rounding=corner_radius, edges="Z");
        }
    }
}

gridfinity_cup();
