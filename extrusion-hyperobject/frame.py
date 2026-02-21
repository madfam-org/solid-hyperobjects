import cadquery as cq

extrusion_length = globals().get('extrusion_length', 150)
profile_scale = globals().get('profile_scale', 1.0)
wall_thickness = globals().get('wall_thickness', 2.0)

# Aluminum frame profile (hollow tube)
outer_w = 40 * profile_scale
outer_h = 40 * profile_scale
inner_w = outer_w - (wall_thickness * 2)
inner_h = outer_h - (wall_thickness * 2)

result = (
    cq.Workplane("XY")
    .rect(outer_w, outer_h)
    .rect(inner_w, inner_h)
    .extrude(extrusion_length)
)
