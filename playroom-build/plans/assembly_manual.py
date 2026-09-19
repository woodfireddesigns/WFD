"""LEGO-style build manual. Letter landscape so it prints at home.
Every number comes from geometry.py, every image from the real model."""
import os, sys, math, datetime, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from params import *
import geometry as G
from assembly import STEPS
from drawkit import frac

W, H = 11*72, 8.5*72
ROOT = os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "exports", "Playroom_Loft_Build_Manual.pdf")
IMG  = os.path.join(ROOT, "exports", "steps")
DATE = datetime.date.today().strftime("%Y-%m-%d")

INK   = HexColor("#16160f")
AMBER = HexColor("#e09528")
GREEN = HexColor("#2f4f34")
DARK  = HexColor("#20301f")
GREY  = HexColor("#8b8b85")
PALE  = HexColor("#f3f1e8")
RED   = HexColor("#b4291f")
LINE  = HexColor("#cfc9b8")

GROUP_MEMBERS = collections.defaultdict(list)
for m in G.MEMBERS:
    GROUP_MEMBERS[m["group"]].append(m)

def parts_for(step):
    agg = collections.OrderedDict()
    for g in step["groups"]:
        for m in GROUP_MEMBERS.get(g, []):
            k = (m["stock"], round(m["L"], 2))
            agg[k] = agg.get(k, 0) + 1
    return [(st, L, q) for (st, L), q in agg.items()]

def wrap(c, s, fs, width, font="Helvetica"):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    out, cur = [], ""
    for wd in s.split(" "):
        t = (cur + " " + wd).strip()
        if stringWidth(t, font, fs) <= width or not cur: cur = t
        else: out.append(cur); cur = wd
    out.append(cur); return out

def chip(c, x, y, n, r=15, fill=AMBER, col=HexColor("#ffffff")):
    c.saveState(); c.setFillColor(fill); c.circle(x, y, r, stroke=0, fill=1)
    c.setFillColor(col); c.setFont("Helvetica-Bold", r*1.15)
    c.drawCentredString(x, y - r*0.40, str(n)); c.restoreState()

def footer(c, label, page):
    c.saveState()
    c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(40, 34, W-40, 34)
    c.setFont("Helvetica-Bold", 7.4); c.setFillColor(GREEN)
    c.drawString(40, 23, "KIDS' PLAYROOM LOFT")
    c.setFont("Helvetica", 7.4); c.setFillColor(GREY)
    c.drawString(148, 23, label)
    c.drawRightString(W-40, 23, f"{DATE}   ·   page {page}")
    c.restoreState()

def img(c, path, x, y, w, h):
    if not os.path.exists(path):
        c.setFillColor(RED); c.setFont("Helvetica", 8)
        c.drawString(x, y+h/2, f"[missing {os.path.basename(path)}]"); return
    ir = ImageReader(path); iw, ih = ir.getSize()
    s = min(w/iw, h/ih)
    c.drawImage(ir, x + (w-iw*s)/2, y + (h-ih*s)/2, iw*s, ih*s, mask='auto')

# ----------------------------------------------------------------------
def cover(c):
    c.setFillColor(DARK); c.rect(0, 0, W, H, stroke=0, fill=1)
    img(c, os.path.join(IMG, "step_99_complete.png"), W*0.40, 70, W*0.58, H-150)
    c.setFillColor(HexColor("#e8e2d2")); c.setFont("Helvetica-Bold", 40)
    c.drawString(48, H-110, "THE LOFT")
    c.setFont("Helvetica", 15); c.setFillColor(HexColor("#b9c4a8"))
    c.drawString(50, H-136, "build manual")
    c.setStrokeColor(AMBER); c.setLineWidth(3); c.line(50, H-152, 240, H-152)
    c.setFont("Helvetica", 10.5); c.setFillColor(HexColor("#cdd4c2"))
    for i, ln in enumerate([
        "A five-sided timber platform 44 inches up, with a round",
        "hobbit door into the den underneath.",
        "",
        "14 steps. Two saw angles. One weekend with a helper."]):
        c.drawString(50, H-186-i*15, ln)
    rows = [("Deck", "60 x 60 inch corner, five sides, 21.9 sq ft"),
            ("Platform height", '44 inches'),
            ("Guard", '36 inches, balusters at 3 inches clear'),
            ("Round door", '27 inch circle in a 30 inch square opening'),
            ("Saw settings", "45 degrees and 22-1/2 degrees. That is all."),
            ("Posts", "4 tall, 1 corner stub"),
            ("Serves", "18 months to about 9 years")]
    y = H-300
    for a, b in rows:
        c.setFont("Helvetica-Bold", 8.4); c.setFillColor(AMBER); c.drawString(50, y, a.upper())
        c.setFont("Helvetica", 9); c.setFillColor(HexColor("#e2e6d8")); c.drawString(50, y-12, b)
        y -= 30
    c.setFont("Helvetica", 7.6); c.setFillColor(HexColor("#7f8a74"))
    c.drawString(50, 52, "Generated from the parametric model. Every dimension traces to params.py.")
    c.drawString(50, 41, "Not engineer-stamped. Verify stud locations on site before drilling.")
    c.showPage()

def rules(c):
    c.setFillColor(PALE); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 22)
    c.drawString(44, H-64, "Before you start")
    c.setStrokeColor(AMBER); c.setLineWidth(3); c.line(44, H-76, 230, H-76)
    cols = [
      ("TOOLS", [
        "Miter saw (10 inch is plenty)", "Drill / driver, 1/4 and 9/16 sockets",
        "Jigsaw", "Router + circle jig (for the round door)",
        "Stud finder", "4 ft level", "Speed square", "Clamps",
        "Orbital sander"]),
      ("THE FOUR RULES", [
        "1.  The two wall ledgers carry the loft.",
        "     The posts are secondary. Bolt the",
        "     ledgers into studs, never drywall.",
        "",
        "2.  Everything is screwed, not nailed.",
        "",
        "3.  No guard gap over 3-1/2 inches,",
        "     anywhere, ever. Check with a block.",
        "",
        "4.  Cut one, test fit, then cut the rest."]),
      ("KEEPS THE LITTLE ONE SAFE", [
        "The ladder LIFTS OFF. Two pins. That is",
        "what keeps an 18-month-old off a 44 inch",
        "platform, not the gate.",
        "",
        "No rope anywhere a child can loop it.",
        "No shelves in the guardrail - they are a",
        "ladder.",
        "No lock on the round door, ever.",
        "A 2 inch mat under the open faces."]),
    ]
    cw = (W-88-40)/3
    for i, (t, lines) in enumerate(cols):
        x = 44 + i*(cw+20)
        c.setFillColor(GREEN); c.rect(x, H-112, cw, 18, stroke=0, fill=1)
        c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 9)
        c.drawString(x+8, H-106, t)
        y = H-132
        for ln in lines:
            c.setFont("Helvetica-Bold" if ln[:2] in ("1.","2.","3.","4.") else "Helvetica", 8.6)
            c.setFillColor(INK); c.drawString(x+8, y, ln); y -= 12.4
    # full cut inventory
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 13)
    c.drawString(44, 268, "Cut everything first")
    c.setFont("Helvetica", 8.2); c.setFillColor(GREY)
    c.drawString(160, 268, "tick them off as you go - it is much faster than cutting as you build")
    agg = collections.OrderedDict()
    for m in G.MEMBERS:
        k = (m["stock"], round(m["L"], 2))
        agg[k] = agg.get(k, 0) + 1
    items = sorted(agg.items(), key=lambda kv: (kv[0][0], -kv[0][1]))
    percol = math.ceil(len(items)/4)
    for i, ((st, L), q) in enumerate(items):
        col, row = divmod(i, percol)
        x = 44 + col*((W-88)/4); y = 248 - row*11.4
        c.setStrokeColor(GREY); c.setLineWidth(0.7); c.rect(x, y-1.5, 7, 7, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 7.6); c.setFillColor(AMBER)
        c.drawString(x+12, y, f"{q}x")
        c.setFont("Helvetica", 7.6); c.setFillColor(INK)
        c.drawString(x+28, y, f"{st}")
        c.setFont("Helvetica-Bold", 7.6)
        c.drawRightString(x+(W-88)/4-14, y, frac(L))
    footer(c, "tools, rules and the full cut list", 2)
    c.showPage()

def step_page(c, st, page):
    c.setFillColor(HexColor("#ffffff")); c.rect(0, 0, W, H, stroke=0, fill=1)
    # header
    chip(c, 68, H-62, st["n"], 24)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 21)
    c.drawString(102, H-70, st["title"])
    c.setStrokeColor(LINE); c.setLineWidth(1); c.line(44, H-96, W-44, H-96)
    # image left
    IW = W*0.52
    img(c, os.path.join(IMG, f"step_{st['n']:02d}.png"), 40, 56, IW, H-164)
    c.setFont("Helvetica", 7.2); c.setFillColor(GREY)
    c.drawString(46, 46, "amber = install this step      grey = already built")
    # right column
    x = 40 + IW + 16; cw = W - x - 40
    y = H-124
    c.setFillColor(GREEN); c.rect(x, y-3, cw, 15, stroke=0, fill=1)
    c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 8)
    c.drawString(x+7, y+1.5, "YOU NEED")
    y -= 17
    for ln in wrap(c, st["tools"], 8.4, cw-12):
        c.setFont("Helvetica", 8.4); c.setFillColor(INK); c.drawString(x+7, y, ln); y -= 11
    y -= 8
    parts = parts_for(st)
    extra = st.get("extra", [])
    if parts or extra:
        c.setFillColor(AMBER); c.rect(x, y-3, cw, 15, stroke=0, fill=1)
        c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 8)
        c.drawString(x+7, y+1.5, "PARTS FOR THIS STEP")
        y -= 18
        for stock, L, q in parts:
            c.setFillColor(PALE); c.rect(x, y-3.4, cw, 12.4, stroke=0, fill=1)
            c.setFont("Helvetica-Bold", 8.4); c.setFillColor(AMBER)
            c.drawString(x+7, y, f"{q}x")
            c.setFont("Helvetica", 8.4); c.setFillColor(INK)
            c.drawString(x+26, y, stock)
            c.setFont("Helvetica-Bold", 8.4)
            c.drawRightString(x+cw-8, y, frac(L))
            y -= 13.4
        for q, desc in extra:
            c.setFillColor(HexColor("#faf6ec")); c.rect(x, y-3.4, cw, 12.4, stroke=0, fill=1)
            c.setFont("Helvetica-Bold", 8.4); c.setFillColor(AMBER)
            c.drawString(x+7, y, f"{q}x")
            c.setFont("Helvetica", 8.4); c.setFillColor(INK)
            for seg in wrap(c, desc, 8.4, cw-40)[:1]:
                c.drawString(x+26, y, seg)
            y -= 13.4
        y -= 6
    for ln in st["text"]:
        if not ln: y -= 5; continue
        for seg in wrap(c, ln, 8.6, cw-10):
            c.setFont("Helvetica", 8.6); c.setFillColor(INK)
            c.drawString(x+7, y, seg); y -= 11.4
    if st.get("warn"):
        h = 16 + 11.4*len(wrap(c, st["warn"], 8.4, cw-34))
        y -= 8
        c.setFillColor(HexColor("#fdf0ec")); c.setStrokeColor(RED); c.setLineWidth(1)
        c.rect(x, y-h+10, cw, h, stroke=1, fill=1)
        c.setFillColor(RED); c.setFont("Helvetica-Bold", 12)
        c.drawString(x+9, y-3, "!")
        yy = y-3
        for seg in wrap(c, st["warn"], 8.4, cw-34):
            c.setFont("Helvetica-Bold", 8.4); c.setFillColor(RED)
            c.drawString(x+24, yy, seg); yy -= 11.4
    footer(c, f"step {st['n']} of {len(STEPS)}  ·  {st['title']}", page)
    c.showPage()

def finish(c, page):
    c.setFillColor(DARK); c.rect(0, 0, W, H, stroke=0, fill=1)
    img(c, os.path.join(IMG, "step_99_complete.png"), 30, 150, W*0.52, H-210)
    x = W*0.56
    c.setFillColor(HexColor("#e8e2d2")); c.setFont("Helvetica-Bold", 26)
    c.drawString(x, H-84, "Done.")
    c.setStrokeColor(AMBER); c.setLineWidth(3); c.line(x, H-98, x+120, H-98)
    c.setFont("Helvetica", 10); c.setFillColor(HexColor("#cdd4c2"))
    y = H-126
    for ln in ["Now it has to survive being lived with.", ""]:
        c.drawString(x, y, ln); y -= 15
    phases = [("18 months - 3 years",
               "Den and the round door only. Ladder stored flat,",
               "off the structure. Nothing to fall from."),
              ("3 years +",
               "Hang the ladder. Loft in use. Gate self-closes.",
               "Only once he climbs it unassisted, both ways."),
              ("5 years +",
               "Unscrew the removable panel on the north face",
               "and add the rope bridge to a second structure.")]
    for t, a, b in phases:
        c.setFont("Helvetica-Bold", 10); c.setFillColor(AMBER); c.drawString(x, y, t)
        c.setFont("Helvetica", 8.8); c.setFillColor(HexColor("#cdd4c2"))
        c.drawString(x, y-13, a); c.drawString(x, y-24, b)
        y -= 46
    y -= 6
    c.setFont("Helvetica-Bold", 10); c.setFillColor(HexColor("#ffffff"))
    c.drawString(x, y, "CHECK THESE, ON A SCHEDULE")
    y -= 16
    for ln in ["30 days:  re-torque every lag. Green lumber shrinks",
               "              and they WILL be loose.",
               "6 months:  lags again, gate latches, ladder pins",
               "              present, no gap grown past 3-1/2 inches.",
               "Write the date on the ledger in pencil."]:
        c.setFont("Helvetica", 8.8); c.setFillColor(HexColor("#cdd4c2"))
        c.drawString(x, y, ln); y -= 12
    c.setFillColor(HexColor("#7f8a74")); c.setFont("Helvetica", 7.6)
    c.drawString(30, 116, "Full dimensioned drawing set, cut list and hardware schedule: Playroom_Build_Plans.pdf")
    c.showPage()

def main():
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Kids' Playroom Loft - Build Manual")
    cover(c); rules(c)
    p = 3
    for st in STEPS:
        step_page(c, st, p); p += 1
    finish(c, p)
    c.save()
    print("MANUAL:", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")

main()
