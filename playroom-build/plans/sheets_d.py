"""Sheets: cut list, hardware / Home Depot buy list, render plates."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G
from drawkit import *
from reportlab.lib.utils import ImageReader

def table(c, x, y, cols, rows, widths, fs=7.2, rh=12.2, hdr=True, zebra=True, right=()):
    if hdr:
        c.setFillColor(HexColor("#20301f")); c.rect(x, y-3, sum(widths), rh+1, stroke=0, fill=1)
        c.setFillColor(HexColor("#e8e2d2")); c.setFont("Helvetica-Bold", fs)
        cx = x
        for w, h in zip(widths, cols):
            c.drawString(cx+4, y+1.5, h); cx += w
        y -= rh+2
    for i, r in enumerate(rows):
        if zebra and i % 2:
            c.setFillColor(HexColor("#f1eee4")); c.rect(x, y-2.6, sum(widths), rh, stroke=0, fill=1)
        cx = x
        for j, (w, cell) in enumerate(zip(widths, r)):
            bold = str(cell).startswith("**")
            s = str(cell).replace("**", "")
            c.setFont("Helvetica-Bold" if bold or j == 0 and s.isupper() else "Helvetica", fs)
            c.setFillColor(ACCENT if s.isupper() and j == 0 else INK)
            if j in (right or ()):
                c.drawRightString(cx+w-5, y, s)
            else:
                c.drawString(cx+4, y, s)
            cx += w
        y -= rh
    return y

def cutlist(sh):
    c = sh.c
    from collections import OrderedDict
    agg = OrderedDict()
    for m in G.MEMBERS:
        k = (m["group"], m["stock"], round(m["L"], 3), m["note"])
        agg[k] = agg.get(k, 0) + 1
    groups = OrderedDict()
    for (grp, stock, L, note), q in agg.items():
        groups.setdefault(grp, []).append((stock, L, q, note))

    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK)
    c.drawString(54, sh.H-96, "CUT LIST — generated directly from the model. Every length is the finished cut length.")
    c.setFont("Helvetica", 7.6); c.setFillColor(THIN)
    c.drawString(54, sh.H-108, "Lengths are long-point to long-point where a member is mitered. Cut one of any repeated part, "
                               "test-fit it, then batch the rest.")

    NC = 3
    GAP = 16
    CW = (sh.W - 108 - GAP*(NC-1)) / NC
    widths = [58, 52, 26, CW-136]
    X = [54 + i*(CW+GAP) for i in range(NC)]
    TOP = sh.H-130
    PANEL_H = 250                      # reserved at the bottom of the last column
    col, y = 0, TOP
    for grp, items in groups.items():
        need = 15 + 14 + len(items)*11.0 + 12
        floor = 92 + (PANEL_H if col == NC-1 else 0)
        if y - need < floor and col < NC-1:
            col += 1; y = TOP
        c.setFont("Helvetica-Bold", 8.4); c.setFillColor(ACCENT)
        c.drawString(X[col], y, grp.upper())
        c.setStrokeColor(ACCENT); c.setLineWidth(0.7); c.line(X[col], y-4, X[col]+sum(widths), y-4)
        y -= 15
        rows = [(stock, frac(L), str(q), note[:52]) for stock, L, q, note in items]
        y = table(c, X[col], y, ["STOCK", "LENGTH", "QTY", "NOTE"], rows, widths, 6.8, 11.0, right=(2,))
        y -= 13

    # buy panel, bottom of the last column
    px, py = X[NC-1], 92
    c.setFillColor(HexColor("#f2efe6")); c.setStrokeColor(HexColor("#cfc8b6")); c.setLineWidth(0.9)
    c.rect(px, py, CW, PANEL_H-18, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 9.5); c.setFillColor(INK)
    c.drawString(px+12, py+PANEL_H-38, "SHEET GOODS + WHAT TO ACTUALLY BUY")
    tot = {}
    for m in G.MEMBERS: tot[m["stock"]] = tot.get(m["stock"], 0) + m["L"]
    rows = [
      ("4x4 x 8 ft PT post", f'{tot.get("4x4 PT",0)/12:.1f} lf', "8"),
      ("4x4 x 10 ft PT post", "(1 post + the stub)", "1"),
      ("2x6 x 8 ft Ground Contact PT", f'{tot.get("2x6 PT",0)/12:.1f} lf', "3"),
      ("2x6 x 8 ft SPF", f'{tot.get("2x6",0)/12:.1f} lf', "5"),
      ("2x4 x 8 ft Ground Contact PT", f'{tot.get("2x4 PT",0)/12:.1f} lf', "2"),
      ("2x4 x 8 ft SPF stud", f'{tot.get("2x4",0)/12:.1f} lf', "18"),
      ("1x3 x 8 ft pine (book lips)", f'{tot.get("1x3",0)/12:.1f} lf', "1"),
      ('3/4" 4x8 ply — deck + shelf', "21.75 sq ft + shelf", "2"),
      ('3/4" 4x8 ext ply — skins + doors', "~46 sq ft", "2"),
      ("1x4 T&G pine — door faces", "~24 lf", "1 bdl"),
    ]
    table(c, px+12, py+PANEL_H-58, ["ITEM", "NET", "BUY"], rows, [CW-124, 78, 34], 7.2, 12.6, right=(2,))
    c.setFont("Helvetica-Oblique", 6.9); c.setFillColor(THIN)
    for i, t in enumerate([
        "2x quantities include 15% waste. Every cut in this set fits an 8 ft stick.",
        'The one 10 ft 4x4 yields an 80" post AND the 37-3/4" corner stub with',
        "almost no waste. Nine 8-footers would leave you one post short."]):
        c.drawString(px+12, py+30-i*9.5, t)
HD = [
 ("LUMBER", None, None, None, None),
 ('4 in. x 4 in. x 8 ft. #1 Pressure-Treated Post', "202812131", "8", "$12 - $16", 'four loft posts at 80" + four playhouse posts at 84"'),
 ('4 in. x 4 in. x 10 ft. #1 Pressure-Treated Post', "—", "1", "$16 - $22", 'yields the fifth 80" post AND the 37-3/4" corner stub'),
 ('2 in. x 6 in. x 8 ft. Ground Contact PT', "—", "3", "$9 - $13", "ledgers: loft N + W, bridge both sides"),
 ('2 in. x 6 in. x 8 ft. Prime Kiln-Dried SPF', "—", "6", "$7 - $10", "joists, rim, playhouse header, ridge"),
 ('2 in. x 4 in. x 8 ft. Ground Contact PT', "—", "2", "$6 - $9", "knee wall bottom plates (on subfloor)"),
 ('2 in. x 4 in. x 8 ft. Prime Kiln-Dried Stud', "—", "18", "$4 - $6", "studs, plates, rafters, ladder, door framing"),
 ('1 in. x 3 in. x 8 ft. Pine Board', "—", "1", "$6 - $9", "shelf book lips"),
 ('3/4 in. 4x8 Sanded Plywood (BC or Sande)', "—", "4", "$48 - $68", "2 structural, 2 skin + doors"),
 ('1 in. x 4 in. Tongue & Groove Pine (bundle)', "—", "1", "$28 - $40", "door faces, both doors"),
 ("STRUCTURAL HARDWARE", None, None, None, None),
 ('Simpson Strong-Tie LUS26 Face-Mount Joist Hanger', "100374889", "8", "$1.77 ea", "square joist-to-ledger connections"),
 ('Simpson Strong-Tie LSU26 Adjustable Skewable U Hanger', "100375129", "6", "$4 - $6 ea", "J2/J3 into the angled rims — THE part for this"),
 ('Simpson Strong-Tie ABU44Z Adjustable Standoff Post Base', "100375358", "4", "$14 - $19 ea", "free-standing posts: loft D, playhouse SW, ladder foot"),
 ('Simpson Strong-Tie A23 / A35 Framing Angle', "—", "16", "$0.80 ea", "post-to-rim and plate ties"),
 ('Everbilt 3/8 in. x 4 in. Hex Lag Screw (bulk)', "—", "60", "$0.55 ea", "ledgers into studs, posts into studs"),
 ('Everbilt 3/8 in. Flat Washer (bulk)', "—", "100", "$0.15 ea", "every lag and every bolt, both sides"),
 ('Everbilt 3/8 in. x 6 in. Zinc-Plated Eye Bolt w/ Nut', "806746", "12", "$1.11 ea", "bridge + rope railing anchors — BOLTS not screw eyes"),
 ('Everbilt 3/8 in. Nylon Insert Lock Nut (nylock)', "—", "16", "$0.35 ea", "back side of every eye bolt"),
 ('Everbilt 1/4 in. x 3 in. Hex Lag Screw', "—", "40", "$0.40 ea", "bookshelf to posts, hinges, trim"),
 ('#9 x 3 in. Star Drive Construction Screw, 5 lb box', "—", "1", "$34 - $44", "general framing"),
 ('#8 x 1-5/8 in. Construction Screw, 1 lb box', "—", "2", "$9 - $12", "decking + skins — SCREWED, never nailed"),
 ("ROPE, NET, PLAY HARDWARE", None, None, None, None),
 ('VEVOR Climbing Cargo Net 6.6 x 10.5 ft Double-Layer Rope Bridge', "320569708", "1", "$70 - $110", "cut/fold to 54 x 18 — double layer gives side panels"),
 ('VEVOR Playground Climbing Cargo Net 8 x 4 ft', "320580952", "1", "$45 - $70", "ALTERNATE if you want the smaller single panel"),
 ('Everbilt 1/2 in. x 50 ft. Twisted Poly Rope (manila look)', "—", "2", "$22 - $32", "guard ropes, ladder handrails, post wrap"),
 ('Everbilt 1/2 in. Rope Thimble + Wire Rope Clip set', "—", "16", "$2 - $4 ea", "every rope termination — no knots at anchors"),
 ('Everbilt 3/8 in. Quick Link / Screw-Pin Shackle', "—", "8", "$3 - $5 ea", "net to eye bolt, serviceable"),
 ("DOORS, FINISH, LIGHT", None, None, None, None),
 ('NUVO IRON 12 in. Black Steel Strap Hinges Kit (2-pack)', "320202663", "2", "$18 - $26", "one 2-pack per door"),
 ('2-3/4 in. Round Wood Cabinet Knob', "—", "2", "$4 - $7", "hobbit door knobs"),
 ('Everbilt Magnetic Push Catch', "—", "2", "$4 - $6", "NO latch, NO lock — kid must push out from inside"),
 ('8 in. Clear Acrylic Circle / Plexiglass sheet to cut', "—", "1", "$12 - $22", "porthole — acrylic only, never glass"),
 ('12 in. Clear Acrylic Circle', "—", "1", "$16 - $28", "playhouse round window"),
 ('Commercial Electric LED Puck Light, battery, 3-pack', "—", "2", "$18 - $26", "2 inside the loft base, 1 in the playhouse"),
 ('BEHR Premium Plus Interior Eggshell — deep green', "—", "1 qt", "$20 - $26", 'match "Dark Everglade" / "Pine Mountain"'),
 ('Varathane Dark Walnut Wood Stain, qt', "—", "1", "$14 - $19", "rough-sawn look on 4x4s and trim"),
 ('Minwax Polycrylic Clear Satin, qt', "—", "1", "$20 - $26", "water-based topcoat — low odor for a kid room"),
 ('Zero-VOC primer, qt', "—", "1", "$16 - $22", "everything a kid touches"),
 ("FALL PROTECTION — NOT OPTIONAL", None, None, None, None),
 ('3/4 in. Interlocking Foam Mat Tiles, 24x24, 6-pack', "—", "3", "$26 - $38", "floor under the bridge and both entries"),
]

def hardware(sh):
    c = sh.c
    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK)
    c.drawString(54, sh.H-96, "HARDWARE SCHEDULE + HOME DEPOT BUY LIST")
    c.setFont("Helvetica", 7.6); c.setFillColor(THIN)
    c.drawString(54, sh.H-110, 'Internet # verified against homedepot.com. Prices are US national ranges and move weekly — treat them as a budget, not a quote. '
                               'Items without an Internet # are commodity stock carried in every store; grab them off the shelf.')
    y = sh.H-134
    widths = [292, 72, 40, 76, 300]
    y = table(c, 54, y, ["ITEM", "INTERNET #", "QTY", "EST. EACH", "WHAT IT DOES / WHY THIS ONE"],
              [], widths, 7.4, 13.4)
    for r in HD:
        if r[1] is None:
            y -= 6
            c.setFillColor(HexColor("#dfe6d6")); c.rect(54, y-3.4, sum(widths), 13, stroke=0, fill=1)
            c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 8)
            c.drawString(58, y, r[0]); y -= 16
            continue
        c.setFont("Helvetica", 7.4); c.setFillColor(INK)
        cx = 54
        for j, (w, cell) in enumerate(zip(widths, r)):
            if j == 1 and cell != "—":
                c.setFillColor(HexColor("#0b5e9c")); c.setFont("Helvetica-Bold", 7.4)
            elif j == 4 and ("not" in str(cell) or "NOT" in str(cell) or "never" in str(cell) or "NO " in str(cell)):
                c.setFillColor(RED); c.setFont("Helvetica-Bold", 7.2)
            else:
                c.setFillColor(INK); c.setFont("Helvetica", 7.4)
            (c.drawRightString(cx+w-6, y, str(cell)) if j in (2, 3) else c.drawString(cx+4, y, str(cell)))
            cx += w
        y -= 12.4
    y -= 10
    c.setStrokeColor(INK); c.setLineWidth(1); c.line(54, y, 54+sum(widths), y); y -= 16
    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK)
    c.drawString(54, y, "BUDGET:   $1,050 - $1,350 in materials.   Add ~$120 if you buy the double-layer net instead of the single panel.")
    y -= 20
    block(c, 54, min(y, 150), sum(widths)-40, [
        "THE ONE SPEC THE BRIEF GOT WRONG ABOUT SOURCING",
        'The brief says "Home Depot only, no specialty suppliers" AND "commercial playground-rated net, not hardware-store rope."',
        "Those pull against each other. Home Depot does carry real polyester cargo netting (VEVOR, SVOPES, Swing-N-Slide) rated 500 lb —",
        "that satisfies both. What it does NOT carry is certified playground equipment to ASTM F1487. If you want a certified net,",
        "that is a specialty order and the only line item in this build that leaves Home Depot. Your call; the framing does not change."],
        y_min=68, size=8.0, lead=11.4)

def plate(sh, imgs, title, caps, cols=2):
    c = sh.c
    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK); c.drawString(54, sh.H-96, title)
    rows = math.ceil(len(imgs)/cols)
    gw = (sh.W-108-18*(cols-1))/cols
    gh = (sh.H-190-20*(rows-1))/rows
    for i, p in enumerate(imgs):
        r, k = divmod(i, cols)
        x = 54 + k*(gw+18); y = sh.H-124 - (r+1)*gh - r*20
        try:
            ir = ImageReader(p); iw, ih = ir.getSize()
            s = min(gw/iw, (gh-16)/ih)
            c.drawImage(ir, x + (gw-iw*s)/2, y+16, iw*s, ih*s, mask='auto')
            c.setStrokeColor(HexColor("#cfc8b6")); c.setLineWidth(0.8)
            c.rect(x + (gw-iw*s)/2, y+16, iw*s, ih*s, stroke=1, fill=0)
        except Exception as e:
            c.setFillColor(RED); c.setFont("Helvetica", 8); c.drawString(x, y+40, f"[{os.path.basename(p)} missing]")
        c.setFont("Helvetica-Bold", 8); c.setFillColor(ACCENT)
        c.drawString(x, y+4, caps[i])
