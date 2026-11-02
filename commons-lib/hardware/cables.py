# SPDX-License-Identifier: CERN-OHL-W-2.0
# requires:
"""Generic cable components, in millimetres. Each takes its own parameter dict.

Local connector frame: X is width, Y is height, +Z points to the mating tip;
the housing lies behind z=0. Cable paths run along X in the XY plane. Geometry
is an interface envelope, without individual electrical contacts or threads.
"""
import math

import cadquery as cq


def cable_section(w, h, profile):
    """One closed profile. An obround retains its exact published extents."""
    wp = cq.Workplane("XY")
    if profile == "round":
        return wp.circle(w / 2)
    if profile == "dshape":
        return wp.polyline([(-w/2, h/2), (w/2, h/2),
                            (w*.38, -h/2), (-w*.38, -h/2)]).close()
    if profile == "obround" and w > h:
        return wp.slot2D(w, h)
    return wp.rect(w, h)


def connector_plug(p):
    """Mating shell and generic overmold, one body. Optional bore or pin.

    width/height/length are the shell; body_* the archetype overmold.
    A positive pin_length adds a coaxial pin. A bore cuts through the shell
    and overmold's front by 0.2 mm, not through the complete cable housing.
    """
    w, h, length = p["width"], p["height"], p["length"]
    bw, bh, bl = p["body_width"], p["body_height"], p["body_length"]
    shell = cable_section(w, h, p["profile"]).extrude(length + .2).translate((0, 0, -.2))
    body = cq.Workplane("XY").rect(bw, bh).extrude(-bl)
    shape = body.union(shell)
    if p.get("pin_length", 0) > 0:
        pin = cq.Workplane("XY").circle(p["pin_diameter"] / 2).extrude(
            p["pin_length"] + .2).translate((0, 0, length - .2))
        shape = shape.union(pin)
    if p.get("bore", 0) > 0:
        hole = cq.Workplane("XY").circle(p["bore"] / 2).extrude(
            length + 1.2).translate((0, 0, -.2))
        shape = shape.cut(hole)
    return shape


def strain_relief(p):
    """Tapered boot along +X, overlapping housing and jacket by 0.2 mm."""
    return (cq.Workplane("YZ").circle(p["body_diameter"] / 2)
            .workplane(offset=p["length"]).circle(p["jacket_diameter"] / 2)
            .loft().translate((p["start"], 0, 0)))


def cable_path(p):
    """Centerline and endpoint. Arc/s-curve share horizontal end tangents."""
    length, bow = p["span"], p["bow"]
    if p["path"] == "straight" or bow == 0:
        return cq.Workplane("XY").moveTo(0, 0).lineTo(length, 0), length
    sign = -1 if p["path"] == "s_curve" else 1
    points = [(0, 0), (length*.25, bow), (length*.5, 0 if sign < 0 else bow),
              (length*.75, bow*sign), (length, 0)]
    wire = cq.Workplane("XY").spline(points, tangents=[(1, 0), (1, 0)])
    return wire, length


def cable_jacket(p):
    """Circular jacket swept over a planar path, terminating on X axis."""
    path, _ = cable_path(p)
    return cq.Workplane("YZ").circle(p["diameter"] / 2).sweep(path)


def coil_cord(p):
    """Helix about +X with straight leads. Half-integer turns only.

    The specified OD is outside the wire, so centerline radius is
    (OD - diameter)/2. Leads end at the helix endpoint's actual Y/Z rather
    than pretending a half-integer helix closes onto its starting axis.
    """
    turns, pitch, diameter = p["turns"], p["pitch"], p["diameter"]
    if turns <= 0 or abs(turns*2 - round(turns*2)) > 1e-8:
        raise ValueError("coil turns must be a positive multiple of 0.5")
    if pitch <= diameter or p["outside_diameter"] <= 2*diameter:
        raise ValueError("coil pitch and OD must separate adjacent turns")
    radius = (p["outside_diameter"] - diameter) / 2
    height = turns * pitch
    helix = cq.Wire.makeHelix(pitch, height, radius)
    tube = cq.Workplane("XZ").center(radius, 0).circle(diameter / 2).sweep(
        cq.Workplane(obj=helix), isFrenet=True)
    # Rotate the Z-axis helix onto X. Its endpoints are evaluated, not rounded.
    tube = tube.rotate((0, 0, 0), (0, 1, 0), 90)
    end_y, end_z = radius*math.sin(2*math.pi*turns), -radius*math.cos(2*math.pi*turns)
    return tube, (0.0, 0.0, -radius), (height, end_y, end_z)


def cable_ferrite(p):
    """Generic ferrite casing, coaxial with a straight jacket section."""
    return (cq.Workplane("YZ").circle(p["diameter"] / 2)
            .extrude(p["length"]).translate((p["start"], 0, 0)))


def coil_with_leads(p):
    """One continuous sweep, with tangent spline leads on an exact helix.

    Joining independently swept lead tubes by endpoint balls can leave
    tessellation cracks at OCCT's shared seams. This path has matched endpoint
    tangents and is swept once, so it has no Boolean junction at the coil ends.
    """
    turns, pitch, d = p['turns'], p['pitch'], p['diameter']
    if turns <= 0 or abs(turns*2-round(turns*2)) > 1e-8:
        raise ValueError('coil turns must be a positive multiple of 0.5')
    if pitch <= d or p['outside_diameter'] <= 2*d:
        raise ValueError('coil turns must remain separated')
    radius = (p['outside_diameter']-d)/2
    helix = cq.Wire.makeHelix(pitch, turns*pitch, radius).rotate(
        (0,0,0),(0,1,0),90)
    a, b = helix.positionAt(0), helix.positionAt(1)
    lead = p['lead']
    start, end = cq.Vector(a.x-lead,a.y,a.z), cq.Vector(b.x+lead,b.y,b.z)
    first = cq.Edge.makeSpline([start, a], tangents=[cq.Vector(1,0,0),helix.tangentAt(0)])
    last = cq.Edge.makeSpline([b, end], tangents=[helix.tangentAt(1),cq.Vector(1,0,0)])
    wire = cq.Wire.assembleEdges([first, *helix.Edges(), last])
    shape = cq.Workplane('YZ', origin=start.toTuple()).circle(d/2).sweep(
        cq.Workplane(obj=wire), isFrenet=True)
    return shape, start.toTuple(), end.toTuple()
