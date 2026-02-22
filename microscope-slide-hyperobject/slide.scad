// Standard Microscope Slide Dimensions (ISO 8037)
function slide_slot_width(thickness, tolerance) = thickness + tolerance + 0.1;
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
