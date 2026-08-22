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
matrix_size = int(PARAM(lambda: matrix_size, 3))
clearance = float(PARAM(lambda: clearance, 0.3))
shrinkage_factor = float(PARAM(lambda: shrinkage_factor, 0.0))
cdg_mount_type = int(PARAM(lambda: cdg_mount_type, 0))
render_mode = 0

def generate():
    block_s = 15
    sz = block_s - clearance
    
    if render_mode == 0:
        base_block = cq.Workplane("XY").box(sz, sz, sz)
        tabs = cq.Workplane("YZ").cylinder(sz*0.6, sz/4).translate((sz/2, 0, 0)).union(cq.Workplane("XZ").cylinder(sz*0.6, sz/4).translate((0, sz/2, 0)))
        neg_tabs = cq.Workplane("YZ").cylinder(sz*0.8, sz/4 + clearance/2).translate((-sz/2, 0, 0)).union(cq.Workplane("XZ").cylinder(sz*0.8, sz/4 + clearance/2).translate((0, -sz/2, 0)))
        single_block = base_block.union(tabs).cut(neg_tabs)
        
        matrix = cq.Workplane("XY")
        for x in range(matrix_size):
            for y in range(matrix_size):
                matrix = matrix.union(single_block.translate((x*block_s, y*block_s, 0)))
        result = matrix
    else:
        frame_w = matrix_size * block_s + block_s
        wall_t = 4
        
        frame = cq.Workplane("XY").box(frame_w + wall_t*2, frame_w + wall_t*2, block_s).translate((frame_w/2, frame_w/2, 0))
        hollow = cq.Workplane("XY").box(frame_w, frame_w, block_s+1).translate((frame_w/2, frame_w/2, 0))
        
        if cdg_mount_type == 1:
            frame = frame.union(cq.Workplane("XY").box(16, 15, 5).translate((-8, 0, -block_s/2+2.5))).union(cq.Workplane("XY").box(16, 15, 5).translate((frame_w+8, 0, -block_s/2+2.5)))
        elif cdg_mount_type == 2:
            frame = frame.union(cq.Workplane("XY").workplane(offset=-4.5-block_s/2).rect(42, 42).workplane(offset=4.5).rect(41.5, 41.5).loft().translate((frame_w/2, frame_w/2, 0)))
            
        result = frame.cut(hollow)
        
        for x in range(matrix_size):
            cut1 = cq.Workplane("XZ").cylinder(block_s*0.8, block_s/4 + clearance/2).translate((block_s/2 + x*block_s, 0, 0))
            cut2 = cq.Workplane("YZ").cylinder(block_s*0.8, block_s/4 + clearance/2).translate((0, block_s/2 + x*block_s, 0))
            result = result.cut(cut1).cut(cut2)
            
        result = result.translate((-block_s/2, -block_s/2, 0))
        
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
    "interlocking_blocks": 0,
    "peripheral_frame": 1,
}

_target_part = str(PARAM(lambda: target_part, "interlocking_blocks"))
render_mode = _PART_RENDER_MODE.get(_target_part, render_mode)

result = generate()
