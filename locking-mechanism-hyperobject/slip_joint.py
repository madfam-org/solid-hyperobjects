import cadquery as cq


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
material_modulus = float(PARAM(lambda: material_modulus, 1.5))
shrinkage_factor = float(PARAM(lambda: shrinkage_factor, 0.0))
clearance = float(PARAM(lambda: clearance, 0.3))
cdg_mount_type = int(PARAM(lambda: cdg_mount_type, 0))
render_mode = 0

def generate():
    hinge_t = 2.5 * ((1.5 / max(material_modulus, 0.05)) ** 0.3)
    pin_d = 4

    if render_mode == 0 or render_mode == 3:
        base = cq.Workplane("XY").box(40, latch_width, 18).translate((0,0,9))
        if cdg_mount_type == 1:
            flanges = cq.Workplane("XY").box(16, 15, 5).translate((-28, 0, 2.5)).union(cq.Workplane("XY").box(16, 15, 5).translate((28, 0, 2.5)))
            holes = cq.Workplane("XY").cylinder(15, 1.7).translate((-28, 0, 0)).union(cq.Workplane("XY").cylinder(15, 1.7).translate((28, 0, 0)))
            base = base.union(flanges).cut(holes)
        elif cdg_mount_type == 2:
            base = base.union(cq.Workplane("XY").workplane(offset=-4.5).rect(42, 42).workplane(offset=4.5).rect(41.5, 41.5).loft())
            
        slot = cq.Workplane("XY").box(42, latch_width - hinge_t*2, 20).translate((0,0,10))
        pivot = cq.Workplane("YZ").cylinder(latch_width+1, pin_d/2 + clearance).translate((-10,0,9))
        housing = base.cut(slot).cut(pivot)

    if render_mode == 2 or render_mode == 3:
        anchor = cq.Workplane("XY").box(5, latch_width - hinge_t*2 - clearance*2, 18).translate((-17.5, 0, 9))
        leaf = cq.Workplane("XY").box(35, latch_width - hinge_t*2 - clearance*2, hinge_t).translate((0, 0, 18 - hinge_t/2))
        spring = anchor.union(leaf)
        
    if render_mode == 1 or render_mode == 3:
        hub = cq.Workplane("XY").box(12, latch_width - hinge_t*2 - clearance*2, 12)
        blade = cq.Workplane("XY").box(30, latch_width - hinge_t*2 - clearance*2, 10).translate((21, 0, 0))
        pivot_hole = cq.Workplane("YZ").cylinder(latch_width, pin_d/2)
        rot_blade = hub.union(blade).cut(pivot_hole).translate((0, 30, 0))
        
    if render_mode == 0: result = housing
    elif render_mode == 1: result = rot_blade
    elif render_mode == 2: result = spring
    elif render_mode == 3: result = housing.union(spring).union(rot_blade)
        
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
    "housing": 0,
    "blade": 1,
    "spring_t2": 2,
    "assembly_slip": 3,
}

_target_part = str(PARAM(lambda: target_part, "housing"))
render_mode = _PART_RENDER_MODE.get(_target_part, render_mode)

result = generate()
