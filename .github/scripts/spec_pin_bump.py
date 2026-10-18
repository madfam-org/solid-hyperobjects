#!/usr/bin/env python3
"""Move SPEC_PIN (the keystone revision every CI lane installs) to a new commit.

Usage: spec_pin_bump.py [--root DIR] --to SHA [--github-output FILE]

Rewrites `SPEC_PIN:` in .github/workflows/ci.yml and every copy of the old pin in
the entry docs (the full 40-character sha, and the 8-character short form the
README quotes in backticks), then prints `old=`, `new=` and `changed=` lines (also
appended to --github-output, for a workflow step). Exit 0 whether or not anything
changed; exit 2 on a malformed sha or a ci.yml with no single SPEC_PIN.

WHY THIS EXISTS
---------------
The pin trailed the keystone by six minor versions (0.9.0 against 0.15.0, 2026-10-18
audit) because nothing ever proposed a bump: the commons kept clearing an older bar
than the one the keystone documented, and nobody saw it. The weekly workflow
(.github/workflows/spec-pin-bump.yml) runs this, opens the bump PR and dispatches a
full sweep at the new pin. The rewrite lives here, not in the workflow, so it is
unit-tested (test_spec_pin_bump.py).

The docs are rewritten together with ci.yml because they tell a contributor which
keystone to install locally ("The one command that decides your PR"); a pin bump that
left them behind would hand out the old bar.
"""

import argparse
import pathlib
import re
import sys

CI = pathlib.Path(".github/workflows/ci.yml")
# The entry docs that quote the pin. Others (docs/STATUS.md and the like) are dated
# snapshots and keep the pin they were written at.
DOCS = (
    pathlib.Path("README.md"),
    pathlib.Path("AGENTS.md"),
    pathlib.Path("CONTRIBUTING.md"),
    pathlib.Path("llms.txt"),
    pathlib.Path("llms-full.txt"),
)
SHA = re.compile(r"^[0-9a-f]{40}$")
PIN_LINE = re.compile(r"^(\s+SPEC_PIN:\s*)([0-9a-f]{40})(\s*)$", re.MULTILINE)


def current_pin(ci_text):
    """The one SPEC_PIN in ci.yml, or ValueError when there is not exactly one."""
    pins = PIN_LINE.findall(ci_text)
    if len(pins) != 1:
        raise ValueError(f"expected one `SPEC_PIN: <40-hex sha>` line in {CI}, found {len(pins)}")
    return pins[0][1]


def rewrite(text, old, new):
    """Replace the full sha everywhere, and the short form only where it is quoted."""
    text = text.replace(old, new)
    return text.replace(f"`{old[:8]}`", f"`{new[:8]}`")


def bump(root, new):
    """Rewrite ci.yml and the docs under `root`. Returns (old, [changed paths])."""
    if not SHA.match(new):
        raise ValueError(f"not a full lowercase commit sha: {new!r}")
    ci_path = root / CI
    ci_text = ci_path.read_text(encoding="utf-8")
    old = current_pin(ci_text)
    if old == new:
        return old, []
    changed = []
    for rel in (CI, *DOCS):
        path = root / rel
        if not path.is_file():
            continue
        before = path.read_text(encoding="utf-8")
        after = rewrite(before, old, new)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(str(rel))
    if str(CI) not in changed:
        raise ValueError(f"{CI} was not rewritten; refusing a docs-only bump")
    return old, changed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="the commons checkout (default: .)")
    ap.add_argument("--to", required=True, help="the keystone commit to pin")
    ap.add_argument("--github-output", help="append old=/new=/changed= here")
    args = ap.parse_args(argv)
    try:
        old, changed = bump(pathlib.Path(args.root), args.to)
    except ValueError as exc:
        print(f"::error title=SPEC_PIN bump::{exc}", file=sys.stderr)
        return 2
    lines = [f"old={old}", f"new={args.to}", f"changed={'true' if changed else 'false'}"]
    print("\n".join(lines))
    for rel in changed:
        print(f"rewrote {rel}", file=sys.stderr)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
