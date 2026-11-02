"""Original living-hinge media case; catalog envelopes, explicit archetype detail."""
from common import DeriveError,Family,is_sourced,rnd,state
from hyperobjects_standard_parts import load_part,part_digest

BASE=dict(slug='__archetype__',width=150,height=210,depth=16,retention='disc_hub',capacity=1,
          media_width=75,media_height=85,media_depth=8)


def read_case(o):
    d=state(o,'closed')
    if any(d.get(k) is None for k in ('width','height','depth')):return None
    s=dict(slug=o['key'],width=d['width'],height=d['height'],depth=d['depth'],_fallbacks=[])
    f=o.get('features') or {}
    for k in ('retention','capacity'):
        v=f.get(k) if is_sourced(o,'features.'+k) else None
        if v is None:s['_fallbacks'].append(k)
        else:s[k]=v
    return s


def derive(src,*,full):
    cd=load_part('optical-disc-cd-120mm')['dimensions']
    disc=cd['diameter']['value'];hole=cd['centre_hole_diameter']['value']
    s={**BASE,**src};W,H,T=map(float,(s['width'],s['height'],s['depth']));kind=s['retention'];n=int(s['capacity'])
    if kind not in ('disc_hub','cartridge_pocket','card_slots','mixed'):
        raise DeriveError(f"{s['slug']}: unsupported retention {kind}")
    if T<10 or min(W,H)<60 or n>2:
        raise DeriveError(f"{s['slug']}: current construction needs a larger case or at most two media")
    if kind in ('disc_hub','mixed') and min(W,H)<132:
        raise DeriveError(f"{s['slug']}: the archetype 120mm disc keep-out does not fit")
    return dict(case_width=rnd(W),case_height=rnd(H),case_thickness=rnd(T),wall=1.2,corner_radius=2,
        clearance=0.4,open_angle=0,hinge_web=0.5,retention=kind,
        media_width=rnd(40 if kind=='card_slots' else s['media_width']),
        media_height=rnd(30 if kind=='card_slots' else s['media_height']),
        media_depth=rnd(3 if kind=='card_slots' else s['media_depth']),
        card_count=n,disc_diameter=disc,hub_diameter=rnd(hole-0.5),hub_height=4,
        multi_disc=kind=='disc_hub' and n>1,insert_angle=0,booklet_clips=True,
        sleeve_lip=2,sleeve_recess=0.2),list(s.get('_fallbacks',[]))+[
            'living hinge, shell and clips','media pocket geometry','sleeve recess']


def _archetypes():
    out=[]
    for name,over in [('disc',{}),('double-disc',dict(depth=22,capacity=2)),
        ('cartridge',dict(width=150,height=175,depth=18,retention='cartridge_pocket')),
        ('cards',dict(width=115,height=150,depth=14,retention='card_slots',capacity=2)),
        ('mixed',dict(width=165,height=230,depth=20,retention='mixed'))]:
        vals,_=derive({**BASE,**over},full=False)
        out.append(dict(slug='archetype-'+name,kind='archetype',
            label={'en':'Archetype — '+name,'es':'Arquetipo — '+{'disc':'disco','double-disc':'disco doble','cartridge':'cartucho','cards':'tarjetas','mixed':'mixto'}[name]},
            source='Original case, not a manufacturer package. Envelope and pocket sizes are archetype choices; no historical SKU is asserted. Disc diameter/hole reference the keystone CD standard part.',
            standard_part={'key':'optical-disc-cd-120mm','digest':part_digest(load_part('optical-disc-cd-120mm'))},values=vals))
    return out

FAMILY=Family(slug='keep-case',base=BASE,read=read_case,derive=derive,
    axis_mapping={'case_width':'closed.width -> X','case_height':'closed.height -> Y','case_thickness':'closed.depth -> Z'},
    source_line='published closed envelope and sourced retention/capacity; all mechanical details remain archetypal.',
    extra_presets=_archetypes())
