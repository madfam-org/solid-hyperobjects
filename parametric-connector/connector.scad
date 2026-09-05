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

module core_sphere() {
    sphere(d=socket_od, $fn=64);
}

module parametric_connector() {
    union() {
        core_sphere();
        
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
