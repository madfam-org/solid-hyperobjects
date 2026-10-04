"""Unit checks for render_scope.py's file classification (run: python3 -m pytest .github/scripts)."""

import importlib.util
import pathlib

import pytest

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


def test_verification_changes_keep_the_cartridge_in_scope():
    """A parity exemption or a declared body count lives under `verification`.

    Those are the manifest's own claims about what the render must produce, so
    changing one has to be re-proven by a render — the allow-list must never
    grow to cover them, or a cartridge could widen its own tolerance and skip
    the gate that would have checked it.
    """
    assert not rs._allowed("verification")
    assert not rs._allowed("verification.stages.geometry.checks.body_count.expected")
    assert not rs._allowed(
        "verification.mode_overrides.bolt.part_overrides.bolt.geometry.parity.tolerance"
    )
    before = {"verification": {"stages": {"geometry": {"checks": {"body_count": {"expected": 1}}}}}}
    after = {"verification": {"stages": {"geometry": {"checks": {"body_count": {"expected": 2}}}}}}
    assert not all(rs._allowed(p) for p in rs.changed_paths(before, after))


def test_unparseable_manifest_fails_closed(tmp_path, monkeypatch):
    """A manifest that does not parse on either side keeps the cartridge in scope.

    The lane must never read "I could not tell" as "nothing to render".
    """
    import subprocess as sp

    repo = tmp_path / "repo"
    (repo / "widget").mkdir(parents=True)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@e", "PATH": "/usr/bin:/bin:/usr/local/bin"}

    def git(*args):
        sp.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)

    git("init", "-q")
    (repo / "widget" / "project.json").write_text('{"project": {"name": "a"}}')
    git("add", "-A")
    git("commit", "-qm", "base")
    base = sp.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
                  env=env).stdout.strip()
    (repo / "widget" / "project.json").write_text('{"project": {"name": "b",,}')  # invalid JSON
    git("add", "-A")
    git("commit", "-qm", "broken")
    head = sp.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
                  env=env).stdout.strip()

    monkeypatch.chdir(repo)
    assert rs._manifest_at(head, "widget") is None
    assert rs.needs_render(base, head, "widget")


@pytest.mark.parametrize("source_key", ["scad_file", "cq_file", "graph_file"])
def test_spec_pin_change_includes_unchanged_graph_cartridges(monkeypatch, source_key):
    import json
    objects = {
        "base:.github/workflows/ci.yml": "env:\n  SPEC_PIN: old\n",
        "head:.github/workflows/ci.yml": "env:\n  SPEC_PIN: new\n",
        "head:graph/project.json": json.dumps({"modes": [{source_key: "part.graph.json"}]}),
        "head:plain/project.json": json.dumps({"modes": [{"cq_file": "main.py"}]}),
    }
    def git(*args):
        if args[0] == "ls-tree":
            return "plain/project.json\ngraph/project.json\ndocs/nested/project.json\n"
        return objects[args[1]]
    monkeypatch.setattr(rs, "_git", git)
    assert rs.graph_scope_on_spec_change("base", "head") == ["graph"]


def test_unchanged_spec_pin_does_not_expand_scope(monkeypatch):
    monkeypatch.setattr(rs, "_git", lambda *args: "env:\n  SPEC_PIN: same\n")
    assert rs.graph_scope_on_spec_change("base", "head") == []


def test_missing_spec_pin_fails_closed(monkeypatch):
    import pytest
    monkeypatch.setattr(rs, "_git", lambda *args: "env: {}")
    with pytest.raises(ValueError, match="Cannot resolve SPEC_PIN"):
        rs.graph_scope_on_spec_change("base", "head")


# ── F6: frames-only diffs force a render ─────────────────────────────────────
def _iface(**extra):
    base = {"id": "motor_face", "label": {"en": "Motor face"}, "geometry_type": "bolt_pattern"}
    base.update(extra)
    return base


FRAME = {"part": "plate", "origin": [0, 0, "plate_t"], "normal": [0, 0, 1], "x_axis": [1, 0, 0]}


@pytest.mark.parametrize(
    "field, before_value, after_value",
    [
        ("frame", None, FRAME),
        ("frame", FRAME, {**FRAME, "origin": [0, 0, "plate_t + 1"]}),
        ("size_key", None, "nema-17-face"),
        ("size_key", "nema-17-face", {"param": "nema", "map": {"NEMA17": "nema-17-face"}}),
        ("polarity", "male", "female"),
        ("symmetry", 4, 2),
        ("let", None, {"pilot_r": {"param": "nema", "map": {"NEMA17": 11}}}),
        ("let", {"h": "plate_t"}, {"h": "plate_t * 2"}),
        ("geometry_type", "bolt_pattern", "flange"),
    ],
)
def test_a_frame_gate_field_change_forces_a_render(field, before_value, after_value):
    def manifest(value):
        iface = _iface()
        if value is not None:
            iface[field] = value
        return {"hyperobject": {"cdg_interfaces": [iface]}}

    before, after = manifest(before_value), manifest(after_value)
    # The allow-list alone would skip it: `hyperobject` is metadata…
    assert all(rs._allowed(p) for p in rs.changed_paths(before, after))
    # …but the frame gate must re-judge the interface.
    assert rs.frame_fields_changed(before, after)


def test_the_nested_project_hyperobject_list_is_gated_too():
    before = {"project": {"hyperobject": {"cdg_interfaces": [_iface()]}}}
    after = {"project": {"hyperobject": {"cdg_interfaces": [_iface(frame=FRAME)]}}}
    assert rs.frame_fields_changed(before, after)


def test_a_label_only_interface_change_stays_metadata():
    before = {"hyperobject": {"cdg_interfaces": [_iface(frame=FRAME)]}}
    after = {"hyperobject": {"cdg_interfaces": [
        {**_iface(frame=FRAME), "label": {"en": "Motor face", "es": "Cara del motor"},
         "standard": "NEMA 17", "compatible_with": ["motor-mount"]}]}}
    assert not rs.frame_fields_changed(before, after)
    assert all(rs._allowed(p) for p in rs.changed_paths(before, after))


def test_removing_a_framed_interface_forces_a_render():
    before = {"hyperobject": {"cdg_interfaces": [_iface(frame=FRAME), _iface(id="other")]}}
    after = {"hyperobject": {"cdg_interfaces": [_iface(id="other")]}}
    assert rs.frame_fields_changed(before, after)


def test_needs_render_keeps_a_frames_only_pr_in_scope(tmp_path, monkeypatch):
    """End to end through git: a PR that only adds a frame is rendered."""
    import json
    import subprocess as sp

    repo = tmp_path / "repo"
    (repo / "widget").mkdir(parents=True)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@e", "PATH": "/usr/bin:/bin:/usr/local/bin"}

    def git(*args):
        return sp.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True,
                      env=env).stdout.strip()

    def commit(manifest, msg):
        (repo / "widget" / "project.json").write_text(json.dumps(manifest))
        git("add", "-A")
        git("commit", "-qm", msg)
        return git("rev-parse", "HEAD")

    git("init", "-q")
    base = commit({"hyperobject": {"cdg_interfaces": [_iface()]}}, "base")
    framed = commit({"hyperobject": {"cdg_interfaces": [_iface(frame=FRAME)]}}, "frame")
    relabelled = commit({"hyperobject": {"cdg_interfaces": [
        {**_iface(frame=FRAME), "label": {"en": "Motor face (top)"}}]}}, "label")
    monkeypatch.chdir(repo)
    assert rs.needs_render(base, framed, "widget")
    assert not rs.needs_render(framed, relabelled, "widget")
