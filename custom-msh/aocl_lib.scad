/*
 * ============================================================================
 * YANTRA4D AOCL HYPEROBJECT LIBRARY (NATIVE)
 *
 * Copyright (c) 2026 madfam-org
 * Licensed under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0).
 * ============================================================================
 * 
 * CORE CDG: AOCL Substrate Retention & Box Latches
 *
 * Welcome to the AOCL Library!
 * This file contains reusable "helper modules" and mathematical functions. 
 * Instead of rewriting the code for a latch or a slide-holder rib in every 
 * single file, we write it once here. Other files can then "use" this file 
 * to generate those shapes effortlessly. Think of it as a toolbox!
 */

// Import the BOSL2 standard library for advanced 3D geometry manipulation
include <BOSL2/std.scad>

// --- AOCL Standard Defaults ---
// Shared constants as functions so `use <aocl_lib.scad>` imports them.
// OpenSCAD `use` imports modules and functions but NOT variables —
// wrapping defaults as zero-arg functions is the canonical DRY pattern.
// Each consuming file still declares a top-level variable (e.g.
//   substrate_length = aocl_substrate_length();
// ) so OpenSCAD CLI `-D` overrides continue to work.
function aocl_substrate_length()       = 25.4;
function aocl_substrate_width()        = 25.4;
function aocl_slide_thickness()        = 1.0;
function aocl_tolerance_xy()           = 0.4;
function aocl_tolerance_z()            = 0.2;
function aocl_wall_thickness()         = 2.0;
function aocl_num_slots()              = 10;
function aocl_min_rib_w()              = 2.75;
function aocl_crossbar_h()             = 2.5;
function aocl_fn()                     = 32;

// --- CDG Math Functions ---
function slide_slot_width(thickness, tolerance) = thickness + 2 * tolerance;
function slide_pitch(slot_w, rib_w) = slot_w + rib_w;
// --- Core Modules ---
// These modules generate physical 3D shapes.

// Generates a solid rectangular block that will later be SUBTRACTED from another object to make a shallow dent (recess) for sticking a label on.
module aocl_label_recess(w, h, d = 0.4) {
  // Create a box anchored to the bottom face
  cuboid([w, h, d], anchor=BOTTOM);
}

// Generates a snap-fit cantilever arm. This is a flexible plastic stick with a hook at the top.
// Used mainly on the lid to securely snap onto the box.
module aocl_snap_arm(len, w, t, hook_h, hook_d) {
  // First, draw the flexible stick (arm)
  cuboid([w, t, len], anchor=BOTTOM + BACK) {
    // Then, attach the hook to the top of the stick
    attach(TOP) cuboid([w, t + hook_d, hook_h], anchor=BOTTOM + BACK);
  }
}

// Generates the solid catch/receptacle for the snap-fit arm.
// This is simply a small block sticking out of the box base that the snap-arm hook grabs onto.
module aocl_snap_catch(w, h, d) {
  cuboid([w, d, h], anchor=BOTTOM);
}

// Generates a 45-degree diamond lattice panel.
// span: primary extent (X), thickness: panel depth (Y), height: panel height (Z)
// step: lattice cell size, bar: lattice line thickness
module diamond_grid_guard(span, thickness, height, step=8, bar=1.5) {
  // ONE construction: resolve the whole panel as a 2D region in the X-Z plane and
  // extrude it once through the panel thickness.
  //
  // It used to be a 3D `intersection()` of an envelope cube against loose
  // 45-degree bar cubes, and that carried two defects:
  //
  //   * Disjoint panel. With no perimeter frame the panel is only as connected as
  //     the bars' own crossings; above a span of roughly 45 mm the two families
  //     stop overlapping and the guard exported as 2 separate bodies (this is the
  //     rack at `num_slots` >= 11). A retaining grid wants a frame anyway -- an
  //     unframed lattice has bar ends cantilevered into thin air all round.
  //
  //   * Severed slivers. Any bar that ends tangent to an edge of the region it is
  //     clipped against leaves a wedge that the union can orphan. The wedges were
  //     tiny (-0.02 to -0.56 mm3) and they tracked placement and span exactly,
  //     which is what identifies a tangency rather than a boolean tolerance.
  //
  // KNOWN RESIDUAL: chamfering removes every wedge at the shipped spans -- the
  // whole `y4d-spec` matrix (23 renders, 14 presets) is watertight with 0
  // negative bodies -- but it protects CORNERS, and at a few non-default spans a
  // bar can still run tangent to a straight window EDGE. `multi_rack` at
  // `num_slots` 5 and 15 shows 6 and 12 such wedges of -0.02 to -0.05 mm3.
  // Clipping the lattice to the panel outline instead of the window removes
  // those but reintroduces wedges at the DEFAULT span, so it is strictly worse;
  // the real cure is a lattice whose period divides the window, which changes
  // the visible grid and belongs to a design decision, not a repair lane.
  //
  // The construction below addresses both. The ring and BOTH bar families are
  // unioned as polygons and the union is clipped ONCE to the panel outline, and
  // `linear_extrude` of a well-formed 2D region is always a closed solid -- so
  // the panel is one connected piece by construction rather than by luck. The
  // chamfered window corners then remove the corner tangency, which is what the
  // shipped spans actually hit.
  //
  // The window is clamped positive so a panel narrower or shorter than two frame
  // widths degenerates to a solid plate rather than to an inside-out difference.
  _frame = bar;
  _wx = max(0.01, span - 2 * _frame);
  _wz = max(0.01, height - 2 * _frame);
  _max = max(span, height) + step;

  // The 2D profile lives in X-Z; rotate it upright and pull it back so the solid
  // occupies x [0, span], y [0, thickness], z [0, height] -- the same box every
  // caller already positions.
  rotate([90, 0, 0])
    translate([0, 0, -thickness])
      linear_extrude(height = thickness)
        intersection() {
          square([span, height]);
          union() {
            // Perimeter ring, its window corners chamfered at 45 degrees so the
            // window edge runs PARALLEL to the bar family that would otherwise
            // slice a triangle off a sharp corner and orphan it.
            difference() {
              square([span, height]);
              _cx = min(bar, _wx / 2);
              _cz = min(bar, _wz / 2);
              polygon([
                [_frame + _cx,       _frame],
                [_frame + _wx - _cx, _frame],
                [_frame + _wx,       _frame + _cz],
                [_frame + _wx,       _frame + _wz - _cz],
                [_frame + _wx - _cx, _frame + _wz],
                [_frame + _cx,       _frame + _wz],
                [_frame,             _frame + _wz - _cz],
                [_frame,             _frame + _cz],
              ]);
            }
            // 45-degree lattice, both families.
            for (x = [-_max : step : span + _max]) {
              translate([x, 0]) rotate(-45) translate([0, -_max]) square([bar, _max * 3]);
              translate([x, 0]) rotate(45)  translate([0, -_max]) square([bar, _max * 3]);
            }
          }
        }
}

module slide_retention_rib(height, depth, root_w, tip_w, chamfer_h = 0) {
  _main_h = height - chamfer_h;
  // The two prismoids MUST be an explicit union and MUST overlap. As bare
  // siblings meeting exactly at z = _main_h -- the main one's top face
  // [tip_w, depth] against the chamfer's bottom face of the same [tip_w,
  // depth] -- every rib contributed a zero-thickness contact, and with one rib
  // per slot that is what made the whole rack non-watertight. Overlap the
  // chamfer down into the main body by _lap so the seam has volume.
  _lap = min(0.2, _main_h > 0 ? _main_h * 0.5 : 0.2);
  union() {
    if (_main_h > 0) {
      prismoid(size1=[root_w, depth], size2=[tip_w, depth], h=_main_h, anchor=BOTTOM);
    }
    if (chamfer_h > 0) {
      translate([0, 0, _main_h - _lap])
        prismoid(size1=[tip_w, depth], size2=[tip_w * 0.3, depth * 0.3],
                 h=chamfer_h + _lap, anchor=BOTTOM);
    }
  }
}
