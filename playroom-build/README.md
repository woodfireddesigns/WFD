# Kids' Playroom Build — Loft, Playhouse & Rope Bridge

Parametric 3D model, construction plan set, and render pipeline for two connected
indoor play structures in a 13'6" x 13'5" playroom with 8-foot ceilings.
Woodsy / hobbit-hole theme. Dimensional lumber and stock hardware only.

## Three specs in the original brief are not buildable. This set fixes them.

| # | Brief said | This set uses | Why |
|---|---|---|---|
| 1 | Hobbit door R.O. 36-38" tall | **R.O. 26" W x 32" H** | 44" deck − 3/4" ply − 5-1/2" joist = 37-3/4" of wall. Minus plates, header and a cripple, 32" is what physically remains. |
| 2 | Knee wall studs 40-42" | **34-3/4"** | Same arithmetic. The wall dies at 37-3/4" and two plates eat 3". |
| 3 | Bridge span ~42" | **54" clear** | 162" wall − 60" loft − 48" playhouse = 54". Both structures are in corners, so neither can slide. |

A fourth tension is flagged on sheet A9: "Home Depot only" vs "commercial playground-rated
net." Home Depot does carry 500 lb polyester cargo netting, which satisfies both. Certified
ASTM F1487 equipment does not exist there — that one line item would have to leave the store.

## Resolved hexagon geometry

A 45-degree chamfer of one corner produces a **pentagon**, not a hexagon: the two cut edges
come out collinear, so the middle vertex is not a corner. A true six-sided deck inside a
60 x 60 corner needs two 22-1/2 degree joints flanking one 45 degree joint.

| Vertex | u | v | Post |
|---|---|---|---|
| A | 0.000 | 0.000 | 4x4 x 37-3/4" (corner stub) |
| B | 60.000 | 0.000 | 4x4 x 80" — bridge |
| C | 60.000 | 20.000 | 4x4 x 80" |
| D | 48.284 | 48.284 | 4x4 x 80" — rotated 45 deg |
| C' | 20.000 | 60.000 | 4x4 x 80" |
| B' | 0.000 | 60.000 | 4x4 x 80" — ladder |

Interior angles 90 / 90 / 157.5 / 135 / 157.5 / 90 = 720. Every miter is 11-1/4 or
22-1/2 degrees — both are detents on any 10" miter saw. Deck area 21.75 sq ft.
Six posts total, and both 60" wall runs stay full length for maximum ledger engagement.

## Layout

```
                    NORTH WALL  (162")
  +--------60"--------+------54" clear-----+-------48"-------+
  |   CORNER LOFT     |    ROPE BRIDGE     |    PLAYHOUSE    |
  |   hex deck 44"    |    net @ 44"       |   floor-ceiling |
  |   post B  -------------- 54" span ----------- post NW    |
  |   apothecary      |                    |  ranger's post  |
  +-- ladder @ post B'                                       |
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
| A3 | Loft developed elevation — all four open faces unrolled |
| A4 | Knee wall section + full hobbit door template on a 2" grid |
| A5 | Ladder + bookshelf guard |
| A6 | Playhouse plan, south elevation, roof framing |
| A7 | Rope bridge elevation, enlarged anchor detail, safety |
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

- Guard height 36" above the deck — the top of the 32-36" range, not the bottom.
- The bridge gets a top rope **and** a mid rope at 18", plus full-height side net panels.
  A single top rope 36" above a sagging net is not a guard.
- Hobbit doors get a magnetic catch, never a latch and never a lock. A child has to be able
  to push out from the inside with no hardware.
- Porthole and playhouse window are acrylic. No glass anywhere, including the "apothecary" jars.
- 3/4" interlocking foam under the full bridge span and 24" past each end.
- Re-torque every eye bolt and lag at 30 days, then every 6 months.
