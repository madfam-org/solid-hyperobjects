# SPDX-License-Identifier: CERN-OHL-W-2.0
# SPDX-FileCopyrightText: 2026 madfam-org
# requires: console_supports
"""Original disc-base, vertical clip and cradle stand constructions.

Consumes an archetype device/stand seat, not a manufacturer mating profile.
Published stand envelopes constrain X width/Y depth/Z height. No load, tipping,
retention, contact or manufacturing claim follows from geometric validity.
"""
import math
import cadquery as cq


def console_stand_body(p):
    w,d,h,t=p['width'],p['depth'],p['height'],p['wall']
    if p['kind']=='base_disc':
        body=support_disc(dict(width=w,depth=d,height=h))
        recess=cq.Workplane('XY').ellipse(p['seat_width']/2,p['seat_depth']/2).extrude(
            h-p['base']+1).translate((0,0,p['base']))
        body=body.cut(recess)
    else:
        body=support_box(dict(width=w,depth=d,height=p['base'],radius=p['radius']))
        if p['kind']=='vertical_clip':
            for sign in (-1,1):
                rail=support_box(dict(width=t,depth=p['seat_depth'],height=h-p['base']+.2,
                    x=sign*(p['seat_width']/2+t/2),z=p['base']-.2))
                body=body.union(rail)
            lip=support_box(dict(width=p['seat_width']+2*t,depth=t,height=h*.25,
                y=-p['seat_depth']/2+t/2,z=p['base']-.2))
            body=body.union(lip)
        else:
            run=(h-p['base']+.2)/math.tan(math.radians(p['angle']))
            rear=p['seat_depth']/2
            profile=[(rear-run,p['base']-.2),(rear-run-t,p['base']-.2),
                     (rear-t,h),(rear,h)]
            back=(cq.Workplane('YZ').polyline(profile).close().extrude(p['seat_width'])
                .translate((-p['seat_width']/2,0,0)))
            body=body.union(back)
            lip=support_box(dict(width=p['seat_width'],depth=t,height=h*.20,
                y=-d/2+t/2,z=p['base']-.2))
            body=body.union(lip)
    if p['mount_hole']>0:
        hole=cq.Workplane('XY').circle(p['mount_hole']/2).extrude(h+2).translate((0,0,-1))
        body=body.cut(hole)
    if p['cable_slot']>0:
        slot=support_box(dict(width=p['cable_slot'],depth=d/2+1,height=p['base']+1,
            y=d/4+.5,z=-.5))
        body=body.cut(slot)
    return body
