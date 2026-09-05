import cadquery as cq
import math
import json
import argparse


def build(params, part="planter"):
    turns = int(params.get("turns", 3))
    spacing = float(params.get("spacing", 8))
    wall_thickness = float(params.get("wall_thickness", 2))
    base_diameter = float(params.get("base_diameter", 60))
    height = float(params.get("height", 80))
    drainage = params.get("drainage", True)
    if isinstance(drainage, str):
        drainage = drainage.lower() in ("true", "1", "yes")

    base_r = base_diameter / 2.0
    top_r = base_r + turns * spacing

    # ── Saucer ──────────────────────────────────────────────────────
    if part == "saucer":
        saucer_height = 8.0
        lip = 5.0
        outer = (
            cq.Workplane("XY")
            .circle(top_r + lip)
            .extrude(saucer_height)
        )
        inner = (
            cq.Workplane("XY")
            .workplane(offset=2.0)
            .circle(top_r + lip - 2.0)
            .extrude(saucer_height)
        )
        return outer.cut(inner).clean()

    # ── Planter body ────────────────────────────────────────────────
    # Tapered cylinder shell created by lofting two circles and
    # subtracting a slightly smaller lofted inner volume.
    outer = (
        cq.Workplane("XY")
        .circle(base_r)
        .workplane(offset=height)
        .circle(top_r)
        .loft()
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall_thickness)
        .circle(base_r - wall_thickness)
        .workplane(offset=height - wall_thickness)
        .circle(top_r - wall_thickness)
        .loft()
    )
    planter = outer.cut(inner)

    # ── Drainage holes ──────────────────────────────────────────────
    if drainage:
        hole_d = 5.0
        hole_count = 4
        for i in range(hole_count):
            angle = i * 2 * math.pi / hole_count
            cx = base_r * 0.5 * math.cos(angle)
            cy = base_r * 0.5 * math.sin(angle)
            hole = (
                cq.Workplane("XY")
                .center(cx, cy)
                .circle(hole_d / 2.0)
                .extrude(wall_thickness + 2)
                .translate((0, 0, -1))
            )
            planter = planter.cut(hole)

    return planter.clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CadQuery spiral planter generator")
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--part", type=str, default="planter")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)

    # The part comes from `params["target_part"]` first and only falls back to
    # `--part`. The platform runner
    # (apps/api/services/engine/cq_runner.py:50) sets sys.argv to exactly
    # ["<script>", "--params", <json>, "--out", <path>] and executes the file,
    # so this block DOES run under the platform -- but `--part` is never among
    # the arguments it passes, and `args.part` therefore always fell back to
    # "planter". Both declared parts rendered the planter: the sweep measured
    # byte-identical volumes for `planter` and `saucer` and a 72 mm AABB gap
    # against spiral_planter.scad, which dispatches on render_mode correctly.
    part = params.get("target_part") or args.part
    res = build(params, part=part)

    # Name the result so the runner's own lookup finds it directly rather than
    # falling through to its "last CadQuery object created" scan.
    result = res

    if args.out:
        cq.exporters.export(res, args.out)
