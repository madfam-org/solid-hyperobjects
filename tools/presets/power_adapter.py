"""Published adapter bodies and explicitly generic mains/output details.

Electrical ratings remain reference facts; they never become geometry controls.
The reference body envelope never includes our cord/prong routing archetype.
"""
from common import Family, state
from hyperobjects_reference import is_sourced
from hyperobjects_standard_parts import load_part
from cable_assembly import TABLE


def inlet_dims(key):
    part=load_part(key)
    return {axis:part['dimensions']['recess_'+axis]['value'] for axis in ('width','height')}


BASE = {'body_width':70,'body_height':35,'body_depth':45,'corner_radius':3,
        'form':'brick','prong_layout':'flat_pair','prong_width':5,'prong_thickness':1.5,
        'prong_spacing':14,'prong_length':15,'prong_z':16,
        'inlet_kind':'none','inlet_depth':6,'cord_length':120,
        'jacket_diameter':4,'boot_length':12,'output_connector':'usb_c',
        'led_window':True,'led_diameter':2,'label_recess':0.4,'prong_extension':1}
for name,key in [('c8','iec-60320-c8'),('c14','iec-60320-c14')]:
    BASE.update({name+'_'+k:v for k,v in inlet_dims(key).items()})
for name in ('usb_c','dc5521'):
    BASE.update({name+'_'+k:v for k,v in TABLE[name].items()})


def read_adapter(obj):
    body=state(obj,'body')
    if not all(body.get(k) is not None and is_sourced(obj,'dimensions_mm.states.body.'+k)
               for k in ('width','height','depth')):
        return None
    src={'body_'+k:body[k] for k in ('width','height','depth')}
    f=obj.get('features') or {}
    for key in ('output_connector','cable_length_mm'):
        if f.get(key) is not None and is_sourced(obj,'features.'+key):src[key]=f[key]
    return src


def derive(src,*,full):
    out=dict(BASE) if full else {k:src[k] for k in ('body_width','body_height','body_depth')}
    fb=['form, prong layout and all prong dimensions', 'inlet and LED location',
        'corner radius and label recess','generic housing and lead routing']
    if src.get('cable_length_mm') is not None:out['cord_length']=src['cable_length_mm']
    else:fb.append('cord length')
    key=src.get('output_connector')
    if key=='usb-c-plug':out['output_connector']='usb_c'
    elif key=='dc-barrel-plug-5-5x2-1':out['output_connector']='dc5521'
    elif not full:out['output_connector']='generic';fb.append('output connector')
    if not full:out['prong_z']=src['body_height']*.45
    return out,fb


EXTRAS=[]
for slug,en,es,v in [
 ('archetype-inline','Inline brick','Bloque en línea',{'inlet_kind':'c8'}),
 ('archetype-flat-prongs','Wall adapter with flat prongs','Adaptador con clavijas planas',{'form':'wall_wart'}),
 ('archetype-round-prongs','Wall adapter with round prongs','Adaptador con clavijas redondas',{'form':'wall_wart','prong_layout':'round_pair'}),
 ('archetype-large-brick','Large external brick','Bloque externo grande',{'body_width':150,'body_height':55,'body_depth':70,'inlet_kind':'c14','output_connector':'dc5521'}),
]:EXTRAS.append({'slug':slug,'kind':'archetype','label':{'en':en,'es':es},'source':'Original generic adapter archetype; no product or electrical conformance claim.','values':v})

FAMILY=Family(slug='power-adapter',base=BASE,read=read_adapter,derive=derive,
              axis_mapping={'body_width':'published width -> X','body_depth':'published depth -> Y',
                            'body_height':'published height -> Z, floor z=0'},
              source_line='Published body envelope and sourced cord length/output identity only; all other features are archetypes.',
              extra_presets=EXTRAS)
