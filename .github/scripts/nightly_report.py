#!/usr/bin/env python3
"""A red nightly sweep opens — and keeps — ONE tracking issue.

The 2026-08-26 availability audit found that zero alerts had ever reached a
human. The nightly sweeps in this estate render everything and then fail into
a run log nobody opens. This script closes that gap in the cheapest way that
actually works: it turns a red sweep into a GitHub issue, and it keeps that
issue current rather than opening a new one every night.

The shape, deliberately:

  ONE issue, not one per night.  A sweep that stays red for a week is one
  problem, and seven issues is how a tracker becomes noise nobody reads. The
  open issue labelled ``nightly-sweep`` IS the alert; a later red run rewrites
  its body (latest table on top, a short dated history below) and comments the
  delta — what broke since last night, what got fixed. The delta comment is
  the part a human actually reads.

  A GREEN sweep closes it.  An alert that does not clear itself trains people
  to ignore it. When the sweep passes and an issue is open, this closes it with
  a comment naming the run.

  Parsing is per-render, not per-run.  ``cartridge | mode/part | preset |
  engine | reason`` — the table says which renders failed, so triage starts
  from the table instead of from a 400 MB log.

  stdlib only, no gh CLI.  It runs on the self-hosted pool where the CLI is not
  guaranteed, and vendoring a dependency into a nightly alerting path is how
  the alerting path itself breaks.

AUTH
----
``GH_TOKEN`` first (normally the job's ``GITHUB_TOKEN`` with
``issues: write``). If the org's default workflow permission blocks issue
writes the API answers 403, and that is NOT a reason for the alert to vanish
silently: the script retries once with ``GH_TOKEN_FALLBACK`` (the repo secret
``MADFAM_BOT_PAT``) and says on stdout which path it used. A YAML-level
``${{ secrets.X || github.token }}`` cannot express "try, and on 403 try the
other one" — the retry has to live here.

FAILING TO REPORT NEVER FAILS THE SWEEP
---------------------------------------
The sweep's own exit code is the verdict. This script exits 0 even when it
could not reach the API, after printing a ``::error::`` annotation: an alerting
path that turns a green sweep red is worse than the silence it replaces. The
one exception is ``--selftest``, which is a unit test and reports honestly.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

LABEL = "nightly-sweep"
API = "https://api.github.com"

# A per-render failure line, as the sweeps emit it:
#
#   "  FAIL <slug>: render (<mode>, <part>[, preset '<p>'][, <engine>]): FAIL — <reason>"
#
# and the plainer shape the pattern sweeps use:
#
#   "  FAIL <slug>: <reason>"
#
# Both are matched by the same expression; everything after the slug is picked
# apart below, so a sweep that grows a new parenthetical does not stop being
# reported — it just lands in the reason column.
FAIL_RE = re.compile(r"^\s*FAIL\s+(?P<slug>[^\s:]+):\s*(?P<rest>.*)$")

# A cartridge the sweep actually reached, as `-v` prints it:
#
#   "  ok <slug> (./<slug>, N render(s) verified)"   — cleared the bar
#   "  FAIL <slug>: <rest>"                           — reached, and failed
#   "  note <slug>: <rest>"                           — reached, with a note
#
# Those three are the ONLY per-cartridge shapes y4d_spec/cli.py emits (`  ok
# {name} ({d}{suffix})`, `  FAIL {name}: {prob}`, `  note {name}: {note}`), so
# matching them is matching "the sweep reached this cartridge". Deliberately
# anchored and deliberately narrow: a pattern that also matched, say, a stray
# "ok" inside a reason string would inflate coverage and re-open the very hole
# this check exists to close. Fail closed — an unrecognised line is NOT
# coverage.
#
# The union of both is the COVERAGE of a sweep. Since 2026-09-06 the nightly
# fans out over a matrix and the report concatenates every group's log, so the
# coverage of the whole night is the union across groups — and comparing it
# against the scope is the only thing that can tell an incomplete sweep from a
# green one. Run 33998128926 rendered 454 of 500 and reported no error at all
# for the 46 it never reached.
OK_RE = re.compile(r"^\s{1,4}ok\s+(?P<slug>[^\s:(]+)\s+\(")
NOTE_RE = re.compile(r"^\s{1,4}note\s+(?P<slug>[^\s:]+):")

# The matrix runner writes one of these at the top of each group's log so a
# concatenated report can say which group a row came from, and so a group whose
# log is MISSING entirely (lost runner, cancelled job) is still visible.
GROUP_RE = re.compile(r"^===\s*nightly group\s+(?P<group>\S+)\s*:\s*(?P<slugs>.*?)\s*===\s*$")

# "render (<mode>, <part>[, preset '<p>'][, <engine>]): FAIL — <reason>"
RENDER_RE = re.compile(
    r"^render\s*\((?P<inner>[^)]*)\)\s*:\s*(?:FAIL\s*[—-]\s*)?(?P<reason>.*)$")

PRESET_RE = re.compile(r"^preset\s+'(?P<preset>[^']*)'$")
KNOWN_ENGINES = {"cadquery", "openscad", "build123d", "fc"}

# "y4d-spec check: cartridges=N failures=M ..." / "patterns: cartridges=N ..."
SUMMARY_RE = re.compile(
    r"^(?P<prefix>[\w .-]*?):?\s*cartridges=(?P<cartridges>\d+)\b.*?"
    r"failures=(?P<failures>\d+)", re.IGNORECASE)

HISTORY_MARKER = "<!-- nightly-sweep:history -->"
MAX_TABLE_ROWS = 60
MAX_HISTORY = 14


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------

def parse_failures(text: str) -> list:
    """Every ``FAIL`` line in the sweep log, as table rows."""
    rows = []
    for line in text.splitlines():
        m = FAIL_RE.match(line)
        if not m:
            continue
        slug, rest = m.group("slug"), m.group("rest").strip()
        mode_part, preset, engine = "", "", ""
        rm = RENDER_RE.match(rest)
        if rm:
            reason = rm.group("reason").strip()
            fields = [f.strip() for f in rm.group("inner").split(",") if f.strip()]
            leftover = []
            for f in fields:
                pm = PRESET_RE.match(f)
                if pm:
                    preset = pm.group("preset")
                elif f.lower() in KNOWN_ENGINES:
                    engine = f
                else:
                    leftover.append(f)
            mode_part = "/".join(leftover)
        else:
            reason = rest
        rows.append({"cartridge": slug, "mode_part": mode_part,
                     "preset": preset, "engine": engine, "reason": reason})
    return rows


def parse_summary(text: str) -> dict:
    """The sweep's own counts, when it printed them."""
    out = {}
    for line in text.splitlines():
        m = SUMMARY_RE.search(line.strip())
        if m:
            out = {"cartridges": int(m.group("cartridges")),
                   "failures": int(m.group("failures")),
                   "line": line.strip()}
    return out


def parse_coverage(text: str) -> set:
    """Every cartridge the sweep actually reached, across all group logs."""
    seen = set()
    for line in text.splitlines():
        m = OK_RE.match(line)
        if m:
            seen.add(m.group("slug"))
            continue
        m = FAIL_RE.match(line)
        if m:
            seen.add(m.group("slug"))
            continue
        m = NOTE_RE.match(line)
        if m:
            seen.add(m.group("slug"))
    return seen


def parse_groups(text: str) -> list:
    """The group headers a concatenated multi-group report carries."""
    out = []
    for line in text.splitlines():
        m = GROUP_RE.match(line)
        if m:
            out.append((m.group("group"), m.group("slugs").split()))
    return out


def read_scope(path: str) -> list:
    """The scope the matrix was SUPPOSED to cover, one slug per line."""
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


def missing_cartridges(scope, text: str) -> list:
    """Scope minus coverage: the cartridges this night never rendered.

    This is the completeness check. A sweep that ran out of wall clock exits
    with rows for the cartridges it reached and NOTHING for the rest; without
    this comparison such a night looks exactly like a green one.
    """
    if not scope:
        return []
    return sorted(set(scope) - parse_coverage(text))


def completeness_rows(missing) -> list:
    """Table rows for cartridges that were never rendered at all."""
    return [{"cartridge": slug, "mode_part": "", "preset": "", "engine": "",
             "reason": "NEVER RENDERED — the sweep never reached this "
                       "cartridge (no ok and no FAIL row in any group log)"}
            for slug in missing]


def row_key(row: dict) -> str:
    """Identity of a failing render, for the new/fixed delta."""
    return " | ".join((row["cartridge"], row["mode_part"],
                       row["preset"], row["engine"]))


def _cell(value: str) -> str:
    value = (value or "—").replace("|", "\\|").replace("\n", " ").strip()
    return value or "—"


def render_table(rows: list) -> str:
    head = ("| cartridge | mode/part | preset | engine | reason |\n"
            "| --- | --- | --- | --- | --- |\n")
    body = "".join(
        f"| `{_cell(r['cartridge'])}` | {_cell(r['mode_part'])} | "
        f"{_cell(r['preset'])} | {_cell(r['engine'])} | {_cell(r['reason'])} |\n"
        for r in rows[:MAX_TABLE_ROWS])
    if len(rows) > MAX_TABLE_ROWS:
        body += (f"\n_{len(rows) - MAX_TABLE_ROWS} further failing render(s) "
                 f"not listed — see the run log._\n")
    return head + body


# ---------------------------------------------------------------------------
# GitHub API — two tokens, one retry
# ---------------------------------------------------------------------------

class Api:
    """Minimal GitHub REST client that fails over from GH_TOKEN on 403."""

    def __init__(self, repo: str, token: str, fallback: str = ""):
        self.repo = repo
        self.tokens = [t for t in (token, fallback) if t]
        self.used = None
        self.path_name = None

    def _once(self, method: str, url: str, token: str, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "madfam-nightly-report")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8") or "null"
        return json.loads(body)

    def call(self, method: str, path: str, payload=None):
        url = path if path.startswith("http") else f"{API}{path}"
        last = None
        for index, token in enumerate(self.tokens):
            # Once a token has worked, stay on it: a mid-run switch would make
            # the issue's author flip between runs for no reason.
            if self.used is not None and token != self.used:
                continue
            try:
                result = self._once(method, url, token, payload)
            except urllib.error.HTTPError as exc:
                last = exc
                if exc.code in (401, 403) and index + 1 < len(self.tokens):
                    print(f"::warning::nightly_report: {exc.code} on {method} "
                          f"{path} with the primary token — retrying with "
                          f"GH_TOKEN_FALLBACK (MADFAM_BOT_PAT).")
                    continue
                raise
            else:
                if self.used is None:
                    self.used = token
                    self.path_name = ("GITHUB_TOKEN (GH_TOKEN)" if index == 0
                                      else "MADFAM_BOT_PAT (GH_TOKEN_FALLBACK)")
                return result
        raise last

    # -- the three calls this script makes -------------------------------
    def ensure_label(self):
        try:
            self.call("GET", f"/repos/{self.repo}/labels/{LABEL}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            try:
                self.call("POST", f"/repos/{self.repo}/labels", {
                    "name": LABEL, "color": "B60205",
                    "description": "A nightly sweep is red; one tracking "
                                   "issue per repo, kept current."})
            except urllib.error.HTTPError as exc2:
                # A race with a concurrent run, or a token without label
                # scope: neither is a reason to drop the alert.
                print(f"::warning::nightly_report: could not create the "
                      f"{LABEL} label ({exc2.code}); continuing unlabelled.")

    def open_issue(self):
        issues = self.call(
            "GET",
            f"/repos/{self.repo}/issues?state=open&labels={LABEL}&per_page=1")
        return issues[0] if issues else None


# ---------------------------------------------------------------------------
# body assembly
# ---------------------------------------------------------------------------

def build_body(rows, summary, date, run_url, workflow, previous_body="",
               coverage=None):
    counts = (f"`{summary['line']}`" if summary
              else f"{len(rows)} failing render(s) parsed from the log")
    parts = [
        f"The **{workflow}** nightly sweep is red.",
        "",
        f"- last red run: **{date}** — [run log]({run_url})",
        f"- failing renders in that run: **{len(rows)}**",
        f"- sweep summary: {counts}",
    ]
    if coverage:
        parts.append(
            f"- coverage: **{coverage['covered']}/{coverage['scope']}** "
            f"cartridge(s) rendered"
            + (f" — **{coverage['missing']} NEVER RENDERED** (the sweep did "
               f"not reach them; an incomplete night is not a green night)"
               if coverage.get("missing") else " — complete"))
    parts += [
        "",
        "This is the single tracking issue for the nightly sweep: a later red "
        "run rewrites the table below and comments the delta; the first green "
        "sweep closes it. Do not open a second one.",
        "",
        f"## Failing renders — {date}",
        "",
        render_table(rows) if rows else
        "_The sweep failed but printed no parseable `FAIL` line — read the run "
        "log; the failure is in the harness, not in a cartridge._\n",
        "",
        HISTORY_MARKER,
        "",
        "## History",
        "",
    ]
    entry = f"- {date} — {len(rows)} failing render(s) ([run]({run_url}))"
    history = [entry]
    if HISTORY_MARKER in previous_body:
        tail = previous_body.split(HISTORY_MARKER, 1)[1]
        for line in tail.splitlines():
            line = line.strip()
            if line.startswith("- ") and line != entry:
                history.append(line)
    parts.extend(history[:MAX_HISTORY])
    parts.append("")
    return "\n".join(parts)


def build_delta(rows, previous_body, date, run_url):
    """What changed since the table already on the issue."""
    now = {row_key(r) for r in rows}
    before = set()
    if previous_body:
        # Read back the rows of the previous table: first column, backticked.
        section = previous_body.split(HISTORY_MARKER, 1)[0]
        for line in section.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4:
                before.add(" | ".join(
                    (cells[0].strip("`"),
                     "" if cells[1] == "—" else cells[1],
                     "" if cells[2] == "—" else cells[2],
                     "" if cells[3] == "—" else cells[3])))
    new = sorted(now - before)
    fixed = sorted(before - now)
    lines = [f"Nightly sweep still red on **{date}** — [run log]({run_url}).", ""]
    lines.append(f"- failing renders: **{len(rows)}** "
                 f"(was {len(before)} on the previous red run)")
    if new:
        lines += ["", f"**New since the last red run ({len(new)}):**", ""]
        lines += [f"- `{k}`" for k in new[:30]]
        if len(new) > 30:
            lines.append(f"- …and {len(new) - 30} more")
    if fixed:
        lines += ["", f"**Fixed since the last red run ({len(fixed)}):**", ""]
        lines += [f"- `{k}`" for k in fixed[:30]]
        if len(fixed) > 30:
            lines.append(f"- …and {len(fixed) - 30} more")
    if not new and not fixed:
        lines += ["", "No change: the same renders failed as on the previous "
                      "red run."]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# selftest — the parser and the body assembly, no network
# ---------------------------------------------------------------------------

def selftest(fixture: str) -> int:
    """The parser's unit checks. Always run against the canonical fixtures.

    `fixture` names the FIXTURES DIRECTORY to use, not the log to assert on:
    the checks below are hardcoded to the contents of
    `nightly-fail-sample.txt` and `nightly-multigroup-sample.txt`, so pointing
    --selftest at some other log used to fail with four bogus "expected 3 FAIL
    rows" complaints (dispatch 34020739707). A unit test that reports a
    problem in its own argument rather than in the code is noise, so the
    argument is now only a way to locate the fixture directory.
    """
    fixtures = pathlib.Path(fixture)
    fixtures = fixtures.parent if fixtures.is_file() else fixtures
    canonical = fixtures / "nightly-fail-sample.txt"
    if not canonical.is_file():
        print(f"nightly_report selftest: checks_failed=1\n"
              f"  FAIL canonical fixture not found at {canonical}")
        return 1
    fixture = str(canonical)
    text = canonical.read_text(encoding="utf-8")
    rows = parse_failures(text)
    summary = parse_summary(text)
    problems = []

    def check(cond, what):
        if not cond:
            problems.append(what)

    check(len(rows) == 3, f"expected 3 FAIL rows, parsed {len(rows)}")
    if len(rows) == 3:
        a, b, c = rows
        check(a["cartridge"] == "fixture-alpha", f"row1 slug {a['cartridge']!r}")
        check(a["mode_part"] == "print/body", f"row1 mode/part {a['mode_part']!r}")
        check(a["preset"] == "", f"row1 preset {a['preset']!r}")
        check(a["engine"] == "cadquery", f"row1 engine {a['engine']!r}")
        check("not watertight" in a["reason"], f"row1 reason {a['reason']!r}")
        check(b["preset"] == "tall", f"row2 preset {b['preset']!r}")
        check(b["engine"] == "openscad", f"row2 engine {b['engine']!r}")
        check(c["mode_part"] == "", f"row3 mode/part {c['mode_part']!r}")
        check(c["reason"].startswith("script assigned no"),
              f"row3 reason {c['reason']!r}")
    check(summary.get("cartridges") == 500,
          f"summary cartridges {summary.get('cartridges')}")
    check(summary.get("failures") == 3, f"summary failures {summary.get('failures')}")

    body = build_body(rows, summary, "2026-09-06", "https://example/run", "CI")
    check("| cartridge | mode/part | preset | engine | reason |" in body,
          "table header missing from body")
    check(HISTORY_MARKER in body, "history marker missing from body")
    check("`fixture-alpha`" in body, "row1 missing from the rendered table")

    # A second red run: the delta must see one new and one fixed render.
    later = parse_failures(
        "  FAIL fixture-alpha: render (print, body, cadquery): FAIL — still bad\n"
        "  FAIL fixture-delta: render (print, body, cadquery): FAIL — new one\n")
    delta = build_delta(later, body, "2026-09-07", "https://example/run2")
    check("fixture-delta" in delta.split("**New since")[-1],
          "delta did not report the new failure")
    check("**Fixed since the last red run (2)" in delta,
          f"delta fixed-count wrong:\n{delta}")

    # Round-trip: a body built from the later run reads back its own rows.
    body2 = build_body(later, None, "2026-09-07", "https://example/run2", "CI", body)
    check(body2.count("- 2026-09-0") == 2, "history did not accumulate two dates")
    delta2 = build_delta(later, body2, "2026-09-08", "https://example/run3")
    check("No change" in delta2, f"identical runs should read as no change:\n{delta2}")

    # --- the chunked path: a concatenated multi-group report ---------------
    # The parser is line-based, so a concatenation of group logs should Just
    # Work — "should" is not evidence, so this asserts it against a fixture
    # with two group headers, two group summaries, ok rows and FAIL rows.
    multi = pathlib.Path(fixture).with_name("nightly-multigroup-sample.txt")
    scope_file = pathlib.Path(fixture).with_name("nightly-multigroup-scope.txt")
    if multi.is_file() and scope_file.is_file():
        mtext = multi.read_text(encoding="utf-8")
        mrows = parse_failures(mtext)
        check(len(mrows) == 2, f"multigroup: expected 2 FAIL rows, got {len(mrows)}")
        groups = parse_groups(mtext)
        check([g for g, _ in groups] == ["g0", "g1"],
              f"multigroup: group headers parsed as {[g for g, _ in groups]!r}")
        cov = parse_coverage(mtext)
        check(cov == {"fixture-alpha", "fixture-beta", "fixture-gamma",
                      "fixture-delta"},
              f"multigroup: coverage {sorted(cov)!r}")
        scope = read_scope(str(scope_file))
        check(len(scope) == 5, f"multigroup: scope has {len(scope)} slugs")
        miss = missing_cartridges(scope, mtext)
        check(miss == ["fixture-never"],
              f"completeness: expected ['fixture-never'], got {miss!r}")
        crows = completeness_rows(miss)
        check(len(crows) == 1 and "NEVER RENDERED" in crows[0]["reason"],
              "completeness: NEVER RENDERED row not built")
        # Fail CLOSED: lines that merely mention a slug must not count as
        # coverage, or the check re-opens the hole it exists to close. Only
        # y4d_spec's own three per-cartridge shapes count.
        decoys = (
            "       render (print, body, cadquery): ok",   # a -v render detail
            "  FAIL other: render (x, y): FAIL — ok fixture-never (./x)",
            "ok fixture-never (./fixture-never)",          # no leading indent
            "                ok fixture-never (./x)",      # over-indented
            "  okay fixture-never (./fixture-never)",
        )
        for d in decoys:
            check(parse_coverage(d) - {"other"} == set(),
                  f"coverage must not be claimed by: {d!r} -> {parse_coverage(d)}")
        # …and the three real shapes DO count, including a `note` row.
        check(parse_coverage("  ok fixture-x (./fixture-x, 6 render(s) verified)")
              == {"fixture-x"}, "an ok row must count as coverage")
        check(parse_coverage("  note fixture-y: declared 2 bodies") == {"fixture-y"},
              "a note row must count as coverage")

        # A complete log must report NO missing cartridge — the check has to be
        # able to say "fine", or it is just noise that gets muted.
        check(missing_cartridges(scope[:4], mtext) == [],
              "completeness: a complete sweep must report nothing missing")
        # …and the coverage line has to reach the issue body.
        cbody = build_body(crows + mrows, parse_summary(mtext), "2026-09-06",
                           "https://example/run", "CI",
                           coverage={"scope": 5, "covered": 4, "missing": 1})
        check("NEVER RENDERED" in cbody,
              "completeness: the issue body does not say a cartridge was never rendered")
        check("**4/5**" in cbody, f"completeness: coverage line missing from body")
    else:
        problems.append(f"multigroup fixture missing next to {fixture}")

    print(f"nightly_report selftest: checks_failed={len(problems)}")
    for p in problems:
        print(f"  FAIL {p}")
    return 1 if problems else 0


# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log", help="the sweep's tee'd output")
    ap.add_argument("--workflow", default="nightly sweep",
                    help="name used in the issue title and body")
    ap.add_argument("--green", action="store_true",
                    help="the sweep passed: close any open tracking issue")
    ap.add_argument("--selftest", metavar="FIXTURE",
                    help="run the parser's unit checks against a fixture log")
    ap.add_argument("--scope", metavar="FILE",
                    help="the slug list the matrix was supposed to cover "
                         "(nightly_scope.py --slug-list). Enables the "
                         "completeness check: any scoped cartridge with no ok "
                         "and no FAIL row in the concatenated log is reported "
                         "as NEVER RENDERED.")
    ap.add_argument("--require-complete", action="store_true",
                    help="exit 1 when the completeness check finds a scoped "
                         "cartridge that was never rendered. This is the only "
                         "flag that lets this script fail a job: an incomplete "
                         "sweep must not be able to look green.")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(args.selftest)

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GH_TOKEN", "")
    fallback = os.environ.get("GH_TOKEN_FALLBACK", "")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_url = f"{server}/{repo}/actions/runs/{run_id}" if run_id else server
    date = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")

    # --- the completeness check ------------------------------------------
    # Computed BEFORE any network call, and its verdict is returned even when
    # the API is unreachable: "this night did not cover the commons" is a fact
    # about the sweep, not about GitHub. It is also the ONE thing here that may
    # fail a job (with --require-complete) — everything else about this script
    # exits 0 so an alerting path can never turn a green sweep red.
    text = ""
    if args.log and os.path.isfile(args.log):
        text = open(args.log, encoding="utf-8", errors="replace").read()
    scope = read_scope(args.scope)
    missing = missing_cartridges(scope, text) if scope else []
    coverage = None
    if scope:
        coverage = {"scope": len(scope), "covered": len(scope) - len(missing),
                    "missing": len(missing)}
        groups = parse_groups(text)
        print(f"nightly_report: completeness — scope={len(scope)} "
              f"covered={coverage['covered']} missing={len(missing)} "
              f"group_logs={len(groups)}")
        if missing:
            print(f"::error title=incomplete nightly sweep::"
                  f"{len(missing)} of {len(scope)} cartridge(s) were never "
                  f"rendered: {' '.join(missing[:20])}"
                  + (" …" if len(missing) > 20 else ""))
            # A sweep that skipped cartridges is not green, whatever the group
            # jobs said. Force the red path so the tracking issue opens.
            args.green = False
            rows_extra = completeness_rows(missing)
        else:
            rows_extra = []
        summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_file:
            with open(summary_file, "a", encoding="utf-8") as fh:
                fh.write(f"\n### Completeness\n\n"
                         f"`scope={len(scope)} covered={coverage['covered']} "
                         f"never_rendered={len(missing)}`\n")
                if missing:
                    fh.write("\nNever rendered: "
                             + ", ".join(f"`{m}`" for m in missing[:60])
                             + ("\n" if len(missing) <= 60 else
                                f" …and {len(missing) - 60} more\n"))
    else:
        rows_extra = []

    def _verdict():
        return 1 if (missing and args.require_complete) else 0

    if not repo or not token:
        print("::error::nightly_report: GITHUB_REPOSITORY or GH_TOKEN is unset "
              "— the sweep result was NOT reported to an issue.")
        return _verdict()

    api = Api(repo, token, fallback)
    try:
        existing = api.open_issue()

        if args.green:
            if existing is None:
                print("nightly_report: sweep green, no open tracking issue — "
                      "nothing to do.")
            else:
                number = existing["number"]
                api.call("POST", f"/repos/{repo}/issues/{number}/comments", {
                    "body": f"Nightly sweep is **green** on {date} — "
                            f"[run log]({run_url}). Closing; a later red sweep "
                            f"opens a fresh tracking issue."})
                api.call("PATCH", f"/repos/{repo}/issues/{number}",
                         {"state": "closed", "state_reason": "completed"})
                print(f"nightly_report: sweep green — closed #{number}.")
            print(f"nightly_report: auth path = {api.path_name}")
            return _verdict()

        if not args.log or not os.path.isfile(args.log):
            print(f"::error::nightly_report: log {args.log!r} not found — the "
                  f"red sweep was NOT reported to an issue.")
            return _verdict()

        # NEVER RENDERED rows go FIRST: a night with a coverage hole is a
        # worse problem than any single bad geometry, and the table is what a
        # human reads before the log.
        rows = rows_extra + parse_failures(text)
        summary = parse_summary(text)
        api.ensure_label()

        if existing is None:
            issue = api.call("POST", f"/repos/{repo}/issues", {
                "title": f"Nightly render sweep is red ({date})",
                "body": build_body(rows, summary, date, run_url, args.workflow,
                                   coverage=coverage),
                "labels": [LABEL]})
            print(f"nightly_report: opened #{issue['number']} — "
                  f"{issue['html_url']} ({len(rows)} failing render(s))")
        else:
            number = existing["number"]
            previous = existing.get("body") or ""
            api.call("PATCH", f"/repos/{repo}/issues/{number}", {
                "body": build_body(rows, summary, date, run_url,
                                   args.workflow, previous,
                                   coverage=coverage)})
            api.call("POST", f"/repos/{repo}/issues/{number}/comments",
                     {"body": build_delta(rows, previous, date, run_url)})
            print(f"nightly_report: updated #{number} — "
                  f"{existing['html_url']} ({len(rows)} failing render(s))")

        print(f"nightly_report: auth path = {api.path_name}")
        summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_file:
            with open(summary_file, "a", encoding="utf-8") as fh:
                fh.write(f"\n### Nightly sweep reported to the tracking issue\n\n"
                         f"{len(rows)} failing render(s); auth path "
                         f"{api.path_name}.\n")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        print(f"::error::nightly_report: GitHub API {exc.code} on the tracking "
              f"issue — the sweep result was NOT reported. {detail}")
    except Exception as exc:  # noqa: BLE001 - alerting must not fail the sweep
        print(f"::error::nightly_report: {type(exc).__name__}: {exc} — the "
              f"sweep result was NOT reported.")
    return _verdict()


if __name__ == "__main__":
    sys.exit(main())
