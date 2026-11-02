"""Analytic support chassis, seat clearance and cover motion checks."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip('cadquery')
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('inline_parts_supports',ROOT/'tools/inline_parts.py')
ip=importlib.util.module_from_spec(spec);spec.loader.exec_module(ip)


@pytest.fixture(scope='module')
def ns():return ip.load(['console_supports'],root=ROOT)


def test_cradle_chassis_has_the_declared_outer_box(ns):
    p=dict(width=180,depth=80,height=110,wall=2,base=12,radius=3,style='tablet_cradle')
    s=ns['dock_chassis'](p).val();b=s.BoundingBox()
    assert s.isValid() and len(s.Solids())==1
    assert (b.xlen,b.ylen,b.zlen)==pytest.approx((180,80,110))


def test_device_tool_adds_clearance_without_double_offset(ns):
    p=dict(width=100,depth=20,height=80,clearance=.4,seat_z=12,y=30,angle=0)
    s=ns['dock_device_tool'](p).val();b=s.BoundingBox()
    assert (b.xlen,b.ylen,b.zlen)==pytest.approx((100.8,20.8,82))
    assert s.Center().y==pytest.approx(30)


def test_cover_rotation_is_rigid_and_connected(ns):
    p=dict(width=100,height=40,thickness=1,clearance=.4,y=25,z=12)
    a=ns['dock_door']({**p,'angle':0}).val();b=ns['dock_door']({**p,'angle':90}).val()
    assert a.isValid() and b.isValid() and len(a.Solids())==len(b.Solids())==1
    assert a.Volume()==pytest.approx(b.Volume())
    assert b.Center().y>a.Center().y+5


def test_named_envelope_matches_catalog_axes():
    import json
    from y4d_spec.geometry import _exec_cartridge
    from hyperobjects_reference import load_object
    m=json.loads((ROOT/'console-dock/project.json').read_text())
    for preset in m['presets']:
        if not preset.get('registry'):continue
        d=load_object(preset['slug'])['dimensions_mm']['states']['body']
        shape=_exec_cartridge(str(ROOT/'console-dock/main.py'),{**preset['values'],'target_part':'envelope'}).val()
        b=shape.BoundingBox()
        assert (b.xlen,b.ylen,b.zlen)==pytest.approx((d['width'],d['depth'],d['height']),abs=.01)
