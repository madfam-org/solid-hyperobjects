import cadquery as cq
import math
import json
import argparse


def torus_knot_path(p, q, torus_r, segments, scale):
    """Generate 3D points along a (p,q) torus knot.

    The torus knot winds p times around the torus axis and q times
    around the tube center.  The coordinate formula places the knot
    on a torus of effective radius ``torus_r / 3`` so the default
    parameters produce a model that fits comfortably on a print bed.
    """
    pts = []
    for i in range(segments):
        t = i * 2 * math.pi / segments
        r = math.cos(q * t) + 2
        x = r * math.cos(p * t) * torus_r / 3.0 * scale
        y = r * math.sin(p * t) * torus_r / 3.0 * scale
        z = -math.sin(q * t) * torus_r / 3.0 * scale
        pts.append((x, y, z))
    return pts


def build(params):
    p = int(params.get("p", 2))
    q = int(params.get("q", 3))
    tube_radius = float(params.get("tube_radius", 4))
    torus_radius = float(params.get("torus_radius", 30))
    segments = int(params.get("segments", 120))
    scale_factor = float(params.get("scale_factor", 1.0))

    path_pts = torus_knot_path(p, q, torus_radius, segments, scale_factor)

    # Build the path as a closed 3-D spline wire
    vectors = [cq.Vector(*pt) for pt in path_pts]
    path_wire = cq.Wire.makeSpline(vectors, periodic=True)

    # Sweep a circular cross-section along the wire using Frenet framing
    result = (
        cq.Workplane("XY")
        .circle(tube_radius)
        .sweep(path_wire, isFrenet=True)
    )

    return result.clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CadQuery torus knot generator")
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)
    res = build(params)

    if args.out:
        cq.exporters.export(res, args.out)
