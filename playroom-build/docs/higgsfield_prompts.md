# Higgsfield Prompt Library — Kids' Playroom Build (phase 1)

Reusable, production-ready prompts. Paste as-is.
Model routing: `gpt_image_2_5` for photoreal and reference-driven edits.
**Always attach the matching Blender render from `exports/renders/` as the reference
image.** Text-only prompts drift off the built geometry immediately.

> **Phase 1 only.** No rope bridge. Guards are vertical balusters, not rope net.
> No bookshelf in the railing. Rope appears only as tight wrapping on posts.
> If you prompt for a rope net guardrail you will get renders that do not match
> the plans, and worse, that make an unsafe detail look approved.

---

## 0. Shared style block (prepend or paste inline)

```
Photoreal interior photography, 35mm, f/4, natural window light from camera left plus
warm practical lamplight inside the structures. Hand-hewn rough-sawn timber, visible
saw marks and grain, walnut and honey-amber wood tones, deep moss-green painted doors,
matte black forged iron hardware. Hobbit-hole / Lord of the Rings woodland craft
aesthetic. Warm, earthy, slightly cinematic grade. Gender-neutral, leaning adventurous
and boyish. Absolutely no pastels, no fairy lights, no glitter, no primary-color
plastic, no decals, no cartoon elements, no text.
```

## 0b. Shared geometry block (the part that keeps renders honest)

```
Guardrails are CLOSELY SPACED VERTICAL WOOD BALUSTERS, roughly 2.6 inches apart, with a
flat top rail and a solid kick board at deck level. NOT rope net, NOT rope mesh, NOT
horizontal cables. No shelves and no books built into any railing. No rope bridge and no
hanging rope anywhere. Rope appears only as tight spiral wrapping bound onto posts.
```

---

## 1. Hero — both structures
**Reference:** `01_hero_iso.png`

```
Convert this grey 3D massing render into a photoreal photograph of a finished
children's playroom, keeping the exact geometry, proportions and camera angle.

A 13'6" square playroom with 8-foot ceilings. In the far left corner, a raised timber
loft platform 44 inches off the floor with a six-sided hexagonal plank deck and five
rough-sawn 4x4 posts. Beneath the loft the base is fully enclosed with a low deep
moss-green painted plank wall containing a small round-top hobbit door with black iron
strap hinges and a round wood knob, glowing warm from inside, and a small round
porthole. A straight wood ladder climbs the near corner. In the far right corner, a
floor-to-ceiling 4-foot-square timber playhouse with a small peaked shingled roof, its
own round-top green hobbit door and a round porthole window above it, one corner post
spiral-wrapped in rope. The wall between them is bare except for a low timber ledger
band.

[shared geometry block]
[shared style block]
```

---

## 2. Loft three-quarter
**Reference:** `02_loft_three_qtr.png`

```
Photoreal close three-quarter view of the corner loft, exact same geometry and camera as
the reference. Hexagonal plank deck 44 inches up, ringed by closely spaced vertical wood
balusters with a flat top rail and a solid kick board at deck level. One baluster panel
on the near side is a hinged gate at the top of the ladder. A wool blanket and two
cushions on the empty deck. Below, the enclosed base in moss-green plank boards, with a
round porthole glowing warm amber and a low shelf of worn board books just visible
through the open hobbit door.

[shared geometry block]
[shared style block]
```

---

## 3. Playhouse — Ranger's Outpost
**Reference:** `03_playhouse_front.png`

```
Photoreal front view of the small timber playhouse, exact same geometry and camera as
the reference. Four-foot-square, floor to ceiling, shallow peaked roof with rough cedar
shakes and a dark rake board. A round-top deep moss-green hobbit door with two long
black iron strap hinges and a round wood knob, slightly ajar with warm lantern light
spilling out. A round window above the door with a black iron ring frame. The exposed
corner post is spiral-wrapped in thick natural rope, tight, no slack. Ranger's outpost
character: a small hanging iron lantern, a coil of rope on a peg, a wooden map tube.
Adventurous, not cute.

[shared geometry block]
[shared style block]
```

---

## 4. The den — floor level, the 18-month-old's room
**Reference:** `05_hobbit_door.png`

```
Photoreal low camera at a toddler's eye level, looking into the enclosed base of the
loft through its open hobbit door, exact same geometry and camera as the reference. The
door is a 24-inch-wide slab with a true semicircular arched top, faced in vertical
tongue-and-groove boards, painted deep moss green with brush texture showing. Two long
black forged-iron strap hinges, a round turned-wood knob. Inside: a small wool rug, two
low wood shelves of chunky board books, warm amber puck light, a round 8-inch porthole
in the side wall. Soft, cave-like, safe. A space a very small child would crawl into and
stay in.

[shared geometry block]
[shared style block]
```

---

## 5. From the doorway
**Reference:** `06_from_doorway.png`

```
Photoreal wide-angle view from the playroom doorway, exact same geometry and camera as
the reference. Both structures read at once. Late-afternoon warm light. A thick folding
gymnastics mat on the floor at the foot of the ladder, a soft wool rug, a basket of
wooden blocks, a small pair of boots. Lived-in, not staged, shot as if for an
architectural magazine feature on a family home.

[shared geometry block]
[shared style block]
```

---

## 6. Phase 3 — what the bridge WILL look like (not built yet)

Use `04_bridge_along.png` only if you regenerate it with `BRIDGE_BUILD = True`
in `params.py`. Label any output clearly as a future phase so it never gets mistaken
for the current build.

```
...a 24-inch-wide rope cargo net bridge spanning 54 inches between the loft and the
playhouse at 44 inches off the floor, mesh under 3.5 inches, taut top rope and
full-height rope side panels, galvanized forged eye bolts and thimbles at both anchors.

[shared style block]
```

---

## 7. Bulk variation modifiers

| Modifier | Use for |
|---|---|
| `Lit at night, only the warm practicals inside both structures, deep shadow.` | mood / bedtime |
| `Morning, cool daylight from the left, low warm fill.` | clean daytime |
| `Shot on 85mm, shallow depth of field, focus on the hobbit door.` | detail beauty shot |
| `A four-year-old mid-climb on the ladder, motion slightly blurred, face not visible.` | scale, phase 2 |
| `A toddler sitting inside the lit den, seen through the open hobbit door, face not visible.` | scale, phase 1 |
| `Ladder lifted off and standing against the wall behind the playhouse.` | showing phase 1 mode |
| `Heavier patina: worn paint on the door edges, scuffed deck, rope slightly fuzzed.` | realism pass |

---

## 8. Negative prompt

```
rope net railing, rope mesh guardrail, cargo net, rope bridge, hanging rope, slack rope
loops, horizontal cable railing, bookshelf built into a railing, books on the upper deck,
wide gaps between balusters, pastel colors, pink, lavender, fairy lights, glitter, tulle,
unicorns, rainbow decals, primary-color plastic, IKEA flatpack, molded plastic playset,
cartoon, CGI look, wall text, signage, watermark, warped geometry, floating furniture,
impossible joinery, glass jars, exposed fasteners at child height.
```
