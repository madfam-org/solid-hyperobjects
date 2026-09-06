// Yantra4D wrapper — Text Plaque
// Rectangular base with raised or inset text

message = "Hello";
font_size = 12;
text_depth = 1.5;
base_width = 80;
base_height = 40;
base_thickness = 3;
raised = true;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 32;

// Font and clip.
//
// Neither kernel used to name a font, so each took its own default and the two
// typefaces set the same string at the same nominal size to different widths.
// That is this cartridge's entire parity gap: at preset name_plaque
// ("Your Name" at size 12 on an 80 mm plate) OpenSCAD's default face runs
// 81.656 mm and overhangs the plate by 0.83 mm at each end, against a
// CadQuery run that fits -- a 1.656 mm bounding-box difference on plaque,
// sign and tag alike. door_sign's 2.80% volume gap is the same cause measured
// on glyph AREA at equal depth.
//
// Naming the font on both sides removes the substitution. The clip below then
// makes the bound STRUCTURAL rather than font-dependent: raised text is
// intersected with the plate footprint, so no `message` within the
// parameter's 30-character budget can push the bounding box past base_width
// on either kernel, whichever face the render image happens to resolve. A cut
// can never grow the box, so the engraved branch needs the font only.
FONT = "Liberation Sans";


if (raised) {
    // Raised text: base + extruded text on top, clipped to the plate.
    union() {
        cube([base_width, base_height, base_thickness]);
        intersection() {
            translate([base_width / 2, base_height / 2, base_thickness])
                linear_extrude(text_depth)
                    text(message, size = font_size, font = FONT,
                         halign = "center", valign = "center");
            translate([0, 0, base_thickness])
                cube([base_width, base_height, text_depth]);
        }
    }
} else {
    // Inset text: base with text carved in
    difference() {
        cube([base_width, base_height, base_thickness]);
        translate([base_width / 2, base_height / 2, base_thickness - text_depth])
            linear_extrude(text_depth + 0.1)
                text(message, size = font_size, font = FONT,
                     halign = "center", valign = "center");
    }
}
