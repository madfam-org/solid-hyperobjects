"""Unit checks for assembly_check.py (run: python3 -m pytest .github/scripts)."""

import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("assembly_check", pathlib.Path(__file__).with_name("assembly_check.py"))
ac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ac)


def fake_checker(exit_for: dict[str, int] | None = None) -> list[str]:
    """A checker that exits with the code mapped to the document's slug (0 by default)."""
    table = repr(exit_for or {})
    code = ("import sys, pathlib; t = " + table +
            "; sys.exit(t.get(pathlib.Path(sys.argv[1]).parent.name, 0))")
    return [sys.executable, "-c", code]


def write_doc(root: pathlib.Path, slug: str) -> None:
    d = root / "assemblies" / slug
    d.mkdir(parents=True)
    (d / "assembly.json").write_text("{}\n")


def test_no_assemblies_directory_is_nothing_to_check(tmp_path, capsys):
    assert ac.discover(tmp_path) == ([], [])
    assert ac.run_checks(tmp_path, fake_checker()) == 0
    assert "nothing to check" in capsys.readouterr().out


def test_discovers_every_document_in_order(tmp_path):
    for slug in ("b-two", "a-one"):
        write_doc(tmp_path, slug)
    (tmp_path / "assemblies" / "README.md").write_text("index\n")
    docs, problems = ac.discover(tmp_path)
    assert [str(d) for d in docs] == ["assemblies/a-one/assembly.json", "assemblies/b-two/assembly.json"]
    assert problems == []


def test_all_passing_documents_exit_zero(tmp_path):
    write_doc(tmp_path, "a-one")
    write_doc(tmp_path, "b-two")
    assert ac.run_checks(tmp_path, fake_checker()) == 0


def test_one_failing_document_fails_the_lane_and_the_rest_still_run(tmp_path, capsys):
    write_doc(tmp_path, "a-one")
    write_doc(tmp_path, "b-two")
    write_doc(tmp_path, "c-three")
    assert ac.run_checks(tmp_path, fake_checker({"a-one": 1})) == 1
    out = capsys.readouterr().out
    assert "checked=3 failed=1" in out
    assert "assemblies/a-one/assembly.json (exit 1)" in out
    assert "::group::assemblies/c-three/assembly.json" in out


def test_an_unreadable_document_exit_two_fails_the_lane(tmp_path):
    write_doc(tmp_path, "a-one")
    assert ac.run_checks(tmp_path, fake_checker({"a-one": 2})) == 1


def test_a_directory_without_a_document_fails_closed(tmp_path, capsys):
    write_doc(tmp_path, "a-one")
    misnamed = tmp_path / "assemblies" / "b-two"
    misnamed.mkdir()
    (misnamed / "assemlby.json").write_text("{}\n")
    docs, problems = ac.discover(tmp_path)
    assert [str(d) for d in docs] == ["assemblies/a-one/assembly.json"]
    assert len(problems) == 1 and "assemblies/b-two/ has no assembly.json" in problems[0]
    assert ac.run_checks(tmp_path, fake_checker()) == 1
    assert "layout_problems=1" in capsys.readouterr().out


def test_a_stray_file_under_assemblies_fails_closed(tmp_path):
    (tmp_path / "assemblies").mkdir()
    (tmp_path / "assemblies" / "assembly.json").write_text("{}\n")
    docs, problems = ac.discover(tmp_path)
    assert docs == [] and len(problems) == 1
    assert ac.run_checks(tmp_path, fake_checker()) == 1


def test_main_requires_a_checker(tmp_path):
    assert ac.main(["--root", str(tmp_path)]) == 2
    assert ac.main(["--root", str(tmp_path), "--"]) == 2
    write_doc(tmp_path, "a-one")
    assert ac.main(["--root", str(tmp_path), "--", *fake_checker()]) == 0
