"""Analytic case-envelope, connected hub and rigid hinge checks."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip('cadquery')
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('inline_parts_cases',ROOT/'tools/inline_parts.py')
ip=importlib.util.module_from_spec(spec);spec.loader.exec_module(ip)


@pytest.fixture(scope='module')
def ns():return ip.load(['media_cases'],root=ROOT)


def test_pan_keeps_closed_extrema_and_positive_floor(ns):
    p=dict(width=100,height=80,depth=10,wall=1.2,radius=2,z=0)
    s=ns['case_pan'](p).val();b=s.BoundingBox()
    assert s.isValid() and len(s.Solids())==1
    assert (b.xlen,b.ylen,b.zlen)==pytest.approx((100,80,10))
    import cadquery as cq
    bottom=cq.Workplane('XY').add(s).intersect(cq.Workplane('XY').box(10,10,0.5).translate((0,0,0.25)))
    assert bottom.val().Volume()==pytest.approx(50)


def test_rosette_keeps_a_connected_root(ns):
    hub=ns['case_disc_hub'](dict(diameter=14.5,height=4,z=2,kind='rosette',petals=8,slot_width=0.7)).val()
    assert hub.isValid() and len(hub.Solids())==1 and hub.Volume()>0


def test_opening_is_rigid_and_fixes_the_hinge_axis(ns):
    panel=ns['case_box'](dict(width=150,height=140,depth=1.2,radius=2,z=12.8))
    closed=panel.val();opened=ns['case_open'](panel,dict(width=150,thickness=14,angle=90)).val()
    assert opened.isValid() and opened.Volume()==pytest.approx(closed.Volume())
    assert opened.Center().z>closed.Center().z+50


def test_each_archetype_envelope_is_exact():
    import json
    from y4d_spec.geometry import _exec_cartridge
    m=json.loads((ROOT/'jewel-case/project.json').read_text())
    for p in m['presets']:
        v=p['values'];shape=_exec_cartridge(str(ROOT/'jewel-case/main.py'),{**v,'target_part':'envelope'}).val()
        b=shape.BoundingBox()
        assert (b.xlen,b.ylen,b.zlen)==pytest.approx((v['case_width'],v['case_height'],v['case_thickness']),abs=0.01)
