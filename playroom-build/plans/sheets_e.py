"""A12 - practicalities, fit by age, and the live-with checklist."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G
from drawkit import *

# CDC 50th percentile standing height, boys, inches
AGES = [("18 mo",32.0),("2 yr",34.0),("3 yr",37.5),("4 yr",40.5),
        ("5 yr",43.5),("6 yr",46.0),("7 yr",48.5),("8 yr",51.0),("10 yr",55.5)]
DECK_HEADROOM = CEILING - DECK_TOP          # 52
DEN_HEADROOM  = JOIST_BOT                   # 37.75

def practicalities(sh):
    c = sh.c
    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK)
    c.drawString(54, sh.H-96, "WILL THIS STILL BE FUN IN FIVE YEARS? — fit by age, and the things that only show up after you live with it")
    c.setFont("Helvetica", 7.8); c.setFillColor(THIN)
    c.drawString(54, sh.H-108, "Heights are CDC 50th percentile standing height. Your kid will not be average; add or subtract and re-read the table.")

    # ---------- headroom chart ----------
    sh.view(56, 300, (sh.W-120)*0.46, sh.H-450, -14, -4, 62, len(AGES)*7+12)
    sh.line((0,0), (0, len(AGES)*7+6), INK, 1.2)
    for gx in range(0, 61, 12):
        sh.line((gx, 0), (gx, len(AGES)*7+4), GRID, 0.6)
        sh.txt((gx, -3.4), f'{gx}"', 5.8, THIN, "c")
    for i, (lbl, h) in enumerate(AGES):
        y = (len(AGES)-i)*7
        sh.txt((-1.5, y-1), lbl, 6.6, INK, "r", True)
        ok_deck = h < DECK_HEADROOM; ok_den = h < DEN_HEADROOM
        sh.poly([(0,y-2.3),(h,y-2.3),(h,y+2.3),(0,y+2.3)],
                fill=HexColor("#b9c4a0") if ok_deck else HexColor("#e0c5b4"), stroke=INK, w=0.6)
        sh.txt((h+1.5, y-1), ("stands on the deck" if ok_deck else "sits on the deck"), 5.8,
               ACCENT if ok_deck else NOTE)
        if ok_den: sh.txt((1.8, y-1), "stands in the den", 5.6, HexColor("#3b5c3f"))
    sh.line((DEN_HEADROOM, 0), (DEN_HEADROOM, len(AGES)*7+4), NOTE, 1.4, (4,2))
    sh.txt((DEN_HEADROOM, len(AGES)*7+7), f'DEN {frac(DEN_HEADROOM)}', 6.4, NOTE, "c", True)
    sh.line((DECK_HEADROOM, 0), (DECK_HEADROOM, len(AGES)*7+4), ACCENT, 1.4, (4,2))
    sh.txt((DECK_HEADROOM, len(AGES)*7+7), f'DECK {frac(DECK_HEADROOM)}', 6.4, ACCENT, "c", True)
    sh.txt((30, -9), "STANDING HEADROOM vs AGE", 9.5, INK, "c", True)

    block(c, 56, 280, (sh.W-120)*0.46, [
        "WHAT THE CHART SAYS",
        "· The DEN is a stand-up room only until about 3. After that it is",
        "  a sit-down cave, which is exactly what a 5-year-old wants it to be.",
        "  It never stops working; it just changes job.",
        "· The DECK takes a standing child to about 8. Past that they sit up",
        "  there, which is still where kids read and hide at that age.",
        "· An adult can never stand on the deck. That is deliberate. If you",
        "  could, they would want you up there, and 22 sq ft is a two-kid deck.",
        "",
        "THE HONEST LIFESPAN: 18 MONTHS TO ROUGHLY 9 OR 10.",
        "The bridge in phase 3 is what buys the last three years of it."],
        y_min=74, size=7.7, lead=11.0)

    # ---------- checklist ----------
    X = 56 + (sh.W-120)*0.50
    CW = (sh.W-120)*0.50
    items = [
     ("ADULT ACCESS — THE ONE PEOPLE FORGET", [
       "If a two-year-old bumps their head inside the den, you have to get to them.",
       'The hobbit door is 24-1/2" x 31-1/4" finished. An adult CAN crawl it, barely.',
       "So: screw the B-C knee-wall skin panel on, never glue and never nail it.",
       "Eight screws and the whole panel comes off in about a minute. Mark the",
       "screw heads with a dab of paint so you can find them in a hurry."]),
     ("AIR", [
       "Plywood floor above, plywood skin around, one sealed acrylic porthole.",
       "Drill a pattern of 1-1/4\" holes near the top of two panels. Read as a",
       "design detail, and they vent the box.",
       "Use 1-1/4\", never 3/8\" to 1\" — that range is a finger-entrapment size."]),
     ("SPLINTERS BEAT AESTHETICS AT THIS AGE", [
       "Rough-sawn is the look you want and the worst possible surface for an",
       "18-month-old who mouths everything.",
       "Wire-brush and stain only what nobody grips: posts ABOVE the deck, roof",
       "trim, the gable. Sand every graspable surface to 150-180 — balusters,",
       "top rails, rungs, grab rails, door edges, the whole den interior.",
       "Run a bare forearm over every surface below 40\" before you let him in."]),
     ("STORING THE LADDER", [
       "Lay it FLAT behind the playhouse or strap it to a wall. A ladder leaning",
       "against a wall is the single most tippable object in the room, and a",
       "toddler will pull on it precisely because it is new and out of place."]),
     ("NO CORDS. NONE.", [
       "Battery puck lights only, with the battery cover screwed shut.",
       "No plug-in string lights, no extension cords, no lamp on the deck.",
       "A cord at 44\" is a strangulation hazard and a trip hazard at once."]),
     ("RE-CHECK SCHEDULE — write the date on the ledger in pencil", [
       "30 days: re-torque every lag. Green lumber shrinks and they WILL be loose.",
       "Every 6 months: lags again, gate closes and latches, ladder pins present,",
       "  no baluster gap grown past 3-1/2\", no splinters, no protruding screws.",
       "Every spring: re-coat anything that has worn through to bare wood."]),
    ]
    y = sh.H-130
    for title, lines in items:
        c.setFillColor(HexColor("#dfe6d6")); c.rect(X, y-3.5, CW, 13, stroke=0, fill=1)
        c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 8.2); c.drawString(X+6, y, title)
        y -= 16
        for ln in lines:
            c.setFont("Helvetica", 7.5)
            c.setFillColor(RED if ("never" in ln or "NEVER" in ln or "strangulation" in ln
                                   or "entrapment" in ln) else INK)
            c.drawString(X+6, y, ln); y -= 10.2
        y -= 7
