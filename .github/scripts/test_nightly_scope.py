"""Unit checks for nightly_scope.py (run: python3 -m pytest .github/scripts)."""

import importlib.util
import json
import pathlib

import pytest

spec = importlib.util.spec_from_file_location(
    "nightly_scope", pathlib.Path(__file__).with_name("nightly_scope.py"))
ns = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ns)


def test_plan_groups_are_bounded_and_ordered():
    groups = ns.plan(list("jihgfedcba"), 4, slow=())
    assert groups == ["a b c d", "e f g h", "i j"]
    assert all(len(g.split()) <= 4 for g in groups)


def test_plan_is_deterministic():
    """Two runs of the same scope must produce byte-identical groups."""
    slugs = ["m", "b", "z", "a", "q", "c"]
    assert ns.plan(slugs, 2, slow=()) == ns.plan(sorted(slugs), 2, slow=())
    assert ns.plan(slugs, 2, slow=()) == ["a b", "c m", "q z"]


def test_slow_cartridges_get_a_group_of_their_own():
    """zipper's coil takes >16 min for ONE render; it must not starve seven."""
    groups = ns.plan(["a", "b", "c", "zipper", "d"], 8, slow=("zipper",))
    assert groups[0] == "zipper"
    assert all("zipper" not in g.split() for g in groups[1:])
    assert groups[1].split() == ["a", "b", "c", "d"]


def test_slow_group_comes_first():
    """Longest job first, so the matrix wall clock is not the slow job queued last."""
    groups = ns.plan([f"c{i:02d}" for i in range(20)] + ["zipper"], 8,
                     slow=("zipper",))
    assert groups[0] == "zipper"


def test_slow_entry_absent_from_scope_is_harmless():
    assert ns.plan(["a", "b"], 8, slow=("zipper",)) == ["a b"]


def test_every_slug_appears_exactly_once():
    slugs = [f"c{i:03d}" for i in range(101)] + ["zipper"]
    groups = ns.plan(slugs, 8, slow=("zipper",))
    flat = [s for g in groups for s in g.split()]
    assert sorted(flat) == sorted(slugs)
    assert len(flat) == len(set(flat))


def test_zipper_is_declared_slow():
    """The regression this lane exists for: zipper must stay in a lane of its own."""
    assert "zipper" in ns.SLOW


def test_chunk_size_must_be_positive():
    with pytest.raises(ValueError):
        ns.plan(["a"], 0)


def test_cartridges_skips_dirs_without_a_manifest(tmp_path):
    (tmp_path / "alpha").mkdir()
    (tmp_path / "alpha" / "project.json").write_text("{}")
    (tmp_path / "libs").mkdir()           # submodule mount point, no manifest
    (tmp_path / ".github").mkdir()        # dotdir
    (tmp_path / "beta").mkdir()
    (tmp_path / "beta" / "project.json").write_text("{}")
    assert ns.cartridges(str(tmp_path)) == ["alpha", "beta"]


def test_main_emits_a_json_matrix_and_a_slug_list(tmp_path, capsys):
    for name in ("alpha", "beta", "zipper"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "project.json").write_text("{}")
    listing = tmp_path / "scope.txt"
    rc = ns.main(["--root", str(tmp_path), "--chunks", "8",
                  "--slug-list", str(listing)])
    assert rc == 0
    groups = json.loads(capsys.readouterr().out)
    assert groups == ["zipper", "alpha beta"]
    assert listing.read_text().split() == ["alpha", "beta", "zipper"]


def test_limit_truncates_the_scope_for_a_proof_run(tmp_path, capsys):
    for i in range(20):
        (tmp_path / f"c{i:02d}").mkdir()
        (tmp_path / f"c{i:02d}" / "project.json").write_text("{}")
    listing = tmp_path / "scope.txt"
    ns.main(["--root", str(tmp_path), "--chunks", "8", "--limit", "16",
             "--slug-list", str(listing)])
    out = capsys.readouterr()
    groups = json.loads(out.out)
    assert [len(g.split()) for g in groups] == [8, 8]
    # The slug list is the LIMITED scope, so the completeness check compares
    # against what the matrix was actually told to render.
    assert len(listing.read_text().split()) == 16
    assert "deliberately incomplete" in out.err
