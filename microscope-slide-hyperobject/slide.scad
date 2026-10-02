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
