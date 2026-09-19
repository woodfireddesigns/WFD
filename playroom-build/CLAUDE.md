# Kids' Playroom Build — project context

Parametric 3D model + construction documents for a corner loft in a 13'6" x 13'5"
playroom with 8-foot ceilings. Hobbit-hole / woodland theme. Dimensional lumber and
stock hardware only.

**Phase 1 is the LOFT ONLY.** `BUILD_PLAYHOUSE = False` and `BRIDGE_BUILD = False`
in params.py. The playhouse and bridge code is intact and switched off, not deleted.

Two documents come out of this repo:
- `Playroom_Loft_Build_Manual.pdf` - LEGO-style, 14 steps, letter landscape. The one
  you build from. Amber = install this step, grey = already built.
- `Playroom_Build_Plans.pdf` - the dimensioned drawing set. The one you check against.

## The one rule

**`params.py` is the single source of truth. Never hard-code a dimension anywhere else.**

Change a number there and the Blender model, every drawing, every dimension string and
the cut list all move together. `geometry.py` derives all 84 framing members from it;
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
python3 blender/render_steps.py 1500 28   # [width] [samples] - the 14 manual steps
python3 blender/render_views.py 64 1700   # photoreal-ish views for reference
python3 blender/export_mobile.py    # USDZ for iPhone AR, mobile GLB
python3 plans/assembly_manual.py    # the LEGO-style build manual
python3 plans/generate_plans.py     # the dimensioned drawing set
```

`ONLY_STEP=6 python3 blender/render_steps.py 1100 18` re-renders a single step while
iterating. Freestyle outlines are what make the step images read as a manual, and they
are also why a full set takes ~35 minutes on 4 cores.

Blender runs headless as the `bpy` Python module. There is no GUI step in the pipeline.

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
- **The round door is framed in a SQUARE rough opening.** 30" x 30" R.O., with four
  router-cut plywood quadrants forming the 28" circle inside it. You never cut a curved
  stud. The 27" slab is 3/4" ply (~9 lb) - do not build it thicker, a toddler swings it.
- **The knee wall caps the door at 30".** 44" deck minus 3/4" ply minus a 5-1/2" joist
  leaves 37-3/4" of wall; plates, a header and a cripple eat the rest.

## Geometry note

The deck is a PENTAGON: two wall edges, then straight off the north wall, one 45-degree
diagonal, straight off the west wall. Interior angles 90/90/135/135/90.

That means exactly **two saw settings for the whole deck: 45 and 22.5 degrees**.
Faces are 30" / 42-7/16" / 30". Four tall posts plus one corner stub. 21.88 sq ft.

An earlier version used a true hexagon (six sides, 11.25-degree cuts, six posts). It
bought 0.5 sq ft and cost a third saw setting and a whole extra post. Simplicity won.
Do not "improve" it back into a hexagon.

## Layout

```
params.py                   every dimension
geometry.py                 member list + cut list
blender/build_model.py      builds the scene from geometry.MEMBERS
blender/render_views.py     photoreal-ish reference views
blender/render_steps.py     the 14 LEGO-style step renders (Freestyle outlines)
blender/render_fix.py       true plan + framing-only views
blender/export_mobile.py    USDZ + mobile GLB
plans/drawkit.py            drafting primitives (dimensions, leaders, fitted blocks)
plans/sheets_a|b|c|d|e.py   sheets A0-A12 of the drawing set
plans/generate_plans.py     assembles the drawing set
assembly.py                 the 14-step build sequence + per-step copy
plans/assembly_manual.py    assembles the LEGO-style manual
docs/higgsfield_prompts.md  photoreal render prompt library
exports/                    .blend .glb .usdz, the PDF, renders
```

## Conventions

- Inches everywhere. `frac()` in `plans/drawkit.py` formats to feet/inch/sixteenths.
- Room frame: X west->east, Y south->north, Z up. Origin at the southwest floor corner.
- The loft is in the northwest corner. The playhouse (off) would be northeast.
- Members are defined by start point, end point, cross-section and an up vector.
- Blender objects carry `stock`, `cut_length_in`, `end_cuts` and `note` as custom
  properties, so a part clicked in the viewport reports its own cut data.
- Sheet size is ANSI B (17 x 11) landscape.

## Not certified

Designed against CPSC Pub. 325, ASTM F1148 and the 16 CFR 1213 guardrail gap rule.
Tested against none of them, and not engineer-stamped. Stud spacing is assumed 16" O.C.
and must be verified on site.
