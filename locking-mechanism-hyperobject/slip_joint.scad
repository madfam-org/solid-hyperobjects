// Slip Joint Monolithic Spring Check
include <../../libs/BOSL2/std.scad>

latch_width = 15;
material_modulus = 1.5;
shrinkage_factor = 0.0;
clearance = 0.3;
fn = 0;
cdg_mount_type = 0;
$fn = fn > 0 ? fn : $preview ? 32 : 64;

modulus_modifier = pow(1.5 / max(material_modulus, 0.05), 0.3);
hinge_t = 2.5 * modulus_modifier;
pin_d = 4;

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

module rigid_housing() {
    difference() {
        apply_cdg(40) {
            cuboid([40, latch_width, 18], anchor=BOTTOM);
        }
        translate([0,0,10])
        cuboid([42, latch_width - hinge_t*2, 20], anchor=BOTTOM);
        translate([-10,0,9])
        xrot(90) cyl(h=latch_width+1, d=pin_d + clearance*2);
    }
}

module flex_spring() {
    translate([-17.5, 0, 9])
    cuboid([5, latch_width - hinge_t*2 - clearance*2, 18], anchor=BOTTOM);
    translate([0, 0, 18 - hinge_t/2])
    cuboid([35, latch_width - hinge_t*2 - clearance*2, hinge_t], anchor=BOTTOM);
}

module rotating_blade() {
    translate([0, 30, 0])
    difference() {
        union() {
            cuboid([12, latch_width - hinge_t*2 - clearance*2, 12], anchor=CENTER);
            translate([21, 0, 0])
            cuboid([30, latch_width - hinge_t*2 - clearance*2, 10], anchor=CENTER);
        }
        xrot(90) cyl(h=latch_width, d=pin_d);
    }
}

render_mode = 0;

scale([1 + shrinkage_factor/100, 1 + shrinkage_factor/100, 1 + shrinkage_factor/100]) {
    if (render_mode == 0) { rigid_housing(); }
    else if (render_mode == 1) { rotating_blade(); }
    else if (render_mode == 2) { flex_spring(); }
    else if (render_mode == 3) { rigid_housing(); color("orange") flex_spring(); color("silver") rotating_blade(); }
}
