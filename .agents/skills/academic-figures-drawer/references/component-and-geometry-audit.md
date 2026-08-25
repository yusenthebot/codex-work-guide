# Component Match And Geometry Audit

Use this contract for every non-trivial figure. It closes two gaps that a
normal Draw.io XML linter cannot close: whether a selected stencil actually
means the intended noun, and whether repeated geometry and connector clearance
are exact enough for a paper figure.

## 1. Component selection is a semantic decision

Native, Visio-derived, or bundled does not mean suitable. A component is
acceptable only when a reader can identify the intended noun from its
silhouette at manuscript scale and its visual language matches its neighbors.

For every important icon or component, shortlist at least three candidates:

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Semantic specificity | suggests another noun | generic category | exact intended noun |
| Silhouette match | misleading | recognizable with label | recognizable without label |
| Style coherence | different rendering genre | can be normalized | same family and stroke language |
| Paper-scale legibility | detail collapses | readable with effort | immediate at target width |
| Aspect fit | must be distorted | tolerable crop/padding | native ratio fits the slot |

Choose only a candidate scoring at least 21/25, with no criterion below 4.
`approximate` components are warnings and require a visible text label plus an
explicit approximation note. A `reject` component blocks handoff. When no
candidate passes, build a simple editable primitive instead of forcing a
nearby stencil into the role.

Record the decision in `component-audit.md` and machine-checkable facts in
`figure-contract.json`. The rejected candidates matter: they prove that the
first search result was not accepted automatically.

## 2. Preserve intrinsic geometry

- Never stretch a recognizable object to fill a slot. Preserve its native
  aspect ratio or use a documented expected range.
- Compare optical size, not only bounding-box size. Thin line icons may need a
  slightly larger box than filled icons, but their perceived weight must match.
- Repeated components must share the same icon box, label baseline, internal
  padding, stroke width, and color treatment unless semantics require a stated
  exception.
- Tiny stencil details that disappear at paper width are defects. Replace the
  stencil with a simpler primitive; do not enlarge an ornamental detail until
  it competes with the scientific content.

## 3. Dimension contract

Repeated rows and columns must be declared in `figure-contract.json`, not
eyeballed. Supported checks include:

- equal width and height;
- aligned left/right/top/bottom/center axes;
- equal horizontal or vertical gaps;
- minimum non-overlap clearance;
- containment inside a declared panel;
- grid snapping for deliberately mechanical layouts.

Default tolerance is 1 px for exact groups and 2 px for optical groups. A
larger tolerance must be justified in `visual-spec.md`.

## 4. Penetration and routing contract

An edge penetrates a component when any segment enters the bounding rectangle
of an unrelated obstacle, including text and icons. Touching an obstacle after
expanding it by the declared clearance also fails.

- Declare high-risk edges and their obstacle set in `figure-contract.json`.
- Give high-risk orthogonal routes explicit waypoints. Auto-routing is not
  auditable from XML and therefore cannot prove a no-penetration claim.
- Endpoint components are ignored only for their own edge. All other boxes,
  labels, icons, divider text, and panel boundaries remain obstacles when
  declared.
- Inspect arrowheads after export. Static geometry can prove clearance but not
  every renderer-specific arrowhead or z-order artifact.

### 4.1 Mandatory global zero-overlap policy

Handpicked route obstacles do not prove that the rest of a diagram is clean.
Enable `global_routing` on every non-trivial figure. The validator automatically
uses every declared semantic component as an obstacle, including `container=1`
skill cards, and audits the complete semantic edge list against:

- all unrelated component boxes plus their minimum 8 px keep-out margins;
- freestanding signal, relation, and annotation labels listed as additional obstacles;
- the actual four border segments of relevant semantic group containers;
- perpendicular entry/exit through each connector's own source and target ports;
- strict orthogonal geometry with explicit waypoints for every semantic edge;
- intersections, shared collinear segments, and a minimum 12 px separation
  between parallel routes.

Plan the channels before finalizing component placement. A channel containing
`n` parallel centerlines requires both obstacle keep-out margins plus
`(n - 1) × edge_clearance`; expand the layout whenever that channel cannot fit.
A visible or machine-detected connector overlap is P0 and blocks delivery.

## 5. Required commands

Run the semantic/geometry contract before rendering and again after the final
XML change:

```bash
python3 <skill-dir>/scripts/validate_figure_contract.py \
  <figure>.drawio --contract figure-contract.json --strict
```

Then run the general visual and structural validators. Zero failures are
required. Contract warnings must be fixed or recorded in `defect-log.md`.

## 6. Minimal JSON shape

```json
{
  "version": 1,
  "components": [
    {
      "id": "robot_icon",
      "intended_noun": "industrial robot arm",
      "selected_candidate": "editable six-axis arm primitive",
      "match_grade": "exact",
      "visual_family": "two-tone engineering line",
      "scores": {
        "semantic_specificity": 5,
        "silhouette_match": 5,
        "style_coherence": 5,
        "paper_scale_legibility": 5,
        "aspect_fit": 5
      },
      "alternatives": [
        {"name": "PID loading arm", "rejected_because": "reads as a linkage"},
        {"name": "factory robot photo", "rejected_because": "breaks vector family"}
      ],
      "expected_aspect": [1.1, 1.7],
      "allowed_style_tokens": ["shape=robot_arm_v1"]
    }
  ],
  "dimension_groups": [
    {
      "name": "pipeline stages",
      "ids": ["stage_1", "stage_2", "stage_3"],
      "checks": ["equal_width", "equal_height", "align_top", "equal_horizontal_gap"],
      "tolerance": 1
    }
  ],
  "non_overlap_groups": [
    {"name": "stage row", "ids": ["stage_1", "stage_2", "stage_3"], "clearance": 8}
  ],
  "routes": [
    {
      "name": "feedback lane",
      "edge_ids": ["edge_feedback"],
      "obstacle_ids": ["stage_1", "stage_2", "stage_3", "feedback_label"],
      "clearance": 3,
      "require_explicit_waypoints": true
    }
  ],
  "global_routing": {
    "enabled": true,
    "exclude_edge_prefixes": ["legend_sample_"],
    "additional_obstacle_ids": ["feedback_label"],
    "boundary_ids": ["semantic_group"],
    "obstacle_clearance": 8,
    "edge_clearance": 12,
    "require_explicit_waypoints": true,
    "require_orthogonal": true
  }
}
```
