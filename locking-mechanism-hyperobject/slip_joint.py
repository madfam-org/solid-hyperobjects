import cadquery as cq

latch_width = 15
material_modulus = 1.5
shrinkage_factor = 0.0
clearance = 0.3
cdg_mount_type = 0
render_mode = 0

def generate():
    hinge_t = 2.5 * ((1.5 / max(material_modulus, 0.05)) ** 0.3)
    pin_d = 4

    if render_mode == 0:
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
        
        anchor = cq.Workplane("XY").box(5, latch_width - hinge_t*2 - clearance*2, 18).translate((-17.5, 0, 9))
        leaf = cq.Workplane("XY").box(35, latch_width - hinge_t*2 - clearance*2, hinge_t).translate((0, 0, 18 - hinge_t/2))
        
        result = housing.union(anchor).union(leaf)
    else:
        hub = cq.Workplane("XY").box(12, latch_width - hinge_t*2 - clearance*2, 12)
        blade = cq.Workplane("XY").box(30, latch_width - hinge_t*2 - clearance*2, 10).translate((21, 0, 0))
        pivot = cq.Workplane("YZ").cylinder(latch_width, pin_d/2)
        result = hub.union(blade).cut(pivot).translate((0, 30, 0))
        
    return result.scale(1 + shrinkage_factor/100.0)

if 'show_object' in globals():
    show_object(generate())
else:
    result = generate()
