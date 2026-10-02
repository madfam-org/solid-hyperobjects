// ----------------------------------------------------
// Fit and scale compensation (explicit geometry inputs)
// ----------------------------------------------------
// scale_comp_x/y/z: unitless scale factors applied to the slide body
// (1.0 = none). Manifest parameters of microscope-slide-hyperobject.
scale_comp_x = 1.0;
scale_comp_y = 1.0;
scale_comp_z = 1.0;
// fit_clearance_slide: extra slot clearance in mm that slide_slot_width()
// adds for a sliding fit (0 = none). A library input: microscope-slide-holder
// declares it; microscope-slide-hyperobject renders no slot, so it does not.
fit_clearance_slide = 0.0;

// LEGACY material injection. REMOVE AT THE FLIP of the yantra4d flag
// RENDER_MATERIAL_INJECTION (owner ruling "flag now, flip later").
// While that flag is on, a render request naming target_material makes the
// platform pass the material card's mat_shrinkage_x/y/z and mat_clear_slide
// with -D. They are undef unless injected, and an injected value WINS over
// the explicit parameter above, so a render with the flag on is unchanged.
// At the flip, delete these four assignments and _legacy_or() and read the
// explicit parameters directly. mat_clear_press and mat_clear_loose were
// declared here but never read, so they are no longer declared.
mat_shrinkage_x = undef;
mat_shrinkage_y = undef;
mat_shrinkage_z = undef;
mat_clear_slide = undef;
function _legacy_or(legacy, explicit) = is_undef(legacy) ? explicit : legacy;

// Standard Microscope Slide Dimensions (ISO 8037)
function slide_slot_width(thickness, tolerance) =
  thickness + tolerance + _legacy_or(mat_clear_slide, fit_clearance_slide) + 0.1;
function slide_pitch(slot_w, rib_w) = slot_w + rib_w;

module slide_retention_rib(height, depth, root_w, tip_w, chamfer_h) {
  // ONE polyhedron, not a cube unioned with a chamfer cap.
  //
  // The rib used to be `cube([root_w, depth, height - chamfer_h])` unioned with
  // a polyhedron frustum that started at exactly z = height - chamfer_h. That
  // is a zero-overlap coincident-face union: the two solids share an exact
  // plane and touch on it rather than interpenetrating. CGAL resolves it, but
  // OpenSCAD's Manifold backend -- which is what the platform and
  // `y4d-spec check --render` both use -- snaps near-coincident vertices and
  // tears the pair apart at that plane. Three or more ribs in one array was
  // enough: a 4-rib array came out as 8 shells, not watertight, and a 20-slot
  // box_base as 119 bodies with 26 of them negative.
  //
  // Written as a single closed polyhedron there is no interface plane at all,
  // so there is nothing to tear. Faces are wound CLOCKWISE seen from outside,
  // which is what OpenSCAD wants (the opposite of a CadQuery Shell); wound the
  // other way it renders NoError but inside-out.
  //
  // Volume and extents are unchanged to 3 decimal places; only the redundant
  // interface faces go away (28 -> 20 facets per rib).
  _ch = min(chamfer_h, height);
  _bz = height - _ch;
  _lo = (root_w - tip_w) / 2;
  _hi = (root_w + tip_w) / 2;
  polyhedron(
    points=[
      // 0-3: base, z = 0
      [0, 0, 0], [root_w, 0, 0], [root_w, depth, 0], [0, depth, 0],
      // 4-7: chamfer start, z = height - chamfer_h
      [0, 0, _bz], [root_w, 0, _bz], [root_w, depth, _bz], [0, depth, _bz],
      // 8-11: tip, z = height
      [_lo, 0, height], [_hi, 0, height], [_hi, depth, height], [_lo, depth, height],
    ],
    faces=[
      [0, 1, 2, 3],                                        // base
      [11, 10, 9, 8],                                      // tip (opposite base winding)
      [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0],       // prism sides
      [4, 8, 9, 5], [5, 9, 10, 6], [6, 10, 11, 7], [7, 11, 8, 4],   // chamfer sides
    ]
  );
}

module slide_slot_array(count, pitch, height, depth, root_w, tip_w, chamfer_h, tapered) {
  for (i = [0:count]) {
    translate([i * pitch, 0, 0])
      slide_retention_rib(height, depth, root_w, tip_w, chamfer_h);
  }
}

// ----------------------------------------------------
// ISO 8037-1 Bounded 4D Geometry
// ----------------------------------------------------

module iso_8037_slide(length, width, thickness) {
  // A standard microscope slide volumetric cartridge.
  // Glass usually has polished or ground edges.
  cube([length, width, thickness], center=true);
}

// ----------------------------------------------------
// Cartridge Execution Logic (Triggered by Manifest)
// ----------------------------------------------------

slide_standard = 0; // [0:ISO 8037-1 Primary, 1:ISO 8037-1 Alternate, 2:ISO 8255 #1.5H Cover, 3:ISO 8255 #1 Cover, 4:Custom]
custom_slide_length = 76.0;
custom_slide_width = 26.0;
custom_slide_thickness = 1.0;

render_mode = 0; // [0:main]

if (render_mode == 0) {
  // Material simulation logic for transparency via OpenSCAD nightly alpha
  color([0.8, 0.9, 0.9, 0.4]) {
    // Scale compensation: the explicit scale_comp_* parameters, or the legacy
    // injected mat_shrinkage_* while the platform still injects them.
    scale([_legacy_or(mat_shrinkage_x, scale_comp_x),
           _legacy_or(mat_shrinkage_y, scale_comp_y),
           _legacy_or(mat_shrinkage_z, scale_comp_z)]) {
      if (slide_standard == 0) {
        // ISO 8037-1 Primary
        iso_8037_slide(76.0, 26.0, 1.0);
      } else if (slide_standard == 1) {
        // ISO 8037-1 Alternate
        iso_8037_slide(75.0, 25.0, 1.0);
      } else if (slide_standard == 2) {
        // ISO 8255 #1.5H Cover Glass
        iso_8037_slide(22.0, 22.0, 0.17);
      } else if (slide_standard == 3) {
        // ISO 8255 #1 Cover Glass
        iso_8037_slide(22.0, 22.0, 0.15);
      } else if (slide_standard == 4) {
        // Custom Geometry
        iso_8037_slide(custom_slide_length, custom_slide_width, custom_slide_thickness);
      }
    }
  }
}
