include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
// These names must match project.json, and socket.py, exactly. They used to be
// upper_circumference_mm / lower_circumference_mm / socket_length_mm, which the
// manifest never declares, so the render harness — which only forwards
// parameters a .scad actually declares — passed none of them and this file
// silently used its own defaults of 320/240/250 while socket.py built from the
// manifest's 350/250/300. The two engines were modelling different sockets:
// 251 mm against 300 mm tall, and 161% apart by volume.
circumference_top = 350;
circumference_bottom = 250;
length = 300;
voronoi_density = 10;
wall_thickness = 4;

// Internal Calcs
r_upper = circumference_top / (2 * PI);
r_lower = circumference_bottom / (2 * PI);
distal_interface_d = 50; // Standard distal cap

module voronoi_pattern(r, h, density) {
    // Simplified Voronoi-like pattern using spheres
    // Real Voronoi on curved surface is hard in pure SCAD without heavy comp.
    // Approximating with random spherical cutouts.
    
    // We use a deterministic seed relative to input params to keep it consistent
    seed_base = r * h;
    
    for (i=[0:density*2]) {
        z = rands(20, h-20, 1, i)[0];
        ang = rands(0, 360, 1, i+seed_base)[0];
        rad = rands(5, 15, 1, i+seed_base*2)[0];
        
        up(z)
        rotate([0, 0, ang])
        right(r) // Push to surface
        sphere(r=rad);
    }
}

module socket_shell() {
    
    difference() {
        // Outer Shell
        hull() {
            cylinder(h=1, r=r_lower + wall_thickness, $fn=64);
            up(length)
            cylinder(h=1, r=r_upper + wall_thickness, $fn=64);
        }
        
        // Inner Cavity
        hull() {
            up(wall_thickness)
            cylinder(h=1, r=r_lower, $fn=64);
            up(length + 1)
            cylinder(h=1, r=r_upper, $fn=64);
        }
        
        // Voronoi Ventilation
        // Apply pattern to the tapered surface
        // We approximate the surface at mid-radius for subtraction
        r_mid = (r_upper + r_lower) / 2;
        voronoi_pattern(r_mid + wall_thickness, length, voronoi_density);
        
        // Distal Hardware Mounting Holes
        down(1)
        cylinder(h=10, d=6, $fn=32); // Central bolt
        
        for(a=[0:90:360]) {
             rotate([0,0,a])
             right(15)
             down(1)
             cylinder(h=10, d=4, $fn=32); // Mounting pattern 4xM4
        }
    }
}

socket_shell();
