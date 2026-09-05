// ============================================================================
// multi_rack.scad — AOCL Multi-Rack Joined Body (NATIVE)
// ============================================================================
// Copyright (c) 2026 madfam-org
// Licensed under the CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W-2.0).
//
// Produces 2–5 contiguous staining racks joined along Y-axis (front-to-back,
// default) or X-axis (side-by-side).
// Internal junctions use Diamond Grid Side Guards instead of double solid walls.
// Side guards are mandatory (always ON) — not toggleable in this mode.

use <aocl_lib.scad>
include <../../libs/BOSL2/std.scad>

// --- Configuration Parameters ---
// Defaults sourced from aocl_lib.scad; CLI -D overrides still work.
substrate_length = aocl_substrate_length();
substrate_width = aocl_substrate_width();
custom_slide_thickness = aocl_slide_thickness();
tolerance_xy = aocl_tolerance_xy();
tolerance_z = aocl_tolerance_z();
wall_thickness = aocl_wall_thickness();

num_slots = aocl_num_slots();
multi_num_racks = 3;
multi_stack_y = 1; // 1 = join along Y (front-to-back, default), 0 = join along X (side-by-side)
handle = 1;
open_bottom = 1;
label_area = 1;
numbering_start = 1;
divider_style = 1;
show_numbers = 1;
frame_base_grid = 1;
fn = aocl_fn();
$fn = fn > 0 ? fn : 32;

// --- Derived Geometry ---
_min_rib_w = aocl_min_rib_w();
_slot_w = slide_slot_width(custom_slide_thickness, tolerance_z);
_pitch = slide_pitch(_slot_w, _min_rib_w);

_slot_depth = substrate_width + tolerance_xy;
_rib_height = _slot_depth;
_cavity_y = substrate_length + tolerance_xy;
_chamfer_h = min(1.5, _rib_height * 0.15);

_pillar_w = wall_thickness;
_crossbar_w = 3.0;
_crossbar_h = aocl_crossbar_h();

// Single-rack inner dimensions (without end walls)
_inner_x = (num_slots * _pitch) + _min_rib_w;
_inner_per_rack = _inner_x;
_inner_y = _cavity_y;

// Single-rack body dimensions
_body_x_single = _inner_x + 2 * _pillar_w;
_body_y = substrate_length + (2 * _pillar_w) + tolerance_xy;
_base_h = open_bottom == 1 ? _crossbar_h : wall_thickness;
_body_z = _rib_height + _base_h;

// Axis-aware total dimensions
_total_x = multi_stack_y == 1
  ? _body_x_single
  : (multi_num_racks * _inner_x) + (multi_num_racks + 1) * _pillar_w;

_total_y = multi_stack_y == 1
  ? (multi_num_racks * _inner_y) + (multi_num_racks + 1) * _pillar_w
  : _body_y;

// Handle geometry (matches rack.scad)
_leg_w = 4.5;
_grip_h = 5;
_wall_z = _body_z;

// Labels
_label_w = min(30, _total_x * 0.3);
_label_h = min(10, _body_z * 0.4);
_num_size = min(2.5, _pitch * 0.7, _base_h * 0.85);

// Diamond grid
_grid_h = _body_z * 0.6;
_grid_thick = 1.5;

// --- Helper Modules ---

module am_ramp(w, l, h) {
  translate([-w/2, 0, 0])
    rotate([90, 0, 90])
      linear_extrude(w)
        polygon([[0,0], [0,h], [l,h]]);
}

// Handle wall (left or right outer end) with optional handle cutout.
// Spans y_span in Y dimension, placed at x_pos.
module handle_wall(x_pos, y_span) {
  translate([x_pos, 0, 0]) difference() {
    cube([_pillar_w, y_span, _wall_z]);
    if (handle == 1) {
      _holex = _pillar_w + 0.2;
      _local_holey = max(10, y_span - 2 * _leg_w);
      _rect_h = max(0, (_wall_z - _base_h - _grip_h) - (_local_holey / 2));
      translate([-0.1, _leg_w, _base_h]) {
        if (_rect_h > 0) cube([_holex, _local_holey, _rect_h]);
        translate([0, 0, _rect_h])
          hull() {
            cube([_holex, _local_holey, 0.01]);
            translate([0, _local_holey / 2, _local_holey / 2]) cube([_holex, 0.01, 0.01]);
          }
      }
    }
  }
}

// Solid end wall (X-Z plane, no handle) for Y-stacking front/back ends.
module plain_end_wall(y_pos, x_span) {
  translate([0, y_pos, 0])
    cube([x_span, _pillar_w, _wall_z]);
}

// Dividers for one rack segment at explicit (seg_x, seg_y) cavity origin
module rack_segment_dividers(seg_x, seg_y) {
  _z_offset = frame_base_grid == 1 ? 0 : _base_h;
  _actual_rib_height = frame_base_grid == 1 ? _rib_height + _base_h : _rib_height;

  translate([seg_x + _min_rib_w / 2, seg_y + _cavity_y / 2, _z_offset]) {
    for (i = [0:num_slots]) {
      translate([i * _pitch, 0, 0]) {
        if (divider_style == 0) {
          // Stub-rib mode
          if (frame_base_grid == 0) {
            _stub_ramp_l = min(_base_h, _pillar_w);
            translate([0, -(_cavity_y / 2), -_base_h])
              am_ramp(_min_rib_w, _stub_ramp_l, _base_h);
            translate([0, (_cavity_y / 2), -_base_h])
              rotate([0, 0, 180])
                am_ramp(_min_rib_w, _stub_ramp_l, _base_h);
          } else {
            prismoid(size1=[_min_rib_w, _cavity_y], size2=[_min_rib_w, _cavity_y],
                     h=_base_h, anchor=BOTTOM);
          }
          translate([0, -(_cavity_y / 2 - _pillar_w / 2), 0])
            slide_retention_rib(height=_actual_rib_height, depth=_pillar_w,
                               root_w=_min_rib_w, tip_w=_min_rib_w * 0.65,
                               chamfer_h=_chamfer_h);
          translate([0, (_cavity_y / 2 - _pillar_w / 2), 0])
            slide_retention_rib(height=_actual_rib_height, depth=_pillar_w,
                               root_w=_min_rib_w, tip_w=_min_rib_w * 0.65,
                               chamfer_h=_chamfer_h);
        } else {
          // Full-depth fin mode
          if (frame_base_grid == 0) {
            translate([0, -(_cavity_y / 2), -_base_h])
              am_ramp(_min_rib_w, _base_h, _base_h);
            translate([0, (_cavity_y / 2), -_base_h])
              rotate([0, 0, 180])
                am_ramp(_min_rib_w, _base_h, _base_h);
          }
          slide_retention_rib(height=_actual_rib_height, depth=_cavity_y,
                             root_w=_min_rib_w, tip_w=_min_rib_w * 0.65,
                             chamfer_h=_chamfer_h);
        }
      }
    }
  }
}

// Slot numbers for one segment at explicit position with specified start number
module rack_segment_numbers(seg_x, seg_y, start_num) {
  if (show_numbers == 1 && fn > 0) {
    _front_y = seg_y - _pillar_w + 0.4;
    _back_y = seg_y + _inner_y + _pillar_w - 0.4;

    for (i = [0:num_slots - 1]) {
      _num = start_num + i;
      _slot_center_x = seg_x + _min_rib_w + _slot_w / 2 + i * _pitch;

      // Front face number
      translate([_slot_center_x, _front_y, _base_h / 2])
        rotate([90, 0, 0])
          linear_extrude(height=0.9)
            text(str(_num), size=_num_size, halign="center", valign="center",
                 font="Liberation Sans:style=Bold");

      // Back face number
      translate([_slot_center_x, _back_y, _base_h / 2])
        rotate([90, 0, 180])
          linear_extrude(height=0.9)
            text(str(_num), size=_num_size, halign="center", valign="center",
                 font="Liberation Sans:style=Bold");
    }
  }
}

// Diamond grid guard in X-Z plane at Y junction (for Y-axis stacking)
module junction_guard_xz(jy) {
  translate([_pillar_w, jy, _base_h])
    diamond_grid_guard(_inner_x, _pillar_w, _grid_h - _base_h);
}

// Continuous diamond grid guards on the perimeter sides
module continuous_side_guards() {
  if (multi_stack_y == 0) {
    // X stacking: front/back guards (X-Z plane, span full inner X)
    _guard_span_x = _total_x - 2 * _pillar_w;

    // Front guard (Y = 0 face)
    translate([_pillar_w, 0, _base_h])
      diamond_grid_guard(_guard_span_x, _grid_thick, _grid_h - _base_h);

    // Back guard (Y = _body_y face)
    translate([_pillar_w, _body_y - _grid_thick, _base_h])
      diamond_grid_guard(_guard_span_x, _grid_thick, _grid_h - _base_h);
  }
}

// Label recess centered on the front face
module multi_rack_label() {
  if (label_area == 1) {
    translate([(_total_x - _label_w) / 2, -0.01, (_body_z - _label_h) / 2])
      rotate([90, 0, 0])
        translate([0, 0, -0.4])
          aocl_label_recess(_label_w, _label_h, 0.5);
  }
}

// --- Main Composition ---
module multi_rack_complete() {
  difference() {
    union() {
      if (multi_stack_y == 1) {
        // === Y-AXIS STACKING (front-to-back) ===

        // Per-segment handle walls (front/back, each with independent handle cutout)
        for (i = [0:multi_num_racks - 1]) {
          _seg_y_start = i * (_inner_y + _pillar_w);
          translate([0, _seg_y_start, 0]) {
            handle_wall(0, _body_y);
            handle_wall(_body_x_single - _pillar_w, _body_y);
          }
        }

        // End walls (front/back, solid, no handles)
        plain_end_wall(0, _body_x_single);
        plain_end_wall(_total_y - _pillar_w, _body_x_single);

        // Base plate
        if (open_bottom == 1) {
          // Full-span left/right rails
          cube([_pillar_w, _total_y, _crossbar_h]);
          translate([_body_x_single - _pillar_w, 0, 0])
            cube([_pillar_w, _total_y, _crossbar_h]);

          // Full-span front/back rails
          cube([_body_x_single, _pillar_w, _crossbar_h]);
          translate([0, _total_y - _pillar_w, 0])
            cube([_body_x_single, _pillar_w, _crossbar_h]);

          // Junction rails (X direction at each Y junction)
          for (j = [0:multi_num_racks - 2]) {
            _jy = _pillar_w + (j + 1) * _inner_y + j * _pillar_w;
            translate([0, _jy, 0])
              cube([_body_x_single, _pillar_w, _crossbar_h]);
          }

          // Per-segment inner crossbar rails (at 33%/67% of inner_y within each segment)
          for (i = [0:multi_num_racks - 1]) {
            _sy = _pillar_w + i * (_inner_y + _pillar_w);
            for (frac = [0.33, 0.67])
              translate([0, _sy + _inner_y * frac - _crossbar_w / 2, 0])
                cube([_body_x_single, _crossbar_w, _crossbar_h]);
          }
        } else {
          // Solid base floor
          cube([_body_x_single, _total_y, wall_thickness]);
        }

        // Dividers and slot numbers for each rack segment
        for (i = [0:multi_num_racks - 1]) {
          _sy = _pillar_w + i * (_inner_y + _pillar_w);
          rack_segment_dividers(_pillar_w, _sy);
          rack_segment_numbers(_pillar_w, _sy, numbering_start + i * num_slots);
        }

        // Junction diamond grid guards (X-Z plane between adjacent segments)
        for (j = [0:multi_num_racks - 2]) {
          _jy = _pillar_w + (j + 1) * _inner_y + j * _pillar_w;
          junction_guard_xz(_jy);
        }

        // Per-segment side guards (X-Z plane diamond grid at each segment's Y boundaries)
        for (i = [0:multi_num_racks - 1]) {
          _sy = _pillar_w + i * (_inner_y + _pillar_w);

          // Segment front side guard (Y = segment start)
          translate([_pillar_w, _sy - _grid_thick, _base_h])
            diamond_grid_guard(_inner_x, _grid_thick, _grid_h - _base_h);

          // Segment back side guard (Y = segment end)
          translate([_pillar_w, _sy + _inner_y, _base_h])
            diamond_grid_guard(_inner_x, _grid_thick, _grid_h - _base_h);
        }

      } else {
        // === X-AXIS STACKING (side-by-side) ===

        // Outer handle walls (with handle cutouts)
        handle_wall(0, _body_y);
        handle_wall(_total_x - _pillar_w, _body_y);

        // Base plate
        if (open_bottom == 1) {
          // Full-width front and back rails
          cube([_total_x, _pillar_w, _crossbar_h]);
          translate([0, _body_y - _pillar_w, 0])
            cube([_total_x, _pillar_w, _crossbar_h]);

          // Outer side rails (front-to-back at each end)
          cube([_pillar_w, _body_y, _crossbar_h]);
          translate([_total_x - _pillar_w, 0, 0])
            cube([_pillar_w, _body_y, _crossbar_h]);

          // Junction side rails (front-to-back at each internal junction)
          for (j = [0:multi_num_racks - 2]) {
            _jx = _pillar_w + (j + 1) * _inner_x + j * _pillar_w;
            translate([_jx, 0, 0])
              cube([_pillar_w, _body_y, _crossbar_h]);
          }

          // Inner crossbar rails (full-width at 33% and 67% of Y)
          for (frac = [0.33, 0.67])
            translate([0, _body_y * frac - _crossbar_w / 2, 0])
              cube([_total_x, _crossbar_w, _crossbar_h]);
        } else {
          // Solid base floor
          cube([_total_x, _body_y, wall_thickness]);
        }

        // Dividers and slot numbers for each rack segment
        for (i = [0:multi_num_racks - 1]) {
          _sx = _pillar_w + i * (_inner_x + _pillar_w);
          rack_segment_dividers(_sx, _pillar_w);
          rack_segment_numbers(_sx, _pillar_w, numbering_start + i * num_slots);
        }

        // Junction walls (solid handle walls between adjacent segments)
        for (j = [0:multi_num_racks - 2]) {
          _jx = _pillar_w + (j + 1) * _inner_x + j * _pillar_w;
          handle_wall(_jx, _body_y);
        }

        // Continuous front/back diamond grid guards (full width)
        continuous_side_guards();
      }
    }

    // Subtract label recess
    multi_rack_label();
  }
}

// --- Render ---
render_mode = 5;
if (render_mode == 5) multi_rack_complete();
