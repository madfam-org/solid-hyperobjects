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
