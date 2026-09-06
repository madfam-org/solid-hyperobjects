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
// rounded to `fr`: the wall runs up to the fillet's tangent, the fillet arc
// turns the corner, and the flat top closes it on the axis.
module _button_profile(r, h, fr) {
  fr_c = min(max(fr, 0), min(r, h));
  hull() {
    // Body below the fillet's tangent line.
    square([r, h - fr_c]);
    // Fillet: a disc of radius fr_c centred at the arc's centre, clipped to the
    // profile's quadrant by the hull with the body below it.
    translate([r - fr_c, h - fr_c])
      intersection() {
        circle(r = fr_c, $fn = 64);
        translate([-fr_c, 0]) square([fr_c * 2, fr_c]);
      }
  }
}

// Shaft with or without thread
if (thread_enabled) {
  y4d_standard_thread(d=diameter, p=pitch, l=length, anchor=BOT);
} else {
  cylinder(d=diameter, h=length, anchor=BOT);
}
