"""Analytic envelope, cell bay and media motion checks for handheld components."""
import importlib.util
from pathlib import Path
import pytest

pytest.importorskip("cadquery")
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location("inline_parts_handheld",ROOT/"tools/inline_parts.py")
ip=importlib.util.module_from_spec(spec);spec.loader.exec_module(ip)


@pytest.fixture(scope="module")
def ns():
    return ip.load(["handheld_body"],root=ROOT)


def test_slab_keeps_the_published_extrema_with_crowned_back(ns):
    p=dict(width=100,height=150,depth=30,face_depth=30,corner_radius=8,
           back_crown=2,grip_count=0,grip_width=18,grip_length=110,
           grip_drop=0,grip_radius=3,grip_front_y=12)
    s=ns["slab_body"](p).val();b=s.BoundingBox()
    assert s.isValid() and len(s.Solids())==1
    assert (b.xlen,b.ylen,b.zlen)==pytest.approx((100,30,150),abs=1e-6)
    assert ns["rear_y"](p,0)==30
    assert ns["rear_y"](p,50)==pytest.approx(28)


def test_cell_bay_uses_the_keystone_maxima_and_clearance(ns):
    from hyperobjects_standard_parts import load_part
    d=load_part("cell-aa")["dimensions"]
    p=dict(diameter=d["diameter_max"]["value"],length=d["height_max"]["value"],
           count=4,axis="x",clearance=0.4)
    assert ns["cell_bay_size"](p)==pytest.approx((51.3,60,14.9))


def test_media_insertion_is_rigid_motion_with_positive_clearance(ns):
    p=dict(kind="slot_top",width=40,height=30,thickness=4,clearance=0.4,
           insert_depth=20,center_x=0,center_y=12,center_z=100,
           face_z=150,open_y=28,back_y=30)
    seated=ns["media_proxy"]({**p,"insert":1}).val()
    out=ns["media_proxy"]({**p,"insert":0}).val()
    assert seated.isValid() and out.isValid()
    assert seated.Volume()==pytest.approx(out.Volume())
    assert out.Center().z-seated.Center().z==pytest.approx(22)
    cavity=ns["media_slot"](p).val().BoundingBox()
    assert cavity.xlen-seated.BoundingBox().xlen==pytest.approx(0.8)


def test_kickstand_frames_preserve_one_connected_solid(ns):
    p=dict(width=30,height=40,thickness=1.2,bite=0.8,center_x=20,top_z=80,hinge_y=28)
    shapes=[ns["kickstand"]({**p,"angle":a}).val() for a in (0,15,30,45,60)]
    assert all(s.isValid() and len(s.Solids())==1 for s in shapes)
    assert all(s.Volume()==pytest.approx(shapes[0].Volume()) for s in shapes)


def test_cell_selector_and_count_drive_the_rendered_cover():
    from y4d_spec.geometry import _exec_cartridge
    from hyperobjects_standard_parts import load_part
    for kind,n in (("aa",4),("aaa",2)):
        dims=load_part("cell-"+kind)["dimensions"]
        dia=dims["diameter_max"]["value"];length=dims["height_max"]["value"]
        shape=_exec_cartridge(str(ROOT/"slab-handheld/main.py"),{
            "cell_kind":kind,"cell_count":n,"target_part":"battery_door"}).val()
        box=shape.BoundingBox()
        assert box.xlen==pytest.approx(length+0.8+3-0.8)
        assert box.zlen==pytest.approx(n*(dia+0.4)+0.4+3-0.8)
