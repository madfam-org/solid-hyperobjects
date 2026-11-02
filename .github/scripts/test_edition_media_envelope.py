"""Exact edition facts may feed only a blank envelope, with pinned provenance."""
import sys
from pathlib import Path

import pytest
pytest.importorskip('hyperobjects_reference')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/presets'))
import _edition_media
import plug_in_media
from common import build_presets
from y4d_spec.rules import preset_targets


def edition():
    return dict(key='fixture-edition', kind='edition', family=None, status='partial',
        model='Fictional issue', brand='Fixture',
        edition=dict(product_code='FIXTURE', platform='fictional', media=dict(key=None)),
        features=dict(media_width_mm=115, media_height_mm=75, media_depth_mm=19),
        sources=[dict(field='features.catalog_media_size', url='https://example.org/fixture')])


def test_missing_source_or_axis_does_not_create_preset(monkeypatch):
    monkeypatch.setattr(_edition_media, 'is_sourced', lambda obj, field: False)
    assert _edition_media.read_edition(edition()) is None
    monkeypatch.setattr(_edition_media, 'is_sourced', lambda obj, field: True)
    obj = edition(); obj['features']['media_depth_mm'] = None
    assert _edition_media.read_edition(obj) is None


def test_edition_is_envelope_only_and_has_no_invented_internal_dimensions(monkeypatch):
    monkeypatch.setattr(_edition_media, 'is_sourced', lambda obj, field: True)
    presets, skipped = build_presets(plug_in_media.FAMILY, [edition()])
    p = next(p for p in presets if p['slug'] == 'fixture-edition')
    assert not skipped and p['mode'] == 'envelope'
    assert p['registry']['geometry_scope'] == 'measured-envelope-only'
    assert p['registry']['product_code'] == 'FIXTURE'
    assert p['values']['shell_width'] == 115 and p['values']['shell_height'] == 75
    assert p['values']['shell_thickness'] == 19
    assert p['values']['corner_radius'] == 0 and p['values']['grip_thickness'] == 0
    assert not {'edge_contacts', 'pcb_thickness', 'label_front_width'} & p['values'].keys()
    import json
    m = json.loads((ROOT/'plug-in-media/project.json').read_text())
    m['presets'] = [p]
    assert [(mode,part) for slug,mode,part,values in preset_targets(m)] == [('envelope','envelope')]


@pytest.mark.parametrize('emit', ['presets', 'block', 'skipped'])
def test_cli_emit_and_manifest_generation_use_the_same_supplemental_sources(emit, capsys):
    import json
    import presets
    from common import generated
    metadata, expected = generated(plug_in_media.FAMILY)
    assert presets.main(['--family', 'plug-in-media', '--emit', emit]) == 0
    result = json.loads(capsys.readouterr().out)
    if emit == 'block':
        assert result == {'_generated_from': metadata, 'presets': expected}
        assert 'nintendo-64-the-legend-of-zelda-ocarina-of-time-jp' in result['_generated_from']['catalog']['supplemental_objects']
    elif emit == 'skipped':
        assert result == metadata['awaiting_a_source']
    else:
        assert result == expected
        assert any(p['slug'] == 'nintendo-64-the-legend-of-zelda-ocarina-of-time-jp' for p in result)


def test_majora_issue_measurements_stay_separate_and_envelope_scoped():
    from common import generated
    from hyperobjects_reference import load_object, object_digest
    metadata, presets = generated(plug_in_media.FAMILY)
    by = {p['slug']: p for p in presets}
    dimensions = []
    for key in ('nintendo-64-the-legend-of-zelda-majoras-mask-jp',
                'nintendo-64-the-legend-of-zelda-majoras-mask-expansion-pak-jp'):
        obj = load_object(key); p = by[key]; f = obj['features']
        assert p['mode'] == 'envelope'
        assert p['registry']['edition'] == key
        assert p['registry']['product_code'] == obj['edition']['product_code']
        assert metadata['catalog']['supplemental_objects'][key] == object_digest(obj)
        actual = tuple(p['values'][k] for k in ('shell_width', 'shell_height', 'shell_thickness'))
        assert actual == tuple(f[k] for k in ('media_width_mm', 'media_height_mm', 'media_depth_mm'))
        dimensions.append(actual)
    assert dimensions == [(115, 75, 19), (115, 76, 18)]
