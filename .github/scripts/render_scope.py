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
configurator evaluates on the parameter set — they never reach the kernel),
animations (parametric flipbook sequences the API renders on demand from
from_state/to_state; the cartridge's own render never reads them).
Anything else — .scad/.py/.cq source,
fonts/ (they change what .text() renders), parameters, parts, modes, presets,
engine, verification, or any unknown file — keeps the cartridge in scope. A
manifest that fails to parse on either side keeps the cartridge in scope too:
the lane fails closed, never open.

`hyperobject` is metadata EXCEPT the interface fields the keystone's render-time
frame gate judges (ASM-1 §8): a change to any cdg_interfaces entry's `frame`,
`size_key`, `polarity`, `symmetry`, `let` or `geometry_type` (GATED_INTERFACE_KEYS)
keeps the cartridge in scope, because `y4d-spec check --render` is the only thing
that compares a frame with the geometry. Without this, a frames-only PR skipped the
render lane and its frames were proven by nothing but the nightly sweep (F6).
A label- or prose-only interface change is still metadata.
"""

import json
import re
import subprocess
import sys

ALLOW = (
    "animations",
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

# cdg_interfaces fields the frame gate reads (`geometry_type` picks its rule, `let`
# feeds the frame, the rest are what a mate and the gate verify). A change to any of
# them, on any interface, forces a render.
GATED_INTERFACE_KEYS = ("frame", "size_key", "polarity", "symmetry", "let", "geometry_type")
INTERFACE_LISTS = (("hyperobject", "cdg_interfaces"), ("project", "hyperobject", "cdg_interfaces"))

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


def _gated_interfaces(manifest):
    """{(list path, interface id or position): {gated key: canonical JSON}} for every
    interface that carries at least one gated key."""
    out = {}
    for path in INTERFACE_LISTS:
        node = manifest
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
        for pos, iface in enumerate(node if isinstance(node, list) else []):
            if not isinstance(iface, dict):
                continue
            fields = {k: json.dumps(iface[k], sort_keys=True) for k in GATED_INTERFACE_KEYS
                      if k in iface}
            if fields:
                ident = iface.get("id") if isinstance(iface.get("id"), str) else f"#{pos}"
                out[(".".join(path), ident)] = fields
    return out


def frame_fields_changed(before, after):
    """True when any interface's frame-gate fields differ between the two manifests
    (added, removed or edited)."""
    return _gated_interfaces(before) != _gated_interfaces(after)


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
    if frame_fields_changed(before, after):
        return True  # the frame gate must re-judge them (F6)
    return not all(_allowed(p) for p in changed_paths(before, after))


def chunk(slugs, size):
    """Split the kept slugs into space-joined groups of at most `size`.

    One CI job per group keeps every render job short and bounded: a 51-cartridge
    PR on a 6 GiB / 1.5-CPU runner took two ~30-minute attempts to lose the
    runner entirely, with no log left behind to name the cartridge. Small groups
    isolate a failure to a handful of slugs and let the rest of the PR go green.
    """
    return [" ".join(slugs[i : i + size]) for i in range(0, len(slugs), size)]


def graph_scope_on_spec_change(base, head):
    """Re-prove graph cartridges when the package owning their transpiler moves."""
    def pin(revision):
        workflow = _git("show", f"{revision}:.github/workflows/ci.yml")
        match = re.search(r"^\s+SPEC_PIN:\s*(\S+)", workflow, re.MULTILINE)
        if not match:
            raise ValueError(f"Cannot resolve SPEC_PIN at {revision}")
        return match.group(1)

    if pin(base) == pin(head):
        return []
    paths = _git("ls-tree", "-r", "--name-only", head).splitlines()
    graphs = []
    for path in paths:
        parts = path.split("/")
        if len(parts) != 2 or parts[1] != "project.json":
            continue
        manifest = json.loads(_git("show", f"{head}:{path}"))
        if any(
            isinstance(mode.get(key), str) and mode[key].endswith(".graph.json")
            for mode in manifest.get("modes", [])
            for key in ("cq_file", "scad_file", "graph_file")
        ):
            graphs.append(parts[0])
    print(f"render scope: SPEC_PIN changed; graph cartridges={len(graphs)}", file=sys.stderr)
    return sorted(graphs)


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
    keep = sorted(set(s for s in slugs if needs_render(base, head, s)) |
                  set(graph_scope_on_spec_change(base, head)))
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
