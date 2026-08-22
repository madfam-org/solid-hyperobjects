import cadquery as cq
import math

# The CDG french-cleat interface, inlined so this cartridge is self-contained.
# The sandbox blocks `os`/`sys`, so the shared libs/ tree cannot be reached from
# here — and a standalone cartridge must not depend on the parent repo anyway.
# Keep this in sync with libs/yantra4d/cdg_interfaces.py::cdg_french_cleat.
def cdg_french_cleat(length=100, height=30, depth=15, angle=45):
    rad = math.radians(angle)
    pts = [
        (0, 0),
        (depth, 0),
        (depth, height),
        (depth - (height * math.tan(rad)), height),
    ]
    cleat = cq.Workplane("YZ").polyline(pts).close().extrude(length)
    return cleat.translate((-length / 2, -height / 2, 0)).clean()

def cubic_bezier(p0, p1, p2, p3, steps=20):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts

def build_frame(params):
    width = float(params.get("width", 200))
    height = float(params.get("height", 250))
    depth = float(params.get("depth", 20))
    mounting_style = params.get("mounting_style", "none")
    
    # CDG Interface parameters mapped from project.json
    glazing_thickness = float(params.get("glazing_thickness", 2))
    
    w = 30
    d = depth
    rabbet_d = 10 + glazing_thickness # Rabbet adjusts based on glazing CDG
    rabbet_w = 5
    
    p0 = (w/3, 0)
    p1 = (w/2, d/4)
    p2 = (w/2, d*0.75)
    p3 = (w, d)
    
    bez_pts = cubic_bezier(p0, p1, p2, p3, 20)[1:] # Skip the first point since we'll draw to it
    pts = [(0,0), p0] + bez_pts + [(w, d - rabbet_d), (w - rabbet_w, d - rabbet_d), (w - rabbet_w, 0)]
    
    def make_side(L):
        # Draw on standard XY plane to avoid any mapping bugs, then rotate the Solid
        base = cq.Workplane("XY").polyline(pts).close()
        
        # Extrude along Z
        side = base.extrude((L/2) + w + 10, both=True)
        # Now the solid is extending along Z. The profile is on XY.
        # We want to map it so the length L is on the X axis.
        # Currently length is on Z. 
        # So we rotate around Y axis by 90 degrees.
        # Then Z becomes X, X becomes -Z, Y stays Y.
        
        # We need the profile's X (outward width) to map to Y, and Y (height) to map to Z.
        # Right now, profile X is X, profile Y is Y. 
        # If we rotate around X by 90: Y -> Z, Z -> -Y.
        # The extrusion was along Z. So it becomes -Y.
        # If we then rotate around Z by 90: X -> Y, Y -> -X.
        
        # Let's just create it on "YZ" but safely.
        # What if the duplicate point wasn't fully removed in my math? Let's clean the list just in case.
        clean_pts = []
        for p in pts:
            if not clean_pts or (abs(clean_pts[-1][0] - p[0]) > 1e-5 or abs(clean_pts[-1][1] - p[1]) > 1e-5):
                clean_pts.append(p)
                
        # Draw on YZ plane directly.
        yz_pts = [(p[0], p[1]) for p in clean_pts]
        side = cq.Workplane("YZ").polyline(yz_pts).close().extrude((L/2) + w + 10, both=True)
        
        # Cut miters using explicit 45-degree boolean subtractions
        # We want to keep X - Y <= L/2 (right side)
        cut_pts_1 = [(L/2, 0), (L/2 + 50, 0), (L/2 + 50, 50)]
        cut1 = cq.Workplane("XY").polyline(cut_pts_1).close().extrude(100, both=True)
        
        # We want to keep X + Y >= -L/2 (left side) -> Remove X + Y < -L/2
        cut_pts_2 = [(-L/2, 0), (-L/2 - 50, 0), (-L/2 - 50, 50)]
        cut2 = cq.Workplane("XY").polyline(cut_pts_2).close().extrude(100, both=True)
        
        side = side.cut(cut1).cut(cut2)
        
        return side

    top_edge = make_side(width).translate((0, height/2, 0))
    bottom_edge = make_side(width).rotate((0,0,0), (0,0,1), 180).translate((0, -height/2, 0))
    right_edge = make_side(height).rotate((0,0,0), (0,0,1), -90).translate((width/2, 0, 0))
    left_edge = make_side(height).rotate((0,0,0), (0,0,1), 90).translate((-width/2, 0, 0))
    
    frame = top_edge.union(bottom_edge).union(right_edge).union(left_edge)
    
    if mounting_style == "french_cleat":
        cleat = cdg_french_cleat(length=width - 40)
        cleat = cleat.translate((0, height/3, -depth/2))
        frame = frame.union(cleat)
    
    return frame.clean()

def _seated_panel(params, thickness, z_offset):
    """A flat panel sized to seat in the frame's rabbet, `thickness` thick."""
    width = float(params.get("width", 200))
    height = float(params.get("height", 250))
    # rabbet_w (5mm per side) is how far the rabbet reaches inward from the
    # frame's inner edge — the panel spans the opening plus both rabbet lips.
    rabbet_w = 5
    panel_w = width - (2 * rabbet_w)
    panel_h = height - (2 * rabbet_w)
    return (
        cq.Workplane("XY")
        .box(panel_w, panel_h, thickness)
        .translate((0, 0, z_offset))
        .clean()
    )


def build_glazing(params):
    """The glazing sheet (acrylic/glass) that fronts the artwork."""
    t = float(params.get("glazing_thickness", 2))
    depth = float(params.get("depth", 20))
    # Seats at the front of the rabbet.
    return _seated_panel(params, t, (depth / 2) - (t / 2))


def build_back_panel(params):
    """The backing board that closes the frame behind the artwork."""
    t = 3.0
    depth = float(params.get("depth", 20))
    # Seats at the rear of the rabbet.
    return _seated_panel(params, t, -(depth / 2) + (t / 2))


def build(params):
    """Dispatch on target_part — the platform injects it as the part id."""
    target_part = params.get("target_part", "frame_assembly")
    if target_part == "glazing":
        return build_glazing(params)
    if target_part == "back_panel":
        return build_back_panel(params)
    return build_frame(params)


# Parameters arrive as bare globals injected by the runner, so probe each one
# through a lambda and fall back to the manifest default when it is absent.
def PARAM(probe, default):
    try:
        return probe()
    except NameError:
        return default


result = build({
    "width": PARAM(lambda: width, 200),
    "height": PARAM(lambda: height, 250),
    "depth": PARAM(lambda: depth, 20),
    "glazing_thickness": PARAM(lambda: glazing_thickness, 2),
    "mounting_style": PARAM(lambda: mounting_style, "none"),
    "target_part": PARAM(lambda: target_part, "frame_assembly"),
})

