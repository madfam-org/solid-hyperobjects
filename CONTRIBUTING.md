# Contributing a cartridge

## One cartridge per PR

A pull request adds or changes exactly one `<slug>/`. That keeps the render lane
small enough to run geometry on every changed cartridge, and keeps a licence or
provenance question scoped to one object.

## Before you claim a slug: census

Search the tree and the catalog first. A near-duplicate of an existing cartridge
should extend that cartridge's parameter space, not open a second slug for the
same family — a hyperobject is the family, so two slugs for one family is a bug.

## Born bilingual (en/es)

Every human-readable string in `project.json` — names, descriptions, parameter
labels, mode and part labels, presets — carries both `en` and `es`. This is
enforced: `y4d-spec check` fails on a missing locale, it does not warn. Translate
at authoring time; a retrofit pass never catches up.

Per RFC 0039 the commons is moving to **quadrilingual** (en/es/fr/pt), starting
with the lexicon and with new catalog waves. The machine-checked floor in this
repo today is en/es; fr/pt are welcome now and will become required.

## Licence: CERN-OHL-W-2.0

Cartridges here are licensed CERN-OHL-W-2.0 (ADR-011, RFC 0038 §9 — an owner
ruling, not a per-PR choice). Ship a `LICENSE` in your cartridge that matches.

If your cartridge includes files from an upstream project, that upstream's terms
travel with them:

- **Permissive upstream** (MIT/BSD/Apache/CERN-OHL-P) — vendor the files, add a
  `<slug>/NOTICE` naming the author, source, licence and what was used, and add
  the carve-out to the root [`NOTICE.md`](./NOTICE.md).
- **Copyleft or NonCommercial upstream** (GPL, CC-BY-NC-*) — do **not** vendor.
  Consume it as a submodule fetched at build time, declare it in the root
  `.gitmodules`, and record it in both `<slug>/NOTICE` and `NOTICE.md`. If it
  cannot be kept separate, the cartridge does not belong in this commons.

Never ship a `LICENSE` that contradicts your manifest's declared licence:
`y4d-spec check` fails on that too.

## The bar your PR has to clear

```bash
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@3aa57133186573b26279417f8de59b6c47ed9027"

y4d-spec check ./<slug>            # manifest + files
y4d-spec check ./<slug> --render --require-openscad --parity \
  --openscad-path libs --openscad-path .    # + geometry, both kernels, defaults AND every preset
```

`--render` is fail-closed. Each mesh must be watertight, of positive volume,
free of inverted bodies, **valid as a B-Rep before tessellation**, distinct per
part, of the declared body count, and in agreement with the other kernel. A
preset that raises or produces broken geometry is a failure, not a note.
Printability findings (thin walls, overhangs, build volume) are measurements,
never failures.

CI runs exactly this command (see the README's *How CI verifies a change*).
There is no second, hidden bar.

**A macOS-green render is not proof.** The gate checks `BRepCheck` plus a
per-solid signed volume before any mesh exists, because a `Reversed()` solid is
`IsValid()` yet negative, and because the two OCCT builds disagree: the
tripod-hub fuse is *invalid* on macOS OCCT and *valid* on Linux OCP. Run the
command above locally, then read CI's Linux result as the verdict.

### OpenSCAD cartridges

- Include libraries by search path — `include <BOSL2/std.scad>`, `use <dotSCAD/src/…>` — never by
  relative `../../libs/` paths; CI, the platform worker and the local harness all resolve `<Lib/…>`
  through `OPENSCADPATH` (`libs/` for the six pinned third-party libraries, the repository root for the
  first-party helpers in `commons-lib/`). BOSL2 is `include`-only: `use` drops its `$tags_shown` default
  and every attachable primitive then fails BOSL2's own assertion.
- Dispatch every declared part on `render_mode` (and, in a CadQuery twin, on the `target_part` global):
  the checker rejects a cartridge whose parts render the same fallback body.
- Both kernels are rendered in CI; the local CLI (`/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
  --backend=Manifold` on macOS) is what you run before pushing:
  `y4d-spec check ./<slug> --render --require-openscad --openscad-path libs --openscad-path .`.

### Declaring body counts

498 of the 500 cartridges declare a body count; a new cartridge is expected to.
Declare the *design's* count, never the count a defect happens to produce — the
declaration is how a later regression becomes visible.

```jsonc
"verification": {
  "stages": { "geometry": { "checks": { "body_count": { "expected": 1 } } } },
  "mode_overrides": {
    "<mode>": { "part_overrides": { "<part>": { "geometry.body_count": 2 } } }
  }
}
```

Overrides use **stage-qualified keys** (`"geometry.body_count"`), and an
override *replaces* the base value; it never merges. A mode/part that is more
than one body by design declares it and says why in the source's docstring;
undeclared multi-body renders are flagged for review. Parametric counts use the
`part_quantities` expression dialect.

- Never leave a cut ending exactly on a face, a pocket wholly inside a solid, or a decorative plate unioned
  after the `difference()` that vents a cavity — all three export as inverted shells and fail the bar.

### Cross-kernel parity, and how to declare an exemption

`--parity` compares the CadQuery and OpenSCAD meshes of the same `(mode, part)`
on three gates: extents (AABB), volume, and shape. The shape gate reports the
placement offset (AABB-centre delta) as a note — or fails it under a per-part
`"placement": "strict"` — and computes the Hausdorff distance **after**
alignment, failing above `max(0.5 mm, tolerance)`.

Fix the geometry first. Only where the two kernels genuinely cannot express the
same surface does the manifest declare it, under `verification` as a base or a
per-part `"geometry.parity"` override (which, like every override, replaces the
base object whole):

```jsonc
"geometry.parity": {
  "enabled": false,
  "reason": "The OpenSCAD side cuts a real BOSL2 helical thread; the CadQuery side models it as a revolved sawtooth stack because OCCT booleans against an exact helical solid fail. The divergence is 0.902 x the ISO thread depth on every preset: the thread idiom, not a dimension error."
}
```

`enabled` (bool), `tolerance` (mm — widen only with cause), `reason` (required),
`placement` (`"strict"` to fail on offset). **A missing reason, or a widened
tolerance without one, is a conformance failure** — caught without `--render`,
so it costs a second, not an hour. Reasons are read in review: name the idiom,
the measured divergence, and where the real fix is tracked. The five standing
exemptions (`fasteners`, `spiral-planter`, `faircap-filter`, `relief`,
`locking-mechanism-hyperobject`) are worked examples. Exempt pairs print as
`parity (mode, part): exempt — <reason>`, and the summary reads
`parity=N/M ok, warn=K, exempt=E, failures=J`.

### Feasibility constraints

Every manifest on `main` carries at least one constraint (500/500). A constraint
is a rule the **configurator** evaluates on the parameter set before anything is
rendered; it never reaches a kernel, which is why a constraints-only manifest
change is skipped by the render lane.

```jsonc
"constraints": [
  { "rule": "pen_diameter > wall_thickness * 2",
    "message": { "en": "Pen must fit in the hole", "es": "El bolígrafo debe caber en el orificio" },
    "severity": "error",
    "applies_to": ["pen_diameter", "wall_thickness"] }
]
```

The dialect is the Studio's own `safeFormula` evaluator
(`apps/studio/src/lib/safeFormula.ts`), **not** a general expression language:
comparisons and arithmetic, `&&` / `||` / `!`, the ternary `c ? a : b`, and
parameter names. **No string literals** (so select parameters cannot be tested),
no function calls, 256 characters / 128 tokens. Write rules only in that subset:
the evaluator swallows exceptions, so an unevaluable rule silently never fires —
it does not shout, it just stops protecting anyone.

Both `message` locales are required, `severity` is `error` or `warning`, and
**every preset the cartridge ships must satisfy every `error` constraint** — a
preset that violates its own cartridge's rule is a bug in one of the two.

### Animations

`animations` are **parameter-state interpolation**, not per-part keyframes: the
API interpolates from `from_state` to `to_state` over `frames` and re-renders
the cartridge from the kernel at each step.

```jsonc
"animations": [
  { "id": "tray-grow",
    "label": { "en": "Tray 120 → 300 mm", "es": "Bandeja 120 → 300 mm" },
    "from_state": { "tray_width": 120 }, "to_state": { "tray_width": 300 },
    "frames": 6, "duration_ms": 3000, "easing": "ease-in-out", "mode": "unit" }
]
```

Both states must name real parameters of that `mode`, and every intermediate
point has to be renderable — an interpolation that walks through an infeasible
parameter set is a broken animation. Exploded views are not a manifest feature:
they exist only where the source itself reads an explode variable. 20 cartridges
are animated today.

### The gotchas that keep recurring

Forty-one are recorded across the wave reports; these are the ones that catch
almost every new cartridge:

- **Coincident faces are not a join.** Two members that merely touch export as
  separate bodies (or an invalid shell). Give every join a real overlap — at
  least 0.01 mm of penetration, or fuse the pair in one union.
- **Do not offset twice.** A `.transformed(offset)` followed by an `extrude`
  that also carries the offset lands the feature at double the distance; it
  renders fine and is wrong.
- **A degenerate helix radius** (a sweep radius that reaches zero at either end)
  yields a non-manifold sweep. Clamp it.
- **Tangent cylinders do not boolean.** Exactly-touching cylinders — and a wall
  tangent to every tooth root — leave CGAL/OCCT with a zero-thickness contact.
  Overlap them or step them apart.
- **Selects are strings.** A select parameter arrives as a string on both
  kernels; `int(...)`-ing it on one side and comparing strings on the other is
  how the same preset grew a 5 mm additive prism on one kernel only.
- **BOSL2 `diff()` keeps by tag.** Children are removed only where their tags
  say so; a `keep`-tagged child is never bored. Check both sides of a
  `diff()`/`difference()` pair render the same voids.
- **Name your font.** Neither kernel defaults to the same face, so unnamed
  `.text()` diverges by millimetres. Pin the font, and expect glyph outlines to
  still differ slightly between OCCT and FreeType.
- **OpenSCAD silently accepts an unknown `-D`.** A parameter declared in the
  manifest but never referenced by the `.scad` is a dead slider, and nothing
  errors. Grep your source for every parameter you declare.
- **BOSL2 is `include`-only** (see above), and **rotation composes**: OpenSCAD's
  `twist=+a` rotates the top by −a where CadQuery's `twistExtrude` rotates by
  +a. A herringbone whose halves point the same way is this bug.

## Sign-off (DCO)

ADR-012 rules that commons contributions certify origin with the Developer
Certificate of Origin — a `Signed-off-by:` trailer on every commit (`git commit
-s`), no CLA. That ADR's scope is Fashion Cabinet first, with this commons
adopting the same rule when its third-party pipeline opens. **The sign-off lane
here is pending the ADR-012 operator steps**; until they are done, sign off if
you can and no check will block you if you did not.
