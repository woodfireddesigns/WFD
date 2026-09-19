# Kids' Playroom Build — project context

Parametric 3D model + construction plan set for two indoor play structures in a
13'6" x 13'5" playroom with 8-foot ceilings. Hobbit-hole / woodland theme.
Dimensional lumber and stock hardware only.

## The one rule

**`params.py` is the single source of truth. Never hard-code a dimension anywhere else.**

Change a number there and the Blender model, every drawing, every dimension string and
the cut list all move together. `geometry.py` derives all 112 framing members from it;
the Blender scene and the PDF both read that same member list. If a number appears in
two places, that is a bug.

## Pipeline

```
params.py  ->  geometry.py  ->  blender/build_model.py   -> .blend / .glb
                            ->  plans/generate_plans.py  -> the PDF
```

```bash
./setup.sh                          # installs bpy 4.2 + reportlab (bpy is a 500 MB wheel)
python3 blender/build_model.py      # .blend + .glb
python3 blender/render_views.py 64 1700   # [samples] [width] - 6 perspective + 4 ortho
python3 blender/render_fix.py       # true plan + playhouse framing view
python3 blender/export_mobile.py    # USDZ for iPhone AR, mobile GLB
python3 plans/generate_plans.py     # the 13-sheet PDF
```

Renders take roughly 8 minutes for the full set on 4 CPU cores. Blender runs headless as
the `bpy` Python module; there is no GUI step in the pipeline.

## Design decisions that must not be quietly undone

These came out of a redesign to serve an 18-month-old and a four-year-old at once.
Each one exists for a reason written on sheet A0 of the PDF. Do not "restore" any of
them without saying why.

- **Guards are 2x2 balusters at 2.59"-2.70" clear, never rope net.** CPSC treats any
  opening between 3.5" and 9" as head entrapment. A 4-6" net mesh fails both probes.
- **No shelves in any guardrail.** A shelf in a guard is a ladder; a child puts a foot
  on it and clears the 36" rail. Books live on the floor-level den shelf instead.
- **Rope is decoration only.** Tight wraps, no spans, no slack. A loose loop over 5" is
  a strangulation hazard under 3.
- **The ladder lifts off.** That, not the gate, is the barrier that keeps an
  18-month-old off a 44" platform (CPSC caps toddler platforms at 32").
- **The bridge is deferred to phase 3.** Provisions install now; `BRIDGE_BUILD = False`.
  Strength was never the problem (8-11x margin). Width and mesh size were.
- **Hobbit door R.O. is 26" x 32".** It cannot be taller: 44" deck minus 3/4" ply minus
  a 5-1/2" joist leaves 37-3/4" of wall, and plates plus a header plus a cripple eat
  the rest.

## Geometry note

The loft deck is a true hexagon, not a chamfered square. A 45-degree chamfer of one
corner produces a pentagon — the two cut edges come out collinear. Two 22.5-degree
joints flank one 45-degree joint, giving interior angles 90/90/157.5/135/157.5/90.
Every miter is 11.25 or 22.5 degrees, both saw detents.

## Layout

```
params.py                   every dimension
geometry.py                 member list + cut list
blender/build_model.py      builds the scene from geometry.MEMBERS
blender/render_views.py     6 perspective + 4 orthographic views
blender/render_fix.py       true plan + playhouse framing view
blender/export_mobile.py    USDZ + mobile GLB
plans/drawkit.py            drafting primitives (dimensions, leaders, fitted blocks)
plans/sheets_a|b|c|d|e.py   sheets A0-A12
plans/generate_plans.py     assembles the PDF
docs/higgsfield_prompts.md  photoreal render prompt library
exports/                    .blend .glb .usdz, the PDF, renders
```

## Conventions

- Inches everywhere. `frac()` in `plans/drawkit.py` formats to feet/inch/sixteenths.
- Room frame: X west->east, Y south->north, Z up. Origin at the southwest floor corner.
- The loft is in the northwest corner, the playhouse in the northeast.
- Members are defined by start point, end point, cross-section and an up vector.
- Blender objects carry `stock`, `cut_length_in`, `end_cuts` and `note` as custom
  properties, so a part clicked in the viewport reports its own cut data.
- Sheet size is ANSI B (17 x 11) landscape.

## Not certified

Designed against CPSC Pub. 325, ASTM F1148 and the 16 CFR 1213 guardrail gap rule.
Tested against none of them, and not engineer-stamped. Stud spacing is assumed 16" O.C.
and must be verified on site.
