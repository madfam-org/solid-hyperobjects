import cadquery as cq
import math
import json
import argparse


def build(params):
    """Julia fractal vase — CadQuery translation.

    Creates a vase by revolving a sinusoidal-taper wall profile around the
    Z axis.  The outer radius oscillates with ``wave_frequency`` and
    ``wave_amplitude``; the inner wall is offset inward by
    ``wall_thickness``.
    """
    height = float(params.get('height', 150))
    base_radius = float(params.get('base_radius', 40))
    wave_frequency = float(params.get('wave_frequency', 5))
    wave_amplitude = float(params.get('wave_amplitude', 10))
    wall_thickness = float(params.get('wall_thickness', 2))
    # project.json declares resolution's default as 100, and vase.scad uses
    # 100. This side defaulted to 50, so any render that omitted the parameter
    # sampled the wall profile at half the density of the OpenSCAD side.
    resolution = int(params.get('resolution', 100))

    steps = max(20, resolution)

    # --- Build vase profile points (outer wall) in XZ plane for revolution ---
    # Radius varies sinusoidally along height.
    outer_pts = []
    for i in range(steps + 1):
        z = i * height / steps
        t = z / height
        r = base_radius + wave_amplitude * math.sin(t * wave_frequency * math.pi)
        outer_pts.append((r, z))

    # Inner wall profile (offset inward by wall_thickness).
    # Walk the outer wall in reverse so the closed polygon is wound correctly.
    inner_pts = []
    for r, z in reversed(outer_pts):
        inner_pts.append((max(1.0, r - wall_thickness), z))

    # Close the profile: bottom edge connects outer start to inner end.
    profile_pts = outer_pts + inner_pts

    # Create the profile wire on XZ and revolve 360 degrees around Z.
    # revolve()'s axis points are LOCAL to the workplane: on "XZ" the local
    # (x, y) map to global (x, z), so the global Z axis is local (0, 1, 0).
    # Passing (0, 0, 1) here would be the XZ plane's own normal and would
    # sweep the profile within its own plane into a flat, zero-volume disc.
    result = (
        cq.Workplane("XZ")
        .polyline(profile_pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
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
