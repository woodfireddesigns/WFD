import os, sys, math, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from params import *
import geometry as G
from drawkit import *
import sheets_a as A, sheets_b as B, sheets_c as C, sheets_d as D, sheets_e as E

W, H = 17*72, 11*72                      # ANSI B landscape
OUT = os.path.join(os.path.dirname(HERE), "exports", "Playroom_Build_Plans.pdf")
RND = os.path.join(os.path.dirname(HERE), "exports", "renders")
DATE = datetime.date.today().strftime("%Y-%m-%d")

NOTES = [
 ('This has to work for an 18-month-old AND a four-year-old. That drove a redesign.',
  'one structure, one age',
  'age-staged in three phases',
  ['CPSC caps a TODDLER platform (6-23 months) at 32". This deck is 44". You cannot make a 44" loft safe for an',
   '18-month-old, so the loft is not his. The enclosed ground den and the playhouse are, from day one.',
   'The ladder LIFTS OFF, which is what actually keeps him out of the loft. Full phase table on this sheet.']),
 ('The rope net guardrail had to go. It is a head-entrapment hazard.',
  'rope net railing, 4-6" mesh',
  '2x2 balusters, 2.59-2.70" clear',
  ['CPSC: any opening between 3.5" and 9" lets a small body through and catches the head. A 4-6" mesh fails both probes.',
   'Vertical balusters at under 3-3/8" clear instead, with a 2x4 toe board closing the gap at deck level.',
   'Rope stays as tight decorative wrapping on the posts. No slack, no loops: a loose loop is a strangulation risk under 3.']),
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
    c.drawString(44, 44, "KIDS' PLAYROOM  ·  CORNER LOFT")
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
    sheet(c, "A2",  "LOFT — DECK FRAMING PLAN", "pentagon geometry · joist layout · post schedule", 'model-derived, fit to sheet',
          A.loft_framing_plan)
    sheet(c, "A3",  "LOFT — DEVELOPED ELEVATION", "the three open faces unrolled flat", 'model-derived, fit to sheet',
          B.developed_elev)
    sheet(c, "A4",  "LOFT — KNEE WALL + HOBBIT DOOR", "wall section · full arch template on a 2\" grid", 'template is scalable off its grid',
          B.kneewall_and_door)
    sheet(c, "A5",  "REMOVABLE LADDER + DEN SHELF", "elevation · hook and pin detail · ground-level shelf", 'model-derived, fit to sheet',
          C.ladder_and_shelf)
    sheet(c, "A6",  "CUT LIST", "every member, every finished length", "n.t.s.", D.cutlist)
    sheet(c, "A7",  "HARDWARE + HOME DEPOT BUY LIST", "internet numbers · quantities · budget", "n.t.s.", D.hardware)

    sheet(c, "A8", "PRACTICALITIES + LIVE-WITH CHECKLIST",
          "fit by age · adult access · air · finish · re-check schedule", "n.t.s.",
          E.practicalities)
    c.save()
    print("PDF:", OUT, f"{os.path.getsize(OUT)/1024:.0f} KB")

main()
