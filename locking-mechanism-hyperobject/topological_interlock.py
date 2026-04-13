import cadquery as cq

matrix_size = 3
clearance = 0.3
shrinkage_factor = 0.0
cdg_mount_type = 0
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
        
    return result.scale(1 + shrinkage_factor/100.0)

if 'show_object' in globals():
    show_object(generate())
else:
    result = generate()
