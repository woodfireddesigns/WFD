# Higgsfield Prompt Library — the Loft (phase 1)

## What AI images are and are not for here

**Never generate a "plan" or a "diagram" with an image model.** It will return something
that looks like a beautiful technical drawing with completely invented numbers. That is
worse than no drawing, because it looks authoritative.

The split in this project:

| Job | Tool | Why |
|---|---|---|
| Step-by-step build diagrams | `blender/render_steps.py` | Rendered from the real model. Every part is where it will actually be. |
| Dimensioned drawings | `plans/generate_plans.py` | Vector, derived from `params.py`. |
| Finished hero / mood images | Higgsfield `gpt_image_2_5` | Nobody builds from these. They are for seeing it. |

Always attach a Blender render as the `image_references` input. Text-only prompts drift
off the built geometry within one generation.

---

## 0. Shared style block

```
Photoreal interior photography, 35mm, f/4, natural window light from camera left plus
warm practical lamplight from inside the den. Hand-hewn rough-sawn timber, visible saw
marks and grain, walnut and honey-amber wood tones, a deep moss-green painted door,
matte black forged iron hardware. Hobbit-hole / Lord of the Rings woodland craft
aesthetic. Warm, earthy, slightly cinematic grade. Gender-neutral, leaning adventurous
and boyish. No pastels, no fairy lights, no glitter, no primary-color plastic, no
decals, no cartoon elements, no text.
```

## 0b. Shared geometry block — this is what keeps renders honest

```
The deck is FIVE-SIDED: it runs straight off one wall, then one 45-degree diagonal
across the corner, then straight off the other wall. Not square, not hexagonal.
Guardrails are CLOSELY SPACED VERTICAL WOOD BALUSTERS about 3 inches apart, with a flat
top rail and a solid kick board at deck level. NOT rope net, NOT rope mesh, NOT
horizontal cables. No shelves or books built into any railing. No rope bridge, no
hanging rope. Rope appears only as tight spiral wrapping bound onto a post.
The door is a TRUE CIRCLE, about 27 inches across, set low in the wall under the deck,
with a small step-over sill at the bottom. Bag End, not an arched door.
```

---

## 1. Hero — the finished loft
**Reference:** `exports/steps/step_99_complete.png`

```
Convert this grey 3D massing render into a photoreal architectural photograph, keeping
the exact geometry, proportions and camera angle.

The corner of a child's playroom with warm white plaster walls and a wide-plank oak
floor. A raised timber loft platform 44 inches off the floor with a five-sided plank
deck on four rough-sawn 4x4 posts. The deck is ringed by closely spaced vertical wood
balusters with a flat top rail and a solid kick board. A wool blanket and two linen
cushions on the deck. Beneath the loft the base is fully enclosed in deep moss-green
painted vertical plank boards, with a TRUE CIRCULAR door about 27 inches across, black
forged-iron strap hinges, a round turned-wood knob, standing slightly ajar with warm
amber light spilling out. A small round porthole in the adjacent panel. A straight wood
ladder with rigid wooden grab rails.

[shared geometry block]
[shared style block]
```

## 2. The round door, close
**Reference:** a cropped step render, or `05_hobbit_door.png` once regenerated

```
Photoreal close detail of a circular child-sized door in a low timber wall, exact same
geometry and camera as the reference. A perfect 27 inch circle of plywood faced with
vertical tongue-and-groove boards, painted deep moss green with the brush texture and
grain reading through. Two long black forged-iron strap hinges with hammered edges,
running most of the way across the circle. A round turned-wood knob near the leading
edge. A shallow curved sill at the bottom that a small child steps over. The door is
open about 30 degrees; inside, warm amber light, a wool rug and low shelves of chunky
board books.

Bag End. Not an arch, not a rounded rectangle - a true circle.

[shared style block]
```

## 3. A child in it, for scale
**Reference:** hero render

```
...add a four-year-old crouching to step through the circular door, seen from behind,
face not visible, motion slightly blurred. The scale should read: the door comes to
about their shoulder.

[shared geometry block]
[shared style block]
```

---

## 4. Variation modifiers

| Modifier | Use for |
|---|---|
| `Lit at night, only the warm practical inside the den, deep shadow.` | mood |
| `Morning, cool daylight from the left, low warm fill.` | clean daytime |
| `Shot on 85mm, shallow depth of field, focus on the circular door.` | detail beauty shot |
| `Ladder lifted off and standing flat against the wall.` | phase 1 mode |
| `Heavier patina: worn paint on the door edge, scuffed deck, softened arrises.` | realism |

## 5. Negative prompt

```
arched door, rounded rectangle door, square door, rope net railing, rope mesh guardrail,
cargo net, rope bridge, hanging rope, horizontal cable railing, bookshelf built into a
railing, books on the upper deck, wide gaps between balusters, hexagonal deck, square
deck, pastel colors, pink, fairy lights, glitter, primary-color plastic, molded plastic
playset, cartoon, CGI look, wall text, signage, watermark, warped geometry, floating
furniture, impossible joinery, exposed fasteners at child height.
```
