import cadquery as cq
import json
import argparse

def build(params):
    width_units = int(params.get('width_units', 2))
    depth_units = int(params.get('depth_units', 2))
    bp_enable_screws = params.get('bp_enable_screws', False)
    bp_corner_radius = float(params.get('bp_corner_radius', 3.75))
    
    pitch = 42.0
    overall_z = 5.0
    
    total_w = width_units * pitch
    total_d = depth_units * pitch
    
    # Baseplate Profile
    bp = (
        cq.Workplane("XY")
        .box(total_w, total_d, overall_z)
        .edges("|Z")
        .fillet(bp_corner_radius)
        .translate((0, 0, overall_z/2.0))
    )
    
    # Top prismoid indents: 39.2 mm at the floor opening out to 42.0 mm at the
    # top over the full 5 mm, with the same corner radius as the plate.
    # baseplate.scad cuts this with prismoid(size1=[39.2,39.2], size2=[42,42],
    # h=5, rounding1=bp_corner_radius, rounding2=bp_corner_radius).
    #
    # The rounding has to be built into the lofted sections. A loft between two
    # plain rects has no vertical edges at all — its four side edges are slanted
    # — so `.edges("|Z")` selected nothing, `.fillet()` raised "Fillets requires
    # that edges be selected", and the bare `except Exception: pass` swallowed
    # it. Every pocket was cut with SHARP corners, which is why the baseplate
    # came out 9.29% lighter than the OpenSCAD one and why its cups would not
    # have seated on the corner radii. Lofting two filleted sketches gives the
    # rounded prismoid the SCAD builds, and cannot fail silently.
    #
    # The 0.1 mm overshoot at each end is kept so the cutter is not coplanar
    # with the plate's faces, but it now follows the prismoid's own taper
    # instead of stretching the same 39.2 -> 42.0 run over 5.2 mm, which
    # shallowed the draft.
    eps = 0.1
    taper = (42.0 - 39.2) / overall_z
    sk_bottom = (
        cq.Sketch().rect(39.2 - taper * eps, 39.2 - taper * eps)
        .vertices().fillet(bp_corner_radius)
        .moved(cq.Location(cq.Vector(0, 0, -eps)))
    )
    sk_top = (
        cq.Sketch().rect(42.0 + taper * eps, 42.0 + taper * eps)
        .vertices().fillet(bp_corner_radius)
        .moved(cq.Location(cq.Vector(0, 0, overall_z + eps)))
    )
    prismoid = cq.Workplane("XY").placeSketch(sk_bottom, sk_top).loft()
    
    start_x = -total_w/2.0 + pitch/2.0
    start_y = -total_d/2.0 + pitch/2.0
    
    for x in range(width_units):
        for y in range(depth_units):
            cx = start_x + x * pitch
            cy = start_y + y * pitch
            bp = bp.cut(prismoid.translate((cx, cy, 0)))
            
            if bp_enable_screws:
                hole = cq.Workplane("XY").circle(3.2/2.0).extrude(10).translate((cx, cy, -1))
                bp = bp.cut(hole)
                
    return bp.clean()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()
    
    params = json.loads(args.params)
    res = build(params)
    
    if args.out:
        cq.exporters.export(res, args.out)
