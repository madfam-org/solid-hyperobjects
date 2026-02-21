/*
 * ============================================================================
 * EXTRUSION HYPEROBJECT - MODULAR POLYMER TRACK
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
  // Base dimensions for a 38mm modular display system extrusion
  ["diameter", 38],
  ["slot_width", 5],
  ["slot_depth", 8],
];

function get_prop(dict, key) = dict[search([key], dict)[0]][1];

// ============================================================================
// [3] EXTERNAL INTERFACES (The "Bounder" - Freedom of Assembly)
// ============================================================================
module ideal_track_profile() {
  d = get_prop(_cfg, "diameter") * get_prop(_cfg, "scale");
  wall = get_prop(_cfg, "wall");
  l = get_prop(_cfg, "length");
  sw = get_prop(_cfg, "slot_width") * get_prop(_cfg, "scale");
  sd = get_prop(_cfg, "slot_depth") * get_prop(_cfg, "scale");

  linear_extrude(height=l, center=true) {
    difference() {
      // Main cylindrical body
      circle(d=d);

      // Hollow core
      circle(d=d - wall * 2);

      // Mounting Slot 1 (North)
      translate([-sw / 2, d / 2 - sd]) rect([sw, sd + 1]);

      // Mounting Slot 2 (South)
      translate([-sw / 2, -d / 2 - 1]) rect([sw, sd + 1]);

      // Mounting Slot 3 (East)
      translate([d / 2 - sd, -sw / 2]) rect([sd + 1, sw]);

      // Mounting Slot 4 (West)
      translate([-d / 2 - 1, -sw / 2]) rect([sd + 1, sw]);
    }

    // Inner reinforcement tube
    difference() {
      circle(d=d / 2);
      circle(d=d / 2 - wall);
    }

    // Spokes connecting inner and outer tubes
    translate([-wall / 2, 0]) rect([wall, d / 2 - sd]);
    translate([0, -wall / 2]) rect([d / 2 - sd, wall]);
    translate([-wall / 2, -(d / 2 - sd)]) rect([wall, d / 2 - sd]);
    translate([-(d / 2 - sd), -wall / 2]) rect([d / 2 - sd, wall]);
  }
}

// ============================================================================
// [4] INTERNAL CORE GEOMETRY (The Commons Engine - Forced Reciprocity)
// ============================================================================
// Applies the "phasing" / degradation state 
module core_hyperobject_track() {
  decayLevel = get_prop(_cfg, "decay");
  l = get_prop(_cfg, "length");
  d = get_prop(_cfg, "diameter") * get_prop(_cfg, "scale");

  if (decayLevel == 0) {
    ideal_track_profile();
  } else {
    // Simulating the decomposition into micro-plastics. 
    // We use a high density of small subtractions to simulate brittleness/cracking.
    difference() {
      ideal_track_profile();

      for (i = [0:decayLevel * 15]) {
        z_pos = (rands(-l / 2, l / 2, 1, i)[0]);
        angle = rands(0, 360, 1, i + 10)[0];
        radius_pos = rands(d / 4, d / 2, 1, i + 20)[0];
        radius = rands(0.2, decayLevel * 0.5, 1, i + 30)[0];

        x_pos = radius_pos * cos(angle);
        y_pos = radius_pos * sin(angle);

        translate([x_pos, y_pos, z_pos]) {
          sphere(r=radius, $fn=8); // Low poly spheres for a shattered plastic look
        }
      }
    }
  }
}

// ============================================================================
// [5] MAIN EXECUTION (Render Modes)
// ============================================================================
if (render_mode == 0) {
  color("#1C1C1C") rot(x=90) core_hyperobject_track();
}
