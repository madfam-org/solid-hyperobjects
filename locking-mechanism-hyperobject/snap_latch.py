import cadquery as cq
import math

# Variables injected by Yantra4D at runtime

def PARAM(getter, default):
    """Return an injected global if present, else the default.

    Manifest parameters arrive as BARE globals injected before this module runs.
    A plain `latch_width = 15` would overwrite the injected value, so every
    parameter is read through this helper instead (house idiom; see other
    yantra4d CadQuery cartridges).
    """
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


# ── Parameters ───────────────────────────────────────────────────────────────
latch_width = float(PARAM(lambda: latch_width, 15))
hook_depth = float(PARAM(lambda: hook_depth, 2))
spring_angle = float(PARAM(lambda: spring_angle, 30))
wall_thickness = float(PARAM(lambda: wall_thickness, 2))
base_length = float(PARAM(lambda: base_length, 40))
clearance = float(PARAM(lambda: clearance, 0.3))
material_modulus = float(PARAM(lambda: material_modulus, 1.5))
shrinkage_factor = float(PARAM(lambda: shrinkage_factor, 0.0))
cdg_mount_type = int(PARAM(lambda: cdg_mount_type, 0))
render_mode = 0

def apply_cdg(base_obj, base_x):
    if cdg_mount_type == 1:
        flanges = (
            cq.Workplane("XY").box(16, 15, 5).translate((-base_x/2 - 8, 0, 2.5))
            .union(cq.Workplane("XY").box(16, 15, 5).translate((base_x/2 + 8, 0, 2.5)))
        )
        holes = (
            cq.Workplane("XY").cylinder(15, 1.7).translate((-base_x/2 - 8, 0, 0))
            .union(cq.Workplane("XY").polygon(6, 3.1).extrude(10).translate((-base_x/2 - 8, 0, 2)))
            .union(cq.Workplane("XY").cylinder(15, 1.7).translate((base_x/2 + 8, 0, 0)))
            .union(cq.Workplane("XY").polygon(6, 3.1).extrude(10).translate((base_x/2 + 8, 0, 2)))
        )
        return base_obj.union(flanges).cut(holes)
    elif cdg_mount_type == 2:
        return base_obj.union(cq.Workplane("XY").workplane(offset=-4.5).rect(42, 42).workplane(offset=4.5).rect(41.5, 41.5).loft())
    return base_obj

def generate():
    mod_mod = (1.5 / max(material_modulus, 0.05)) ** 0.3
    arm_l = base_length * 0.7
    arm_t = wall_thickness * 0.8 * mod_mod
    base_h = wall_thickness * 2.5

    if render_mode == 0:
        base_l = base_length - arm_l
        base = cq.Workplane("XY").box(base_l, latch_width, base_h).translate((-base_l/2, 0, base_h/2))
        base = apply_cdg(base, base_l)
        
        arm = cq.Workplane("XY").box(arm_l, latch_width, arm_t).translate((arm_l/2, 0, arm_t/2))

        hook_l = hook_depth / math.tan(math.radians(35))
        ret_off = hook_depth / math.tan(math.radians(85))

        # Both kernels now build the SAME construction. snap_latch.scad extends
        # each hook polygon back INTO the beam by `_hook_overlap` so the boolean
        # has volume to fuse; this file used to sink the wedges by `weld =
        # arm_t*0.5` instead. Same intent, different solid: the OpenSCAD hook
        # reaches 0.5 mm further back in X and sits 0.8 mm higher in Z, which is
        # exactly the 0.692822 mm AABB parity gap (and 0.4 mm in X). Use the
        # OpenSCAD polygons verbatim — they are the reference side.
        hook_overlap = 0.5

        # extrude(latch_width/2, both=True), not extrude(latch_width, both=True):
        # `both` mirrors the extrusion about the sketch plane, so passing the
        # full width builds a 2 x latch_width prism. snap_latch.scad extrudes
        # the same two profiles with `linear_extrude(height=latch_width,
        # center=true)`, which is latch_width in total.
        half_w = latch_width / 2.0
        hook = (
            cq.Workplane("XZ")
            .polyline([(-hook_overlap, -hook_overlap), (-ret_off, hook_depth),
                       (hook_l, 0), (hook_l, -hook_overlap)])
            .close().extrude(half_w, both=True).translate((arm_l, 0, arm_t))
        )
        undercut = (
            cq.Workplane("XZ")
            .polyline([(-hook_overlap, 0), (hook_l, 0), (0, -arm_t),
                       (-hook_overlap, -arm_t)])
            .close().extrude(half_w, both=True).translate((arm_l, 0, 0))
        )

        # Stress-relief fillets at the beam root. snap_latch.scad builds these as
        # two BOSL2 `prismoid`s (anchor=BOTTOM+LEFT, shift=[fillet_r,0]) and this
        # file omitted them entirely — 208.67 mm3 of the volume gap.
        #
        # `size2=[0, latch_width]` shifted by `fillet_r` collapses the top face to
        # a LINE at x = fillet_r*2, so the prismoid is simply a wedge. Build it as
        # an extruded triangle. Lofting to a 1e-6-wide top instead reproduced the
        # volume exactly but left `BRepCheck_Analyzer` False and tessellated with
        # 12 boundary edges — a knife-edge face OCCT meshes open.
        fillet_r = arm_t * 1.5
        fillet_top = (cq.Workplane("XZ")
                      .polyline([(0, 0), (fillet_r*2, 0), (fillet_r*2, fillet_r)])
                      .close().extrude(half_w, both=True).translate((0, 0, arm_t)))
        fillet_bot = (cq.Workplane("XZ")
                      .polyline([(0, 0), (fillet_r*2, 0), (fillet_r*2, -fillet_r)])
                      .close().extrude(half_w, both=True))

        full_arm = (arm.union(hook).union(undercut)
                    .union(fillet_top).union(fillet_bot)
                    .rotate((0,0,0), (0,1,0), -spring_angle)
                    .translate((0, 0, base_h/2 - arm_t/2)))
        result = base.union(full_arm)
    else:
        p_l = base_length * 0.4
        p_w = latch_width + clearance*2 + wall_thickness*2
        hook_z = base_h/2 - arm_t/2 + arm_l * math.sin(math.radians(spring_angle)) + hook_depth
        p_h = hook_z + wall_thickness*2
        
        base = cq.Workplane("XY").box(p_l, p_w, p_h).translate((0, 0, p_h/2))
        slot = cq.Workplane("XY").box(p_l+1, latch_width + clearance*2, hook_depth + clearance).translate((0, 0, hook_z - (hook_depth+clearance)/2))
        # BOSL2's `cuboid(..., anchor=BOTTOM)` puts the box's BASE on the origin
        # before the rotate; cq's `.box()` centres it. Rotating a centred box
        # dropped the chamfer cutter half a plate-height low and ate 1124.27 mm3
        # (20.16 %) more of the plate than snap_latch.scad does. Lift the box by
        # p_h/2 first so both kernels rotate the same bottom-anchored cutter.
        chamf = (cq.Workplane("XY").box(p_l*1.5, latch_width + clearance*2, p_h)
                 .translate((0, 0, p_h/2))
                 .rotate((0,0,0),(0,1,0), 35).translate((-p_l/2, 0, p_h)))
        
        result = base.cut(slot).cut(chamf).translate((arm_l * math.cos(math.radians(spring_angle)), 0, 0))

    # Compensate for material shrinkage. cq.Workplane has no .scale(); the
    # operation lives on the underlying Shape, so unwrap, scale and rewrap.
    factor = 1 + shrinkage_factor/100.0
    if factor == 1.0:
        return result
    return cq.Workplane("XY").newObject([result.val().scale(factor)])

# ── Dispatch ─────────────────────────────────────────────────────────────────
# The platform injects parameters as bare globals and reads back `result`.
# CadQuery renders are selected by `target_part` (the part id); the OpenSCAD
# twin of this script is selected by the `render_mode` integer. Map one to the
# other so both engines build the same part from the same manifest.
_PART_RENDER_MODE = {
    "latch_arm": 0,
    "striker_plate": 1,
}

_target_part = str(PARAM(lambda: target_part, "latch_arm"))
render_mode = _PART_RENDER_MODE.get(_target_part, render_mode)

result = generate()
