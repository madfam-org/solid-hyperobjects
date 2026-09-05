include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
mount_width = 40;
bolt_spacing = 20;
bolt_size = 1; // 0=M3, 1=M4, 2=M5

// CDG Constants (TS35)
RAIL_WIDTH = 35;
RAIL_DEPTH = 7.5;
LIP_THICKNESS = 1.0;

module din_clip() {
    bolt_d = (bolt_size == 0) ? 3.2 : ((bolt_size == 1) ? 4.2 : 5.2);
    
    diff()
    cuboid([mount_width, RAIL_WIDTH + 10, 8], anchor=BOTTOM) {
        // DIN Rail Cutout.
        // position(), not attach(): attach(BOTTOM) also REORIENTS the child so
        // its +Z points out of the bottom face, so the prismoid grew downwards
        // out of the body and the diff() removed only the 0.1 mm sliver that
        // down(0.1) pushed back inside. The clip rendered as a solid block with
        // no rail channel at all — 14160 mm^3 against clip.py's 4370 mm^3.
        // position() places the child at the same anchor point without rotating
        // it, so the prismoid runs upwards from z = -0.1 to z = RAIL_DEPTH - 0.1
        // with its wide face at the opening, exactly as clip.py cuts it.
        tag("remove")
        position(BOTTOM)
        down(0.1)
        prismoid([mount_width, RAIL_WIDTH + 0.5], [mount_width, RAIL_WIDTH - 2], h=RAIL_DEPTH, anchor=BOTTOM);
        
        // Locking Lip (Fixed Top)
        tag("keep")
        position(TOP+BACK)
        down(2)
        prismoid([mount_width, 3], [mount_width, 1], h=3, anchor=TOP+BACK);
        
        // Spring Lip (Flexible Bottom)
        tag("keep")
        position(TOP+FWD)
        down(2)
        prismoid([mount_width, 3], [mount_width, 1], h=3, anchor=TOP+FWD);

        // Mounting Holes
        tag("remove") {
            attach(TOP)
            left(bolt_spacing/2)
            cylinder(h=20, d=bolt_d, center=true, $fn=32);
            
            attach(TOP)
            right(bolt_spacing/2)
            cylinder(h=20, d=bolt_d, center=true, $fn=32);
        }
    }
}

din_clip();
