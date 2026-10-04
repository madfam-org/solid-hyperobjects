#!/usr/bin/env python3
"""Run the keystone's assembly check on every assemblies/*/assembly.json (ASM-1 §3, §7).

Usage: assembly_check.py [--root DIR] -- CHECKER [ARG ...]

CHECKER is the command that judges one document; the document's path is appended to
it. CI passes the pinned keystone:

    assembly_check.py -- .venv/bin/y4d-spec assembly check --commons . \
        --standard-parts <the pinned catalog's parts directory>

The lane fails closed:

- every document is checked, even after one fails, and the exit code is 1 if any
  check exits non-zero (the keystone exits 1 on a validation error and 2 when it
  cannot read the document);
- a directory under assemblies/ without an assembly.json is an error, so a
  misnamed document (assemlby.json, assembly.jsonc) cannot pass by being skipped;
- a file directly under assemblies/ is an error unless it is a README.

With no assemblies/ directory, or an empty one, there is nothing to check: the
script says so and exits 0.
"""

import argparse
import subprocess
import sys
from pathlib import Path

DOC_NAME = "assembly.json"


def is_readme(name: str) -> bool:
    return name.upper().startswith("README")


def discover(root: Path) -> tuple[list[Path], list[str]]:
    """(documents to check, problems) under root/assemblies, in sorted order."""
    base = root / "assemblies"
    if not base.is_dir():
        return [], []
    docs: list[Path] = []
    problems: list[str] = []
    for entry in sorted(base.iterdir()):
        rel = entry.relative_to(root)
        if entry.is_dir():
            doc = entry / DOC_NAME
            if doc.is_file():
                docs.append(doc.relative_to(root))
            else:
                problems.append(f"{rel}/ has no {DOC_NAME}: every assemblies/<slug>/ must carry one")
        elif not is_readme(entry.name):
            problems.append(f"{rel} is a file directly under assemblies/; documents live at "
                            f"assemblies/<slug>/{DOC_NAME}")
    return docs, problems


def run_checks(root: Path, checker: list[str]) -> int:
    docs, problems = discover(root)
    for problem in problems:
        print(f"::error title=assembly layout::{problem}")
    if not docs and not problems:
        print("assemblies: none under assemblies/ — nothing to check")
        return 0
    failed: list[str] = []
    for doc in docs:
        print(f"::group::{doc}", flush=True)
        code = subprocess.call([*checker, str(doc)], cwd=root)
        print("::endgroup::", flush=True)
        if code != 0:
            failed.append(f"{doc} (exit {code})")
            print(f"::error title=assembly check failed::{doc} exited {code}", flush=True)
    print(f"assemblies: checked={len(docs)} failed={len(failed)} layout_problems={len(problems)}")
    for item in failed:
        print(f"  FAIL {item}")
    return 1 if failed or problems else 0


def main(argv: list[str]) -> int:
    if "--" not in argv:
        print("usage: assembly_check.py [--root DIR] -- CHECKER [ARG ...]", file=sys.stderr)
        return 2
    split = argv.index("--")
    parser = argparse.ArgumentParser(prog="assembly_check.py")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv[:split])
    checker = argv[split + 1:]
    if not checker:
        print("assembly_check.py: no checker command after --", file=sys.stderr)
        return 2
    return run_checks(Path(args.root), checker)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
