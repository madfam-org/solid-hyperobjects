// ============================================================================
// rack.scad — AOCL 10-Slot Substrate Rack (NATIVE)
// ============================================================================
// Copyright (c) 2026 madfam-org
// Licensed under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0).
//
// Welcome to the Staining Rack module!
// This file designs a skeletal frame designed to hold up to 10 glass slides 
// securely during chemical treatments or storage. It features a carrying handle 
// and internal ribbed separators to keep the slides spaced perfectly.

// Import our custom helper library for the retention ribs and labels
use <aocl_lib.scad>

// Import the Standard BOSL2 Library for math and geometry
include <../../libs/BOSL2/std.scad>

// --- Configuration Parameters ---
// These variables act as the control panel for the 3D model.

// Standard slide dimensions (25.4mm = 1 inch)
substrate_length = 25.4;
substrate_width = 25.4;
custom_slide_thickness = 1.0;

// Clearances and walls for 3D printing tolerances
tolerance_xy = 0.4; // Horizontal wiggle room
tolerance_z = 0.2; // Vertical wiggle room
wall_thickness = 2.0; // Standard thickness of the outer frame walls

// Features and capacities
num_slots = 10; // Number of substrate slots in the rack
handle = 1; // 1 = True (add carrying handle), 0 = False
open_bottom = 1; // 1 = True (base is open gaps to let liquids drain), 0 = solid floor
drainage_angle = 5; // Tilt angle (reserved for future fluid drainage features)
label_area = 1; // Add a recess for a label sticker
numbering_start = 1; // The first number engraved above the slide slots (e.g., 1 to 10)
divider_style = 1; // 0 = stub ribs (2mm front+back rails only, faster print); 1 = full-depth fins (span entire cavity, true slide separation)
show_numbers = 1; // 1 = True (engrave slot numbers on front face), 0 = False
frame_base_grid = 1; // 1 = True (fins start from Z=0 floor), 0 = False
side_guards = 1; // 1 = True (adds 45-degree mid-height diamond grid to side walls), 0 = False
fn = 32; // Curved geometry quality. Defaults to 32.
$fn = fn > 0 ? fn : 32;

// --- Derived Geometry / Math ---
// These equations figure out how big the rack needs to be based on the number of slots and tolerances.

_min_rib_w = 2.75; // The minimum thickness of the plastic dividers holding slides (forced to match AOCL spec)

// Calculate precise slot width and overall pitch (distance from slot to slot)
_slot_w = slide_slot_width(custom_slide_thickness, tolerance_z); // Gap width
_pitch = slide_pitch(_slot_w, _min_rib_w); // Centre-to-centre distance between adjacent slots

// Determine the height of the ribs based on how deep the slide sits in it
_slot_depth = substrate_width + tolerance_xy;
_rib_height = _slot_depth;
_cavity_y = substrate_length + tolerance_xy;  // Inner cavity Y-span (front-to-back)
_chamfer_h = min(1.5, _rib_height * 0.15); // Slope at the top of the rib for guiding slides in

// Structural elements sizing (the skeleton framework)
_pillar_w = wall_thickness;
_crossbar_w = 3.0; // Base crossbar width if open_bottom is enabled
_crossbar_h = 2.5; // Base crossbar height

// Overall bounding box of the main lattice frame
// The X axis spans all slots + all ribs + the two end walls
_body_x = (num_slots * _pitch) + _min_rib_w + (2 * _pillar_w);
// The Y axis spans the length of the slide + tolerances + front/back walls
_body_y = substrate_length + (2 * _pillar_w) + tolerance_xy;
_base_h = open_bottom == 1 ? _crossbar_h : wall_thickness; // Thickness of the floor
_body_z = _rib_height + _base_h; // Total height of the skeleton frame

// Side wall extended arch variables for integrated handles
_leg_w = 4.5; // Width of the solid handle support pillars on the left/right faces
_grip_h = 5; // Thickness of the top grip bar
_holey = max(10, _body_y - 2 * _leg_w); // The wide finger cutout length
_wall_z = _body_z; // Wall height is always _body_z; arch is carved within, not added on top

// Labels sizing math
_label_w = min(30, _body_x * 0.5);
_label_h = min(10, _body_z * 0.4);
_num_size = min(2.5, _pitch * 0.7, _base_h * 0.85);

// --- Core Modules ---

// Helper module for Additive Manufacturing triangular support ramps
module am_ramp(w, l, h) {
    translate([-w/2, 0, 0])
    rotate([90, 0, 90])
    linear_extrude(w)
    polygon([[0,0], [0,h], [l,h]]);
}

// Builds the structural lattice (skeleton) of the rack and populates the retention ribs inside
module rack_body() {
  // Solid Left wall (with handle cutout if enabled)
  difference() {
    cube([_pillar_w, _body_y, _wall_z]);
    if (handle == 1) {
      // 45-degree arched cutout for the fingers
      _holex = _pillar_w + 0.2; // Extra depth to punch through cleanly
      _rect_h = max(0, (_wall_z - _base_h - _grip_h) - (_holey/2));

      translate([-0.1, _leg_w, _base_h]) {
        // Base rectangle for the fingers
        if (_rect_h > 0) cube([_holex, _holey, _rect_h]);
        
        // 45-degree peaked roof to avoid bridging
        translate([0, 0, _rect_h])
          hull() {
             cube([_holex, _holey, 0.01]);
             translate([0, _holey/2, _holey/2]) cube([_holex, 0.01, 0.01]);
          }
      }
    }
  }

  // Solid Right wall (with identical handle cutout if enabled)
  translate([_body_x - _pillar_w, 0, 0]) difference() {
    cube([_pillar_w, _body_y, _wall_z]);
    if (handle == 1) {
      _holex = _pillar_w + 0.2;
      _rect_h = max(0, (_wall_z - _base_h - _grip_h) - (_holey/2));

      translate([-0.1, _leg_w, _base_h]) {
        if (_rect_h > 0) cube([_holex, _holey, _rect_h]);
        
        translate([0, 0, _rect_h])
          hull() {
             cube([_holex, _holey, 0.01]);
             translate([0, _holey/2, _holey/2]) cube([_holex, 0.01, 0.01]);
          }
      }
    }
  }

  // Bottom plate (either a skeletal frame or a solid floor based on `open_bottom` setting)
  if (open_bottom == 1) {
    // Skeletal crossbar base (allows fluids to drain perfectly)
    cube([_body_x, _pillar_w, _crossbar_h]); // Front rail
    translate([0, _body_y - _pillar_w, 0]) cube([_body_x, _pillar_w, _crossbar_h]); // Back rail
    cube([_pillar_w, _body_y, _crossbar_h]); // Left rail
    translate([_body_x - _pillar_w, 0, 0]) cube([_pillar_w, _body_y, _crossbar_h]); // Right rail

    // Add two inner rails spanning across the X axis to hold the glass slide's bottom edges
    for (frac = [0.33, 0.67])
      translate([0, _body_y * frac - _crossbar_w / 2, 0])
        cube([_body_x, _crossbar_w, _crossbar_h]);
  } else {
    // Solid base (no gaps)
    cube([_body_x, _body_y, wall_thickness]);
  }

  // Side Guards (Diamond Grid Retaining Walls)
  if (side_guards == 1) {
    _grid_h = _body_z * 0.6;
    _grid_thick = 1.5;
    _guard_span_x = _body_x - 2 * _pillar_w;

    // Front Guard (Y = 0)
    translate([_pillar_w, 0, _base_h])
      diamond_grid_guard(_guard_span_x, _grid_thick, _grid_h - _base_h);

    // Back Guard (Y = _body_y - _grid_thick)
    translate([_pillar_w, _body_y - _grid_thick, _base_h])
      diamond_grid_guard(_guard_span_x, _grid_thick, _grid_h - _base_h);
  }

  // --- Dividers ---
  // The outer translate X is shifted +_min_rib_w/2 so divider i=0's left edge sits flush
  // with the left wall's inner face, and divider i=num_slots's right edge sits flush with
  // the right wall's inner face — achieving perfect X-axis symmetry around _body_x/2.
  //
  // Y is centred at _pillar_w + _cavity_y/2 = _body_y/2 for perfect Y-axis symmetry.
  _z_offset = frame_base_grid == 1 ? 0 : _base_h;
  _actual_rib_height = frame_base_grid == 1 ? _rib_height + _base_h : _rib_height;

  translate([_pillar_w + _min_rib_w / 2, _pillar_w + _cavity_y / 2, _z_offset]) {
    for (i = [0:num_slots]) {
      translate([i * _pitch, 0, 0]) {
        if (divider_style == 0) {
          // Stub-rib mode: two thin 2mm-deep stubs per divider (front rail + back rail).
          // Minimal material — fast to print. Slides are only retained at their edges.
          
          if (frame_base_grid == 0) {
            _stub_ramp_l = min(_base_h, _pillar_w);
            // Front Stub AM Ramp Support
             translate([0, -(_cavity_y / 2), -_base_h])
               am_ramp(_min_rib_w, _stub_ramp_l, _base_h);
            
            // Back Stub AM Ramp Support
             translate([0,  (_cavity_y / 2), -_base_h])
               rotate([0, 0, 180])
                 am_ramp(_min_rib_w, _stub_ramp_l, _base_h);
          } else {
            // Frame-Base Grid: continuous inner floor rail linking the front and back stub columns
            prismoid(size1=[_min_rib_w, _cavity_y], size2=[_min_rib_w, _cavity_y], h=_base_h, anchor=BOTTOM);
          }
          
          translate([0, -(_cavity_y / 2 - _pillar_w / 2), 0])
            slide_retention_rib(height=_actual_rib_height, depth=_pillar_w, root_w=_min_rib_w, tip_w=_min_rib_w * 0.65, chamfer_h=_chamfer_h);
          translate([0,  (_cavity_y / 2 - _pillar_w / 2), 0])
            slide_retention_rib(height=_actual_rib_height, depth=_pillar_w, root_w=_min_rib_w, tip_w=_min_rib_w * 0.65, chamfer_h=_chamfer_h);
        } else {
          // Full-depth fin mode: one continuous fin spanning the entire inner cavity depth.
          // True slide separation visible from all angles; preferred for staining use.

          if (frame_base_grid == 0) {
            // Full-Depth Fin AM Ramp Supports (anchoring to front/back crossbars)
             // Front edge of the fin
             translate([0, -(_cavity_y / 2), -_base_h])
               am_ramp(_min_rib_w, _base_h, _base_h);
               
             // Back edge of the fin
             translate([0,  (_cavity_y / 2), -_base_h])
               rotate([0, 0, 180])
                 am_ramp(_min_rib_w, _base_h, _base_h);
          }

          slide_retention_rib(height=_actual_rib_height, depth=_cavity_y, root_w=_min_rib_w, tip_w=_min_rib_w * 0.65, chamfer_h=_chamfer_h);
        }
      }
    }
  }

  // Removed external overhead handle logic; handled natively within side walls now
}

// Extrudes standard numerical text (e.g. 1 2 3...) on the frame to identify sample locations
module slot_numbers() {
  if (show_numbers == 1 && fn > 0) {
    // Only generate numbers if high quality is enabled, to save compute
    for (i = [0:num_slots - 1]) {
      // Current slot number to display
      _num = numbering_start + i;
      // Slot i centre X = left_wall + full_rib_width + half_slot + i*pitch
      // (accounts for the _min_rib_w/2 symmetry offset applied to the divider translate)
      _slot_center_x = _pillar_w + _min_rib_w + _slot_w / 2 + i * _pitch;

      // Position the number on the front face of the base rail, extruding
      // 0.4mm INTO the rail (ensuring union/merge) + 0.5mm outward (raised text).
      translate([_slot_center_x, 0.4, _base_h / 2])
        rotate([90, 0, 0])
          linear_extrude(height=0.9)
            text(str(_num), size=_num_size, halign="center", valign="center", font="Liberation Sans:style=Bold");

      // Position the identical number on the back face of the base rail
      translate([_slot_center_x, _body_y - 0.4, _base_h / 2])
        rotate([90, 0, 180]) // Flip text 180 deg around Z to face matching orientation outwards
          linear_extrude(height=0.9)
            text(str(_num), size=_num_size, halign="center", valign="center", font="Liberation Sans:style=Bold");
    }
  }
}

// Subtracts a shallow box from the solid body to form a neat labeling recess area
module rack_label() {
  if (label_area == 1) {
    // Center the label cutout horizontally and vertically on the front face
    translate([(_body_x - _label_w) / 2, -0.01, (_body_z - _label_h) / 2])
      rotate([90, 0, 0])
        translate([0, 0, -0.4])
          aocl_label_recess(_label_w, _label_h, 0.5);
    // Punches a hole exactly 0.5mm deep
  }
}

// This wrapper module cleanly combines all the shapes natively into one solid "rack"
// It ensures the label dent is cleanly SUBTRACTED out of the main body, then ADDs the raised slot numbers onto it.
module rack_complete() {
  difference() {
    rack_body();
    rack_label();
  }
  slot_numbers();
}

// Default Render
// render_mode guard: only render when compiled directly (mode 1) or without explicit mode.
// (If imported by assembly.scad via `use`, this top-level code is safely ignored.)
render_mode = 1;
if (render_mode == 1) rack_complete();
