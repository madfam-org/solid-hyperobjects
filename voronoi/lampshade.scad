// Yantra4D wrapper — Voronoi Lampshade
// Spherical lampshade with voronoi cell openings

cell_count = 20;
size = 100;          // diameter in mm
thickness = 3;
cell_wall = 2;
seed = 42;
height = 120;
fn = 0;
render_mode = 0;

$fn = fn > 0 ? fn : 32;

// Spherical Voronoi cells are intersections of great-circle half-spaces.
// This avoids stereographic projection at the poles and the triangulation
// degeneracies that produced invalid meshes with the CGAL backend.
radius = size / 2;
points = [for (i = [0:cell_count-1])
    let(z = 1 - 2 * (i + 0.5) / cell_count,
        angle = i * 137.507764 + seed,
        r = sqrt(1 - z*z))
    [r*cos(angle), r*sin(angle), z]];

module positive_halfspace(normal, inset) {
    n = normal / norm(normal);
    rotate([0, acos(n.z), atan2(n.y, n.x)])
        translate([0, 0, 2*radius + inset])
            cube([4*radius, 4*radius, 4*radius], center=true);
}

module cell_opening(index) {
    intersection() {
        cube(4*radius, center=true);
        intersection_for (j = [for (k = [0:cell_count-1]) if (k != index) k])
            positive_halfspace(points[index] - points[j], cell_wall/2);
    }
}

assert(cell_count >= 4, "At least four cells are required");
assert(thickness > 0 && thickness < radius, "Invalid shell thickness");
assert(cell_wall > 0, "Cell walls must have positive width");
difference() {
    sphere(r=radius);
    sphere(r=radius-thickness);
    translate([0, 0, -radius-0.1])
        cylinder(h=radius*0.4+0.1, r=radius*0.3);
    for (i = [0:cell_count-1]) cell_opening(i);
}
