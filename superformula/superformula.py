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


# Smallest radius any sampled point is allowed to collapse to.  The inner void
# is inset by a CONSTANT ``wall_thickness``; where a superformula valley is
# itself narrower than the wall, an unclamped inset would send the radius
# negative and turn the ring inside out.  Flooring it keeps the void strictly
# inside the outer surface, which is what keeps deeply lobed presets
# (``sea_urchin``, m1 = 12) a single body at their own declared wall.
MIN_RADIUS = 0.5


def _ring(z, height, radius, m, n1, n2, n3, num_pts, inset=0.0, z_at=None):
    """One sampled cross-section as 3D points at height *z*.

    *z_at* overrides the height the PROFILE is evaluated at, without moving the
    points in Z; the void's overshoot cap uses it to continue the rim section
    straight up past the top of the vase.
    """
    rz = _vase_radius(z if z_at is None else z_at, height, radius)
    pts = []
    for i in range(num_pts):
        theta = i * 2.0 * math.pi / num_pts
        rr = max(MIN_RADIUS, rz * superformula_radius(theta, m, n1, n2, n3) - inset)
        pts.append((rr * math.cos(theta), rr * math.sin(theta), z))
    return pts


def _skin(rings):
    """Build a closed solid by skinning a bottom-to-top stack of equal-length rings.

    Each adjacent pair of rings is joined by a band of triangles and the two
    ends are closed with a centroid fan, so the result is a genuine loft of the
    sampled cross-sections.  This is what makes the two kernels agree: a
    ``hull()`` of consecutive sections (which is what both sides used to do)
    fills in the superformula's CONCAVE lobes, because a convex hull cannot be
    concave.  On the default profile that inflated the outer body to 1.38e6 mm3
    against 769e3 for the true polygon — the sweep's parity gap.
    """
    num_pts = len(rings[0])
    num_rings = len(rings)
    verts = []
    for r in rings:
        verts.extend(r)

    def vid(ri, i):
        return ri * num_pts + (i % num_pts)

    faces = []
    for ri in range(num_rings - 1):
        for i in range(num_pts):
            a, b = vid(ri, i), vid(ri, i + 1)
            c, d = vid(ri + 1, i + 1), vid(ri + 1, i)
            faces.append((a, b, c))
            faces.append((a, c, d))

    # Bottom cap, wound so its normal points down and out of the solid.
    verts.append((0.0, 0.0, rings[0][0][2]))
    bottom = len(verts) - 1
    for i in range(num_pts):
        faces.append((bottom, vid(0, i + 1), vid(0, i)))

    # Top cap, wound the other way.
    verts.append((0.0, 0.0, rings[-1][0][2]))
    top = len(verts) - 1
    for i in range(num_pts):
        faces.append((top, vid(num_rings - 1, i), vid(num_rings - 1, i + 1)))

    vecs = [cq.Vector(*v) for v in verts]
    tris = [
        cq.Face.makeFromWires(
            cq.Wire.makePolygon([vecs[a], vecs[b], vecs[c], vecs[a]])
        )
        for a, b, c in faces
    ]
    return cq.Solid.makeSolid(cq.Shell.makeShell(tris))


def build(params):
    """Superformula vase — CadQuery translation.

    Builds a hollow, open-topped vase by skinning superformula cross-sections
    whose radius follows a sinusoidal taper along Z.  The inner void is the
    same skin inset by a constant ``wall_thickness``, floored at
    ``wall_thickness`` so the vase has a base, and run past the rim so the bore
    breaks through and the vase is OPEN at the top.

    Both shells sample the profile at the SAME z, so the wall is
    ``wall_thickness`` everywhere.  The previous implementation stacked thin
    extruded slabs and indexed the inner stack by ``i * slice_h + wall``, which
    evaluated the void's radius a wall higher up the taper than the outer slab
    it sat inside: the wall came out 0.50 mm near the base and 3.47 mm over the
    descending half against a nominal 2.0, and clamping that void at
    ``height - 0.01`` left a 0.01 mm lid that sealed the interior into an
    undrainable cavity (the CI's "body 1 has negative volume").
    """
    m1 = float(params.get('m1', 5))
    n1 = float(params.get('n1', 2))
    n2 = float(params.get('n2', 7))
    n3 = float(params.get('n3', 7))
    height = float(params.get('height', 100))
    wall_thickness = float(params.get('wall_thickness', 2))
    radius = float(params.get('radius', 40))

    steps = max(20, int(height / 3))
    num_pts = 64

    zs = [i * height / steps for i in range(steps + 1)]

    # --- Outer shell: a true skin of the sampled cross-sections -------------
    outer = _skin([
        _ring(z, height, radius, m1, n1, n2, n3, num_pts) for z in zs
    ])

    # --- Inner void: same sections, constant inset, floored, open at top ----
    # Sampled at the outer shell's own z values so the two surfaces stay
    # parallel, starting at the floor and ending ABOVE the rim.  The final ring
    # repeats the rim cross-section (z_at = height) one millimetre higher, so
    # the cut breaks cleanly through the top face instead of leaving a lid.
    void_zs = [wall_thickness] + [z for z in zs if z > wall_thickness]
    if void_zs[-1] < height:
        void_zs.append(height)
    rings = [
        _ring(z, height, radius, m1, n1, n2, n3, num_pts, inset=wall_thickness)
        for z in void_zs
    ]
    rings.append(
        _ring(height + 1.0, height, radius, m1, n1, n2, n3, num_pts,
              inset=wall_thickness, z_at=height)
    )
    inner = _skin(rings)

    result = cq.Workplane("XY").newObject([outer]).cut(
        cq.Workplane("XY").newObject([inner])
    )

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
