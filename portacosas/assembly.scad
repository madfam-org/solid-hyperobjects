// Assembly — Portacosas
// Each declared part rendered in its ASSEMBLED position on the tray.
// render_mode: 0=tray_base, 1=pen_holder, 2=phone_stand,
//              3=card_slot, 4=cable_clip, 5=label_plate
//
// The platform renders one part at a time, dispatched by render_mode/target_part
// (hyperobjects-spec rules.render_targets: "a mode listing three parts is three
// renders"). This file previously drew every component unconditionally, so all six
// declared parts rendered the identical six-component scene. Two consequences the
// render sweep caught:
//
//   1. Every part's mesh was the same scene, so no part was actually its own body.
//   2. The components' hardcoded tray placements INTERSECT each other at every
//      parameter point — at the defaults the card slot (x 55..145) runs through the
//      pen holder (x 7..79) and caps pen bores 3 and 4, which then export as sealed
//      voids: the -476.1203 and -952.2404 mm3 inverted shells CI reported. The same
//      collision recurs, with different numbers, at all five presets.
//
// Rendering one part per render removes both: a part is its own solid, and two
// components are never in the same mesh to intersect. `use` (not `include`) keeps
// desk_organizer.scad's own top-level selector from firing and drawing a second,
// stray tray_base at the origin.
//
// Placement is unchanged from the original layout — this file positions, it does
// not resize. Parameter ids, ranges, defaults and presets are all untouched.

use <desk_organizer.scad>

// --- Parameters (mirrored from desk_organizer.scad; -D still overrides) ---
render_mode = 0;

tray_width = 200;
tray_depth = 120;
wall_height = 80;
wall_thickness = 2.0;

pen_count = 5;
pen_diameter = 12;
pen_style = false;

phone_width = 75;
phone_angle = 65;
charging_slot = true;

card_width = 90;
card_depth = 60;
card_angle = 10;

clip_count = 2;
clip_diameter = 6;

label_text = "YANTRA4D";
label_depth = 0.5;

rows = 1;
cols = 1;

$fn = 48;

// --- Derived (mirrored) ---
base_h = wall_thickness;
pen_holder_d = pen_diameter + wall_thickness * 2;

// `use` does not import variables, so every call passes the parameters the
// component needs explicitly. desk_organizer.scad's modules take them as
// arguments defaulting to its own globals, so a plain call still works there.
module _tray_base() {
    tray_base(tray_width=tray_width, tray_depth=tray_depth,
              wall_thickness=wall_thickness, clip_count=clip_count);
}

module _pen_holder() {
    translate([wall_thickness + 5, (tray_depth - pen_holder_d) / 2, base_h])
        pen_holder(pen_count=pen_count, pen_diameter=pen_diameter,
                   pen_style=pen_style, wall_thickness=wall_thickness,
                   wall_height=wall_height);
}

module _phone_stand() {
    translate([tray_width - wall_thickness - phone_width - 5,
               (tray_depth - 40 - wall_thickness) / 2, base_h])
        phone_stand(phone_width=phone_width, wall_height=wall_height,
                    wall_thickness=wall_thickness, charging_slot=charging_slot);
}

module _card_slot() {
    translate([(tray_width - card_width) / 2, wall_thickness + 2, base_h])
        card_slot(card_width=card_width, card_depth=card_depth,
                  wall_height=wall_height, wall_thickness=wall_thickness);
}

// The mode declares part_quantities.cable_clip = clip_count, so this part is
// clip_count bodies by design — the clips print as separate pieces. The manifest
// declares that count; see verification.mode_overrides.
module _cable_clips() {
    for (i = [0 : clip_count - 1]) {
        cx = wall_thickness + 20 + i * (tray_width - 40) / max(clip_count - 1, 1);
        translate([cx, tray_depth - wall_thickness - 15, base_h])
            cable_clip(clip_diameter=clip_diameter, wall_thickness=wall_thickness);
    }
}

module _label_plate() {
    translate([(tray_width - tray_width * 0.4) / 2, 0, base_h + 4])
        label_plate(tray_width=tray_width, wall_thickness=wall_thickness,
                    label_text=label_text, label_depth=label_depth);
}

// --- Render mode dispatch: one branch per declared part ---
if (render_mode == 0) {
    _tray_base();
} else if (render_mode == 1) {
    _pen_holder();
} else if (render_mode == 2) {
    _phone_stand();
} else if (render_mode == 3) {
    _card_slot();
} else if (render_mode == 4) {
    _cable_clips();
} else if (render_mode == 5) {
    _label_plate();
}
