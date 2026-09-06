// Yantra4D wrapper — Parametric Bolt (BOSL2)
include <commons-lib/scad_core.scad>

diameter = 5;
length = 20;
pitch = 0.8;
head_diameter = 0; // 0 = auto (1.7x diameter)
head_height = 0; // 0 = auto (0.7x diameter)
head_style_id = 0; // 0=hex, 1=socket, 2=button
thread_enabled = true;
render_mode = 0;
fn = 0;

$fn = fn > 0 ? fn : 32;

_head_d = head_diameter > 0 ? head_diameter : diameter * 1.7;
_head_h = head_height > 0 ? head_height : diameter * 0.7;

// Head
if (head_style_id == 0) {
  // Hex head
  translate([0, 0, length])
    cylinder(d=_head_d, h=_head_h, $fn=6);
} else if (head_style_id == 1) {
  // Socket head (cylinder with socket recess)
  translate([0, 0, length]) {
    difference() {
      cylinder(d=_head_d, h=_head_h);
      translate([0, 0, _head_h / 2])
        cylinder(d=diameter * 0.6, h=_head_h / 2 + 0.1, $fn=6);
    }
  }
} else {
  // Button head (dome).
  //
  // This said "dome" but built a bare cylinder, while bolt.py rounds the same
  // cylinder's top edge with a `fillet(_head_h * 0.6 - 0.1)` -- the two kernels
  // disagreed by 4.4 % in volume and the parity gate failed the pair on the
  // surfaces. Build the identical profile here: a cylinder of height
  // `_head_h * 0.6` whose top edge carries a fillet of radius `that - 0.1`,
  // revolved. `rotate_extrude` of the filleted half-section reproduces the
  // CadQuery solid rather than approximating it with a sphere.
  translate([0, 0, length])
    rotate_extrude($fn = fn > 0 ? fn : 64)
      _button_profile(_head_d / 2, _head_h * 0.6, _head_h * 0.6 - 0.1);
}

// Half-section of a cylinder (radius r, height h) with its TOP OUTER edge
// rounded to `fr`, as ONE closed polygon: up the wall to the fillet's tangent,
// round the fillet arc, then flat in to the axis.
//
// This was a `hull()` of the body square and a clipped fillet disc. A hull is
// the convex closure of its members, and the square reaches the axis, so the
// hull filled the whole near-axis wedge: revolving it planted 193 vertices on
// and around the rotation axis INSIDE the head (z = 30.1 .. 31.9 on the M8
// button), where `bolt.py`'s filleted solid has none at all. Those phantom
// interior points are what the parity gate measured as "the surfaces diverge
// too" -- a 3.233791mm Hausdorff proxy on a pair whose outer silhouettes
// already agreed to within a facet.
//
// Sampling the arc explicitly also makes the segment count ours rather than
// OpenSCAD's, so the revolved surface matches bolt.py's analytic fillet.
module _button_profile(r, h, fr, seg = 64) {
  fr_c = min(max(fr, 0), min(r, h));
  cx = r - fr_c;
  cz = h - fr_c;
  arc = [for (i = [0:seg]) let(t = i * 90 / seg)
           [cx + fr_c * cos(t), cz + fr_c * sin(t)]];
  polygon(concat([[0, 0], [r, 0]], arc, [[0, h]]));
}

// Shaft with or without thread
if (thread_enabled) {
  y4d_standard_thread(d=diameter, p=pitch, l=length, anchor=BOT);
} else {
  cylinder(d=diameter, h=length, anchor=BOT);
}
