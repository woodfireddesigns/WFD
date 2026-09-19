# Kids' Playroom Build — Loft, Playhouse & Rope Bridge

Parametric 3D model, construction plan set, and render pipeline for two indoor play
structures in a 13'6" x 13'5" playroom with 8-foot ceilings. Woodsy / hobbit-hole theme.
Dimensional lumber and stock hardware only.

**Designed to serve an 18-month-old and a four-year-old at the same time, in three
phases.** That constraint drove a redesign: the rope net guard, the bookshelf railing,
the rope handrails and the bridge all came out.

## Phases

| Phase | Age | What is in use | What keeps the little one out |
|---|---|---|---|
| 1 | 18 mo - 3 yr | Ground den + playhouse. Both at floor level. | The ladder is stored **off** the structure. Nothing to climb. |
| 2 | 3 yr + | Ladder hung, loft in use. | Self-closing gate at the deck. Ladder still pulls off at night. |
| 3 | 5 yr + (or when the youngest is 4) | Rope bridge. | Deferred. All provisions are already in the wall. |

Phase 3 is a two-hour job later: unscrew an 8-screw baluster panel, drill 8 holes, bolt
8 eye bolts, hang the net. The wall ledgers, the playhouse bay post and the net-header
blocking all go in during phase 1 so nothing finished has to be opened up.

## Three specs in the original brief are not buildable. This set fixes them.

| # | Brief said | This set uses | Why |
|---|---|---|---|
| 1 | Hobbit door R.O. 36-38" tall | **R.O. 26" W x 32" H** | 44" deck − 3/4" ply − 5-1/2" joist = 37-3/4" of wall. Minus plates, header and a cripple, 32" is what physically remains. |
| 2 | Knee wall studs 40-42" | **34-3/4"** | Same arithmetic. The wall dies at 37-3/4" and two plates eat 3". |
| 3 | Bridge span ~42" | **54" clear** | 162" wall − 60" loft − 48" playhouse = 54". Both structures are in corners, so neither can slide. |
| 4 | Rope net guardrail, 4-6" mesh | **2x2 balusters, 2.59-2.70" clear** | CPSC: any opening between 3.5" and 9" passes a small body and catches the head. A 4-6" mesh fails both probes. |
| 5 | Bookshelf built into the railing | **moved to the ground-level den** | A shelf in a guardrail is a ladder. A 4-year-old puts a foot on it and their centre of mass clears the 36" rail. |

### On the bridge: strength was never the problem

Two 42 lb kids with a 5x dynamic factor is 420 lb, 105 lb per anchor. A 3/8" forged
shoulder eye bolt is good for ~1000 lb in line, and the 3/8" lags into studs give ~587 lb
each in withdrawal. **Eight to eleven times the load.** What actually made it wrong for
this age range was 18" of width (a balance beam, not a bridge) and 4-6" net mesh sitting
in the head-entrapment window. The loft's bridge gate went from 20" to 24" so the future
bridge is a real 24" wide — which also grew the deck slightly, to 22.36 sq ft.

### Rope is decoration now

Tight spiral wraps on the posts, whipping on the rail ends. No spans, no slack, no loops.
A loose rope loop over 5" is a strangulation hazard under 3, so the ladder's rope
handrails became rigid 2x2 grab rails.

## Resolved hexagon geometry

A 45-degree chamfer of one corner produces a **pentagon**, not a hexagon: the two cut edges
come out collinear, so the middle vertex is not a corner. A true six-sided deck inside a
60 x 60 corner needs two 22-1/2 degree joints flanking one 45 degree joint.

| Vertex | u | v | Post |
|---|---|---|---|
| A | 0.000 | 0.000 | 4x4 x 37-3/4" (corner stub) |
| B | 60.000 | 0.000 | 4x4 x 80" — future bridge |
| C | 60.000 | 24.000 | 4x4 x 80" |
| D | 49.456 | 49.456 | 4x4 x 80" — rotated 45 deg |
| C' | 24.000 | 60.000 | 4x4 x 80" |
| B' | 0.000 | 60.000 | 4x4 x 80" — ladder |

Interior angles 90 / 90 / 157.5 / 135 / 157.5 / 90 = 720. Every miter is 11-1/4 or
22-1/2 degrees — both are detents on any 10" miter saw. Deck area 22.36 sq ft.
Six posts total, and both 60" wall runs stay full length for maximum ledger engagement.

## Layout

```
                    NORTH WALL  (162")
  +--------60"--------+------54" clear-----+-------48"-------+
  |   CORNER LOFT     |  (bridge: phase 3) |    PLAYHOUSE    |
  |   hex deck 44"    |   provisions only  |   floor-ceiling |
  |   post B  · · · · · · · 54" span · · · · · · · post WM   |
  |   den below       |                    |  ranger's post  |
  +-- ladder @ post B' — LIFTS OFF                           |
```

## Repository

```
params.py                   single source of truth — every dimension
geometry.py                 builds all 83 framing members + the cut list
blender/build_model.py      constructs the Blender scene from geometry.MEMBERS
blender/render_views.py     6 perspective + 4 orthographic views
plans/drawkit.py            drafting primitives (dimensions, leaders, fitted note blocks)
plans/sheets_a|b|c|d.py     the twelve sheets
plans/generate_plans.py     assembles the PDF
docs/higgsfield_prompts.md  reusable photoreal prompt library
exports/Playroom_Build_Plans.pdf
exports/playroom_build.blend
exports/playroom_build.glb
exports/renders/
```

Change a number in `params.py` and the model, the drawings, the dimensions and the
cut list all move together. Nothing is typed twice.

## Rebuild

```bash
pip install bpy==4.2.0 reportlab numpy
python3 blender/build_model.py      # .blend + .glb
python3 blender/render_views.py     # [samples] [width]
python3 plans/generate_plans.py     # the PDF
```

## Sheet index

| | |
|---|---|
| A0 | Cover, critical notes, sheet index |
| A1 | Overall room plan, wall anchor zones, stud layout |
| A2 | Loft deck framing plan, hexagon geometry, joist layout |
| A3 | Loft developed elevation — baluster guards, gate, removable panel |
| A4 | Knee wall section + full hobbit door template on a 2" grid |
| A5 | Removable ladder, hook and pin detail, ground-level den shelf |
| A6 | Playhouse plan, south elevation, roof framing |
| A7 | Bridge — DEFERRED. Provisions to install now, plus the load check |
| A8 | Cut list |
| A9 | Hardware schedule + Home Depot buy list with internet numbers |
| A10 | Reference model views |
| A11 | Technical orthographic views |

## Load path

Wall ledgers carry the load. Posts are secondary.

- **Loft** — two 2x6 PT ledgers (north and west walls), 3/8" x 4" lag + washer into every stud.
- **Playhouse** — NW and SE posts lag directly into wall studs; SW post on a Simpson ABU44Z base.
- **Bridge** — 3/8" x 6" eye **bolts**, through-bolted with a fender washer and a nylock nut,
  into 2x6 ledgers that are themselves lagged into a minimum of two studs. Never screw eyes.

Stud spacing is assumed 16" O.C. throughout. **Verify on site with a stud finder before
drilling any ledger.** These drawings are not engineer-stamped.

## Safety decisions baked into the model

Measured against the CPSC Public Playground Safety Handbook (Pub. 325), ASTM F1148 for
home playground equipment, and the 16 CFR 1213 bunk-bed guardrail gap rule. **Designed to
those rules, certified against none of them, and not engineer-stamped.**

- **Guard openings 2.59"-2.70" clear.** Nothing passes the 3.5" torso probe, and nothing
  sits in the 3.5"-9" head-entrapment window.
- **Guard height 36"** above the deck — top of the range, not the bottom.
- **2x4 toe board on edge** at deck level. No gap under the balusters, and kicked toys
  stay up top instead of landing on whoever is in the den.
- **The ladder lifts off.** Two pins, and the loft is unreachable. This, not the gate, is
  what keeps an 18-month-old out — any latch a 4-year-old can work, a toddler eventually works.
- **Self-closing gate** at the deck opening, swings inward, no lock.
- **Rigid 2x2 grab rails** on the ladder instead of rope. No slack rope anywhere.
- **Acorn nuts on every through-bolt end** a child can reach (CPSC protrusion rule).
- **2" gymnastics mat** under the ladder and open faces. 3/4" foam attenuates about a
  2 ft fall; the deck is 44".
- Hobbit doors get a magnetic catch — never a latch, never a lock. A child must be able to
  push out from the inside with no hardware.
- Acrylic only. No glass, including the apothecary jars — and the jars stay sealed or stay
  out until the youngest is 3, because acorns and dried botanicals are a choking hazard.
- Re-torque every lag at 30 days, then every 6 months.
