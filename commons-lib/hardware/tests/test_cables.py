"""Interface bounds, topology and a half-turn coil, using the real CAD kernel."""
import importlib.util
import math
from pathlib import Path

import pytest

cq = pytest.importorskip('cadquery')
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('inline_parts', ROOT/'tools/inline_parts.py')
ip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ip)


@pytest.fixture(scope='module')
def ns():
    return ip.load(['cables'], root=ROOT)


def test_standard_shell_extents_and_bore(ns):
    p = dict(width=5.5,height=5.5,length=9.5,body_width=10,body_height=10,
             body_length=20,profile='round',bore=2.1)
    result = ns['connector_plug'](p)
    assert len(result.solids().vals()) == 1 and result.val().isValid()
    tip = result.intersect(cq.Workplane('XY').box(20,20,1).translate((0,0,8)))
    assert tip.val().Volume() == pytest.approx(math.pi*(5.5**2-2.1**2)/4,abs=1e-6)
    b = result.val().BoundingBox()
    assert (b.zmin,b.zmax) == pytest.approx((-20,9.5),abs=1e-6)


def test_obround_keeps_interface_bounds(ns):
    p = dict(width=8.25,height=2.4,length=6.65,body_width=12,body_height=7,
             body_length=20,profile='obround')
    result = ns['connector_plug'](p)
    tip = result.intersect(cq.Workplane('XY').box(20,20,1).translate((0,0,5)))
    b=tip.val().BoundingBox()
    assert (b.xlen,b.ylen)==pytest.approx((8.25,2.4),abs=1e-6)


def test_straight_jacket_length_and_volume(ns):
    result = ns['cable_jacket'](dict(path='straight',span=100,bow=0,diameter=4))
    assert len(result.solids().vals()) == 1 and result.val().isValid()
    assert result.val().Volume()==pytest.approx(math.pi*4*100,rel=1e-6)
    assert result.val().BoundingBox().xlen==pytest.approx(100,abs=1e-6)


def test_half_turn_coil_uses_true_endpoints(ns):
    result,start,end=ns['coil_cord'](dict(turns=3.5,pitch=7,diameter=4,outside_diameter=24))
    assert len(result.solids().vals())==1 and result.val().isValid()
    assert start==pytest.approx((0,0,-10),abs=1e-6)
    assert end==pytest.approx((24.5,0,10),abs=1e-6)
    with pytest.raises(ValueError):
        ns['coil_cord'](dict(turns=3.2,pitch=7,diameter=4,outside_diameter=24))


def test_continuous_coil_leads_export_watertight(ns,tmp_path):
    trimesh=pytest.importorskip('trimesh')
    result,a,b=ns['coil_with_leads'](dict(turns=3.5,pitch=7,diameter=4,outside_diameter=24,lead=24))
    assert len(result.solids().vals())==1 and result.val().isValid()
    out=tmp_path/'coil.stl';cq.exporters.export(result,str(out))
    assert trimesh.load(str(out)).is_watertight
    assert a==pytest.approx((-24,0,-10),abs=1e-6)
    assert b==pytest.approx((48.5,0,10),abs=1e-6)
