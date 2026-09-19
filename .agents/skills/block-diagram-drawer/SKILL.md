---
name: block-diagram-drawer
description: "Draw publication-quality block diagrams and method figures (framework overviews, system architectures, pipelines, control loops, skill libraries, comparison and concept figures) as code-generated SVG plus 2x PNG that look like figures in ICRA, IROS, RSS, CoRL and NeurIPS robotics and AI papers: labels that print at 6 to 9 pt, names instead of sentences, symbols next to module names, real renders and photos, a muted flat palette and typeset math, verified by a headless-Chrome QA gate for overflow, overlaps, lines through labels, print-size text, sentence-length labels and a word budget. Use this skill whenever the user asks to draw, redraw, restyle or polish a block diagram, framework figure, method overview, architecture or pipeline figure for a paper, report, slide or case study (框图, 流程图, 方法图, 架构图, 示意图, 科研绘图, 论文插图, 把这个图画出来), sends a sketch, ASCII diagram, README or screenshot to turn into a figure, or says a figure does not look like a paper figure, is hard to read, has too much blank space, looks plain or looks AI-generated. Prefer academic-figures-drawer only when an editable draw.io source is the primary deliverable, archify for interactive HTML architecture explorers, and a charting skill for plots of real data."
---

# Block Diagram Drawer

Turn a description, sketch, README, ASCII diagram, or reference image into a block diagram that reads like a figure in a robotics or AI paper.
Each figure is a small Python build script using `scripts/figkit.py`; the SVG and a 2x PNG are derived from it and gated by `scripts/qa_svg_figure.py`.
The target look was measured on about forty ICRA, IROS, RSS and CoRL method figures (`references/paper-figure-study.md`): labels print at 6 to 8 pt, module names at 7 to 11 pt and panel titles at 9 to 12 pt; labels are names paired with symbols; real renders or photos carry the scene; explanations live in the caption.

## Setup

Start every new figure with the scaffold; it vendors the kit next to the build script so old figures keep rendering after the skill changes:

```bash
python <skill-dir>/scripts/scaffold.py <project>/figures/src/fig_<name>.py --width 1400 --height 500 --panels 4
cd <project>/figures/src
python fig_<name>.py
python qa_svg_figure.py ../<name>-figure.svg --png
```

The QA gate needs Chrome, Chromium, or Edge; set `CHROME_PATH` if it is not found.
Before the first figure of a session, read `references/paper-figure-study.md` (what real figures look like, with measured sizes) and `references/visual-contract.md` (palette roles, typography, shapes, connectors, pitfalls, API).
`examples/example_pipeline.py` is a complete figure that passes the gate; copy idioms from it.

## Workflow

### 1. Build a content inventory and a caption draft

List every label, number, relationship, and loop from the user's source before drawing.
This list is the contract for the figure: redraws and restyles must reproduce it exactly.
Split it into what the canvas shows (module names, symbols, structure, example inputs and outputs) and what the caption says (definitions, cardinalities, explanations, why a part exists), and write the caption draft now.
A paper figure is read together with its caption, so moving a sentence into the caption keeps the content while keeping the canvas readable.
Never invent results, dimensions, module names, or case details.
When a card needs a data sketch that is not real data (a trajectory, a progress curve, an attention map), label it `schematic`.

### 2. Fix the print target, then plan the grid

- Decide where the figure will print: a text-width `figure*` uses a 1400 px canvas and a single column uses 700 px; both are about 2.7 px per printed point, so `f.fs()` sizes work for either.
- Use a wide aspect for text-width figures, about 2:1 to 3.5:1 (1400 by 400 to 700 px); a method overview taller than that usually carries too much text.
- Lay stages out left to right in two to five columns, each with a short title; stack rows only for parallel variants or a real hierarchy.
- Draw a hierarchy as stacked group containers with the title inside each container, as Kimera, RoboMatrix and LLM3 do; do not build full-width bands with a separate header column of descriptions and a column of notes, because that reads as documentation, not as a paper figure.
- A layered schema (goal, sub-goals, sub-graphs, contracts, policies) is the exception: a narrow left column carries only layer names and, in the gaps, each relation with its cardinality, while the instances sit on shared columns to the right (`examples/example_hierarchy.py`, visual contract section 6.3).
- Split a two-part figure into panels `(a)` and `(b)` with short titles, optionally separated by a thin vertical rule.
- Use 8 px outer margins and 8 to 12 px gutters, share column positions across rows, and keep the figure title out of the canvas.
- Write the grid down as numbers (panel x-ranges, row y-ranges, card rectangles) before writing code, then express it in code with `f.cols`, `f.rows` and `f.place` instead of typed coordinates, so gutters and columns stay exact through every later edit.
- Keep one height per row and one width per column; when a row of peers needs different heights, it is two rows, not one sloppy one.
- Give each band row lines (title baseline, content top, content bottom, and an icon band and a name band in a row of tiles) and snap every card's first and last element to them; split a card shared by two things into equal halves.
- Align inside elements too: give two cards stacked in one panel shared columns, snap a patch-grid scene to its cells (`f.cells`), centre tags and example blocks by their measured width, and measure an icon's ink before centring it on a row line.
- Before the first wire, check that every cross-band wire can run straight: the two cards must overlap in x, or the gutter it climbs must fall inside the target. Move column edges instead of adding jogs.

### 3. Assign roles, then draw

- Take every font size from `f.fs(role)`: `min` 16 px, `label` 18 px, `module` 21 px, `title` 24 px, `hero` 33 px on a 1400 px canvas; primitives default to these sizes.
- Write labels as names of one to four words, pair them with a symbol where the method has one (for example "World model $F_\psi$"), and never write explanatory sentences on the canvas.
- Put verbatim example content (a user instruction, prompt, generated code, reasoning trace, feedback message) in `f.example()` cards or `f.bubble()`; only there may text run as sentences, set in serif, mono or a quote style.
- Show the task with real imagery: embed renders, camera frames, point clouds or robot photos from the project with `f.image(path, x, y, w, h)`, and ask the user for a render when none is available; a drawn `scene()` is only a placeholder labeled `schematic`.
- Give each concept one color role, keep it across every figure of the same report, and use two to four fills per figure; when the subject is a team of robots or agents, one color per member in every view, with neutral panels.
- Emphasize one key module, either with a stronger fill or with `key=True`; do not outline a whole path.
- Label edges where they are drawn (relation names in mono, flow labels in serif italic) and keep any legend to four entries in a corner.
- Draw every arrow with `f.connect`, `f.bus`, `f.arc`, `f.route` or `f.curve` so both ends sit exactly on a port: `connect` for a flow (straight when the ports line up, an elbow otherwise, `ta=None` to meet a short card head-on), `bus` for one source feeding several targets, `arc` for a short feedback bend, `route` for a loop that wraps around content through a reserved lane, `curve` for a many-to-many mapping between two stacked layers.
- Reach for `f.zone` when a row has no card of its own, and keep hand-typed paths for wires that start at a brace, a sketch or a circled step; anchor even those on `f.port` so both ends land on a real edge.
- A long feedback wire needs a lane: reserve a gutter between columns or run it through a panel title row, and give its label a knock-out (`knockout=True`) so it sits on the wire instead of beside a card; `label_at` keeps that label inside one panel.
- Curves and straight lines are both fine, but no wire may overlap another, cross a card it does not attach to, or stop short of its box.
- Use bold only for panel titles and key words, medium weight for module names, serif italic for data names and language, monospace for tokens, identifiers and code, and `$...$` for every symbol.
- Use shapes that carry meaning (token pills, trapezoid encoders, bracketed vectors, cylinders, speech bubbles, circled steps, braces, block arrows between stages) and vendored open-source icons for recognizable objects, products and actions.
- Draw networks as networks: `layer_stack` for a deep model (with `repeat="$\\times L$"`), `feature_maps` or `cuboid` for convolutional tensors, `mlp` for a small fully connected net, `token_grid` for token or patch embeddings (`masked`, `highlight`), `vector` for a single embedding, `patch_grid` for an image cut into patches, and `heatmap` for attention. A box that says "encoder" is the last resort.
- Draw by hand only what no icon can say: data sketches, graphs and plots. A hand-built robot, room or gripper glyph survives at 11 px and reads as crude at print size, so reach for `svgicons.py` first and give the icon 36 to 104 px with a 2 px display stroke.
- Keep at least 12 px of clear space between an icon, thumbnail or sketch and the next label, and compute rows of primitives from the card's inner width so nothing hangs over an edge.
- Pass `box=` for every label inside a container so the gate can check overflow and exempt example content.

### 4. Gate, look, fix, repeat

Run the QA gate after every edit, and add `--strict-tidy` for any figure that goes into a paper.
By default it fails on overflow, collisions, box overlaps, labels hidden under a later card, lines through labels, labels that print below 6 pt, labels longer than six words outside example content, more label words than the canvas budget (1 word per 10,000 px², about 70 words at 1400 by 500), and coverage below 0.40.
When text does not fit, cut words and move explanations to the caption first, then enlarge boxes or the canvas; never shrink type below `f.fs("min")`.
Relax a limit only on purpose (`--words-per-10k`, `--max-words`, `--min-coverage`), and report the measured value and the reason to the user.
The `tidy` block measures what a reader calls tidy: `--strict-tidy` fails on connector ends that miss their box (`edgeGap`), wires crossing a card they do not attach to (`edgeThroughBox`), overlapping wires (`edgeOverlap`), peer boxes that nearly line up but miss (`misalign`), off-center chip labels (`offCenter`), labels pressed against a drawing (`crowded`, measured on the ink with 3 px of clear space), drawings or icons that cross the edge of the card they belong to (`sketchOverflow`), and cards, chips or wire labels that sit half inside a panel (`straddle`).
Fix a `misalign` by making the two boxes share the number, not by nudging one of them.
`gapUneven`, `crossings`, the text fill and near-empty cards are hints: read them, then decide.
Passing the gate is necessary, not sufficient, so always open the PNG and inspect it, including crops around dense cards, math, and connectors.
Compare the PNG with two or three figures from `references/paper-figure-study.md` at the same scale: if it has more words, smaller type, or more boxes than they do, simplify before delivering.
Check that serif and monospace labels really render in those families, that arrows point the right way, and that no sketch implies data the source does not have.
Do at least three gate-and-inspect cycles for a figure the user cares about.

### 5. Deliver

- Put the SVG and PNG where the user keeps figures, and the build scripts plus the vendored kit in a `src/` folder beside them; keep `src/assets/` (icons, license files, `ASSETS.md`, and any renders) with the scripts.
- Before overwriting figures the user already has, move the previous versions into an archive folder such as `v1/`, and say so.
- Send or show the PNG together with the caption draft, summarize what changed, and state which parts are schematic or still need a real render.

## Open-source icons

Readers recognize a robot arm, camera, door, target or checklist faster than the word, so every recognizable object, product or action comes from a real icon set; only data sketches stay hand-drawn.
`scripts/svgicons.py` searches nine permissively licensed families (eight icon sets and the LobeHub logos) and vendors only the files a figure uses.

| Family | License | Style | What it is for |
|---|---|---|---|
| `tabler` | MIT | stroke | 5900 pictograms, the broad default for objects and actions |
| `lucide` | ISC | stroke | 1800 very plain icons, the calmest line family |
| `iconoir` | MIT | stroke | 1600 icons on a 1.5 px grid, a little more geometric |
| `phosphor` | MIT | fill | 9000 icons in one solid-outline style, the richest vocabulary |
| `material` | Apache-2.0 | fill | 3700 Material Symbols at weight 400; the only family with real machine and robotics vocabulary (`precision_manufacturing`, `conveyor_belt`) |
| `material200` | Apache-2.0 | fill | the same set at weight 200, for an icon that carries a card at 60 px or more |
| `fluentemoji` | MIT | colour | 1200 Microsoft Fluent Emoji, Flat style: objects in a scene (package, apple, camera, robot) and the 🔥 / ❄ trained and frozen marks; place with `color=None` |
| `fluent` | MIT | fill | 2700 Microsoft Fluent UI System Icons; the largest regular drawing of each is vendored, so detail holds at 36 px and more |
| `lobe` | MIT | logos | logos of AI models and providers (`qwen`, `openai`, `claude`) |

```bash
python <skill-dir>/scripts/svgicons.py search "robot arm"          # every family, ranked
python <skill-dir>/scripts/svgicons.py search door --family phosphor
python <skill-dir>/scripts/svgicons.py get material:precision_manufacturing --out <project>/figures/src/assets/m-arm.svg
```

Place an icon with `f.asset(HERE / "assets" / "m-arm.svg", x, y, 104, color=STEEL)`; figkit validates the file, embeds it once as a symbol, normalizes a line icon's display stroke, and tints a solid icon through `currentColor`.

- Search several synonyms across families, render the candidates on a contact sheet at the size they will be used, and pick the silhouette that names the object. A robot arm, a cup and a door are different icons in every family, and the weight that looks right at 40 px is often too heavy at 96 px.
- Mix by job, not at random: colour Fluent Emoji for objects inside frames and scenes and for the trained and frozen marks, one monochrome family for pictograms beside labels, and the Material manipulator when a robot arm is meant.
- Keep one family per figure, chosen because it has every object the figure needs; never mix a stroke family with a fill family, or either with the built-in `icon()` glyphs. Borrowing one icon from a second family is fine when the first has no word for it (a Material manipulator inside a Phosphor figure) as long as both are the same style and weight.
- When the family choice matters, make it a switch instead of an argument: read the set from an environment variable, keep each set in `assets/set-<name>/<slot>.svg` with one file name per slot, and build the same figure two or three times. Crop the icon-heavy band from each PNG, stack the crops, and choose from the stack.
- Stroke families take `sw` (1.5 px default, 2 px from about 36 px up); fill families carry their own weight, so step down to a lighter weight (`material200`) instead of enlarging a heavy one.
- Sizes: 18 to 28 px beside a label, 36 to 48 px in a tile over its name, 60 to 110 px when the icon is a card's subject. Tint with the role's deep color, ink, or a neutral steel gray.
- Put an icon beside a label or above it in a tile; it never replaces the label, never stands in for model internals, data or math, and never becomes decoration on every card.
- Place an icon beside a label from the label's measured end with 12 px of clear space, centred on that label's line rather than between two lines; an icon that only repeats a word already written on the card is decoration, so drop it.
- Use a `lobe` logo only for the exact model or provider the figure names, prefer the mono variant, and keep it smaller than the module name.
- `get` copies the family license and records the source in `assets/ASSETS.md`; ship both with the figure.
- Without network access, fall back to figkit's built-in `icon()` glyphs and say so.

## Editable draw.io export

When the user wants to edit a figure by hand, convert the finished SVG instead of redrawing it:

```bash
python <skill-dir>/scripts/svg2drawio.py <project>/figures/<name>-figure.svg --png
```

The converter renders the SVG in headless Chrome and writes `<name>-figure.drawio`: panels, cards and chips become rounded rectangles (a chip's centered label becomes its vertex label), circles become ellipses, text keeps its spans (family, size, weight, italics, color, script offsets), orthogonal connectors become edges with waypoints, arrowheads and dashes, and icons, embedded images, curves and sketches are embedded as SVG images with no external files.
`--png` renders the result with the draw.io desktop CLI (set `DRAWIO_PATH` if needed); compare it with the figure PNG before handing it over.
Edges are free-standing rather than glued to shapes, so moving a card does not drag its connectors; say so when you deliver.

## Compaction requests

When the user asks for a more compact figure, keep the content inventory and the column grid, archive the current version, and reclaim height before width.

- Move explanatory words into the caption before touching geometry.
- Tighten card heights to their content and put connector labels in bands that already exist, such as the strip above a row of cards.
- Route feedback lanes and their labels through panel title rows, and start cards beside a panel title at the title's top.
- Shrink sketch frames and images before shrinking any font; type never goes below `f.fs("min")`, and the gate rejects it.
- Rerun the gate after every step; math with subscripts needs chips at least 1.9 times the font size tall.

## Restyle requests

When the user asks only for a better look (colors, fonts, "less AI", "more like a paper"), keep the content inventory unchanged and edit only the visual layer, except that sentences may move into the caption.
If the user names a venue or the current style is not landing, study five to ten recent method figures from that venue on arXiv HTML pages (the figure images are linked from each `figure` element) and compare them with `references/paper-figure-study.md` before editing; add durable findings to that file.
Compare the label inventory, the wire inventory (every source and target pair) and the caption before and after the restyle; a rebuilt script that silently drops one arrow is a content change.

## Language

Follow the language of the user's report.
For bilingual figures, use English technical terms and math as the main label with a short Chinese annotation, or the reverse, but keep one pattern per figure.
Keep Chinese text upright in sans; never italicize CJK.

## Resources

| Path | Use |
|---|---|
| `scripts/scaffold.py` | start a figure: vendors the kit and writes a starter build script |
| `scripts/figkit.py` | primitives: print-size fonts (`fs`), grid (`cols`, `rows`, `place`), panels, cards, example cards, chips, text with math, real images, network visuals (`layer_stack`, `feature_maps`, `cuboid`, `mlp`, `token_grid`, `vector`, `patch_grid`, `heatmap`), trapezoids, cylinders, bubbles, anchored connectors (`connect`, `bus`, `arc`, `route`), sketches |
| `scripts/qa_svg_figure.py` | headless-Chrome QA gate (layout, print size, words) and 2x PNG export |
| `scripts/svg2drawio.py` | convert a finished SVG into an editable `.drawio` file, with an optional draw.io-rendered PNG for checking |
| `scripts/svgicons.py` | search and vendor open-source SVG icons (Tabler, Lucide, Iconoir, Phosphor, Material Symbols, Fluent, Fluent Emoji, LobeHub logos) with license and ledger |
| `references/paper-figure-study.md` | measured sizes, patterns and anti-patterns from ICRA, IROS, RSS and CoRL method figures |
| `references/licenses/` | MIT license texts copied beside vendored icons |
| `references/visual-contract.md` | full visual contract, API table, and pitfalls |
| `examples/example_pipeline.py` | complete reference figure |
| `examples/example_hierarchy.py` | minimal layered schema: bands, a schema column with cardinalities, many-to-many `curve` wires |
| `tests/` | unit and browser tests for the kit (`python -m unittest discover -s tests`) |
