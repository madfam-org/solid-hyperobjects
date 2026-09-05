// =============================================================================
// commons-lib/scad_core.scad — CDG helper modules for the solid commons
// =============================================================================
//
// Original author:  Innovaciones MADFAM
// Originally published under AGPL-3.0 in madfam-org/yantra4d as
//                   libs/scad_core/core.scad and libs/yantra4d/cdg_interfaces.scad.
// Relicensed by the rights holder (Innovaciones MADFAM) under CERN-OHL-W-2.0
//                   on 2026-09-05, per operator ruling G11.
// SPDX-License-Identifier: CERN-OHL-W-2.0
//
// Why this file exists: `fasteners` and `framing-hyperobject` used to reach
// OUTSIDE this repository at render time, for AGPL-3.0 platform code that is
// not part of the commons and does not resolve in this layout. Ruling G11
// relicenses exactly the helpers those two cartridges call, so a CERN-OHL-W-2.0
// commons is self-contained.
//
// Scope: ONLY the modules the two cartridges actually invoke. Nothing else from
// the platform libraries is vendored here.
//   y4d_standard_thread  — fasteners/bolt.scad
//   y4d_vesa_pattern     — framing-hyperobject/framing.scad  (with vesa_spec)
//   y4d_standoff_set     — framing-hyperobject/framing.scad  (with y4d_standoff_barrel)
//   y4d_french_cleat     — framing-hyperobject/framing.scad
//
// Resolved through OPENSCADPATH, so this file is included as
// `include <commons-lib/scad_core.scad>` and the repository ROOT (the directory
// that CONTAINS commons-lib/) must be on OPENSCADPATH.
// =============================================================================

include <BOSL2/std.scad>
include <BOSL2/threading.scad>

// --- Threads -----------------------------------------------------------------
// A standard wrapper around BOSL2's threading to enforce Yantra4D defaults.
module y4d_standard_thread(d, p, l, internal = false, anchor = CENTER) {
  if (internal) {
    threaded_nut(nutwidth=d + 5, id=d, h=l, pitch=p, ibevel=true, $fa=2, $fs=0.5, anchor=anchor);
  } else {
    threaded_rod(d=d, l=l, pitch=p, end_len1=0, end_len2=0, internal=false, $fa=2, $fs=0.5, anchor=anchor);
  }
}

// --- VESA standards ----------------------------------------------------------
function vesa_spec(standard) =
  (standard == "MIS-D 75") ? [75, 75, 4]
  : (standard == "MIS-D 100") ? [100, 100, 4]
  : (standard == "MIS-E") ? [200, 100, 4]
  : [100, 100, 4]; // Default

module y4d_vesa_pattern(standard = "MIS-D 100", center = true) {
  spec = vesa_spec(standard);
  sx = spec[0];
  sy = spec[1];
  d = spec[2];

  translate(center ? [-sx / 2, -sy / 2, 0] : [0, 0, 0]) {
    circle(d=d);
    translate([sx, 0, 0]) circle(d=d);
    translate([0, sy, 0]) circle(d=d);
    translate([sx, sy, 0]) circle(d=d);
  }
}

// --- French cleat ------------------------------------------------------------
// The four-point profile from cdg_interfaces.scad. core.scad carried a
// five-point variant whose last point repeated the first; cdg_interfaces.scad's
// definition shadowed it wherever both were included, so the four-point form is
// the one framing-hyperobject has always rendered.
module y4d_french_cleat(length = 100, height = 30, depth = 15, angle = 45) {
  polygon_points = [
    [0, 0],
    [depth, 0],
    [depth, height],
    [depth - (height * tan(angle)), height],
  ];
  translate([-length / 2, -height / 2, 0])
    rotate([90, 0, 90])
      linear_extrude(height=length) {
        polygon(points=polygon_points);
      }
}

// --- Standoffs ---------------------------------------------------------------
module y4d_standoff_barrel(h = 20, d = 12, thread_d = 4) {
  difference() {
    cylinder(h=h, d=d);
    translate([0, 0, -1]) cylinder(h=h + 2, d=thread_d);
  }
}

module y4d_standoff_set(spacing_x = 100, spacing_y = 100, h = 25) {
  sx = spacing_x / 2;
  sy = spacing_y / 2;
  translate([-sx, -sy, 0]) y4d_standoff_barrel(h=h);
  translate([sx, -sy, 0]) y4d_standoff_barrel(h=h);
  translate([-sx, sy, 0]) y4d_standoff_barrel(h=h);
  translate([sx, sy, 0]) y4d_standoff_barrel(h=h);
}
