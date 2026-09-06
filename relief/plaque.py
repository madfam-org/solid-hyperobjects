import cadquery as cq
import json
import argparse


# ── Cross-kernel text ───────────────────────────────────────────────────────
# Three separate divergences sat between this cartridge's two kernels. Each is
# measured against Liberation Sans 2.1.5, the face the render image ships
# (`fonts-liberation`; spec render_environment.APT_PACKAGES).
#
# 1. THE FONT WAS NEVER APPLIED ON THIS SIDE. `Workplane.text(font=...)` reaches
#    OCCT's `Font_FontMgr.FindFont`, which does not raise on a miss: it logs
#    `Font_FontMgr, warning: unable to find font 'Liberation Sans' [regular];
#    'Arial' ... is used instead` and returns the fallback. Naming the font is a
#    NO-OP wherever the family is not in OCCT's own index -- "Liberation Sans",
#    "Arial" and even "NoSuchFontXYZ" gave byte-identical geometry here. Only
#    `fontPath=` registers a face by file. OpenSCAD resolves the name through
#    fontconfig and did get Liberation, so the two kernels set different
#    typefaces while both appeared to name the same one.
# 2. `size=` MEANS DIFFERENT THINGS. OCCT's `StdPrs_BRepFont` takes points at
#    72 dpi; OpenSCAD's `text(size=)` is millimetres. Ratio measured
#    1.388866-1.388882 across seven strings at sizes 8-20 -- 1/0.72 to 1.2e-5.
# 3. `valign="center"` CENTRES ON DIFFERENT THINGS. OpenSCAD centres the glyph
#    BOUNDING BOX; OCCT's Graphic3d_VTA_CENTER centres on the font's metric
#    midline, leaving the text up to 0.75 mm high at size 20.
#
# With all three applied the kernels' text agrees to <= 0.00065 mm on every
# bound across "Hello", "Your Name", "J. Smith", "Max", "Welcome", "With Love"
# and "Room 101". The residual 0.23-0.75% of volume is glyph-curve faceting:
# OpenSCAD linear-extrudes a polygonised outline, OCCT meshes analytic faces.
POINTS_PER_MM = 1.0 / 0.72
FONT_FAMILY = "Liberation Sans"

_FONT_CANDIDATES = (
    "fonts/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/LiberationSans-Regular.ttf",
    "~/Library/Fonts/LiberationSans-Regular.ttf",
    "/Library/Fonts/LiberationSans-Regular.ttf",
)


def _font_path():
    """The Liberation Sans regular face, as a path OCCT will register.

    Raises rather than falling back. A fallback face is the very failure this
    resolves, and OCCT's own fallback is only a warning on stderr that a render
    job does not fail on -- the cartridge would go on producing the wrong glyphs
    quietly, which is how a 2.21% volume gap survived a green-looking fix.
    """
    from pathlib import Path

    here = Path(__file__).resolve().parent
    tried = []
    for candidate in _FONT_CANDIDATES:
        path = (
            here / candidate
            if not candidate.startswith(("/", "~"))
            else Path(candidate).expanduser()
        )
        tried.append(str(path))
        if path.is_file():
            return str(path)
    raise RuntimeError(
        f"{FONT_FAMILY} (LiberationSans-Regular.ttf) was not found, so this "
        f"cartridge's two kernels cannot be made to agree: OCCT substitutes a "
        f"different face silently. Install `fonts-liberation` (the render image's "
        f"own package) or bundle the face in relief/fonts/. Searched: "
        + "; ".join(tried)
    )


def _text_solid(workplane, message, font_size, depth):
    """`message` extruded `depth` deep, matching OpenSCAD's `text(size=font_size)`.

    Centred on its own bounding box in X and Y, the way OpenSCAD's
    `halign="center", valign="center"` centres. The caller positions and clips it.
    """
    built = workplane.text(message, font_size * POINTS_PER_MM, depth, fontPath=_font_path())
    solid = built.val()
    bb = solid.BoundingBox()
    return built.newObject(
        [solid.translate((-(bb.xmin + bb.xmax) / 2.0, -(bb.ymin + bb.ymax) / 2.0, 0))]
    )


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
    # Set through _text_solid so the face, the size and the centring are the
    # OpenSCAD side's -- see the block above. The clip then makes the bound
    # STRUCTURAL rather than font-dependent: raised text is intersected with
    # the plate footprint, so no `message` within the parameter's 30-character
    # budget can push the bounding box past base_width on either kernel. A cut
    # can never grow the box, so the engraved branch needs the face only.
    if raised:
        # Extrude text upward from the top surface, clipped to the plate.
        text = _text_solid(
            cq.Workplane("XY").workplane(offset=base_thickness),
            message,
            font_size,
            text_depth,
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
        text = _text_solid(
            cq.Workplane("XY").workplane(offset=base_thickness - text_depth),
            message,
            font_size,
            text_depth + 0.1,
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
