"""Original console support family: sourced stand envelope, archetype seat/profile.
Frame X width, Y depth, Z height, bottom z=0. family.py is authored; main.py is
GENERATED from shared support components. No stability or physical-fit proof.
"""
import cadquery as cq
import math


def PARAM(getter,default):
    try:
        value=getter()
        return default if value is None else value
    except Exception:
        return default

body_width = PARAM(lambda: body_width, 110)
body_depth = PARAM(lambda: body_depth, 70)
body_height = PARAM(lambda: body_height, 65)
stand_kind = PARAM(lambda: stand_kind, 'cradle')
wall = PARAM(lambda: wall, 2)
base_height = PARAM(lambda: base_height, 13)
corner_radius = PARAM(lambda: corner_radius, 2.8)
seat_width = PARAM(lambda: seat_width, 71.5)
seat_depth = PARAM(lambda: seat_depth, 52.5)
tilt_angle = PARAM(lambda: tilt_angle, 65)
mount_hole_diameter = PARAM(lambda: mount_hole_diameter, 4)
cable_slot_width = PARAM(lambda: cable_slot_width, 12)
target_part=PARAM(lambda:target_part,'stand')

# inline-parts: console_stands


def stand_part():
    return console_stand_body(dict(width=body_width,depth=body_depth,height=body_height,
        kind=stand_kind,wall=wall,base=base_height,radius=corner_radius,seat_width=seat_width,
        seat_depth=seat_depth,angle=tilt_angle,mount_hole=mount_hole_diameter,cable_slot=cable_slot_width))


def envelope_part():
    return support_box(dict(width=body_width,depth=body_depth,height=body_height,radius=0))


BUILDERS={'stand':stand_part,'envelope':envelope_part}
result=BUILDERS.get(target_part,stand_part)()
