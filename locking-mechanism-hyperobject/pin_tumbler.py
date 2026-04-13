import cadquery as cq

clearance = 0.3
num_pins = 5
shrinkage_factor = 0.0
cdg_mount_type = 0
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
        
    return result.scale(1 + shrinkage_factor/100.0)

if 'show_object' in globals():
    show_object(generate())
else:
    result = generate()
