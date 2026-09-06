// Yantra4D Gear Reducer — Housing Only
// Renders just the housing parts for print plate layout

include <BOSL2/std.scad>
include <BOSL2/gears.scad>

input_teeth = 12;
output_teeth = 36;
module_size = 1.5;
gear_thickness = 8;
shaft_diameter = 5;
bore_diameter = 5;
wall_thickness = 3;
pressure_angle = 20;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 48;
input_pd = pitch_radius(mod=module_size, teeth=input_teeth) * 2;
output_pd = pitch_radius(mod=module_size, teeth=output_teeth) * 2;
center_distance = (input_pd + output_pd) / 2;
clearance = 0.4;
bearing_od = 22;
bearing_h = 7;

housing_width = output_pd + wall_thickness * 2 + 10;
housing_depth = center_distance + output_pd / 2 + wall_thickness * 2 + 10;
housing_height = gear_thickness + bearing_h * 2 + wall_thickness * 2;

// Guide posts on the BOTTOM half / matching sockets in the TOP half.
// Assembly step 5 is "Align guide posts and press down": the two halves are
// NOT the same part mirrored — the bottom carries the posts, the top carries
// the blind sockets they press into. Rendering both from one un-branched
// mirror() made the two declared parts identical solids (same volume), which
// is what the render sweep flagged: a user printing "housing_top" got a second
// bottom, and the reducer never closed.
post_d = min(4, wall_thickness + 1);
post_h = min(4, gear_thickness / 2);
post_fit = 0.25;                 // press-fit clearance, socket over post

// The four post/socket stations. A post must stand on material that survives
// BOTH the gear cavity and the bolt holes at every preset, so the station is
// derived, not hardcoded: sit it just inside the shell wall at each corner and
// keep it clear of the two cavity circles. The cavity is offset toward +X
// (the output gear sits at x = center_distance), so the +X corners need the
// larger inset — computing it from the cavity radii is what keeps the posts
// attached across nema17_3to1 .. heavy_duty rather than only at defaults.
cav_r_in  = input_pd  / 2 + module_size * 2 + clearance;
cav_r_out = output_pd / 2 + module_size * 2 + clearance;
post_gap  = 1.5;                 // material left between post and cavity wall

// x stations: hard against the left/right walls, past the bolt column.
gs_x0 = -housing_width / 2 + post_d / 2 + 1.5;
gs_x1 =  housing_width / 2 - post_d / 2 - 1.5;
// y stations: hard against the front/back walls of the shell footprint.
gs_y0 = -output_pd / 2 - wall_thickness + post_d / 2 + 1.5;
gs_y1 = -output_pd / 2 - wall_thickness + housing_depth - post_d / 2 - 1.5;

// A station is usable only when the post footprint clears both cavity circles
// and both bolt columns. Push an offending station along +Y (the free direction:
// the cavity is centred on y = 0 and the shell is deepest in Y) until it clears.
function _cav_clear(x, y) =
    min(norm([x, y]) - cav_r_in, norm([x - center_distance, y]) - cav_r_out)
    - post_d / 2 - post_gap;

function _bolt_clear(x, y) =
    min([for (bx = [-housing_width/2 + 5, housing_width/2 - 5])
          for (by = [-output_pd/2 - wall_thickness + 5,
                     -output_pd/2 - wall_thickness + housing_depth - 5])
            norm([x - bx, y - by])]) - post_d / 2 - 1.6 - 0.8;

// Slide a station along Y in 1 mm steps (bounded) until both clearances pass.
function _slide(x, y, dir, i) =
    i > 60 ? undef
  : (_cav_clear(x, y + dir * i) >= 0 && _bolt_clear(x, y + dir * i) >= 0
     && y + dir * i >= gs_y0 && y + dir * i <= gs_y1)
      ? [x, y + dir * i]
      : _slide(x, y, dir, i + 1);

function _station(x, y) =
    (_cav_clear(x, y) >= 0 && _bolt_clear(x, y) >= 0) ? [x, y]
  : (_slide(x, y, 1, 1) != undef) ? _slide(x, y, 1, 1)
  : _slide(x, y, -1, 1);

function guide_stations() = [
    for (s = [_station(gs_x0, gs_y0), _station(gs_x0, gs_y1),
              _station(gs_x1, gs_y0), _station(gs_x1, gs_y1)])
        if (s != undef) s
];

module housing_shell() {
    half_h = housing_height / 2;
    difference() {
        // Outer shell
        translate([-housing_width/2, -output_pd/2 - wall_thickness, 0])
            cube([housing_width, housing_depth, half_h]);

        // Input shaft bore
        translate([0, 0, -1])
            cylinder(d=bearing_od + clearance, h=bearing_h + 1, $fn=$fn);

        // Output shaft bore
        translate([center_distance, 0, -1])
            cylinder(d=bearing_od + clearance, h=bearing_h + 1, $fn=$fn);

        // Gear cavity
        translate([0, 0, bearing_h])
            hull() {
                cylinder(d=input_pd + module_size * 4 + clearance * 2, h=half_h, $fn=$fn);
                translate([center_distance, 0, 0])
                    cylinder(d=output_pd + module_size * 4 + clearance * 2, h=half_h, $fn=$fn);
            }

        // Bolt holes (4 corners)
        for (x = [-housing_width/2 + 5, housing_width/2 - 5])
            for (y = [-output_pd/2 - wall_thickness + 5, -output_pd/2 - wall_thickness + housing_depth - 5])
                translate([x, y, -1])
                    cylinder(d=3.2, h=half_h + 2, $fn=24);
    }
}

// top=false -> bottom half: shell PLUS four guide posts standing on the split face.
// top=true  -> top half:    shell MINUS four sockets sunk into the split face.
// The posts stand proud of the split plane and the sockets are blind pockets that
// vent through it, so each half is one watertight positive solid and the two have
// visibly different volumes.
module housing_half(top=false) {
    half_h = housing_height / 2;
    if (top) {
        difference() {
            housing_shell();
            for (s = guide_stations())
                translate([s[0], s[1], half_h - post_h])
                    cylinder(d=post_d + post_fit * 2, h=post_h + 0.1, $fn=32);
        }
    } else {
        union() {
            housing_shell();
            for (s = guide_stations())
                translate([s[0], s[1], half_h - 0.01])
                    cylinder(d1=post_d, d2=post_d * 0.85, h=post_h + 0.01, $fn=32);
        }
    }
}

if (render_mode == 0) {
    // Housing bottom — guide posts on the split face
    housing_half(top=false);
} else if (render_mode == 1) {
    // Housing top — matching sockets; its own solid, not a mirror of the bottom
    housing_half(top=true);
}
