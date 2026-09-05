include <../../libs/BOSL2/std.scad>

// Yantra4D Parameters
pipe_od_mm = 21.3; // Nominal OD
connector_type = "elbow"; // [elbow, tee, cross, 3-way-corner, 4-way-corner, 5-way, 6-way]
wall_thickness_mm = 3;
insertion_depth_mm = 20;

// Internal calculations
socket_od = pipe_od_mm + (wall_thickness_mm * 2);
socket_length = insertion_depth_mm + wall_thickness_mm;

module socket_arm() {
    difference() {
        cylinder(h=socket_length, d=socket_od, $fn=64);
        up(wall_thickness_mm)
        cylinder(h=socket_length, d=pipe_od_mm + 0.5, $fn=64); // +0.5 tolerance
    }
}

// Solid hub the arms grow out of: a chamfered cube, deliberately OVERSIZE.
//
// This was `sphere(d=socket_od)`. Both CadQuery sides of this cartridge --
// connector.py:16-38 and main.py:81-95, which is the primary entry point for
// the elbow/tee/corner_3way modes -- replaced that sphere years ago and
// document why at length:
//
//   1. A sphere's UV poles tessellate into coincident vertices that collapse
//      to zero-length edges, so the export never encloses a volume.
//   2. A hub whose half-extent is exactly socket_od/2 makes every arm exactly
//      TANGENT to it, and the union of two surfaces that merely kiss
//      tessellates into razor-thin slivers.
//
// Both are fixed the same way: give the hub strictly more radius than the
// socket, so the arms INTERSECT the hub rather than touching it. Two of this
// cartridge's three sources already agreed on the rule and the constants; only
// this file still carried the sphere, which is the whole of the 2.999999 mm
// AABB divergence -- exactly the 1.5 mm oversize, doubled.
hub_r = (socket_od / 2) + max(1.5, wall_thickness_mm * 0.5);

module core_hub() {
    cuboid([hub_r * 2, hub_r * 2, hub_r * 2], chamfer=hub_r * 0.35);
}

module parametric_connector() {
    union() {
        core_hub();
        
        // Z+
        if (connector_type != "elbow" && connector_type != "tee")
            up(socket_od/2 - wall_thickness_mm) socket_arm();
            
        // Z-
        if (connector_type == "cross" || connector_type == "5-way" || connector_type == "6-way")
            down(socket_od/2 - wall_thickness_mm) zrot(180) socket_arm();

        // X+
        if (true) // All connectors have at least one arm
            right(socket_od/2 - wall_thickness_mm) yrot(90) socket_arm();

        // X-
        // "elbow" used to be listed here as well. Together with the X+ arm that
        // every connector gets, and the Y+ arm added for elbows further down,
        // that gave a 90-degree elbow three arms — a tee. connector.py has only
        // ever built two, so the two engines disagreed by 20 mm in X and 20% by
        // volume on this cartridge's default mode.
        if (connector_type == "tee" || connector_type == "cross" || connector_type == "4-way-corner" || connector_type == "5-way" || connector_type == "6-way")
            left(socket_od/2 - wall_thickness_mm) yrot(-90) socket_arm();

        // Y+
        if (connector_type == "elbow" || connector_type == "3-way-corner" || connector_type == "4-way-corner" || connector_type == "5-way" || connector_type == "6-way" || connector_type == "tee")
            back(socket_od/2 - wall_thickness_mm) xrot(-90) socket_arm();

        // Y-
        if (connector_type == "6-way")
            fwd(socket_od/2 - wall_thickness_mm) xrot(90) socket_arm();
    }
}

parametric_connector();
