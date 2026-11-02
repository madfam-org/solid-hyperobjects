# SPDX-License-Identifier: CERN-OHL-W-2.0
"""Cable interface envelope. X along route; Y bow; Z height, centerline at Z=0.

The cable is for routing/fit study, not electrical manufacture. Standard shell
bounds coexist with explicit archetype overmolds. See docs/README.md.
"""
# inline-parts: cables


def PARAM(read, default):
    try:
        return read()
    except NameError:
        return default


P = {
    'connector_a': PARAM(lambda: connector_a, 'usb_a'),
    'connector_b': PARAM(lambda: connector_b, 'usb_c'),
    'path': PARAM(lambda: path, 'straight'),
    'length': PARAM(lambda: length, 200),
    'jacket_diameter': PARAM(lambda: jacket_diameter, 4),
    'bow': PARAM(lambda: bow, 20),
    'boot_length': PARAM(lambda: boot_length, 12),
    'coil_turns': PARAM(lambda: coil_turns, 3.5),
    'coil_pitch': PARAM(lambda: coil_pitch, 7),
    'coil_od': PARAM(lambda: coil_od, 24),
    'ferrite_present': PARAM(lambda: ferrite_present, False),
    'ferrite_diameter': PARAM(lambda: ferrite_diameter, 12),
    'ferrite_length': PARAM(lambda: ferrite_length, 20),
    'ferrite_position': PARAM(lambda: ferrite_position, 0.3),
    'proprietary_profile': PARAM(lambda: proprietary_profile, 'rect'),
    'proprietary_width': PARAM(lambda: proprietary_width, 12),
    'proprietary_height': PARAM(lambda: proprietary_height, 7),
    'proprietary_length': PARAM(lambda: proprietary_length, 8),
    'proprietary_body_width': PARAM(lambda: proprietary_body_width, 18),
    'proprietary_body_height': PARAM(lambda: proprietary_body_height, 12),
    'proprietary_body_length': PARAM(lambda: proprietary_body_length, 20),
    'proprietary_pin_diameter': PARAM(lambda: proprietary_pin_diameter, 0),
    'proprietary_pin_length': PARAM(lambda: proprietary_pin_length, 0),
    'proprietary_bore': PARAM(lambda: proprietary_bore, 0),
    'usb_a_width': PARAM(lambda: usb_a_width, 12),
    'usb_a_height': PARAM(lambda: usb_a_height, 4.5),
    'usb_a_length': PARAM(lambda: usb_a_length, 11.75),
    'usb_a_body_width': PARAM(lambda: usb_a_body_width, 16),
    'usb_a_body_height': PARAM(lambda: usb_a_body_height, 8.5),
    'usb_a_body_length': PARAM(lambda: usb_a_body_length, 20),
    'usb_a_pin_diameter': PARAM(lambda: usb_a_pin_diameter, 0),
    'usb_a_pin_length': PARAM(lambda: usb_a_pin_length, 0),
    'usb_a_bore': PARAM(lambda: usb_a_bore, 0),
    'usb_c_width': PARAM(lambda: usb_c_width, 8.25),
    'usb_c_height': PARAM(lambda: usb_c_height, 2.4),
    'usb_c_length': PARAM(lambda: usb_c_length, 6.65),
    'usb_c_body_width': PARAM(lambda: usb_c_body_width, 12.25),
    'usb_c_body_height': PARAM(lambda: usb_c_body_height, 8),
    'usb_c_body_length': PARAM(lambda: usb_c_body_length, 20),
    'usb_c_pin_diameter': PARAM(lambda: usb_c_pin_diameter, 0),
    'usb_c_pin_length': PARAM(lambda: usb_c_pin_length, 0),
    'usb_c_bore': PARAM(lambda: usb_c_bore, 0),
    'hdmi_a_width': PARAM(lambda: hdmi_a_width, 13.9),
    'hdmi_a_height': PARAM(lambda: hdmi_a_height, 4.45),
    'hdmi_a_length': PARAM(lambda: hdmi_a_length, 8),
    'hdmi_a_body_width': PARAM(lambda: hdmi_a_body_width, 17.9),
    'hdmi_a_body_height': PARAM(lambda: hdmi_a_body_height, 8.45),
    'hdmi_a_body_length': PARAM(lambda: hdmi_a_body_length, 20),
    'hdmi_a_pin_diameter': PARAM(lambda: hdmi_a_pin_diameter, 0),
    'hdmi_a_pin_length': PARAM(lambda: hdmi_a_pin_length, 0),
    'hdmi_a_bore': PARAM(lambda: hdmi_a_bore, 0),
    'de9f_width': PARAM(lambda: de9f_width, 16.4592),
    'de9f_height': PARAM(lambda: de9f_height, 8.0264),
    'de9f_length': PARAM(lambda: de9f_length, 6.2992),
    'de9f_body_width': PARAM(lambda: de9f_body_width, 20.4592),
    'de9f_body_height': PARAM(lambda: de9f_body_height, 12.0264),
    'de9f_body_length': PARAM(lambda: de9f_body_length, 20),
    'de9f_pin_diameter': PARAM(lambda: de9f_pin_diameter, 0),
    'de9f_pin_length': PARAM(lambda: de9f_pin_length, 0),
    'de9f_bore': PARAM(lambda: de9f_bore, 0),
    'de9m_width': PARAM(lambda: de9m_width, 17.0434),
    'de9m_height': PARAM(lambda: de9m_height, 8.4836),
    'de9m_length': PARAM(lambda: de9m_length, 6.0452),
    'de9m_body_width': PARAM(lambda: de9m_body_width, 21.0434),
    'de9m_body_height': PARAM(lambda: de9m_body_height, 12.4836),
    'de9m_body_length': PARAM(lambda: de9m_body_length, 20),
    'de9m_pin_diameter': PARAM(lambda: de9m_pin_diameter, 0),
    'de9m_pin_length': PARAM(lambda: de9m_pin_length, 0),
    'de9m_bore': PARAM(lambda: de9m_bore, 0),
    'rca_width': PARAM(lambda: rca_width, 9),
    'rca_height': PARAM(lambda: rca_height, 9),
    'rca_length': PARAM(lambda: rca_length, 5.5),
    'rca_body_width': PARAM(lambda: rca_body_width, 13),
    'rca_body_height': PARAM(lambda: rca_body_height, 13),
    'rca_body_length': PARAM(lambda: rca_body_length, 20),
    'rca_pin_diameter': PARAM(lambda: rca_pin_diameter, 3.25),
    'rca_pin_length': PARAM(lambda: rca_pin_length, 8),
    'rca_bore': PARAM(lambda: rca_bore, 0),
    'trs35_width': PARAM(lambda: trs35_width, 3.5),
    'trs35_height': PARAM(lambda: trs35_height, 3.5),
    'trs35_length': PARAM(lambda: trs35_length, 14),
    'trs35_body_width': PARAM(lambda: trs35_body_width, 10),
    'trs35_body_height': PARAM(lambda: trs35_body_height, 8),
    'trs35_body_length': PARAM(lambda: trs35_body_length, 20),
    'trs35_pin_diameter': PARAM(lambda: trs35_pin_diameter, 0),
    'trs35_pin_length': PARAM(lambda: trs35_pin_length, 0),
    'trs35_bore': PARAM(lambda: trs35_bore, 0),
    'dc5521_width': PARAM(lambda: dc5521_width, 5.5),
    'dc5521_height': PARAM(lambda: dc5521_height, 5.5),
    'dc5521_length': PARAM(lambda: dc5521_length, 9.5),
    'dc5521_body_width': PARAM(lambda: dc5521_body_width, 10),
    'dc5521_body_height': PARAM(lambda: dc5521_body_height, 9.5),
    'dc5521_body_length': PARAM(lambda: dc5521_body_length, 20),
    'dc5521_pin_diameter': PARAM(lambda: dc5521_pin_diameter, 0),
    'dc5521_pin_length': PARAM(lambda: dc5521_pin_length, 0),
    'dc5521_bore': PARAM(lambda: dc5521_bore, 2.1),
    'iec_c8_width': PARAM(lambda: iec_c8_width, 16.5),
    'iec_c8_height': PARAM(lambda: iec_c8_height, 8.2),
    'iec_c8_length': PARAM(lambda: iec_c8_length, 12),
    'iec_c8_body_width': PARAM(lambda: iec_c8_body_width, 20.5),
    'iec_c8_body_height': PARAM(lambda: iec_c8_body_height, 12.2),
    'iec_c8_body_length': PARAM(lambda: iec_c8_body_length, 20),
    'iec_c8_pin_diameter': PARAM(lambda: iec_c8_pin_diameter, 0),
    'iec_c8_pin_length': PARAM(lambda: iec_c8_pin_length, 0),
    'iec_c8_bore': PARAM(lambda: iec_c8_bore, 0),
    'iec_c14_width': PARAM(lambda: iec_c14_width, 24),
    'iec_c14_height': PARAM(lambda: iec_c14_height, 16),
    'iec_c14_length': PARAM(lambda: iec_c14_length, 12),
    'iec_c14_body_width': PARAM(lambda: iec_c14_body_width, 28),
    'iec_c14_body_height': PARAM(lambda: iec_c14_body_height, 20),
    'iec_c14_body_length': PARAM(lambda: iec_c14_body_length, 20),
    'iec_c14_pin_diameter': PARAM(lambda: iec_c14_pin_diameter, 0),
    'iec_c14_pin_length': PARAM(lambda: iec_c14_pin_length, 0),
    'iec_c14_bore': PARAM(lambda: iec_c14_bore, 0),
    'f_type_width': PARAM(lambda: f_type_width, 9.525),
    'f_type_height': PARAM(lambda: f_type_height, 9.525),
    'f_type_length': PARAM(lambda: f_type_length, 10),
    'f_type_body_width': PARAM(lambda: f_type_body_width, 13.525),
    'f_type_body_height': PARAM(lambda: f_type_body_height, 13.525),
    'f_type_body_length': PARAM(lambda: f_type_body_length, 20),
    'f_type_pin_diameter': PARAM(lambda: f_type_pin_diameter, 0),
    'f_type_pin_length': PARAM(lambda: f_type_pin_length, 0),
    'f_type_bore': PARAM(lambda: f_type_bore, 0),
}
TARGET = PARAM(lambda: target_part, "cable")


def plug_dims(name):
    prefix = 'proprietary' if name in ('proprietary', 'hardwired') else name
    dims = {k: P[prefix+'_'+k] for k in
            ('width','height','length','body_width','body_height','body_length',
             'pin_diameter','pin_length','bore')}
    profiles = {'usb_a':'rect','usb_c':'obround','hdmi_a':'dshape',
                'de9f':'dshape','de9m':'dshape','rca':'round','trs35':'round',
                'dc5521':'round','iec_c8':'obround','iec_c14':'dshape','f_type':'round'}
    dims['profile'] = P['proprietary_profile'] if prefix == 'proprietary' else profiles[name]
    return dims


def make_endpoint(name, point, side):
    dims = plug_dims(name)
    bl = dims['body_length']
    if name == 'hardwired':
        # A generic feed-through boot, without an invented proprietary plug.
        local = cq.Workplane('XY').circle(P['jacket_diameter']).extrude(-bl)
    else:
        local = connector_plug(dims)
    return local.rotate((0,0,0),(0,1,0), side*90).translate(
        (point[0] + side*bl, point[1], point[2]))


if P['path'] == 'coil':
    jacket, start, end = coil_with_leads({'turns':P['coil_turns'], 'pitch':P['coil_pitch'],
        'diameter':P['jacket_diameter'], 'outside_diameter':P['coil_od'],
        'lead':P['boot_length']*2})
else:
    jacket = cable_jacket({'path':P['path'],'span':P['length'],
                           'bow':P['bow'],'diameter':P['jacket_diameter']})
    start, end = (0,0,0), (P['length'],0,0)

A = make_endpoint(P['connector_a'], start, -1)
B = make_endpoint(P['connector_b'], end, 1)
for pt, sign, name in ((start,1,P['connector_a']),(end,-1,P['connector_b'])):
    dims = plug_dims(name)
    boot = strain_relief({'body_diameter':min(dims['body_width'],dims['body_height']),
                         'jacket_diameter':P['jacket_diameter']+.2,
                         'length':P['boot_length'], 'start':-.2})
    if sign < 0:
        boot = boot.rotate((0,0,0),(0,0,1),180)
    jacket = jacket.union(boot.translate(pt))
if P['ferrite_present']:
    # Only on a straight lead: it remains coaxial for every route shape.
    pt = start
    ferrite = cable_ferrite({'diameter':P['ferrite_diameter'],
                            'length':P['ferrite_length'],
                            'start':P['boot_length']+1})
    if P['path'] == 'coil':
        ferrite = ferrite.translate(pt)
    elif P['path'] != 'straight':
        # Locate a casing on the generated curve, with its local tangent.
        t = P['ferrite_position']
        wire,_ = cable_path({'span':P['length'],'bow':P['bow'],'path':P['path']})
        edge = wire.val()
        pos,tangent = edge.positionAt(t), edge.tangentAt(t)
        angle = math.degrees(math.atan2(tangent.y,tangent.x))
        ferrite = cable_ferrite({'diameter':P['ferrite_diameter'],
            'length':P['ferrite_length'],'start':-P['ferrite_length']/2})
        ferrite = ferrite.rotate((0,0,0),(0,0,1),angle).translate(pos.toTuple())
    else:
        ferrite = ferrite.translate((P['length']*P['ferrite_position'],0,0))
    jacket = jacket.union(ferrite)

if TARGET == 'connector_a':
    result = A
elif TARGET == 'connector_b':
    result = B
else:
    result = jacket.union(A).union(B)
    if TARGET == 'envelope':
        bounds = result.val().BoundingBox()
        result = cq.Workplane('XY').box(bounds.xlen, bounds.ylen, bounds.zlen).translate(
            ((bounds.xmin+bounds.xmax)/2, (bounds.ymin+bounds.ymax)/2,
             (bounds.zmin+bounds.zmax)/2))
