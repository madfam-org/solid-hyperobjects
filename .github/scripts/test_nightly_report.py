"""Unit checks for nightly_report.py's VERDICT (run: python3 -m pytest .github/scripts).

The parser has had a --selftest since it was written; what it did not have was
an opinion about its own --green flag. On 2026-09-06 the first full chunked
sweep (run 34023334942) concluded success with every job green while its own
concatenated log carried 62 FAIL rows, and this script was called with --green
on that log and reported "sweep green, no open tracking issue — nothing to do."

These checks are about that: the rows outrank the flag. They are pytest rather
than more --selftest cases because a regression in the verdict has to fail the
`python3 -m pytest .github/scripts` gate every PR runs, not only the dispatch
paths that happen to invoke --selftest.
"""

import importlib.util
import pathlib

import pytest

spec = importlib.util.spec_from_file_location(
    "nightly_report", pathlib.Path(__file__).with_name("nightly_report.py"))
nr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nr)

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"

# The shape group job 101459896772 actually emitted: a failing cartridge, then
# a green one after it in the same group.
RED_LOG = """=== nightly group g0 : fixture-alpha fixture-beta ===
  ok fixture-alpha (./fixture-alpha, 5 render(s) verified)
y4d-spec check: cartridges=1 failures=0
  FAIL fixture-beta: parity (nut, nut): FAIL — Volumes differ by 7.146905mm^3 (4.3991%)
y4d-spec check: cartridges=1 failures=1 parity=2/5 ok, warn=1, failures=2
  ok fixture-gamma (./fixture-gamma, 6 render(s) verified)
y4d-spec check: cartridges=1 failures=0
"""

CLEAN_LOG = """=== nightly group g0 : fixture-alpha fixture-beta ===
  ok fixture-alpha (./fixture-alpha, 5 render(s) verified)
  ok fixture-beta (./fixture-beta, 5 render(s) verified)
y4d-spec check: cartridges=2 failures=0
"""


@pytest.fixture(autouse=True)
def _no_api(monkeypatch):
    """No token, so main() returns its verdict without touching the network."""
    for key in ("GITHUB_REPOSITORY", "GH_TOKEN", "GH_TOKEN_FALLBACK",
                "GITHUB_STEP_SUMMARY", "GITHUB_RUN_ID"):
        monkeypatch.delenv(key, raising=False)


def _write(tmp_path, log, scope_slugs):
    log_file = tmp_path / "sweep-report.txt"
    log_file.write_text(log, encoding="utf-8")
    scope_file = tmp_path / "nightly-scope.txt"
    scope_file.write_text("\n".join(scope_slugs) + "\n", encoding="utf-8")
    return str(log_file), str(scope_file)


def test_green_is_refused_when_the_log_has_fail_rows(tmp_path, capsys):
    """THE regression: --green on a red log must exit 1, not close the issue."""
    log, scope = _write(tmp_path, RED_LOG,
                        ["fixture-alpha", "fixture-beta", "fixture-gamma"])
    rc = nr.main(["--green", "--log", log, "--scope", scope,
                  "--require-complete"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "--green refused" in out
    assert "fixture-beta" in out
    # It must NOT have taken the green path's "nothing to do" branch.
    assert "nothing to do" not in out


def test_green_is_refused_even_without_require_complete(tmp_path):
    """The refusal is independent of the completeness flag and of a --scope."""
    log, _ = _write(tmp_path, RED_LOG, ["fixture-alpha"])
    assert nr.main(["--green", "--log", log]) == 1


def test_green_still_passes_on_a_clean_complete_log(tmp_path, capsys):
    """The refusal must not turn a genuinely green night red.

    An alerting path that fails a passing sweep is worse than the silence it
    replaces — that rule survives this change; only the definition of "passing"
    got stricter.
    """
    log, scope = _write(tmp_path, CLEAN_LOG, ["fixture-alpha", "fixture-beta"])
    rc = nr.main(["--green", "--log", log, "--scope", scope,
                  "--require-complete"])
    assert rc == 0
    assert "--green refused" not in capsys.readouterr().out


def test_completeness_still_fails_an_incomplete_green(tmp_path):
    """The pre-existing verdict (run 33998128926's hole) is untouched."""
    log, scope = _write(tmp_path, CLEAN_LOG,
                        ["fixture-alpha", "fixture-beta", "fixture-never"])
    assert nr.main(["--green", "--log", log, "--scope", scope,
                    "--require-complete"]) == 1


def test_a_red_log_with_a_hole_reports_both(tmp_path, capsys):
    log, scope = _write(tmp_path, RED_LOG,
                        ["fixture-alpha", "fixture-beta", "fixture-gamma",
                         "fixture-never"])
    assert nr.main(["--green", "--log", log, "--scope", scope,
                    "--require-complete"]) == 1
    out = capsys.readouterr().out
    assert "--green refused" in out
    assert "incomplete nightly sweep" in out


def test_the_false_green_fixture_is_complete_and_red():
    """The committed fixture must reproduce run 34023334942, not something easier.

    Complete coverage is the point: if the fixture were missing a cartridge the
    completeness check would catch it and the FAIL-row verdict would never be
    exercised.
    """
    log = FIXTURES / "nightly-false-green-sample.txt"
    scope = FIXTURES / "nightly-false-green-scope.txt"
    assert log.is_file() and scope.is_file()
    text = log.read_text(encoding="utf-8")
    assert nr.missing_cartridges(nr.read_scope(str(scope)), text) == []
    rows = nr.parse_failures(text)
    assert len(rows) == 2
    assert {r["cartridge"] for r in rows} == {"fixture-gamma"}
    # Two groups, and a green cartridge after the failing one.
    assert [g for g, _ in nr.parse_groups(text)] == ["g0", "g1"]
    assert "fixture-delta" in nr.parse_coverage(text)


def test_selftest_passes():
    """`nightly_report.py --selftest` is itself part of the gate."""
    assert nr.selftest(str(FIXTURES / "nightly-fail-sample.txt")) == 0
