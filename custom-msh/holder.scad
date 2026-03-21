// ============================================================================
// holder.scad — AOCL Single Substrate Holder (NATIVE)
// ============================================================================
// Copyright (c) 2026 madfam-org
// Licensed under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0).
//
// Welcome to the Custom-MSH Single Holder!
// This file generates a thick, robust block designed to securely hold a single 
// 1x1 inch glass slide. It is primarily used for individual substrate investigation 
// under a microscope.

// Import our custom helper library to generate the label recess
use <aocl_lib.scad>

// Import the BOSL2 library for advanced geometric operations like creating cuboids and chamfers
include <../../libs/BOSL2/std.scad>

// --- Configuration Parameters ---
// These variables act as the control panel for the 3D model.
// Changing them alters how the model looks and prints.

// Defaults sourced from aocl_lib.scad; CLI -D overrides still work.

// Substrate physical dimensions (AOCL standard is 25.4mm, or 1 inch)
substrate_length = aocl_substrate_length();
substrate_width = aocl_substrate_width();

// FDM 3D printing clearances. Plastic shrinks and layers bulge, so we add
// a small "wiggle room" gap to the holes so parts fit together smoothly.
tolerance_xy = aocl_tolerance_xy(); // Clearance on the sides (X and Y axes)
tolerance_z = aocl_tolerance_z(); // Clearance top to bottom (Z axis)

// Structural thickness for robust parts. How thick the walls of the holder are.
wall_thickness = aocl_wall_thickness();
holder_thickness = 2.0; // Total Z-axis thickness of the solid holder block

// Feature toggles (1 = True/On, 0 = False/Off)
label_area = 1; // Controls whether to cut a shallow dent to stick a label onto
chamfer_pocket = 1; // Controls whether the top edge of the hole should be sloped to guide the slide in easily
fn = aocl_fn(); // Geometry curve quality ($fn). Higher = smoother curves but slower rendering. Defaults to 32.

$fn = fn > 0 ? fn : 32; // Set global quality. If it's 0 (auto), force to 32.

// --- Derived Geometry Variables ---
// These variables do the math behind the scenes to size the bulk of the object.
// The base holder block is fixed to exactly 5 x 3 inches long and uses the parametric thickness.
_length = 5 * 25.4;
_width = 3 * 25.4;
_thickness = holder_thickness;

// Add clearance to the pocket so the slide physically fits into it
_pocket_length = substrate_length + tolerance_xy;
_pocket_width = substrate_width + tolerance_xy;
_chamfer_size = 1.5; // Depth and width of the sloped top rim

// Dimensions for the recess where the user can put a sticker or write on it
_label_w = 40; // 40mm wide
_label_h = 15; // 15mm tall
_label_d = 0.4; // 0.4mm deep

// --- Main Module ---
// Generates the solid body and uses BOSL2 "diff" to cave out the shapes we want empty.

module holder_body() {
  // We center the whole object mathematically based on its size
  translate([_length / 2, _width / 2, _thickness / 2]) {

    // Evaluate geometry matching "pocket" and "label" tags and SUBTRACT them from the main base block.
    // Think of this like taking a cookie cutter to playdough.
    diff("pocket label") {

      // 1. Create the main solid playdough block (Base cuboid)
      cuboid([_length, _width, _thickness], rounding=min(1.5, _thickness / 2.01), edges=[TOP, BOTTOM], anchor=CENTER);

      // 2. Define the exact shape and position of the 1x1 inch pocket to be carved out
      tag("pocket") {
        // We make the pocket cutout slightly taller than the thickness so it punches clean through
        cuboid([_pocket_length, _pocket_width, _thickness + 2], anchor=CENTER);

        // Subtract a chamfered (sloped) rim around the top edge of the pocket for easier slide insertion
        if (chamfer_pocket == 1) {
          // Move to the top of the block before applying the chamfer shape
          up(_thickness / 2) down(_chamfer_size)
              prismoid(size1=[_pocket_length, _pocket_width], size2=[_pocket_length + 2 * _chamfer_size, _pocket_width + 2 * _chamfer_size], h=_chamfer_size + 0.01, anchor=BOTTOM);
        }
      }

      // 3. Define the exact shape of the debossed label area to be carved out
      if (label_area == 1) {
        tag("label")
          // Move to the top face of the block, sunken by the depth of the label
          down(_thickness / 2 - _label_d)
            aocl_label_recess(_label_w, _label_h, _label_d + 0.1);
      }
    }
  }
}

// Top-level instantiation
// render_mode guard: only render when compiled directly (mode 0) or without explicit mode
render_mode = 0;
if (render_mode == 0) holder_body();
