"""Example: a layered hierarchy - goal, sub-goals, skill sub-graphs, contracts and policies.

A minimal schema figure (symbols only) that passes `qa_svg_figure.py --strict-tidy --min-coverage 0.2`;
the coverage floor is relaxed on purpose because the figure is kept sparse.
Goal g decomposes into sub-goals s_k, a high-level function layer; a failed sub-goal can only be replanned.
Each sub-goal owns exactly one skill sub-graph G_k (1 : 1) whose skill nodes are linked by relations such as
fallback and alternative. Every node references exactly one contract, and one contract can be referenced by many
nodes (n : 1). Policies execute contracts: one contract can be executed by several policies and one policy can
execute several contracts (n : m).

Structure. The left column is the schema (layer names, and each relation with its cardinality in the gap between
two layers); the instances sit on shared columns to its right: every sub-goal is centred over its sub-graph, every
policy under a contract, and each contract under the node or the pair of nodes that reference it. With two
sub-graphs the three contracts fall on equal spacing, the figure is mirror-symmetric and no two wires cross.
The canvas is 1060 px wide and prints at 391 pt, so type keeps the sizes of the 1400 px figures.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from figkit import INK, MUTED, PAL, WIRE, Fig, text_w

OUT = HERE / "example_hierarchy.svg"

W = 1060
BAND_H = (68, 68, 120, 68, 68)  # goal, sub-goals, skill sub-graphs, contracts, policies
GAP, TOP = 40, 8
H = TOP * 2 + sum(BAND_H) + GAP * (len(BAND_H) - 1)
f = Fig(W, H, print_width_pt=516 * W / 1400)  # same type sizes as a 1400 px text-width figure
MODULE, LABEL, SMALL = f.fs("module"), f.fs("label"), f.fs("min")
LOOP = "#7A7A7A"
G_, S_, N_, C_, P_ = (PAL[k] for k in ("gray", "amber", "purple", "green", "blue"))

# ---------------------------------------------------------------- grid
BAND_Y = []
y = TOP
for h in BAND_H:
    BAND_Y.append(y)
    y += h + GAP
MID = [by + h / 2 for by, h in zip(BAND_Y, BAND_H)]
GRAPH_W, GRAPH_GAP = 360, 28
X0 = 216  # instance columns start here; the schema column sits to the left
X1 = X0 + 2 * GRAPH_W + GRAPH_GAP
LABEL_X = 8 + 16
LANE_X = (X1 + W - 8 - 16) / 2  # replan lane in the bands' right margin

GRAPH_X = [X0, X0 + GRAPH_W + GRAPH_GAP]
GRAPH_MID = [x + GRAPH_W / 2 for x in GRAPH_X]
NODE_X = [x + GRAPH_W * q for x in GRAPH_X for q in (0.25, 0.75)]
CONTRACT_X = (NODE_X[0], (NODE_X[1] + NODE_X[2]) / 2, NODE_X[3])  # equally spaced
CHIP_W, CHIP_H, NODE_D = 120, 40, 44


def chip(cx, cy, s, role, w=CHIP_W):
    R = PAL[role]
    return f.chip(cx - w / 2, cy - CHIP_H / 2, w, CHIP_H, s, size=MODULE, fill=R.tint, stroke=R.accent, color=R.deep)


# ================================================================ layers and the schema column
LAYERS = ("Goal", "Sub-goals", "Skill sub-graphs", "Contracts", "Policies")
RELATIONS = (("decompose", "1 : n"), ("map", "1 : 1"), ("reference", "n : 1"), ("execute", "n : m"))
for by, h, name, mid in zip(BAND_Y, BAND_H, LAYERS, MID):
    band = f.panel(8, by, W - 16, h, "gray", None)
    f.text(LABEL_X, mid + 7, name, size=MODULE, weight=700, color=INK)
CARD_X = LABEL_X + max(text_w(v, SMALL) for v, _ in RELATIONS) + 12  # cardinalities share one column
for k, (verb, card) in enumerate(RELATIONS):
    gy = BAND_Y[k] + BAND_H[k] + GAP / 2 + 6
    f.text(LABEL_X, gy, verb, size=SMALL, color=MUTED, family="serif", italic=True)
    f.text(CARD_X, gy, card, size=SMALL, color=INK, family="mono")

# ================================================================ instances
goal = chip((X0 + X1) / 2, MID[0], "$g$", "gray", w=140)
subgoals = [chip(x, MID[1], f"$s_{k + 1}$", "amber") for k, x in enumerate(GRAPH_MID)]
f.bus(goal, subgoals, side="bottom")

# one sub-graph per sub-goal; its two skill nodes are linked by a relation
RELATION = ("fallback", "alternative")
G_Y, G_H = BAND_Y[2] + 16, BAND_H[2] - 32
nodes = []
for k, (gx, rel) in enumerate(zip(GRAPH_X, RELATION)):
    graph = f.card(gx, G_Y, GRAPH_W, G_H, fill="#FFFFFF", stroke=N_.accent, dashed=True)
    f.text(gx + 12, G_Y + 24, f"$G_{k + 1}$", size=LABEL, color=N_.deep, box=graph)
    f.connect(subgoals[k], graph, sides=("bottom", "top"), color=WIRE, sw=1.3, head=7)
    ny = G_Y + G_H / 2 + 8
    pair = [f.chip(NODE_X[2 * k + j] - NODE_D / 2, ny - NODE_D / 2, NODE_D, NODE_D, f"$n_{2 * k + j + 1}$", size=LABEL,
                   fill=N_.tint, stroke=N_.accent, color=N_.deep, r=NODE_D / 2) for j in (0, 1)]
    nodes += pair
    f.connect(pair[0], pair[1], sides=("right", "left"), color=N_.accent, sw=1.3, head=6.5, dashed=True,
              start=rel == "alternative")
    f.text(GRAPH_MID[k], ny - 10, rel, size=SMALL, anchor="middle", color=MUTED, family="mono", box=graph)

contracts = [chip(x, MID[3], f"$c_{m + 1}$", "green") for m, x in enumerate(CONTRACT_X)]
policies = [chip(x, MID[4], f"$\\pi_{p + 1}$", "blue") for p, x in enumerate(CONTRACT_X)]

# every node references exactly one contract; the middle contract is shared by a node of each sub-graph
REFERENCES = ((0, 0, 0.5), (1, 1, 0.25), (2, 1, 0.75), (3, 2, 0.5))
for n, c, t in REFERENCES:
    f.curve(nodes[n], contracts[c], tb=t)
# policies execute contracts, many to many: c1 and c3 have two policies each, pi2 serves all three contracts
EXECUTES = ((0, 0, 0.5, 0.5), (1, 0, 0.2, 0.8), (1, 1, 0.5, 0.5), (1, 2, 0.8, 0.2), (2, 2, 0.5, 0.5))
for p, c, tp, tc in EXECUTES:
    f.curve(policies[p], contracts[c], ta=tp, tb=tc, up=True)

# a failed sub-goal can only be replanned from the goal
f.route(subgoals[-1], goal, (LANE_X,), sides=("right", "right"), color=LOOP, sw=1.4, dashed=True, head=7,
        label="replan", label_seg=2, label_color=MUTED, label_size=SMALL, knockout=True)

f.save(str(OUT))
print(OUT)
