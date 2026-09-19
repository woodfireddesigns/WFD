# Higgsfield renders — the Loft, pentagon + round door

## Read this before generating any more

**Never ask an image model for a plan, a diagram or a dimensioned drawing.** It returns
something that looks authoritative with invented numbers, which is worse than nothing.

| Job | Tool |
|---|---|
| Step-by-step build diagrams | `blender/render_steps.py` — rendered from the real model |
| Dimensioned drawings | `plans/generate_plans.py` — vector, derived from `params.py` |
| Finished hero / mood images | Higgsfield `gpt_image_2_5` — nobody builds from these |

## Current set — phase 1 loft, five-sided deck, true circular door

Reference for all three: `exports/steps/step_99_complete.png` (media_id
`7c24c450-534a-40da-9500-1580195de85b`, valid 24h).

| # | View | Job ID |
|---|---|---|
| 1 | Hero — finished loft, door ajar, daylight | `f65541d4-e97a-43e4-a32e-d112d592978c` |
| 2 | The circular door, close, low camera | `9f28df44-e219-48cb-80e8-165e659dea7c` |
| 3 | Night — lit only from inside the den | `c49aadfd-e5a0-41c5-92c2-a03bbdc166d9` |

The container's network policy blocks the delivery CDN, so these could not be committed.
Pull them from the Higgsfield gallery.

## SUPERSEDED — delete these

Every earlier set shows geometry that no longer exists: the hexagonal deck, the arched
door, the rope net guardrails, the bookshelf railing, the playhouse and the rope bridge.

Jobs: `57e8b669…` `e3d72fea…` `e8518204…` `a257d983…` `dda4c15d…` `307752e5…`
`236c918d…` `23c83a67…` and the 1K first pass before them.

## Generating more

`docs/higgsfield_prompts.md` carries the shared **geometry block**, which pins the
five-sided deck, the balusters and the true circle, and forbids everything removed.
Always attach a Blender render as `image_references`.
