/*
 * ============================================================================
 * EXTRUSION HYPEROBJECT - RAIL VECTOR
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
degradation_state = 0; // [0:1:10]

// ============================================================================
// [2] OEP8 DATA STRUCTURES (Geometry Logic)
// ============================================================================
_cfg = [
  ["length", extrusion_length],
  ["scale", profile_scale],
  ["decay", degradation_state],
  // Standard I/T Rail dimensions (approximate proportions relative to a base of 20mm width)
  ["rail_base_w", 20],
  ["rail_base_h", 3],
  ["rail_web_w", 4],
  ["rail_web_h", 12],
  ["rail_head_w", 12],
  ["rail_head_h", 6],
];

function get_prop(dict, key) = dict[search([key], dict)[0]][1];

// ============================================================================
// [3] EXTERNAL INTERFACES (The "Bounder" - Freedom of Assembly)
// ============================================================================
// A continuous, unbroken extrusion represents the ideal (non-degraded) rail segment
module ideal_rail_profile() {
  base_w = get_prop(_cfg, "rail_base_w") * profile_scale;
  base_h = get_prop(_cfg, "rail_base_h") * profile_scale;
  web_w = get_prop(_cfg, "rail_web_w") * profile_scale;
  web_h = get_prop(_cfg, "rail_web_h") * profile_scale;
  head_w = get_prop(_cfg, "rail_head_w") * profile_scale;
  head_h = get_prop(_cfg, "rail_head_h") * profile_scale;
  total_h = base_h + web_h + head_h;

  // Using a 2D path sweep for the rail cross-section
  path = [
    [-base_w / 2, 0],
    [base_w / 2, 0],
    [base_w / 2, base_h],
    [web_w / 2, base_h + 2], // Taper
    [web_w / 2, base_h + web_h - 2], // Taper
    [head_w / 2, base_h + web_h],
    [head_w / 2, total_h - 1], // Rounded top corner
    [head_w / 2 - 1, total_h],
    [-head_w / 2 + 1, total_h],
    [-head_w / 2, total_h - 1],
    [-head_w / 2, base_h + web_h],
    [-web_w / 2, base_h + web_h - 2],
    [-web_w / 2, base_h + 2],
    [-base_w / 2, base_h],
  ];

  // Extrude the 2D path
  linear_extrude(height=get_prop(_cfg, "length"), center=true) {
    polygon(path);
  }
}

// ============================================================================
// [4] INTERNAL CORE GEOMETRY (The Commons Engine - Forced Reciprocity)
// ============================================================================
// Applies the "phasing" / degradation state 
module core_hyperobject_rail() {
  decayLevel = get_prop(_cfg, "decay");
  l = get_prop(_cfg, "length");

  if (decayLevel == 0) {
    ideal_rail_profile();
  } else {
    // Aesthetic Causality: The object degrades and asserts its alien presence
    // We simulate this by taking "bites" out of the geometry using randomized spheres
    difference() {
      ideal_rail_profile();

      // Generate degradation geometry
      // pseudo-random generation based on decay level
      for (i = [0:decayLevel * 5]) {
        // Random position along the rail
        z_pos = (rands(-l / 2, l / 2, 1, i)[0]);
        x_pos = rands(-15, 15, 1, i + 10)[0] * profile_scale;
        y_pos = rands(0, 25, 1, i + 20)[0] * profile_scale;
        radius = rands(1, decayLevel * 1.5, 1, i + 30)[0];

        translate([x_pos, y_pos, z_pos]) {
          sphere(r=radius, $fn=16);
        }
      }
    }
  }
}

// ============================================================================
// [5] MAIN EXECUTION (Render Modes)
// ============================================================================
if (render_mode == 0) {
  color("#757575") rot(x=90) core_hyperobject_rail();
}
