// Yantra4D Torus Knot Sculpture
// Uses BOSL2 sweep for solid geometry along a torus knot path.
//
// A torus knot is defined by integers (p, q) that describe how the
// curve winds around the torus surface.

include <../../libs/BOSL2/std.scad>
include <../../libs/BOSL2/skin.scad>

// --- Parameters (overridden by platform) ---
p = 2;
q = 3;
tube_radius = 4;
torus_radius = 30;
segments = 120;
scale_factor = 1.0;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 24;

// Torus knot parametric curve:
//   x(t) = (R + r*cos(q*t)) * cos(p*t)
//   y(t) = (R + r*cos(q*t)) * sin(p*t)
//   z(t) = r * sin(q*t)
// where R is the major radius and r is the minor radius of the torus.
_R = torus_radius * scale_factor;
_r = _R * 0.4;  // minor radius proportional to major

knot_path = [for (i = [0:segments-1])
    let(t = i * 360 / segments)
    [(_R + _r * cos(q * t)) * cos(p * t),
     (_R + _r * cos(q * t)) * sin(p * t),
     _r * sin(q * t)]
];

// Create circular cross-section profile
function circle_profile(r, n=16) =
    [for (i = [0:n-1]) [r * cos(i * 360/n), r * sin(i * 360/n)]];

// Sweep a circular profile along the knot path
module knot_body() {
    path_sweep(circle_profile(tube_radius, $fn), knot_path, closed=true);
}

// --- Render ---
if (render_mode == 0) {
    knot_body();
}
