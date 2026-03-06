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
    resolution = int(params.get('resolution', 50))

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
    result = (
        cq.Workplane("XZ")
        .polyline(profile_pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 0, 1))
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
