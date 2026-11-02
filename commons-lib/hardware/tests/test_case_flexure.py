"""Analytic spine length/volume and connected-shell motion, no material claims."""
import importlib.util,math
from pathlib import Path
import pytest
pytest.importorskip('cadquery')
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('inline_parts_flexure',ROOT/'tools/inline_parts.py')
ip=importlib.util.module_from_spec(spec);spec.loader.exec_module(ip)


@pytest.fixture(scope='module')
def ns():return ip.load(['case_flexure'],root=ROOT)


def test_closed_and_flat_endpoints_follow_the_length_convention(ns):
    p=dict(x=10,z=0.6,length=math.pi*6.4)
    assert ns['flexure_pose']({**p,'angle':0})==pytest.approx((10,13.4))
    assert ns['flexure_pose']({**p,'angle':180})==pytest.approx((10-math.pi*6.4,0.6))


def test_spine_skin_remains_connected_with_constant_volume(ns):
    p=dict(x=0,z=0.6,length=math.pi*6.4,thickness=0.5,height=100)
    expected=(p['length']+0.4)*p['thickness']*p['height']
    for angle in (0,36,72,108,144,180):
        shape=ns['flexure_web']({**p,'angle':angle}).val()
        assert shape.isValid() and len(shape.Solids())==1
        assert shape.Volume()==pytest.approx(expected,rel=1e-6)


def test_connected_shell_survives_all_animation_frames():
    from y4d_spec.geometry import _exec_cartridge
    for angle in (0,36,72,108,144,180):
        shape=_exec_cartridge(str(ROOT/'keep-case/main.py'),{'open_angle':angle,'target_part':'shell'}).val()
        assert shape.isValid() and len(shape.Solids())==1 and shape.Volume()>0
