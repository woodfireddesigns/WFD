# How WFD builds a brand identity case study

Drawn from six case studies Michael picked as the bar (2026-10-28): Layers (bakery, Amsterdam), Highland (Visit Highlands NC), Godby Hotel (pub, Melbourne), Armando (sandwich shop, Tucumán), We Can Run (running club, Brazil) and Galloway District (historic district, Springfield MO). Screenshots live in `WFD/<Name>_Example Case Study_*`.

## The one rule

**Show the brand living in its world. Never just show the logo.**

None of the six opens on a logo floating on white. They open on a person holding the cup, a hat sitting on a log, a staff tee seen from behind at the bar, a sign glowing on a tiled wall. The logo shows up the way it would in real life: on things, in places, in hands. A case study proves that a brand *works*. A logo sheet only proves it exists.

## Ten principles

### 1. One idea, said everywhere
Every great study is built around a single line or concept, and every frame serves it:
- Layers: "Baked with attitude"
- Highland: "Hewn from the wild in 1875"
- Godby: a top-hatted gentleman, "where the good times roll"
- Armando: Tucumán pride ("Orgullo Tucumano")
- We Can Run: "Quem corre sente" (whoever runs, feels it)
- Galloway: "Historic by nature, connected by community"

Before choosing images, write the idea in one sentence. If a frame doesn't serve it, cut the frame.

### 2. Open in the world, not on the mark
The first frame decides whether people keep scrolling. Use a lifestyle or environment shot (Layers' street crowd, Godby's staff tee, Armando's lit sign), or an origin image (Highland's archival postcard). Save the clean logo board for frame 3 to 6.

### 3. Root it in a real place and a real date
Specifics are credibility. Highland puts "ELEV 4118" and "1875" in the frames. Galloway has "EST. 1883" and "Springfield, Missouri". Godby has "163 Toorak Road, Old South Yarra Station". Armando draws a map of Tucumán. Find the client's street, city, founding year, elevation, area code or landmark, and put it in the work.

### 4. Two or three colors, in every frame
Each study holds a tight palette, and **the photography is graded into it**: Godby is all amber and mustard, Highland all forest green, We Can Run only volt and black, Armando only yellow and cobalt. Nothing off-palette sneaks in, not even a background. Scrolling the grid should feel like one color story.

### 5. Prove the system, not just the logo
Each study has at least one flat "system" frame, and these are what separate an identity from a logo:
- **Logo family** (Armando's oval, script and A monogram, shown together)
- **Color with codes** (Armando prints `#FFD506` and `#0E0E96` right on the board)
- **Type specimen** (Armando names all four fonts)
- **Pattern** (Armando's wallpaper, Layers' tissue paper, Galloway's checkered blanket)
- **Character sheet** (Godby's eight mascot poses: pouring, carving, DJing)

Aim for two or three of these per study.

### 6. Show the production files proudly
Layers shows its red box dielines and tissue repeat flat, as working files. Highland shows the logo construction over an archival photo. Craft documents read as expertise. When we have a real dieline, template or construction drawing, it belongs in the study.

### 7. Get close: one tactile macro
Each study has at least one frame you can almost feel: Godby's debossed menu cover, a pint glass etched with the mascot, Highland's blind-embossed business card, Layers' tote fabric. Name the process (letterpress, deboss, embroidery, foil, enamel) and shoot it at macro distance.

### 8. Merch is proof of love
Hats, pennants, blankets, totes, tees, coasters. If people would wear it, the brand has a fan base, not just a logo. Highland's rope hat and pennant, Galloway's blanket and tees, Godby's staff shirts. Include at least two pieces of wearable or carryable merch.

### 9. Let the voice be an image
At least one frame is set type alone, a headline in the brand's own fonts over a photo or a flat color: Highland's "Hewn from the wild", Galloway's "Historic by nature", We Can Run's "Quem corre sente", Armando's "República del Tucumán". It shows the brand has something to say, plus a type system to say it with.

### 10. Pace it like a carousel
Every study uses one frame format (mostly 4:5 portrait, built for Instagram), and the rhythm alternates:

> world → world → **system** → detail → world → **voice** → **system** → merch → world → close

Never put three of the same kind of frame in a row. Eight to fourteen frames is the range. Fewer looks thin, and more than sixteen starts repeating.

## The frame recipe (12 frames)

| # | Frame | Job | Example |
|---|---|---|---|
| 1 | Hero in the world | Stop the scroll | Layers street crowd, Armando lit sign |
| 2 | Origin or place | Root it | Highland archival postcard |
| 3 | Logo family board | Show the system | Armando oval, script, A |
| 4 | Signature touchpoint | The thing customers see most | Godby menu, Rae van |
| 5 | Tactile macro | Craft | Godby deboss, Highland emboss |
| 6 | Voice frame | The idea in words | "Hewn from the wild" |
| 7 | Color and type board | Rigor | Armando palette and fonts |
| 8 | Merch, wearable | Love | Highland hat, Galloway tee |
| 9 | Pattern or character sheet | Range | Godby poses, Armando wallpaper |
| 10 | Environment at scale | Presence | Galloway street banners, Godby facade |
| 11 | Production file | Expertise | Layers dielines |
| 12 | Close | Leave them wanting it | Highland "AFTER", We Can Run wordmark |

Not every client has all twelve. Frames 1, 3, 4, 5, 6 and 8 are the minimum.

## Writing the blurb

Three sentences, in this order:
1. **Who and where**: the client, the trade and the place, in plain words.
2. **The idea**: the one line from principle 1 and why it fits them.
3. **How it shows up**: the two or three touchpoints that carry it, named concretely.

No adjective stacks, no "elevated" or "bespoke". Say what a customer sees.

## What to avoid

- A logo on white as the first frame
- The same mockup type three times in a row (three tees, three trucks)
- Off-palette photos, like a blue sky in a brown-and-red brand
- Settings from the wrong world. A Seattle drain company doesn't belong in a Texas desert
- Generic stock-mockup lighting with no time of day or weather
- Showing a mark the client never used, or one that breaks their own rules
- Unlabeled AI. Where the site format allows it, say what's a rendered mockup

## How this maps to woodfireddesigns.com

`data/case-studies.js` takes a `cover` (frame 1), a `blurb` (three sentences) and a `gallery`. In the gallery, `wide: true` spans two columns, so alternate one wide frame with two regular frames (W, 2, W, 2), and pair same-aspect images in the regular slots (two portraits, or two 4:3s). System boards and voice frames read best as wide. Macros, merch and portraits read best as regular.

## Scoring a draft (check before publishing)

- [ ] Can I say the idea in one sentence, and does every frame serve it?
- [ ] Is frame 1 the brand in its world?
- [ ] Is a real place, date or detail visible somewhere?
- [ ] Is every frame on-palette?
- [ ] At least two system frames (logo family, color and type, pattern, characters)?
- [ ] At least one tactile macro and two merch pieces?
- [ ] At least one voice frame?
- [ ] No three same-type frames in a row?
- [ ] 8 to 14 frames?
- [ ] Every mark shown is one the client actually uses?
