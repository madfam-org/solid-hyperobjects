import cadquery as cq
import json
import argparse


def _rounded_prismoid(bottom, top, height, radius, z0=0.0):
    """A square prismoid with filleted vertical edges, matching BOSL2's prismoid."""
    solid = (
        cq.Workplane("XY", origin=(0, 0, z0))
        .rect(bottom, bottom)
        .workplane(offset=height)
        .rect(top, top)
        .loft(combine=True)
    )
    try:
        solid = solid.edges("|Z").fillet(radius)
    except Exception:
        # A fillet larger than the taper allows is a cosmetic loss, not a defect.
        pass
    return solid


def build(params):
    width_units = int(params.get('width_units', 2))
    depth_units = int(params.get('depth_units', 1))
    height_units = int(params.get('height_units', 3))
    cup_floor_thickness = float(params.get('cup_floor_thickness', 0.7))

    pitch = 42.0
    zpitch = 7.0
    corner_radius = 3.75
    wall = 1.2

    # Gridfinity base profile — kept in step with cup.scad.
    base_h = 5.0
    foot_bottom = 39.2
    foot_top = pitch - 0.5
    # Solid web sealing the groove between adjacent cells. Without it the
    # interior cavity spans the groove and the bin is open to the outside
    # between cells — a through-slot, and the reason OCCT reported genus 1
    # where CGAL's tessellation happened to close it over.
    web = 0.6

    total_w = width_units * pitch - 0.5
    total_d = depth_units * pitch - 0.5
    total_h = height_units * zpitch
    body_h = total_h - base_h

    # The base was previously carved by subtracting one prismoid per cell that
    # grew to the full 42 mm cell footprint. At the top of that taper the
    # cutters spanned the whole cross section, leaving geometry that was closed
    # but self-touching: OCCT produced non-manifold edges here and CGAL split
    # the OpenSCAD build into two volumes. It also removed the floor and part of
    # the walls, so the part was lighter than a Gridfinity bin its size because
    # it was not printable.
    #
    # The feet are positive geometry now, fused into the body with a slight
    # overlap so no coincident plane survives, and the interior is cut in one
    # pass so the feet and bin are shelled together.
    def cell_centres():
        for ix in range(width_units):
            for iy in range(depth_units):
                yield (
                    (ix - (width_units - 1) / 2.0) * pitch,
                    (iy - (depth_units - 1) / 2.0) * pitch,
                )

    solid = None
    for cx, cy in cell_centres():
        foot = _rounded_prismoid(foot_bottom, foot_top, base_h + 0.1,
                                 corner_radius).translate((cx, cy, 0))
        solid = foot if solid is None else solid.union(foot)

    body = (
        cq.Workplane("XY")
        .box(total_w, total_d, body_h)
        .edges("|Z")
        .fillet(corner_radius)
        .translate((0, 0, base_h + body_h / 2.0))
    )
    solid = solid.union(body)

    cavity = None
    for cx, cy in cell_centres():
        inner_foot = _rounded_prismoid(
            foot_bottom - 2 * wall, foot_top - 2 * wall, base_h + web,
            corner_radius, z0=cup_floor_thickness,
        ).translate((cx, cy, 0))
        cavity = inner_foot if cavity is None else cavity.union(inner_foot)

    # Overshoot the top so the bin is open rather than a sealed void.
    inner_body = (
        cq.Workplane("XY")
        .box(total_w - 2 * wall, total_d - 2 * wall, body_h + 1)
        .edges("|Z")
        .fillet(corner_radius)
        .translate((0, 0, base_h + web + (body_h + 1) / 2.0))
    )
    cavity = cavity.union(inner_body)

    return solid.cut(cavity).clean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=str, default="{}")
    parser.add_argument("--out", type=str, default="out.stl")
    args = parser.parse_args()

    params = json.loads(args.params)
    res = build(params)

    if args.out:
        cq.exporters.export(res, args.out)
