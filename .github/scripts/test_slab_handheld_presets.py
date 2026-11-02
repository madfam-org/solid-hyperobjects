"""Preserve source axes and omit unsupported tablet-only envelopes."""
import importlib.util
from pathlib import Path
import sys
import pytest

pytest.importorskip("hyperobjects_reference")
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools/presets"))
spec=importlib.util.spec_from_file_location("slab_handheld_presets",ROOT/"tools/presets/slab_handheld.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)


def test_source_height_can_be_thickness_without_changing_the_catalog():
    o={'key':'test','dimensions_mm':{'states':{'body':{'width':170,'height':18,'depth':73}}}}
    s=h.read_device(o)
    assert (s['width'],s['height'],s['depth'])==(170,73,18)
    assert o['dimensions_mm']['states']['body']['height']==18


def test_with_controllers_never_substitutes_for_tablet_body():
    o={'key':'test','dimensions_mm':{'states':{'with_controllers':{'width':240,'height':102,'depth':14}}}}
    assert h.read_device(o) is None


def test_uncovered_lists_keep_fallbacks(monkeypatch):
    o={'key':'test','dimensions_mm':{'states':{'body':{'width':170,'height':90,'depth':26}}}}
    s=h.read_device(o)
    assert 'media kind' in s['_fallbacks']
    assert 'stick count' in s['_fallbacks']


def test_every_archetype_reaches_every_render_part():
    import json
    from y4d_spec.rules import preset_targets
    m=json.loads((ROOT/'slab-handheld/project.json').read_text())
    targets=preset_targets(m)
    for p in m['presets']:
        assert len([t for t in targets if t[0]==p['slug']])==7
