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

    # Font and clip -- see plaque.py for the full rationale. In short: neither
    # kernel named a font, so OpenSCAD used Liberation Sans (the CI image's
    # font) and CadQuery used Arial, which is absent there and silently
    # substituted by a wider face. That is this cartridge's entire parity gap
    # (1.656 mm of bounding box at name_plaque, 2.80% of volume at door_sign).
    # Name the font on both sides, and clip raised text to the plate so the
    # bounding box can never grow with the string.
    FONT = "Liberation Sans"

    if raised:
        text_solid = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness)
            .text(message, font_size, text_depth, font=FONT)
        )
        # The clip is the tag's own ROUNDED outline, not a plain rect, so the
        # text is bounded by the same silhouette the plate has.
        clip = (
            cq.Workplane("XY", origin=(0, 0, base_thickness))
            .rect(base_width, base_height)
            .extrude(text_depth)
            .edges("|Z")
            .fillet(corner_r)
        )
        result = base.union(text_solid.intersect(clip))
    else:
        text_solid = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness - text_depth)
            .text(message, font_size, text_depth + 0.1, font=FONT)
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
