"""Hinged ring shell. Original parametric construction study.
Two semicircular shells with complementary same-side hinge knuckles and a separate pin; nominal assembly clearance only.
No physical fit, retention, strength, or material qualification.
Loose parts are deliberate; they are not a solved assembly.
"""

DEFAULT_SIZE = 20
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


# The unpacked shells share a ring centre and hinge axis (x=11, y=0).
# Shell edges have a 0.2 mm nominal gap; the knuckles have a 0.2 mm axial gap.
a = ring(10, 12, 5).cut(box(30, 15.1, 9, 0, -7.45, 2.5))
b = ring(10, 12, 5).cut(box(30, 15.1, 9, 0, 7.45, 2.5))
a = a.cut(cyl(2.7, 3.5, 11, 0, 2.5)).union(eye(1, 2.5, 2.4, 11, 0, 0))
b = b.cut(cyl(2.7, 3.5, 11, 0, -1)).union(eye(1, 2.5, 2.4, 11, 0, 2.6))
# Recut the complete bore after union so shell material cannot occlude it.
a = a.cut(cyl(1, 7, 11, 0, -1))
b = b.cut(cyl(1, 7, 11, 0, -1))
r = pack([a, b, cyl(0.8, 5)], 32)
result = r
