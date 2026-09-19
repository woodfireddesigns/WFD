"""Sheets: ladder + bookshelf, playhouse, bridge."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G
from drawkit import *

def ladder_and_shelf(sh):
    # ---------- LADDER ELEVATION ----------
    sh.view(64, 214, (sh.W-190)*0.36, sh.H-354, -24, -18, LADDER_RUN+36, POST_TOP+22)
    sh.line((-20, 0), (LADDER_RUN+30, 0), INK, 1.6)
    sh.poly([(0,0),(POST,0),(POST,POST_TOP),(0,POST_TOP)], fill=HexColor("#8a6a44"), stroke=INK, w=1.0)
    sh.poly([(-18,JOIST_BOT),(POST,JOIST_BOT),(POST,JOIST_TOP),(-18,JOIST_TOP)], fill=HexColor("#cdb98f"), stroke=INK, w=0.9)
    sh.poly([(-18,JOIST_TOP),(POST,JOIST_TOP),(POST,DECK_TOP),(-18,DECK_TOP)], fill=HexColor("#e0d3b2"), stroke=INK, w=0.7)
    sh.poly([(-18,0),(0,0),(0,KNEE_TOTAL),(-18,KNEE_TOTAL)], fill=HexColor("#dfe4d4"), stroke=INK, w=0.7)
    sh.txt((-9, DECK_TOP+8), "LOFT", 6.6, ACCENT, "c", True)
    # guard + gate above
    sh.poly([(-14,POST_TOP-RAIL_T),(POST,POST_TOP-RAIL_T),(POST,POST_TOP),(-14,POST_TOP)], fill=HexColor("#a5804f"), stroke=INK, w=0.8)
    sh.poly([(-14,DECK_TOP),(POST,DECK_TOP),(POST,DECK_TOP+TOE_H),(-14,DECK_TOP+TOE_H)], fill=HexColor("#a5804f"), stroke=INK, w=0.8)
    for bx in (-12.5, -7.5, -2.5):
        sh.poly([(bx,BAL_BOT),(bx+BAL_S,BAL_BOT),(bx+BAL_S,BAL_TOP),(bx,BAL_TOP)], fill=HexColor("#c8a468"), stroke=INK, w=0.6)
    # hanger rail
    sh.poly([(POST,DECK_TOP-5.5),(POST+T_2X,DECK_TOP-5.5),(POST+T_2X,DECK_TOP),(POST,DECK_TOP)],
            fill=HexColor("#7a5c3a"), stroke=RED, w=1.4)
    ang = math.radians(LADDER_ANGLE)
    sp0 = (LADDER_RUN, 0.0); sp1 = (POST+1.0, DECK_TOP)
    nx, nz = (sp1[1]-sp0[1]), -(sp1[0]-sp0[0]); m = math.hypot(nx,nz); nx, nz = nx/m*W_2X4, nz/m*W_2X4
    sh.poly([sp0, sp1, (sp1[0]+nx, sp1[1]+nz), (sp0[0]+nx, sp0[1]+nz)], fill=HexColor("#a5804f"), stroke=INK, w=1.2)
    gx, gz = nx*2.1, nz*2.1
    sh.poly([(sp0[0]+gx, sp0[1]+gz+14),(sp1[0]+gx, sp1[1]+gz+6),
             (sp1[0]+gx+1.5, sp1[1]+gz+6),(sp0[0]+gx+1.5, sp0[1]+gz+14)],
            fill=HexColor("#c8a468"), stroke=INK, w=1.0)
    for k in range(1, LADDER_RUNGS+1):
        t = k/(LADDER_RUNGS+1)
        rx = sp0[0]+(sp1[0]-sp0[0])*t; rz = k*LADDER_RISER
        sh.poly([(rx-1.9, rz-0.75),(rx+1.9, rz-0.75),(rx+1.9, rz+0.75),(rx-1.9, rz+0.75)],
                fill=HexColor("#c8a468"), stroke=INK, w=0.9)
    sh.dim((LADDER_RUN+20, 0), (LADDER_RUN+20, DECK_TOP), 8, f'RISE {frac(DECK_TOP)}')
    sh.dim((LADDER_RUN+11, 0), (LADDER_RUN+11, LADDER_RISER), 8, frac(LADDER_RISER))
    sh.dim((0, -8), (LADDER_RUN, -8), -14, f'RUN {frac(LADDER_RUN)}')
    sh.arc_seg((LADDER_RUN, 0), 13, 116, 180, RED, 1.0)
    sh.txt((LADDER_RUN-18, 6), "65 deg", 6.6, RED, "c", True)
    sh.leader((POST+T_2X/2, DECK_TOP-2.75), (44, 36), 'HANGER RAIL 2x6 — the ladder HOOKS over this', 6.2, RED)
    sh.leader((sp0[0]+gx+0.7, 30), (40, -30), '2x2 RIGID GRAB RAIL both sides (no rope)', 6.0)
    sh.leader((sp0[0]+nx/2, 1.5), (26, -48), 'Feet: 2x4 cleat lagged to the subfloor, or ABU44 standoff', 6.0)
    sh.txt((LADDER_RUN/2, POST_TOP+14), "LADDER ELEVATION — LIFTS OFF", 10, INK, "c", True)
    sh.txt((LADDER_RUN/2, POST_TOP+6), f'{LADDER_RUNGS} rungs @ {frac(LADDER_RISER)} riser', 6.4, THIN, "c")

    # ---------- TOP-OF-LADDER / HOOK DETAIL ----------
    ox = 64+(sh.W-190)*0.38
    sh.view(ox, 330, (sh.W-190)*0.24, sh.H-470, -3, -3.5, 12, 11)
    sh.poly([(0,0),(1.5,0),(1.5,10),(0,10)], fill=HexColor("#cdb98f"), stroke=INK, w=1.2)
    sh.poly([(1.5,6.0),(3.0,6.0),(3.0,10),(1.5,10)], fill=HexColor("#7a5c3a"), stroke=INK, w=1.2)
    sh.poly([(2.6,0),(4.1,0),(4.1,7.2),(3.0,8.4),(2.6,8.4)], fill=HexColor("#a5804f"), stroke=INK, w=1.4)
    sh.poly([(2.6,6.0),(3.05,6.0),(3.05,7.6),(2.6,7.6)], fill=HexColor("#fbfaf6"), stroke=RED, w=1.0, dash=(2,1))
    sh.circle((3.5,4.6), 0.28, fill=RED, stroke=INK, w=0.7)
    sh.line((1.2,4.6),(5.2,4.6), RED, 1.4)
    sh.leader((3.5,4.6), (36,-16), '3/8" x 5" PIN — drops through both, locks the ladder down', 5.8)
    sh.leader((2.25,8.8), (30,20), 'notch in the stringer hooks the 2x6 hanger rail', 5.8)
    sh.leader((0.75,2.0), (-20,-34), 'deck rim joist', 5.8, anchor="r")
    sh.txt((4.0,-2.6), "HOOK + PIN DETAIL", 9, INK, "c", True)
    sh.txt((4.0,-3.3), "pull two pins, lift the ladder off, store it flat", 6.0, THIN, "c")

    # ---------- GROUND-LEVEL DEN SHELF ----------
    ox2 = 64+(sh.W-190)*0.64
    sh.view(ox2, 356, (sh.W-190)*0.30, sh.H-500, -9, -9, G.DEN_SHELF_CLEAR+14, 33)
    sh.line((-4,0),(G.DEN_SHELF_CLEAR+8,0), INK, 1.6)
    sh.poly([(-1.5,0),(G.DEN_SHELF_CLEAR+1.5,0),(G.DEN_SHELF_CLEAR+1.5,27),(-1.5,27)],
            fill=HexColor("#e2e6d8"), stroke=INK, w=1.0)
    for sx in (-1.5, G.DEN_SHELF_CLEAR):
        sh.poly([(sx,0),(sx+1.5,0),(sx+1.5,27),(sx,27)], fill=HexColor("#cfd8bd"), stroke=INK, w=0.8)
    hts = (6.8, 5.4, 7.2, 6.0, 7.6, 5.0)
    for zi, z in enumerate(DEN_SHELF_Z):
        sh.poly([(-1.5,z),(G.DEN_SHELF_CLEAR+1.5,z),(G.DEN_SHELF_CLEAR+1.5,z+PLY),(-1.5,z+PLY)],
                fill=HexColor("#c7ab7c"), stroke=INK, w=1.0)
        for bk in range(6):
            bx = 0.6+bk*2.75
            if bx+2.1 < G.DEN_SHELF_CLEAR-0.3:
                h = hts[(bk+zi*2) % 6]
                sh.poly([(bx,z+PLY),(bx+2.1,z+PLY),(bx+2.1,z+PLY+h),(bx,z+PLY+h)],
                        fill=HexColor("#9aa88c") if bk%2 else HexColor("#b08a5a"), stroke=THIN, w=0.5)
        sh.poly([(-1.5,z+PLY),(G.DEN_SHELF_CLEAR+1.5,z+PLY),(G.DEN_SHELF_CLEAR+1.5,z+PLY+2.0),(-1.5,z+PLY+2.0)],
                fill=None, stroke=NOTE, w=1.1, dash=(2,2))
    sh.dim((-1.5,-1.5),(G.DEN_SHELF_CLEAR+1.5,-1.5), -10, frac(G.DEN_SHELF_CLEAR+3))
    sh.dim((G.DEN_SHELF_CLEAR+3,0),(G.DEN_SHELF_CLEAR+3,DEN_SHELF_Z[0]), 9, frac(DEN_SHELF_Z[0]))
    sh.dim((G.DEN_SHELF_CLEAR+3,DEN_SHELF_Z[0]),(G.DEN_SHELF_CLEAR+3,DEN_SHELF_Z[1]), 9, frac(DEN_SHELF_Z[1]-DEN_SHELF_Z[0]))
    sh.leader((G.DEN_SHELF_CLEAR*0.5, DEN_SHELF_Z[1]+PLY+1.0), (18, 26), '2" book lip, rounded', 6.0)
    sh.txt((G.DEN_SHELF_CLEAR/2, 31.5), "DEN SHELF — GROUND LEVEL", 9.5, INK, "c", True)
    sh.txt((G.DEN_SHELF_CLEAR/2, 29.2), "inside the enclosed base, NOT in the guardrail", 6.2, RED, "c", True)

    c = sh.c
    block(c, 64, 194, (sh.W-190)*0.34, [
        "WHY THE LADDER LIFTS OFF",
        "A gate stops a fall. It does not stop an 18-month-old,",
        "because whatever latch a 4-year-old can work, a determined",
        "toddler eventually works too.",
        "",
        "The ladder is the real access control. Pull two pins, lift",
        "it off, stand it behind the playhouse. The loft is then",
        "physically unreachable — there is nothing to climb.",
        "",
        "Hang it when the 4-year-old is up there. Pull it at night",
        "and any time the little one is loose in the room."],
        y_min=72, size=7.6, lead=11.0)
    block(c, ox2, 322, (sh.W-190)*0.30, [
        "WHY THE SHELVES CAME OUT OF THE RAILING",
        "You were right, and for a better reason than you think.",
        "A shelf bolted into a guardrail is a ladder. A 4-year-old",
        "puts a foot on the bottom shelf and their centre of mass",
        "clears a 36\" rail. The guard stops working.",
        "",
        "The books and the apothecary jars move to floor level,",
        "inside the den, where the 18-month-old actually plays.",
        "",
        "CHOKING — READ THIS",
        "Acorns, dried botanicals and anything under 1-3/4\" is a",
        "choking hazard until 3. Either hot-glue the jar lids shut",
        "so they are display-only, or leave the jars out until the",
        "little one is past it. Board books only down here."],
        y_min=72, size=7.5, lead=10.8)

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
    sh.view(64, 300, sh.W-400, sh.H-470, BRIDGE_X0-40, 22, BRIDGE_X1+40, POST_TOP+20)
    sh.line((BRIDGE_X0-38, 26), (BRIDGE_X1+38, 26), THIN, 0.8, (3,2))
    sh.poly([(BRIDGE_X0-30,JOIST_BOT),(BRIDGE_X0,JOIST_BOT),(BRIDGE_X0,DECK_TOP),(BRIDGE_X0-30,DECK_TOP)],
            fill=HexColor("#cdb98f"), stroke=INK, w=1.0)
    sh.poly([(BRIDGE_X0-POST,26),(BRIDGE_X0,26),(BRIDGE_X0,POST_TOP),(BRIDGE_X0-POST,POST_TOP)],
            fill=HexColor("#8a6a44"), stroke=INK, w=1.1)
    sh.txt((BRIDGE_X0-16, POST_TOP+9), "LOFT — post B", 7.4, ACCENT, "c", True)
    sh.poly([(BRIDGE_X1,26),(BRIDGE_X1+POST,26),(BRIDGE_X1+POST,PH_WALL_H),(BRIDGE_X1,PH_WALL_H)],
            fill=HexColor("#8a6a44"), stroke=INK, w=1.1)
    sh.txt((BRIDGE_X1+18, POST_TOP+9), "PLAYHOUSE — post WM", 7.4, ACCENT, "c", True)
    # removable panel on the loft side
    ax = BRIDGE_X0-19.5; 
    sh.poly([(ax, DECK_TOP),(BRIDGE_X0, DECK_TOP),(BRIDGE_X0, POST_TOP),(ax, POST_TOP)],
            fill=HexColor("#eee9da"), stroke=RED, w=1.4, dash=(4,2))
    for k in range(4):
        bx = ax + 2.7*(k+1) + 1.5*k
        sh.poly([(bx,BAL_BOT),(bx+BAL_S,BAL_BOT),(bx+BAL_S,BAL_TOP),(bx,BAL_TOP)],
                fill=HexColor("#c8a468"), stroke=INK, w=0.7)
    sh.leader(((ax+BRIDGE_X0)/2, POST_TOP-8), (-26, 34), "REMOVABLE PANEL — 8 screws", 6.4, RED, anchor="r")
    # provisions installed now
    sh.poly([(BRIDGE_X0-20, DECK_TOP-W_2X6),(BRIDGE_X0+2, DECK_TOP-W_2X6),
             (BRIDGE_X0+2, DECK_TOP),(BRIDGE_X0-20, DECK_TOP)], fill=HexColor("#c4a874"), stroke=ACCENT, w=1.6)
    sh.poly([(PH_X0-2, DECK_TOP-W_2X6),(PH_X0+20, DECK_TOP-W_2X6),
             (PH_X0+20, DECK_TOP),(PH_X0-2, DECK_TOP)], fill=HexColor("#c4a874"), stroke=ACCENT, w=1.6)
    for x, s_ in ((BRIDGE_X0, 1), (BRIDGE_X1, -1)):
        for z in (DECK_TOP-2.75, POST_TOP-2):
            sh.circle((x+s_*2.0, z), 1.1, fill=None, stroke=RED, w=1.0)
            sh.line((x+s_*0.6, z), (x+s_*3.4, z), RED, 0.5, (1.5,1.5))
    # ghosted future net
    n = 22
    for arr, z0, sag in (("deck", DECK_TOP, 5.0), ("top", POST_TOP-2, 1.0)):
        pts = [(BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)*i/n, z0 - sag*math.sin(math.pi*i/n)) for i in range(n+1)]
        for i in range(n): sh.line(pts[i], pts[i+1], HexColor("#c9bda4"), 1.6, (3,2))
    for i in range(0, n+1, 3):
        t = i/n; x = BRIDGE_X0+(BRIDGE_X1-BRIDGE_X0)*t
        sh.line((x, DECK_TOP-5.0*math.sin(math.pi*t)), (x, POST_TOP-2-1.0*math.sin(math.pi*t)),
                HexColor("#d5cab3"), 1.0, (2,2))
    sh.txt(((BRIDGE_X0+BRIDGE_X1)/2, DECK_TOP+14), "FUTURE — NOT BUILT IN PHASE 1", 9, HexColor("#a99a7c"), "c", True)
    sh.dim((BRIDGE_X0, 30), (BRIDGE_X1, 30), -16, f'CLEAR SPAN {frac(BRIDGE_SPAN)}')
    sh.dim((BRIDGE_X0-34, 26), (BRIDGE_X0-34, DECK_TOP), 14, frac(DECK_TOP-26), flip=True)
    sh.txt(((BRIDGE_X0+BRIDGE_X1)/2, POST_TOP+18), "BRIDGE — FUTURE PROVISIONS", 10.5, INK, "c", True)

    c = sh.c
    block(c, 64, 250, sh.W-440, [
        "INSTALL THESE THREE THINGS NOW. THEY COST ABOUT $40 AND SAVE A TEARDOWN LATER.",
        "1.  Both 2x6 PT wall ledgers, lagged into studs. They read as a trim band until the day you use them.",
        "2.  The playhouse WM post at 18\" off the north wall. It makes the bay. Skip it and you are cutting into finished siding later.",
        "3.  The 2x6 net headers as blocking behind the loft rim and the playhouse west face.",
        "",
        "ADDING THE BRIDGE LATER IS THEN A TWO-HOUR JOB: unscrew the 8-screw panel, drill 8 holes, bolt 8 eye bolts, hang the net."],
        y_min=196, size=8.2, lead=12.0)
    block(c, sh.W-350, sh.H-118, 296, [
        "I CHECKED THE BRIDGE BEFORE DELETING IT",
        "You asked whether it holds a 4-year-old. It does, easily.",
        "",
        "Two 42 lb kids, x5 dynamic factor for bouncing = 420 lb,",
        "split across 4 anchors = 105 lb per anchor.",
        "A 3/8\" FORGED shoulder eye bolt is good for ~1000 lb",
        "in line. Eight times the load.",
        "The 3/8\" lags into studs give ~587 lb each in withdrawal;",
        "four per ledger is about eleven times what is needed.",
        "",
        "Strength was never the problem. Two other things were.",
        "",
        "WIDTH",
        "18\" is a balance beam, not a bridge. Playground crossings",
        "run 20-24\". So the loft gate face went from 20\" to 24\",",
        "which also made the deck slightly BIGGER, 22.36 sq ft.",
        "The bridge you add later will be 24\" wide.",
        "",
        "MESH SIZE — THE ONE THAT MATTERS",
        "CPSC treats any opening between 3.5\" and 9\" as a head",
        "entrapment: a small body passes through, the head does not.",
        "A 4-6\" cargo net mesh fails both probes. That is fine for",
        "a supervised 6-year-old and wrong for a 2-year-old in the",
        "same room. When you buy the net, get mesh under 3.5\",",
        "or add a fine secondary net on both faces.",
        "",
        "WAIT UNTIL THE YOUNGEST IS 4. The bridge is the single",
        "most dangerous element in the whole build, and the one",
        "you lose the least by deferring."],
        y_min=78, size=7.6, lead=10.8)

