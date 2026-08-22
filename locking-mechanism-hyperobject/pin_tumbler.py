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
clearance = float(PARAM(lambda: clearance, 0.3))
num_pins = int(PARAM(lambda: num_pins, 5))
shrinkage_factor = float(PARAM(lambda: shrinkage_factor, 0.0))
cdg_mount_type = int(PARAM(lambda: cdg_mount_type, 0))
render_mode = 0

def bitting(i): return 2.0 + (i % 3) * 1.5

def generate():
    plug_d = 12
    stator_d = 20
    core_l = 10 + num_pins * 6
    pin_d = 2.5
    pin_pitch = 6
    key_gap = 1.5
    
    if render_mode == 0:
        plug = cq.Workplane("YZ").cylinder(core_l, (plug_d - clearance)/2).translate((core_l/2, 0, 0))
        keyway = cq.Workplane("XY").box(core_l+1, key_gap, plug_d).translate((core_l/2, 0, -plug_d/4))
        chambers = cq.Workplane("XY")
        for i in range(num_pins):
            chambers = chambers.union(cq.Workplane("XY").cylinder(plug_d*0.8, (pin_d + clearance*1.5)/2).translate((6 + i*pin_pitch, 0, plug_d/2 - (plug_d*0.8)/2)))
        result = plug.cut(keyway).cut(chambers)
        
    elif render_mode == 1:
        stator = cq.Workplane("YZ").cylinder(core_l, stator_d/2).translate((core_l/2, 0, 0))
        if cdg_mount_type == 1:
            stator = stator.union(cq.Workplane("XY").box(16, 15, 5).translate((-8, 0, 2.5))).union(cq.Workplane("XY").box(16, 15, 5).translate((core_l+8, 0, 2.5)))
        elif cdg_mount_type == 2:
            stator = stator.union(cq.Workplane("XY").workplane(offset=-4.5).rect(42, 42).workplane(offset=4.5).rect(41.5, 41.5).loft().translate((core_l/2,0,0)))
            
        bore = cq.Workplane("YZ").cylinder(core_l+1, (plug_d + clearance)/2).translate((core_l/2, 0, 0))
        chambers = cq.Workplane("XY")
        for i in range(num_pins):
            chambers = chambers.union(cq.Workplane("XY").cylinder(stator_d, (pin_d + clearance*1.5)/2).translate((6 + i*pin_pitch, 0, plug_d/2 - clearance + stator_d/2)))
        result = stator.cut(bore).cut(chambers)
        
    elif render_mode == 2:
        blade = cq.Workplane("XY").box(core_l, key_gap - clearance, plug_d*0.8).translate((core_l/2, 0, 0))
        cuts = cq.Workplane("XY")
        for i in range(num_pins):
            cd = plug_d*0.4 - bitting(i)
            cuts = cuts.union(cq.Workplane("XZ").cylinder(key_gap, pin_d*1.5).translate((6 + i*pin_pitch, 0, plug_d*0.4)))
        key = blade.cut(cuts).translate((0, 0, -plug_d))
        bow = cq.Workplane("YZ").cylinder(key_gap - clearance, stator_d/2).translate((0, 0, -plug_d))
        
        pins = cq.Workplane("XY")
        for i in range(num_pins):
            pins = pins.union(cq.Workplane("YZ").cylinder(bitting(i), pin_d/2).translate((i*10, plug_d*1.5, bitting(i)/2)))
            pins = pins.union(cq.Workplane("YZ").cylinder(3, pin_d/2).translate((i*10, plug_d*1.5+pin_d*2, 1.5)))
        
        result = key.union(bow).union(pins)
        
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
    "plug": 0,
    "stator": 1,
    "keys": 2,
}

_target_part = str(PARAM(lambda: target_part, "plug"))
render_mode = _PART_RENDER_MODE.get(_target_part, render_mode)

result = generate()
