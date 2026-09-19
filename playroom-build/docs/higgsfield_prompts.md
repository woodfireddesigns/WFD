# Higgsfield Prompt Library — Kids' Playroom Build

Reusable, production-ready prompts. Every one is written to be pasted as-is.
Model routing: `gpt_image_2_5` for photoreal + reference-driven edits.
Always attach the matching Blender render from `exports/renders/` as the reference
image so the geometry stays true to the plans.

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

---

## 1. Hero — both structures and the crossing
**Reference:** `01_hero_iso.png`

```
Convert this grey 3D massing render into a photoreal photograph of a finished
children's playroom, keeping the exact geometry, proportions and camera angle.

A 13'6" square playroom with 8-foot ceilings. In the far left corner, a raised timber
loft platform 44 inches off the floor with a six-sided hexagonal deck, five rough-sawn
4x4 posts, and a knotted rope net guardrail on the two angled outer faces. Beneath the
loft the base is fully enclosed with a low painted plank wall containing a small round-
top hobbit door, deep moss green, black iron strap hinges, round wood knob, glowing
warm from inside. A straight wood ladder with thick rope handrails climbs the near
corner. In the far right corner, a floor-to-ceiling 4-foot-square timber playhouse with
a small peaked shingled roof, its own round-top green hobbit door and a round porthole
window above it, one corner post spiral-wrapped in rope. Between them, a rope cargo net
bridge crosses at platform height with a gentle sag, top and side rope netting.

[shared style block]
```

---

## 2. Loft three-quarter — the apothecary corner
**Reference:** `02_loft_three_qtr.png`

```
Photoreal close three-quarter view of the corner loft, exact same geometry and camera
as the reference. Hexagonal plank deck 44 inches up. A built-in shallow bookshelf is
integrated into one railing panel, filled with well-worn children's hardbacks and a few
small lidded amber plastic apothecary jars of dried leaves, acorns and pinecones with
handwritten paper labels. The adjacent railing panel is a knotted rope net. Rough-sawn
4x4 posts with visible grain. A wool blanket and two cushions on the deck. Warm amber
puck light glowing through a small round porthole in the enclosed base below.

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
spilling out. A round window above the door with a black iron ring frame and four
muntins. The exposed corner post is spiral-wrapped in thick natural rope. Ranger's
outpost / tinker's workshop character: a small hanging iron lantern, a coil of rope on
a peg, a wooden map tube. Adventurous, not cute.

[shared style block]
```

---

## 4. The crossing — bridge at eye level
**Reference:** `04_bridge_along.png`

```
Photoreal view looking along the rope bridge, exact same geometry and camera as the
reference. A 54-inch cargo net bridge spans between the loft platform and the playhouse
at 44 inches off the floor, with a natural 6-inch sag, thick natural-fiber poly rope,
four-inch mesh, full-height rope side panels and a taut top rope. Galvanized eye bolts
and thimbles at both anchors, bolted through visible timber headers. Interlocking dark
foam mat tiles on the floor beneath the span.

[shared style block]
```

---

## 5. Hobbit door — detail
**Reference:** `05_hobbit_door.png`

```
Photoreal tight detail of the child-scale hobbit door in the enclosed base of the loft,
exact same geometry and camera as the reference. A 24-inch-wide door with a true
semicircular arched top, faced in vertical tongue-and-groove boards, painted deep moss
green with the brush texture showing and the grain reading through. Two long black
forged-iron strap hinges with hammered edges. A round turned-wood knob. The door is open
a few inches; warm amber light and a small wool rug are visible inside. A round 8-inch
porthole nearby.

[shared style block]
```

---

## 6. From the doorway — what a kid sees
**Reference:** `06_from_doorway.png`

```
Photoreal wide-angle view from the playroom doorway, exact same geometry and camera as
the reference. Both structures and the rope bridge read at once. Late-afternoon warm
light. Soft wool rug, a basket of wooden blocks, a small pair of boots by the ladder.
Lived-in, not staged. Shot as if for an architectural magazine feature on a family home.

[shared style block]
```

---

## 7. Bulk variation modifiers

Append any one of these to generate a variant set from the same base prompt:

| Modifier | Use for |
|---|---|
| `Lit at night, only the warm practicals inside both structures, deep shadow.` | mood / bedtime shot |
| `Morning, cool daylight from the left, low warm fill.` | clean daytime |
| `Shot on 85mm, shallow depth of field, focus on the hobbit door.` | detail beauty shot |
| `Include a 5-year-old child mid-climb on the ladder, motion slightly blurred, face not visible.` | lifestyle / scale |
| `Autumn palette push: more amber and rust, cooler grey-green walls.` | seasonal |
| `Heavier patina: worn paint on the door edges, rope slightly fuzzed, scuffed deck.` | realism pass |

---

## 8. Negative prompt (paste into any model that takes one)

```
pastel colors, pink, lavender, fairy lights, glitter, tulle, unicorns, rainbow decals,
primary-color plastic, IKEA flatpack, molded plastic playset, cartoon, CGI look, wall
text, signage, watermark, warped geometry, floating furniture, impossible joinery,
extra posts, missing railings, glass jars, exposed fasteners at child height.
```
