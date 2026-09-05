include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters — defaults are project.json's declared defaults.
// face_pattern used to default to "prismatic" (which is not one of the
// manifest's options at all) and the jaw height was hard-coded at 1.25 in
// rather than taking the manifest's 1.735 in. Rendering this mode with no
// parameters therefore produced a 31.75 mm-tall jaw carrying a full-width
// V-rib in OpenSCAD against a plain 44.069 mm-tall blank in CadQuery.
jaw_width_inch = 6;          // project.json jaw_width, default 6.0 in
jaw_height_inch = 1.735;     // project.json jaw_height, default 1.735 in
jaw_thickness_inch = 0.75;   // project.json jaw_thickness, default 0.75 in
face_pattern = "smooth";     // project.json face_pattern, default "smooth"
magnet_holes = true;         // project.json magnet_pockets, default true

// CDG Constants (Kurt 6")
JAW_HEIGHT = jaw_height_inch * 25.4;
JAW_THICKNESS = jaw_thickness_inch * 25.4;
BOLT_SPACING = 3.875 * 25.4; // Varies by model, using standard spacing
BOLT_HEAD_D = 14; 
BOLT_SHAFT_D = 9;

module soft_jaw() {
    width_mm = jaw_width_inch * 25.4;
    
    diff()
    cuboid([width_mm, JAW_THICKNESS, JAW_HEIGHT], anchor=BACK) {
        
        // Face Pattern logic
        attach(FWD)
        if (face_pattern == "prismatic") {
            // V-grooves for round stock
            zrot(90)
            linear_extrude(width_mm)
            polygon([[-5,0], [0,5], [5,0]]);
        } else if (face_pattern == "grid") {
            // Knurling pattern
           grid_2d(spacing=5, size=[width_mm, JAW_HEIGHT])
           pyramid(h=1, size=[5,5], anchor=BOTTOM);
        }
        
        // Mounting Holes (Counterbored)
        tag("remove")
        attach(BACK)
        left(BOLT_SPACING/2)
        rotate([90,0,0])
        cylinder(h=JAW_THICKNESS+1, d1=BOLT_HEAD_D, d2=BOLT_SHAFT_D, $fn=32);
        
        tag("remove")
        attach(BACK)
        right(BOLT_SPACING/2)
        rotate([90,0,0])
        cylinder(h=JAW_THICKNESS+1, d1=BOLT_HEAD_D, d2=BOLT_SHAFT_D, $fn=32);
        
        // Magnet Pockets.
        //
        // These used to be `attach(BACK) up(...)` / `down(...)`. Inside an
        // attach() the up/down offsets move along the ATTACH frame's own axis,
        // which points into the jaw -- not along Z as intended. Both pockets
        // therefore landed buried at y = -14.69..-11.69 inside a jaw spanning
        // y = -19.05..0: a fully enclosed void, so jaw_body rendered a
        // negative-volume body on every variant.
        //
        // `position(BACK)` places the child on the back face without adopting
        // an attach frame, so up/down move along Z as intended and an explicit
        // rotate drives the bore into the jaw. h is 3.5 rather than 3 so the
        // pocket breaks the face instead of kissing it.
        if (magnet_holes) {
            tag("remove")
            position(BACK)
            up(JAW_HEIGHT/3)
            rotate([90, 0, 0])
            cylinder(h=3.5, d=10.2, $fn=32); // 10mm magnet

            tag("remove")
            position(BACK)
            down(JAW_HEIGHT/3)
            rotate([90, 0, 0])
            cylinder(h=3.5, d=10.2, $fn=32);
        }
    }
}

soft_jaw();
