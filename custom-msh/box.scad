// ============================================================================
// box.scad — AOCL Outer Box (Portamuestras) (NATIVE)
// ============================================================================
// Copyright (c) 2026 madfam-org
// Licensed under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0).
//
// Welcome to the Box & Lid module!
// This file designs an outer protective casing tailored specifically to hold 
// 3 assembled "staining racks". It consists of two selectable components:
// a deeper base, and a snap-fit lid to lock everything safely inside.

// Import our custom helper library for building snaps and catches
use <aocl_lib.scad>

// Import the Standard BOSL2 Library for advanced geometric shapes like 'cuboid'
include <../../libs/BOSL2/std.scad>

// --- Configuration Parameters ---
// Defaults sourced from aocl_lib.scad; CLI -D overrides still work.

// Accommodated slide dimensions (Standard 1 inch AOCL slides)
substrate_length = aocl_substrate_length();
substrate_width = aocl_substrate_width();
custom_slide_thickness = aocl_slide_thickness();

// Fits and Tolerances (Wiggle room for 3D printing accuracy)
tolerance_xy = aocl_tolerance_xy();
tolerance_z = aocl_tolerance_z();
wall_thickness = aocl_wall_thickness();

// Global Setup Configuration
num_racks = 3; // Determines how wide the box should be to fit this many racks
label_area = 1; // Indents a space for writing labels
stack_along_y = 1; // If 1, expand box along the Y-axis instead of the X-axis
fn = aocl_fn(); // Smoothness curve quality. (Default to 32)
$fn = fn > 0 ? fn : 32;

// Part renderer (0 = Draw Base, 1 = Draw Lid)
render_mode = 0;

// --- Imposed Rack Math ---
// Recalculating the exact physical footprint of the inner `rack.scad` objects 
// here so the box can dynamically scale to fit them perfectly without importing them.

_min_rib_w = aocl_min_rib_w();
_slot_w = slide_slot_width(custom_slide_thickness, tolerance_z); // Gap width
_pitch = slide_pitch(_slot_w, _min_rib_w); // Centre-to-centre distance between adjacent slots
num_slots = aocl_num_slots(); // Substrate slots per rack (matches rack.scad default)
_pillar_w = wall_thickness;

_rack_x = (num_slots * _pitch) + _min_rib_w + (2 * _pillar_w); // Total Rack Width
_rack_y = substrate_length + (2 * _pillar_w) + tolerance_xy; // Total Rack Length
_slot_depth = substrate_width + tolerance_xy;
_crossbar_h = aocl_crossbar_h();

_rack_z = _slot_depth + _crossbar_h; // Height without handle
_handle_h = 0; // Handle is an internal arch (no protrusion above _rack_z)

// --- Box Cavity Calculations ---

_rack_clearance = 0.5; // Gap between the racks and the box walls
_guide_w = 1.5; // Thickness of the internal divider walls
_comp_gap = _rack_clearance * 2 + _guide_w; // Total inter-rack spacing

// Define inner hollow cavity to hold all racks across X, Y, Z dimensions
_inner_x =
  (stack_along_y) ? (_rack_x + _rack_clearance * 2)
  : (num_racks * _rack_x + _rack_clearance * 2 + (num_racks >= 2 ? (num_racks - 1) * _comp_gap : 0));

_inner_y =
  (stack_along_y) ? (num_racks * _rack_y + _rack_clearance * 2 + (num_racks >= 2 ? (num_racks - 1) * _comp_gap : 0))
  : (_rack_y + _rack_clearance * 2);
// Box base cavity height (Low lip)
_inner_z = 10;

// Define the absolute outer shell boundaries of the box base
_box_x = _inner_x + 2 * wall_thickness;
_box_y = _inner_y + 2 * wall_thickness;
_box_z = _inner_z + wall_thickness;

// Mid-height divider wall between consecutive rack slots
_div_h = _inner_z; // Rises to the edge of the base interior lip

// Lid specs (Flush fitting)
// Lid depth = full inner height minus the base lip height + ceiling thickness
_lid_z = (_rack_z + _rack_clearance) - _inner_z + wall_thickness;

_label_w = min(60, _box_x * 0.55);
_label_h = min(18, _box_y * 0.35);

// --- Core Modules ---

// Mid-height divider walls between consecutive rack slots
// Each divider is perfectly spaced in the inter-rack gap.
module rack_dividers() {
  if (num_racks >= 2) {
    for (r = [0:num_racks - 2]) { // one divider per inter-rack gap
      if (stack_along_y) {
        // Racks stacked along Y: divider is a wall parallel to X-Z plane
        _ry_back = wall_thickness + _rack_clearance + r * (_rack_y + _comp_gap) + _rack_y;
        translate([
          wall_thickness,
          _ry_back + _rack_clearance, // perfectly between the two clearances
          wall_thickness
        ])
          cube([_inner_x, _guide_w, _div_h]);
      } else {
        // Racks stacked along X: divider is a wall parallel to Y-Z plane
        _rx_right = wall_thickness + _rack_clearance + r * (_rack_x + _comp_gap) + _rack_x;
        translate([
          _rx_right + _rack_clearance,
          wall_thickness,
          wall_thickness
        ])
          cube([_guide_w, _inner_y, _div_h]);
      }
    }
  }
}

// Bottom enclosure shell (Base of the box)
module box_base() {
  union() {
    // Use `difference()` to scoop out an inner cavity from a solid block
    difference() {
      // 1. Draw solid outer box shell with rounded bottom edges
      cuboid([_box_x, _box_y, _box_z], rounding=1.5, edges=[BOTTOM], anchor=BOTTOM + LEFT + FRONT);

      // Finally, subtract the huge core cubic volume for the main internal cavity!
      translate([wall_thickness, wall_thickness, wall_thickness])
        cube([_inner_x, _inner_y, _inner_z + 1]);

      // Subtract a labeling recess from the front shell surface
      if (label_area == 1) {
        _lbl_w = min(40, _box_x * 0.45);
        _lbl_h = min(10, _box_z * 0.35);
        translate([(_box_x - _lbl_w) / 2, -0.01, (_box_z - _lbl_h) / 2])
          rotate([90, 0, 0])
            translate([0, 0, -0.4])
              aocl_label_recess(_lbl_w, _lbl_h, 0.5);
      }
    }

    // 3. Draw the mid-height dividers inside the hollow cavity
    rack_dividers();
  }
}

// Top cap enclosure that slips over perfectly flush
module box_lid() {
  // Define lid outer boundaries expanding outside the main box 
  _o_x = _box_x;
  _o_y = _box_y;

  difference() {
    // Draw the overall solid outer lid shell with rounded top edges
    cuboid([_o_x, _o_y, _lid_z], rounding=1.5, edges=[TOP], anchor=BOTTOM + LEFT + FRONT);

    // Scoop out the inner empty cavity where the base and rack handles enter
    translate([wall_thickness, wall_thickness, -0.01]) cube([_inner_x, _inner_y, _lid_z - wall_thickness + 0.01]);

    // Honeycomb/Voronoi grid from Left and Right sides (moved from base)
    _hex_frame = 5;
    _hex_d = 8;
    _hx_len = _o_y - (_hex_frame * 2);
    _hx_hei = _lid_z - (_hex_frame * 2) - 4; // Extra clearance from top
    
    // Subtract honeycomb hex pattern from left and right walls
    if (_hx_hei > 5 && _hx_len > 5) {
      _hex_sp_y = _hex_d + 1;
      _hex_sp_z = _hex_d + 1.5;
      _hex_cols = floor(_hx_len / _hex_sp_y);
      _hex_rows = floor(_hx_hei / _hex_sp_z);
      _hex_oy = (_hx_len - _hex_cols * _hex_sp_y) / 2;
      _hex_oz = (_hx_hei - _hex_rows * _hex_sp_z) / 2;

      // Left wall hex cutouts
      for (row = [0:_hex_rows - 1])
        for (col = [0:_hex_cols - 1]) {
          _stagger = (row % 2 == 1) ? _hex_sp_y / 2 : 0;
          _cy = _hex_frame + _hex_oy + col * _hex_sp_y + _hex_sp_y / 2 + _stagger;
          _cz = _hex_frame + _hex_oz + row * _hex_sp_z + _hex_sp_z / 2;
          if (_cy > _hex_frame + _hex_d/2 && _cy < _o_y - _hex_frame - _hex_d/2 &&
              _cz > _hex_frame + _hex_d/2 && _cz < _lid_z - _hex_frame - _hex_d/2 - 4)
            translate([-1, _cy, _cz])
              rotate([0, 90, 0])
                cylinder(d=_hex_d, h=wall_thickness+2+0.01, $fn=6);
        }

      // Right wall hex cutouts
      for (row = [0:_hex_rows - 1])
        for (col = [0:_hex_cols - 1]) {
          _stagger = (row % 2 == 1) ? _hex_sp_y / 2 : 0;
          _cy = _hex_frame + _hex_oy + col * _hex_sp_y + _hex_sp_y / 2 + _stagger;
          _cz = _hex_frame + _hex_oz + row * _hex_sp_z + _hex_sp_z / 2;
          if (_cy > _hex_frame + _hex_d/2 && _cy < _o_y - _hex_frame - _hex_d/2 &&
              _cz > _hex_frame + _hex_d/2 && _cz < _lid_z - _hex_frame - _hex_d/2 - 4)
            translate([_o_x - wall_thickness - 1, _cy, _cz])
              rotate([0, 90, 0])
                cylinder(d=_hex_d, h=wall_thickness+2+0.01, $fn=6);
        }
    }


    // Indent a small label space directly on the ceiling of the lid
    if (label_area) {
      translate([(_o_x - _label_w) / 2, (_o_y - _label_h) / 2, _lid_z - 0.39])
        aocl_label_recess(_label_w, _label_h, 0.4);
    }
  }
}

// Render the selected discrete part natively based on configuration
if (render_mode == 0 || render_mode == 2) {
  box_base();
}
if (render_mode == 1 || render_mode == 3) {
  box_lid();
}
