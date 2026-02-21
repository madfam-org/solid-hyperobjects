import cadquery as cq

# Parameters provided by cq_runner.py
extrusion_length = globals().get('extrusion_length', 150)
profile_scale = globals().get('profile_scale', 1.0)
degradation_state = globals().get('degradation_state', 0)

# Create an I-beam representing the rail body
w = 50 * profile_scale
h = 80 * profile_scale
web = 10 * profile_scale

# Simple profile extrusion for a rail
result = (
    cq.Workplane("XY")
    .box(w, h, extrusion_length)
    .edges("|Z")
    .chamfer(5 * profile_scale)
)

# Apply a generic deformation based on degradation_state
if degradation_state > 0:
    # A simple fillet or chamfer adjustment to simulate wear
    result = result.edges(">Z").fillet(min(15 * profile_scale, degradation_state * 2))
