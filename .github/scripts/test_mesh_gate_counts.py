"""mesh_gate_counts.py: the nightly's per-check sums of the keystone's mesh-gate clause."""

import importlib.util
import pathlib

SPEC = importlib.util.spec_from_file_location(
    "mesh_gate_counts", pathlib.Path(__file__).with_name("mesh_gate_counts.py")
)
mgc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mgc)

LINE = (
    "y4d-spec check: cartridges=1 failures=0 notes={notes} geometry=verified renders=4 "
    "presets=0 skipped=0 mesh-gate[report-only]: manifold=0 zero-area={za} "
    "duplicate-faces=0 chord-error={ce} segments=0 exempt={ex} size=0 facet-lint={fl} "
    "parity=1/1 ok, warn=0, exempt=0, placement=0, failures=0"
)


def test_sums_one_clause_per_cartridge():
    log = "\n".join([
        "=== nightly group a : a b ===",
        LINE.format(notes=2, za=0, ce=1, ex=0, fl=1),
        LINE.format(notes=1, za=1, ce=1, ex=2, fl=0),
        "  ok c (./c)",
    ])
    clauses, sums, tiers = mgc.totals(log)
    assert clauses == 2 and tiers == {"report-only"}
    assert sums == {"manifold": 0, "zero-area": 1, "duplicate-faces": 0, "chord-error": 2,
                    "segments": 0, "exempt": 2, "size": 0, "facet-lint": 1}
    # the parity clause's own `exempt=` and `failures=` are not mesh-gate fields
    assert "failures" not in sums


def test_a_log_without_the_clause_says_so_rather_than_printing_zeros():
    out = mgc.report("y4d-spec check: cartridges=1 failures=0 notes=0 geometry=verified")
    assert "No `mesh-gate[...]` clause" in out and "=0" not in out


def test_strict_tier_is_reported():
    log = LINE.format(notes=0, za=0, ce=1, ex=0, fl=0).replace(
        "[report-only]", "[strict=chord-error]")
    assert "tier: strict=chord-error" in mgc.report(log)
