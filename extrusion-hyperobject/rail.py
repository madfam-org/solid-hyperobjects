import cadquery as cq


# ─── Sandbox-safe parameter access ───────────────────────────────────────────
# cq_runner injects parameters as module globals but blocks the globals()
# builtin, so reading them via globals().get() failed every production render
# of this cartridge. The NameError probe below needs no blocked builtins.
def PARAM(getter, default):
    try:
        return getter()
    except Exception:
        return default


extrusion_length = float(PARAM(lambda: extrusion_length, 150))
profile_scale = float(PARAM(lambda: profile_scale, 1.0))
degradation_state = float(PARAM(lambda: degradation_state, 0))

# Create an I-beam representing the rail body
w = 50 * profile_scale
h = 80 * profile_scale
web = 10 * profile_scale
chamfer = 5 * profile_scale

# Simple profile extrusion for a rail
result = (
    cq.Workplane("XY")
    .box(w, h, extrusion_length)
    .edges("|Z")
    .chamfer(chamfer)
)

# Apply a generic deformation based on degradation_state.
# The top face is already chamfered, so the wear fillet has to stay inside the
# material the chamfer left behind: a radius approaching the chamfer width or
# the profile's smallest half-dimension overruns the face and OCCT aborts with
# "BRep_API: command not done". Bounding it by the real geometry keeps the full
# 0-10 slider range (and the shipped 'decaying_rail' preset) renderable.
if degradation_state > 0:
    # The chamfered top face tops out near chamfer*(1+sqrt(2))/sqrt(2) ~= 1.71*chamfer
    # (verified by bisection across profile_scale 0.5-3.0); 1.6 keeps a safety margin
    # while still letting the slider travel most of its range visibly.
    max_wear = min(1.6 * chamfer, w / 2.0, h / 2.0, extrusion_length / 2.0)
    result = result.edges(">Z").fillet(min(max_wear, degradation_state * 2))
