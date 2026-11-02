# SPDX-License-Identifier: CERN-OHL-W-2.0
"""Generic adapter body and cord. Published body frame X width/Y depth/Z height.
The envelope mode is the body fit surface, excluding archetype cord and prongs.
"""
# inline-parts: cables power_cases


def PARAM(read, default):
    try:
        return read()
    except NameError:
        return default


P = {
    'body_width': PARAM(lambda: body_width, 70),
    'body_height': PARAM(lambda: body_height, 35),
    'body_depth': PARAM(lambda: body_depth, 45),
    'corner_radius': PARAM(lambda: corner_radius, 3),
    'form': PARAM(lambda: form, 'brick'),
    'prong_layout': PARAM(lambda: prong_layout, 'flat_pair'),
    'prong_width': PARAM(lambda: prong_width, 5),
    'prong_thickness': PARAM(lambda: prong_thickness, 1.5),
    'prong_spacing': PARAM(lambda: prong_spacing, 14),
    'prong_length': PARAM(lambda: prong_length, 15),
    'prong_z': PARAM(lambda: prong_z, 16),
    'inlet_kind': PARAM(lambda: inlet_kind, 'none'),
    'inlet_depth': PARAM(lambda: inlet_depth, 6),
    'cord_length': PARAM(lambda: cord_length, 120),
    'jacket_diameter': PARAM(lambda: jacket_diameter, 4),
    'boot_length': PARAM(lambda: boot_length, 12),
    'output_connector': PARAM(lambda: output_connector, 'usb_c'),
    'led_window': PARAM(lambda: led_window, True),
    'led_diameter': PARAM(lambda: led_diameter, 2),
    'label_recess': PARAM(lambda: label_recess, 0.4),
    'prong_extension': PARAM(lambda: prong_extension, 1),
    'c8_width': PARAM(lambda: c8_width, 16.5),
    'c8_height': PARAM(lambda: c8_height, 8.2),
    'c14_width': PARAM(lambda: c14_width, 24),
    'c14_height': PARAM(lambda: c14_height, 16),
    'usb_c_width': PARAM(lambda: usb_c_width, 8.25),
    'usb_c_height': PARAM(lambda: usb_c_height, 2.4),
    'usb_c_length': PARAM(lambda: usb_c_length, 6.65),
    'usb_c_body_width': PARAM(lambda: usb_c_body_width, 12.25),
    'usb_c_body_height': PARAM(lambda: usb_c_body_height, 8),
    'usb_c_body_length': PARAM(lambda: usb_c_body_length, 20),
    'usb_c_pin_diameter': PARAM(lambda: usb_c_pin_diameter, 0),
    'usb_c_pin_length': PARAM(lambda: usb_c_pin_length, 0),
    'usb_c_bore': PARAM(lambda: usb_c_bore, 0),
    'dc5521_width': PARAM(lambda: dc5521_width, 5.5),
    'dc5521_height': PARAM(lambda: dc5521_height, 5.5),
    'dc5521_length': PARAM(lambda: dc5521_length, 9.5),
    'dc5521_body_width': PARAM(lambda: dc5521_body_width, 10),
    'dc5521_body_height': PARAM(lambda: dc5521_body_height, 9.5),
    'dc5521_body_length': PARAM(lambda: dc5521_body_length, 20),
    'dc5521_pin_diameter': PARAM(lambda: dc5521_pin_diameter, 0),
    'dc5521_pin_length': PARAM(lambda: dc5521_pin_length, 0),
    'dc5521_bore': PARAM(lambda: dc5521_bore, 2.1),
}
TARGET = PARAM(lambda: target_part, "body")

body = adapter_body({'width':P['body_width'],'depth':P['body_depth'],
                     'height':P['body_height'],'radius':P['corner_radius']})
if TARGET == 'envelope':
    result = body
else:
    # A shallow label recess and an indicator seat, without glyphs or artwork.
    label = cq.Workplane('XZ').rect(P['body_width']*.55,P['body_height']*.45).extrude(
        P['label_recess']+1).translate((0,-P['body_depth']/2+P['label_recess'],P['body_height']/2))
    body=body.cut(label)
    if P['led_window']:
        led=cq.Workplane('XY').center(-P['body_width']*.3,0).circle(P['led_diameter']/2).extrude(2).translate((0,0,P['body_height']-1))
        body=body.cut(led)
    if P['inlet_kind'] != 'none':
        prefix='c8' if P['inlet_kind']=='c8' else 'c14'
        body=body.cut(adapter_inlet({'width':P[prefix+'_width'],'height':P[prefix+'_height'],
            'depth':P['inlet_depth'],'body_width':P['body_width'],'body_height':P['body_height']}))
    if P['form']=='wall_wart':
        prongs=adapter_prongs({'layout':P['prong_layout'],'width':P['prong_width'],
            'thickness':P['prong_thickness'],'length':P['prong_length']*P['prong_extension'],
            'spacing':P['prong_spacing'],'z':P['prong_z'],'body_depth':P['body_depth']})
        body=body.union(prongs)
    if TARGET == 'cord':
        z=P['body_height']*.35
        cord=cq.Workplane('YZ').circle(P['jacket_diameter']/2).extrude(P['cord_length']+.2).translate((P['body_width']/2-.2,0,z))
        boot=strain_relief({'body_diameter':P['jacket_diameter']*2,'jacket_diameter':P['jacket_diameter']+.2,'length':P['boot_length'],'start':-.2})
        cord=cord.union(boot.translate((P['body_width']/2,0,z)))
        prefix=P['output_connector']
        if prefix=='generic':
            plug=cq.Workplane('XY').box(12,8,20).translate((0,0,-10))
            bl=20
        else:
            dims={k:P[prefix+'_'+k] for k in ('width','height','length','body_width','body_height','body_length','pin_diameter','pin_length','bore')}
            dims['profile']='obround' if prefix=='usb_c' else 'round'
            plug=connector_plug(dims);bl=dims['body_length']
        plug=plug.rotate((0,0,0),(0,1,0),90).translate((P['body_width']/2+P['cord_length']+bl-.2,0,z))
        result=cord.union(plug)
    else:
        result=body
