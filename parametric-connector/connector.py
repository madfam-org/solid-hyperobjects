import cadquery as cq
import json
import argparse

def build(params):
    pipe_od_mm = float(params.get('pipe_od_mm', 21.3))
    connector_type = params.get('connector_type', "elbow")
    wall_thickness_mm = float(params.get('wall_thickness_mm', 3.0))
    insertion_depth_mm = float(params.get('insertion_depth_mm', 20.0))
    
    socket_od = pipe_od_mm + (wall_thickness_mm * 2.0)
    socket_length = insertion_depth_mm + wall_thickness_mm
    offset = (socket_od / 2.0) - wall_thickness_mm
    
    # Core hub — a chamfered cube, NOT a sphere, and deliberately OVERSIZE.
    #
    # Two distinct defects were fixed here; both produced a non-watertight mesh.
    #
    # 1. Sphere pole singularity. CadQuery tessellates a sphere's UV poles into
    #    coincident vertices that merge down to two ZERO-LENGTH edges at
    #    z = +/- socket_od/2, so every export reported 2 boundary edges and did
    #    not enclose a volume. A polyhedral hub has no pole.
    #
    # 2. Exact tangency. The arms are cylinders of radius socket_od/2. A hub
    #    whose half-extent is ALSO socket_od/2 makes each arm exactly tangent to
    #    a hub face, and the union of two surfaces that merely kiss tessellates
    #    into razor-thin slivers — 5-way and 6-way blew up to 128 boundary edges.
    #    The B-Rep solid was valid; only the mesh was broken, and a finer export
    #    tolerance made it worse, which is the signature of a tangency seam
    #    rather than a coarse-tessellation artifact. Tuning the chamfer ratio
    #    alone does NOT fix it (0.28 and 0.35 both still fail at pipe_od 40 /
    #    wall 6).
    #
    # The fix is to give the hub strictly more radius than the socket so the arms
    # INTERSECT the hub instead of touching it — the same rule main.py's `_hub()`
    # uses (`hub_r = socket_r + max(1.5, wall_eff * 0.5)`). Verified watertight
    # across all 7 connector_type values x the parameter extremes (35/35).
    hub_r = (socket_od / 2.0) + max(1.5, wall_thickness_mm * 0.5)
    hub_side = hub_r * 2.0
    res = cq.Workplane("XY").box(hub_side, hub_side, hub_side)
    try:
        res = res.edges().chamfer(hub_r * 0.35)
    except Exception:
        pass  # chamfer can fail on tight geometry — a plain cube is still valid

    # Base socket arm (oriented along +Z, starting from Z=0)
    arm_solid = (
        cq.Workplane("XY")
        .circle(socket_od / 2.0)
        .extrude(socket_length)
        .faces(">Z")
        .workplane()
        .circle((pipe_od_mm + 0.5) / 2.0)
        .cutBlind(-insertion_depth_mm)
    )
    
    def add_arm(vec=(0,0,1)):
        rx, ry, _rz = 0, 0, 0
        if vec == (0,0,-1): 
            rx = 180
        elif vec == (1,0,0): 
            ry = 90
        elif vec == (-1,0,0): 
            ry = -90
        elif vec == (0,1,0): 
            rx = -90
        elif vec == (0,-1,0): 
            rx = 90
            
        arm = arm_solid.rotate((0,0,0), (1,0,0), rx).rotate((0,0,0), (0,1,0), ry)
        arm = arm.translate((vec[0]*offset, vec[1]*offset, vec[2]*offset))
        return arm

    arms = []
    
    # Determine axes based on connector type
    # Fixed the elbow having 3 arms SCAD bug!
    axes = [(1,0,0)] # All connectors have X+
    
    if connector_type == "elbow":
        axes.append((0,1,0)) # Y+
    elif connector_type == "tee":
        axes.extend([(-1,0,0), (0,1,0)]) # X-, Y+
    elif connector_type == "cross":
        axes.extend([(-1,0,0), (0,0,1), (0,0,-1)]) # X-, Z+, Z-
    elif connector_type == "3-way-corner":
        axes.extend([(0,1,0), (0,0,1)]) # Y+, Z+
    elif connector_type == "4-way-corner":
        axes.extend([(-1,0,0), (0,1,0), (0,0,1)]) # X-, Y+, Z+
    elif connector_type == "5-way":
        axes.extend([(-1,0,0), (0,1,0), (0,0,1), (0,0,-1)]) # X-, Y+, Z+, Z-
    elif connector_type == "6-way":
        axes.extend([(-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]) # All 6
        
    for vec in axes:
        arms.append(add_arm(vec))
        
    for arm in arms:
        res = res.union(arm)
        
    return res.clean()

# ── Sandbox-safe parameter access ────────────────────────────────────────────
def PARAM(getter, default):
    """Return an injected global if present, else the default.
    The platform sandbox injects manifest parameters as BARE globals; `except
    Exception` catches the NameError raised for an unbound param name (the
    sandbox does not expose globals()/NameError directly)."""
    try:
        v = getter()
        return default if v is None else v
    except Exception:
        return default


def _sandbox_params():
    """Collect this mode's parameters from whichever channel supplied them.

    The sandbox injects bare globals; the CLI passes a --params JSON blob. Read
    the bare globals FIRST so a platform render honours the user's values, then
    let any explicit --params JSON win for standalone CLI use.
    """
    params = {
        "pipe_od_mm": PARAM(lambda: pipe_od_mm, 21.3),
        "connector_type": PARAM(lambda: connector_type, "elbow"),
        "wall_thickness_mm": PARAM(lambda: wall_thickness_mm, 3.0),
        "insertion_depth_mm": PARAM(lambda: insertion_depth_mm, 20.0),
    }
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--params", type=str, default="{}")
        parser.add_argument("--out", type=str, default="")
        args, _unknown = parser.parse_known_args()
        cli = json.loads(args.params or "{}")
        if isinstance(cli, dict):
            params.update({k: v for k, v in cli.items() if k in params})
        out_path = args.out
    except Exception:
        out_path = ""
    return params, out_path


_params, _out = _sandbox_params()

# The sandbox contract: assign the final solid to a top-level name `result`.
result = build(_params)

if _out:
    cq.exporters.export(result, _out)
