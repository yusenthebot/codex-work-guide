# Block Diagram Visual Contract

This contract governs static, paper-style block diagrams built as code-generated SVG.
The figure build script is the source of truth; the SVG and PNG are derived artifacts.
It trades in-editor editability for print-size typography, typeset math, real imagery, data sketches, and exact reproducible layout.
Its numbers come from measured robotics and AI method figures; see `paper-figure-study.md`.

## 1. When this skill is the right tool

Use it when at least one of these holds:

- The user wants a figure that looks like a top-venue paper figure and says the current result is sparse, plain, hard to read, generic, or looks AI-generated.
- The figure needs many small typeset symbols, sub/superscripts, or inline math next to labels.
- Cards should carry data sketches: thumbnails, trajectory curves, bar strips, attention maps, timelines, or schematic plots.
- Labels mix CJK and Latin text and must render consistently.
- The figure will be regenerated often, or several figures must share one exact visual system.

Use `academic-figures-drawer` instead when the user or venue needs an editable `.drawio` source, when collaborators will hand-edit the figure, or when the figure is a routing-heavy graph that benefits from the draw.io routing contract.
Use `archify` for interactive HTML architecture explorers, and a charting skill when the figure plots real data.
When the choice is unclear, ask once; otherwise default to this skill for "make it look like the paper figure" requests.

## 2. Why generated figures do not look like paper figures

Compare the draft against strong paper figures on these axes before changing anything.

| Axis | Strong paper figure | Typical generated draft |
|---|---|---|
| Print size | Labels print at 6 to 8 pt, module names 7 to 11 pt, titles 9 to 12 pt (16 to 33 px on a 1400 px text-width canvas) | 11 to 13 px labels that print at 4 to 5 pt |
| Words | 30 to 80 label words in a text-width figure; sentences only inside example prompts, code or traces | Explanatory sentences, questions and notes beside every part |
| Structure | Stage columns or titled group containers; explanations in the caption | Full-width bands with a header column of descriptions and a notes column, plus a legend strip explaining every symbol |
| Imagery | Real renders, camera frames, point clouds or photos | Cartoon scenes drawn from icons, or no task context at all |
| Fill | Content and imagery cover most of the canvas at readable size; gutters about 8 to 12 px | Large margins, in-canvas title band, long arrows, boxes two to three times larger than their text |
| Hierarchy | Three nesting levels: stage panel, card, chip or symbol | One level of same-size boxes |
| Content | Names paired with symbols, terms, and notation hooks on every card | Prose sentences that read like slides |
| Palette | Three or four muted flat fills with a slightly darker stroke, warm-gray neutrals | Gradients, many saturated hues, thick colored outlines, filled saturated badges |
| Typography | Bold only for panel titles and key words; regular or medium module names; serif italic for data names and language; monospace for tokens and outputs | Bold sans everywhere and uppercase letter-spaced headers, which read as a UI dashboard |
| Shapes | Token pills, trapezoid encoders, bracketed vectors, cylinders, block arrows, circled step numbers, dashed groups | Rounded rectangles and generic UI icons for everything |
| Connectors | Thin near-black wires, braces, fork and merge dots, dashed gray loops with italic labels | Colored arrows on every edge |
| Layout | Wide single-row pipeline on a strict column grid; title lives in the caption | Vertical single columns with empty sides; title inside the canvas |

## 3. Print size and density contract

- The canvas maps to a print width: 1400 px for a text-width `figure*` (516 pt) and 700 px for one column (252 pt), about 2.7 px per point either way; `Fig` stores it as `data-print-width-pt`.
- No label prints below 6 pt (16.3 px at 1400 px); the gate enforces it, and math scripts inside a label are exempt.
- No label outside example content has more than six words, and label words stay within 1 per 10,000 px² of canvas (70 words at 1400 by 500).
- Content coverage, measured by `scripts/qa_svg_figure.py`, is at least 0.40 and typically 0.55 to 0.75 once imagery is in place; framed coverage is usually above 0.85.
- Outer margin is 8 px; gutter between panels is 8 to 12 px; card padding is 10 to 14 px.
- No empty band wider than one card height may remain inside a panel; fill it with an image, sketch, notation, or example content, or shrink the panel.
- Do not put the figure title, a long subtitle, or explanatory notes inside the canvas; the paper caption carries them.
- Prefer a wide aspect ratio for text-width figures (about 2:1 to 3.5:1) and stack rows only when the story has parallel variants or a layered hierarchy with vertical cross-layer arrows.
- Panel title rows are shared space: cards beside the title may start at its top, and loop lanes with their labels may run through the row.
- Density never comes from small text: first move explanations into the caption, then remove redundant words, then tighten boxes to their content, then reflow, then grow the canvas.

## 4. Visual language

The defaults in `scripts/figkit.py` follow measured method figures from ICRA, IROS, RSS and CoRL papers such as LOTUS, BUMBLE, ConceptGraphs, Kimera, LLM3, Octo, DROC, MOKA, VoxPoser and ReKep (`paper-figure-study.md`).
Study a few current method figures from the target venue before a major restyle, and record the palette, weights, and shape vocabulary you adopt.

### 4.1 Composition

- **Stage panel:** flat, very light role tint without an outline, or a dashed warm-gray outline for input groups; left-aligned bold title with a panel label such as `(a)`, followed by a regular gray subtitle on the same line or below it in narrow panels.
- **Card:** pastel role tint with a 1 px stroke one step darker; white cards with a hairline stroke for neutral content.
- **Group container:** a layer or subsystem is a light container with its title inside the top-left corner (or in a title bar); descriptions of what it does go in the caption, not in a side column.
- **Key module:** exactly the module the reader should find first gets a stronger fill or a near-black 1.4 px outline (`key=True`); do not outline everything.
- **Example card:** verbatim prompts, instructions, generated code and reasoning traces sit in `example()` cards or bubbles; these are the only places for sentences.
- **Image:** renders, camera frames, point clouds and photos are embedded with `image()` in a thin frame; they are the default way to show the task.
- **Chip:** small light rectangle with a hairline stroke; dashed chips mark derived or linked quantities.
- **Tag:** tint fill with bold deep-color text for a key number; never a saturated filled pill with white text.
- Use a shared column grid across rows so equivalent stages align vertically.
- Every card gets a hook: a symbol, notation, thumbnail, data sketch, or attached technical term.
- Attach technical terms to the component they belong to instead of listing them in a separate legend; when a legend is unavoidable, keep it to four entries in a corner.

### 4.2 Color roles

Assign one role per concept and reuse it in every figure of the same paper.

| Role key (alias) | Typical meaning |
|---|---|
| `amber` (ochre) | reasoning model, planner, the key module |
| `blue` (teal) | motor policy, perception, main learned policy |
| `green` (sage) | accept, success, closing feedback |
| `red` (terracotta) | contribution highlight, override, error, loss |
| `purple` (lavender) | control, structure, auxiliary models |
| `orange` (clay) | proprioception or a secondary signal |
| `gray` (stone) | inputs, neutral containers, standard components |

Connectors are near-black (`WIRE`) by default; color an edge only when it carries a branch outcome such as accept or override.
When the subject is a team (robots, agents), give each member one color and keep it in every view (task chips, winning allocation cells, agent cards, message frames, map markers, schedule bars); keep the panels neutral and red for failure only, so color reads as identity.
Avoid gradients on containers; a gentle gradient is acceptable only inside a token row that blends two modalities.

### 4.3 Typography

- Sans (Helvetica Neue or Arial with a CJK fallback) for labels.
- Bold (700) only for panel titles, branch outcomes, and one or two key words per card.
- Medium (500) for module and card names; light (300) for one large focal word or number.
- Serif italic (`family="serif", italic=True`) for data names, variables in prose, quoted language, and connector labels.
- Monospace (`family="mono"`) for tokens, discrete outputs such as `accept` or `override`, tick labels, and code-like terms.
- Math through `$...$` for every symbol; never fake math with sans italics.
- Sentence case everywhere; no uppercase letter-spaced headers.
- Chinese text stays upright in sans; do not synthesize italic CJK.
- Sizes come from `f.fs(role)`, which converts measured printed sizes to canvas pixels: `min` 6 pt (16.3 px at 1400 px), `label` 6.7 pt (18.2 px), `module` 7.8 pt (21.2 px), `title` 9 pt (24.4 px), `hero` 12 pt (32.6 px) for one focal symbol or number.
- Many IEEE figures set every label in the paper's Times-like serif with bold serif module names; that is a valid alternative to sans when the paper body is Times, but keep one family per figure for labels.
- Nothing prints below 6 pt: figures are read at column or text width, where smaller labels become unreadable. The QA gate enforces this with `smallText`.

### 4.4 Shape vocabulary

| Meaning | Primitive |
|---|---|
| sequence of tokens or an action chunk | `tokens` |
| encoder or feature extractor | `trapezoid` |
| action or state vector | `bracket` around math symbols |
| stored data, history, dataset | `cylinder` |
| language input or model utterance | `bubble` |
| ordered sub-steps | `step` circled numbers |
| stage transition | `block_arrow` |
| grouped inputs | `brace` |
| task scene, camera frame, point cloud, robot photo | `image` with a real render or photo; `scene` only as a labeled placeholder |
| user instruction, prompt, generated code, reasoning trace | `example` card or `bubble` |
| recognizable object (robot, camera, door, goal, checklist) | vendored Tabler outline icon via `asset` |
| named model or provider | vendored LobeHub mono logo via `asset` |

Icons label objects; they are not content.
Method-specific structure (graphs, token rows, kinematic chains, curves) stays a drawn sketch, while recognizable objects use a vendored open-source icon instead of a hand-drawn imitation.

### 4.5 Open-source icons

- Source icons with `scripts/svgicons.py`, which spans eight permissively licensed families, including colour Fluent Emoji for scene objects and Fluent UI System Icons, and before them: `tabler`, `lucide` and `iconoir` (line), `phosphor` and Material Symbols `material` / `material200` (solid outline), and `lobe` for model and provider logos. Only the selected files are downloaded.
- Material Symbols is the only family with real machine and robotics vocabulary, so a figure that needs a manipulator, a conveyor or a sensor usually adopts it for everything.
- Compare candidates per noun on a contact sheet rendered with `asset` at the size they will be used, and choose the silhouette that names the object.
- Use one family per figure; do not mix a stroke family with a fill family, or either with built-in `icon()` glyphs. One borrowed icon is acceptable when no other family has the word for it and the style and weight match.
- Families differ in vocabulary, not only in looks: at the time of writing Material has a manipulator and Lucide has no table, so the family is chosen by what the figure has to name.
- A line icon's weight is normalized by `sw` (1.5 px default, about 2 px from 36 px up). A solid icon carries its own weight, so at 60 px and above step down a weight (`material200`) instead of enlarging weight 400, which reads as a black blot.
- Sizes: 18 to 28 px beside a label, 36 to 48 px in a tile above its name, 60 to 110 px when the icon is the card's subject. Color from the role's deep tone, ink, or a neutral steel gray.
- An icon sits beside a label or above it and never replaces the label; do not put an icon on every card.
- Logos are trademarks: use one only for the product the figure names, prefer the mono variant, and keep it smaller than the module name.
- `asset` rejects scripts, stylesheets, event handlers, embedded documents, entities and external references, namespaces internal ids, and maps a literal black fill or stroke to `currentColor` so a solid icon tints like a line icon.
- Keep `assets/` with the build script: the SVGs, the copied `LICENSE-*.txt`, and `ASSETS.md` with each source URL.

## 5. Content grammar and honesty

- Thumbnails of the task scene belong in input, perception, and execution regions only.
- Data sketches (curves, bars, heatmaps, timelines, progress plots) must be labeled `schematic` when they do not plot real data.
- Plot real numbers only when the source states them; simple derived arithmetic (for example showing a stated 40% reduction as a 60% bar) is allowed and must stay traceable.
- Never invent results, dimensions, module names, or case details; when a case study is only described in words, draw a schematic and say so in the figure.
- A visual restyle must not change content; compare the label inventory before and after.
- Prefer a linked pair of dashed chips with the same color over a long arrow that would cross several cards.

## 6. Connector vocabulary

- Thin near-black arrow with a small filled head for the main flow.
- Dot plus short bus for fork and merge; color only the branch segments that carry an outcome.
- Dashed gray rounded arc routed inside panel gutters for closed loops and feedback, with a serif italic label on a white knock-out.
- Double-headed short arrow with a monospace label (for example `MSE`) for comparisons.
- Curly brace to group several inputs into one consumer.
- Vertical S-curves (`curve`) for a many-to-many mapping between two stacked layers: straight where the ports line up, a smooth S where they do not, never an orthogonal elbow that would overlap its neighbours.
- Diamond or two-segment pill only for an explicit decision; label branches in serif italic (`yes`, `no`) or monospace (`accept`, `override`).
- No connector may cross a label; move the label or reroute, then rerun QA.

### 6.1 Geometry: compute the grid, anchor every wire

Tidiness is what separates a drawn figure from a typed one, and it is mechanical, so let the kit compute it instead of typing coordinates.
Published figures read as tidy because equivalent things share an edge, peers share a gap, and every wire starts and ends exactly on a box.

- Derive the grid with `cols`, `rows` and `place` instead of hand-typed x and y values, so columns, rows and gutters are exact by construction and a later edit cannot drift by a pixel.
- Give boxes that belong to one row the same height, and boxes that belong to one column the same width; a 2 px difference between two cards in the same row is visible and is what the gate reports as `misalign`.
- Anchor every arrow with `connect`, `bus`, `arc` or `route`, which take container ids and compute the ports; a hand-typed path is only acceptable for a wire that starts at a brace, a sketch or a circled step, and then it should still end on a port from `port()`.
- `connect` draws a straight line when the two ports line up and an orthogonal elbow otherwise; pass `ta=None` or `tb=None` to let one end follow the other box's port, which is how a tall container meets a short card head-on.
- Use `bus` for one source feeding several targets (a stem, one trunk, one arrow per target) rather than several long arrows leaving the same edge.
- Use `arc` for a short feedback bend and `route` for a feedback path that has to wrap around content through a reserved lane; keep the lane in a gutter or inside the panel's padding, never over a card.
- Register an invisible `zone` when a row has no card of its own (a numbered step, a label column), so its connectors are anchored like everything else.
- Give the arrowheads of parallel relations the same fractions along the shared edges (`ta`, `tb`), so a bundle of edges stays parallel and evenly spaced.
- Curves are allowed, straight lines are allowed, but overlapping wires and ends that miss their box are not; `--strict-tidy` turns those into failures.

### 6.2 Local structure: row lines, halves and straight cross-band wires

Symmetry is not only equal widths; it is every peer card agreeing on where its content starts and stops.

- Give each band named row lines and make every card in the band snap to them: one title baseline, one content top, one content bottom, and in a row of tiles one icon band and one name band. When one card's last element ends 14 px above its neighbours', the row reads ragged even if every box is aligned.
- Treat a card holding a different kind of content the same way: in a row of icon-over-name tiles, a card with a sketch puts the sketch in the icon band and its names in the name band.
- When two things share a card, split its inner width into equal halves (or thirds) with `place`, and centre each caption under the thing it names; 124 px beside 116 px reads as a mistake.
- Before drawing wires between bands, check that each can run straight: the source and target cards must overlap in x, or the gutter a wire climbs through must fall inside its target. If a wire needs a jog, move the column edges first; two jogs meeting in a 24 px gutter end in a crossing or a 6 px arrow.
- Two feedback labels that describe the same kind of flow sit on one line, not wherever each wire's midpoint happens to be.
- A relation label between two stacked chips needs a gap of about 26 px: a serif line box is about 1.5 em tall even when its ink is half that. Keep the row pitch equal across the thumbnail rather than widening one gap.
- Every label keeps at least 3 px of clear space, measured on its ink, from any shape or stroke it does not sit in; the gate's `crowded` check reports the offender and its coordinates.
- In a band of titled cards, run the band's row line through the centre of the space under the titles, not through the middle of the card, so chips, marks and the wires that meet them share one line; a group label without a card of its own (memory over two cylinders) sits on the card titles' baseline.
- When two cards are stacked in one panel, give their contents shared columns: an arm over "done" and the next frame over "retry" line up, and the wire from the frame lands straight above what it feeds.
- Inside a frame cut into patches, snap the scene to the grid: `f.cells(x, y, w, h, rows, cols)` returns each patch's centre and size, so the table edge or horizon sits on a patch boundary and every object is centred in one patch; objects placed at 22 and 58 percent of the width look random once grid lines are drawn over them.
- Centre a tag (camera icon plus symbol) over its frame by the width of the whole group, and centre a block of example lines in its card by its measured width (monospace is 0.6 em per character); a block pinned 14 px from the left leaves 21 px on the right.
- Measure an icon's ink before centring it on a row line: Material glyphs fill about two thirds of their box and sit slightly above centre, so a centred box can leave the drawing off the line.
- Never place an icon by hand-typed offsets next to text: compute its x from the label's measured width and its y from the label's line. A camera typed in at a fixed x beside "arm · camera" ended 7 px from the text and floated between the title and subtitle lines, and since the subtitle already said camera it was removed.
- A label on a lane that runs under several panels sits inside one panel, placed with `route(..., label_at=x)`; centred on the whole lane it can land on a panel edge, which the gate reports as `straddle`.
- Labels that sit on a bus or strip (message pills on a message bus) go in the gaps between the wires that tap it, never under a tap.

### 6.3 Layered hierarchies

A hierarchy of layers (goal, sub-goals, sub-graphs, contracts, policies) reads best as full-width bands stacked top to bottom with a schema column on the left.

- Put each layer's name in its band and each relation between two layers (verb plus cardinality, such as `reference n : 1`) in the gap between the bands, with the cardinalities in one column.
- Put the instances on shared columns to the right: every child centred under its parent, a shared target centred under the pair that references it, and each policy under a contract; `examples/example_hierarchy.py` does this.
- Show a cardinality with the smallest instance that proves it: two sources on one target for `n : 1`, and for `n : m` one target with two sources plus one source with two targets.
- Draw the mappings with `curve`, spread a box's ports (0.2, 0.5, 0.8) when it takes several wires, mirror the ports between the two halves, and order the boxes until no two wires cross.
- Pick the instance count that makes the spacing come out even: two sub-graphs put three shared contracts on equal spacing where three sub-graphs could not.
- A figure kept deliberately sparse may sit below the coverage floor; first narrow the canvas and keep the type size with `Fig(w, h, print_width_pt=516 * w / 1400)`, then relax `--min-coverage` and report the measured value.

## 7. Workflow

1. Write the content inventory: inputs, stages, contribution, outputs, every label and number, and which parts may only be schematic.
2. Sketch the column grid in numbers: canvas size, panel x-ranges, row y-ranges, card rectangles.
3. Start each figure with `scripts/scaffold.py`, then write one build script per figure with the vendored `figkit.py`; keep coordinates explicit and grouped by panel.
4. Run `python scripts/qa_svg_figure.py <figure>.svg --png`.
5. Fix every reported issue, then open the PNG and inspect it at 100 percent and in crops around dense cards, math, and connectors; confirm serif and monospace labels really render in those families.
6. Repeat until QA passes and the visual inspection finds no P0 or P1 defect; perform at least three cycles for a user-critical figure.
7. Deliver the build script, `figkit.py` version in use, SVG, and 2x PNG together.

## 8. QA gate and its limits

The gate fails on any of: text overflowing its container or the canvas, text collisions, partially overlapping sibling boxes, a label hidden under a card or chip drawn after it (`textCovered`), strokes crossing uncovered labels, labels that print below 6 pt, labels longer than six words outside example content, more label words than the canvas budget, or coverage below the threshold.
Every limit has a flag (`--min-pt`, `--print-width-pt`, `--max-words`, `--words-per-10k`, `--min-coverage`); relax one only deliberately and report why.
The gate also prints a geometry report (`tidy`) that measures what "tidy" usually means by eye: connector ends that stop short of a box edge or die inside one (`edgeGap`), wires crossing a card they do not attach to (`edgeThroughBox`), collinear wires lying on top of each other (`edgeOverlap`), peer boxes whose edges or centers nearly line up but miss (`misalign`), and centered labels that sit off-center in their chip (`offCenter`).
`--strict-tidy` turns those five into failures, together with `sketchOverflow` (a curve, glyph, icon or bar that belongs to a card but crosses its edge), `straddle` (a card, chip or wire label that sits half inside a panel) and `crowded`, a label within 3 px of a shape or stroke it does not sit in (measured on the ink, so a serif line box does not count against its neighbours), and is the right setting for a figure that goes into a paper.
Connector crossings, uneven gaps in a run of peers (`gapUneven`), the median text share of cards, and near-empty cards are printed but never fail, because a column keyed to rows of different heights and a deliberate crossing are legitimate.
Peers in these checks are boxes of the same kind inside the same container, so nested groups and separate columns are never compared with each other.
Two exemptions keep the geometry checks honest: a wire end that sits on another wire at a T junction is a fork, not a miss, and a card drawn after a wire with an opaque fill is a knock-out, not an obstacle.
QA cannot judge semantics, arrow direction, icon fit, misleading sketches, font fallback, or aesthetic balance, so the rendered PNG must still be inspected.
Link every text element to its container with `box=` so overflow is checked; freestanding labels are still covered by the collision and line checks.

## 9. Pitfalls observed in practice

- A `text{font-family: ...}` rule inside the SVG `<style>` overrides per-element `font-family` attributes, so serif and monospace labels silently fall back to sans; set the default family on the root `<svg>` instead, as figkit does.
- Heuristic text widths are only estimates; accept a layout only after the browser measurement passes.
- A `text` element with `text-anchor="middle"` stays centered only while its tspans use relative `dy`/`dx`; absolute `x` on a tspan starts a new chunk.
- Serif math glyphs have tall bounding boxes; give large focal symbols about 1.2 times their font size of vertical clearance, and give connector labels a knock-out at least 21 px high.
- A subscripted symbol such as $t_1$ or $\pi_{0.5}$ overflows a chip shorter than about 1.9 times its font size; at `fs("label")` use chips at least 36 px tall.
- Full-width layer bands with a header column of descriptions, a notes column and a legend strip of meanings look like documentation even when every check passes; use titled group containers and move the prose to the caption.
- Raising coverage by adding notes, legends or extra cards makes a figure denser but less like a paper figure; fill space with imagery, examples or larger type instead.
- `scene()` keeps its own 4:3 artwork, so a much wider frame shows empty side bars; keep scene frames near 4:3 or use a real image with `fit="cover"`.
- Outlining every step of an example path in black removes the single focal point; emphasize one module.
- A connector that must cross another connector should break the secondary (dashed feedback) line for a few pixels at the crossing rather than hide the primary flow.
- An arrow that crosses a panel gutter must be drawn after both panels; otherwise the later panel's fill hides the arrowhead.
- A label pill centered on a short connector hides the line and its direction; place the pill beside the connector instead.
- Write primes as `a'_t` rather than as a superscript command, so the subscript attaches correctly.
- Unbraced scripts such as `E_\theta` must consume the whole command; figkit handles this, and a regression test covers it.
- Card-bottom chip rows reserve space; sketches placed above them must end at least 6 px earlier.
- Curves in schematic plots often cross their own annotations; place annotations in empty plot regions and use a short leader arrow when needed.
- Gradients, uppercase tracked headers, saturated filled badges, and decorative UI icons are the fastest way to make a figure look machine-generated.
- A decorative element that looks like data invites misreading; either make it schematic and labeled or remove it.
- A hand-drawn glyph (a robot arm from strokes, a room from rectangles, a gripper from three lines) can pass at 11 px and read as crude at print size; use a vendored icon for every recognizable object, product or action, and keep hand drawing for data sketches (curves, bars, strips, graphs, plots).
- Icons carry the figure at 36 to 104 px too, with the display stroke raised to about 2 px; tint them with the role's deep color or a neutral steel gray.
- Leave at least 12 px between an icon, thumbnail or sketch and the next label; at print size a 4 px gap reads as touching, which is the fastest way to make a figure look unfinished.
- A row of primitives (tokens, bars, a strip) must be computed from its card's inner width instead of a pill count times a guessed width; figkit registers the token row so an overhang is reported rather than drawn over the card's edge.
- A math label's line box is about 1.6 times its font size, so two stacked symbols need about 28 px at label size; a symbol placed beside its name usually beats a symbol stacked inside a small plot frame.
- Tabler sets `stroke-width="2"` on a 24 px grid, which renders thinner at 16 px and heavier at 32 px; place icons with `asset` so the display stroke stays constant.
- LobeHub color variants carry brand gradients that clash with a muted palette; use the mono variant tinted with ink.
- A hand-drawn glyph next to a vendored icon of the same kind reads as two styles; replace the whole row.

## 10. figkit API summary

| Call | Purpose |
|---|---|
| `Fig(w, h, print_width_pt=None)` then `save(path)` | canvas, defs, and output; print width defaults to 516 pt for canvases at least 1000 px wide and 252 pt otherwise; pass `516 * w / 1400` to keep the 1400 px type sizes on a narrower canvas |
| `fs(role)` | print-size font in px for `min`, `label`, `module`, `title`, `hero` |
| `panel(x, y, w, h, role, title, sub=None, dashed=False, sub_below=False)` | flat stage panel; returns the content top y; `title=None` for a headerless strip |
| `card(x, y, w, h, role, stack=0, key=False, fill=None, stroke=None, dashed=False)` | pastel or white card; returns an id for `box=` |
| `example(x, y, w, h, role=None, fill=None, stroke=None, dashed=False)` | card for verbatim prompts, code and traces; its labels are exempt from word limits |
| `image(path, x, y, w, h, fit="cover", r=3, frame=HAIR)` | embed a PNG, JPEG or WebP render or photo (up to 8 MB) as a data URI with a thin frame |
| `chip`, `badge`, `pill`, `step` | small labeled containers, quiet number tags, connector labels, circled step numbers |
| `text(x, y, s, size, weight, color, anchor, box=id, family="sans", italic=False)` | rich text with `$math$`; `family` is `sans`, `serif`, or `mono` |
| `layer_stack(x, y, w, h, n, role, s, repeat)` | a deep network as n stacked layers; returns a box of full width and front-face height, and leaves the front in `f.stack_front` |
| `feature_maps(x, cy, [(thickness, side), ...], role)`, `cuboid(x, y, w, h, d, role)` | convolutional feature maps and tensors with depth |
| `mlp(x, y, w, h, layers, role)` | node-link diagram of a fully connected network |
| `token_grid(x, y, rows, cols, role, masked, highlight)`, `vector(x, y, n, role)` | token or patch embeddings, and one embedding |
| `patch_grid(x, y, w, h, rows, cols, masked, content)`, `heatmap(x, y, rows, cols, role)` | an image cut into patches over drawn content, and an attention map |
| `Fig.cells(x, y, w, h, rows, cols)` | returns `cell(r, c) -> (cx, cy, cw, ch)`, the centre and size of each patch, for snapping a scene to its grid |
| `tokens`, `trapezoid(direction=up/down/left/right, dashed)`, `bracket`, `cylinder`, `bubble`, `block_arrow` | shapes with meaning (section 4.4); a `right` trapezoid is an encoder in a left-to-right flow, a dashed one an EMA copy |
| `cols(x0, x1, n, gap)`, `rows(y0, y1, n, gap)` | n equal columns or rows with equal gaps, snapped to whole pixels |
| `place(x0, x1, widths, gap=None)` | x positions for a run of given widths: equal gaps, run centered |
| `zone(x, y, w, h)` | invisible rectangle registered for layout and ports (a step row, a reserved lane) |
| `rect(id)`, `port(id, side, t=0.5, out=0)` | a container's rectangle, and an exact point on one of its edges |
| `connect(a, b, sides=None, ta=.5, tb=.5, mid=None, label=None, knockout=False)` | anchored arrow: straight when the ports line up, else an orthogonal elbow; `ta=None` follows the other box |
| `bus(src, targets, side="bottom", at=None)` | stem plus one trunk plus one arrow per target |
| `arc(a, b, sides=None, bulge=40, label=None)` | one quadratic feedback bend; the label sits outside the bend |
| `curve(a, b, ta=.5, tb=.5, up=False)` | vertical S-curve between two stacked layers, straight when the ports line up; for many-to-many mappings |
| `route(a, b, lanes, sides=None, label=None, label_seg=None, label_at=None)` | orthogonal feedback path that wraps through reserved lanes; `label_at` centres the label at an x (or y) on its segment |
| `arrow(d, color=WIRE, dashed, start, end, open_)`, `line`, `dot`, `brace` | raw connectors for wires that start at a brace or sketch |
| `scene(x, y, w, h, frame)` | schematic tabletop thumbnail |
| `bars`, `curves`, `strip` | schematic data sketches |
| `asset(path, x, y, size, color, sw=1.5)` | vendored open-source SVG icon or logo as a shared symbol with a QA box |
| `icon(name, x, y, size, color)` | built-in line glyph; offline fallback when no vendored icon fits |

See `examples/example_pipeline.py` for a complete figure that exercises the visual language and passes the QA gate.
