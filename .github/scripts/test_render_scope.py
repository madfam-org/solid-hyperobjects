"""Unit checks for render_scope.py's file classification (run: python3 -m pytest .github/scripts)."""

import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("render_scope", pathlib.Path(__file__).with_name("render_scope.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


def test_non_geometry_files_are_recognised():
    for path in ("NOTICE", "LICENSE", "LICENSE.txt", "README.md", "docs/README.md", "docs/es/guide.md",
                 "thumbnail.png", "renders/iso.jpg", "CHANGELOG.md"):
        assert rs.is_non_geometry_file(path), path


def test_geometry_files_are_not():
    for path in ("main.py", "robot.scad", "part.cq", "fonts/Aileron.otf", "project.json",
                 "helpers/geometry.py", "data/profile.csv"):
        assert not rs.is_non_geometry_file(path), path


def test_chunking_keeps_order_and_size():
    assert rs.chunk(list("abcdefghij"), 4) == ["a b c d", "e f g h", "i j"]
    assert rs.chunk([], 8) == []


def test_constraints_are_metadata():
    """Feasibility rules are evaluated on the parameter set, never by the kernel."""
    assert rs._allowed("constraints")
    assert rs._allowed("constraints.0.expression")
    before = {"parameters": [{"id": "wall", "default": 2}]}
    after = {"parameters": [{"id": "wall", "default": 2}],
             "constraints": [{"expression": "wall >= 1.2", "severity": "error"}]}
    assert all(rs._allowed(p) for p in rs.changed_paths(before, after))


def test_parameter_change_alongside_constraints_still_renders():
    before = {"parameters": [{"id": "wall", "default": 2}]}
    after = {"parameters": [{"id": "wall", "default": 3}],
             "constraints": [{"expression": "wall >= 1.2"}]}
    assert not all(rs._allowed(p) for p in rs.changed_paths(before, after))


def test_animations_are_metadata():
    """Flipbook sequences are interpolated into render parameters by the API on
    demand; the cartridge's own CI render never reads the animations block."""
    assert rs._allowed("animations")
    assert rs._allowed("animations.0.to_state.explode_factor")
    before = {"parameters": [{"id": "explode_factor", "default": 0}]}
    after = {"parameters": [{"id": "explode_factor", "default": 0}],
             "animations": [{"id": "explode", "label": {"en": "Explode"},
                             "from_state": {"explode_factor": 0},
                             "to_state": {"explode_factor": 40}, "frames": 8}]}
    assert all(rs._allowed(p) for p in rs.changed_paths(before, after))


def test_parameter_change_alongside_animations_still_renders():
    before = {"parameters": [{"id": "explode_factor", "default": 0}]}
    after = {"parameters": [{"id": "explode_factor", "default": 5}],
             "animations": [{"id": "explode", "from_state": {"explode_factor": 0},
                             "to_state": {"explode_factor": 40}}]}
    assert not all(rs._allowed(p) for p in rs.changed_paths(before, after))
