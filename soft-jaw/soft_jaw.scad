include <BOSL2/std.scad>

// Yantra4D Parameters — defaults are project.json's declared defaults.
// face_pattern used to default to "prismatic" (which is not one of the
// manifest's options at all) and the jaw height was hard-coded at 1.25 in
// rather than taking the manifest's 1.735 in. Rendering this mode with no
// parameters therefore produced a 31.75 mm-tall jaw carrying a full-width
// V-rib in OpenSCAD against a plain 44.069 mm-tall blank in CadQuery.
jaw_width_inch = 6;          // project.json jaw_width, default 6.0 in
jaw_height_inch = 1.735;     // project.json jaw_height, default 1.735 in
jaw_thickness_inch = 0.75;   // project.json jaw_thickness, default 0.75 in
face_pattern = "smooth";     // project.json face_pattern, default "smooth"
serration_pitch = 2.5;       // project.json serration_pitch, default 2.5 mm
magnet_holes = true;         // project.json magnet_pockets, default true

// project.json declares face_pattern as a select over the STRINGS
// "smooth" | "serrations" | "grid". This file used to compare it against
// "prismatic" -- not one of the manifest's options -- so the *_scad presets,
// which carry the legacy integer codes 0/1/2, always fell through to a plain
// blank here while soft_jaw.py's `int(...) == 1` branch added a 5 mm additive
// V-prism. jaw_body's two kernels therefore differed by exactly 5.000 mm in Y
// at preset kurt_dx6_prismatic_scad (19.05 vs 24.05).
//
// Normalise both spellings to the manifest's options, then build the SAME
// subtractive V-groove face soft_jaw.py builds -- which is in turn main.py's
// face_cutter(), the construction the jaw / jaw_pair / vee_jaw modes already
// use. Cutting rather than adding is what keeps the jaw inside its declared
// envelope: a soft jaw bolts into the vise at a known thickness, so the grip
// pattern must never move the bounding box.
function normalise_face_pattern(v) =
    (v == "serrations" || v == 1 || v == "1") ? "serrations" :
    (v == "grid"       || v == 2 || v == "2") ? "grid" :
    "smooth";

FACE = normalise_face_pattern(face_pattern);

// CDG Constants (Kurt 6")
JAW_HEIGHT = jaw_height_inch * 25.4;
JAW_THICKNESS = jaw_thickness_inch * 25.4;
BOLT_SPACING = 3.875 * 25.4; // Varies by model, using standard spacing
BOLT_HEAD_D = 14;
BOLT_SHAFT_D = 9;

// Groove geometry — identical arithmetic to soft_jaw.py / main.py.
WIDTH = jaw_width_inch * 25.4;
PITCH = max(1.5, min(serration_pitch, JAW_HEIGHT / 4));
GROOVE_DEPTH = min(0.8, PITCH * 0.45);
HALF_W = GROOVE_DEPTH;                  // ~90 deg included V
// The vertical (grid) grooves are cut slightly SHALLOWER than the horizontal
// ones. At equal depth the two families' apex lines are coplanar and cross
// along a zero-thickness line: OpenSCAD still calls that manifold (genus 2,
// 0 boundary edges) but the tessellation carries edges shared by four faces
// and zero-area triangles at y = -T/2 + GROOVE_DEPTH, and the mesh check
// reads it as not watertight. Offsetting the crossing family by a fraction of
// the depth makes every crossing a real volume -- and is how a cross-hatch
// knurl is actually cut. soft_jaw.py applies the same factor.
GRID_DEPTH = GROOVE_DEPTH * 0.75;
HZ_MAX = 12;
VT_MAX = 10;
N_HZ = min(HZ_MAX, max(1, floor(JAW_HEIGHT / PITCH) - 1));
N_VT = min(VT_MAX, max(1, floor(WIDTH / (PITCH * 2)) - 1));

// The body is Z-centred and Y-centred so both kernels share one origin:
// x in [-W/2, W/2], y in [-T/2, T/2], z in [-H/2, H/2]. The front (gripping)
// face is at y = -T/2, the vise-side back face at y = +T/2.
module face_grooves() {
    // Horizontal V-grooves running in X, stacked up the face in Z.
    for (i = [1 : N_HZ]) {
        z = -JAW_HEIGHT / 2 + i * (JAW_HEIGHT / (N_HZ + 1));
        translate([-(WIDTH / 2 + 1), -JAW_THICKNESS / 2, z])
            rotate([0, 90, 0])
                linear_extrude(height = WIDTH + 2)
                    // local (x,y) after the rotate maps to global (z,y):
                    // mouth on the face, apex driven into the jaw (+Y)
                    polygon([[-HALF_W, 0], [HALF_W, 0], [0, GROOVE_DEPTH]]);
    }

    if (FACE == "grid") {
        // Vertical V-grooves running in Z, spaced across X.
        for (j = [1 : N_VT]) {
            x = -WIDTH / 2 + j * (WIDTH / (N_VT + 1));
            translate([x, -JAW_THICKNESS / 2, -JAW_HEIGHT / 2 - 1])
                linear_extrude(height = JAW_HEIGHT + 2)
                    polygon([[-HALF_W, 0], [HALF_W, 0], [0, GRID_DEPTH]]);
        }
    }
}

module soft_jaw() {
    difference() {
        cube([WIDTH, JAW_THICKNESS, JAW_HEIGHT], center = true);

        // Gripping face treatment.
        if (FACE != "smooth") face_grooves();

        // Mounting holes (counterbored), driven in from the back face (+Y).
        // Overshoot both ends so neither mouth is a zero-thickness opening.
        for (sx = [-1, 1]) {
            translate([sx * BOLT_SPACING / 2, JAW_THICKNESS / 2 + 0.5, 0])
                rotate([90, 0, 0])
                    cylinder(h = JAW_THICKNESS + 1, d1 = BOLT_HEAD_D,
                             d2 = BOLT_SHAFT_D, $fn = 32);
        }

        // Magnet pockets (10 mm magnets) bored into the back face.
        // h is 3.5 rather than 3 so the pocket breaks the face instead of
        // kissing it — a pocket that only touches the surface exports as an
        // enclosed void, which is how jaw_body used to render a
        // negative-volume body on every variant.
        if (magnet_holes) {
            for (sz = [-1, 1]) {
                translate([0, JAW_THICKNESS / 2 + 0.5, sz * JAW_HEIGHT / 3])
                    rotate([90, 0, 0])
                        cylinder(h = 3.5, d = 10.2, $fn = 32);
            }
        }
    }
}

soft_jaw();
