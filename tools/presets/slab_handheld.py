"""Slab handheld archetype rules and sourced catalog mapping.

Frame: published width -> X, height -> Z, depth -> Y; face y=0, rear +Y.
All profiles, feature positions and mechanical clearances are our archetype.
"""
from common import DeriveError, Family, control_count, display, has_port, is_sourced, rnd, state
from hyperobjects_standard_parts import load_part

BASE = dict(slug="__archetype__", width=170, height=90, depth=26,
            layout="landscape", media_kind="slot_top", cell_kind="built_in", cell_count=0,
            controller_attach="none", kickstand=True, grip_count=0, dpad=1,
            face_count=4, stick_count=2, system_count=2, rear_count=0,
            usb=True, jack=True, crank=False,bumper_count=2,trigger_count=0,touchpad=False)
RULES = dict(wall=2, clearance=0.4, door_thickness=1.5, door_lip=1.5,
             recess=1.2, corner_ratio=0.08, face_ratio=0.65,
             grip_width_ratio=0.18, grip_height_ratio=0.75)


def _feature(o, k):
    return (o.get("features") or {}).get(k) if is_sourced(o, f"features.{k}") else None


def read_device(o):
    b=state(o,"body")
    if any(b.get(k) is None for k in ("width","height","depth")):
        return None
    s=dict(slug=o["key"], width=b["width"],height=max(b["height"],b["depth"]),
           depth=min(b["height"],b["depth"]),_fallbacks=[])
    for k in ("layout","cell_kind","cell_count","controller_attach","kickstand"):
        value=_feature(o,k)
        if value is None:
            s["_fallbacks"].append(k.replace("_"," "))
        else:
            s[k]=value
    for dest,kind in (("dpad","dpad"),("face_count","abxy"),("stick_count","stick"),
                      ("system_count","button"),("rear_count","rear_button"),("crank","crank"),
                      ("bumper_count","bumper"),("trigger_count","trigger"),("touchpad","touchpad")):
        value=control_count(o,kind)
        if value is None:
            s["_fallbacks"].append(dest.replace("_"," "))
        else:
            s[dest]=value
    for dest,kind in (("usb","usb_c"),("jack","headphone_3_5")):
        value=has_port(o,kind)
        if value is None:
            s["_fallbacks"].append(dest+" port")
        else:
            s[dest]=value
    if is_sourced(o,"media"):
        kinds={i["kind"] for i in o.get("media") or []}
        s["media_kind"]=next((dest for k,dest in (("cartridge_rear","cart_rear"),
            ("cartridge_top","slot_top"),("card_slot","slot_top"),("umd","umd_rear"),
            ("faceplate","faceplate")) if k in kinds),"none")
    else:
        s["_fallbacks"].append("media kind")
    active=display(o,"primary")
    if active:
        s["screen"]=(active[0],active[1])
    else:
        s["_fallbacks"].append("display active area")
    return s


def derive(src, *, full):
    s={**BASE,**src}; fb=list(s.get("_fallbacks",[])); W,H,D=map(float,(s["width"],s["height"],s["depth"]))
    if min(W,H)<40 or D<8:
        raise DeriveError(f"{s['slug']}: envelope below the slab construction floor")
    portrait=s["layout"]=="portrait"; grips=int(s.get("grip_count",0))
    sw,sh=s.get("screen",(W*(0.65 if portrait else 0.52),H*(0.32 if portrait else 0.65)))
    if sw>W-8 or sh>H-8:
        raise DeriveError(f"{s['slug']}: sourced active area does not fit the body frame")
    cell=s["cell_kind"]
    if cell not in ("aa","aaa","built_in"):
        raise DeriveError(f"{s['slug']}: unsupported cell kind {cell}")
    n=int(s["cell_count"]) if cell!="built_in" else 0
    dia=ln=0
    if n:
        dims=load_part("cell-"+cell)["dimensions"]
        dia=float(dims["diameter_max"]["value"]);ln=float(dims["height_max"]["value"])
    bw=ln+0.8 if n else min(0.36*W,45)
    bh=n*(dia+0.4)+0.4 if n else min(0.20*H,25)
    bd=dia+0.4 if n else 0
    if bw+7>W or bh+7>H or bd+5>D:
        raise DeriveError(f"{s['slug']}: cylindrical-cell bay does not fit the sourced envelope")
    v=dict(body_width=rnd(W),body_height=rnd(H),body_depth=rnd(D),layout=s["layout"],
        corner_radius=rnd(min(W,H)*0.08),back_crown=rnd(min(D*0.08,2)),
        grip_count=grips,face_depth=rnd(D*(0.65 if grips else 1)),grip_width=rnd(W*0.18),
        grip_length=rnd(H*0.75),grip_drop=rnd(H*0.08 if grips else 0),
        screen_width=rnd(sw),screen_height=rnd(sh),screen_z=rnd(H*(0.68 if portrait else 0.53)),
        control_z=rnd(H*(0.25 if portrait else 0.48)),control_x=rnd(W*(0.23 if portrait else 0.39)),
        dpad_count=int(bool(s["dpad"])),face_count=int(s["face_count"]),stick_count=int(s["stick_count"]),
        system_count=int(s["system_count"]),rear_count=int(s["rear_count"]),crank_present=bool(s["crank"]),
        bumper_count=int(s["bumper_count"]),trigger_count=int(s["trigger_count"]),touchpad_present=bool(s["touchpad"]),
        control_size=rnd(min(W,H)*0.14),button_radius=rnd(min(W,H)*0.035),
        media_kind=s["media_kind"],media_width=rnd(min(W*0.42,55)),
        media_height=rnd(min(H*0.32,40)),media_thickness=rnd(min(D*0.22,5)),
        media_insert_depth=rnd(H*0.18),media_insert=1,
        cell_kind=cell,cell_count=n,bay_width=rnd(bw),bay_height=rnd(bh),bay_depth=rnd(bd),
        bay_z=rnd(H*0.30),controller_attach=s["controller_attach"] or "none",
        kickstand_present=bool(s["kickstand"]),kickstand_angle=0,
        kickstand_width=rnd(W*0.25),kickstand_height=rnd(H*0.40),
        usb_present=bool(s["usb"]),jack_present=bool(s["jack"]),
        wall=2,clearance=0.4,recess_depth=1.2)
    if s["media_kind"]=="umd_rear":
        v.update(media_width=rnd(min(W*0.45,65)),media_height=rnd(H*0.40),
                 media_thickness=rnd(min(D*0.25,5)),media_insert_depth=rnd(H*0.18))
    return v,fb


ARCHETYPES=[
    ("portrait-cart-rear",dict(width=90,height=155,depth=32,layout="portrait",media_kind="cart_rear",
        cell_kind="aa",cell_count=4,stick_count=0,kickstand=False)),
    ("landscape",{}),
    ("gripped-pc",dict(width=290,height=120,depth=45,grip_count=2,media_kind="none",rear_count=4,kickstand=False)),
    ("hybrid-rail",dict(width=180,height=105,depth=14,controller_attach="rail",media_kind="slot_top",
        dpad=0,face_count=0,stick_count=0,system_count=1)),
    ("hybrid-magnetic",dict(width=200,height=115,depth=16,controller_attach="magnetic",media_kind="slot_top",
        dpad=0,face_count=0,stick_count=0,system_count=1)),
    ("faceplate",dict(width=100,height=160,depth=30,layout="portrait",media_kind="faceplate",
        cell_kind="aaa",cell_count=2,dpad=0,face_count=2,stick_count=0,kickstand=False)),
    ("landscape-umd",dict(width=180,height=90,depth=28,media_kind="umd_rear",stick_count=1,kickstand=False)),
]


def _presets():
    out=[]
    for name,overrides in ARCHETYPES:
        v,_=derive({**BASE,**overrides},full=False)
        out.append(dict(slug="archetype-"+name,kind="archetype",
            label=dict(en="Archetype — "+name.replace("-"," "),es="Arquetipo — "+{"portrait-cart-rear":"vertical con cartucho trasero","landscape":"horizontal","gripped-pc":"PC con agarres","hybrid-rail":"híbrida con rieles","hybrid-magnetic":"híbrida magnética","faceplate":"placa intercambiable","landscape-umd":"horizontal con disco"}[name]),
            source="Original archetype, not a product. All sizes and placements follow tools/presets/slab_handheld.py; cylindrical-cell maxima come from keystone standard parts.",values=v))
    return out

FAMILY=Family(slug="slab-handheld",base=BASE,read=read_device,derive=derive,
    axis_mapping=dict(body_width="states.body.width -> X",body_height="larger of states.body.height/depth -> Z",
                      body_depth="smaller of states.body.height/depth -> Y; explicit thickness mapping, front face y=0"),
    source_line="published body envelope and sourced control counts; profile and placements are archetype rules.",
    extra_presets=_presets())
