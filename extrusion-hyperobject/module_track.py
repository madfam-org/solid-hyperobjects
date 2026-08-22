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

# Polymer track body
w = 30 * profile_scale
h = 15 * profile_scale

result = (
    cq.Workplane("XY")
    .box(w, h, extrusion_length)
    .faces(">Z")
    .hole(5 * profile_scale) # Add a repetitive feature
)
