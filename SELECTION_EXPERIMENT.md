# Erratum (2026-10-23), read first

The rule 54 numbers in Part B2 below are superseded. The defect detector used
there (non-ether 4-words, clusters with gap 2) flags each mover as two
fragments four cells apart, so movers were counted about twice, and its
tracker merged trains of movers. The exact replacements, with movers counted
cell by cell against the known ether, are in `code/rule54_exact.py`,
`rule54_phases.py`, `rule54_sparse.py` and `rule54_charge.py`, and in Section 5
of the article:

- each direction of motion has a single phase class in the uniform ether;
  every head-on collision of two single movers is mirror-symmetric and
  annihilates (so "five of seven torus collisions pass through" below is
  wrong: those were trains and double counts);
- the wall event is the same collision; trains lose all members at a wall;
- sparse launches without guns: box 0 movers in 90/90, ring keeps movers in
  46/90, all moving in one direction, N+ - N- conserved in 88/90;
- dense runs: guns sustain the population, ring 107 ± 9 movers vs box 94 ± 13,
  no significant difference.

The conclusion changes accordingly: the wall does not pick a collision phase
that the bulk avoids (the bulk has only that phase); the box drains movers
because a mirror-symmetric state is balanced.

# Do the walls select? An experiment (2026-10-22)

Hypothesis (from the functional-information discussion): by the reflection
principle a structure hitting a wall collides with its own mirror image, so a
box should act as a filter, removing structure types whose self-collision
annihilates and keeping those whose self-collision is elastic. If the rule
has several structure types with different self-collision outcomes, the box
population should drift toward the self-elastic types. That would be
differential persistence imposed by the environment, i.e. selection in the
sense of Wong et al.

Rule: 1-D, `u' = frac((u_{i-1}+u_i+u_{i+1})/3 + 0.398)`, nine-decimal
rounding. Scripts: `code/tracker.py`, `catalogue.py`, `catalogue2.py`,
`population.py`, `sparse_box.py`, `slowclass.py`, `slowclass2.py`,
`perstep.py`.

## 1. The structure zoo is almost a single type

Tracking active clusters on a 600-cell torus (steps 1000–4000, tracks of at
least 50 steps, 371 tracks):

| velocity (cells/step) | tracks | mean width |
|---|--:|--:|
| −0.15 … −0.05 | 204 | 3.5–3.7 |
| −0.05 … +0.05 |  19 | 7.2–7.6 |
| +0.05 … +0.15 | 148 | 3.5 |

So there is one dominant mover, speed 0.1 cells per step in either direction,
width about 3.5, and a rare slow/wide class (about 5 % of tracks, width about
7.5, mean lifetime 60 steps versus 105 for the movers), which looks like a
bound pair born in collisions. Structure count on the torus is steady
(43–48 on 600 cells).

## 2. The dominant type reflects elastically

A single random patch on a uniform background in a 200-cell mirror box emits
structures that travel to the walls and come back as V shapes
(`figures/sparse_mirror.png`); the cluster count stabilizes at 14, against 15
for the same patch on a torus (`figures/sparse_periodic.png`). The walls do
not remove movers.

## 3. Population size: torus and box agree

Three seeds, 400 cells, 20 000 steps, cluster counts at
t = 500, 1000, 2000, 4000, 8000, 12000, 16000, 20000:

- torus: 30.0, 26.3, 29.7, 31.3, 30.0, 30.0, 32.7, 28.7
- box:   30.7, 25.0, 26.0, 28.0, 30.3, 29.3, 30.3, 25.3

No decay in the box, no trend. Within noise the box carries the same number
of structures as the torus; if anything a few per cent fewer.

## 4. Population composition: a marginal difference, and a trap

Tracks with lifetime ≥ 50 steps whose mean position lies in the bulk (cells
50–350, same criterion in both geometries), five seeds, steps 3000–10 000:

| geometry | bulk tracks | slow/wide fraction | mean life slow | mean life fast |
|---|--:|--:|--:|--:|
| torus | 1826 | 0.061 (111) | 59 | 104 |
| box   | 1966 | 0.043 (85)  | 60 | 105 |

The slow fraction is lower in the box by a factor 1.4, about 1.8 standard
deviations: suggestive, not established. The lifetimes of both classes are
identical in the two geometries, which argues against the walls killing
either class; if the composition really differs, the likelier cause is a
lower birth rate of bound pairs, since pairs are born in collisions and the
box holds slightly fewer movers.

The trap: a fitted velocity classifies a reflection (a V-shaped track) as
"slow", and the periodic seam of the tracker splits structures at cell 0
into stubs that also look slow. Both artifacts pile up within five cells of
the ends (8.5 "slow" tracks per cell at the box walls, 4.2 at the torus
seam, against 0.3 in the bulk). Any claim that structures are born or die at
the walls must use a per-step measure, not fitted velocities. Section 5 does
that.

## 5. Per-step densities (no tracking)

Ten seeds, 400 cells, steps 3000–13 000, every step, bulk = cells 50–350.
A "wide" cluster has width ≥ 6 (this catches bound pairs and crossing blobs
alike; the point is that the same measure is applied to both geometries).

| geometry | clusters / cell / step | wide / cell / step | wide fraction |
|---|--:|--:|--:|
| torus | 0.0723 | 0.02937 | 0.4064 |
| box   | 0.0723 | 0.02948 | 0.4077 |

Identical to three significant figures. Within ten cells of the walls the
box has 0.0762 clusters per cell per step (5 % above the bulk, the
reflections pile up there) with a wide fraction of 0.36; the torus "ends"
show 0.094 and 0.30, which is the seam artifact and not comparable.

## 6. Verdict

The walls do not select in this rule. Three independent measurements agree:

1. The dominant structure (speed 0.1, width 3.5) reflects elastically; the
   wall collision is the same event as the bulk head-on collision of two
   opposite movers, which is also elastic (V shapes in both pictures).
2. Structure counts and per-step densities in the bulk of the box are
   indistinguishable from the torus (0.0723 vs 0.0723 clusters per cell per
   step; wide fraction 0.408 vs 0.406), and the mean lifetimes of both
   structure classes are the same in both geometries (60/59 slow, 105/104
   fast).
3. The marginal difference in tracked composition (slow fraction 0.043 vs
   0.061, 1.8 σ) is not reproduced by the per-step measure and should be
   regarded as noise or a tracking artifact.

Why the hypothesis fails here: selection by self-collision needs at least
two structure types with different self-collision outcomes. This rule has
essentially one mover whose self-collision is elastic, and a rare bound pair
whose lifetime is set by bulk collisions, not by the walls. The box is a
mirror and nothing more, which is what the article already states.

What would make the hypothesis testable: a rule with a genuine zoo of
gliders of different speeds and widths, where the outcome of a symmetric
head-on collision differs between types. Candidates are the one-dimensional
class-4 rules with several glider species (elementary rule 110 is the
classical example, with a dozen known gliders and tabulated collision
outcomes, though it is discrete rather than continuous), or Lenia-type
rules in two dimensions, where the symmetric four-body collision at a
corner is a second, independent filter. The experiment designed here
(sparse launch, population counts, per-step composition, torus vs box,
same seeds) transfers to those rules unchanged.


---

# Part B: elementary automata with a real glider zoo (2026-10-22, later)

Scripts: `code/eca.py` (rules on torus / mirror box, ether detection, tracker),
`eca_catalogue.py`, `eca_box.py`, `wall_scatter.py`, `eca54.py`, `single54.py`,
`decay54.py`, `collisions54.py`. Figures: `figures/rule110_*.png`,
`figures/rule54_*.png`.

Ether detection: a cell is a defect if the p-word centred on it is not one of
the background's words (p = 14 for rule 110, whose ether tile is
`11000100110111` with temporal period 7; p = 4 for rule 54, tile `1000`,
period 4). Species are classified by the fitted velocity of tracked defect
clusters.

## B1. Rule 110: the catalogue comes out right, but the wall is a source

On a 1400-cell torus the tracker recovers the known species by speed:
A (+2/3), B (−1/2), C (0), D (+1/5), E (−1/4), F (−1/9).

Rule 110 is not left-right symmetric, so the reflection principle does not
apply and the mirror wall is a new boundary rule, not a self-collision. What
it does (figures `rule110_defects_fixed.png`, `rule110_rightwall_raw.png`):

- The right wall is nearly ether-compatible: it hosts stationary C gliders
  and little else.
- The left wall is incompatible with the ether. It can be kicked, by an
  arriving glider, into a state that grows a different periodic background
  behind a front moving into the box at roughly 0.3–0.5 cells per step,
  emitting A gliders as it advances. Once nucleated the invasion is total:
  in one of two 1400-cell runs the ether fraction went from 0.90 at step
  5000 to 0.00 at step 8000; in the other it stayed at 0.96 through step
  8000. The event is stochastic in the seed, irreversible once started.
- Species composition in the bulk shifts accordingly: torus B 38 %, C 15 %,
  F 15 %, E 14 %, A 8 %; box A 48 %, B 15 %, E 15 %. The wall-scattering
  table (tracks within 40 cells of a wall) shows why: left wall, 15
  incoming (mostly F and E), 16 outgoing (13 of them A); right wall, 4 in,
  4 out. (Note 2026-10-24: these torus fractions came from an earlier
  `eca.defects`; the current code gives torus B 39 %, C 16 %, E 14 %,
  F 13 %, A 8 %, see `code/eca_box_110.txt` and `results/eca_box.txt`.
  No number of the article depends on them.)

So for an asymmetric rule the box does change the population, but by
emission from a wall that acts as a phase source and glider gun, not by
differential persistence. That is an environment, not a selector, and it
eventually destroys the medium the gliders live in.

## B2. Rule 54: the wall annihilates movers

Rule 54 is left-right symmetric, its ether tile `1000` is mirror-compatible
when the wall nodes sit on a `1` (box length 4k+1), and the reflection
principle holds exactly. Species on the torus from sparse launches: movers
w± at speed ±1 and stationary gutters g, plus rare slow composites.

**Single launches** (`single54.py`, `decay54.py`; one 8-cell random patch at
the centre of an ether-filled 401-cell box, or a 400-cell torus; seeds whose
patch forms a gutter gun, about one in three, excluded). Movers alive at
steps 60, 300, 600, 900, 1500, averaged over the eight non-gun seeds:

| geometry | 60 | 300 | 600 | 900 | 1500 |
|---|--:|--:|--:|--:|--:|
| torus | 2.25 | 1.25 | 1.25 | 1.25 | 1.25 |
| box   | 2.25 | 0.00 | 0.00 | 0.00 | 0.00 |

On the torus the emitted pair meets head-on on the far side at a random
relative phase; in five of seven seeds with movers both survive the
collision and live to the end of the run. In the box every mover dies at
its first wall contact, in every seed, and leaves nothing behind (defect
density at the walls after the event: 0.000).

**Dense runs** (`wall_scatter.py 54`, three seeds, 1401 cells, 6000 steps):
left wall 958 incoming movers, 32 outgoing; right wall 382 incoming, 0
outgoing. Of the roughly 1340 movers that reached a wall, 32 came back.

**Torus head-on collision outcomes.** The event detector in `collisions54.py` (both tracks end at the same place) only sees annihilations by construction, since a pass-through keeps both tracks alive, so it found 2 events, both annihilations, and says nothing about the rest. The single launches are the usable statistic: of the seven torus seeds with movers, five pass through their head-on collision and two annihilate.

**Mechanism.** By Theorem (reflection principle) a mover hitting the mirror
is a head-on collision of w+ with w− at the one relative phase that is
mirror-symmetric about the wall node. In rule 54 the outcome of a head-on
w+/w− collision depends on the relative phase; the symmetric phase
annihilates. On the torus the phase is random, so most collisions are
solitonic pass-throughs and the movers persist. The wall therefore removes
exactly one thing the torus keeps: every mover, at first contact. It does
this without any bulk effect, since the box and the torus are identical away
from the walls.

**Caveat on dense-run compositions.** The tracked species fractions in dense
runs (torus w− 42 % / w+ 26 %, box w− 25 % / w+ 49 %) are asymmetric in a
symmetric rule and therefore carry a tracker bias (crossing movers exchange
identities depending on scan order); they should not be quoted. The sparse
launches, the wall-scattering counts and the per-step densities do not
depend on identity continuity and are the evidence used above.

## B3. Verdict for Part B

In a symmetric rule with a glider zoo the hypothesis is confirmed in its
simplest form: the mirror wall is a selector, and it selects by the
self-collision outcome exactly as the reflection principle predicts. In
rule 54 the selection is total against movers (annihilation at the
symmetric phase) and neutral for gutters, so a box drains its mover
population at the rate at which movers reach the walls and keeps only the
stationary species, while the torus keeps both. In the vocabulary of Wong
et al. this is differential persistence imposed by the environment, with
"survive your own reflection" as the function; it is a one-shot filtering
toward a fixed survivor set, not open-ended ratcheting, because nothing is
copied or varied.

In the asymmetric rule 110 the walls are sources rather than filters, and
the question of selection is moot because the medium itself is eventually
replaced.

The next step, if the line is pursued: a rule with several mover species
whose symmetric-phase self-collisions differ (some annihilate, some
reflect), which would make the box select among movers rather than against
all of them. Rule 110 has the zoo but not the symmetry; rule 54 has the
symmetry but a single mover species. Two-dimensional Lenia-type rules have
both and add the corner as a second filter.
