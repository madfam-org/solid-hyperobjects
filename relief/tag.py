import cadquery as cq
import json
import argparse


def build(params):
    message = str(params.get('message', 'Hello'))
    font_size = float(params.get('font_size', 12))
    text_depth = float(params.get('text_depth', 1.5))
    base_width = float(params.get('base_width', 80))
    base_height = float(params.get('base_height', 40))
    base_thickness = float(params.get('base_thickness', 3))
    raised = params.get('raised', True)
    hole_diameter = float(params.get('hole_diameter', 4))
    if isinstance(raised, str):
        raised = raised.lower() in ('true', '1', 'yes')

    corner_r = 4.0
    hole_r = hole_diameter / 2.0
    hole_x = base_width / 2.0 - corner_r - hole_r - 2
    hole_y = base_height / 2.0 - corner_r - hole_r - 2

    # Rounded rectangle base
    base = (
        cq.Workplane("XY")
        .rect(base_width, base_height)
        .extrude(base_thickness)
        .edges("|Z")
        .fillet(corner_r)
    )

    # Hanging hole
    hole = (
        cq.Workplane("XY")
        .circle(hole_r)
        .extrude(base_thickness + 2)
        .translate((hole_x, hole_y, -1))
    )
    base = base.cut(hole)

    if raised:
        text_solid = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness)
            .text(message, font_size, text_depth)
        )
        result = base.union(text_solid)
    else:
        text_solid = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness - text_depth)
            .text(message, font_size, text_depth + 0.1)
        )
        result = base.cut(text_solid)

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
