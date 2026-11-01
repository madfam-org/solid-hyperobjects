"""Unit checks for size_gate.py (run: python3 -m pytest .github/scripts)."""

import importlib.util
import json
import pathlib
import subprocess as sp

import pytest

spec = importlib.util.spec_from_file_location("size_gate", pathlib.Path(__file__).with_name("size_gate.py"))
sg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg)

ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@e", "PATH": "/usr/bin:/bin:/usr/local/bin"}
MARKER = "# BEGIN commons-lib/hardware/controls.py@" + "a" * 40


def lines(n, first="x = 1"):
    return "\n".join([first] + ["pass"] * (n - 1)) + "\n"


def put(repo, files):
    for rel, text in files.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    sp.run(["git", "add", "-A"], cwd=repo, check=True, env=ENV)


@pytest.fixture
def repo(tmp_path):
    sp.run(["git", "init", "-q"], cwd=tmp_path, check=True, env=ENV)
    put(tmp_path, {"small/main.py": lines(10), "warn/main.py": lines(601), "big/main.scad": lines(900),
                   "notes.md": lines(2000), ".github/fixtures/log.py": lines(2000)})
    return tmp_path


def run(repo, *args):
    return sg.main(["--root", str(repo), *args])


def baseline(repo):
    return json.loads((repo / sg.BASELINE).read_text())["files"]


def test_counts_like_wc_l(tmp_path):
    (tmp_path / "f").write_bytes(b"a\nb\nc")
    assert sg.count_lines(tmp_path / "f") == 2


def test_measures_tracked_py_and_scad_only(repo):
    (repo / "untracked.py").write_text(lines(5000))
    sizes, exempt = sg.measure(repo)
    assert set(sizes) == {"small/main.py", "warn/main.py", "big/main.scad"} and exempt == []


def test_a_new_file_over_800_fails_and_over_600_warns(repo, capsys):
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert "::error file=big/main.scad" in out and "a new file over the hard limit" in out
    assert "::warning file=warn/main.py" in out


def test_seed_then_grandfathered_passes(repo, capsys):
    assert run(repo, "--update-baseline") == 0
    assert baseline(repo) == {"big/main.scad": 900}
    assert run(repo) == 0
    assert "grandfathered: big/main.scad" in capsys.readouterr().out


def test_a_baselined_file_that_grows_fails(repo, capsys):
    run(repo, "--update-baseline")
    put(repo, {"big/main.scad": lines(901)})
    assert run(repo) == 1
    assert "grew from 900 to 901" in capsys.readouterr().out


def test_a_shrunk_offender_must_leave_the_baseline_deliberately(repo, capsys):
    run(repo, "--update-baseline")
    put(repo, {"big/main.scad": lines(700)})
    assert run(repo) == 1
    assert "no longer needs its baseline exception" in capsys.readouterr().out
    assert run(repo, "--update-baseline") == 0
    assert baseline(repo) == {}
    assert run(repo) == 0


def test_update_ratchets_a_baselined_size_down(repo):
    run(repo, "--update-baseline")
    put(repo, {"big/main.scad": lines(850)})
    assert run(repo) == 0
    assert run(repo, "--update-baseline") == 0
    assert baseline(repo) == {"big/main.scad": 850}


def test_update_never_grows_the_baseline(repo, capsys):
    run(repo, "--update-baseline")
    put(repo, {"new/main.py": lines(801)})
    assert run(repo, "--update-baseline") == 1
    assert "the baseline never grows" in capsys.readouterr().out
    assert baseline(repo) == {"big/main.scad": 900}
    put(repo, {"new/main.py": lines(5), "big/main.scad": lines(950)})
    assert run(repo, "--update-baseline") == 1
    assert baseline(repo) == {"big/main.scad": 900}


def test_a_removed_baselined_file_must_be_dropped(repo, capsys):
    run(repo, "--update-baseline")
    sp.run(["git", "rm", "-qf", "big/main.scad"], cwd=repo, check=True, env=ENV)
    assert run(repo) == 1
    assert "no longer measured" in capsys.readouterr().out


def test_generated_main_with_marker_and_family_is_exempt(repo):
    put(repo, {"fam/family.py": lines(300), "fam/main.py": lines(1200, first=MARKER)})
    sizes, exempt = sg.measure(repo)
    assert exempt == ["fam/main.py"] and sizes["fam/family.py"] == 300


@pytest.mark.parametrize("files", [
    {"fam/main.py": lines(1200, first=MARKER)},                          # no family.py
    {"fam/family.py": lines(3), "fam/main.py": lines(1200)},             # no marker
    {"fam/family.py": lines(3), "fam/other.py": lines(1200, first=MARKER)},  # not main.py
    {"fam/family.py": lines(3),
     "fam/main.py": lines(1200, first="x = '# BEGIN commons-lib/hardware/a.py@" + "a" * 40 + "'")},
])
def test_the_exemption_needs_the_marker_and_the_family(repo, files):
    put(repo, files)
    sizes, exempt = sg.measure(repo)
    assert exempt == [] and any(n == 1200 for n in sizes.values())


def test_the_repository_passes_its_own_gate():
    assert sg.main([]) == 0
