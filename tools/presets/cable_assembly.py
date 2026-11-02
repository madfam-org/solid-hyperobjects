"""Cable interfaces from keystone parts; generic overmolds and routing are ours.

IEC cord ends use the inlet recess as an envelope, not an asserted C7/C13
standard. F-type is a smooth coupling envelope, not a manufactured thread.
Inches convert by the exact 25.4 mm/in factor. No electrical behavior is modeled.
"""
from common import DeriveError, Family, rnd
from hyperobjects_reference import is_sourced
from hyperobjects_standard_parts import load_part

PART_KEYS = {
    'usb_a': 'usb-a-plug', 'usb_c': 'usb-c-plug', 'hdmi_a': 'hdmi-type-a-plug',
    'de9f': 'dsub-de9-female', 'de9m': 'dsub-de9-male', 'rca': 'rca-plug',
    'trs35': 'trs-3-5mm-plug', 'dc5521': 'dc-barrel-plug-5-5x2-1',
    'iec_c8': 'iec-60320-c8', 'iec_c14': 'iec-60320-c14', 'f_type': 'f-type-port',
}
PROFILES = {'usb_a':'rect', 'usb_c':'obround', 'hdmi_a':'dshape',
            'de9f':'dshape', 'de9m':'dshape', 'rca':'round', 'trs35':'round',
            'dc5521':'round', 'iec_c8':'obround', 'iec_c14':'dshape', 'f_type':'round'}


def interface_table():
    table = {}
    for name, key in PART_KEYS.items():
        part = load_part(key)
        def dim(field, fallback):
            d = part['dimensions'].get(field)
            if not d:
                return fallback
            return rnd(float(d['value']) * (25.4 if d['unit'] == 'in' else 1))
        if name.startswith('usb_') or name == 'hdmi_a':
            w, h = dim('shell_width', 12), dim('shell_height', 5)
            length = dim('shell_length', dim('shell_length_min', 8))
        elif name.startswith('de9'):
            w, h = dim('shell_width_max', 17), dim('shell_height_max', 8)
            length = dim('shell_protrusion_max', 6)
        elif name == 'rca':
            w = h = dim('sleeve_outside_diameter', 9)
            length = dim('sleeve_length', 5.5)
        elif name == 'trs35':
            w = h = dim('shaft_diameter', 3.5)
            length = dim('shaft_length', 14)
        elif name == 'dc5521':
            w = h = dim('outside_diameter', 5.5)
            length = dim('barrel_length', 9.5)
        elif name.startswith('iec_'):
            w, h, length = dim('recess_width', 17), dim('recess_height', 9), 12
        else:
            w = h = dim('thread_major_diameter', 9.525)
            length = 10
        table[name] = {'width': w, 'height': h, 'length': length,
                       'body_width': rnd(max(w+4, 10)),
                       'body_height': rnd(max(h+4, 8)), 'body_length': 20,
                       'pin_diameter': dim('pin_diameter', 0) if name == 'rca' else 0,
                       'pin_length': dim('pin_protrusion', 0) if name == 'rca' else 0,
                       'bore': dim('inside_diameter', 0) if name == 'dc5521' else 0}
    return table


TABLE = interface_table()
BASE = {'connector_a':'usb_a', 'connector_b':'usb_c', 'path':'straight',
        'length':200, 'jacket_diameter':4, 'bow':20, 'boot_length':12,
        'coil_turns':3.5, 'coil_pitch':7, 'coil_od':24,
        'ferrite_present':False, 'ferrite_diameter':12, 'ferrite_length':20,
        'ferrite_position':0.3, 'proprietary_profile':'rect',
        'proprietary_width':12, 'proprietary_height':7, 'proprietary_length':8,
        'proprietary_body_width':18, 'proprietary_body_height':12,
        'proprietary_body_length':20, 'proprietary_pin_diameter':0,
        'proprietary_pin_length':0, 'proprietary_bore':0}
for _name, _dims in TABLE.items():
    BASE.update({f'{_name}_{k}': v for k, v in _dims.items()})


def read_cable(obj):
    f, out = obj.get('features') or {}, {}
    for key in ('connector_a', 'connector_b', 'cable_length_mm'):
        if f.get(key) is not None and is_sourced(obj, f'features.{key}'):
            out[key] = f[key]
    if 'cable_length_mm' not in out:
        return None
    return out


def derive(src, *, full):
    values = dict(BASE) if full else {}
    fallbacks = ['generic overmolds and boots', 'jacket diameter', 'route shape',
                 'connector details absent from the standard are archetypes']
    if 'cable_length_mm' in src:
        values['length'] = src['cable_length_mm']
        fallbacks.append('published length mapped to straight jacket span; endpoint convention unknown')
    reverse = {v:k for k,v in PART_KEYS.items()}
    for side in ('a','b'):
        key = src.get('connector_'+side)
        if key:
            if full and key in PART_KEYS:
                continue
            if key not in reverse:
                raise DeriveError('connector is not in the standard-parts table: '+str(key))
            values['connector_'+side] = reverse[key]
        elif not full:
            values['connector_'+side] = 'proprietary'
            fallbacks.append('connector '+side+' unresolved: generic proprietary envelope')
    return values, fallbacks


EXTRAS = []
for slug, en, es, vals in [
    ('archetype-usb-cable','USB cable archetype','Arquetipo de cable USB',{}),
    ('archetype-controller-coil','Coiled controller cord','Cable helicoidal de mando',
     {'connector_a':'de9f','connector_b':'hardwired','path':'coil'}),
    ('archetype-av','AV cable archetype','Arquetipo de cable AV',
     {'connector_a':'rca','connector_b':'rca','path':'arc','ferrite_present':True}),
    ('archetype-link','Link cable archetype','Arquetipo de cable de enlace',
     {'connector_a':'proprietary','connector_b':'proprietary','path':'s_curve'}),
]:
    EXTRAS.append({'slug':slug,'kind':'archetype','label':{'en':en,'es':es},
                   'source':'Original generic archetype; connector interface dimensions from keystone standard parts.',
                   'values':vals})

FAMILY = Family(slug='cable-assembly', base=BASE, read=read_cable, derive=derive,
                axis_mapping={'length':'straight jacket span along X; connector A points -X',
                              'standard':'part +Z tip maps to outward cable tangent'},
                source_line='Only explicitly sourced length and connector identities are read.',
                extra_presets=EXTRAS)
