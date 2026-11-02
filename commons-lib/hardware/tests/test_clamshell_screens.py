"""The new display switch must change a real lower-deck cavity."""
from pathlib import Path
import pytest
pytest.importorskip('cadquery')
ROOT=Path(__file__).resolve().parents[3]


def test_screen_absence_restores_exact_display_recess_volume():
    from y4d_spec.geometry import _exec_cartridge
    script=str(ROOT/'clamshell-dual-screen-handheld/main.py')
    with_screen=_exec_cartridge(script,{'target_part':'lower_deck','secondary_screen_present':True}).val()
    without=_exec_cartridge(script,{'target_part':'lower_deck','secondary_screen_present':False}).val()
    assert with_screen.isValid() and without.isValid()
    assert without.Volume()-with_screen.Volume()==pytest.approx(80*50*.8,abs=1e-5)
