# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires:
"""Original dock chassis, device keep-outs, connector bosses and support seats.
Frame X width, Y depth (front negative), Z height above the bottom. Components
consume their own dictionaries. Unknown profiles/positions remain archetypal.
"""
import math
import cadquery as cq


def support_box(p):
    s=cq.Workplane('XY').box(p['width'],p['depth'],p['height']).translate((p.get('x',0),p.get('y',0),p.get('z',0)+p['height']/2))
    if p.get('radius',0)>0:s=s.edges('|Z').fillet(min(p['radius'],p['width']/3,p['depth']/3))
    return s


def dock_chassis(p):
    if p['style']=='charging_station':
        return support_box(p)
    w,d,h,t=p['width'],p['depth'],p['height'],p['wall']
    base=support_box(dict(width=w,depth=d,height=p['base'],radius=p['radius']))
    back=support_box(dict(width=w,depth=t,height=h-p['base']+.2,y=d/2-t/2,z=p['base']-.2))
    front=support_box(dict(width=w,depth=t,height=h*.30,y=-d/2+t/2,z=p['base']-.2))
    sides=None
    for sign in (-1,1):
        side=(cq.Workplane('YZ').polyline([(-d/2,p['base']-.2),(d/2,p['base']-.2),
            (d/2,h),(-d/2,p['base']+h*.30)]).close().extrude(t).translate((sign*(w/2-t) if sign>0 else -w/2,0,0)))
        sides=side if sides is None else sides.union(side)
    return base.union(back).union(front).union(sides)


def dock_device_tool(p):
    """Device envelope plus clearance; no manufacturer profile inferred."""
    tool=support_box(dict(width=p['width']+2*p['clearance'],depth=p['depth']+2*p['clearance'],
        height=p['height']+2,z=p['seat_z'],y=p['y']))
    return tool.rotate((0,p['y'],p['seat_z']),(1,p['y'],p['seat_z']),-p['angle'])


def dock_boss(p):
    return support_box(dict(width=p['width'],depth=p['depth'],height=p['height']+.2,
                           x=p.get('x',0),y=p['y'],z=p['z']-.2))


def dock_port_cut(p):
    return support_box(dict(width=p['width'],depth=p['cut_depth']+1,height=p['height'],
        x=p['x'],y=p['back_y']+.5-p['cut_depth']/2,z=p['z']-p['height']/2))


def dock_door(p):
    panel=support_box(dict(width=p['width']-2*p['clearance'],depth=p['thickness'],
        height=p['height']-2*p['clearance'],y=p['y'],z=p['z']+p['clearance']))
    barrel=cq.Workplane('XY').add(cq.Solid.makeCylinder(p['thickness'],p['width']*.75,
        cq.Vector(-p['width']*.375,p['y'],p['z']+p['thickness']),cq.Vector(1,0,0)))
    panel=panel.union(barrel)
    return panel.rotate((0,p['y'],p['z']+p['thickness']),(1,p['y'],p['z']+p['thickness']),-p['angle'])


def support_disc(p):
    return cq.Workplane('XY').ellipse(p['width']/2,p['depth']/2).extrude(p['height'])


def stand_seat_tool(p):
    return support_box(dict(width=p['width']+2*p['clearance'],depth=p['depth']+2*p['clearance'],
                           height=p['height']+1,z=p['base']))
