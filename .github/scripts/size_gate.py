#!/usr/bin/env python3
"""File-size gate: over 600 lines warns, over 800 fails (the MADFAM size policy).

Usage: size_gate.py [--update-baseline] [--root DIR] [--baseline PATH]

Measures every TRACKED `.py` and `.scad` file (`git ls-files`; submodules under
libs/ are gitlinks, so their files are never listed) except fixtures and the
GENERATED main.py of a family cartridge: a `<slug>/main.py` whose `<slug>/family.py`
is tracked and which carries a `# BEGIN commons-lib/hardware/<m>.py@<sha>` marker.
That file is inlined output (tools/inline_parts.py, ruling R2) and its length is the
sum of authored files this gate already measures — family.py and every module.

Files that were already over 800 lines when the gate landed are grandfathered in a
committed baseline (`.github/size-limit-baseline.json`), the crea-map pattern:

  * a file over 800 that the baseline does not list FAILS (a new crossing);
  * a baselined file that GREW past its recorded size FAILS;
  * a baselined file now at or under 800, or no longer tracked, FAILS until
    `--update-baseline` drops it — so the baseline only ever shrinks on purpose
    and a refactored file cannot silently climb back;
  * anything over 600 warns.

`--update-baseline` only shrinks: it lowers recorded sizes to the current ones and
drops entries that no longer need an exception. It refuses to add a file or raise
a size — split the file instead. (With no baseline file at all, it seeds one.)

Pure stdlib.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

WARN_AT = 600
FAIL_AT = 800
EXTENSIONS = (".py", ".scad")
EXCLUDE = (re.compile(r"(^|/)fixtures/"),)
MARKER = re.compile(r"^# BEGIN commons-lib/hardware/[a-z][a-z0-9_]*\.py@[0-9a-f]{40}$", re.M)
ROOT = Path(__file__).resolve().parents[2]
BASELINE = ".github/size-limit-baseline.json"
COMMENT = (
    "Grandfather baseline for .github/scripts/size_gate.py. Files listed here already "
    "exceeded 800 lines when the gate landed; each is tolerated AT OR BELOW its recorded "
    "size and FAILS if it grows. Refactor one to <= 800 and run `python3 "
    ".github/scripts/size_gate.py --update-baseline` to drop it: the baseline only shrinks. "
    "Do not hand-edit."
)


def tracked(root):
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True,
                         capture_output=True, text=True).stdout
    return sorted(p for p in out.split("\0") if p)


def count_lines(path):
    """`wc -l` semantics: the number of newline bytes."""
    return path.read_bytes().count(b"\n")


def is_generated(root, rel, files):
    """A family's inlined main.py: sibling family.py tracked and a marker present."""
    parts = rel.split("/")
    if len(parts) != 2 or parts[1] != "main.py" or f"{parts[0]}/family.py" not in files:
        return False
    return bool(MARKER.search((root / rel).read_text(encoding="utf-8", errors="replace")))


def measure(root):
    """({path: lines} for every measured file, [exempted generated paths])."""
    files = tracked(root)
    listed = set(files)
    sizes, exempt = {}, []
    for rel in files:
        if not rel.endswith(EXTENSIONS) or any(rx.search(rel) for rx in EXCLUDE):
            continue
        if not (root / rel).is_file():
            continue  # deleted in the work tree but not yet from the index
        if is_generated(root, rel, listed):
            exempt.append(rel)
            continue
        sizes[rel] = count_lines(root / rel)
    return sizes, exempt


def load_baseline(path):
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    files = data.get("files", {})
    if not isinstance(files, dict) or not all(isinstance(v, int) for v in files.values()):
        raise ValueError(f"{path}: `files` must map paths to line counts")
    return files


def judge(sizes, baseline):
    """(failures, warnings, grandfathered) — lists of (path, message)."""
    failures, warnings, grandfathered = [], [], []
    for rel, size in sorted(sizes.items()):
        cap = baseline.get(rel)
        if size > FAIL_AT:
            if cap is None:
                failures.append((rel, f"{size} lines (over {FAIL_AT}): a new file over the hard "
                                      "limit — split it"))
            elif size > cap:
                failures.append((rel, f"grew from {cap} to {size} lines: baselined at {cap}, it "
                                      "must not grow — refactor before adding more"))
            else:
                grandfathered.append((rel, f"{size} lines (baselined at {cap}, not growing)"))
        elif cap is not None:
            failures.append((rel, f"now {size} lines (<= {FAIL_AT}): it no longer needs its "
                                  "baseline exception — run --update-baseline to drop it"))
        elif size > WARN_AT:
            warnings.append((rel, f"{size} lines (over {WARN_AT}, approaching the {FAIL_AT} limit)"))
    for rel in sorted(set(baseline) - set(sizes)):
        failures.append((rel, "baselined but no longer measured — run --update-baseline to drop it"))
    return failures, warnings, grandfathered


def update(sizes, baseline):
    """The shrunk baseline, or (None, refusals) when it would have to grow."""
    if baseline is None:  # seeding
        return {rel: n for rel, n in sorted(sizes.items()) if n > FAIL_AT}, []
    refusals = [f"{rel}: {n} lines is not in the baseline — split it; the baseline never grows"
                for rel, n in sorted(sizes.items()) if n > FAIL_AT and rel not in baseline]
    refusals += [f"{rel}: {sizes[rel]} lines exceeds its baselined {cap} — the baseline never grows"
                 for rel, cap in sorted(baseline.items()) if sizes.get(rel, 0) > cap]
    if refusals:
        return None, refusals
    return {rel: sizes[rel] for rel in sorted(baseline) if sizes.get(rel, 0) > FAIL_AT}, []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline", default=BASELINE)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    path = root / args.baseline
    sizes, exempt = measure(root)
    baseline = load_baseline(path)

    if args.update_baseline:
        files, refusals = update(sizes, baseline)
        if files is None:
            for refusal in refusals:
                print(f"❌ {refusal}")
            return 1
        path.write_text(json.dumps({"_comment": COMMENT, "warnAt": WARN_AT, "failAt": FAIL_AT,
                                    "files": files}, indent=2) + "\n", encoding="utf-8")
        print(f"✅ baseline rewritten: {len(files)} file(s) over {FAIL_AT} lines in {args.baseline}")
        return 0

    failures, warnings, grandfathered = judge(sizes, baseline or {})
    for rel, message in warnings:
        print(f"::warning file={rel},title=file size::{rel} — {message}")
    for rel, message in grandfathered:
        print(f"   grandfathered: {rel} — {message}")
    for rel in exempt:
        print(f"   exempt (generated by tools/inline_parts.py): {rel}")
    for rel, message in failures:
        print(f"::error file={rel},title=file size::{rel} — {message}")
    print(f"size gate: {len(sizes)} files measured · {len(failures)} fail · {len(warnings)} warn · "
          f"{len(grandfathered)} grandfathered · {len(exempt)} generated exempt")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
