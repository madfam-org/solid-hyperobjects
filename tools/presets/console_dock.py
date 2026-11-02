"""Dock: sourced body envelopes/counts, original chassis/seat/port profiles."""
from common import DeriveError,Family,is_sourced,rnd,state
from hyperobjects_standard_parts import load_part,part_digest

BASE=dict(slug='__archetype__',width=180,depth=80,height=110,style='tablet_cradle',capacity=1)


def read_dock(o):
    d=state(o,'body')
    if any(d.get(k) is None for k in ('width','height','depth')):return None
    s=dict(slug=o['key'],width=d['width'],height=d['height'],depth=d['depth'],_fallbacks=[])
    s['style']='charging_station' if d['width']<d['depth'] else 'tablet_cradle'
    f=o.get('features') or {};cap=f.get('capacity') if is_sourced(o,'features.capacity') else None
    if cap is None:s['_fallbacks'].append('capacity');cap=2 if s['style']=='charging_station' else 1
    s['capacity']=cap
    if is_sourced(o,'ports'):
        items=o.get('ports') or []
        for dest,kinds in [('usb_count',('usb','usb_a')),('hdmi',('hdmi',)),('ethernet',('ethernet',)),('power_in',('power_in',))]:
            found=[x for x in items if x['kind'] in kinds]
            count=None if any(x.get('count') is None for x in found) else sum(x['count'] for x in found)
            if count is None:s['_fallbacks'].append(dest)
            else:s[dest]=count if dest=='usb_count' else bool(count)
    else:s['_fallbacks'].append('port list')
    return s


def derive(src,*,full):
    s={**BASE,**src};W,D,H=map(float,(s['width'],s['depth'],s['height']));station=s['style']=='charging_station'
    if min(W,D,H)<25:raise DeriveError(f"{s['slug']}: body below dock construction floor")
    plug=load_part('usb-c-plug')['dimensions']
    n=int(s['capacity'])
    if n not in (1,2):raise DeriveError(f"{s['slug']}: only one/two-seat dock constructions are authored")
    return dict(body_width=rnd(W),body_depth=rnd(D),body_height=rnd(H),style=s['style'],
        wall=2,base_height=rnd(min(12,H*.20)),corner_radius=rnd(min(W,D)*.04),
        seat_width=rnd(W*.72 if station else W*.86),seat_depth=rnd(D*.24),seat_height=rnd(H*.90),
        capacity=n,back_angle=0 if station else 10,clearance=.4,
        boss_width=plug['shell_width']['value'],boss_depth=plug['shell_height']['value'],
        boss_height=plug['shell_length']['value'],boss_present=not station,
        usb_count=int(s.get('usb_count',0 if station else 2)),hdmi_present=bool(s.get('hdmi',not station)),
        ethernet_present=bool(s.get('ethernet',False)),power_present=bool(s.get('power_in',not station)),
        rear_door_present=not station,door_angle=0),list(s.get('_fallbacks',[]))+[
            'seat dimensions and angle','connector role/position','chassis profile and rear door','port openings and positions']


def registry_extra(o,v):return {'host_console':(o.get('features') or {}).get('host_console')}


def _archetypes():
    out=[]
    for name,over in [('tablet',{}),('dual-charger',dict(width=65,depth=170,height=60,style='charging_station',capacity=2))]:
        vals,_=derive({**BASE,**over},full=False)
        out.append(dict(slug='archetype-'+name,kind='archetype',
            label={'en':'Archetype — '+name,'es':'Arquetipo — '+('tableta' if name=='tablet' else 'cargador doble')},
            source='Original dock, not a product. USB-C plug shell dimensions come from the keystone standard part; connector role/position remains archetypal.',
            standard_part={'key':'usb-c-plug','digest':part_digest(load_part('usb-c-plug'))},values=vals))
    return out

FAMILY=Family(slug='console-dock',base=BASE,read=read_dock,derive=derive,
    axis_mapping={'body_width':'body.width -> X','body_depth':'body.depth -> Y','body_height':'body.height -> Z'},
    source_line='published dock body envelope and sourced port/capacity counts; seat, openings and chassis remain archetypal.',
    registry_extra=registry_extra,extra_presets=_archetypes())
