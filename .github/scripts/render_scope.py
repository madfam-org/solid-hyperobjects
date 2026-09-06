#!/usr/bin/env python3
"""Drop cartridges whose only change is manifest metadata from the render scope.

Usage: render_scope.py [--chunks N] BASE HEAD [SLUG ...]
Prints the slugs that still need a render, one per line (or, with --chunks N, a
JSON list of space-joined groups of at most N slugs for a CI matrix); names the
skipped ones on stderr.

A cartridge needs no render when every changed file under it is either
(a) a non-geometry file — NOTICE, LICENSE*, README*, any *.md, anything under
docs/, images (png/jpg/jpeg/gif/svg/webp) — or (b) project.json with every
changed leaf under an allow-listed key that has no bearing on geometry:
attribution, prose, tags, lineage, constraints (feasibility rules the
configurator evaluates on the parameter set — they never reach the kernel).
Anything else — .scad/.py/.cq source,
fonts/ (they change what .text() renders), parameters, parts, modes, presets,
engine, verification, or any unknown file — keeps the cartridge in scope. A
manifest that fails to parse on either side keeps the cartridge in scope too:
the lane fails closed, never open.
"""

import json
import subprocess
import sys

ALLOW = (
    "constraints",
    "hyperobject",
    "tags",
    "project.attribution",
    "project.description",
    "project.name",
    "project.tags",
    "project.difficulty",
    "project.thumbnail",
    "project.hyperobject",
    "project.version",
)

# Files whose change can never move geometry. fonts/ is deliberately absent:
# a bundled font changes what Workplane.text() renders.
NON_GEOMETRY_NAMES = {"NOTICE", "LICENSE", "LICENCE", "COPYING", "README"}
NON_GEOMETRY_SUFFIXES = {".md", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf"}
NON_GEOMETRY_DIRS = {"docs"}

_MISSING = object()


def is_non_geometry_file(path):
    """True for a cartridge-relative path (below the slug) that cannot affect a render."""
    parts = path.split("/")
    if parts[0] in NON_GEOMETRY_DIRS:
        return True
    name = parts[-1]
    stem = name.split(".")[0].upper()
    if stem in NON_GEOMETRY_NAMES:
        return True
    dot = name.rfind(".")
    return dot > 0 and name[dot:].lower() in NON_GEOMETRY_SUFFIXES


def _leaves(obj, prefix=""):
    if isinstance(obj, dict) and obj:
        for key, val in obj.items():
            yield from _leaves(val, f"{prefix}.{key}" if prefix else key)
    elif isinstance(obj, list):
        yield prefix, json.dumps(obj, sort_keys=True)
    else:
        yield prefix, obj


def changed_paths(before, after):
    a, b = dict(_leaves(before)), dict(_leaves(after))
    return {p for p in set(a) | set(b) if a.get(p, _MISSING) != b.get(p, _MISSING)}


def _git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def _manifest_at(rev, slug):
    try:
        return json.loads(_git("show", f"{rev}:{slug}/project.json"))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def _allowed(path):
    return any(path == key or path.startswith(key + ".") for key in ALLOW)


def needs_render(base, head, slug):
    files = _git("diff", "--name-only", base, head, "--", f"{slug}/").split()
    if not files:
        return True  # nothing diffed under the slug: not our call to skip
    rel = [f[len(slug) + 1 :] for f in files]
    others = [r for r in rel if r != "project.json"]
    if any(not is_non_geometry_file(r) for r in others):
        return True
    if "project.json" not in rel:
        return False  # only NOTICE / docs / images moved
    before, after = _manifest_at(base, slug), _manifest_at(head, slug)
    if before is None or after is None:
        return True
    return not all(_allowed(p) for p in changed_paths(before, after))


def chunk(slugs, size):
    """Split the kept slugs into space-joined groups of at most `size`.

    One CI job per group keeps every render job short and bounded: a 51-cartridge
    PR on a 6 GiB / 1.5-CPU runner took two ~30-minute attempts to lose the
    runner entirely, with no log left behind to name the cartridge. Small groups
    isolate a failure to a handful of slugs and let the rest of the PR go green.
    """
    return [" ".join(slugs[i : i + size]) for i in range(0, len(slugs), size)]


def main(argv):
    args = list(argv[1:])
    chunks = None
    if args[:1] == ["--chunks"]:
        if len(args) < 2 or not args[1].isdigit() or int(args[1]) < 1:
            print("usage: render_scope.py [--chunks N] BASE HEAD [SLUG ...]", file=sys.stderr)
            return 2
        chunks = int(args[1])
        args = args[2:]
    if len(args) < 2:
        print("usage: render_scope.py [--chunks N] BASE HEAD [SLUG ...]", file=sys.stderr)
        return 2
    base, head, slugs = args[0], args[1], args[2:]
    keep = [s for s in slugs if needs_render(base, head, s)]
    skipped = sorted(set(slugs) - set(keep))
    if skipped:
        print(
            f"render scope: {len(skipped)} metadata-only cartridge(s) skipped: {' '.join(skipped)}",
            file=sys.stderr,
        )
    if chunks is not None:
        print(json.dumps(chunk(keep, chunks)))
    else:
        print("\n".join(keep))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
