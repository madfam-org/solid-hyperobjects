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
wall_thickness = float(PARAM(lambda: wall_thickness, 2.0))

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
