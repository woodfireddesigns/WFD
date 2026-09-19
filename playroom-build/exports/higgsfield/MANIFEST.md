# Higgsfield photoreal render set

Generated 2026-09-19 with `gpt_image_2_5`, each one driven by the matching Blender
massing render as an `image_references` input so the geometry matches the plan set.
Quality: high, resolution 2K.

These live in the Higgsfield account (michaeltdesh@gmail.com) and are viewable in the
Higgsfield gallery. The build container's network policy blocks the delivery CDN, so the
files could not be committed here — download them from the URLs below or from the gallery.

| # | View | Reference | Size | Job ID | URL |
|---|---|---|---|---|---|
| 1 | Hero — both structures + the crossing | `01_hero_iso.png` | 2688x1520 | `57e8b669-9d03-411d-a1fe-e1d4c3385f93` | https://d8j0ntlcm91z4.cloudfront.net/user_2zxtX3H4xIEOxGPpDYHwE9UX8pF/hf_20260919_032116_57e8b669-9d03-411d-a1fe-e1d4c3385f93.png |
| 2 | Loft three-quarter — apothecary corner | `02_loft_three_qtr.png` | 2336x1744 | `e3d72fea-017d-450a-a0dc-244872694f8d` | https://d8j0ntlcm91z4.cloudfront.net/user_2zxtX3H4xIEOxGPpDYHwE9UX8pF/hf_20260919_032116_e3d72fea-017d-450a-a0dc-244872694f8d.png |
| 3 | Playhouse front — Ranger's Outpost | `03_playhouse_front.png` | 2336x1744 | `e8518204-512b-4548-a9a7-8d56f9bcac4c` | https://d8j0ntlcm91z4.cloudfront.net/user_2zxtX3H4xIEOxGPpDYHwE9UX8pF/hf_20260919_032116_e8518204-512b-4548-a9a7-8d56f9bcac4c.png |
| 4 | From the doorway — wide | `06_from_doorway.png` | 2688x1520 | `a257d983-763c-4878-9504-d0bfdc4b57e1` | https://d8j0ntlcm91z4.cloudfront.net/user_2zxtX3H4xIEOxGPpDYHwE9UX8pF/hf_20260919_032116_a257d983-763c-4878-9504-d0bfdc4b57e1.png |

A first pass at 1K/low quality was also generated; the 2K set above supersedes it.

## Uploaded reference media IDs (reusable for 24h, then re-upload)

| Blender render | Higgsfield media_id |
|---|---|
| 01_hero_iso.png | `6d9ee934-c1e4-48dc-976b-39a5dff19f84` |
| 02_loft_three_qtr.png | `e94046ca-063a-4299-94af-7a567afb15c4` |
| 03_playhouse_front.png | `6aa61674-4abe-4b7e-8769-75c14ef4b9bc` |
| 06_from_doorway.png | `c40e9764-435b-4e5b-96ab-52fe200b3d34` |

## To generate more

`docs/higgsfield_prompts.md` holds the full prompt library, including two views not yet
run (`04_bridge_along`, `05_hobbit_door`) and a table of variation modifiers for night
shots, lifestyle shots with a child, and seasonal palette pushes.

Always attach the matching Blender render as the reference. Text-only prompts drift off
the built geometry immediately.
