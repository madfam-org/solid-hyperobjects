import cadquery as cq
import math

# Variables injected by Yantra4D at runtime
latch_width = 15
hook_depth = 2
spring_angle = 15
wall_thickness = 2
base_length = 40
clearance = 0.3
material_modulus = 1.5
shrinkage_factor = 0.0
cdg_mount_type = 0
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
        
        hook = cq.Workplane("XZ").polyline([(0,0), (-ret_off, hook_depth), (hook_l, 0)]).close().extrude(latch_width, both=True).translate((arm_l, 0, arm_t))
        undercut = cq.Workplane("XZ").polyline([(0,0), (hook_l, 0), (0, -arm_t)]).close().extrude(latch_width, both=True).translate((arm_l, 0, 0))
        
        full_arm = arm.union(hook).union(undercut).rotate((0,0,0), (0,1,0), -spring_angle).translate((0, 0, base_h/2 - arm_t/2))
        result = base.union(full_arm)
    else:
        p_l = base_length * 0.4
        p_w = latch_width + clearance*2 + wall_thickness*2
        hook_z = base_h/2 - arm_t/2 + arm_l * math.sin(math.radians(spring_angle)) + hook_depth
        p_h = hook_z + wall_thickness*2
        
        base = cq.Workplane("XY").box(p_l, p_w, p_h).translate((0, 0, p_h/2))
        slot = cq.Workplane("XY").box(p_l+1, latch_width + clearance*2, hook_depth + clearance).translate((0, 0, hook_z - (hook_depth+clearance)/2))
        chamf = cq.Workplane("XY").box(p_l*1.5, latch_width + clearance*2, p_h).rotate((0,0,0),(0,1,0), 35).translate((-p_l/2, 0, p_h))
        
        result = base.cut(slot).cut(chamf).translate((arm_l * math.cos(math.radians(spring_angle)), 0, 0))

    return result.scale(1 + shrinkage_factor/100.0)

if 'show_object' in globals():
    show_object(generate())
else:
    result = generate()
