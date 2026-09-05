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
  union() {
    cube([root_w, depth, height - chamfer_h]);
    translate([0, 0, height - chamfer_h])
      polyhedron(
        points=[
          [0, 0, 0],
          [root_w, 0, 0],
          [root_w, depth, 0],
          [0, depth, 0],
          [(root_w - tip_w) / 2, 0, chamfer_h],
          [(root_w + tip_w) / 2, 0, chamfer_h],
          [(root_w + tip_w) / 2, depth, chamfer_h],
          [(root_w - tip_w) / 2, depth, chamfer_h],
        ],
        faces=[
          [0, 1, 2, 3],
          [4, 5, 6, 7],
          [0, 4, 7, 3],
          [1, 5, 6, 2],
          [0, 1, 5, 4],
          [3, 2, 6, 7],
        ]
      );
  }
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
