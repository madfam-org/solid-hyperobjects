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

A change under `commons-lib/hardware/` (the shared components, ruling R2) puts
every cartridge that INLINES the changed module in scope, whether or not its own
files moved (hardware_scope). "Inlines" is read three ways and unioned: an
`# BEGIN commons-lib/hardware/<m>.py@` marker in its main.py at base or head, or
its family.py's `# inline-parts:` line naming the module directly or through a
`# requires:` chain. Fail-closed: a family.py whose line cannot be read, a module
whose `# requires:` cannot be read, and a changed file under hardware/ that is
not a module (anything but docs and tests/) each put every inlining cartridge in
scope.
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

# The shared components (tools/inline_parts.py). The patterns mirror that tool's
# grammar; this script stays stdlib-only and imports nothing from the repo.
HARDWARE_DIR = "commons-lib/hardware/"
HARDWARE_NON_GEOMETRY_DIRS = {"tests"}
HARDWARE_MARKER = re.compile(r"^# BEGIN commons-lib/hardware/([a-z][a-z0-9_]*)\.py@[0-9a-f]{40}$", re.M)
INLINE_DIRECTIVE = re.compile(r"^# inline-parts:(.*)$", re.M)
REQUIRES_LINE = re.compile(r"^# requires:(.*)$", re.M)
MODULE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
ALL = None  # "inlines something, and we cannot tell what": in scope for any hardware change


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


def _show(rev, path):
    """`path`'s text at `rev`, or None when it does not exist there."""
    try:
        return _git("show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None


def _module_requires(rev, name, cache):
    """The module's `# requires:` names at `rev`; ALL when unreadable (fail closed)."""
    if (rev, name) not in cache:
        text = _show(rev, f"{HARDWARE_DIR}{name}.py")
        lines = REQUIRES_LINE.findall(text) if text is not None else []
        names = lines[0].split() if len(lines) == 1 else ALL
        if names is not ALL and not all(MODULE_NAME.match(n) for n in names):
            names = ALL
        cache[(rev, name)] = names
    return cache[(rev, name)]


def family_modules(rev, text, cache):
    """Every module a family.py inlines (requirements included), or ALL."""
    lines = INLINE_DIRECTIVE.findall(text)
    if len(lines) != 1 or not lines[0].split():
        return ALL
    seen, todo = set(), list(lines[0].split())
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        if not MODULE_NAME.match(name):
            return ALL
        seen.add(name)
        requires = _module_requires(rev, name, cache)
        if requires is ALL:
            return ALL
        todo.extend(requires)
    return seen


def hardware_inliners(rev):
    """{slug: set of modules it inlines, or ALL} at `rev`, read from every
    main.py's markers and every family.py's `# inline-parts:` line."""
    out, cache = {}, {}
    grep = subprocess.run(["git", "grep", "-l", "-E", "^# BEGIN commons-lib/hardware/", rev,
                           "--", "*/main.py"], capture_output=True, text=True)
    if grep.returncode not in (0, 1):  # 1 = no match; anything else is git failing
        raise subprocess.CalledProcessError(grep.returncode, grep.args, grep.stdout, grep.stderr)
    for hit in grep.stdout.splitlines():
        path = hit.split(":", 1)[1]
        slug = path.split("/")[0]
        out.setdefault(slug, set()).update(HARDWARE_MARKER.findall(_show(rev, path) or ""))
    for path in _git("ls-tree", "-r", "--name-only", rev).splitlines():
        parts = path.split("/")
        if len(parts) != 2 or parts[1] != "family.py":
            continue
        modules = family_modules(rev, _show(rev, path) or "", cache)
        slug = parts[0]
        if modules is ALL or out.get(slug, set()) is ALL:
            out[slug] = ALL
        else:
            out.setdefault(slug, set()).update(modules)
    return out


def hardware_scope(base, head):
    """Cartridges that inline a commons-lib/hardware/ module this diff touched.

    A regenerated main.py already puts its cartridge in scope through its own diff;
    this is what still renders it when the module moved and main.py did not (and
    `inline_parts.py --check` is failing the manifests lane for the same reason).
    """
    # --no-renames: a renamed module must name its OLD path too, or the cartridges
    # still inlining it under that name would drop out of scope.
    changed = _git("diff", "--name-only", "--no-renames", base, head, "--", HARDWARE_DIR).split()
    modules, unknown = set(), False
    for path in changed:
        rel = path[len(HARDWARE_DIR):]
        if rel.split("/")[0] in HARDWARE_NON_GEOMETRY_DIRS or is_non_geometry_file(rel):
            continue
        if "/" not in rel and rel.endswith(".py") and MODULE_NAME.match(rel[:-3]):
            modules.add(rel[:-3])
        else:
            unknown = True  # a file the inliner does not know about: fail closed
    if not modules and not unknown:
        return []
    users = {}
    for rev in (base, head):
        for slug, inlined in hardware_inliners(rev).items():
            users[slug] = ALL if inlined is ALL or users.get(slug, set()) is ALL \
                else users.get(slug, set()) | inlined
    keep = sorted(slug for slug, inlined in users.items()
                  if (unknown or inlined is ALL or inlined & modules)
                  and _show(head, f"{slug}/project.json") is not None)
    print(f"render scope: commons-lib/hardware changed ({' '.join(sorted(modules)) or 'non-module files'}); "
          f"inlining cartridges={len(keep)}", file=sys.stderr)
    return keep


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
                  set(graph_scope_on_spec_change(base, head)) |
                  set(hardware_scope(base, head)))
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
