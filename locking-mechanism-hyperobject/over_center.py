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
lever_length = float(PARAM(lambda: lever_length, 30))
over_center_offset = float(PARAM(lambda: over_center_offset, 2))
wall_thickness = float(PARAM(lambda: wall_thickness, 2.5))
latch_width = float(PARAM(lambda: latch_width, 15))
base_length = float(PARAM(lambda: base_length, 40))
clearance = float(PARAM(lambda: clearance, 0.3))
shrinkage_factor = float(PARAM(lambda: shrinkage_factor, 0.0))
cdg_mount_type = int(PARAM(lambda: cdg_mount_type, 0))
render_mode = 0

def generate():
    pin_d = wall_thickness * 1.5
    joint_w = latch_width - wall_thickness*2 - clearance*2
    
    if render_mode == 0:
        # over_center.scad anchors this cuboid BOTTOM+RIGHT, so it spans
        # x = -base_length/2 .. 0 and the pivot sits on its right-hand end.
        # cq's box() is centred, so it needs the extra -base_length/4 shift;
        # without it the base straddled the pivot and the whole linkage was
        # 10 mm out along X.
        base = cq.Workplane("XY").box(base_length/2, latch_width, pin_d*2.5).translate((-base_length/4, 0, pin_d*1.25))
        
        if cdg_mount_type == 1:
            base = base.union(cq.Workplane("XY").box(16, 15, 5).translate((-28, 0, 2.5))).union(cq.Workplane("XY").box(16, 15, 5).translate((28, 0, 2.5)))
        elif cdg_mount_type == 2:
            base = base.union(cq.Workplane("XY").workplane(offset=-4.5).rect(42, 42).workplane(offset=4.5).rect(41.5, 41.5).loft())
            
        slot = cq.Workplane("XY").box(pin_d*4, joint_w + clearance*2, pin_d*4).translate((0, 0, pin_d*1.5))
        # Every pin, bore and barrel in this linkage runs ACROSS the latch, along
        # Y — that is the axis the lever and the link swing about, and it is what
        # over_center.scad builds with `rotate([90,0,0]) cyl(...)`. Workplane
        # "YZ" has normal +X, so these used to be extruded along X: the pins ran
        # lengthwise through the mechanism and the round barrels were 4.4 mm
        # discs on their sides instead of 7.5 mm rollers. "XZ" has normal -Y and
        # is the plane that matches the SCAD.
        hole = cq.Workplane("XZ").cylinder(latch_width+1, pin_d/2 + clearance).translate((0, 0, pin_d*1.5))
        base_asm = base.cut(slot).cut(hole)
        
        base_pin = cq.Workplane("XZ").cylinder(latch_width, pin_d/2).translate((0, 0, pin_d*1.5))
        
        lever_hub = cq.Workplane("XZ").cylinder(joint_w, pin_d).translate((0,0,pin_d*1.5))
        lever_arm = cq.Workplane("XY").box(lever_length, joint_w, wall_thickness).translate((lever_length/2, 0, pin_d*1.5))
        lever_slot = cq.Workplane("XY").box(pin_d*3, joint_w - wall_thickness*2 + clearance*2, pin_d*4).translate((lever_length*0.4, 0, pin_d*1.5 + over_center_offset))
        lever = lever_hub.union(lever_arm).cut(lever_slot)
        
        link_pin = cq.Workplane("XZ").cylinder(joint_w, pin_d/2).translate((lever_length*0.4, 0, pin_d*1.5 + over_center_offset))
        
        link_w = joint_w - wall_thickness*2
        link_barrel1 = cq.Workplane("XZ").cylinder(link_w, pin_d).translate((0,0,0))
        link_arm = cq.Workplane("XY").box(lever_length*0.7, link_w, wall_thickness).translate((lever_length*0.35, 0, 0))
        link_barrel2 = cq.Workplane("XZ").cylinder(link_w, pin_d).translate((lever_length*0.7, 0, 0))
        link = link_barrel1.union(link_arm).union(link_barrel2)
        link = link.cut(cq.Workplane("XZ").cylinder(latch_width, pin_d/2 + clearance))
        link = link.rotate((0,0,0),(0,1,0), 20).translate((lever_length*0.4, 0, pin_d*1.5 + over_center_offset))
        
        lever_asm = lever.union(link_pin).union(link)
        lever_asm = lever_asm.rotate((0,0,0),(0,1,0), -15)
        
        # One fuse over all the solids at once, not a chain of pairwise unions.
        # `base_asm.union(base_pin).union(lever_asm)` silently returned base_asm
        # alone — 1391 mm^3 of a 3554 mm^3 mechanism, with the pin, the lever and
        # the link all gone and no error raised — because the second fuse in the
        # chain was handed a compound of solids that only touch or stand clear of
        # each other (a linkage is meant to have running clearance at its
        # joints) and OCCT dropped the arguments instead of failing. A single
        # BRepAlgoAPI fuse over the whole list keeps every part: the ones that
        # interpenetrate merge, the ones separated by clearance stay as their own
        # solids, exactly as OpenSCAD's union() of the same parts does.
        _parts = [s for w in (base_asm, base_pin, lever_asm) for s in w.val().Solids()]
        result = cq.Workplane("XY").newObject([_parts[0].fuse(*_parts[1:])])
    else:
        catch_x = lever_length * 0.8
        base = cq.Workplane("XY").box(base_length/3, latch_width, pin_d*2.5).translate((catch_x, 0, pin_d*1.25))
        cut = cq.Workplane("XY").box(pin_d*2, latch_width+1, pin_d*3).rotate((0,0,0),(0,1,0), 75).translate((catch_x - base_length/6, 0, pin_d*1.8))
        result = base.cut(cut)
        
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
    "lever_assembly": 0,
    "hook_catch": 1,
}

_target_part = str(PARAM(lambda: target_part, "lever_assembly"))
render_mode = _PART_RENDER_MODE.get(_target_part, render_mode)

result = generate()
