/*
 * ============================================================================
 * EXTRUSION HYPEROBJECT - CURTAIN WALL FRAME
 *
 * Copyright (c) 2026 madfam-org
 * Released under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal
 * (CERN-OHL-W-2.0).
 * ============================================================================
 */

include <../../libs/BOSL2/std.scad>

// ============================================================================
// [1] INPUT PARAMETERS (Mapped to project.json)
// ============================================================================
render_mode = 0;
extrusion_length = 100; // [10:10:500]
profile_scale = 1.0; // [0.5:0.1:3.0]
wall_thickness = 2.0; // [1.0:0.5:5.0]
degradation_state = 0; // [0:1:10]

// ============================================================================
// [2] OEP8 DATA STRUCTURES (Geometry Logic)
// ============================================================================
_cfg = [
  ["length", extrusion_length],
  ["scale", profile_scale],
  ["decay", degradation_state],
  ["wall", wall_thickness],
  // Base dimensions for a complex hollow extrusion (e.g. 50x100mm mullion profile)
  ["outer_w", 50],
  ["outer_d", 100],
];

function get_prop(dict, key) = dict[search([key], dict)[0]][1];

// ============================================================================
// [3] EXTERNAL INTERFACES (The "Bounder" - Freedom of Assembly)
// ============================================================================
module ideal_frame_profile() {
  w = get_prop(_cfg, "outer_w") * get_prop(_cfg, "scale");
  d = get_prop(_cfg, "outer_d") * get_prop(_cfg, "scale");
  wall = get_prop(_cfg, "wall");
  l = get_prop(_cfg, "length");

  linear_extrude(height=l, center=true) {
    difference() {
      // Outer bounding profile
      rect([w, d], rounding=1);

      // Hollow inner core 1
      translate([0, d / 4])
        rect([w - wall * 2, d / 2 - wall * 1.5], rounding=0.5);

      // Hollow inner core 2
      translate([0, -d / 4])
        rect([w - wall * 2, d / 2 - wall * 1.5], rounding=0.5);
    }

    // Add some glass-retaining lips / screw bosses
    translate([w / 2, d / 2]) circle(r=wall);
    translate([-w / 2, d / 2]) circle(r=wall);
    translate([0, d / 2 + wall / 2]) rect([w / 3, wall]);
  }
}

// ============================================================================
// [4] INTERNAL CORE GEOMETRY (The Commons Engine - Forced Reciprocity)
// ============================================================================
// Applies the "phasing" / degradation state 
module core_hyperobject_frame() {
  decayLevel = get_prop(_cfg, "decay");
  l = get_prop(_cfg, "length");
  w = get_prop(_cfg, "outer_w") * get_prop(_cfg, "scale");
  d = get_prop(_cfg, "outer_d") * get_prop(_cfg, "scale");

  if (decayLevel == 0) {
    ideal_frame_profile();
  } else {
    // Simulating the pitting/oxidation of aluminum over time
    difference() {
      ideal_frame_profile();

      for (i = [0:decayLevel * 10]) {
        z_pos = (rands(-l / 2, l / 2, 1, i)[0]);
        // target the edges
        x_pos = (rands(0, 1, 1, i + 10)[0] > 0.5 ? w / 2 : -w / 2) + rands(-2, 2, 1, i + 15)[0];
        y_pos = rands(-d / 2, d / 2, 1, i + 20)[0];
        radius = rands(0.5, decayLevel * 0.8, 1, i + 30)[0];

        translate([x_pos, y_pos, z_pos]) {
          sphere(r=radius, $fn=12);
        }
      }
    }
  }
}

// ============================================================================
// [5] MAIN EXECUTION (Render Modes)
// ============================================================================
if (render_mode == 0) {
  color("#C0C0C0") rot(x=90) core_hyperobject_frame();
}
