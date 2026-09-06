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
