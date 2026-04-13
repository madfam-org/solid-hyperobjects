import cadquery as cq

lever_length = 30
over_center_offset = 2
wall_thickness = 2.5
latch_width = 15
base_length = 40
clearance = 0.3
shrinkage_factor = 0.0
cdg_mount_type = 0
render_mode = 0

def generate():
    pin_d = wall_thickness * 1.5
    joint_w = latch_width - wall_thickness*2 - clearance*2
    
    if render_mode == 0:
        base = cq.Workplane("XY").box(base_length/2, latch_width, pin_d*2.5).translate((0, 0, pin_d*1.25))
        
        if cdg_mount_type == 1:
            base = base.union(cq.Workplane("XY").box(16, 15, 5).translate((-28, 0, 2.5))).union(cq.Workplane("XY").box(16, 15, 5).translate((28, 0, 2.5)))
        elif cdg_mount_type == 2:
            base = base.union(cq.Workplane("XY").workplane(offset=-4.5).rect(42, 42).workplane(offset=4.5).rect(41.5, 41.5).loft())
            
        slot = cq.Workplane("XY").box(pin_d*4, joint_w + clearance*2, pin_d*4).translate((0, 0, pin_d*1.5))
        hole = cq.Workplane("YZ").cylinder(latch_width+1, pin_d/2 + clearance).translate((0, 0, pin_d*1.5))
        base_asm = base.cut(slot).cut(hole)
        
        base_pin = cq.Workplane("YZ").cylinder(latch_width, pin_d/2).translate((0, 0, pin_d*1.5))
        
        lever_hub = cq.Workplane("YZ").cylinder(joint_w, pin_d).translate((0,0,pin_d*1.5))
        lever_arm = cq.Workplane("XY").box(lever_length, joint_w, wall_thickness).translate((lever_length/2, 0, pin_d*1.5))
        lever_slot = cq.Workplane("XY").box(pin_d*3, joint_w - wall_thickness*2 + clearance*2, pin_d*4).translate((lever_length*0.4, 0, pin_d*1.5 + over_center_offset))
        lever = lever_hub.union(lever_arm).cut(lever_slot)
        
        link_pin = cq.Workplane("YZ").cylinder(joint_w, pin_d/2).translate((lever_length*0.4, 0, pin_d*1.5 + over_center_offset))
        
        link_w = joint_w - wall_thickness*2
        link_barrel1 = cq.Workplane("YZ").cylinder(link_w, pin_d).translate((0,0,0))
        link_arm = cq.Workplane("XY").box(lever_length*0.7, link_w, wall_thickness).translate((lever_length*0.35, 0, 0))
        link_barrel2 = cq.Workplane("YZ").cylinder(link_w, pin_d).translate((lever_length*0.7, 0, 0))
        link = link_barrel1.union(link_arm).union(link_barrel2)
        link = link.cut(cq.Workplane("YZ").cylinder(latch_width, pin_d/2 + clearance))
        link = link.rotate((0,0,0),(0,1,0), 20).translate((lever_length*0.4, 0, pin_d*1.5 + over_center_offset))
        
        lever_asm = lever.union(link_pin).union(link)
        lever_asm = lever_asm.rotate((0,0,0),(0,1,0), -15)
        
        result = base_asm.union(base_pin).union(lever_asm)
    else:
        catch_x = lever_length * 0.8
        base = cq.Workplane("XY").box(base_length/3, latch_width, pin_d*2.5).translate((catch_x, 0, pin_d*1.25))
        cut = cq.Workplane("XY").box(pin_d*2, latch_width+1, pin_d*3).rotate((0,0,0),(0,1,0), 75).translate((catch_x - base_length/6, 0, pin_d*1.8))
        result = base.cut(cut)
        
    return result.scale(1 + shrinkage_factor/100.0)

if 'show_object' in globals():
    show_object(generate())
else:
    result = generate()
