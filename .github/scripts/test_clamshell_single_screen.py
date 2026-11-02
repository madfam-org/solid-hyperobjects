"""Preserve legacy presets/graph and route only sourced screen absence to CQ."""
import hashlib,json,sys
from pathlib import Path
import pytest
pytest.importorskip('hyperobjects_reference')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/presets'))
import clamshell
from common import build_presets
from y4d_spec.rules import preset_targets


def test_legacy_values_and_graph_bytes_are_unchanged():
    lock=json.loads((ROOT/'.github/fixtures/clamshell-legacy-values.json').read_text())
    m=json.loads((ROOT/'clamshell-dual-screen-handheld/project.json').read_text())
    by={p['slug']:p for p in m['presets']}
    for key,expected in lock['preset_values'].items():
        actual=hashlib.sha256(json.dumps(by[key]['values'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert actual==expected,key
    assert hashlib.sha256((ROOT/'clamshell-dual-screen-handheld/clamshell.graph.json').read_bytes()).hexdigest()==lock['graph_sha256']


def test_legacy_graph_and_cadquery_preset_targets_remain_covered():
    lock=json.loads((ROOT/'.github/fixtures/clamshell-legacy-values.json').read_text())
    m=json.loads((ROOT/'clamshell-dual-screen-handheld/project.json').read_text())
    actual={(pid,mode,part) for pid,mode,part,values in preset_targets(m)}
    assert {tuple(row) for row in lock['preset_targets']} <= actual
    graph=next(mode for mode in m['modes'] if mode['id']=='graph_device')
    assert graph['engine']=='graph' and graph['scad_file']=='clamshell.graph.json'
    assert graph['parts']==['lower_deck','upper_deck','hinge']
    single=[(mode,part) for pid,mode,part in actual if pid=='archetype-single-screen']
    assert set(single)=={('configurable_screens',p) for p in ('lower_deck','upper_deck','hinge')}


def fixture_object():
    return {'key':'fixture-fold','brand':'Fixture','model':'Fictional fold',
        'dimensions_mm':{'states':{'closed':{'width':90,'height':100,'depth':24}}},
        'displays':[{'role':'primary','active_area_mm':{'width':60,'height':40}}]}


def test_uncovered_display_list_does_not_establish_absence(monkeypatch):
    monkeypatch.setattr(clamshell,'is_sourced',lambda obj,field:False)
    source=clamshell.read_device(fixture_object())
    assert 'secondary_screen_present' not in source
    assert '_preset_mode' not in source


def test_complete_single_display_routes_to_new_cq_mode(monkeypatch):
    monkeypatch.setattr(clamshell,'is_sourced',lambda obj,field:field=='displays')
    obj=fixture_object();source=clamshell.read_device(obj)
    assert source['secondary_screen_present'] is False
    assert source['_preset_mode']=='configurable_screens'
    presets,skipped=build_presets(clamshell.FAMILY,[obj])
    named=next(p for p in presets if p['slug']==obj['key'])
    assert not skipped and named['mode']=='configurable_screens'
    assert named['values']['secondary_screen_present'] is False
    assert 'stick count' in named['registry']['archetype_fallbacks']
