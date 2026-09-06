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
    # Font and clip.
    #
    # Neither kernel used to name a font, so each took its own default:
    # OpenSCAD's is Liberation Sans (what the CI image ships via
    # fonts-liberation), CadQuery's is Arial, which is not present on the
    # render image and is silently substituted. The two typefaces set the same
    # string at the same nominal size to different widths, which is the whole
    # of this cartridge's parity gap -- 1.656 mm of bounding box at preset
    # name_plaque (81.656 vs the plate's own 80.0) and 2.80% of volume at
    # door_sign, where the glyph AREA differs at equal depth.
    #
    # Naming the font on both sides removes the substitution. The clip below
    # then makes the bound structural rather than font-dependent: raised text
    # is intersected with the plate footprint, so no `message` in the
    # parameter's 30-character budget can push the bounding box past
    # base_width no matter which face the platform resolves. A cut can never
    # grow the box, so the engraved branch needs the font only.
    FONT = "Liberation Sans"

    if raised:
        # Extrude text upward from the top surface, clipped to the plate.
        text = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness)
            .text(message, font_size, text_depth, font=FONT)
        )
        clip = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness)
            .rect(base_width, base_height)
            .extrude(text_depth)
        )
        result = base.union(text.intersect(clip))
    else:
        # Carve text into the top surface
        text = (
            cq.Workplane("XY")
            .workplane(offset=base_thickness - text_depth)
            .text(message, font_size, text_depth + 0.1, font=FONT)
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
