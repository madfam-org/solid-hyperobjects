"""Original docking/charging archetype. Published named body envelopes are sourced;
seat/profile/port positions remain explicit archetype rules. Frame X width,
Y depth (front negative), Z height. main.py is generated; edit family.py.
"""
import cadquery as cq
import math


def PARAM(getter,default):
    try:
        value=getter()
        return default if value is None else value
    except Exception:
        return default

body_width = PARAM(lambda: body_width, 180)
body_depth = PARAM(lambda: body_depth, 80)
body_height = PARAM(lambda: body_height, 110)
style = PARAM(lambda: style, 'tablet_cradle')
wall = PARAM(lambda: wall, 2)
base_height = PARAM(lambda: base_height, 12)
corner_radius = PARAM(lambda: corner_radius, 3.2)
seat_width = PARAM(lambda: seat_width, 154.8)
seat_depth = PARAM(lambda: seat_depth, 19.2)
seat_height = PARAM(lambda: seat_height, 99)
capacity = PARAM(lambda: capacity, 1)
back_angle = PARAM(lambda: back_angle, 10)
clearance = PARAM(lambda: clearance, 0.4)
boss_width = PARAM(lambda: boss_width, 8.25)
boss_depth = PARAM(lambda: boss_depth, 2.4)
boss_height = PARAM(lambda: boss_height, 6.65)
boss_present = PARAM(lambda: boss_present, True)
usb_count = PARAM(lambda: usb_count, 2)
hdmi_present = PARAM(lambda: hdmi_present, True)
ethernet_present = PARAM(lambda: ethernet_present, False)
power_present = PARAM(lambda: power_present, True)
rear_door_present = PARAM(lambda: rear_door_present, True)
door_angle = PARAM(lambda: door_angle, 0)
target_part = PARAM(lambda: target_part,'dock')

# inline-parts: console_supports


def door_params():
    return dict(width=body_width*.66,height=body_height*.45,thickness=wall*.5,
        clearance=clearance,y=body_depth/2-wall,z=body_height*.12,angle=door_angle)


def ports():
    rows=[(13.4,6)]*int(usb_count)+([(14,5)] if hdmi_present else [])
    rows+=([(16,13.5)] if ethernet_present else [])+([(8,8)] if power_present else [])
    span=sum(w for w,h in rows)+4*max(len(rows)-1,0)
    x=-span/2
    out=[]
    for w,h in rows:
        out.append(dock_port_cut(dict(width=w,height=h,cut_depth=wall+1,
            x=x+w/2,back_y=body_depth/2,z=body_height*.78)))
        x+=w+4
    return out


def chassis_part():
    body=dock_chassis(dict(width=body_width,depth=body_depth,height=body_height,
        wall=wall,base=base_height,radius=corner_radius,style=style))
    ys=[(i-(int(capacity)-1)/2)*body_depth*.48 for i in range(int(capacity))]
    for y in ys:
        body=body.cut(dock_device_tool(dict(width=seat_width,depth=seat_depth,height=seat_height,
            clearance=clearance,seat_z=base_height+1,y=y,angle=back_angle)))
    if rear_door_present:
        d=door_params()
        opening=support_box(dict(width=d['width'],depth=wall+3,height=d['height'],
            y=body_depth/2-wall/2,z=d['z']))
        body=body.cut(opening)
    for tool in ports():body=body.cut(tool)
    if boss_present:
        for y in ys:
            body=body.union(dock_boss(dict(width=boss_width,depth=boss_depth,height=boss_height,
                y=y,z=base_height)))
    return body


def body_part():
    body=chassis_part()
    if not rear_door_present:return body
    door=dock_door(door_params())
    return cq.Workplane('XY').add(cq.Compound.makeCompound([body.val(),door.val()]))


def envelope_part():
    return support_box(dict(width=body_width,depth=body_depth,height=body_height,radius=0))


BUILDERS={'dock':body_part,'envelope':envelope_part,'rear_door':lambda:dock_door(door_params())}
result=BUILDERS.get(target_part,body_part)()
