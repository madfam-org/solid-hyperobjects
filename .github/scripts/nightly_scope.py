#!/usr/bin/env python3
"""Cut the WHOLE commons into render groups for the nightly matrix.

Usage: nightly_scope.py [--root DIR] [--chunks N] [--limit N] [--slow-list FILE]

Prints a JSON list of space-joined groups, one per CI matrix job, on stdout;
names what it did on stderr.

WHY THIS EXISTS
---------------
The nightly used to render all 500 cartridges in ONE job. The 2026-09-06 run
(33998128926) ran 2 h 09 m and produced rows for only 454 of them: the
alphabetical tail (``tri-glide-slider`` … ``zipper-pull-assist``) plus a
handful of others never rendered at all. It did not fail on those cartridges —
it never reached them. A fail-closed nightly that silently skips 46 cartridges
is not a bar; it is a bar with a hole in it, and nothing in the run said so.

Two rules follow, and both live here rather than in the workflow so they can be
unit-tested:

1. **Deterministic order.**  ``sorted()``, always. Two runs of the same commit
   must produce byte-identical groups, or "which group covers X" stops being a
   question with an answer and a re-run cannot be compared to its predecessor.

2. **A slow cartridge gets a group of its own.**  ``zipper``'s 200 mm
   print-in-place coil takes > 16 min of kernel time for a SINGLE render
   locally (measured 2026-09-06, ``nice -n 10``, both kernels, 458 MB RSS —
   working, not hung), and it has 3 modes × 4 parts × 4 preset states × 2
   kernels to get through. Put it in a group with seven neighbours and one slow
   cartridge starves them all into the job timeout; the neighbours then look
   "never rendered" for a reason that has nothing to do with them. Any
   cartridge whose local render exceeds 5 minutes belongs in ``SLOW`` below.

The completeness check in the workflow is what makes rule 1 enforceable: the
union of the cartridges the matrix actually rendered is compared against the
scope this script printed, and a shortfall fails the report job.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Cartridges that get a matrix job to themselves. Add a slug here when its
# local render (`y4d-spec check ./<slug> --render --require-openscad
# --openscad-path libs --openscad-path . -v`, `nice -n 10`) exceeds 5 minutes.
# Keep the measurement in the comment: an unexplained entry here is an
# unfalsifiable claim about a runner nobody re-measures.
SLOW = (
    # zipper: 2352 s — 39 min 12 s — for the ONE cartridge, measured
    # 2026-09-06 02:13:48–02:53:00 CDMX (M-series, `nice -n 10`, both
    # --openscad-path roots, -v). 18 renders / 10 presets, peaking ~326 MB
    # RSS; the 200 mm print-in-place coil is the cost, and the `duffel`
    # preset stretches it to 1203 mm. A whole group of eight ordinary
    # cartridges takes 3–5 min on the CI pool, so zipper alone is ~8x the
    # group it would otherwise share — it would eat the group's budget and
    # its seven neighbours would be reported as unrendered for a reason
    # that has nothing to do with them.
    "zipper",
)


def cartridges(root: str) -> list:
    """Every directory under `root` that carries a project.json, sorted.

    Deliberately not a glob of ``*/``: ``libs/`` is a submodule mount point
    with no manifest, and y4d-spec correctly refuses it as "not a cartridge".
    """
    out = []
    for name in os.listdir(root):
        if name.startswith("."):
            continue
        if os.path.isfile(os.path.join(root, name, "project.json")):
            out.append(name)
    return sorted(out)


def plan(slugs, size: int, slow=SLOW):
    """Group `slugs` into space-joined matrix groups of at most `size`.

    Slow cartridges come first, one per group — first so the longest jobs start
    earliest and the matrix's wall clock is the slowest job, not the slowest
    job queued last behind everything else.
    """
    if size < 1:
        raise ValueError("chunk size must be >= 1")
    slugs = sorted(slugs)
    slow_here = [s for s in slugs if s in slow]
    rest = [s for s in slugs if s not in slow]
    groups = [s for s in slow_here]
    groups += [" ".join(rest[i:i + size]) for i in range(0, len(rest), size)]
    return groups


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".", help="repository root to scan")
    ap.add_argument("--chunks", type=int, default=8,
                    help="maximum cartridges per matrix group (default 8)")
    ap.add_argument("--limit", type=int, default=0,
                    help="proof-run escape hatch: RENDER only the first N "
                         "cartridges, while the scope stays the whole commons. "
                         "That asymmetry is the point: the matrix is "
                         "deliberately short of the bar, so the completeness "
                         "check has something real to catch. Never use it for "
                         "a real nightly.")
    ap.add_argument("--slug-list", metavar="FILE",
                    help="also write the full scope, one slug per line, here "
                         "(the completeness check reads it back)")
    args = ap.parse_args(argv)

    scope = cartridges(args.root)
    # The SCOPE is always the whole commons — it is the bar. --limit shortens
    # only what the matrix is told to RENDER, so a limited run under-covers the
    # scope on purpose and the completeness check has a real shortfall to
    # catch. Writing the shortened list as the scope instead would make the
    # check compare N against N and pass, which is exactly the false green this
    # lane exists to make impossible.
    render = scope[:args.limit] if args.limit and args.limit > 0 else scope
    if len(render) != len(scope):
        print(f"nightly scope: LIMITED — rendering the first {len(render)} of "
              f"{len(scope)} cartridges. The scope stays {len(scope)}, so this "
              f"run is DELIBERATELY incomplete and the completeness check must "
              f"fail the report job.", file=sys.stderr)
    groups = plan(render, args.chunks)
    if args.slug_list:
        with open(args.slug_list, "w", encoding="utf-8") as fh:
            fh.write("\n".join(scope) + ("\n" if scope else ""))
    slugs = render
    print(f"nightly scope: {len(slugs)} cartridge(s) in {len(groups)} group(s) "
          f"of at most {args.chunks}; {len([g for g in groups if ' ' not in g and g in SLOW])} "
          f"dedicated slow group(s).", file=sys.stderr)
    print(json.dumps(groups))
    return 0


if __name__ == "__main__":
    sys.exit(main())
