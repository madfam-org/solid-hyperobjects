"""Rigid media-case family. Original mechanisms and contours; sourced presets.
X width, Y height, Z closed thickness; base z=0, hinge parallel to Y.
family.py is authored; main.py is generated from shared media-case components.
"""
import cadquery as cq
import math


def PARAM(getter,default):
    try:
        value=getter()
        return default if value is None else value
    except Exception:
        return default

case_width = PARAM(lambda: case_width, 150)
case_height = PARAM(lambda: case_height, 140)
case_thickness = PARAM(lambda: case_thickness, 14)
wall = PARAM(lambda: wall, 1.2)
clearance = PARAM(lambda: clearance, 0.4)
corner_radius = PARAM(lambda: corner_radius, 2)
lid_angle = PARAM(lambda: lid_angle, 0)
tray_kind = PARAM(lambda: tray_kind, 'disc_hub')
tray_angle = PARAM(lambda: tray_angle, 0)
disc_diameter = PARAM(lambda: disc_diameter, 120.0)
hub_diameter = PARAM(lambda: hub_diameter, 14.5)
hub_height = PARAM(lambda: hub_height, 4)
hub_kind = PARAM(lambda: hub_kind, 'rosette')
petal_count = PARAM(lambda: petal_count, 8)
booklet_tabs = PARAM(lambda: booklet_tabs, True)
spine_window = PARAM(lambda: spine_window, True)
hinge_pin_radius = PARAM(lambda: hinge_pin_radius, 2)
hinge_pin_length = PARAM(lambda: hinge_pin_length, 10)
tab_width = PARAM(lambda: tab_width, 4)
tab_length = PARAM(lambda: tab_length, 8)
target_part = PARAM(lambda: target_part,"base")

# inline-parts: media_cases


def pan_params():
    return dict(width=case_width,height=case_height,depth=case_thickness*0.60,
                wall=wall,radius=corner_radius,z=0)


def base_part():
    base=case_pan(pan_params())
    for sign in (-1,1):
        pin=case_pin(dict(radius=hinge_pin_radius,length=hinge_pin_length,
            x=-case_width/2+3,y=sign*case_height*0.35,z=case_thickness/2))
        base=base.union(pin)
    return base


def tray_part():
    z=case_thickness*0.45 if tray_kind=="flip_tray" else wall+1
    tray=case_tray(dict(width=case_width-2*(wall+clearance),height=case_height-2*(wall+clearance),
        floor=1.2,radius=corner_radius,z=z,disc_diameter=disc_diameter,clearance=clearance,
        hub_diameter=hub_diameter,hub_height=hub_height,hub_kind=hub_kind,petals=petal_count,
        slot_width=0.7,double=tray_kind=="flip_tray"))
    return tray.rotate((-case_width/2+wall+clearance,0,z),
                       (-case_width/2+wall+clearance,1,z),-tray_angle)


def lid_part():
    depth=3
    lid=case_box(dict(width=case_width,height=case_height,depth=depth,radius=corner_radius,z=case_thickness-depth))
    cavity=cq.Workplane("XY").box(case_width-2*wall,case_height-2*wall,depth+1).translate(
        (0,0,case_thickness-wall-(depth+1)/2))
    lid=lid.cut(cavity)
    for sign in (-1,1):
        cy=sign*(case_height*0.35+hinge_pin_length/2+1.5+clearance)
        eye=case_hinge_eye(dict(radius=3,bore_radius=hinge_pin_radius+clearance,length=3,
            x=-case_width/2+3,y=cy,z=case_thickness/2))
        arm=cq.Workplane("XY").box(3,3,case_thickness/2).translate(
            (-case_width/2+1.5,cy,case_thickness*0.75))
        lid=lid.union(eye).union(arm)
    if booklet_tabs:
        lid=lid.union(case_booklet_tabs(dict(width=tab_width,length=tab_length,thickness=1,
            case_width=case_width,case_height=case_height,z=case_thickness-2)))
    if spine_window:
        window=cq.Workplane("XY").box(wall+2,case_height*0.36,1).translate(
            (-case_width/2,0,case_thickness-1.5))
        lid=lid.cut(window)
    return case_open(lid,dict(width=case_width,thickness=case_thickness,angle=lid_angle))


def envelope_part():
    return case_box(dict(width=case_width,height=case_height,depth=case_thickness,radius=corner_radius,z=0))


BUILDERS={"base":base_part,"tray":tray_part,"lid":lid_part,"envelope":envelope_part}
result=BUILDERS.get(target_part,base_part)()
