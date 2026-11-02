"""tools/projections.py: the view grammar and the --check walk (no CAD kernel needed)."""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import projections


def test_view_with_overrides():
    name, direction, overrides = projections.parse_view("open:0,-1,0.35:fold_angle=180,usb_c_present=false")
    assert name == "open" and direction == (0.0, -1.0, 0.35)
    assert overrides == {"fold_angle": 180, "usb_c_present": False}


def test_view_with_a_select_value():
    _, _, overrides = projections.parse_view("iso:1,-1,1:body_plan=tower")
    assert overrides == {"body_plan": "tower"}


@pytest.mark.parametrize("bad", ["iso", "iso:1,1", "iso:0,0,0"])
def test_malformed_views_are_refused(bad):
    with pytest.raises(SystemExit):
        projections.parse_view(bad)


def test_check_counts_the_committed_clamshell_projections(capsys):
    rc = projections.main(["clamshell-dual-screen-handheld", "--mode", "device",
                           "--view", "closed:0,0,1", "--view", "open:0,0,1", "--check"])
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "missing=0" in out


def scoped_manifest(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(projections, 'REPO_ROOT', tmp_path)
    cartridge = tmp_path / 'fixture'
    out = cartridge / 'docs/projections'; out.mkdir(parents=True)
    (cartridge / 'project.json').write_text(json.dumps({
        'modes': [{'id': 'media', 'cq_file': 'fixture.py', 'parts': ['front', 'back']},
                  {'id': 'envelope', 'cq_file': 'fixture.py', 'parts': ['envelope']}],
        'presets': [{'slug': 'shared', 'values': {}},
                    {'slug': 'assembled', 'mode': 'media', 'values': {}},
                    {'slug': 'exact-issue', 'mode': 'envelope', 'values': {}}],
    }))
    for slug in ('archetype-default', 'shared', 'assembled'):
        (out / f'{slug}-iso.svg').write_text('<svg/>')


def test_projection_check_does_not_expand_a_scoped_envelope_into_internal_parts(tmp_path, monkeypatch, capsys):
    scoped_manifest(tmp_path, monkeypatch)
    assert projections.main(['fixture', '--mode', 'media', '--view', 'iso:1,-1,1', '--check']) == 0
    assert 'targets=3' in capsys.readouterr().out


def test_explicit_wrong_mode_request_fails_instead_of_rendering_archetype_internals(tmp_path, monkeypatch):
    scoped_manifest(tmp_path, monkeypatch)
    with pytest.raises(SystemExit, match="belongs to mode 'envelope'"):
        projections.main(['fixture', '--mode', 'media', '--preset', 'exact-issue',
                          '--view', 'iso:1,-1,1', '--check'])
