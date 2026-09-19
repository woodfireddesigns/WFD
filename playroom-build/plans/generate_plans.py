import os, sys, math, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from params import *
import geometry as G
from drawkit import *
import sheets_a as A, sheets_b as B, sheets_c as C, sheets_d as D

W, H = 17*72, 11*72                      # ANSI B landscape
OUT = os.path.join(os.path.dirname(HERE), "exports", "Playroom_Build_Plans.pdf")
RND = os.path.join(os.path.dirname(HERE), "exports", "renders")
DATE = datetime.date.today().strftime("%Y-%m-%d")

NOTES = [
 ('A 36-38" hobbit door will not fit under a 44" platform',
  'R.O. 24-26" W x 36-38" H',
  'R.O. 26" W x 32" H',
  ['44" deck  -  3/4" plywood  -  5-1/2" joist  =  37-3/4" of wall, floor to underside of framing.',
   'Take out the 1-1/2" bottom plate, a 1-1/2" flat header, a 2-3/4" cripple and a 1-1/2" top plate and 32" is what is left.',
   'A 32" door is still right for a 3-6 year old. The semicircular arch on top reads taller than it measures.']),
 ('The knee wall studs are 34-3/4", not 40-42"',
  'studs ~40-42" tall',
  'studs 34-3/4"',
  ['Same arithmetic. The wall dies into the underside of the joists at 37-3/4", and two plates eat 3" of that.',
   'Cut one, hold it in place, and confirm before you cut the other fifteen.']),
 ('The bridge span is 54", not 42"',
  'span ~42"',
  'clear span 54"',
  ['162" wall  -  60" loft  -  48" playhouse  =  54" of clear air between them.',
   'Both structures are in corners, so neither can slide toward the other to close the gap.',
   'Order the net for 54". Expect 6-8" of sag at that span, which is why the plan set carries a top rope AND a mid rope.']),
]

def title_block(c, num, title, sub, scale):
    c.saveState()
    c.setStrokeColor(HexColor("#20301f")); c.setLineWidth(1.4); c.rect(28, 28, W-56, H-56, stroke=1, fill=0)
    c.setFillColor(HexColor("#20301f")); c.rect(28, H-72, W-56, 44, stroke=0, fill=1)
    c.setFillColor(HexColor("#e8e2d2")); c.setFont("Helvetica-Bold", 15)
    c.drawString(44, H-58, title)
    c.setFont("Helvetica", 9); c.setFillColor(HexColor("#a8b59a"))
    c.drawString(44, H-70, sub)
    c.setFont("Helvetica-Bold", 22); c.setFillColor(HexColor("#d8cfa8"))
    c.drawRightString(W-44, H-62, num)
    c.setFillColor(HexColor("#f2efe6")); c.rect(28, 28, W-56, 30, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#20301f")); c.setLineWidth(0.8); c.line(28, 58, W-28, 58)
    c.setFont("Helvetica-Bold", 7.4); c.setFillColor(HexColor("#20301f"))
    c.drawString(44, 44, "KIDS' PLAYROOM BUILD  ·  LOFT / BRIDGE / PLAYHOUSE")
    c.setFont("Helvetica", 7)
    c.drawString(300, 44, f"SCALE: {scale}")
    c.drawString(430, 44, f"DATE: {DATE}")
    c.drawString(540, 44, "UNITS: INCHES")
    c.drawString(650, 44, "GENERATED FROM THE PARAMETRIC MODEL — params.py / geometry.py / Blender 4.2")
    c.setFillColor(HexColor("#a3231b")); c.setFont("Helvetica-Bold", 7)
    c.drawRightString(W-44, 44, "NOT ENGINEER-STAMPED · VERIFY STUDS ON SITE · SEE A0")
    c.restoreState()

def sheet(c, num, title, sub, scale, fn):
    title_block(c, num, title, sub, scale)
    sh = Sheet(c, W, H, num, title, sub, scale)
    if fn: fn(sh)
    c.showPage()

def main():
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Kids' Playroom Build — Construction Plans")
    c.setAuthor("Wood Fired Designs")

    sheet(c, "A0",  "COVER · CRITICAL NOTES · SHEET INDEX", "read before you buy anything", "n.t.s.",
          lambda sh: A.cover(sh, NOTES))
    sheet(c, "A1",  "OVERALL ROOM PLAN", "structure locations · wall anchor zones · stud layout", 'model-derived, fit to sheet',
          A.room_plan)
    sheet(c, "A2",  "LOFT — DECK FRAMING PLAN", "hexagon geometry · joist layout · post schedule", 'model-derived, fit to sheet',
          A.loft_framing_plan)
    sheet(c, "A3",  "LOFT — DEVELOPED ELEVATION", "all four open faces unrolled flat", 'model-derived, fit to sheet',
          B.developed_elev)
    sheet(c, "A4",  "LOFT — KNEE WALL + HOBBIT DOOR", "wall section · full arch template on a 2\" grid", 'template is scalable off its grid',
          B.kneewall_and_door)
    sheet(c, "A5",  "LADDER + BOOKSHELF GUARD", "elevation · plan · build notes", 'model-derived, fit to sheet',
          C.ladder_and_shelf)
    sheet(c, "A6",  "PLAYHOUSE", "plan · south elevation · roof framing", 'model-derived, fit to sheet',
          C.playhouse)
    sheet(c, "A7",  "ROPE BRIDGE", "elevation · anchor detail · span correction · safety", 'model-derived, fit to sheet',
          C.bridge)
    sheet(c, "A8",  "CUT LIST", "every member, every finished length", "n.t.s.", D.cutlist)
    sheet(c, "A9",  "HARDWARE + HOME DEPOT BUY LIST", "internet numbers · quantities · budget", "n.t.s.", D.hardware)

    R = lambda n: os.path.join(RND, n)
    sheet(c, "A10", "REFERENCE VIEWS — MODEL", "rendered from the Blender model, dimensionally accurate", "n.t.s.",
          lambda sh: D.plate(sh,
            [R("01_hero_iso.png"), R("06_from_doorway.png"), R("02_loft_three_qtr.png"), R("03_playhouse_front.png")],
            "MODEL VIEWS — these are the geometry, not a mood board. Use them to check that what you build matches what was drawn.",
            ["01  Isometric overview — both structures and the crossing",
             "02  From the room doorway — what a kid sees walking in",
             "03  Loft three-quarter — hex deck, rope guard, bookshelf",
             "04  Playhouse front — hobbit door, round window, peaked roof"]))
    sheet(c, "A11", "TECHNICAL MODEL VIEWS", "orthographic + framing-only", "n.t.s.",
          lambda sh: D.plate(sh,
            [R("T1_plan.png"), R("T4_loft_frame.png"), R("T2_elev_north.png"), R("T3_elev_west.png")],
            "ORTHOGRAPHIC + FRAMING-ONLY VIEWS",
            ["T1  True plan — room shell removed",
             "T2  Loft framing only — skins, deck and rope hidden",
             "T3  North elevation", "T4  West elevation"]))
    c.save()
    print("PDF:", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")

main()
