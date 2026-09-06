// Yantra4D wrapper — Sign with Border
// Larger plate with decorative border frame and text

message = "Hello";
font_size = 12;
text_depth = 1.5;
base_width = 80;
base_height = 40;
base_thickness = 3;
raised = true;
border_width = 2;
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


module sign_base() {
    cube([base_width, base_height, base_thickness]);
}

module border_frame() {
    // Raised border around the edge
    difference() {
        cube([base_width, base_height, text_depth]);
        translate([border_width, border_width, -0.1])
            cube([base_width - border_width * 2,
                  base_height - border_width * 2,
                  text_depth + 0.2]);
    }
}

if (raised) {
    union() {
        sign_base();
        // Border frame on top
        translate([0, 0, base_thickness])
            border_frame();
        // Raised text, clipped to the INNER window rather than the outer
        // plate, so it can neither overhang the sign nor fuse into the frame.
        intersection() {
            translate([base_width / 2, base_height / 2, base_thickness])
                linear_extrude(text_depth)
                    text(message, size = font_size, font = FONT,
                         halign = "center", valign = "center");
            translate([border_width, border_width, base_thickness])
                cube([base_width - border_width * 2,
                      base_height - border_width * 2,
                      text_depth]);
        }
    }
} else {
    difference() {
        union() {
            sign_base();
            // Border frame on top
            translate([0, 0, base_thickness])
                border_frame();
        }
        // Inset text
        translate([base_width / 2, base_height / 2, base_thickness - text_depth])
            linear_extrude(text_depth + 0.1)
                text(message, size = font_size, font = FONT,
                     halign = "center", valign = "center");
    }
}
