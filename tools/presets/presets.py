#!/usr/bin/env python3
"""Generate device-family cartridge presets from the keystone's reference-objects catalog.

USAGE
-----
    python3 tools/presets/presets.py --family clamshell-dual-screen-handheld
        print the presets[] array as JSON

    python3 tools/presets/presets.py --family ... --emit defaults
        print {parameter_id: default} for the archetype's own base envelope

    python3 tools/presets/presets.py --family ... --emit block
        print {"_generated_from": {...}, "presets": [...]}

    python3 tools/presets/presets.py --family ... --write <family>/project.json
        splice `_generated_from` + `presets` into a manifest in place

    python3 tools/presets/presets.py --family ... --check <family>/project.json
    python3 tools/presets/presets.py --check-all
        exit non-zero if a manifest's presets or parameter defaults are not what this
        generator writes today (the CI manifests lane runs --check-all)

`--objects DIR` reads a directory of reference objects instead of the catalog bundled in
the installed keystone (`SPEC_PIN`). The facts, the rules and the derivations are described
in `common.py` and in each family module.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from common import (
    REPO_ROOT,
    Family,
    build_presets,
    check_manifest,
    generated_from,
    report,
    write_manifest,
)
from hyperobjects_reference import load_family

HERE = Path(__file__).resolve().parent
#: Modules in this directory that are infrastructure, not families.
_NOT_FAMILIES = {"common", "presets"}


def discover() -> dict:
    """Every family module in tools/presets/: a module that defines `FAMILY`.

    Adding a family is a new module and nothing else, so parallel family PRs never edit a
    shared list. Each family's manifest is `<slug>/project.json`.
    """
    found = {}
    for path in sorted(HERE.glob("*.py")):
        if path.stem in _NOT_FAMILIES or path.stem.startswith("_"):
            continue
        fam = getattr(importlib.import_module(path.stem), "FAMILY", None)
        if not isinstance(fam, Family):
            continue
        if fam.slug in found:
            raise SystemExit(f"family {fam.slug!r} is defined twice ({path.name})")
        found[fam.slug] = fam
    return found


#: The families this generator writes.
FAMILIES = discover()


def _family(slug: str):
    fam = FAMILIES.get(slug)
    if fam is None:
        raise SystemExit(f"unknown family {slug!r}; this generator writes: "
                         f"{', '.join(sorted(FAMILIES))}")
    return fam


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--objects", type=Path, help="a directory of reference objects")
    ap.add_argument("--family")
    ap.add_argument("--emit", choices=["presets", "block", "defaults", "skipped"],
                    default="presets")
    ap.add_argument("--write", type=Path, help="splice into this project.json")
    ap.add_argument("--check", type=Path, help="verify this project.json")
    ap.add_argument("--check-all", action="store_true",
                    help="verify every family's <slug>/project.json")
    args = ap.parse_args(argv)

    if args.check_all:
        failures = 0
        for slug in sorted(FAMILIES):
            path = REPO_ROOT / slug / "project.json"
            failures += report(path, check_manifest(path, FAMILIES[slug], args.objects))
        print(f"presets check: families={len(FAMILIES)} failures={failures}")
        return 1 if failures else 0
    if not args.family:
        ap.error("--family is required unless --check-all is given")
    fam = _family(args.family)
    if args.check:
        return report(args.check, check_manifest(args.check, fam, args.objects))
    if args.write:
        write_manifest(args.write, fam, args.objects)
        print(f"wrote presets into {args.write}")
        return 0
    if args.emit == "defaults":
        values, _ = fam.derive(fam.base, full=True)
        print(json.dumps(values, indent=2))
        return 0
    objects = load_family(fam.slug, args.objects)
    presets, skipped = build_presets(fam, objects)
    if args.emit == "skipped":
        print(json.dumps(skipped, indent=2, ensure_ascii=False))
    elif args.emit == "block":
        print(json.dumps({"_generated_from": generated_from(fam, objects, skipped, args.objects),
                          "presets": presets}, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(presets, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
