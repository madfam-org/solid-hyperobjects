// Parametric Compliant Bistable Locking Mechanism — Engineered for AM
// Yantra4D — Locking Mechanism Hyperobject
include <BOSL2/std.scad>

// Yantra4D Parameters
latch_width = 15;
wall_thickness = 2;
base_length = 40;
hook_depth = 2;
clearance = 0.3;
fn = 0;
cdg_mount_type = 0;
material_modulus = 1.5;
shrinkage_factor = 0.0;

$fn = fn > 0 ? fn : $preview ? 32 : 64;

// Mechanics for Elastomeric/PP/PETG Printing
modulus_modifier = pow(1.5 / max(material_modulus, 0.05), 0.3);
hinge_t = 0.8 * modulus_modifier; 
hinge_l = 1.5;

module apply_cdg(base_x) {
    if (cdg_mount_type == 1) { // M3 Hex Nut Trap
        difference() {
            union() {
                children();
                translate([-base_x/2 - 8, 0, 0]) cuboid([16, 15, 5], anchor=BOTTOM);
                translate([base_x/2 + 8, 0, 0]) cuboid([16, 15, 5], anchor=BOTTOM);
            }
            translate([-base_x/2 - 8, 0, 0]) cyl(d=3.4, h=15);
            translate([-base_x/2 - 8, 0, 2]) cyl(d=6.2, h=10, $fn=6);
            translate([base_x/2 + 8, 0, 0]) cyl(d=3.4, h=15);
            translate([base_x/2 + 8, 0, 2]) cyl(d=6.2, h=10, $fn=6);
        }
    } else if (cdg_mount_type == 2) { // Gridfinity 42mm
        union() {
            children();
            translate([0, 0, -4.5]) prismoid(size1=[41.5, 41.5], size2=[42, 42], h=4.5, anchor=BOTTOM);
        }
    } else {
        children();
    }
}

module rigid_frame() {
    base_h = wall_thickness * 3;
    difference() {
        apply_cdg(base_length) {
            cuboid([base_length, latch_width, base_h], anchor=BOTTOM);
        }
        translate([0, 0, wall_thickness])
        cuboid([base_length - wall_thickness*2, latch_width+1, base_h], anchor=BOTTOM);
    }
    arch_len = base_length - wall_thickness*2 - hinge_l*2;
    arch_h = arch_len * 0.15;
    stop_h = (base_h/2) - arch_h*0.5; 
    translate([0, 0, wall_thickness])
    cuboid([wall_thickness*3, latch_width, max(0.5, stop_h)], anchor=BOTTOM);
}

module flex_spline() {
    base_h = wall_thickness * 3;
    arch_len = base_length - wall_thickness*2 - hinge_l*2;
    arch_h = arch_len * 0.15;
    
    translate([-arch_len/2 - hinge_l/2, 0, base_h/2])
    cuboid([hinge_l, latch_width, hinge_t], anchor=CENTER);
    
    translate([arch_len/2 + hinge_l/2, 0, base_h/2])
    cuboid([hinge_l, latch_width, hinge_t], anchor=CENTER);
    
    // The arch is ONE sampled ribbon on both kernels. This used to be a hull()
    // chain of 40 axis-aligned cuboids: hulling boxes across a slope sweeps
    // extra material at every joint, so it can never match compliant_lock.py's
    // sampled profile (74.62 mm3 of the 92.62 mm3 spring_t1 parity gap, and the
    // chain's own step count changes the answer). Build the same closed polygon
    // the CadQuery side builds — centreline offset below and above by
    // wall_thickness*0.3, walked back along the top to close — at the same 10
    // samples, then linear_extrude it to latch_width.
    steps = 10;
    arch_lo = [for(i=[0:steps]) let(t = i/steps)
        [-arch_len/2 + arch_len*t, base_h/2 + arch_h*sin(t*180) - wall_thickness*0.3]];
    arch_hi = [for(i=[steps:-1:0]) let(t = i/steps)
        [-arch_len/2 + arch_len*t, base_h/2 + arch_h*sin(t*180) + wall_thickness*0.3]];
    rotate([90, 0, 0])
    linear_extrude(height=latch_width, center=true)
    polygon(concat(arch_lo, arch_hi));
    
    translate([0, 0, base_h/2 + arch_h])
    union() {
        cuboid([wall_thickness*2, latch_width*0.6, wall_thickness*1.5], anchor=BOTTOM);
        // The hook is the SAME triangular prism on both kernels. A prismoid
        // tapering to a full-width rectangle is a frustum, not a wedge, and
        // carried 18 mm3 more than compliant_lock.py's three-point profile.
        translate([0, 0, wall_thickness*1.5])
        rotate([90, 0, 0])
        linear_extrude(height=latch_width*0.6, center=true)
        polygon([[-wall_thickness, 0],
                 [-wall_thickness + wall_thickness/2, hook_depth],
                 [wall_thickness, 0]]);
    }
}

render_mode = 0;

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {
    if (render_mode == 0) { rigid_frame(); }
    else if (render_mode == 1) { flex_spline(); }
    else if (render_mode == 2) { rigid_frame(); color("orange") flex_spline(); }
}
