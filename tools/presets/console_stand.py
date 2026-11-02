"""Console stand envelopes from the catalog, original seat and support rules."""
from common import DeriveError,Family,rnd,state

BASE=dict(slug='__archetype__',width=110,depth=70,height=65,kind='cradle')


def read_stand(o):
    d=state(o,'body')
    if any(d.get(k) is None for k in ('width','height','depth')):return None
    w,dp,h=d['width'],d['depth'],d['height']
    kind='base_disc' if h<min(w,dp)*.20 else 'vertical_clip' if dp>w else 'cradle'
    return dict(slug=o['key'],width=w,depth=dp,height=h,kind=kind)


def derive(src,*,full):
    s={**BASE,**src};w,d,h=map(float,(s['width'],s['depth'],s['height']));k=s['kind']
    if min(w,d)<20 or h<6:raise DeriveError(f"{s['slug']}: envelope below current stand construction floor")
    return dict(body_width=rnd(w),body_depth=rnd(d),body_height=rnd(h),stand_kind=k,
        wall=2,base_height=rnd(h*(.65 if k=='base_disc' else .20)),corner_radius=rnd(min(w,d)*.04),
        seat_width=rnd(w*(.45 if k=='base_disc' else .65)),
        seat_depth=rnd(d*(.45 if k=='base_disc' else .85 if k=='vertical_clip' else .75)),
        tilt_angle=65,mount_hole_diameter=4,cable_slot_width=rnd(min(12,w*.15))),[
            'stand construction selected from envelope ratios','device/stand seat dimensions',
            'mounting hole and cable path','view angle and wall profile']


def registry_extra(o,v):return {'host_console':(o.get('features') or {}).get('host_console')}


def _archetypes():
    out=[]
    for name,over in [('cradle',{}),('vertical-clip',dict(width=80,depth=180,height=40,kind='vertical_clip')),
                      ('disc-base',dict(width=160,depth=160,height=14,kind='base_disc'))]:
        vals,_=derive({**BASE,**over},full=False)
        out.append(dict(slug='archetype-'+name,kind='archetype',label={'en':'Archetype — '+name,
            'es':'Arquetipo — '+{'cradle':'cuna','vertical-clip':'clip vertical','disc-base':'base circular'}[name]},
            source='Original stand envelope and construction, not a product. All seat/profile/clearance values are explicit archetype rules.',values=vals))
    return out

FAMILY=Family(slug='console-stand',base=BASE,read=read_stand,derive=derive,
    axis_mapping={'body_width':'body.width -> X','body_depth':'body.depth -> Y','body_height':'body.height -> Z'},
    source_line='published stand body envelope only; stand form, seat and mounting features remain archetypal.',
    registry_extra=registry_extra,extra_presets=_archetypes())
