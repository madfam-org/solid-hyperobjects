import cadquery as cq
import json
import argparse


def build(params):
    message = str(params.get("message", "Hello"))
    font_size = float(params.get("font_size", 12))
    text_depth = float(params.get("text_depth", 1.5))
    base_width = float(params.get("base_width", 80))
    base_height = float(params.get("base_height", 40))
    base_thickness = float(params.get("base_thickness", 3))
    raised = params.get("raised", True)
    if isinstance(raised, str):
        raised = raised.lower() in ("true", "1", "yes")

    # ── Base plate ──────────────────────────────────────────────────
    # Centered on XY, bottom face at Z = 0.
    base = (
        cq.Workplane("XY")
        .box(base_width, base_height, base_thickness)
        .translate((0, 0, base_thickness / 2.0))
    )

    # ── Text ────────────────────────────────────────────────────────
    if raised:
        # Extrude text upward from the top surface
        text = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness)
            .text(message, font_size, text_depth)
        )
        result = base.union(text)
    else:
        # Carve text into the top surface
        text = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness - text_depth)
            .text(message, font_size, text_depth + 0.1)
        )
        result = base.cut(text)

    return result.clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CadQuery text plaque generator")
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)
    res = build(params)

    if args.out:
        cq.exporters.export(res, args.out)
