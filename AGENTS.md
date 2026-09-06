# AGENTS.md — orientation for an automated contributor

You are changing a **fail-closed geometry commons**: 500 cartridges, each a
manifest plus source that turns a parameter point into geometry, each verified
by rendering it. Nothing here is checked by review alone — if you cannot render
it, you cannot claim it works.

This file is the map. It does not restate the rules; it tells you which of the
two normative documents to open, and names the traps that have actually cost
this repo a red run.

- **[`README.md`](./README.md)** — what CI runs and why: the lanes, the render
  scope, the nightly, the bar per render.
- **[`CONTRIBUTING.md`](./CONTRIBUTING.md)** — how to author a cartridge: the
  command your PR must pass, body counts, parity exemptions, constraints,
  animations, and the recurring geometry gotchas.
- **[`NOTICE.md`](./NOTICE.md)** — licence carve-outs. Read before touching
  `gridfinity`, `keyv2`, `stemfie`, `multiboard`, `polydice` or `rugged-box`.

## The one command that decides your PR

```bash
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@3aa57133186573b26279417f8de59b6c47ed9027"

y4d-spec check ./<slug> --render --require-openscad --parity \
  --openscad-path libs --openscad-path .
```

CI runs exactly this. The keystone pin is `SPEC_PIN` in
[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) — read it from there,
never from memory, and never edit a doc to match a pin you assumed.

## The lanes, in one read

| Lane | Trigger | What it does |
| :-- | :-- | :-- |
| `manifests` | every PR | `y4d-spec check` on all 500, plus `pytest .github/scripts` and the reporter selftest |
| `render-scope` | every PR | fork-point diff → which cartridges need geometry |
| `render-changed` | every PR | renders them, groups of ≤ 8, `max-parallel: 2`, 60-min jobs |
| `nightly-scope` | 09:00Z | cuts the whole commons into deterministic groups of ≤ 8 |
| `render-nightly` | 09:00Z | renders every group, `max-parallel: 3`, 90-min jobs |
| `nightly-report` | after the sweep | verdict + the single `nightly-sweep` tracking issue |

All jobs run on own-runners (ADR-010): `madfam-runners-blue` unless the
repository variable `CI_RUNNER_LABEL` overrides it. No job may use
GitHub-hosted compute.

## Five rules that are not obvious from reading the code

1. **A metadata-only manifest change skips the render lane.**
   [`.github/scripts/render_scope.py`](./.github/scripts/render_scope.py) holds
   the allow-list. `constraints` and `animations` are on it — they never reach a
   kernel. `verification` is deliberately **not**: a cartridge must never be
   able to widen its own tolerance or restate its own body count and skip the
   gate that would have checked it. If you extend `ALLOW`, add the test that
   proves the new key cannot move geometry.

2. **An unparseable manifest keeps the cartridge in scope.** The lane fails
   closed. "I could not tell" is never read as "nothing to render".

3. **Every `run:` step that pipes through `tee` must set `-o pipefail`.**
   GitHub Actions runs `bash -e {0}` — `-e` only, no pipefail. Without it a
   `… | tee` pipeline reports `tee`'s exit 0 and the step goes green over a
   failing command. This is not hypothetical: run 34023334942 showed 67 green
   jobs standing over 62 FAIL rows. The nightly group step now sets it
   explicitly and keeps a sticky return code.

4. **A green render on macOS is not proof.** The two OCCT builds disagree — the
   `tripod-hub` fuse is invalid on macOS OCCT and valid on Linux OCP. Run it
   locally, then read CI's Linux result as the verdict.

5. **The sandbox blocks `sys`, `os` and `importlib`.** A cartridge script cannot
   import a sibling module by any means, so every cartridge is a self-contained
   script. `commons-lib/cq_core.py` is the licensed canonical text that the
   inline copies inside cartridges are kept in sync with — it is not an import
   target. See its own docstring.

## When you touch geometry

Read *The gotchas that keep recurring* in
[`CONTRIBUTING.md`](./CONTRIBUTING.md#the-gotchas-that-keep-recurring) first.
The three that most often survive review and die in CI:

- **OpenSCAD silently accepts an unknown `-D`.** A parameter you declare in the
  manifest but never reference in the `.scad` is a dead slider that renders
  perfectly. Grep the source for every parameter you declare — for an
  `animations` sweep, a dead parameter means every frame is identical.
- **Rotation composes the other way.** OpenSCAD's `linear_extrude(twist=+a)`
  rotates the top by −a where CadQuery's `twistExtrude` rotates by +a. A
  herringbone whose halves point the same way is this bug.
- **Coincident faces are not a join.** Two members that merely touch export as
  separate bodies or an invalid shell. Give every join a real overlap.

## House rules

- One cartridge per PR. Born bilingual (en/es). CERN-OHL-W-2.0.
- Sign off with DCO (`git commit -s`) — ADR-012. The sign-off lane here is
  still pending its operator steps, so nothing blocks you today; sign off
  anyway.
- Never widen a tolerance or disable a parity gate without a written `reason`;
  a missing reason is a conformance failure, caught without `--render`.
- Never declare the body count a defect happens to produce. Declare the
  design's count — the declaration is how a later regression becomes visible.
