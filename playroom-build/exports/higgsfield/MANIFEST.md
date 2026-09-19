# Higgsfield photoreal render set — PHASE 1 (current design)

Generated with `gpt_image_2_5`, each driven by the matching Blender massing render as an
`image_references` input so the geometry matches the plan set. Quality high, 2K.

These live in the Higgsfield account (michaeltdesh@gmail.com) and are viewable in the
Higgsfield gallery. The build container's network policy blocks the delivery CDN, so the
files could not be committed here — pull them from the gallery.

## Current set — 2026-09-19, phase 1

Baluster guards, no rope bridge, no bookshelf in the railing, removable ladder.

| # | View | Reference render | Job ID |
|---|---|---|---|
| 1 | Hero — both structures, bridge-ready wall between | `01_hero_iso.png` | `dda4c15d-2e27-4511-9aad-3a9705270677` |
| 2 | Loft three-quarter — baluster guard, gate, ladder | `02_loft_three_qtr.png` | `307752e5-f52c-46a5-b259-fe306938f936` |
| 3 | The den — floor level, toddler's eye height | `05_hobbit_door.png` | `236c918d-82fb-43b5-9d9b-2928be21b397` |
| 4 | From the doorway — wide | `06_from_doorway.png` | `23c83a67-ddca-4815-9154-bbf40b10ed0d` |

## Reference media IDs (valid 24h, then re-upload)

| Blender render | Higgsfield media_id |
|---|---|
| 01_hero_iso.png | `44475e7e-4ff8-4744-b079-f85095627be8` |
| 02_loft_three_qtr.png | `cd61557f-e289-4b25-bea3-b000668af31e` |
| 05_hobbit_door.png | `62653302-8669-4488-9988-0c0065acfc13` |
| 06_from_doorway.png | `b6fda7cf-feb1-40c8-b874-c2a2a9e73aaf` |

## SUPERSEDED — do not use

An earlier set (jobs `57e8b669…`, `e3d72fea…`, `e8518204…`, `a257d983…`) shows the
**original** design: rope net guardrails, a bookshelf built into the railing, and the
rope bridge. All three of those were removed for cause — see sheet A0 of the plan set.
Those images are still in the gallery. Delete them or label them clearly, because the
details they show are the ones the redesign exists to eliminate.

## To generate more

`docs/higgsfield_prompts.md` holds the prompt library, including a shared **geometry
block** that pins the balusters and forbids the removed elements. Always attach the
matching Blender render — text-only prompts drift off the built geometry immediately,
and here that means rendering an unsafe detail as if it were approved.
