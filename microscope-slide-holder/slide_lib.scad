// ============================================================================
// slide_lib.scad — Shared Geometry Library for Microscope Slide Retention
// ============================================================================
// Reference: docs/RESEARCH.pdf — "Parametric Architectures for Microscope
//            Slide Retention" (ISO 8037 tolerance fields, FDM constraints)
//
// This file is `use`d by all four mode SCAD files (box, tray, staining_rack,
// cabinet_drawer). It provides the common-denominator geometry primitives
// identified in the research analysis.
// ============================================================================

include <../microscope-slide-hyperobject/slide.scad>

// ---------------------------------------------------------------------------
// 1. Slide Standard Lookup (RESEARCH §2)
// ---------------------------------------------------------------------------
// Index: 0=ISO, 1=US, 2=Petrographic, 3=Supa Mega
// Each row: [length, width, thickness]
SLIDE_STANDARDS = [
  [76.0, 26.0, 1.0], // ISO 8037 standard
  [76.2, 25.4, 1.0], // US "3x1 inch"
  [46.0, 27.0, 1.2], // Petrographic (geology)
  [75.0, 50.0, 1.0], // Supa Mega (brain/prostate)
];

// Resolve effective slide dimensions from standard index + custom overrides
function resolve_slide(standard, custom_l, custom_w, custom_t) =
  standard < len(SLIDE_STANDARDS) ? SLIDE_STANDARDS[standard]
  : [custom_l, custom_w, custom_t];

// ---------------------------------------------------------------------------
// 2. Density / Pitch Lookup (RESEARCH §5.1.2, Table B)
// ---------------------------------------------------------------------------
// Index: 0=archival, 1=working, 2=staining, 3=mailer
// Each row: [rib_width_mm, description]
DENSITY_RIB_WIDTHS = [1.0, 1.5, 2.0, 3.0];

// Accessor function for use<> compatibility (use<> imports functions, not variables)
function density_rib_width(idx) = DENSITY_RIB_WIDTHS[idx];

// Compute slot width from slide thickness + tolerances + waviness
function slot_width(slide_thick, tol_z) = slide_slot_width(slide_thick, tol_z);

// Compute pitch (center-to-center distance between slides)
function pitch(slot_w, rib_w) = slide_pitch(slot_w, rib_w);

// ---------------------------------------------------------------------------
// 3. Slide Bounding Box (RESEARCH §8.2)
// ---------------------------------------------------------------------------
// Now inherited natively via `slide_bounding_box` from the CDG hyperobject.

// ---------------------------------------------------------------------------
// 4. Retention Rib — Tapered with Chamfered Lead-In (RESEARCH §5.1.1)
// ---------------------------------------------------------------------------
// A single rib separating two slide slots. Tapered profile is wider at the
// base (root) and narrower at the tip for a funnel effect during insertion.
// The top 1-2mm features a 45° chamfer to guide slides in.
//
// Profile (XZ cross-section, extruded along Y):
//
//       ╱tip_w╲       ← chamfer zone (45°)
//      │       │
//      │       │      ← main body
//     ╱         ╲
//    root_width        ← base
//
module retention_rib(height, depth, root_w, tip_w, chamfer_h) {
  slide_retention_rib(height, depth, root_w, tip_w, chamfer_h);
}

// Rectangular rib (simpler, for archival density)
module rectangular_rib(height, depth, width) {
  cube([width, depth, height]);
}

// ---------------------------------------------------------------------------
// 5. Slot Array (RESEARCH §8.2)
// ---------------------------------------------------------------------------
// Linear array of ribs along the X axis at the computed pitch.
// Uses additive (union) approach — cleaner for tapered ribs per RESEARCH §8.2.
module slot_array(count, pitch, height, depth, root_w, tip_w, chamfer_h, tapered) {
  slide_slot_array(count, pitch, height, depth, root_w, tip_w, chamfer_h, tapered);
}

// ---------------------------------------------------------------------------
// 6. Anti-Capillary Floor Ribs (RESEARCH §4.1)
// ---------------------------------------------------------------------------
// Two parallel rails at 25% and 75% of pocket width to break vacuum seal.
// Dimensions: 2.0mm wide, 0.5-1.0mm high per research.
module anti_capillary_ribs(pocket_length, pocket_width, rib_height = 0.5) {
  _rib_w = 2.0;
  _offset_25 = pocket_width * 0.25 - _rib_w / 2;
  _offset_75 = pocket_width * 0.75 - _rib_w / 2;

  // Rail at 25%
  translate([_offset_25, 0, 0])
    cube([_rib_w, pocket_length, rib_height]);

  // Rail at 75%
  translate([_offset_75, 0, 0])
    cube([_rib_w, pocket_length, rib_height]);
}

// ---------------------------------------------------------------------------
// 7. Finger Notch (RESEARCH §4.2)
// ---------------------------------------------------------------------------
// Cylindrical Boolean subtraction for ergonomic slide removal.
// Width 15-22mm per commercial holder research (Abdos, Globe Scientific).
// Depth extends below floor for finger pad access.
module finger_notch(radius, depth) {
  translate([0, 0, -depth / 2])
    cylinder(r=radius, h=depth + 1, $fn=32);
}

// ---------------------------------------------------------------------------
// 8.// Stacking Lip and Groove (RESEARCH §4.4)
// ---------------------------------------------------------------------------
// Perimeter ridge on top + groove on bottom for stable vertical stacking.
// Lip: 3mm high, 45° chamfer per research.
// FIXED: Chamfer limited to leave 1.0mm top width for printability.
module stacking_lip(outer_x, outer_y, lip_h = 3, lip_w = 1.5) {
  _min_top = 1.0;
  _chamfer_sz = max(0, lip_w - _min_top);

  difference() {
    // Outer ridge
    linear_extrude(height=lip_h)
      difference() {
        square([outer_x, outer_y]);
        offset(delta=-lip_w)
          square([outer_x, outer_y]);
      }

    // 45° outer chamfer
    if (_chamfer_sz > 0) {
      translate([0, 0, lip_h])
        rotate([0, 0, 0])
          linear_extrude(
            height=_chamfer_sz, scale=[
              (outer_x + 2 * _chamfer_sz) / outer_x,
              (outer_y + 2 * _chamfer_sz) / outer_y,
            ]
          )
            translate([-_chamfer_sz, -_chamfer_sz])
              square([outer_x + 2 * _chamfer_sz, outer_y + 2 * _chamfer_sz]);
    }
  }
}

// Groove (on bottom of part above) — slightly wider for clearance
module stacking_groove(outer_x, outer_y, groove_h = 3.2, groove_w = 1.7) {
  linear_extrude(height=groove_h)
    difference() {
      square([outer_x, outer_y]);
      offset(delta=-groove_w)
        square([outer_x, outer_y]);
    }
}

// ---------------------------------------------------------------------------
// 9. Label Recess (RESEARCH §8.3)
// ---------------------------------------------------------------------------
// Debossed flat area for handwritten or printed labels.
// Engraved 0.4mm deep per research (embossed interferes with insertion).
// FIXED: Added 45deg chamfer on top edge for AM-friendliness (no 90deg overhang).
module label_recess(width, height, depth = 0.4) {
  union() {
    cube([width, height, depth]);

    // Chamfer on the "top" edge (Y+ axis).
    // 45 deg triangle prism to ensure no 90 deg overhang on the ceiling.
    translate([0, height, 0])
      rotate([0, -90, 0]) // Rotate to align with X width
        rotate([0, 0, -90]) // Align profile
          linear_extrude(height=width)
            polygon([[0, 0], [depth, 0], [0, depth]]);
    // 45 deg triangle
  }
}

// ---------------------------------------------------------------------------
// 10. Snap-Fit Cantilever Latch (RESEARCH §5.3)
// ---------------------------------------------------------------------------
// Flexible arm on lid engages lip on base. For PLA, arm length >= 15mm
// to stay within yield stress limits.
//
// Hook profile (side view):
//    ┌──╮
//    │  │ ← hook
//    │  │
//    │  │ ← arm (flexible)
//    └──┘ ← anchor
//
module snap_latch_arm(arm_length, arm_width, arm_thick, hook_height, hook_depth) {
  // Arm
  cube([arm_width, arm_thick, arm_length]);

  // Hook at end
  translate([0, 0, arm_length])
    cube([arm_width, arm_thick + hook_depth, hook_height]);
}

// The catch (lip on the base that the hook grabs)
// FIXED: Added 45deg chamfer support below the catch.
module snap_latch_catch(width, height, depth) {
  union() {
    cube([width, depth, height]);
    // Support chamfer below, extending downwards from Z=0
    // Triangle with height=depth and depth=depth (45 deg)
    // Extruded along X (width)
    translate([0, depth, 0]) // Align with back of catch for rotation
      rotate([90, 0, 90]) // Rotate to place triangle under Z=0, sloping up to Y=depth?
        // Let's keep it simple:
        // Polygon in XZ plane: (0,0) -> (depth, 0) -> (depth, -depth) ?
        // Extruded along Y (width)? No width is X.

        // Using linear_extrude(height=width) suggests extrusion along Z before rotation.
        // We want uniform cross section along X (width).
        translate([0, 0, 0])
          rotate([0, 90, 0]) // Extrude becomes X.
            rotate([0, 0, 90]) // Rotate profile in YZ
              linear_extrude(height=width)
                polygon([[0, 0], [depth, 0], [depth, -depth]]);
    // Triangle in YZ plane
    // (0,0) is top-front?
    // The block is [0,0,0] to [width, depth, height].
    // We want support under [0,0,0]..[width, depth, 0].
    // We want a slope from Y=0, Z=-depth to Y=depth, Z=0?
    // Or from Y=0, Z=0 to Y=depth, Z=-depth?
    // Latch catch is on the side of the box.
    // We want the slope to be printable. The bottom needs to be safe.
    // If we print from Z=0 up.
    // This catch is high up on the box.
    // So we need a slope BELOW it connecting to the wall.
    // If the catch sticks out by `depth` from the wall.
    // We need a chamfer from the wall to the tip of the catch.
    // Wall is at Y=0? Or Y=depth? 
    // In box.scad, we position it.
    // Assuming it sticks out, we need support below.
    // So slope from (Y=0, Z=-depth) to (Y=depth, Z=0).
    // Polygon: [[0, -depth], [depth, 0], [0,0]] ?
    // Let's try:
    // polygon([[0,0], [depth,0], [0, -depth]])
  }

  // Revised implementation:
  // Support prism under the block.
  // Block: X=[0..width], Y=[0..depth], Z=[0..height]
  // Gradient should be along Y (from wall to tip).
  // Printable slope: 45 deg.
  // We need a prism X=[0..width], Y=[0..depth], Z=[-depth..0]
  // Shape: Triangle in YZ plane.
  // Vertices: (0,0), (depth,0), (0,-depth).
  // (0,0) connects to wall/bottom-front of block?
  // (depth,0) is tip of block bottom.
  // (0,-depth) is point on wall 45 deg down.
  // Yes.
  translate([0, 0, 0.01])
    rotate([0, 90, 0]) // Extrude along X+
      linear_extrude(height=width)
        polygon([[0, 0], [depth, 0], [0, depth]]);
}

// ---------------------------------------------------------------------------
// 11. Interlocking Stack Tab (RESEARCH §7.1)
// ---------------------------------------------------------------------------
// Trapezoidal dovetail for cabinet stacking stability.
// Male tab on top, female recess on bottom.
module stack_tab_male(base_w = 15, top_w = 10, height = 4, depth = 8) {
  _offset = (base_w - top_w) / 2;
  linear_extrude(height=depth)
    polygon(
      [
        [0, 0],
        [base_w, 0],
        [base_w - _offset, height],
        [_offset, height],
      ]
    );
}

module stack_tab_female(base_w = 15, top_w = 10, height = 4, depth = 8, tol = 0.4) {
  _bw = base_w + tol;
  _tw = top_w + tol;
  _h = height + tol / 2;
  _offset = (_bw - _tw) / 2;
  linear_extrude(height=depth + tol)
    polygon(
      [
        [0, 0],
        [_bw, 0],
        [_bw - _offset, _h],
        [_offset, _h],
      ]
    );
}

// ---------------------------------------------------------------------------
// 12. Drainage Slope (RESEARCH §6.1)
// ---------------------------------------------------------------------------
// Applies a drainage angle to horizontal surfaces for staining rack runoff.
module drainage_slope(length, width, height, angle) {
  _drop = length * tan(angle);
  polyhedron(
    points=[
      [0, 0, 0],
      [width, 0, 0],
      [width, length, 0],
      [0, length, 0],
      [0, 0, height],
      [width, 0, height],
      [width, length, height - _drop],
      [0, length, height - _drop],
    ],
    faces=[
      [0, 1, 2, 3], // bottom
      [7, 6, 5, 4], // top
      [0, 4, 5, 1], // front
      [2, 6, 7, 3], // back
      [0, 3, 7, 4], // left
      [1, 5, 6, 2], // right
    ]
  );
}
