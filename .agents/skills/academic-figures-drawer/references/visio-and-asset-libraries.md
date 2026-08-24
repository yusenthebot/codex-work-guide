# Visio templates and external asset libraries

Read this before using a Visio template, a custom draw.io library, a vendor
icon pack, or a scientific illustration. The goal is to improve recognition
and composition without sacrificing editability, provenance, or paper-scale
clarity.

## Default discovery pass

Run this for every non-trivial figure before composition:

```bash
python3 <skill-dir>/scripts/assetsearch.py "<figure type + concrete objects>" --json
```

Then search the bundled native shapes for each concrete semantic noun:

```bash
python3 <skill-dir>/scripts/shapesearch.py "<object or notation>" --limit 5 --json
```

Do not stop at the first result. Search synonyms and neighboring nouns until
there are at least three plausible candidates. Then run the component-match
matrix in `component-and-geometry-audit.md`. Library provenance and semantic
fitness are separate gates: a permitted native stencil can still be the wrong
component.

Selection order:

1. Editable primitives and the bundled draw.io shape index for the scientific logic.
2. Tabler outline for compact semantic pictograms when an icon is faster to read than text.
3. Other Tier 0 draw.io libraries or normalized open-source SVG families only when
   the component audit proves a materially better family-level match.
4. Tier 1 official vendor assets, only for the exact product/service depicted.
5. Tier 2 scientific SVG libraries after per-asset license and attribution review.
6. Image generation only when a composition study or real-world context image is
   genuinely needed.

External assets are never a substitute for the semantic graph. A Visio template
may suggest grouping, hierarchy, or whitespace; redraw the paper's content with
the current figure contract instead of inheriting a template's labels, colors,
or ornamental detail.

## Component-fit gate

For each important component, write its intended noun before opening a library.
Score at least three candidates on semantic specificity, silhouette match,
style coherence, paper-scale legibility, and aspect fit. The selected candidate
must score at least 21/25 and no criterion may be below 4.

- Reject a loading-arm or linkage stencil when the figure needs a recognizable
  six-axis robot arm.
- Reject a jack, key, or plug silhouette when the concept is provider binding or
  registry selection.
- Reject detailed DIP/QFP packages when pin numbers and package details become
  microtext; use a simplified processor/card primitive instead.
- Reject a filled clip-art certificate if the surrounding family is thin-line;
  draw a document-and-seal primitive in the same stroke language.
- Preserve the component's intrinsic aspect ratio. If it does not fit the
  allocated slot without distortion, change the slot or choose another asset.

Use the same visual family within a component row: shared stroke width, corner
language, fill treatment, optical size, and detail density. A mixed row of
electrical stencil, flat Unicode glyph, 3-D cube, and filled badge is not a
coherent component system even if every item is individually editable.

## Open-source SVG shortlist

For IROS/ICRA-style engineering figures, prefer these normalized outline
families before searching large mixed marketplaces:

1. **Tabler Icons** — MIT, 24×24 grid, consistent round cap/join, broad system
   vocabulary. This is the default external SVG family for compact engineering
   schematics when native draw.io shapes are less coherent. Search and vendor
   selected outline SVGs with `scripts/tablericons.py`; the tool copies the MIT
   notice beside the selected assets and does not require an MCP key.
2. **Iconoir** — MIT, 24×24 outline family. Use when its silhouettes match the
   intended nouns better than Tabler; do not mix both families in one row.
3. **Phosphor Core** — MIT and available as raw SVG. Select one weight and keep
   that weight throughout the figure.
4. **Koboyo** — opt-in for an intentionally hand-drawn explanatory style only.
   Its icons are free for personal and commercial use without attribution, but
   its custom license restricts redistribution of the library and its MCP/API
   may impose account retrieval quotas. Do not spend Koboyo quota when Tabler
   already passes the semantic gate, and do not mix its organic cadence into a
   Tabler or precise engineering-line row.

## Default Tabler workflow

Use concrete English nouns and inspect several silhouettes before choosing:

```bash
python3 <skill-dir>/scripts/tablericons.py search "robot" --limit 8 --json
python3 <skill-dir>/scripts/tablericons.py get robot \
  --out <work-dir>/assets/tabler/robot.svg --json
python3 <skill-dir>/scripts/validate_svg_assets.py \
  <work-dir>/assets/tabler --strict --json
```

The search command caches the official Tabler GitHub tree for seven days. The
`get` command accepts a safe icon slug, downloads only from the official raw
GitHub path, performs a small SVG boundary check, writes atomically, and copies
`LICENSE-Tabler.txt` into the asset directory. Record the selected icon page,
exact semantic role, recoloring, and embedding method in `asset-ledger.md`.

If Tabler has no candidate that reaches 21/25, compare Iconoir or one fixed
Phosphor weight as a complete family. Do not replace a single failed Tabler icon
with a lone icon from another family inside an otherwise Tabler row. Build an
editable primitive or switch the whole repeated group.

**Flaticon is not open source and is not a default source.** Free use generally
requires attribution and the downloadable source assets carry redistribution
and sublicensing limits. Use it only after the exact asset and account/license
terms are recorded; prefer the MIT families above for paper figures.

## External SVG family gate

Before embedding any external SVGs, vendor only the selected files and run:

```bash
python3 <skill-dir>/scripts/validate_svg_assets.py <svg-file-or-directory> --strict --json
```

The gate fails on missing/invalid `viewBox`, declared-size versus `viewBox`
aspect mismatch, scripts, event handlers, `foreignObject`, linked images, URLs,
or inconsistent family attributes such as stroke width/cap/join. Then declare
the actual display frames in `figure-contract.json` and validate:

- exact width and height per repeated row;
- top/center alignment and equal gaps;
- preserved intrinsic aspect (`aspect=fixed` in draw.io);
- one optical stroke weight after scaling;
- connector clearance from the icon frame and its containing box;
- no remote runtime dependency after embedding.

The SVG is a vector image cell, not a native draw.io primitive. Keep the
vendored source beside the figure so path-level edits remain possible, and
record the source, license, display-stroke modification, and embedding method in
`asset-ledger.md`.

## Format compatibility

| Source format | Default handling | Important constraint |
|---|---|---|
| draw.io `.xml` / `mxlibrary` | Open directly as a custom library | Check the individual upstream asset license even when the library repository is permissive |
| Visio `.vsdx` | Import with the online draw.io editor, then save as `.drawio` | Conversion is server-side and may not preserve every Visio detail; never upload sensitive diagrams |
| Visio `.vss` | Convert at `https://vss.draw.io`, then import the resulting library | The converter is online; confirm the stencil contains no sensitive data |
| Visio `.vssx` | Do not assume direct conversion | Prefer an official SVG pack, export selected masters to SVG in Visio, or save a compatible legacy `.vss` copy first |
| Visio `.vstx` | Use as a Visio/layout reference | Do not promise direct draw.io import; recreate the selected composition natively |
| SVG | Sanitize, preserve `viewBox`, and import only for a concrete object/icon | It remains a vector image cell; keep the vendored source for path-level edits |
| PNG/JPG | Input/context region only | Never use a raster screenshot for the algorithm or system backbone |

## Three license tiers

### Tier 0 — default-safe

Use these first: bundled draw.io shapes and explicitly permissive custom
libraries (Apache-2.0, MIT, CC0). Keep a single icon family per figure and
normalize stroke, optical size, and color to the visual contract.

### Tier 1 — official vendor terms

Microsoft, Azure, and AWS assets are suitable when the diagram represents the
corresponding service or product. They are not generic substitutes. Do not
rotate, distort, recolor, or repurpose official product icons against the
vendor's guidance. Record the source page and pack/version date in
`asset-ledger.md`.

### Tier 2 — per-asset or attribution-sensitive

BioIcons mixes licenses by asset. SciDraw and Servier Medical Art require CC BY
4.0 attribution. Before embedding one of these assets, record the creator,
asset title, exact URL, license, required credit, and any modifications. Put the
credit in the paper's figure caption or acknowledgments when the license calls
for it.

## Visual-use rules for academic figures

- Use icons only when shape recognition is faster than reading another box.
- Prefer one-color outline or restrained two-tone assets for IROS/ICRA-style
  system figures. Avoid mixing photorealistic equipment, 3D cloud icons, and
  flat glyphs on one canvas.
- Keep logos and vendor icons subordinate to the method contribution. A logo
  must never be the largest object in a scientific panel.
- Do not use a branded icon for a generic concept such as "cloud," "model," or
  "database." Use a native primitive or generic Tier 0 glyph instead.
- Use external scientific SVGs for concrete entities (robot, organ, lab
  apparatus, sensor setup), not for the execution logic, model internals, or
  evaluation protocol.
- If the asset cannot be traced to a stable source and clear terms, do not use
  it. Redraw a simple editable symbol instead.

## Asset-ledger record

For every non-bundled asset, record:

```text
Asset: <title / filename>
Role: <exact semantic role in the figure>
Source: <stable source page and direct asset URL>
License/terms: <identifier or vendor terms>
Attribution: <exact required credit, or "none stated">
Modifications: <crop/recolor/redraw, or "none">
Decision: <used / rejected and why>
```

The catalog in `data/asset-catalog.json` is a discovery aid, not a license
guarantee. Its `last_verified` date must be considered before using a source
whose terms or files may have changed.
