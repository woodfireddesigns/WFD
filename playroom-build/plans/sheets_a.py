"""Sheets: cover, room plan, loft framing plan."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G
from drawkit import *

def cover(sh, notes):
    c = sh.c; W, H = sh.W, sh.H
    c.saveState(); c.setFillColor(HexColor("#20301f")); c.rect(0, H-268, W, 268, stroke=0, fill=1)
    c.setFillColor(HexColor("#e8e2d2")); c.setFont("Helvetica-Bold", 44)
    c.drawString(54, H-118, "KIDS' PLAYROOM BUILD")
    c.setFont("Helvetica", 17); c.setFillColor(HexColor("#b9c4a8"))
    c.drawString(56, H-146, "Corner Loft  ·  Rope Bridge  ·  Ranger's Outpost Playhouse")
    c.setFont("Helvetica", 9.5); c.setFillColor(HexColor("#8d9a80"))
    c.drawString(56, H-172, "CONSTRUCTION DOCUMENT SET  ·  dimensional lumber + stock hardware only  ·  generated from the parametric Blender model")
    c.setFont("Helvetica-Bold", 10); c.setFillColor(HexColor("#d8cfa8"))
    c.drawString(56, H-206, f'ROOM  {frac(ROOM_W)} x {frac(ROOM_D)}   ·   CEILING  {frac(CEILING)}   ·   PLATFORM  {frac(DECK_TOP)}   ·   GUARD  {frac(GUARD_H)}')
    c.restoreState()

    y = H-310
    c.setFillColor(RED); c.setFont("Helvetica-Bold", 15)
    c.drawString(54, y, "READ FIRST — THREE SPECS IN THE BRIEF ARE NOT BUILDABLE AS WRITTEN")
    y -= 10
    c.setStrokeColor(RED); c.setLineWidth(1.6); c.line(54, y, W-54, y); y -= 26
    for i, (t, was, now, why) in enumerate(notes, 1):
        c.setFillColor(HexColor("#fdf6ef")); c.setStrokeColor(HexColor("#d8c3ac")); c.setLineWidth(0.8)
        c.rect(54, y-76, W-108, 84, stroke=1, fill=1)
        c.setFillColor(RED); c.setFont("Helvetica-Bold", 11); c.drawString(68, y-6, f"{i}.  {t}")
        c.setFont("Helvetica-Bold", 8.6); c.setFillColor(HexColor("#6b6b6b"))
        c.drawString(68, y-24, "BRIEF SAID"); c.drawString(250, y-24, "THIS SET USES")
        c.setFont("Helvetica-Bold", 10.5); c.setFillColor(HexColor("#8a3b12"))
        c.drawString(68, y-40, was); c.setFillColor(ACCENT); c.drawString(250, y-40, now)
        c.setFont("Helvetica", 8.4); c.setFillColor(INK)
        for j, ln in enumerate(why):
            c.drawString(68, y-58-j*10.5, ln)
        y -= 96

    # sheet index
    c.setFont("Helvetica-Bold", 12); c.setFillColor(INK); c.drawString(54, y-4, "SHEET INDEX")
    c.setLineWidth(1); c.setStrokeColor(INK); c.line(54, y-12, 470, y-12)
    idx = [("A0","Cover · critical notes · sheet index"),
           ("A1","Overall room plan · structure locations · wall anchor zones"),
           ("A2","Loft — deck framing plan · hexagon geometry · joist layout"),
           ("A3","Loft — developed elevation of all four open faces"),
           ("A4","Loft — knee wall framing · hobbit door · arch template"),
           ("A5","Ladder detail · bookshelf guard detail"),
           ("A6","Playhouse — plan · elevations · roof framing"),
           ("A7","Rope bridge — elevation · anchor details · load path"),
           ("A8","Cut list (by structure, by stock)"),
           ("A9","Hardware schedule · Home Depot buy list"),
           ("A10","Photoreal reference views"),
           ("A11","Technical model views")]
    yy = y-28
    for s, t in idx:
        c.setFont("Helvetica-Bold", 8.6); c.setFillColor(ACCENT); c.drawString(58, yy, s)
        c.setFont("Helvetica", 8.6); c.setFillColor(INK); c.drawString(94, yy, t); yy -= 13.5

    # quick stats panel
    px = W-470
    c.setFillColor(HexColor("#f2efe6")); c.setStrokeColor(HexColor("#cfc8b6"))
    c.rect(px, y-190, 416, 208, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 12); c.setFillColor(INK); c.drawString(px+18, y-4, "AT A GLANCE")
    rows = [("Loft deck area", "21.75 sq ft  (60\" x 60\" envelope, hexagonal)"),
            ("Loft deck shape", "6-sided · angles 90/90/157.5/135/157.5/90"),
            ("Miter angles required", "11-1/4 deg and 22-1/2 deg — both saw detents"),
            ("Posts", "6 at the loft (5 tall + 1 corner stub), 4 at the playhouse"),
            ("Bridge clear span", f'{frac(BRIDGE_SPAN)}  ·  net {frac(BRIDGE_W)} wide'),
            ("Guard height", f'{frac(GUARD_H)} above deck (top of the 32-36" range)'),
            ("Total 4x4 PT", "~65 lf     Total 2x4: ~127 lf     2x6: ~46 lf"),
            ("Plywood", "3 sheets 3/4\" (2 structural, 1 skin/doors)"),
            ("Est. material cost", "$1,050 - $1,350 — see sheet A9"),
            ("Build time", "2 weekends for 1 person with a helper")]
    yy = y-26
    for a, b in rows:
        c.setFont("Helvetica-Bold", 8.2); c.setFillColor(HexColor("#5a5a5a")); c.drawString(px+18, yy, a)
        c.setFont("Helvetica", 8.4); c.setFillColor(INK); c.drawString(px+170, yy, b); yy -= 17

def room_plan(sh):
    sh.view(76, 96, sh.W-360, sh.H-208, -62, -62, ROOM_W+56, ROOM_D+46)
    # walls
    t = 5.0
    sh.poly([(-t,-t),(ROOM_W+t,-t),(ROOM_W+t,ROOM_D+t),(-t,ROOM_D+t)], fill=FILL2, stroke=INK, w=1.4)
    sh.poly([(0,0),(ROOM_W,0),(ROOM_W,ROOM_D),(0,ROOM_D)], fill=HexColor("#fbfaf6"), stroke=INK, w=1.4)
    # room door
    sh.poly([(ROOM_DOOR_X,-t),(ROOM_DOOR_X+ROOM_DOOR_W,-t),(ROOM_DOOR_X+ROOM_DOOR_W,0),(ROOM_DOOR_X,0)],
            fill=HexColor("#fbfaf6"), stroke=None)
    sh.arc_seg((ROOM_DOOR_X, 0), ROOM_DOOR_W, 0, 88, THIN, 0.6)
    sh.line((ROOM_DOOR_X, 0), (ROOM_DOOR_X, ROOM_DOOR_W), THIN, 0.8)
    sh.txt((ROOM_DOOR_X+ROOM_DOOR_W/2, -17), "ROOM DOOR", 6.4, THIN, "c")
    # stud layout on the two anchor walls
    n = 0
    while n*STUD_OC <= ROOM_W:
        sh.line((n*STUD_OC, ROOM_D), (n*STUD_OC, ROOM_D+t), RED, 0.5); n += 1
    n = 0
    while n*STUD_OC <= ROOM_D:
        sh.line((0, ROOM_D-n*STUD_OC), (-t, ROOM_D-n*STUD_OC), RED, 0.5); n += 1
    sh.txt((ROOM_W*0.34, ROOM_D+13), 'STUDS @ 16" O.C. ASSUMED — VERIFY WITH A STUD FINDER BEFORE DRILLING', 6.6, RED, "c", True)
    # loft hexagon
    pts = [G.RM[k] for k in G.ORDER]
    sh.poly(pts, fill=HexColor("#dfe6d6"), stroke=ACCENT, w=1.6)
    for k in G.ORDER:
        x, y = G.RM[k]
        sh.circle((x, y), 2.2, fill=HexColor("#5a4632"), stroke=INK, w=0.7)
    sh.txt((7, ROOM_D-74), "STRUCTURE 1", 9, ACCENT, "l", True)
    sh.txt((7, ROOM_D-86), "CORNER LOFT", 12, INK, "l", True)
    sh.txt((7, ROOM_D-96), 'apothecary / naturalist', 6.8, THIN)
    sh.txt((7, ROOM_D-105), f'deck {frac(DECK_TOP)} A.F.F.', 6.8, THIN)
    # playhouse
    sh.poly([(PH_X0,PH_Y0),(ROOM_W,PH_Y0),(ROOM_W,ROOM_D),(PH_X0,ROOM_D)],
            fill=HexColor("#e4dccb"), stroke=ACCENT, w=1.6)
    for k, (x, y) in G.PH_POSTS.items():
        sh.poly([(x-1.75,y-1.75),(x+1.75,y-1.75),(x+1.75,y+1.75),(x-1.75,y+1.75)],
                fill=HexColor("#5a4632"), stroke=INK, w=0.6)
    sh.txt((PH_X0+5, PH_Y0+40), "STRUCTURE 2", 9, ACCENT, "l", True)
    sh.txt((PH_X0+5, PH_Y0+29), "PLAYHOUSE", 12, INK, "l", True)
    sh.txt((PH_X0+5, PH_Y0+19), "ranger's outpost", 6.8, THIN)
    sh.txt((PH_X0+5, PH_Y0+10), f'{frac(PH_SIZE)} sq · full height', 6.8, THIN)
    # bridge
    y0, y1 = G.BR_Y0, G.BR_Y1
    sh.poly([(BRIDGE_X0,y0),(BRIDGE_X1,y0),(BRIDGE_X1,y1),(BRIDGE_X0,y1)],
            fill=HexColor("#efe7d2"), stroke=NOTE, w=1.2, dash=(3,2))
    for i in range(9):
        x = BRIDGE_X0 + (BRIDGE_X1-BRIDGE_X0)*(i+0.5)/9
        sh.line((x, y0), (x, y1), NOTE, 0.6)
    sh.txt(((BRIDGE_X0+BRIDGE_X1)/2, y0-13), "ROPE / CARGO NET BRIDGE", 7, NOTE, "c", True)
    # ladder
    lb, lt = G.LADDER_BOT, G.LADDER_TOP
    d = G.LADDER_DIR
    sh.poly([(lt[0]-d[0]*9, lt[1]-d[1]*9), (lt[0]+d[0]*9, lt[1]+d[1]*9),
             (lb[0]+d[0]*9, lb[1]+d[1]*9), (lb[0]-d[0]*9, lb[1]-d[1]*9)],
            fill=HexColor("#e7dcc6"), stroke=NOTE, w=1.0, dash=(3,2))
    sh.leader(((lb[0]+lt[0])/2, (lb[1]+lt[1])/2), (-58, -30), "LADDER — 65 deg, rope handrails", 6.2, NOTE, "r")
    # overall dims
    sh.dim((0, 0), (ROOM_W, 0), -34, f'{frac(ROOM_W)}  ROOM WIDTH')
    sh.dim((ROOM_W, 0), (ROOM_W, ROOM_D), -34, f'{frac(ROOM_D)}  ROOM DEPTH')
    sh.dim((0, ROOM_D), (LOFT_SIZE, ROOM_D), 22, frac(LOFT_SIZE))
    sh.dim((LOFT_SIZE, ROOM_D), (PH_X0, ROOM_D), 22, f'{frac(BRIDGE_SPAN)} CLEAR')
    sh.dim((PH_X0, ROOM_D), (ROOM_W, ROOM_D), 22, frac(PH_SIZE))
    sh.dim((0, ROOM_D), (0, ROOM_D-LOFT_SIZE), 22, frac(LOFT_SIZE), flip=True)
    sh.dim((ROOM_W, ROOM_D), (ROOM_W, PH_Y0), 22, frac(PH_SIZE))
    # side notes
    c = sh.c; x = sh.W-236; y = sh.H-118
    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK); c.drawString(x, y, "LOAD PATH")
    c.setLineWidth(1); c.line(x, y-7, sh.W-64, y-7)
    for i, s in enumerate([
        "The wall ledgers carry the real load.",
        "Posts are secondary / aesthetic.",
        "",
        "LOFT: two 2x6 PT ledgers, one on the",
        "north wall and one on the west wall,",
        '3/8" x 4" lag + washer into EVERY stud.',
        "",
        "PLAYHOUSE: north and east posts",
        "lag-bolted directly to wall studs.",
        "",
        "BRIDGE: both ends through-bolted",
        "into 2x6 ledgers that are themselves",
        "lagged into a minimum of 2 studs.",
        'Eye BOLTS with washer + nylock nut.',
        "Never screw eyes.",
        "",
        "VERIFY STUD SPACING ON SITE.",
        "16\" O.C. is assumed throughout; if",
        "your studs are 24\" O.C. or irregular,",
        "shift ledger bolt locations to land on",
        "wood and add a bolt — do not rely on",
        "drywall anchors anywhere in this set.",
    ]):
        c.setFont("Helvetica-Bold" if s.isupper() and s else "Helvetica", 7.6)
        c.setFillColor(RED if "VERIFY" in s or "Never" in s else INK)
        c.drawString(x, y-24-i*11.6, s)

def loft_framing_plan(sh):
    """Drawn north-up, matching A1. Local frame: x = u (west->east), y = 60 - v (south->north)."""
    P = {n: (u, LOFT_SIZE - v) for n, u, v in LOFT_POLY}
    O = [n for n, _, _ in LOFT_POLY]
    cx = sum(P[n][0] for n in O)/6.0; cy = sum(P[n][1] for n in O)/6.0
    def inw(a, b):
        (x0,y0),(x1,y1) = P[a],P[b]; L = math.hypot(x1-x0,y1-y0)
        d = ((x1-x0)/L,(y1-y0)/L); n = (-d[1],d[0])
        mx,my = (x0+x1)/2,(y0+y1)/2
        return n if ((cx-mx)*n[0]+(cy-my)*n[1]) > 0 else (-n[0],-n[1]), d, L
    def band(a, b, t, fill):
        n,d,L = inw(a,b); p0,p1 = P[a],P[b]
        sh.poly([p0, p1, (p1[0]+n[0]*t, p1[1]+n[1]*t), (p0[0]+n[0]*t, p0[1]+n[1]*t)],
                fill=fill, stroke=INK, w=1.0)

    sh.view(78, 104, sh.W-430, sh.H-206, -34, -30, LOFT_SIZE+30, LOFT_SIZE+34)
    # walls
    sh.poly([(-5,LOFT_SIZE),(LOFT_SIZE+16,LOFT_SIZE),(LOFT_SIZE+16,LOFT_SIZE+5),(-5,LOFT_SIZE+5)],
            fill=FILL2, stroke=INK, w=1.0)
    sh.poly([(-5,-16),(0,-16),(0,LOFT_SIZE+5),(-5,LOFT_SIZE+5)], fill=FILL2, stroke=INK, w=1.0)
    sh.txt((LOFT_SIZE*0.42, LOFT_SIZE+8.5), "NORTH WALL", 6.6, THIN, "c", True)
    sh.txt((-9.5, LOFT_SIZE*0.42), "WEST WALL", 6.6, THIN, "c", True, rot=90)
    n = 0
    while n*STUD_OC <= LOFT_SIZE:
        sh.line((n*STUD_OC, LOFT_SIZE), (n*STUD_OC, LOFT_SIZE+5), RED, 0.6)
        sh.line((-5, LOFT_SIZE-n*STUD_OC), (0, LOFT_SIZE-n*STUD_OC), RED, 0.6); n += 1

    # deck outline
    sh.poly([P[n] for n in O], fill=HexColor("#f6f3ea"), stroke=ACCENT, w=2.0)
    # ledgers (north + west walls)
    sh.poly([(0,LOFT_SIZE),(LOFT_SIZE,LOFT_SIZE),(LOFT_SIZE,LOFT_SIZE-T_2X),(0,LOFT_SIZE-T_2X)],
            fill=HexColor("#c4a874"), stroke=INK, w=1.0)
    sh.poly([(0,0),(T_2X,0),(T_2X,LOFT_SIZE-T_2X),(0,LOFT_SIZE-T_2X)],
            fill=HexColor("#c4a874"), stroke=INK, w=1.0)
    sh.txt((LOFT_SIZE*0.33, LOFT_SIZE-4.6), 'LEDGER N — 2x6 PT x 60"', 5.6, HexColor("#4a3520"), "c", True)
    sh.txt((4.6, LOFT_SIZE*0.30), 'LEDGER W — 2x6 PT x 58-1/2"', 5.6, HexColor("#4a3520"), "c", True, rot=90)
    # rim joists
    for a, b in [("B","C"),("C","D"),("D","Cp"),("Cp","Bp")]:
        band(a, b, T_2X, HexColor("#c4a874"))
    # field joists
    v = JOIST_OC; i = 1
    while v < LOFT_SIZE - 1:
        ue = G.east_edge(v); yy = LOFT_SIZE - v
        sh.poly([(T_2X, yy-T_2X/2),(ue-T_2X, yy-T_2X/2),(ue-T_2X, yy+T_2X/2),(T_2X, yy+T_2X/2)],
                fill=HexColor("#e5d8b8"), stroke=INK, w=0.8)
        sh.txt((T_2X+3.5, yy-1.9), f'J{i}   2x6   {frac(ue-2*T_2X)}', 5.6, HexColor("#3a2c18"), "l", True)
        i += 1; v += JOIST_OC
    # posts
    for n in O:
        x, y = P[n]; tall = n in LOFT_TALL_POSTS
        fillc = HexColor("#6f5436") if tall else HexColor("#b6a283")
        if n == "D":
            r = POST/2*1.4142
            sh.poly([(x-r,y),(x,y-r),(x+r,y),(x,y+r)], fill=fillc, stroke=INK, w=1.0)
        else:
            ox = -POST if x > LOFT_SIZE/2 else 0
            oy = -POST if y > LOFT_SIZE/2 else 0
            sh.poly([(x+ox,y+oy),(x+ox+POST,y+oy),(x+ox+POST,y+oy+POST),(x+ox,y+oy+POST)],
                    fill=fillc, stroke=INK, w=1.0)
        sh.circle((x, y), 0.9, fill=RED, stroke=None)
        lx = x + (5.5 if x < LOFT_SIZE*0.55 else -5.5)
        ly = y + (-8.5 if y > LOFT_SIZE*0.55 else 5.0)
        sh.txt((lx, ly), n, 8.5, RED, "l" if x < LOFT_SIZE*0.55 else "r", True)
    # dimension strings
    sh.dim(P["A"], P["B"], 22, frac(LOFT_SIZE))
    sh.dim(P["Bp"], P["A"], 22, frac(LOFT_SIZE))
    sh.dim(P["B"], P["C"], -13, frac(HEX_H))
    sh.dim(P["C"], P["D"], -13, frac(HEX_T))
    sh.dim(P["D"], P["Cp"], -13, frac(HEX_T))
    sh.dim(P["Cp"], P["Bp"], -13, frac(HEX_H))
    # joist spacing string
    yv = LOFT_SIZE
    for k in range(3):
        sh.dim((LOFT_SIZE*0.30, yv), (LOFT_SIZE*0.30, yv-JOIST_OC), 0, '16" O.C.' if k == 0 else '16"')
        yv -= JOIST_OC
    # corner cut-back
    sh.line((LOFT_SIZE, LOFT_SIZE), (LOFT_SIZE, 0), THIN, 0.5, (2,2))
    sh.line((0, 0), (LOFT_SIZE, 0), THIN, 0.5, (2,2))
    sh.line((LOFT_SIZE, 0), P["D"], RED, 0.8, (3,2))
    sh.txt((LOFT_SIZE-5, 5.5), f'{frac(math.hypot(LOFT_SIZE-P["D"][0], P["D"][1]))} CUT-BACK', 5.8, RED, "r", True)
    # annotations
    sh.leader(P["C"], (46, 30), "157-1/2 deg   miter 11-1/4 deg each side", 6.0)
    sh.leader(P["D"], (50, -6), "135 deg   miter 22-1/2 deg each side", 6.0)
    sh.leader(P["Cp"], (-16, -48), "157-1/2 deg   miter 11-1/4 deg each side", 6.0, anchor="r")
    mid = lambda a, b: ((P[a][0]+P[b][0])/2, (P[a][1]+P[b][1])/2)
    sh.leader(mid("B","C"), (52, 14), "BRIDGE GATE — net lands here", 6.2)
    sh.leader(mid("Cp","Bp"), (-30, -34), "LADDER ENTRY", 6.2, anchor="r")
    sh.leader(mid("C","D"), (54, -34), "BOOKSHELF GUARD  (A5)", 6.2)
    sh.leader(mid("D","Cp"), (10, -50), "ROPE NET GUARD  ·  HOBBIT DOOR BELOW  (A3/A4)", 6.2)
    sh.leader((LOFT_SIZE*0.55, LOFT_SIZE-JOIST_OC), (34, 40), 'JOISTS 2x6 @ 16" O.C. — hung off LEDGER W', 6.0)

    # side panel
    c = sh.c; x = sh.W-346; y = sh.H-120
    c.setFont("Helvetica-Bold", 11); c.setFillColor(INK); c.drawString(x, y, "HEXAGON GEOMETRY — RESOLVED")
    c.setLineWidth(1); c.setStrokeColor(INK); c.line(x, y-7, sh.W-64, y-7)
    hdr = ("VERTEX", "u (in)", "v (in)", "POST CUT")
    yy = y-22
    c.setFont("Helvetica-Bold", 7.4); c.setFillColor(HexColor("#5a5a5a"))
    for j, h in enumerate(hdr): c.drawString(x + j*72, yy, h)
    c.setLineWidth(0.6); c.line(x, yy-4, x+282, yy-4); yy -= 14
    for n, u, v in LOFT_POLY:
        c.setFont("Helvetica-Bold", 7.6); c.setFillColor(RED); c.drawString(x, yy, n)
        c.setFont("Helvetica", 7.6); c.setFillColor(INK)
        c.drawString(x+72, yy, f"{u:.3f}"); c.drawString(x+144, yy, f"{v:.3f}")
        c.drawString(x+216, yy, '4x4 x 80"' if n in LOFT_TALL_POSTS else '4x4 x 37-3/4"')
        yy -= 13
    yy -= 14
    for s in ["WHY THIS SHAPE",
              "A 45-degree chamfer of one corner gives a PENTAGON,",
              "not a hexagon — the two cut edges come out collinear,",
              "so the middle vertex is not a corner at all.",
              "",
              "A true 6-sided deck inside a 60 x 60 corner needs two",
              "22-1/2 degree joints flanking one 45 degree joint.",
              "Interior angles: 90 / 90 / 157-1/2 / 135 / 157-1/2 / 90.",
              "They sum to 720, as a hexagon must.",
              "",
              "Every miter is therefore 11-1/4 or 22-1/2 degrees.",
              "Both are detents on any 10-inch miter saw. Nothing",
              "in this deck needs a custom angle or a bevel gauge.",
              "",
              "DECK AREA   21.75 SQ FT",
              "Both 60-inch wall runs stay full length, so both ledgers",
              "get maximum stud engagement. That is the whole point",
              "of cutting the outer corner instead of the wall corners.",
              "",
              "JOIST NOTES",
              "J1 is square both ends — Simpson LUS26 hangers.",
              "J2 and J3 die into an angled rim. Use Simpson LSU26",
              "adjustable skewable U hangers (Internet # 100375129),",
              "field-bent to the angle shown. Alternatively bevel the",
              "joist end and add a 2x6 cleat underneath.",
              "Do not toe-nail either one.",
              "",
              "POST D sits at 45 degrees so its faces meet both",
              "angled rims squarely. Cut its notches before standing."]:
        up = s.isupper() and s
        c.setFont("Helvetica-Bold" if up else "Helvetica", 7.5)
        c.setFillColor(ACCENT if up else INK)
        c.drawString(x, yy, s); yy -= 11.2
