// Yantra4D wrapper — Gift Tag
// Rounded rectangle with hanging hole and text

message = "Hello";
font_size = 12;
text_depth = 1.5;
base_width = 80;
base_height = 40;
base_thickness = 3;
raised = true;
hole_diameter = 4;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 32;

// Font and clip -- see plaque.scad for the full rationale. In short: neither
// kernel named a font, so each resolved its own default face and the two set
// the same string at the same nominal size to different widths (1.656 mm of
// bounding box at name_plaque, 2.80% of volume at door_sign). Name the font on
// both sides, and clip raised text to the plate so the bounding box can never
// grow with the string.
FONT = "Liberation Sans";


corner_r = 4;
hole_r = hole_diameter / 2;
hole_x = base_width - corner_r - hole_r - 2;
hole_y = base_height - corner_r - hole_r - 2;

module rounded_rect(w, h, r) {
    hull() {
        translate([r, r]) circle(r);
        translate([w - r, r]) circle(r);
        translate([r, h - r]) circle(r);
        translate([w - r, h - r]) circle(r);
    }
}

module tag_base() {
    difference() {
        linear_extrude(base_thickness)
            rounded_rect(base_width, base_height, corner_r);
        // Hanging hole
        translate([hole_x, hole_y, -0.5])
            cylinder(h = base_thickness + 1, r = hole_r);
    }
}

if (raised) {
    union() {
        tag_base();
        // Raised text, clipped to the tag's own ROUNDED outline (not a plain
        // rect) so the text is bounded by the same silhouette the plate has.
        intersection() {
            translate([base_width / 2, base_height / 2, base_thickness])
                linear_extrude(text_depth)
                    text(message, size = font_size, font = FONT,
                         halign = "center", valign = "center");
            translate([0, 0, base_thickness])
                linear_extrude(text_depth)
                    rounded_rect(base_width, base_height, corner_r);
        }
    }
} else {
    difference() {
        tag_base();
        translate([base_width / 2, base_height / 2, base_thickness - text_depth])
            linear_extrude(text_depth + 0.1)
                text(message, size = font_size, font = FONT,
                     halign = "center", valign = "center");
    }
}
