---
name: academic-figures-drawer
description: "Create camera-ready, editable draw.io figures from papers, method descriptions, code, or reference images. Use for ICML, NeurIPS/NIPS, ICLR, and similar ML/AI research figures: concise framework overviews, module-detail diagrams, tensor and attention flows, ablations, training/inference pipelines, and downstream-task panels. Enforce routing-first layouts with explicit orthogonal lanes, perpendicular box ports, and global zero-tolerance validation for connector-box, connector-border, connector-label, and connector-connector overlap. Optionally use image generation for a non-semantic visual concept or input/context asset, then translate the approved semantics into vector draw.io XML with preview, static validation, and screenshot-driven refinement."
---

# Academic Figures Drawer

Turn a paper or description into a figure that is easy to decode at two-column size. The editable `.drawio` XML is the source of truth; PNG/SVG/PDF are derived exports. Optimize for visual hierarchy and semantic clarity, not for enumerating every standard layer.

## Operating contract

- Make the story explicit: **input → transformation → contribution → output**.
- Use a concise framework view for the global story and a separate module view only when internal mechanics matter.
- Every shape, color, icon, tensor label, and connector must have a named meaning. Delete decorative grids, token cards, or colored blocks that do not encode real data.
- Keep real-object imagery (sensor, device, body part, waveform, application scene) in input/data/context regions only. Represent model computation with editable vector primitives.
- Distinguish prior/standard components from the paper contribution with one restrained accent color and an explicit legend.
- Preserve the paper's terminology, tensor symbols, stage order, and training/inference distinction. Never invent results, dimensions, or module names.
- Apply the reusable quality rules in `references/general-quality-contract.md`; they encode paper-scale readability, compact composition, explicit connector semantics, rendered LaTeX, real-object asset boundaries, and export-driven review.
- For every non-trivial figure, run the default template/asset discovery pass in `references/visio-and-asset-libraries.md` before composing. Prefer editable local/Tier 0 shapes; never auto-download or embed a link-only asset whose terms were not checked.
- **Default icon policy:** keep the scientific backbone editable, but when a compact pictogram materially improves recognition, use the MIT-licensed Tabler outline family by default. Search and vendor selected files with `scripts/tablericons.py`; do not wait for or spend a metered MCP allowance when Tabler supplies a suitable noun. Koboyo is opt-in only when the user explicitly asks for a hand-drawn/organic visual language or a supplied style reference requires it.
- Treat component choice as a semantic claim, not a library lookup. Follow `references/component-and-geometry-audit.md`: compare at least three candidates for every important component, require a 21/25 match score with no criterion below 4, preserve intrinsic aspect ratio, and prefer a purpose-built editable primitive when no stencil passes.
- For repeated modules and high-risk routes, create `figure-contract.json` and run `scripts/validate_figure_contract.py`. Handoff requires exact dimension/alignment checks and zero declared route penetrations in addition to the general validators.
- **Zero-overlap routing is a hard delivery gate.** Enable `global_routing` in every non-trivial `figure-contract.json`. Audit every semantic connector against every unrelated semantic box, freestanding label, relevant container boundary, and every other semantic connector. A line touching or following an unrelated box border, crossing another line, sharing a collinear segment, stacking inside the minimum lane clearance, or entering its own box tangentially is a `FAIL`, never a reviewable warning. `container=1` skill cards remain obstacles; generic visual validation alone is insufficient.

## Fast decision tree

1. **Framework overview** — 5–8 major stages, one dominant left-to-right path, only key tensors and one or two branch relations.
2. **Module detail** — zoom into the novelty: operation order, input/output dimensions, Q/K/V or feature-interaction direction, residual/skip paths, and where parameters are learned. Do not expand routine Linear/Norm/Activation layers unless they explain the novelty.
3. **Multi-panel figure** — use `(a) Overall Architecture`, `(b) Proposed Module`, and optionally `(c) Training/Downstream Tasks)` when one canvas would otherwise be unreadable. Panels share the same grid and legend.
4. **Reference replication** — treat the image as a style/layout source, not as the scientific source. Follow `references/reference-replication-protocol.md` and create the required intermediate artifacts before writing XML.

Ask at most three focused questions only when the input cannot establish the diagram type, output format, or missing scientific semantics. Otherwise infer a safe default: landscape, editable draw.io plus PNG preview, English labels unless the source is Chinese.

## End-to-end workflow

### 1. Intake and semantic brief

Read the paper section, abstract/method, prompt, code, and supplied images. Classify each source as content, structure, style, layout, or asset. Extract:

- raw input and its modality/shape;
- preprocessing or patching that is essential to the story;
- named stages and their data dependencies;
- the novel module(s), their operation sequence, and any tensor reshapes;
- training-only branches, losses, inference path, and final output;
- known/frozen components versus trainable/new components.

Create `brief.md` with goal, audience, must-communicate items, exclusions, terminology, and open assumptions. Use `references/self-supervision-and-intake.md` for the traceability table.

### 2. Style contract before drawing

If reference images are provided, read `references/style-extraction.md` and record exact or measured values in `visual-spec.md`: palette, font, type hierarchy, corner radius, stroke widths, dash pattern, margins, spacing rhythm, arrow grammar, icon language, density, and panel composition.

If no style reference is available, read `references/topconf-paper-style.md` and apply `references/figure-contract.md`.

Use this default semantic palette unless the extracted contract overrides it:

| Meaning | Fill | Stroke |
|---|---|---|
| Input/raw signal/context | `#E8F2F5` | `#58727D` |
| Existing or standard component | `#EAF0F6` | `#63758A` |
| Feature/tensor transform | `#EDE9F4` | `#7B6A9A` |
| Training/task/output head | `#F4EEDC` | `#9A7B3F` |
| Paper contribution (accent) | `#F1D7D4` | `#B44948` |
| Output/decision | `#E5F1E3` | `#5A8A55` |
| Main data flow | none | `#263238` |
| Auxiliary/skip/feedback | none | `#6B7280` (dashed) |

Use one font family throughout (Arial/Helvetica; Noto Sans CJK for Chinese text), 1.5–2 px normal strokes, 2–3 px contribution strokes, 10–14 px body labels, 16–24 px panel/stage headings, 8 px alignment grid, and 16–28 px outer margins. Tune these values to the actual canvas and render; never shrink important text below paper-scale legibility.

Relative-scale gate: treat typography and module area as a final design constraint, not an afterthought. Before handoff, inspect a canvas-only screenshot at the intended paper width and verify that panel titles are the largest text, contribution/module titles are visibly larger than annotations, and standard helper cells are not larger than the innovation block. As a practical starting point, use ≥20 px panel titles, ≥15 px key-module labels, ≥12 px tensor annotations on a 1600–2200 px canvas, and reserve at least 80–120 px width or 120–180 px height for a key module. If the figure is dense, enlarge the important module and remove redundant words before shrinking its font. Record any intentional deviations in `visual-spec.md` and the final screenshot review.

### 3. Default template and asset discovery

Before composition, search the curated source catalog using the figure type and concrete objects, then search the native draw.io index for the specific nouns that will appear:

```powershell
python <skill-dir>\scripts\assetsearch.py "<figure type + concrete objects>" --json
python <skill-dir>\scripts\shapesearch.py "<object or notation>" --limit 5 --json
python <skill-dir>\scripts\tablericons.py search "<concrete icon noun>" --limit 8 --json
```

Read `references/visio-and-asset-libraries.md` and follow its three-tier policy. The default order is editable primitives for scientific logic → bundled draw.io shape index → Tabler outline for compact semantic pictograms → other Tier 0 permissive draw.io/SVG families → Tier 1 official vendor assets → Tier 2 attribution-sensitive scientific SVGs. Tabler is the default external icon family: use Iconoir or one fixed Phosphor weight only when the component-match audit proves a materially better family-level fit. Koboyo is never automatic; use it only for an explicitly requested hand-drawn/organic treatment, and never mix it with Tabler in one repeated component group. Flaticon is not open source and must never be treated as a default-safe library. Use a Visio template only as a layout archetype unless it has been safely converted; redraw the scientific semantics and apply the current figure contract. Do not assume `.vssx` or `.vstx` imports are supported. External SVGs are acceptable for exact objects, equipment, or compact semantic pictograms, but the algorithm, model, orchestration, and evaluation logic must remain editable draw.io primitives.

After selecting a Tabler slug, vendor only that icon into the figure workspace and copy its MIT notice automatically:

```powershell
python <skill-dir>\scripts\tablericons.py get <slug> --out <work-dir>\assets\tabler\<slug>.svg --json
python <skill-dir>\scripts\validate_svg_assets.py <work-dir>\assets\tabler --strict --json
```

For every non-bundled asset, add the title/filename, exact role, stable source URL, direct asset URL when available, license/terms, required attribution, and modifications to `asset-ledger.md`. A Tier 1 icon must represent that exact vendor product. A Tier 2 asset must not be used until its individual license and creator credit have been verified. Keep a single icon family per panel or figure. Vendor only the selected SVG files beside the figure and run `scripts/validate_svg_assets.py <files-or-directory> --strict --json`; reject missing/invalid `viewBox`, aspect mismatch, scripts, event handlers, `foreignObject`, linked resources, or inconsistent stroke-family attributes before embedding.

Discovery is followed by a mandatory match gate. For every important component, write the intended noun first, shortlist at least three candidates, and score semantic specificity, silhouette match, style coherence, paper-scale legibility, and aspect fit from 1–5. Record the matrix in `component-audit.md`. A native, SVG, Koboyo, or Visio-derived shape that reads as the wrong noun must be rejected even when it is technically editable. Only candidates scoring at least 21/25 with no criterion below 4 may be selected; otherwise construct a simpler editable primitive in the figure's shared visual family. A candidate family is not approved merely because one icon fits: audit the entire repeated row for common stroke width, cap/join language, detail density, optical frame, and fill treatment.

### 4. Optional image-2 concept pass

Use the image-generation capability only when it helps explore composition or supplies a real-world input/context asset. Prompt for a clean academic concept with **no scientific text, no equations, and no tiny unlabeled blocks**. Treat the result as a visual reference; keep the paper-derived semantic graph authoritative. Do not embed the generated bitmap as the model pipeline. If a real input asset is used, record its provenance and role in `asset-ledger.md`.

Recommended concept prompt shape: “wide camera-ready scientific figure, left-to-right input–core innovation–output story, muted blue/teal/lavender/ochre palette, one restrained coral highlight for the proposed module, consistent rounded vector cards and arrows, generous whitespace, no words or equations, no decorative grids.” After generation, inspect the bitmap, write the semantic/layout inventory, and redraw the shapes and connectors in XML. If editing a user image, inspect it first and pass its local path as the image-generation reference; never use a guessed or missing path.

### 5. Plan the composition

For a framework view, choose a wide landscape canvas (roughly 1600–2200 × 850–1200 px), align stages on a single baseline, and leave whitespace around the contribution. For a module view, use a large central container with 3–6 labeled operations and small tensor-shape annotations. Use dashed containers only for meaningful groups (encoder, training-only path, memory bank, optional branch). Put the legend near a corner, never in the main flow.

Define each edge before authoring it: source, target, direction, relation type (data/control/feedback/update/annotation), cardinality, label, endpoint side, dedicated lane, and forbidden crossing zones. **Allocate lanes before placing boxes.** Reserve at least 8 px obstacle clearance, 12 px between parallel line centerlines, and enough channel width for both keep-out margins plus all planned lanes. If a route does not fit, move or resize the layout; never hide the defect behind a filled card, place a label on a tight connector, or trust automatic orthogonal routing.

Create `figure-contract.json` before XML authoring. Declare repeated card/stage rows that must be equal-width, equal-height, aligned, and equally spaced; when external SVGs are used, declare their actual image-cell frames as a separate dimension group. Declare non-overlap clearance and panel containment; declare high-risk edges with their obstacle ids and explicit-waypoint requirement, including rails and thin dividers that a long return path could penetrate. Also enable `global_routing` with every semantic edge, all semantic components as automatic obstacles, every freestanding label as an additional obstacle, every relevant group border, orthogonality, perpendicular endpoint escape, and edge-to-edge clearance. Exclude legend samples explicitly rather than silently skipping semantic connectors. Use 1 px tolerance for mechanical alignment and at most 2 px for documented optical alignment.

### 6. Author editable XML

Read `references/xml-authoring.md` before hand-authoring XML. Use explicit `mxGeometry` positions and stable ids (never reuse reserved ids `0` and `1`). Use rounded rectangles, containers, arrows, and simple editable primitives. Use `scripts/assetsearch.py` to select a permitted template or asset source, `scripts/shapesearch.py` for a specific draw.io library shape, and `scripts/aiicons.py` only for a required AI brand mark. Use `scripts/autolayout.py` only as a first placement for large graphs; manually restore the paper composition afterward. Run `scripts/edgeports.py` when several edges leave the same side of a node.

Annotate dimensions only where they answer a reader question, using a compact second line such as `X ∈ R^(B×T×D)` or `(B, C, H, W) → (B, T, D)`. For attention, show Q/K/V and arrow direction; for feature interaction, show the actual axes or branches being mixed. Add a legend mapping every used semantic color to a category and mark the contribution explicitly (e.g., `Proposed / trainable`).

### 7. Preflight and visual verification

Use `references/general-quality-contract.md` as the review contract. In particular, verify that the canvas is fitted to the composition, every arrow has an explicit semantic source and target, and formulas are rendered in the exported artifacts rather than shown as source delimiters.

Before any preview, run:

```powershell
python <skill-dir>\scripts\validate_svg_assets.py <svg-files-or-directory> --strict --json  # when external SVGs are used
python <skill-dir>\scripts\validate_figure_contract.py <figure>.drawio --contract figure-contract.json --strict
python <skill-dir>\scripts\validate_visual_quality.py <figure>.drawio
python <skill-dir>\scripts\validate_drawio.py <figure>.drawio
```

Zero `FAIL` items are required. In particular, zero global-route penetrations, border crossings, tangential ports, connector crossings, collinear overlaps, and lane-clearance violations are mandatory; none may be downgraded or justified away. Review every warning, especially component approximation, SVG family mismatch, aspect distortion, image-frame dimension mismatch, route penetration through thin dividers or rails, text overflow, arrow-box collision, overlap, spacing variance, palette scatter, orphan labels, and edge-density hotspots. Read `references/component-and-geometry-audit.md` and `references/xml-preflight.md` when a warning is ambiguous. The screenshot pass must separately trace each complete connector at paper scale and at 200% around every box-port or bend because equal numeric frames alone cannot prove renderer-specific optical clearance.

Run a proportion pass after static preflight: compare title/body/annotation scale, compare contribution versus standard-module area, and confirm that the smallest required label remains readable in the canvas-only screenshot. A figure is not ready if the XML is structurally valid but the key innovation or tensor dimensions disappear at paper scale.

Preferred preview on Windows or when URLs are long:

```powershell
python <skill-dir>\scripts\serve_drawio_preview.py <figure>.drawio --port 8765
```

Open the local preview and capture a canvas-only screenshot (the diagram should fill most of the crop). If browser automation is unavailable, export a preview with draw.io CLI without `-e`; if the CLI is unavailable, deliver XML and a browser-fallback URL from `scripts/encode_drawio_url.py`.

For a camera-ready or user-critical figure, perform at least three screenshot → complete 9-zone defect inventory → fix all P0/P1 → re-render → verify cycles. Log them in `defect-log.md`; use `references/self-supervision-and-intake.md` for the inventory, red-team pass, and self-score. Compare at paper scale, not only at editor zoom.

### 8. Final export and handoff

Export the requested formats. For an editable PNG, use the double extension and repair the known draw.io IEND truncation:

```powershell
drawio -x -f png -e -s 2 -o <figure>.drawio.png <figure>.drawio
python <skill-dir>\scripts\repair_png.py <figure>.drawio.png
```

SVG/PDF exports may also embed the XML. Report the `.drawio` source, latest preview/screenshot, exports, validation status, self-score, and remaining approximations. Never claim completion when a required component/edge is missing, text is clipped, semantics are ambiguous, or the latest evidence is partial.

## Input-specific notes

- **Paper/PDF:** use the available PDF/document reader to extract method and notation; cite no fabricated numbers. Separate training, inference, and evaluation paths.
- **Description only:** state assumptions in `brief.md` and keep the first version abstract; ask only for information that changes the semantic graph.
- **Reference screenshot:** preserve layout rhythm and typography but redraw as vectors; use a raster only for an explicitly requested input/context image.
- **Existing `.drawio`:** patch labels, geometry, styles, or edges in place for local changes; regenerate only for a layout-wide change. Re-run both validators after every edit.

## Bundled resources

- `references/figure-contract.md` — concise ICML/NeurIPS/ICLR visual and semantic contract.
- `references/component-and-geometry-audit.md` — candidate-match rubric plus exact dimension, containment, clearance, and penetration contract.
- `references/topconf-paper-style.md`, `style-extraction.md`, `reference-replication-protocol.md`, `self-supervision-and-intake.md` — paper-figure intake, reference extraction, and evidence loop.
- `references/xml-authoring.md`, `xml-preflight.md`, `primitive-icons.md` — editable XML, layout, and icon recipes.
- `references/diagram-types.md`, `shapes.md`, `visio-and-asset-libraries.md`, `troubleshooting.md` — draw.io shape vocabulary, curated Visio/template/scientific-asset discovery, and fallback guidance.
- `references/THIRD_PARTY_NOTICES.md` — license notices for included utility portions.
- `scripts/make_drawio_preview.py`, `serve_drawio_preview.py`, `validate_drawio.py`, `validate_visual_quality.py`, `validate_figure_contract.py`, and `validate_replication_artifacts.py` — preview, semantic-component, geometry, and quality gates.
- `scripts/init_figure_workspace.py` — create non-destructive `brief.md`, `visual-spec.md`, `layout-grid.md`, `asset-ledger.md`, `component-audit.md`, `figure-contract.json`, and `defect-log.md` scaffolding.
- `scripts/repair_png.py`, `encode_drawio_url.py`, `assetsearch.py`, `shapesearch.py`, `tablericons.py`, `aiicons.py`, `validate_svg_assets.py`, `autolayout.py`, `edgeports.py`, and `validate.py` — export repair, browser fallback, asset/source discovery, default Tabler search/vendor flow, SVG safety/family preflight, shape lookup, optional layout, edge-port distribution, and structural lint.
- `data/asset-catalog.json`, `shape-index.json.gz`, and `lobe-icons.json` — curated source registry plus local indexes used by asset, shape, and AI-icon lookup scripts.
