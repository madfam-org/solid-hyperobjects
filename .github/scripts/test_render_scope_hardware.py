"""render_scope.py × commons-lib/hardware/: a changed shared module puts every
cartridge that inlines it in scope (run: python3 -m pytest .github/scripts).

End to end through a real git repository, because the scope is read from git
objects (`git grep`, `git show`) at base and head, never from the work tree.
"""

import importlib.util
import json
import pathlib
import subprocess as sp

import pytest

spec = importlib.util.spec_from_file_location("render_scope", pathlib.Path(__file__).with_name("render_scope.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

HW = "commons-lib/hardware"
SHA = "0" * 40
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@e", "PATH": "/usr/bin:/bin:/usr/local/bin"}


def module(requires=""):
    return f"# SPDX-License-Identifier: CERN-OHL-W-2.0\n# requires: {requires}\n\ndef f(p):\n    return p\n"


def generated(*names):
    blocks = "".join(f"# BEGIN {HW}/{n}.py@{SHA}\n{module()}# END {HW}/{n}.py@{SHA}\n" for n in names)
    return f'"""Generated."""\n{blocks}result = 1\n'


class Repo:
    def __init__(self, root):
        self.root = root
        self.git("init", "-q")

    def git(self, *args):
        return sp.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True,
                      env=ENV).stdout.strip()

    def write(self, files):
        for path, text in files.items():
            target = self.root / path
            if text is None:
                target.unlink()
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)

    def commit(self, files, msg="c"):
        self.write(files)
        self.git("add", "-A")
        self.git("commit", "-qm", msg, "--allow-empty")
        return self.git("rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    r = Repo(tmp_path)
    r.base = r.commit({
        ".github/workflows/ci.yml": "env:\n  SPEC_PIN: abc\n",
        f"{HW}/patterns.py": module(),
        f"{HW}/structure.py": module("patterns"),
        f"{HW}/controls.py": module("patterns"),
        f"{HW}/displays.py": module(),
        # Generated, current: markers name what it inlines.
        "deck/project.json": "{}",
        "deck/family.py": "# inline-parts: structure\n",
        "deck/main.py": generated("patterns", "structure"),
        "pad/project.json": "{}",
        "pad/family.py": "# inline-parts: controls\n",
        "pad/main.py": generated("patterns", "controls"),
        # A plain cartridge inlines nothing.
        "plain/project.json": "{}",
        "plain/main.py": "result = 1\n",
    }, "base")
    monkeypatch.chdir(tmp_path)
    return r


def scope(repo, files):
    return rs.hardware_scope(repo.base, repo.commit(files))


def test_no_hardware_change_adds_nothing(repo):
    assert scope(repo, {"plain/main.py": "result = 2\n"}) == []


def test_a_module_change_scopes_exactly_its_inliners(repo):
    assert scope(repo, {f"{HW}/controls.py": module("patterns") + "# moved\n"}) == ["pad"]


def test_a_required_module_reaches_every_dependant(repo):
    assert scope(repo, {f"{HW}/patterns.py": module() + "# moved\n"}) == ["deck", "pad"]


def test_a_module_nobody_inlines_scopes_nothing(repo):
    assert scope(repo, {f"{HW}/displays.py": module() + "# moved\n"}) == []


@pytest.mark.parametrize("path", [f"{HW}/README.md", f"{HW}/tests/test_components.py", f"{HW}/notes.txt"])
def test_docs_and_tests_under_hardware_scope_nothing(repo, path):
    assert scope(repo, {path: "x\n"}) == []


@pytest.mark.parametrize("path", [f"{HW}/__init__.py", f"{HW}/data/profile.csv", f"{HW}/Weird.py"])
def test_an_unknown_file_under_hardware_fails_closed(repo, path):
    """Not a module the inliner reads: every inlining cartridge renders."""
    assert scope(repo, {path: "x\n"}) == ["deck", "pad"]


def test_a_stale_main_is_still_scoped_by_its_family_declaration(repo):
    """family.py names `displays` but main.py was never regenerated (no marker)."""
    repo.base = repo.commit({"deck/family.py": "# inline-parts: structure displays\n"})
    assert scope(repo, {f"{HW}/displays.py": module() + "# moved\n"}) == ["deck"]


def test_a_requires_chain_is_followed_from_the_family(repo):
    repo.base = repo.commit({"pad/main.py": "result = 1\n"})  # markers gone, family remains
    assert scope(repo, {f"{HW}/patterns.py": module() + "# moved\n"}) == ["deck", "pad"]


@pytest.mark.parametrize("family", [
    "no directive at all\n",
    "# inline-parts:\n",
    "# inline-parts: controls\n# inline-parts: structure\n",
    "# inline-parts: Not-A-Module\n",
])
def test_an_unreadable_family_fails_closed(repo, family):
    repo.base = repo.commit({"pad/family.py": family, "pad/main.py": "result = 1\n"})
    assert scope(repo, {f"{HW}/displays.py": module() + "# moved\n"}) == ["pad"]


def test_an_unreadable_requires_line_fails_closed(repo):
    repo.base = repo.commit({"pad/main.py": "result = 1\n",
                             f"{HW}/controls.py": "# SPDX-License-Identifier: CERN-OHL-W-2.0\n"})
    assert scope(repo, {f"{HW}/displays.py": module() + "# moved\n"}) == ["pad"]


def test_the_marker_at_base_counts_when_head_drops_it(repo):
    """A PR that removes a module AND its inline copy still renders the cartridge."""
    assert scope(repo, {f"{HW}/controls.py": None, "pad/family.py": "# inline-parts: structure\n",
                        "pad/main.py": generated("patterns", "structure")}) == ["pad"]


def test_a_renamed_module_scopes_the_users_of_its_old_name(repo):
    """git would otherwise report only the new path, and `pad` inlines the old one."""
    assert scope(repo, {f"{HW}/controls.py": None, f"{HW}/buttons.py": module("patterns")}) == ["pad"]


def test_a_cartridge_deleted_at_head_is_not_returned(repo):
    assert scope(repo, {f"{HW}/controls.py": module("patterns") + "# moved\n",
                        "pad/project.json": None, "pad/family.py": None, "pad/main.py": None}) == []


def test_main_puts_unchanged_inliners_in_the_chunks(repo, capsys):
    head = repo.commit({f"{HW}/controls.py": module("patterns") + "# moved\n"})
    assert rs.main(["render_scope.py", "--chunks", "8", repo.base, head]) == 0
    assert json.loads(capsys.readouterr().out) == ["pad"]
