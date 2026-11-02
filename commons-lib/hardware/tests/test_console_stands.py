"""Stand topology, source envelope axes and live cradle-angle geometry."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip('cadquery')
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('inline_parts_stands',ROOT/'tools/inline_parts.py')
ip=importlib.util.module_from_spec(spec);spec.loader.exec_module(ip)


@pytest.fixture(scope='module')
def ns():return ip.load(['console_stands'],root=ROOT)


def test_three_stand_forms_remain_one_positive_solid(ns):
    p=dict(width=110,depth=100,height=40,wall=2,base=8,radius=3,
           seat_width=60,seat_depth=60,angle=65,mount_hole=4,cable_slot=10)
    for kind in ('cradle','vertical_clip','base_disc'):
        shape=ns['console_stand_body']({**p,'kind':kind}).val()
        assert shape.isValid() and len(shape.Solids())==1 and shape.Volume()>0


def test_every_named_envelope_matches_source():
    import json
    from hyperobjects_reference import load_object
    from y4d_spec.geometry import _exec_cartridge
    m=json.loads((ROOT/'console-stand/project.json').read_text())
    for p in m['presets']:
        if not p.get('registry'):continue
        b=load_object(p['slug'])['dimensions_mm']['states']['body']
        shape=_exec_cartridge(str(ROOT/'console-stand/main.py'),{**p['values'],'target_part':'envelope'}).val()
        box=shape.BoundingBox()
        assert (box.xlen,box.ylen,box.zlen)==pytest.approx((b['width'],b['depth'],b['height']),abs=.01)


def test_cradle_angle_changes_the_back_construction():
    from y4d_spec.geometry import _exec_cartridge
    a=_exec_cartridge(str(ROOT/'console-stand/main.py'),{'tilt_angle':60,'target_part':'stand'}).val()
    b=_exec_cartridge(str(ROOT/'console-stand/main.py'),{'tilt_angle':80,'target_part':'stand'}).val()
    assert a.isValid() and b.isValid()
    assert abs(a.Volume()-b.Volume())>1
