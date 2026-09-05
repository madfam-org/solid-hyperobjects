import cadquery as cq
import json
import argparse

# ISO 8037 / ISO 8255 standard slide dimensions: (length, width, thickness)
SLIDE_DIMS = {
    0: (76.0, 26.0, 1.0),    # ISO 8037-1 Primary
    1: (75.0, 25.0, 1.0),    # ISO 8037-1 Alternate
    2: (22.0, 22.0, 0.17),   # ISO 8255 #1.5H Cover Glass
    3: (22.0, 22.0, 0.15),   # ISO 8255 #1 Cover Glass
}


def build(params):
    """Microscope slide hyperobject — CadQuery translation.

    Generates a centered rectangular solid whose dimensions are selected by
    ``slide_standard`` (0-3 for ISO presets, 4 for custom dimensions).
    Matches the OpenSCAD ``iso_8037_slide`` module which uses
    ``cube([l, w, t], center=true)``.
    """
    standard = int(params.get('slide_standard', 0))

    if standard == 4:
        length = float(params.get('custom_slide_length', 76.0))
        width = float(params.get('custom_slide_width', 26.0))
        thickness = float(params.get('custom_slide_thickness', 1.0))
    else:
        length, width, thickness = SLIDE_DIMS.get(standard, SLIDE_DIMS[0])

    # CQ box() is centered by default, matching OpenSCAD center=true.
    result = cq.Workplane("XY").box(length, width, thickness)
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
