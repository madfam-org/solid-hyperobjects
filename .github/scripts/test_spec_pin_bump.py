"""Unit checks for spec_pin_bump.py (run: python3 -m pytest .github/scripts)."""

import importlib.util
import pathlib

import pytest

spec = importlib.util.spec_from_file_location(
    "spec_pin_bump", pathlib.Path(__file__).with_name("spec_pin_bump.py")
)
spb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spb)

OLD = "142db1802bbf9e1135ceae6c9c531c469f2d295b"
NEW = "70fe8213de20bc9a699b2bde2c32ee0b02a6d52d"
REPO = pathlib.Path(__file__).resolve().parents[2]


def _tree(tmp_path, pin=OLD):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        f"env:\n  SPEC_PIN: {pin}\n  OTHER: x\n"
    )
    (tmp_path / "README.md").write_text(
        f"pip install hyperobjects-spec@{pin}\nThe keystone pin CI installs is `{pin[:8]}`.\n"
        f"An unquoted {pin[:8]} in prose is left alone.\n"
    )
    (tmp_path / "AGENTS.md").write_text("no pin here\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "STATUS.md").write_text(f"dated: {pin}\n")
    return tmp_path


def test_bump_rewrites_ci_and_entry_docs_only(tmp_path):
    root = _tree(tmp_path)
    old, changed = spb.bump(root, NEW)
    assert old == OLD
    assert changed == [".github/workflows/ci.yml", "README.md"]
    assert f"SPEC_PIN: {NEW}" in (root / ".github/workflows/ci.yml").read_text()
    readme = (root / "README.md").read_text()
    assert f"@{NEW}" in readme and f"`{NEW[:8]}`" in readme
    assert f"unquoted {OLD[:8]} in prose" in readme
    assert OLD in (root / "docs" / "STATUS.md").read_text()  # a dated snapshot keeps its pin


def test_already_current_changes_nothing(tmp_path):
    root = _tree(tmp_path, pin=NEW)
    assert spb.bump(root, NEW) == (NEW, [])


@pytest.mark.parametrize("bad", ["70fe821", NEW.upper(), NEW + "0", "main", ""])
def test_malformed_sha_is_refused(tmp_path, bad):
    with pytest.raises(ValueError):
        spb.bump(_tree(tmp_path), bad)


def test_ci_without_exactly_one_pin_is_refused(tmp_path):
    root = _tree(tmp_path)
    ci = root / ".github/workflows/ci.yml"
    ci.write_text(ci.read_text() + f"  SPEC_PIN: {OLD}\n")
    with pytest.raises(ValueError):
        spb.bump(root, NEW)


def test_main_writes_github_output(tmp_path, capsys):
    root = _tree(tmp_path)
    out = tmp_path / "gh_output"
    assert spb.main(["--root", str(root), "--to", NEW, "--github-output", str(out)]) == 0
    assert out.read_text() == f"old={OLD}\nnew={NEW}\nchanged=true\n"
    assert spb.main(["--root", str(root), "--to", "nope"]) == 2


def test_this_repository_has_exactly_one_pin():
    """The workflow relies on it; a second SPEC_PIN line would make the bump ambiguous."""
    pin = spb.current_pin((REPO / ".github/workflows/ci.yml").read_text())
    assert spb.SHA.match(pin)
