// ============================================================================
// assembly.scad — AOCL Box & Racks Assembly (NATIVE)
// ============================================================================
// Copyright (c) 2026 madfam-org
// Licensed under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0).
//
// Welcome to the Assembly module! This file acts as the master scene that brings 
// all our individually designed parts (racks, boxes) together into a single 
// view, and adds "glass slides" to show how everything fits and operates.
//
// Think of this script as the instructions for putting Lego pieces together.

// "use" allows us to call modules from other files without executing their global code.
use <rack.scad>
use <box.scad>
use <aocl_lib.scad>

// "include" brings in an external library entirely (BOSL2 here provides advanced shapes if needed).
include <../../libs/BOSL2/std.scad>

// --- Configuration Parameters ---

// Assembly Level allows us to toggle between 3 different stages of assembly.
// Mode 1: Just a single Rack, loaded with glass slides.
// Mode 2: The bottom Box Base, loaded with 3 Racks, each loaded with slides.
// Mode 3: Everything in Mode 2, but we also place the Lid on top to close the box.
assembly_level = 3;

// Part renderer (-1 = Draw Everything, 1 = Draw Racks, 2 = Draw Base, 3 = Draw Lid)
// The Yantra4D frontend API injects this parameter to map materials and colors individually
render_mode = -1;

// --- Visibility Toggles ---
show_base = (assembly_level >= 2);
show_lid = (assembly_level >= 3);

stack_along_y = 0; // If 1, expand box along the Y-axis instead of the X-axis

// --- Physical Dimensions ---
// Note: We redefine the core measurements here so that our assembly math perfectly 
// aligns with the separate source files without having to pass variables around globally.

// Defaults sourced from aocl_lib.scad; CLI -D overrides still work.
substrate_length = aocl_substrate_length(); // Standard AOCL slide length (25.4mm = 1 inch)
substrate_width = aocl_substrate_width(); // Standard AOCL slide width
custom_slide_thickness = aocl_slide_thickness(); // Standard AOCL glass slide thickness
tolerance_xy = aocl_tolerance_xy(); // Wiggle room left and right to allow for 3D printer imprecision
tolerance_z = aocl_tolerance_z(); // Wiggle room top and bottom
num_slots = aocl_num_slots(); // How many slides fit into one rack
num_racks = 3; // How many racks fit into one box
wall_thickness = aocl_wall_thickness(); // Thickness of the standard plastic walls

// --- Math & Alignment Variables ---
// We calculate the exact footprint of the objects so we know where to place them.

// 1. Rack Footprint Math
_crossbar_h = aocl_crossbar_h(); // Height of the bottom floor/crossbars in the rack
_min_rib_w = aocl_min_rib_w(); // Width of the plastic separators (ribs) holding the slides
_slot_w = slide_slot_width(custom_slide_thickness, tolerance_z); // Use aocl_lib function
_pitch = slide_pitch(_slot_w, _min_rib_w); // Use aocl_lib function
_base_h = _crossbar_h; // Where the slide sits vertically in the rack (on top of the crossbars)

// Calculating the entire width (X) and length (Y) of *one* full rack
_rack_x = (num_slots * _pitch) + _min_rib_w + (2 * wall_thickness);
_rack_y = substrate_length + (2 * wall_thickness) + tolerance_xy;
_rack_clearance = 0.5; // Wiggle room between the rack & the box guide rails

// Calculating the exact height (Z) of *one* full rack
_slot_depth = substrate_width + tolerance_xy;
_rack_z = _slot_depth + _crossbar_h;

// 2. Box Cavity Math
// Calculate the hollow interior size of the box based on how many racks we need it to hold
_inner_x =
  (stack_along_y) ? (_rack_x + _rack_clearance * 2)
  : (num_racks * (_rack_x + _rack_clearance) + _rack_clearance);

_inner_y =
  (stack_along_y) ? (num_racks * (_rack_y + _rack_clearance) + _rack_clearance)
  : (_rack_y + _rack_clearance * 2);

// Box base height = exactly half the rack body height
_inner_z = _rack_z / 2 - wall_thickness;

// 3. Lid Positioning Math
// We need to know where the outer edges of the box are to snap the lid perfectly over it.
_box_x = _inner_x + 2 * wall_thickness;
_box_y = _inner_y + 2 * wall_thickness;
_box_z = _inner_z + wall_thickness; // Absolute top of the open box
_lid_clearance = 0.3; // Extra space so the lid isn't too tight
_lid_wall = 1.5; // The thickness of the lid's walls
_o_y = _box_y + _lid_clearance * 2 + _lid_wall * 2; // Outer dimension for the lid

// --- Box module variables (required by box_base/box_lid via `use`) ---
// OpenSCAD `use` only imports modules, NOT variables. These MUST mirror
// the corresponding values in box.scad to ensure assembly renders correctly.
// If box.scad changes any of these, update here too.
snap_lid = 1; // Creates locking latch hooks (1 = True)
label_area = 1; // Indents a space for writing labels
fn = aocl_fn();
$fn = fn > 0 ? fn : 32;

// Guide rail dimensions
_guide_h = _crossbar_h + 2;
_guide_w = 1.5;
_guide_d = _inner_y;

// Latch arm specifications
_latch_arm_len = 15;
_latch_arm_w = 8;
_latch_arm_t = 1.2;
_latch_hook_h = 2;
_latch_hook_d = 1.5;

// Lid dimensions
// Lid depth = full outer box height + ceiling thickness, so the skirt reaches the base floor
_lid_z = _box_z + 1.5;
_label_w = min(60, _box_x * 0.55);
_label_h = min(18, _box_y * 0.35);

// --- Visual Modules ---

// Module: Creates a semi-transparent, light-blue "glass slide"
module slide() {
  // We use RGBA color: Red=0.8, Green=0.9, Blue=0.95, Alpha (transparency)=0.6
  color([0.8, 0.9, 0.95, 0.6])
    cube([custom_slide_thickness, substrate_length, substrate_width]);
}

// Module: Creates one field of glass slides for a single rack (positional only, no rack body)
module slides_for_rack() {
  for (i = [0:num_slots - 1]) {
    translate([wall_thickness + i * _pitch + _min_rib_w + (_slot_w - custom_slide_thickness) / 2, wall_thickness + tolerance_xy / 2, _base_h + 0.01])
      slide();
  }
}

// Module: Renders one Rack and fills its slots with glass slides
module racks_with_slides() {
  // 1. Draw the physical rack model (imported from rack.scad)
  rack_complete();

  // 2. Overlay the glass slides
  slides_for_rack();
}

// Module: Renders ONLY the glass slides at their correct assembly positions.
//   assembly_level == 1 → single rack at origin (one rack's slides)
//   assembly_level >= 2 → num_racks racks in box-frame coordinates
module slides_only() {
  if (assembly_level == 1) {
    // Single standalone rack — slides relative to rack origin
    slides_for_rack();
  } else {
    // Multiple racks in the box — loop over all num_racks
    for (r = [0:num_racks - 1]) {
      if (stack_along_y) {
        _ry = wall_thickness + _rack_clearance + r * (_rack_y + _rack_clearance);
        translate([wall_thickness + _rack_clearance, _ry, wall_thickness])
          slides_for_rack();
      } else {
        _rx = wall_thickness + _rack_clearance + r * (_rack_x + _rack_clearance);
        translate([_rx, wall_thickness + _rack_clearance, wall_thickness])
          slides_for_rack();
      }
    }
  }
}

// Module: Renders ONLY the racks at their correct assembly positions.
//   assembly_level == 1 → single rack at origin
//   assembly_level >= 2 → num_racks racks in box-frame coordinates
module racks_only() {
  if (assembly_level == 1) {
    // Single standalone rack
    rack_complete();
  } else {
    // Multiple racks in the box — loop over all num_racks
    for (r = [0:num_racks - 1]) {
      if (stack_along_y) {
        _ry = wall_thickness + _rack_clearance + r * (_rack_y + _rack_clearance);
        translate([wall_thickness + _rack_clearance, _ry, wall_thickness])
          rack_complete();
      } else {
        _rx = wall_thickness + _rack_clearance + r * (_rack_x + _rack_clearance);
        translate([_rx, wall_thickness + _rack_clearance, wall_thickness])
          rack_complete();
      }
    }
  }
}

// Module: Renders the Box Base and populates it with 3 completed slide-racks
module box_assembly() {
  // 1. Draw the physical box base (imported from box.scad)
  if (show_base) box_base();

  // 2. Run a loop to place all the required racks inside the box cavity
  for (r = [0:num_racks - 1]) {
    if (stack_along_y) {
      _ry = wall_thickness + _rack_clearance + r * (_rack_y + _rack_clearance);
      translate([wall_thickness + _rack_clearance, _ry, wall_thickness])
        racks_with_slides();
    } else {
      // Calculate the starting X coordinate for each rack. 
      // Skips over previously placed racks + the guide rails separating them.
      _rx = wall_thickness + _rack_clearance + r * (_rack_x + _rack_clearance);

      // Translate (move) the completed rack to its designated slot inside the box
      translate([_rx, wall_thickness + _rack_clearance, wall_thickness])
        racks_with_slides();
    }
  }
}

// --- Main Execution Logic ---
// render_mode selects which part to isolate; assembly_level controls box/lid visibility.
// Rack and slide counts always scale with num_racks.

if (render_mode == 1) {
  // 1 = Rack(s) only
  racks_only();
} else if (render_mode == 2) {
  // 2 = Box Base
  if (show_base) box_base();
} else if (render_mode == 3) {
  // 3 = Box Lid
  if (show_lid) {
    translate(
      [
        -(_lid_wall + _lid_clearance),
        -(_lid_wall + _lid_clearance) + _o_y,
        _box_z + 1.5,
      ]
    )
      rotate([180, 0, 0])
        box_lid();
  }
} else if (render_mode == 4) {
  // 4 = Slides only
  slides_only();
} else {
  // render_mode == -1: full visual assembly preview
  if (assembly_level == 1) {
    // Single standalone rack with its slides
    rack_complete();
    slides_for_rack();
  } else {
    // Box with num_racks racks, slides, and optional lid
    if (show_base) box_base();
    racks_only();
    slides_only();
    if (show_lid) {
      translate(
        [
          -(_lid_wall + _lid_clearance),
          -(_lid_wall + _lid_clearance) + _o_y,
          _box_z + 1.5,
        ]
      )
        rotate([180, 0, 0])
          box_lid();
    }
  }
}
