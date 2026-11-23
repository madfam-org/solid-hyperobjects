#!/usr/bin/env python3
"""Sum the mesh gate's per-cartridge counts out of a nightly sweep log.

Usage: mesh_gate_counts.py LOG

The keystone (hyperobjects-spec >= 0.22.0, Yantra4D mesh-gate rulings M4-M7) appends
one clause to every `y4d-spec check --render` summary line:

    mesh-gate[report-only]: manifold=0 zero-area=0 duplicate-faces=0 chord-error=1 \
segments=0 exempt=0 size=0 facet-lint=1

The nightly runs one `y4d-spec check` per cartridge, so each clause counts 0 or 1 per
check and their sum is the number of cartridges that WOULD fail each check: what step 1
of the rollout (report-only) publishes. `exempt` is a number of findings, not of
cartridges. Prints a Markdown block for the job summary; prints a line saying so when
the log carries no clause (a keystone older than 0.22.0), never a row of zeros.
"""

import re
import sys

#: The clause's fields, in the keystone's order. Named, so the next clause on the line
#: (`parity=1/1 ok, …`) is never read as one of them.
FIELDS = ("manifold", "zero-area", "duplicate-faces", "chord-error", "segments", "exempt",
          "size", "facet-lint")
CLAUSE = re.compile(
    r"mesh-gate\[(?P<tier>[^\]]*)\]:(?P<body>(?:\s+(?:" + "|".join(FIELDS) + r")=\d+)+)"
)
FIELD = re.compile(r"([a-z-]+)=(\d+)")


def totals(text):
    """(number of clauses, {field: sum}, set of tiers) over every summary line."""
    sums = {}
    tiers = set()
    clauses = 0
    for match in CLAUSE.finditer(text):
        clauses += 1
        tiers.add(match.group("tier"))
        for name, value in FIELD.findall(match.group("body")):
            sums[name] = sums.get(name, 0) + int(value)
    return clauses, sums, tiers


def report(text):
    clauses, sums, tiers = totals(text)
    if not clauses:
        return "### Mesh gate\n\nNo `mesh-gate[...]` clause in this log (keystone before 0.22.0).\n"
    counts = " ".join(f"{name}={value}" for name, value in sums.items())
    return (
        "### Mesh gate (cartridges that would fail each check)\n\n"
        f"`{counts}` over {clauses} summary line(s); tier: {', '.join(sorted(tiers))}\n"
    )


def main(argv):
    if len(argv) != 2:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8", errors="replace") as fh:
        sys.stdout.write(report(fh.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
