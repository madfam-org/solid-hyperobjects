"""Hair slide and stick. Original parametric construction study.
Two-slot hair slide and independent tapered retaining stick.
No physical fit, retention, strength, or material qualification.
Loose parts are deliberate; they are not a solved assembly.
"""

DEFAULT_SIZE = 64
import cadquery as cq


def PARAM(getter, default):
    try:
        return getter()
    except NameError:
        return default


size = float(PARAM(lambda: size, DEFAULT_SIZE))
section = float(PARAM(lambda: section, 1.0))
if not DEFAULT_SIZE * 0.8 <= size <= DEFAULT_SIZE * 1.2 or not 0.85 <= section <= 1.15:
    raise ValueError("Size or section outside the reviewed study domain")
S = size / DEFAULT_SIZE


# Section scales the axial depth; all planar interface dimensions follow size.
def cyl(radius, height, x=0, y=0, z=0):
    return (
        cq.Workplane("XY")
        .circle(radius * S)
        .extrude(height * S * section)
        .translate((x * S, y * S, z * S * section))
    )


def ring(inner, outer, height):
    return (
        cq.Workplane("XY")
        .circle(outer * S)
        .circle(inner * S)
        .extrude(height * S * section)
    )


def box(x, y, z, px=0, py=0, pz=0):
    return (
        cq.Workplane("XY")
        .box(x * S, y * S, z * S * section)
        .translate((px * S, py * S, pz * S * section))
    )


def plate(x, y, z):
    return box(x, y, z, 0, 0, z / 2)


def eye(inner, outer, height, x, y, z):
    return ring(inner, outer, height).translate((x * S, y * S, z * S * section))


def poly(points, depth):
    return (
        cq.Workplane("XY")
        .polyline([(x * S, y * S) for x, y in points])
        .close()
        .extrude(depth * S * section)
    )


def oval_ring(rx, ry, wall, depth):
    return (
        cq.Workplane("XY")
        .ellipse(rx * S, ry * S)
        .extrude(depth * S * section)
        .cut(
            cq.Workplane("XY")
            .ellipse((rx - wall) * S, (ry - wall) * S)
            .extrude(depth * S * section)
        )
    )


def slot_ring(length, width, wall, depth):
    return (
        cq.Workplane("XY")
        .slot2D(length * S, width * S)
        .extrude(depth * S * section)
        .cut(
            cq.Workplane("XY")
            .slot2D((length - 2 * wall) * S, (width - 2 * wall) * S)
            .extrude(depth * S * section)
        )
    )


def pack(items, pitch):
    return cq.Workplane("XY").newObject(
        [
            cq.Compound.makeCompound(
                [
                    solid
                    for i, item in enumerate(items)
                    for solid in item.translate((i * pitch * S, 0, 0)).solids().vals()
                ]
            )
        ]
    )


a = plate(48, 20, 3).cut(cyl(3, 7, -16, 0, -2)).cut(cyl(3, 7, 16, 0, -2))
b = poly([(-30, -2), (30, -1), (34, 0), (30, 1), (-30, 2)], 3)
r = pack([a, b], 75)
result = r
