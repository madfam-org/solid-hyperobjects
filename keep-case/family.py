"""Original one-piece media-case shell with a kinematic spine and separate insert.
The constant-length arc explains folding; it is not a material simulation.
Frame X width, Y height, Z closed thickness; shell underside z=0.
family.py is authored; main.py is generated from shared components.
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
case_height = PARAM(lambda: case_height, 210)
case_thickness = PARAM(lambda: case_thickness, 16)
wall = PARAM(lambda: wall, 1.2)
corner_radius = PARAM(lambda: corner_radius, 2)
clearance = PARAM(lambda: clearance, 0.4)
open_angle = PARAM(lambda: open_angle, 0)
hinge_web = PARAM(lambda: hinge_web, 0.5)
retention = PARAM(lambda: retention, 'disc_hub')
media_width = PARAM(lambda: media_width, 75)
media_height = PARAM(lambda: media_height, 85)
media_depth = PARAM(lambda: media_depth, 8)
card_count = PARAM(lambda: card_count, 1)
disc_diameter = PARAM(lambda: disc_diameter, 120)
hub_diameter = PARAM(lambda: hub_diameter, 14.5)
hub_height = PARAM(lambda: hub_height, 4)
multi_disc = PARAM(lambda: multi_disc, False)
insert_angle = PARAM(lambda: insert_angle, 0)
booklet_clips = PARAM(lambda: booklet_clips, True)
sleeve_lip = PARAM(lambda: sleeve_lip, 2)
sleeve_recess = PARAM(lambda: sleeve_recess, 0.2)
target_part = PARAM(lambda: target_part,"shell")

# inline-parts: media_cases case_flexure

R=(case_thickness-wall)/2
SPINE=R+hinge_web/2
PANEL_WIDTH=case_width-SPINE
PANEL_CX=SPINE/2
AXIS_X=-case_width/2+SPINE


def flex_params(angle):
    return dict(angle=angle,x=AXIS_X,z=wall/2,closed_z=case_thickness-wall/2,
                length=math.pi*R,thickness=hinge_web,height=case_height-2*wall)


def sleeve_tool(z):
    ring=(cq.Workplane("XY").rect(PANEL_WIDTH-2*wall,case_height-2*wall)
        .rect(PANEL_WIDTH-2*(wall+sleeve_lip),case_height-2*(wall+sleeve_lip))
        .extrude(sleeve_recess+1).translate((PANEL_CX,0,z)))
    return ring


def shell_at(angle):
    base=case_pan(dict(width=PANEL_WIDTH,height=case_height,depth=case_thickness*0.48,
        wall=wall,radius=corner_radius,z=0)).translate((PANEL_CX,0,0))
    if sleeve_recess>0:
        base=base.cut(sleeve_tool(-1))
    lid=case_box(dict(width=PANEL_WIDTH,height=case_height,depth=case_thickness*0.48,
        radius=corner_radius,z=case_thickness*0.52)).translate((PANEL_CX,0,0))
    cavity=cq.Workplane("XY").box(PANEL_WIDTH-2*wall,case_height-2*wall,case_thickness).translate(
        (PANEL_CX,0,case_thickness-wall-case_thickness/2))
    lid=lid.cut(cavity)
    if sleeve_recess>0:
        lid=lid.cut(sleeve_tool(case_thickness-sleeve_recess))
    if booklet_clips:
        tabs=case_booklet_tabs(dict(width=4,length=8,thickness=1,
            case_width=PANEL_WIDTH,case_height=case_height,z=case_thickness-2)).translate((PANEL_CX,0,0))
        lid=lid.union(tabs)
    lid=flexure_lid(lid,flex_params(angle))
    web=flexure_web(flex_params(angle))
    return base.union(web).union(lid)


def insert_part():
    if retention=='disc_hub':
        z=case_thickness*0.45 if multi_disc else wall+1
        tray=case_tray(dict(width=PANEL_WIDTH-2*(wall+clearance),height=case_height-2*(wall+clearance),
            floor=1.2,radius=corner_radius,z=z,disc_diameter=disc_diameter,clearance=clearance,
            hub_diameter=hub_diameter,hub_height=hub_height,hub_kind='rosette',petals=8,
            slot_width=0.7,double=multi_disc)).translate((PANEL_CX,0,0))
        return tray.rotate((AXIS_X,0,z),(AXIS_X,1,z),-insert_angle)
    z=wall+1
    tray=case_box(dict(width=PANEL_WIDTH-2*(wall+clearance),height=case_height-2*(wall+clearance),
                       depth=1.2,radius=corner_radius,z=z)).translate((PANEL_CX,0,0))
    n=int(card_count) if retention=='card_slots' else 1
    for i in range(n):
        x=PANEL_CX+(i-(n-1)/2)*(media_width+4)
        y=case_height*0.28 if retention=='mixed' else 0
        pocket=media_pocket_frame(dict(width=media_width,height=media_height,depth=media_depth,
            wall=1,clearance=clearance,x=x,y=y,z=z+1))
        tray=tray.union(pocket)
    if retention=='mixed':
        hub=case_disc_hub(dict(diameter=hub_diameter,height=hub_height,z=z+1,
            kind='rosette',petals=8,slot_width=0.7)).translate((PANEL_CX,-case_height*0.2,0))
        tray=tray.union(hub)
    return tray


def envelope_part():
    return case_box(dict(width=case_width,height=case_height,depth=case_thickness,radius=0,z=0))


BUILDERS={"shell":lambda:shell_at(open_angle),"insert":insert_part,
    "flat_shell":lambda:shell_at(180),"envelope":envelope_part}
result=BUILDERS.get(target_part,lambda:shell_at(open_angle))()
