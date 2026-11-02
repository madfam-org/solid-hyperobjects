"""Analytic adapter fit bounds and positive-volume prong joins."""
import importlib.util
from pathlib import Path

import pytest

cq=pytest.importorskip('cadquery')
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('inline_parts',ROOT/'tools/inline_parts.py')
ip=importlib.util.module_from_spec(spec);spec.loader.exec_module(ip)


def test_body_dimensions_are_not_expanded_by_rounding():
    n=ip.load(['power_cases'],root=ROOT)
    s=n['adapter_body'](dict(width=65.8,depth=34.6,height=50.8,radius=3))
    b=s.val().BoundingBox()
    assert (b.xlen,b.ylen,b.zlen,b.zmin)==pytest.approx((65.8,34.6,50.8,0),abs=1e-6)
    assert s.val().isValid() and len(s.solids().vals())==1


@pytest.mark.parametrize('layout',['flat_pair','round_pair','angled_pair','three_flat'])
def test_prongs_overlap_body_and_remain_one_solid(layout):
    n=ip.load(['power_cases'],root=ROOT)
    body=n['adapter_body'](dict(width=70,depth=45,height=35,radius=3))
    prongs=n['adapter_prongs'](dict(layout=layout,width=5,thickness=1.5,length=15,
                                    spacing=14,z=16,body_depth=45))
    result=body.union(prongs)
    assert result.val().isValid() and len(result.solids().vals())==1
    assert result.val().Volume()>body.val().Volume()
