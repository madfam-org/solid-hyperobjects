import cadquery as cq
import math
import json
import argparse


def superformula_radius(theta, m, n1, n2, n3):
    """Evaluate the superformula r(theta) for given parameters.

    r = (|cos(m*theta/4)|^n2 + |sin(m*theta/4)|^n3) ^ (-1/n1)
    """
    t1 = abs(math.cos(m * theta / 4.0))
    t2 = abs(math.sin(m * theta / 4.0))
    denom = t1 ** n2 + t2 ** n3
    if denom > 0:
        return denom ** (-1.0 / n1)
    return 1.0


def superformula_points(m, n1, n2, n3, r, num_pts=64):
    """Return a list of (x, y) points tracing a superformula curve scaled by *r*."""
    pts = []
    for i in range(num_pts):
        theta = i * 2.0 * math.pi / num_pts
        rr = superformula_radius(theta, m, n1, n2, n3)
        pts.append((rr * r * math.cos(theta), rr * r * math.sin(theta)))
    return pts


def _vase_radius(z, height, radius):
    """Sinusoidal taper matching the OpenSCAD ``vase_radius`` function.

    Returns ``radius * (0.4 + 0.6 * sin(t * pi))`` where t = z / height.
    """
    t = z / height
    return radius * (0.4 + 0.6 * math.sin(t * math.pi))


def build(params):
    """Superformula vase — CadQuery translation.

    Builds a hollow vase by stacking superformula cross-sections whose
    radius follows a sinusoidal taper along the Z axis.  Each pair of
    adjacent cross-sections is connected via hull (approximated as a
    lofted solid between two wires).  The inner shell is subtracted to
    create the wall thickness.

    Because ``cq.Solid.makeLoft`` can be sensitive to wire topology, this
    implementation uses a stack-of-slices approach: each slice is a thin
    extruded superformula polygon, and successive slices are unioned.
    """
    m1 = float(params.get('m1', 5))
    n1 = float(params.get('n1', 2))
    n2 = float(params.get('n2', 7))
    n3 = float(params.get('n3', 7))
    height = float(params.get('height', 100))
    wall_thickness = float(params.get('wall_thickness', 2))
    radius = float(params.get('radius', 40))

    steps = max(20, int(height / 3))
    slice_h = height / steps
    num_pts = 64

    # --- Outer shell: stack of thin extruded superformula slices -----------
    outer = None
    for i in range(steps):
        z0 = i * slice_h
        z1 = (i + 1) * slice_h
        r0 = _vase_radius(z0, height, radius)
        r1 = _vase_radius(z1, height, radius)
        r_avg = (r0 + r1) / 2.0

        pts = superformula_points(m1, n1, n2, n3, r_avg, num_pts)

        slab = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(slice_h)
            .translate((0, 0, z0))
        )

        if outer is None:
            outer = slab
        else:
            outer = outer.union(slab)

    # --- Inner shell: same shape shrunk inward by wall_thickness -----------
    inner = None
    for i in range(steps):
        z0 = i * slice_h + wall_thickness  # raise floor by wall_thickness
        if z0 >= height:
            break
        z1 = min((i + 1) * slice_h + wall_thickness, height - 0.01)
        slab_h = z1 - z0
        if slab_h <= 0:
            continue

        r0 = _vase_radius(z0, height, radius)
        r1 = _vase_radius(z1, height, radius)
        r_avg = max(1.0, (r0 + r1) / 2.0 - wall_thickness)

        pts = superformula_points(m1, n1, n2, n3, r_avg, num_pts)

        slab = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(slab_h)
            .translate((0, 0, z0))
        )

        if inner is None:
            inner = slab
        else:
            inner = inner.union(slab)

    if inner is not None:
        result = outer.cut(inner)
    else:
        result = outer

    return result.clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)
    res = build(params)

    if args.out:
        cq.exporters.export(res, args.out)
