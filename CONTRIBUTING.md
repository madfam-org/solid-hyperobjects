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
pip install "hyperobjects-spec[geometry] @ git+https://github.com/madfam-org/hyperobjects-spec@cb19e515c4d9b6a603e7d3863a7e6027e6877c59"

y4d-spec check ./<slug>            # manifest + files
y4d-spec check ./<slug> --render   # + geometry: every (mode, part), defaults AND every preset
```

`--render` is fail-closed. Each mesh must be watertight, of positive volume,
free of inverted bodies, and distinct per part. A preset that raises or produces
broken geometry is a failure, not a note. Printability findings (thin walls,
overhangs, build volume) are measurements, never failures.

CI runs exactly these commands. There is no second, hidden bar.

## Sign-off (DCO)

ADR-012 rules that commons contributions certify origin with the Developer
Certificate of Origin — a `Signed-off-by:` trailer on every commit (`git commit
-s`), no CLA. That ADR's scope is Fashion Cabinet first, with this commons
adopting the same rule when its third-party pipeline opens. **The sign-off lane
here is pending the ADR-012 operator steps**; until they are done, sign off if
you can and no check will block you if you did not.
