"""Exact edition diameter evidence never acquires unsourced disc dimensions."""
import json,sys
from pathlib import Path
import pytest
pytest.importorskip('hyperobjects_reference')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/presets'))
import _edition_disc,disc_media
from common import generated
from hyperobjects_reference import load_object,object_digest
from y4d_spec.rules import preset_targets


def test_missing_diameter_evidence_does_not_create_a_study(monkeypatch):
    obj={'key':'fictional','features':{'media_diameter_mm':80}}
    monkeypatch.setattr(_edition_disc,'is_sourced',lambda obj,field:False)
    assert _edition_disc.read_edition_disc(obj) is None
    monkeypatch.setattr(_edition_disc,'is_sourced',lambda obj,field:True)
    obj['features']['media_diameter_mm']=None
    assert _edition_disc.read_edition_disc(obj) is None


def test_twilight_issues_keep_sourced_diameters_and_authored_proxy_height():
    metadata,presets=generated(disc_media.FAMILY);by={p['slug']:p for p in presets}
    m=json.loads((ROOT/'disc-media/project.json').read_text())
    for platform,diameter in [('gamecube',80),('wii',120)]:
        key=f'nintendo-{platform}-the-legend-of-zelda-twilight-princess-jp'
        obj=load_object(key);p=by[key]
        assert obj['features']['media_diameter_mm']==diameter==p['values']['disc_diameter']
        assert p['mode']=='envelope' and p['values']['shell_present'] is False
        assert p['registry']['geometry_scope']=='measured-diameter-only'
        assert p['registry']['sourced_fields']==['features.media_diameter_mm']
        assert p['values']['disc_thickness']==p['registry']['authored_geometry']['proxy_thickness_mm']==1
        assert 'disc_hole' not in p['values']
        assert 'centre hole diameter' in p['registry']['unresolved_geometry']
        assert metadata['catalog']['supplemental_objects'][key]==object_digest(obj)
        m['presets']=[p]
        assert [(mode,part) for slug,mode,part,values in preset_targets(m)]==[('envelope','envelope')]
