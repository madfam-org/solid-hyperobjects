// Yantra4D — SCARA Robotics Robot (BOSL2)
include <BOSL2/std.scad>

$fn = 128;

// Parameters (injected by Yantra4D)
num_teeth = 100;      // Circular Spline teeth
gear_module = 0.5;    // Gear module
bore_diameter = 8;    // Input shaft bore
link1_length = 200;   // Shoulder link L1
link2_length = 150;   // Elbow link L2
z_travel = 100;       // Z-axis travel
harmonic_ratio = 50;  // Strain-wave reduction ratio (sets the tooth differential)
rail_width = 12;      // MGN rail width (9 | 12 | 15)
motor_frame_size = "nema17";  // nema17 | nema23

// render_mode dispatch — one branch per declared part in project.json.
//   0 = full assembly (the else-branch default; only `all` may land here)
//   1 = Wave Generator      2 = Flexspline           3 = Circular Spline
//   4 = Shoulder Link       5 = Elbow Link           6 = Z Spindle
//   7 = End Effector Mount  8 = Endstop Bracket X    9 = Endstop Bracket Y
//  10 = Z Probe Mount
render_mode = 0;

// Derived
// `harmonic_ratio` was declared in project.json and read by nothing; the tooth
// differential was hard-coded to 2. In a strain-wave drive the reduction IS the
// differential, so the slider sets it here and in robot.py identically. At the
// defaults (num_teeth 100, harmonic_ratio 50) tooth_diff is 2 — the same solid
// every preset rendered before.
tooth_diff = max(1, round(num_teeth / (harmonic_ratio + 1)));
flex_teeth = num_teeth - tooth_diff;
pitch_diam = gear_module * num_teeth;
flex_pitch_diam = gear_module * flex_teeth;
thickness = 10;
tooth_w = gear_module * 0.8;
tooth_h = gear_module * 4.0; // 2.0mm depth

// Kinematic-layer / sensorium derived dimensions. Every one of these is a
// function of a manifest parameter, so the seven parts below move when the
// configurator moves — they are not fixed props.
motor_flange = (motor_frame_size == "nema23") ? 57.0 : 42.3;
joint_boss_d = bore_diameter + 14;      // hub around the joint bore
link_h = 12;                            // link beam depth (Z)
link_w = joint_boss_d;                  // link beam width (Y)
pocket_inset = 4;                       // wall left around the lightening pocket
// Z column section. Driven by the rail, but never allowed to close on the
// axial bore: at rail_width 15 with bore_diameter 25 a rail-only section is
// exactly the bore diameter, leaving zero-thickness walls and a mesh that
// is not watertight. Keep 4 mm of wall on each side of the bore.
spindle_across = max(rail_width + 10, bore_diameter + 8);
bracket_t = 4;                          // sheet thickness of the sensorium brackets
bracket_leg = rail_width + 10;          // bracket leg length
endstop_pitch = 9.5;                    // Omron D2F mounting-hole pitch

module component_teeth(n, r, w, h, t) {
    for (i = [0:n-1]) {
        angle = i * (360 / n);
        zrot(angle)
        right(r)
        cube([h, w, t], center=true);
    }
}

module wave_generator() {
    color("#4a90e2")
    diff() {
        cylinder(h=thickness-2, d=flex_pitch_diam - (gear_module * 2), center=true);
        tag("remove")
        cylinder(h=thickness, d=bore_diameter, center=true, $fn=128);
    }
}

module flexspline() {
    color("#e24a4a")
    // The flange is unioned AFTER the cup is subtracted, exactly as robot.py
    // orders it (`res.cut(cup)` then `.union(flange)`). Inside the diff() the
    // cup's 0.1 mm overshoot (h = thickness + 0.1, centred) reached 0.05 mm past
    // the body into the flange and shaved a 23.5 mm-radius disc off it — 86.75
    // of the 89.14 mm3 (1.23 %) flexspline parity gap. Same solid, one boolean
    // reordered.
    //
    // These three discs stay at $fn=64 even though robot.py inscribes them as
    // `.polygon(128, ...)`, which leaves 2.54 mm3 (0.035 %) of faceting between
    // the kernels. Raising them to 128 to close that is NOT available here: the
    // cup's radius is `flex_pitch_diam/2 - gear_module*2` = 23.5 mm, which is
    // EXACTLY the tooth root radius (`flex_pitch_diam/2 - tooth_h/2`), so the cup
    // wall is tangent to all 98 tooth roots. At $fn=64 the polygon apothem
    // (23.4717) clears them; at 128 it rises to 23.4929 and CGAL produces a
    // degenerate mesh — "not watertight, 0 boundary edge(s)", euler -11/-19,
    // measured on the body and the cup independently (the flange at 128 is fine).
    // OCCT tolerates the same tangency, which is why the CadQuery side can hold
    // 128. The volume is right either way (the 128 mesh measures 7309.8772 mm3
    // against CadQuery's 7309.88) — only the tessellation is degenerate.
    //
    // Closing the last 0.035 % needs the tangency removed (give the cup a radial
    // overshoot past the tooth roots on BOTH kernels), which changes the solid
    // rather than its faceting; deferred rather than smuggled in here.
    union() {
        diff() {
            union() {
                // Body
                cylinder(h=thickness, d=flex_pitch_diam - 0.1, center=true, $fn=64);
                // Discrete Teeth
                component_teeth(flex_teeth, (flex_pitch_diam/2), tooth_w, tooth_h, thickness);
            }
            // Subtraction for cup
            tag("remove")
            cylinder(h=thickness + 0.1, d=flex_pitch_diam - (gear_module * 4), center=true, $fn=64);
        }
        // Base flange
        down(thickness/2)
        cylinder(h=2, d=flex_pitch_diam + 10, anchor=TOP, $fn=64);
    }
}

module circular_spline() {
    color("#2d2d2d")
    // $fn=128, not 64: robot.py builds every one of these discs as
    // `.polygon(128, d, circumscribed=False)`. At 64 the two kernels inscribe a
    // different polygon in the same circle, which is the whole 22.25 mm3
    // (0.17 %) circular_spline gap. At 128 the volumes agree to 0.0001 %.
    diff() {
        cylinder(h=thickness, d=pitch_diam + 15, center=true, $fn=128);
        tag("remove") {
            cylinder(h=thickness+1, d=pitch_diam + 0.1, center=true, $fn=128);
            // Internal teeth (subtracted)
            component_teeth(num_teeth, (pitch_diam/2), tooth_w, tooth_h, thickness+1);
        }
    }
}

// ---------------------------------------------------------------------------
// Kinetic Layer — the SCARA linkage. Four parts, each its own solid.
//
// Every module below is plain CSG over cylinders and boxes at an explicit $fn,
// which is what lets robot.py mirror it primitive-for-primitive: CadQuery's
// `.polygon(n, d, circumscribed=False)` is the same inscribed n-gon OpenSCAD
// facets a cylinder into. No BOSL2 attachables here on purpose — `diff()`/
// `tag()` reshape the CSG tree in ways the CadQuery side cannot reproduce
// exactly, and these parts have to agree between kernels.
// ---------------------------------------------------------------------------

// A link beam: two joint hubs `span` apart, bridged by a rectangular web, with
// a bore through each hub and a lightening pocket down the middle of the web.
module link_beam(span, boss_d, beam_w, beam_h, bore_d, pocket) {
    difference() {
        union() {
            // hub at the proximal joint (origin) and at the distal joint
            cylinder(h=beam_h, d=boss_d, center=true, $fn=64);
            translate([span, 0, 0])
            cylinder(h=beam_h, d=boss_d, center=true, $fn=64);
            // web bridging the two hubs
            translate([span/2, 0, 0])
            cube([span, beam_w, beam_h], center=true);
        }
        // joint bores
        cylinder(h=beam_h + 1, d=bore_d, center=true, $fn=64);
        translate([span, 0, 0])
        cylinder(h=beam_h + 1, d=bore_d, center=true, $fn=64);
        // lightening pocket — leaves `pocket` of wall on every side of the web
        if (pocket && span > boss_d + 2 * pocket_inset && beam_w > 2 * pocket_inset) {
            translate([span/2, 0, 0])
            cube([span - boss_d - 2 * pocket_inset,
                  beam_w - 2 * pocket_inset,
                  beam_h + 1], center=true);
        }
    }
}

module shoulder_link() {
    color("#8a8f98")
    link_beam(link1_length, joint_boss_d + 6, link_w + 6, link_h + 4,
              bore_diameter, true);
}

module elbow_link() {
    color("#a8adb6")
    link_beam(link2_length, joint_boss_d, link_w, link_h,
              bore_diameter, true);
}

// The Z column: a square-section tube of z_travel height with a bore down its
// axis and a keying flat, capped by a carriage plate that carries the rail.
module z_spindle() {
    color("#6c7480")
    difference() {
        union() {
            // the column itself
            cube([spindle_across, spindle_across, z_travel], center=true);
            // carriage plate at the bottom of the travel
            translate([0, 0, -z_travel/2 - 3])
            cube([spindle_across + 8, spindle_across, 6], center=true);
        }
        // axial bore
        cylinder(h=z_travel + 8, d=bore_diameter, center=true, $fn=64);
        // rail relief along one face
        translate([0, spindle_across/2, 0])
        cube([rail_width, 4, z_travel + 1], center=true);
    }
}

// The tool flange: a plate carrying the motor bolt circle, with a central
// through-bore and the four NEMA corner holes at their standard pitch.
module end_effector_mount() {
    // The plate IS the motor flange footprint: at motor_flange * 0.75 the four
    // NEMA corner holes (31 mm pitch on a 42.3 mm flange, 47.14 on 57) fall
    // clean outside the plate and cut nothing at all -- the mesh stays
    // watertight, so only measuring the bolt circle catches it. The plate has
    // to carry the bolt pattern the manifest's `nema17_mount` CDG interface
    // declares.
    hole_pitch = (motor_frame_size == "nema23") ? 47.14 : 31.0;
    plate = motor_flange;
    color("#c9ced6")
    difference() {
        union() {
            translate([0, 0, 0])
            cube([plate, plate, 6], center=true);
            // boss around the central bore
            cylinder(h=12, d=bore_diameter + 10, center=true, $fn=64);
        }
        cylinder(h=14, d=bore_diameter, center=true, $fn=64);
        for (sx = [-1, 1]) for (sy = [-1, 1])
            translate([sx * hole_pitch/2, sy * hole_pitch/2, 0])
            cylinder(h=8, d=3.4, center=true, $fn=32);
    }
}

// ---------------------------------------------------------------------------
// Sensory Layer (Panopticon) — the reference anchors.
// ---------------------------------------------------------------------------

// An L-bracket carrying an Omron-D2F switch pair on the upstand and a pair of
// rail slots in the foot.
module endstop_bracket(leg, upstand, t, slot_w) {
    difference() {
        union() {
            // foot
            translate([leg/2, 0, t/2])
            cube([leg, leg, t], center=true);
            // upstand
            translate([t/2, 0, upstand/2])
            cube([t, leg, upstand], center=true);
        }
        // switch holes in the upstand
        for (s = [-1, 1])
            translate([t/2, 0, upstand/2 + s * endstop_pitch/2])
            rotate([0, 90, 0])
            cylinder(h=t + 2, d=2.4, center=true, $fn=32);
        // rail slots in the foot
        for (s = [-1, 1])
            translate([leg * 0.65, s * (leg/4), t/2])
            cylinder(h=t + 2, d=slot_w, center=true, $fn=32);
    }
}

module endstop_bracket_x() {
    color("#e2c14a")
    endstop_bracket(bracket_leg, bracket_leg + 6, bracket_t, 3.4);
}

// The Y anchor is the same family of part on the orthogonal axis: a shorter
// foot and a taller upstand, because it references the forearm rather than the
// base plate. Distinct geometry, deliberately — not a mirror of X.
module endstop_bracket_y() {
    color("#4ae2a0")
    endstop_bracket(bracket_leg - 4, bracket_leg + 14, bracket_t, 3.0);
}

// The Z probe: a closed collar around the spindle with a cantilever arm
// carrying the probe barrel. The collar is a full ring, not a split clamp --
// it slides onto the spindle from the end rather than clamping around it.
module z_probe_mount() {
    ring_id = spindle_across + 2;
    ring_od = ring_id + 8;
    arm_len = bracket_leg + 10;
    color("#9a4ae2")
    difference() {
        union() {
            cylinder(h=bracket_t * 2, d=ring_od, center=true, $fn=64);
            translate([arm_len/2, 0, 0])
            cube([arm_len, bracket_t * 3, bracket_t * 2], center=true);
            // barrel boss at the arm tip
            translate([arm_len, 0, 0])
            cylinder(h=bracket_t * 3, d=bore_diameter + 8, center=true, $fn=64);
        }
        // collar bore and probe bore
        cylinder(h=bracket_t * 2 + 2, d=ring_id, center=true, $fn=64);
        translate([arm_len, 0, 0])
        cylinder(h=bracket_t * 3 + 2, d=bore_diameter, center=true, $fn=64);
    }
}

// Assembly / Rendering
if (render_mode == 0) {
    wave_generator();
    flexspline();
    circular_spline();
} else if (render_mode == 1) {
    wave_generator();
} else if (render_mode == 2) {
    flexspline();
} else if (render_mode == 3) {
    circular_spline();
} else if (render_mode == 4) {
    shoulder_link();
} else if (render_mode == 5) {
    elbow_link();
} else if (render_mode == 6) {
    z_spindle();
} else if (render_mode == 7) {
    end_effector_mount();
} else if (render_mode == 8) {
    endstop_bracket_x();
} else if (render_mode == 9) {
    endstop_bracket_y();
} else if (render_mode == 10) {
    z_probe_mount();
}
