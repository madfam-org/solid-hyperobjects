# Native API count regression

The production Yantra parameter normalizer returns numeric sliders as floats.
For example, a preset's `bumper_count: 2` reaches the native sandbox as `2.0`.
Python's `range()` cannot consume that float. The original handheld family passed
bumper/trigger/rear counts directly to `range()`, so a successful integer-valued
spec preset evaluation did not guarantee a successful production export.

`family.py` now validates all count inputs before construction and converts
finite, non-negative integral numbers to Python integers. Fractional, non-finite,
negative and nonnumeric counts raise an explicit error; they are not truncated.
Manifest slider bounds and the production API's existing normalization remain
unchanged. All preset values, source facts, shapes and archetype rules are
unchanged for previously supported integer input.

Run the count tests normally with the commons geometry environment. To include
the regression through the **real API normalizer and sandbox STL exporter**, use
a separate clean Yantra checkout that supplies its actual producer/normalizer:

```sh
YANTRA4D_ROOT=/path/to/yantra4d python -m pytest \
  .github/scripts/test_slab_normalized_counts.py -q
```

This test normalizes the named ROG Ally preset (including positive rear counts),
asserts the API's float injection, exports a nonempty watertight front shell via
the actual native sandbox, then verifies a fractional normalized rear count fails
explicitly. Without `YANTRA4D_ROOT` it reports an explicit integration-test skip;
no simulated normalizer or native export is substituted. The isolated count
validation tests still run in the normal commons test suite.

The initial local integration used Yantra revision
`49a41f851b1ef66576647bc35f16f6ee7ff3e1cb` and keystone
`43ae9ae1f6d539123b95fd7ab77c3e8829ea49bd`. Source-bound archive capture is a
separate validation step using the frozen public commit and records its own
runtime, native parts, actual parameters and asset hashes. Linux CI remains the
repository's final conformance verdict.
