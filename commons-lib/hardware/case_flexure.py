# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: media_cases
"""Original kinematic case spine and retention pockets, not a material solver.

A constant-length circular arc unfolds continuously into a flat web. Its moving
end determines the lid pose. This explains a living-hinge case; no bending strain,
fatigue, retention force or manufacturing feasibility is inferred.
"""
import math
import cadquery as cq


def flexure_pose(p):
    beta=math.pi-math.radians(p["angle"])
    if abs(beta)<1e-8:
        return p["x"]-p["length"],p["z"]
    r=p["length"]/beta
    return p["x"]-r*math.sin(beta),p["z"]+r*(1-math.cos(beta))


def flexure_web(p):
    """One continuous spine skin; tails bite both panels by 0.2 mm."""
    beta=math.pi-math.radians(p["angle"]);bite=0.2;t=p["thickness"]
    if abs(beta)<1e-8:
        return cq.Workplane("XY").box(p["length"]+2*bite,p["height"],t).translate(
            (p["x"]-p["length"]/2,0,p["z"]))
    r=p["length"]/beta;extra=bite/r;cx,cz=p["x"],p["z"]+r

    def point(rad,u):
        return cx-rad*math.sin(u),cz-rad*math.cos(u)

    start,end=-extra,beta+extra;mid=(start+end)/2
    outer,inner=r+t/2,r-t/2
    return (cq.Workplane("XZ",origin=(0,p["height"]/2,0)).moveTo(*point(outer,start))
        .threePointArc(point(outer,mid),point(outer,end)).lineTo(*point(inner,end))
        .threePointArc(point(inner,mid),point(inner,start)).close().extrude(p["height"]))


def flexure_lid(shape,p):
    """Rotate the rigid lid and translate its hinge edge onto the arc endpoint."""
    x,z=flexure_pose(p)
    return shape.rotate((p["x"],0,p["closed_z"]),(p["x"],1,p["closed_z"]),-p["angle"]).translate(
        (x-p["x"],0,z-p["closed_z"]))


def media_pocket_frame(p):
    """An original raised rim around a media keep-out, fused onto a carrier floor."""
    w,h=p["width"],p["height"];wall=p["wall"];c=p["clearance"]
    outer=cq.Workplane("XY").box(w+2*(wall+c),h+2*(wall+c),p["depth"]).translate(
        (p["x"],p["y"],p["z"]+p["depth"]/2))
    inner=cq.Workplane("XY").box(w+2*c,h+2*c,p["depth"]+2).translate(
        (p["x"],p["y"],p["z"]+p["depth"]/2))
    return outer.cut(inner)


def outer_sleeve_lips(p):
    """Two external rails describing a clear sleeve edge; no artwork or film mesh."""
    rails=None
    for sign in (-1,1):
        rail=cq.Workplane("XY").box(p["width"],p["lip"],p["depth"]).translate(
            (p["center_x"],sign*(p["height"]/2-p["lip"]/2),p["z"]+p["depth"]/2))
        rails=rail if rails is None else rails.union(rail)
    return rails
