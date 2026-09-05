import cadquery as cq
import json
import argparse

def get_nema_dims(size):
    # Returns (face_w, hole_spacing, shaft_hole_d, screw_d, body_len).
    # Mirrors nema_dims() in mount.scad term for term, body_len included --
    # the reference body needs the motor's length and only the SCAD side
    # carried it.
    if size == 23:
        return (56.4, 47.14, 38.1, 5.5, 56.0)
    elif size == 34:
        return (86.0, 69.6, 73.0, 5.5, 66.0)
    else:  # Default to 17
        return (42.3, 31.0, 22.0, 3.0, 48.0)

def build_nema_reference(params):
    """The simplified NEMA motor reference body -- mount.scad's render_mode == 1.

    A fit-check stand-in for the motor itself, not a printed part: the square
    body, the circular front boss and the shaft, stacked exactly as the SCAD
    side stacks them. Without this the CadQuery `build()` returned the mount
    plate for BOTH parts, which is why the sweep saw byte-identical volumes for
    `mount` and `nema_reference` and a 58 mm AABB gap against OpenSCAD.
    """
    nema_size = int(params.get('nema_size', 17))
    base_thickness = float(params.get('base_thickness', 5))
    fn = int(params.get('fn', 0)) or 48

    face_w, hole_spacing, shaft_hole_d, screw_d, body_len = get_nema_dims(nema_size)

    # mount.scad wraps the whole reference in translate([0, 0, base_thickness]),
    # so every z below is relative to the top of the base plate.
    body = (
        cq.Workplane("XY")
        .box(face_w, face_w, body_len)
        .translate((0, 0, base_thickness + body_len / 2.0))
    )
    # Front face plate (circular boss), h=2 from the reference origin.
    boss = (
        cq.Workplane("XY")
        .circle((shaft_hole_d + 2) / 2.0)
        .extrude(2.0)
        .translate((0, 0, base_thickness))
    )
    # Shaft: starts 10 mm below the reference origin, runs 10 + body_len + 5.
    shaft = (
        cq.Workplane("XY")
        .circle(5 / 2.0)
        .extrude(10.0 + body_len + 5.0)
        .translate((0, 0, base_thickness - 10.0))
    )
    return body.union(boss).union(shaft).clean()


def build_mount(params):
    nema_size = int(params.get('nema_size', 17))
    wall_thickness = float(params.get('wall_thickness', 4))
    base_thickness = float(params.get('base_thickness', 5))
    mounting_style = int(params.get('mounting_style', 0))
    
    face_w, hole_spacing, shaft_hole_d, screw_d, body_len = get_nema_dims(nema_size)
    
    plate_size = face_w + (wall_thickness * 2.0)
    bracket_height = face_w if mounting_style == 1 else 0
    
    mount_hole_d = 5.0
    mount_hole_spacing = plate_size - 10.0
    
    # 1. Base Plate
    # Create the base flat plate on XY plane
    # The SCAD anchor was BOT, meaning it sits on Z=0 and extends up.
    # In CQ, box is centered by default. We can extrude from Z=0 up.
    
    plate = (
        cq.Workplane("XY")
        .rect(plate_size, plate_size)
        .extrude(base_thickness)
    )
    
    # Center shaft hole
    plate = plate.faces(">Z").workplane().circle((shaft_hole_d + 1) / 2.0).cutThruAll()
    
    # 4 Motor Holes
    motor_holes_pts = [
        (hole_spacing/2, hole_spacing/2),
        (hole_spacing/2, -hole_spacing/2),
        (-hole_spacing/2, hole_spacing/2),
        (-hole_spacing/2, -hole_spacing/2)
    ]
    plate = (
        plate.faces(">Z").workplane()
        .pushPoints(motor_holes_pts)
        .circle((screw_d + 0.3) / 2.0)
        .cutThruAll()
    )
    
    # 4 Mounting Holes
    mount_holes_pts = [
        (mount_hole_spacing/2, mount_hole_spacing/2),
        (mount_hole_spacing/2, -mount_hole_spacing/2),
        (-mount_hole_spacing/2, mount_hole_spacing/2),
        (-mount_hole_spacing/2, -mount_hole_spacing/2)
    ]
    plate = (
        plate.faces(">Z").workplane()
        .pushPoints(mount_holes_pts)
        .circle(mount_hole_d / 2.0)
        .cutThruAll()
    )
    
    result = plate
    
    # 2. L-Bracket Vertical Wall
    if mounting_style == 1:
        # Create a vertical wall extending up from the base
        # It's at Y = -plate_size/2 + wall_thickness/2
        # Width = plate_size (X), depth = wall_thickness (Y), height = bracket_height + base_thickness (Z)
        
        # We can build it on XY and move it, or just use a box
        v_wall = (
            cq.Workplane("XY")
            .box(plate_size, wall_thickness, bracket_height + base_thickness)
            .translate((0, -plate_size/2.0 + wall_thickness/2.0, (bracket_height + base_thickness)/2.0))
        )
        
        # Lightening hole in the vertical wall
        # Translated to the center of the vertical wall
        lh_d = bracket_height * 0.5
        v_wall = (
            v_wall.faces(">Y").workplane()
            .circle(lh_d / 2.0)
            .cutThruAll()
        )
        
        result = result.union(v_wall).clean()
        
    return result


def build(params):
    """Dispatch on target_part, as the platform injects it.

    `mount.scad` has dispatched on render_mode since it was written; this side
    never did, so both declared parts resolved to the mount plate.
    """
    target_part = params.get('target_part', 'mount')
    if target_part == 'nema_reference':
        return build_nema_reference(params)
    return build_mount(params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)
    res = build(params)
    
    if args.out:
        cq.exporters.export(res, args.out)
