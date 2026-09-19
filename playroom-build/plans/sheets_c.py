"""Sheets: ladder + bookshelf, playhouse, bridge."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G
from drawkit import *

def ladder_and_shelf(sh):
    # ---------- LADDER ELEVATION ----------
    sh.view(70, 118, (sh.W-170)*0.40, sh.H-250, -16, -10, LADDER_RUN+30, POST_TOP+16)
    sh.line((-14, 0), (LADDER_RUN+26, 0), INK, 1.6)
    # post + deck
    sh.poly([(0,0),(POST,0),(POST,POST_TOP),(0,POST_TOP)], fill=HexColor("#8a6a44"), stroke=INK, w=1.0)
    sh.poly([(-14,JOIST_BOT),(POST,JOIST_BOT),(POST,JOIST_TOP),(-14,JOIST_TOP)], fill=HexColor("#cdb98f"), stroke=INK, w=0.9)
    sh.poly([(-14,JOIST_TOP),(POST,JOIST_TOP),(POST,DECK_TOP),(-14,DECK_TOP)], fill=HexColor("#e0d3b2"), stroke=INK, w=0.7)
    sh.poly([(-14,0),(0,0),(0,KNEE_TOTAL),(-14,KNEE_TOTAL)], fill=HexColor("#dfe4d4"), stroke=INK, w=0.7)
    sh.txt((-7, DECK_TOP+6), "LOFT", 6.4, ACCENT, "c", True)
    ang = math.radians(LADDER_ANGLE)
    bx = LADDER_RUN
    for off in (0.0, W_2X4):
        p0 = (bx + off*math.sin(ang), 0 + off*0)
    # stringer as a rotated rectangle
    dx, dz = math.cos(math.pi - ang), math.sin(math.pi - ang)
    sp0 = (bx, 0); sp1 = (POST+0.5, DECK_TOP)
    nx, nz = (sp1[1]-sp0[1]), -(sp1[0]-sp0[0])
    m = math.hypot(nx, nz); nx, nz = nx/m*W_2X4, nz/m*W_2X4
    sh.poly([sp0, sp1, (sp1[0]+nx, sp1[1]+nz), (sp0[0]+nx, sp0[1]+nz)],
            fill=HexColor("#a5804f"), stroke=INK, w=1.2)
    for k in range(1, LADDER_RUNGS+1):
        t = k/(LADDER_RUNGS+1)
        rx = sp0[0]+(sp1[0]-sp0[0])*t; rz = k*LADDER_RISER
        sh.poly([(rx-1.9, rz-0.75),(rx+1.9, rz-0.75),(rx+1.9, rz+0.75),(rx-1.9, rz+0.75)],
                fill=HexColor("#c8a468"), stroke=INK, w=0.9)
        sh.dim((rx+8, rz-LADDER_RISER), (rx+8, rz), 10 if k == 1 else 10, frac(LADDER_RISER) if k == 1 else "")
    sh.dim((bx+16, 0), (bx+16, DECK_TOP), 8, f'RISE {frac(DECK_TOP)}')
    sh.dim((0, -6), (bx, -6), -14, f'RUN {frac(LADDER_RUN)}')
    sh.arc_seg((bx, 0), 12, 115, 180, RED, 1.0)
    sh.txt((bx-17, 5), "65 deg", 6.6, RED, "c", True)
    sh.leader(((sp0[0]+sp1[0])/2, (sp0[1]+sp1[1])/2), (24, 28),
              f'STRINGER 2x4 · {frac(LADDER_LEN)} o/a · both ends cut 25 deg')
    sh.leader((sp0[0]+nx/2, 1.5), (18, -26), 'Floor foot: Simpson ABU44 standoff OR 2x4 cleat lagged to subfloor')
    n = 22
    for zt, sag in ((POST_TOP-4, 2.2), (POST_TOP-16, 1.6)):
        pts = [(sp0[0]+(POST-sp0[0])*i/n,
                (7 + (zt-7)*i/n) - sag*math.sin(math.pi*i/n)) for i in range(n+1)]
        for i in range(n): sh.line(pts[i], pts[i+1], NOTE, 2.0)
    sh.leader((sp0[0]*0.55+POST*0.45, 44), (-46, 40), '3/4" poly rope handrail both sides — eye bolt at the', 6.0, anchor="r")
    sh.leader((sp0[0]*0.55+POST*0.45, 36), (-46, 24), 'post top, floor anchor plate at the bottom', 6.0, anchor="r")
    sh.txt((LADDER_RUN/2, POST_TOP+10), "LADDER ELEVATION", 9.5, INK, "c", True)

    # ---------- LADDER PLAN ----------
    sh.view(70+(sh.W-170)*0.40, 190, (sh.W-170)*0.22, (sh.H-250)*0.52, -10, -34, LADDER_W+16, LADDER_RUN+18)
    for s in (0, LADDER_W-T_2X):
        sh.poly([(s,0),(s+T_2X,0),(s+T_2X,LADDER_RUN),(s,LADDER_RUN)], fill=HexColor("#a5804f"), stroke=INK, w=0.9)
    for k in range(1, LADDER_RUNGS+1):
        ry = LADDER_RUN*(1-k/(LADDER_RUNGS+1))
        sh.poly([(T_2X,ry-1.75),(LADDER_W-T_2X,ry-1.75),(LADDER_W-T_2X,ry+1.75),(T_2X,ry+1.75)],
                fill=HexColor("#c8a468"), stroke=INK, w=0.8)
    sh.dim((0,0),(LADDER_W,0), -12, f'{frac(LADDER_W)} O/A')
    sh.dim((T_2X,LADDER_RUN),(LADDER_W-T_2X,LADDER_RUN), 12, f'{frac(LADDER_W-2*T_2X)} CLEAR')
    sh.txt((LADDER_W/2, LADDER_RUN+13), "LADDER PLAN", 9.5, INK, "c", True)
    sh.txt((LADDER_W/2, -15), 'Rungs: 2x4, dado 3/4" deep into stringers', 6.2, INK, "c")
    sh.txt((LADDER_W/2, -22), '+ two #9 x 3" screws each end. Sand every', 6.2, INK, "c")
    sh.txt((LADDER_W/2, -29), 'edge to 150 grit — bare feet and bare hands.', 6.2, INK, "c")

    # ---------- BOOKSHELF ----------
    ox = 70+(sh.W-170)*0.64
    sh.view(ox, 300, (sh.W-170)*0.30, sh.H-424, -8, -10, G.SHELF_CLEAR+14, SHELF_H+26)
    sh.poly([(0,0),(G.SHELF_CLEAR,0),(G.SHELF_CLEAR,SHELF_H),(0,SHELF_H)],
            fill=HexColor("#f0e9d8"), stroke=INK, w=1.4)
    for k in range(SHELF_COUNT+2):
        z = k*SHELF_H/(SHELF_COUNT+1)
        sh.poly([(0,z),(G.SHELF_CLEAR,z),(G.SHELF_CLEAR,z+PLY),(0,z+PLY)], fill=HexColor("#c7ab7c"), stroke=INK, w=0.9)
        if k <= SHELF_COUNT:
            sh.poly([(0,z+PLY),(G.SHELF_CLEAR,z+PLY),(G.SHELF_CLEAR,z+PLY+2.0),(0,z+PLY+2.0)],
                    fill=None, stroke=NOTE, w=1.2, dash=(2,2))
            for bk in range(8):
                bx2 = 1.2+bk*2.5
                if bx2+2 < G.SHELF_CLEAR-1:
                    sh.poly([(bx2,z+PLY),(bx2+1.9,z+PLY),(bx2+1.9,z+PLY+8),(bx2,z+PLY+8)],
                            fill=HexColor("#9aa88c") if bk%2 else HexColor("#b08a5a"), stroke=THIN, w=0.4)
    for jk in range(3):
        jx = G.SHELF_CLEAR-7 + 0
        sh.circle((G.SHELF_CLEAR-4.5, SHELF_H/(SHELF_COUNT+1)*2 + 3.2), 1.9, fill=HexColor("#d8c9a6"), stroke=INK, w=0.7)
    sh.dim((0,-2),(G.SHELF_CLEAR,-2), -12, frac(G.SHELF_CLEAR))
    sh.dim((G.SHELF_CLEAR+1,0),(G.SHELF_CLEAR+1,SHELF_H), 12, frac(SHELF_H))
    for k in range(SHELF_COUNT+1):
        z0 = k*SHELF_H/(SHELF_COUNT+1)+PLY; z1 = (k+1)*SHELF_H/(SHELF_COUNT+1)
        sh.dim((-1.5,z0),(-1.5,z1), 9, frac(z1-z0), flip=True)
    sh.txt((G.SHELF_CLEAR/2, SHELF_H+22), "BOOKSHELF GUARD — ELEVATION", 9.5, INK, "c", True)
    sh.txt((G.SHELF_CLEAR/2, SHELF_H+14), f'fits between posts C and D · {frac(SHELF_DEPTH)} deep', 6.4, THIN, "c")
    c = sh.c
    block(c, ox, 272, (sh.W-170)*0.30, [
        "THIS SECTION IS A GUARDRAIL FIRST, A SHELF SECOND.",
        '· Carcass: 3/4" ply, dadoed shelves, glued + screwed.',
        '· Lag the two ends to posts C and D with 4x 1/4" x 3"',
        "  lag screws each — 2 top, 2 bottom. It must not rack.",
        '· 1/4" roundover on every exposed edge, then sand 150.',
        '· 2" book lip on the deck side of every shelf.',
        "· Apothecary jars: HDPE or PET only. No glass, no",
        "  mason jars. Dried botanicals, acorns, pinecones.",
        '· Hot-glue or silicone the jar bases to the shelf.',
        "· Nothing heavier than 2 lb above 24\" off the deck."],
        y_min=74, size=7.4, lead=10.4)

def playhouse(sh):
    # ---- plan ----
    sh.view(70, 130, (sh.W-170)*0.36, sh.H-260, PH_X0-16, PH_Y0-16, ROOM_W+16, ROOM_D+16)
    sh.poly([(PH_X0-14,ROOM_D),(ROOM_W+14,ROOM_D),(ROOM_W+14,ROOM_D+5),(PH_X0-14,ROOM_D+5)], fill=FILL2, stroke=INK, w=1.0)
    sh.poly([(ROOM_W,PH_Y0-14),(ROOM_W+5,PH_Y0-14),(ROOM_W+5,ROOM_D+5),(ROOM_W,ROOM_D+5)], fill=FILL2, stroke=INK, w=1.0)
    sh.poly([(PH_X0,PH_Y0),(ROOM_W,PH_Y0),(ROOM_W,ROOM_D),(PH_X0,ROOM_D)],
            fill=HexColor("#f4f1e6"), stroke=ACCENT, w=2.0)
    for n, (x, y) in G.PH_POSTS.items():
        sh.poly([(x-1.75,y-1.75),(x+1.75,y-1.75),(x+1.75,y+1.75),(x-1.75,y+1.75)],
                fill=HexColor("#7a5c3a"), stroke=INK, w=0.9)
        sh.txt((x, y+5), n, 7.4, RED, "c", True)
    # ridge
    rx = PH_X0+PH_SIZE/2
    sh.line((rx, PH_Y0-4), (rx, ROOM_D), NOTE, 1.2, (5,3))
    sh.txt((rx+2, PH_Y0+6), "RIDGE", 6.2, NOTE, "l", rot=90)
    # door swing
    dx0 = rx-PH_DOOR_RO_W/2
    sh.arc_seg((dx0, PH_Y0), PH_DOOR_RO_W, -88, 0, THIN, 0.6)
    sh.line((dx0, PH_Y0), (dx0, PH_Y0-PH_DOOR_RO_W), THIN, 0.9)
    sh.txt((rx, PH_Y0-24), "HOBBIT DOOR", 6.4, NOTE, "c", True)
    # bridge bay
    sh.poly([(PH_X0-2, ROOM_D-PH_BRIDGE_BAY),(PH_X0+2, ROOM_D-PH_BRIDGE_BAY),
             (PH_X0+2, ROOM_D),(PH_X0-2, ROOM_D)], fill=HexColor("#efe7d2"), stroke=NOTE, w=1.2)
    sh.leader((PH_X0, ROOM_D-PH_BRIDGE_BAY/2), (-34, -34), "BRIDGE BAY", 6.2, anchor="r")
    sh.dim((PH_X0, PH_Y0), (ROOM_W, PH_Y0), -22, frac(PH_SIZE))
    sh.dim((ROOM_W, PH_Y0), (ROOM_W, ROOM_D), -22, frac(PH_SIZE))
    sh.dim((PH_X0, ROOM_D), (PH_X0, ROOM_D-PH_BRIDGE_BAY), 20, frac(PH_BRIDGE_BAY), flip=True)
    sh.txt((rx, ROOM_D+14), "PLAYHOUSE PLAN", 9.5, INK, "c", True)

    # ---- south elevation ----
    ox = 70+(sh.W-170)*0.38
    sh.view(ox, 130, (sh.W-170)*0.30, sh.H-260, -10, -8, PH_SIZE+10, CEILING+12)
    sh.line((-8, 0), (PH_SIZE+8, 0), INK, 1.6)
    sh.line((-8, CEILING), (PH_SIZE+8, CEILING), THIN, 1.0, (6,3))
    sh.txt((PH_SIZE+9, CEILING-2), f'CEILING {frac(CEILING)}', 5.8, THIN)
    sh.poly([(0,0),(PH_SIZE,0),(PH_SIZE,PH_WALL_H),(0,PH_WALL_H)], fill=HexColor("#e8dfc9"), stroke=INK, w=1.3)
    sh.poly([(0,PH_WALL_H),(PH_SIZE,PH_WALL_H),(PH_SIZE/2,PH_RIDGE-2.75)],
            fill=HexColor("#d9c9a4"), stroke=INK, w=1.3)
    for s in (0, PH_SIZE-POST):
        sh.poly([(s,0),(s+POST,0),(s+POST,PH_WALL_H),(s,PH_WALL_H)], fill=HexColor("#8a6a44"), stroke=INK, w=1.0)
    sh.poly([(-2,PH_WALL_H),(PH_SIZE+2,PH_WALL_H),(PH_SIZE+2,PH_WALL_H+T_2X),(-2,PH_WALL_H+T_2X)],
            fill=HexColor("#cdb98f"), stroke=INK, w=0.9)
    # rake boards
    for s in (-1, 1):
        x1 = PH_SIZE/2 + s*(PH_SIZE/2+2.5)
        sh.line((PH_SIZE/2, PH_RIDGE-1.4), (x1, PH_WALL_H+T_2X-2.0), HexColor("#4a3520"), 3.0)
    # door + window
    dc = PH_SIZE/2; sdz = PH_DOOR_SLAB_H - PH_DOOR_SLAB_W/2
    sh.poly([(dc-PH_DOOR_RO_W/2,0),(dc+PH_DOOR_RO_W/2,0),(dc+PH_DOOR_RO_W/2,PH_DOOR_RO_H),(dc-PH_DOOR_RO_W/2,PH_DOOR_RO_H)],
            fill=HexColor("#fbfaf6"), stroke=RED, w=1.0, dash=(3,2))
    pts = [(dc-PH_DOOR_SLAB_W/2,0),(dc+PH_DOOR_SLAB_W/2,0),(dc+PH_DOOR_SLAB_W/2,sdz)]
    pts += [(dc+PH_DOOR_SLAB_W/2*math.cos(math.radians(t*3.75)), sdz+PH_DOOR_SLAB_W/2*math.sin(math.radians(t*3.75))) for t in range(49)]
    pts += [(dc-PH_DOOR_SLAB_W/2, sdz)]
    sh.poly(pts, fill=HexColor("#3a5a3c"), stroke=INK, w=1.2)
    for s in (-1, 1):
        sh.poly([(dc-PH_DOOR_SLAB_W/2+0.8, sdz/2+s*sdz*0.33),(dc+PH_DOOR_SLAB_W/2*0.7, sdz/2+s*sdz*0.33),
                 (dc+PH_DOOR_SLAB_W/2*0.7, sdz/2+s*sdz*0.33+1.6),(dc-PH_DOOR_SLAB_W/2+0.8, sdz/2+s*sdz*0.33+1.6)],
                fill=INK, stroke=None)
    sh.circle((dc+PH_DOOR_SLAB_W/2-3.5, sdz*0.6), 1.4, fill=HexColor("#4a3520"), stroke=INK, w=0.7)
    sh.circle((dc, PH_WINDOW_Z), PH_WINDOW_D/2, fill=HexColor("#cfe0e2"), stroke=INK, w=1.2)
    sh.circle((dc, PH_WINDOW_Z), PH_WINDOW_D/2+1.0, fill=None, stroke=INK, w=1.6)
    for a in range(0, 360, 90):
        sh.line((dc+PH_WINDOW_D/2*math.cos(math.radians(a)), PH_WINDOW_Z+PH_WINDOW_D/2*math.sin(math.radians(a))),
                (dc-PH_WINDOW_D/2*math.cos(math.radians(a)), PH_WINDOW_Z-PH_WINDOW_D/2*math.sin(math.radians(a))), INK, 0.9)
    sh.dim((-4,0),(-4,PH_WALL_H), 12, frac(PH_WALL_H), flip=True)
    sh.dim((-4,PH_WALL_H),(-4,PH_RIDGE-2.75), 12, frac(PH_RIDGE-2.75-PH_WALL_H), flip=True)
    sh.dim((dc+PH_DOOR_RO_W/2+2, 0),(dc+PH_DOOR_RO_W/2+2, PH_DOOR_RO_H), 9, f'R.O. {frac(PH_DOOR_RO_H)}')
    sh.dim((dc-PH_DOOR_RO_W/2,-3),(dc+PH_DOOR_RO_W/2,-3), -11, f'R.O. {frac(PH_DOOR_RO_W)}')
    sh.dim((PH_SIZE+3, 0),(PH_SIZE+3, PH_WINDOW_Z), 12, f'{frac(PH_WINDOW_Z)} to window c/l')
    sh.txt((PH_SIZE/2, CEILING+6), "SOUTH ELEVATION  (faces the room)", 9.5, INK, "c", True)

    # ---- roof framing ----
    ox2 = 70+(sh.W-170)*0.70
    sh.view(ox2, 300, (sh.W-170)*0.28, sh.H-424, -10, PH_Y0-12, PH_SIZE+10, ROOM_D+12)
    sh.poly([(0,PH_Y0),(PH_SIZE,PH_Y0),(PH_SIZE,ROOM_D),(0,ROOM_D)], fill=HexColor("#f4f1e6"), stroke=INK, w=1.2)
    sh.poly([(PH_SIZE/2-0.75,PH_Y0-2),(PH_SIZE/2+0.75,PH_Y0-2),(PH_SIZE/2+0.75,ROOM_D),(PH_SIZE/2-0.75,ROOM_D)],
            fill=HexColor("#8a6a44"), stroke=INK, w=0.9)
    for i in range(4):
        y = PH_Y0-2 + (ROOM_D-(PH_Y0-2))*i/3
        for s in (-1, 1):
            xe = PH_SIZE/2 + s*(PH_SIZE/2+2)
            sh.poly([(PH_SIZE/2, y-0.75),(xe, y-0.75),(xe, y+0.75),(PH_SIZE/2, y+0.75)],
                    fill=HexColor("#cdb98f"), stroke=INK, w=0.7)
        if i: sh.dim((PH_SIZE*0.22, y-(ROOM_D-(PH_Y0-2))/3),(PH_SIZE*0.22, y), 0, frac((ROOM_D-(PH_Y0-2))/3))
    rise = (PH_RIDGE-2.75)-(PH_WALL_H+T_2X)
    sh.txt((PH_SIZE/2, ROOM_D+6), "ROOF FRAMING PLAN", 9, INK, "c", True)
    sh.txt((PH_SIZE/2, PH_Y0-8), f'8 rafters 2x4 · {rise/(PH_SIZE/2)*12:.2f}:12 pitch · ridge 2x6', 6.2, THIN, "c")

    c = sh.c
    block(c, 70+(sh.W-170)*0.70, 268, (sh.W-170)*0.28, [
        'WALLS STOP AT 84", NOT 96".',
        "A 96\"-tall box under a 96\" ceiling has no room for a",
        "roof. Dropping the wall to 84\" buys a real 10-1/2\"",
        "peaked roof that reads from across the room, and",
        "still leaves 84\" of interior headroom.",
        "",
        "· NW and SE posts lag directly to wall studs:",
        '  3x 3/8" x 4" lag + washer each, staggered.',
        "· SW post is free-standing — anchor with a Simpson",
        "  ABU44Z post base lagged to the subfloor.",
        "· WM post creates the 18\" bridge bay and matches",
        "  the loft gate width. Do not omit it.",
        "· Rope-wrap the SW post full height: 1/2\" poly rope,",
        "  spiral-wound, hot-glued every 6\".",
        "· Rough-saw look: run a wire wheel over the 4x4s,",
        "  then a coat of dark walnut stain wiped back.",
        "· Interior: battery LED lantern on a hook, no wiring.",
        "· Leave the west wall below the bridge bay open or",
        "  slatted so the space does not feel like a closet."],
        y_min=76, size=7.6, lead=11.0, title="PLAYHOUSE NOTES")

def bridge(sh):
    sh.view(64, 112, sh.W-400, sh.H-214, BRIDGE_X0-34, -30, BRIDGE_X1+34, POST_TOP+26)
    sh.line((BRIDGE_X0-26, 0), (BRIDGE_X1+26, 0), INK, 1.6)
    # loft side
    sh.poly([(BRIDGE_X0-24,JOIST_BOT),(BRIDGE_X0,JOIST_BOT),(BRIDGE_X0,DECK_TOP),(BRIDGE_X0-24,DECK_TOP)],
            fill=HexColor("#cdb98f"), stroke=INK, w=1.0)
    sh.poly([(BRIDGE_X0-POST,0),(BRIDGE_X0,0),(BRIDGE_X0,POST_TOP),(BRIDGE_X0-POST,POST_TOP)],
            fill=HexColor("#8a6a44"), stroke=INK, w=1.1)
    sh.poly([(BRIDGE_X0-24,0),(BRIDGE_X0-POST,0),(BRIDGE_X0-POST,KNEE_TOTAL),(BRIDGE_X0-24,KNEE_TOTAL)],
            fill=HexColor("#dfe4d4"), stroke=INK, w=0.8)
    sh.txt((BRIDGE_X0-14, POST_TOP+8), "LOFT (post B)", 7.4, ACCENT, "c", True)
    # playhouse side
    sh.poly([(BRIDGE_X1,0),(BRIDGE_X1+POST,0),(BRIDGE_X1+POST,PH_WALL_H),(BRIDGE_X1,PH_WALL_H)],
            fill=HexColor("#8a6a44"), stroke=INK, w=1.1)
    sh.poly([(BRIDGE_X1+POST,0),(BRIDGE_X1+26,0),(BRIDGE_X1+26,PH_WALL_H),(BRIDGE_X1+POST,PH_WALL_H)],
            fill=HexColor("#e8dfc9"), stroke=INK, w=0.8)
    sh.txt((BRIDGE_X1+14, POST_TOP+8), "PLAYHOUSE (post NW/WM)", 7.4, ACCENT, "c", True)
    # net deck with sag
    n = 26
    deck = [(BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)*i/n, DECK_TOP-BRIDGE_SAG*math.sin(math.pi*i/n)) for i in range(n+1)]
    for i in range(n): sh.line(deck[i], deck[i+1], NOTE, 2.4)
    topr = [(BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)*i/n, POST_TOP-1.2*math.sin(math.pi*i/n)) for i in range(n+1)]
    midr = [(BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)*i/n, DECK_TOP+18-BRIDGE_SAG*0.7*math.sin(math.pi*i/n)) for i in range(n+1)]
    for arr, w in ((topr, 2.4), (midr, 1.8)):
        for i in range(n): sh.line(arr[i], arr[i+1], NOTE, w)
    for i in range(0, n+1, 2):
        sh.line(deck[i], topr[i], NOTE, 1.0)
    sh.line((BRIDGE_X0, DECK_TOP), (BRIDGE_X1, DECK_TOP), THIN, 0.6, (3,2))
    sh.dim((BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)/2, DECK_TOP-BRIDGE_SAG),
           (BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)/2, DECK_TOP), 0, f'SAG {frac(BRIDGE_SAG)} exp.')
    sh.dim((BRIDGE_X0, -4), (BRIDGE_X1, -4), -18, f'CLEAR SPAN {frac(BRIDGE_SPAN)}')
    sh.dim((BRIDGE_X0-26, 0), (BRIDGE_X0-26, DECK_TOP), 14, frac(DECK_TOP), flip=True)
    sh.dim((BRIDGE_X1+26, DECK_TOP), (BRIDGE_X1+26, POST_TOP), 14, f'{frac(GUARD_H)} guard')
    for x, s in ((BRIDGE_X0, 1), (BRIDGE_X1, -1)):
        for z in (DECK_TOP-1.0, DECK_TOP+18, POST_TOP):
            sh.circle((x+s*1.4, z), 1.1, fill=RED, stroke=INK, w=0.6)
    sh.leader((BRIDGE_X0+2, DECK_TOP), (34, -40), '3/8" x 6" EYE BOLT through 2x6 header — washer + nylock nut')
    sh.leader((BRIDGE_X1-2, POST_TOP), (-40, 36), 'TOP ROPE at 80" — this is the guardrail', 6.2, anchor="r")
    sh.txt((BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)/2, POST_TOP+20), "BRIDGE ELEVATION — looking north", 10, INK, "c", True)

    # ---- large-scale anchor detail ----
    sh.view(90, 96, 300, 200, -1.2, -3.4, 9.0, 7.4)
    sh.poly([(0,0),(1.5,0),(1.5,7),(0,7)], fill=HexColor("#cdb98f"), stroke=INK, w=1.2)
    sh.poly([(1.5,0),(3.0,0),(3.0,7),(1.5,7)], fill=HexColor("#b9a583"), stroke=INK, w=1.2)
    sh.poly([(3.0,0),(6.5,0),(6.5,7),(3.0,7)], fill=HexColor("#e6e2d6"), stroke=INK, w=1.0, dash=(3,2))
    sh.line((-0.6,3.5),(0,3.5), INK, 3.0)
    sh.poly([(-0.55,3.2),(4.6,3.2),(4.6,3.8),(-0.55,3.8)], fill=HexColor("#3a3a3a"), stroke=INK, w=0.8)
    sh.circle((-1.05,3.5), 0.62, fill=None, stroke=HexColor("#3a3a3a"), w=3.4)
    sh.poly([(4.6,2.9),(5.3,2.9),(5.3,4.1),(4.6,4.1)], fill=HexColor("#2a2a2a"), stroke=INK, w=0.8)
    sh.poly([(4.2,2.75),(4.6,2.75),(4.6,4.25),(4.2,4.25)], fill=HexColor("#8a8a8a"), stroke=INK, w=0.7)
    sh.leader((-1.05,3.5), (-6, 48), '3/8" x 6" EYE BOLT', 6.4, anchor="r")
    sh.leader((0.7,5.6), (4, 46), '2x6 PT ledger — lagged into 2 studs min.', 6.2)
    sh.leader((2.2,1.4), (26, -22), "existing 2x4 wall stud", 6.2)
    sh.leader((4.4,2.75), (34, 8), "fender washer", 6.2)
    sh.leader((5.0,4.1), (40, 26), "nylock nut — NOT a plain nut", 6.2)
    sh.leader((4.8,0.9), (36, -26), "drill the shank hole, do not overdrive", 6.2)
    sh.txt((3.2, -2.4), "BRIDGE ANCHOR — enlarged detail", 9, INK, "c", True)
    sh.txt((3.2, -3.1), "same detail at both ends and at every rope railing anchor", 6.2, THIN, "c")

    c = sh.c
    block(c, sh.W-330, sh.H-118, 276, [
        "SPAN CORRECTION",
        f'The brief says ~42". The room says {frac(BRIDGE_SPAN)}.',
        "",
        f'{frac(ROOM_W)} wall  -  {frac(LOFT_SIZE)} loft  -  {frac(PH_SIZE)} playhouse',
        f'=  {frac(BRIDGE_SPAN)} clear.',
        "",
        "Both structures are in corners, so neither can slide",
        "toward the other. Order the net for 54\", not 42\".",
        "",
        "SAFETY — READ THIS BEFORE ORDERING ROPE",
        "· A single top rope 36\" above a sagging net is NOT a",
        "  guard. Order a net with full-height SIDE PANELS,",
        "  or add the mid rope at 18\" shown above. Both is",
        "  better. A kid will lean on whatever is there.",
        '· Commercial cargo net, 1/2" poly or nylon rope,',
        '  4"-6" mesh, playground rated. Not hardware-store',
        "  rope tied by hand. Not climbing rope.",
        '· Eye BOLTS, 3/8" x 6", through-bolted with a fender',
        "  washer and a nylock nut on the back side.",
        "  Screw eyes pull out of wood under cyclic load.",
        "· Both ledgers lag into a MINIMUM of 2 studs each,",
        '  3/8" x 4" lag screws, 2 per stud.',
        "· Fall zone: the bridge is 44\" up. Put 2\" interlocking",
        "  foam or a 1\" gym mat on the floor under the full",
        "  span and 24\" past each end. This is not optional.",
        "· Rated for ONE child at a time. Post a sign. Kids",
        "  will ignore it; the hardware should not.",
        "· Re-torque every eye bolt and lag after 30 days,",
        "  then every 6 months. Write the date on the ledger."],
        y_min=78, size=8.0, lead=11.6)
