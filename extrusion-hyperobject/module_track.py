import cadquery as cq

extrusion_length = globals().get('extrusion_length', 150)
profile_scale = globals().get('profile_scale', 1.0)

# Polymer track body
w = 30 * profile_scale
h = 15 * profile_scale

result = (
    cq.Workplane("XY")
    .box(w, h, extrusion_length)
    .faces(">Z")
    .hole(5 * profile_scale) # Add a repetitive feature
)
