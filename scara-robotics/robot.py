import cadquery as cq
import math
import json
import argparse

def add_discrete_teeth(base, n, r, w, h, t):
    """Add box teeth around a circle."""
    arc_gap = 2 * math.pi * r / n if n > 0 else 0
    for i in range(n):
        if w > arc_gap * 0.95:
            continue  # skip tooth if it would overlap adjacent teeth
        angle = i * (360.0 / n)
        rad = math.radians(angle)
        x = r * math.cos(rad)
        y = r * math.sin(rad)
        tooth = (
            cq.Workplane("XY")
            .box(h, w, t)
            .rotate((0, 0, 0), (0, 0, 1), angle)
            .translate((x, y, 0))
        )
        base = base.union(tooth)
    return base

def wave_generator(flex_pitch_diam, gear_module, thickness, bore_diameter):
    r_base = (flex_pitch_diam - (gear_module * 2)) / 2.0
    res = (
        cq.Workplane("XY")
        .polygon(128, 2*r_base, circumscribed=False)
        .extrude((thickness - 2.0)/2.0, both=True)
    )
    res = res.faces(">Z").workplane().polygon(128, bore_diameter, circumscribed=False).cutThruAll()
    return res

def flexspline(flex_pitch_diam, gear_module, flex_teeth, tooth_w, tooth_h, thickness):
    r_body = (flex_pitch_diam - 0.1) / 2.0
    res = cq.Workplane("XY").polygon(128, 2*r_body, circumscribed=False).extrude(thickness/2.0, both=True)
    res = add_discrete_teeth(res, flex_teeth, flex_pitch_diam/2.0, tooth_w, tooth_h, thickness)
    
    inner_d = (flex_pitch_diam - (gear_module * 4))
    res = res.cut(cq.Workplane("XY").polygon(128, inner_d, circumscribed=False).extrude((thickness + 0.1)/2.0, both=True))
    
    flange_d = (flex_pitch_diam + 10)
    flange = (
        cq.Workplane("XY")
        .workplane(offset=-thickness/2.0)
        .polygon(128, flange_d, circumscribed=False)
        .extrude(-2.0)
    )
    return res.union(flange)

def circular_spline(pitch_diam, num_teeth, tooth_w, tooth_h, thickness):
    outer_d = (pitch_diam + 15)
    inner_d = (pitch_diam + 0.1)
    
    res = cq.Workplane("XY").polygon(128, outer_d, circumscribed=False).extrude(thickness/2.0, both=True)
    
    hole = cq.Workplane("XY").polygon(128, inner_d, circumscribed=False).extrude((thickness + 1.0)/2.0, both=True)
    hole = add_discrete_teeth(hole, num_teeth, pitch_diam/2.0, tooth_w, tooth_h, thickness + 1.0)
    
    return res.cut(hole)

# ---------------------------------------------------------------------------
# Kinetic Layer — the SCARA linkage, mirroring robot.scad primitive for
# primitive. Cylinders come through `.polygon(n, d, circumscribed=False)`
# because that is the inscribed n-gon OpenSCAD facets a `cylinder($fn=n)` into;
# a true `.circle()` would be the analytic cylinder and put the two kernels a
# facet-chord apart on every bore.
# ---------------------------------------------------------------------------

def _disc(d, h, n=64):
    """A faceted disc: the CadQuery twin of `cylinder(h=h, d=d, $fn=n, center=true)`."""
    return (
        cq.Workplane("XY")
        .polygon(n, d, circumscribed=False)
        .extrude(h / 2.0, both=True)
    )


def _box(dx, dy, dz, at=(0.0, 0.0, 0.0)):
    """`cube([dx,dy,dz], center=true)` translated to `at`."""
    return cq.Workplane("XY").box(dx, dy, dz).translate(at)


def link_beam(span, boss_d, beam_w, beam_h, bore_d, pocket, pocket_inset):
    """Two joint hubs `span` apart bridged by a webbed beam — robot.scad's link_beam()."""
    res = _disc(boss_d, beam_h)
    res = res.union(_disc(boss_d, beam_h).translate((span, 0, 0)))
    res = res.union(_box(span, beam_w, beam_h, (span / 2.0, 0, 0)))

    res = res.cut(_disc(bore_d, beam_h + 1))
    res = res.cut(_disc(bore_d, beam_h + 1).translate((span, 0, 0)))

    if pocket and span > boss_d + 2 * pocket_inset and beam_w > 2 * pocket_inset:
        res = res.cut(
            _box(
                span - boss_d - 2 * pocket_inset,
                beam_w - 2 * pocket_inset,
                beam_h + 1,
                (span / 2.0, 0, 0),
            )
        )
    return res


def build_shoulder_link(d):
    return link_beam(
        d['link1_length'], d['joint_boss_d'] + 6, d['link_w'] + 6, d['link_h'] + 4,
        d['bore_diameter'], True, d['pocket_inset'],
    )


def build_elbow_link(d):
    return link_beam(
        d['link2_length'], d['joint_boss_d'], d['link_w'], d['link_h'],
        d['bore_diameter'], True, d['pocket_inset'],
    )


def build_z_spindle(d):
    across = d['spindle_across']
    z_travel = d['z_travel']
    res = _box(across, across, z_travel)
    res = res.union(_box(across + 8, across, 6, (0, 0, -z_travel / 2.0 - 3)))
    res = res.cut(_disc(d['bore_diameter'], z_travel + 8))
    res = res.cut(_box(d['rail_width'], 4, z_travel + 1, (0, across / 2.0, 0)))
    return res


def build_end_effector_mount(d):
    # The plate IS the motor flange footprint -- see the note in robot.scad:
    # at motor_flange * 0.75 the four NEMA corner holes fall outside the plate
    # and cut nothing, leaving the declared `nema17_mount` bolt pattern absent
    # from a mesh that is nonetheless watertight.
    hole_pitch = 47.14 if d['motor_frame_size'] == 'nema23' else 31.0
    plate = d['motor_flange']
    res = _box(plate, plate, 6)
    res = res.union(_disc(d['bore_diameter'] + 10, 12))
    res = res.cut(_disc(d['bore_diameter'], 14))
    for sx in (-1, 1):
        for sy in (-1, 1):
            res = res.cut(
                _disc(3.4, 8, n=32).translate((sx * hole_pitch / 2.0, sy * hole_pitch / 2.0, 0))
            )
    return res


# ---------------------------------------------------------------------------
# Sensory Layer (Panopticon) — the reference anchors.
# ---------------------------------------------------------------------------

def endstop_bracket(leg, upstand, t, slot_w, endstop_pitch):
    """robot.scad's endstop_bracket(): an L of foot + upstand, drilled twice over."""
    res = _box(leg, leg, t, (leg / 2.0, 0, t / 2.0))
    res = res.union(_box(t, leg, upstand, (t / 2.0, 0, upstand / 2.0)))

    # switch holes through the upstand — rotate([0,90,0]) puts the axis on X
    for s in (-1, 1):
        hole = (
            cq.Workplane("XY")
            .polygon(32, 2.4, circumscribed=False)
            .extrude((t + 2) / 2.0, both=True)
            .rotate((0, 0, 0), (0, 1, 0), 90)
            .translate((t / 2.0, 0, upstand / 2.0 + s * endstop_pitch / 2.0))
        )
        res = res.cut(hole)

    # rail slots in the foot
    for s in (-1, 1):
        res = res.cut(
            _disc(slot_w, t + 2, n=32).translate((leg * 0.65, s * (leg / 4.0), t / 2.0))
        )
    return res


def build_endstop_bracket_x(d):
    return endstop_bracket(
        d['bracket_leg'], d['bracket_leg'] + 6, d['bracket_t'], 3.4, d['endstop_pitch']
    )


def build_endstop_bracket_y(d):
    return endstop_bracket(
        d['bracket_leg'] - 4, d['bracket_leg'] + 14, d['bracket_t'], 3.0, d['endstop_pitch']
    )


def build_z_probe_mount(d):
    t = d['bracket_t']
    ring_id = d['spindle_across'] + 2
    ring_od = ring_id + 8
    arm_len = d['bracket_leg'] + 10

    res = _disc(ring_od, t * 2)  # the collar: a full ring, not a split clamp
    res = res.union(_box(arm_len, t * 3, t * 2, (arm_len / 2.0, 0, 0)))
    res = res.union(_disc(d['bore_diameter'] + 8, t * 3).translate((arm_len, 0, 0)))

    res = res.cut(_disc(ring_id, t * 2 + 2))
    res = res.cut(_disc(d['bore_diameter'], t * 3 + 2).translate((arm_len, 0, 0)))
    return res


def derive(params):
    """The derived block from robot.scad, in one place, for the seven new parts."""
    bore_diameter = float(params.get('bore_diameter', 8.0))
    motor_frame_size = str(params.get('motor_frame_size', 'nema17'))
    rail_width = float(params.get('rail_width', 12))
    joint_boss_d = bore_diameter + 14
    return {
        'bore_diameter': bore_diameter,
        'motor_frame_size': motor_frame_size,
        'motor_flange': 57.0 if motor_frame_size == 'nema23' else 42.3,
        'rail_width': rail_width,
        'link1_length': float(params.get('link1_length', 200)),
        'link2_length': float(params.get('link2_length', 150)),
        'z_travel': float(params.get('z_travel', 100)),
        'joint_boss_d': joint_boss_d,
        'link_h': 12.0,
        'link_w': joint_boss_d,
        'pocket_inset': 4.0,
        # Never let the rail-driven section close on the axial bore -- see the
        # same guard in robot.scad. rail_width 15 with bore_diameter 25 gives a
        # rail-only section of exactly the bore diameter: zero-thickness walls.
        'spindle_across': max(rail_width + 10, bore_diameter + 8),
        'bracket_t': 4.0,
        'bracket_leg': rail_width + 10,
        'endstop_pitch': 9.5,
    }


# Every declared part -> its builder. `all` is deliberately absent: it is the
# else-branch assembly, and the spec allows exactly one part to be that.
PART_BUILDERS = {
    'shoulder_link': build_shoulder_link,
    'elbow_link': build_elbow_link,
    'z_spindle': build_z_spindle,
    'end_effector_mount': build_end_effector_mount,
    'endstop_bracket_x': build_endstop_bracket_x,
    'endstop_bracket_y': build_endstop_bracket_y,
    'z_probe_mount': build_z_probe_mount,
}


def build(params, part="all"):
    """Dispatch on the requested part.

    The platform never calls this with a positional `part`: `cq_runner` execs
    the script with the params as globals, so the part arrives as the
    `target_part` key inside `params` and is read in the `__main__` block
    below. Every declared part gets its own branch; only `all` falls through to
    the assembly, because the spec's fallback check allows exactly one part to
    be the else-branch default.

    Each branch builds ONLY the geometry it returns. The previous version built
    all three harmonic bodies before selecting one, which made every per-part
    render pay for the flexspline's ~98 sequential tooth unions.
    """
    num_teeth = int(params.get('num_teeth', 100))
    gear_module = float(params.get('gear_module', 0.5))
    bore_diameter = float(params.get('bore_diameter', 8.0))

    # `harmonic_ratio` used to be declared in project.json and read by nothing:
    # the tooth differential was hard-coded to 2. In a strain-wave drive the
    # reduction IS the differential — ratio = flex_teeth / (num_teeth -
    # flex_teeth) — so the slider now sets it. At the defaults (num_teeth 100,
    # harmonic_ratio 50) this yields a differential of 2 and the identical
    # solid every preset rendered before, so no preset changes meaning.
    harmonic_ratio = float(params.get('harmonic_ratio', 50))
    tooth_diff = max(1, round(num_teeth / (harmonic_ratio + 1.0)))

    flex_teeth = num_teeth - tooth_diff
    pitch_diam = gear_module * num_teeth
    flex_pitch_diam = gear_module * flex_teeth
    thickness = 10.0
    tooth_w = gear_module * 0.8
    tooth_h = gear_module * 4.0 # 2.0mm depth

    if part == "wave_generator":
        return wave_generator(flex_pitch_diam, gear_module, thickness, bore_diameter).clean()
    elif part == "flexspline":
        return flexspline(flex_pitch_diam, gear_module, flex_teeth, tooth_w, tooth_h, thickness).clean()
    elif part == "circular_spline":
        return circular_spline(pitch_diam, num_teeth, tooth_w, tooth_h, thickness).clean()

    builder = PART_BUILDERS.get(part)
    if builder is not None:
        return builder(derive(params)).clean()

    wg = wave_generator(flex_pitch_diam, gear_module, thickness, bore_diameter)
    fs = flexspline(flex_pitch_diam, gear_module, flex_teeth, tooth_w, tooth_h, thickness)
    cs = circular_spline(pitch_diam, num_teeth, tooth_w, tooth_h, thickness)
    res = wg.union(fs).union(cs)
    return res.clean()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--part", type=str, default="all")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)

    # The part comes from `params["target_part"]` first and only falls back to
    # `--part`. `cq_runner` (apps/api/services/engine/cq_runner.py) sets
    # sys.argv to ["<script>", "--params", <json>, "--out", <path>] and execs
    # the file with __name__ == "__main__", so this block DOES run on the
    # platform -- but `--part` is never among those arguments, so `args.part`
    # always fell back to "all" and every declared part rendered the assembly.
    part = params.get("target_part") or args.part
    res = build(params, part=part)

    # Name the result so cq_runner's own lookup finds it directly rather than
    # falling through to its "last CadQuery object created" scan.
    result = res

    if args.out:
        cq.exporters.export(res, args.out)
