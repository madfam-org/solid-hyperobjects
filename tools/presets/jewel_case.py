"""Rigid media-case archetypes; source only published closed envelopes and counts."""
from common import DeriveError,Family,is_sourced,rnd,state
from hyperobjects_standard_parts import load_part,part_digest

BASE=dict(slug="__archetype__",width=150,height=140,depth=14,capacity=1)
RULES=dict(wall=1.2,clearance=0.4,hub_height=4,hub_kind="rosette",petals=8)


def read_case(obj):
    d=state(obj,"closed")
    if any(d.get(k) is None for k in ("width","height","depth")):return None
    f=obj.get('features') or {}
    cap=f.get('capacity') if is_sourced(obj,'features.capacity') else None
    return dict(slug=obj['key'],width=d['width'],height=d['height'],depth=d['depth'],
                capacity=cap or 1,_fallbacks=[] if cap is not None else ['capacity'])


def derive(src,*,full):
    s={**BASE,**src};W,H,T=map(float,(s['width'],s['height'],s['depth']))
    cd=load_part('optical-disc-cd-120mm')['dimensions'];diam=cd['diameter']['value'];hole=cd['centre_hole_diameter']['value']
    if s["capacity"] > 2:
        raise DeriveError(f"{s['slug']}: capacity above two needs a sourced multi-leaf construction")
    if min(W,H)<diam+8 or T<9:
        raise DeriveError(f"{s['slug']}: CD tray does not fit the published case envelope")
    v=dict(case_width=rnd(W),case_height=rnd(H),case_thickness=rnd(T),wall=1.2,clearance=0.4,
        corner_radius=2,lid_angle=0,tray_kind='flip_tray' if s['capacity']>1 else 'disc_hub',
        tray_angle=0,disc_diameter=diam,hub_diameter=rnd(hole-0.5),hub_height=3 if T<12 else 4,
        hub_kind='rosette',petal_count=8,booklet_tabs=True,spine_window=True,hinge_pin_radius=2,
        hinge_pin_length=10,tab_width=4,tab_length=8)
    return v,list(s.get('_fallbacks',[]))+['case construction and hinge','hub and booklet retention']


def _archetypes():
    out=[]
    for name,over in [('single',{}),('slim',dict(depth=10)),('double',dict(depth=20,capacity=2)),('fatbox',dict(width=160,height=150,depth=32,capacity=2))]:
        vals,_=derive({**BASE,**over},full=False)
        out.append(dict(slug='archetype-'+name,label={'en':'Archetype — '+name,'es':'Arquetipo — '+{'single':'sencillo','slim':'delgado','double':'doble','fatbox':'caja gruesa'}[name]},kind='archetype',
            source='Original case dimensions and construction, not a product. Disc diameter and hub hole reference the keystone optical-disc-cd-120mm standard part.',
            standard_part={'key':'optical-disc-cd-120mm','digest':part_digest(load_part('optical-disc-cd-120mm'))},values=vals))
    return out

FAMILY=Family(slug='jewel-case',base=BASE,read=read_case,derive=derive,
 axis_mapping={'case_width':'closed.width -> X','case_height':'closed.height -> Y','case_thickness':'closed.depth -> Z'},
 source_line='published closed envelope and sourced capacity; all case mechanisms remain archetypal.',extra_presets=_archetypes())
