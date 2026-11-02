# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""Original media-case pans, removable retention tray, hinge and booklet clips.

Frame: X case width, Y case height, Z closed thickness. Base underside z=0.
Hinge runs parallel to Y at the left edge; a negative Y rotation opens upward.
Each component consumes its own parameter dict. No product outline or artwork.
"""
import cadquery as cq


def case_box(p):
    body=cq.Workplane("XY").box(p["width"],p["height"],p["depth"]).translate((0,0,p["z"]+p["depth"]/2))
    if p["radius"]>0:
        body=body.edges("|Z").fillet(min(p["radius"],p["width"]/3,p["height"]/3))
    return body


def case_pan(p):
    """Open pan with an overshooting cavity, floor and walls of thickness wall."""
    body=case_box(p);t=p["wall"]
    tool=cq.Workplane("XY").box(p["width"]-2*t,p["height"]-2*t,p["depth"]+1).translate(
        (0,0,p["z"]+t+(p["depth"]+1)/2))
    return body.cut(tool)


def case_pin(p):
    """Cylinder parallel to Y, intended to overlap its support by a real bite."""
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(p["radius"],p["length"],
        cq.Vector(p["x"],p["y"]-p["length"]/2,p["z"]),cq.Vector(0,1,0)))


def case_hinge_eye(p):
    outer=case_pin(p)
    inner=case_pin(dict(p,radius=p["bore_radius"],length=p["length"]+2))
    return outer.cut(inner)


def case_disc_hub(p):
    """Original rosette or button hub, with petal slots above a continuous root."""
    r=p["diameter"]/2
    body=cq.Workplane("XY").circle(r).extrude(p["height"]).translate((0,0,p["z"]))
    if p["kind"]=="rosette":
        for i in range(int(p["petals"])):
            tool=cq.Workplane("XY").box(r+1,p["slot_width"],p["height"]+1).translate(
                (r/2+1,0,p["z"]+0.6+(p["height"]+1)/2))
            body=body.cut(tool.rotate((0,0,0),(0,0,1),i*360/p["petals"]))
    return body


def case_tray(p):
    """Removable tray with an original disc keep-out and connected retention hub."""
    tray=case_box(dict(width=p["width"],height=p["height"],depth=p["floor"],radius=p["radius"],z=p["z"]))
    # Recess shallowly into the floor; a continuous floor remains under the disc.
    tool=cq.Workplane("XY").circle((p["disc_diameter"]+2*p["clearance"])/2).extrude(
        p["floor"]+1).translate((0,0,p["z"]+p["floor"]*0.65))
    tray=tray.cut(tool)
    hub=case_disc_hub(dict(diameter=p["hub_diameter"],height=p["hub_height"],z=p["z"]+p["floor"]*0.45,
                          kind=p["hub_kind"],petals=p["petals"],slot_width=p["slot_width"]))
    tray=tray.union(hub)
    if p["double"]:
        back=case_disc_hub(dict(diameter=p["hub_diameter"],height=p["hub_height"],z=0,
            kind=p["hub_kind"],petals=p["petals"],slot_width=p["slot_width"]))
        back=back.rotate((0,0,0),(1,0,0),180).translate((0,0,p["z"]+0.2))
        tray=tray.union(back)
    return tray


def case_booklet_tabs(p):
    """Two internal ledges per side, overlapping the supporting case wall."""
    out=None
    for side in (-1,1):
        for sign in (-1,1):
            tab=cq.Workplane("XY").box(p["width"],p["length"],p["thickness"]).translate(
                (side*(p["case_width"]/2-p["width"]/2),sign*p["case_height"]*0.28,p["z"]))
            out=tab if out is None else out.union(tab)
    return out


def case_open(shape,p):
    return shape.rotate((-p["width"]/2+3,0,p["thickness"]/2),
                        (-p["width"]/2+3,1,p["thickness"]/2),-p["angle"])
