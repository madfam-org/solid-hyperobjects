"""tools/presets: device-family presets generated from the keystone's reference catalog.

Runs in the manifests lane, where the keystone is installed at SPEC_PIN. Every case reads
the real catalog objects and the real manifests: a fixture that drifted from them would
prove nothing about the cartridges.
"""
import copy
import json
import pathlib
import sys

import pytest

pytest.importorskip("hyperobjects_reference")

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "presets"))

import bookfold  # noqa: E402
import clamshell  # noqa: E402
import presets  # noqa: E402
from common import (  # noqa: E402
    build_presets,
    check_manifest,
    control_count,
    generated,
    has_port,
)
from hyperobjects_reference import family_digest, load_family, load_object  # noqa: E402


def _by_slug(fam):
    _, built = generated(fam)
    return {p["slug"]: p for p in built}


def test_every_family_manifest_matches_the_catalog():
    assert presets.main(["--check-all"]) == 0


def test_families_are_registered():
    assert set(presets.FAMILIES) == {"clamshell-dual-screen-handheld", "book-fold-phone"}


def test_absence_is_a_sourced_zero():
    # Nintendo's quoted DS control list is complete and has no stick.
    ds = load_object("nintendo-ds")
    assert control_count(ds, "stick") == 0
    assert has_port(ds, "usb_c") is False
    # The DSi's controls carry no source, so nothing is known either way.
    assert control_count(load_object("nintendo-dsi"), "stick") is None


def test_unknown_counts_fall_back_by_name():
    dsi = _by_slug(clamshell.FAMILY)["nintendo-dsi"]
    assert "stick count" in dsi["registry"]["archetype_fallbacks"]
    assert "face-button count" in dsi["registry"]["archetype_fallbacks"]


def test_the_2ds_caveat_pins_the_fold():
    p = _by_slug(clamshell.FAMILY)["nintendo-2ds"]
    assert p["values"]["fold_angle"] == 0 and "caveat" in p["registry"]


def test_the_evidence_sweep_shows_as_a_named_fallback():
    p = _by_slug(bookfold.FAMILY)["samsung-galaxy-z-fold7"]
    assert "usb-c port" in p["registry"]["archetype_fallbacks"]
    assert p["values"]["usb_c_present"] is True     # the archetype default, unchanged


def test_unresolved_envelopes_get_no_preset():
    block, built = generated(clamshell.FAMILY)
    waiting = {s["slug"] for s in block["awaiting_a_source"]}
    assert {"ayn-thor", "onexplayer-onexsugar", "sony-tablet-p"} <= waiting
    assert waiting.isdisjoint(p["slug"] for p in built)


def test_provenance_records_the_digest_and_no_version():
    block, _ = generated(bookfold.FAMILY)
    assert block["catalog"]["family_digest"] == family_digest("book-fold-phone")
    assert "version" not in block["catalog"]
    assert block["catalog"]["objects"] == len(load_family("book-fold-phone"))


def test_fold_states_are_not_products():
    states = [p for p in _by_slug(bookfold.FAMILY).values() if p.get("kind") == "fold_state"]
    assert {p["values"]["fold_angle"] for p in states} == {0, 90, 180}
    assert all("registry" not in p for p in states)


def test_presets_are_ordered_by_brand_then_date():
    _, built = generated(clamshell.FAMILY)
    nintendo = [p["slug"] for p in built if p["slug"].endswith(("ds", "ds-lite", "dsi",
                                                                "dsi-xl", "3ds", "3ds-xl",
                                                                "2ds", "2ds-xl"))]
    assert nintendo.index("nintendo-ds") < nintendo.index("nintendo-3ds")


def test_a_hand_edited_preset_is_caught(tmp_path):
    manifest = json.loads((ROOT / "clamshell-dual-screen-handheld" / "project.json")
                          .read_text(encoding="utf-8"))
    edited = copy.deepcopy(manifest)
    edited["presets"][0]["values"]["deck_length"] += 1
    path = tmp_path / "project.json"
    path.write_text(json.dumps(edited), encoding="utf-8")
    problems = check_manifest(path, clamshell.FAMILY)
    assert any("presets[] differs" in p and manifest["presets"][0]["slug"] in p
               for p in problems)


def test_a_moved_fact_moves_the_preset(tmp_path):
    for obj in load_family("clamshell-dual-screen-handheld"):
        if obj["key"] == "nintendo-3ds":
            obj["dimensions_mm"]["states"]["closed"]["width"] = 75
        (tmp_path / f"{obj['key']}.json").write_text(json.dumps(obj), encoding="utf-8")
    built, _ = build_presets(clamshell.FAMILY,
                             load_family("clamshell-dual-screen-handheld", tmp_path))
    assert {p["slug"]: p for p in built}["nintendo-3ds"]["values"]["deck_depth"] == 75
    problems = check_manifest(ROOT / "clamshell-dual-screen-handheld" / "project.json",
                              clamshell.FAMILY, tmp_path)
    assert any("nintendo-3ds" in p for p in problems)
    assert any("_generated_from differs" in p for p in problems)


@pytest.mark.parametrize("module", ["common.py", "clamshell.py", "bookfold.py", "presets.py"])
def test_authored_modules_stay_under_the_size_warning(module):
    lines = (ROOT / "tools" / "presets" / module).read_text(encoding="utf-8").count("\n")
    assert lines < 600, f"{module} has {lines} lines"
