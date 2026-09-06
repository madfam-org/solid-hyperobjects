// ----------------------------------------------------
// Material Hyperobject Compensations
// (Passed dynamically by the Commons API)
// ----------------------------------------------------
mat_shrinkage_x = 1.0;
mat_shrinkage_y = 1.0;
mat_shrinkage_z = 1.0;

mat_clear_press = 0.0;
mat_clear_slide = 0.0;
mat_clear_loose = 0.0;

// Standard Microscope Slide Dimensions (ISO 8037)
function slide_slot_width(thickness, tolerance) = thickness + tolerance + mat_clear_slide + 0.1;
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
      [8, 9, 10, 11],                                      // tip
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
    // Apply Material Hyperobject Shrinkage Compensation
    scale([mat_shrinkage_x, mat_shrinkage_y, mat_shrinkage_z]) {
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
