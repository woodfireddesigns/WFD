"""Sheets: loft developed elevation, knee wall + hobbit door, ladder + bookshelf."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G
from drawkit import *

FACES = [("B","C",HEX_H,"REMOVABLE PANEL (future bridge)"), ("C","D",HEX_T,"FIXED GUARD"),
         ("D","Cp",HEX_T,"FIXED GUARD / HOBBIT DOOR BELOW"), ("Cp","Bp",HEX_H,"SELF-CLOSING GATE")]
DEV_W = sum(f[2] for f in FACES)

def _face_x0(i): return sum(FACES[j][2] for j in range(i))

def developed_elev(sh):
    top = POST_TOP + 14
    sh.view(64, 112, sh.W-138, sh.H-212, -14, -14, DEV_W+20, top)
    # floor + deck datum
    sh.line((-6, 0), (DEV_W+6, 0), INK, 1.6)
    for x in range(0, int(DEV_W)+6, 3):
        sh.line((x, 0), (x-2, -2.4), THIN, 0.5)
    sh.line((-6, DECK_TOP), (DEV_W+6, DECK_TOP), ACCENT, 1.0, (5,3))
    sh.txt((DEV_W+7, DECK_TOP-1.5), f'DECK  {frac(DECK_TOP)} A.F.F.', 6.2, ACCENT, "l", True)
    sh.line((-6, POST_TOP), (DEV_W+6, POST_TOP), ACCENT, 0.8, (5,3))
    sh.txt((DEV_W+7, POST_TOP-1.5), f'GUARD  {frac(POST_TOP)}', 6.2, ACCENT, "l", True)
    sh.line((-6, JOIST_BOT), (DEV_W+6, JOIST_BOT), THIN, 0.6, (2,2))

    for i, (a, b, L, lbl) in enumerate(FACES):
        x0 = _face_x0(i); x1 = x0 + L
        # face separator = post
        sh.poly([(x0, 0), (x0+POST, 0), (x0+POST, POST_TOP), (x0, POST_TOP)],
                fill=HexColor("#8a6a44"), stroke=INK, w=1.0)
        sh.txt((x0+POST/2, POST_TOP+4), a, 8, RED, "c", True)
        # knee wall band
        sh.poly([(x0, 0), (x1, 0), (x1, KNEE_TOTAL), (x0, KNEE_TOTAL)],
                fill=HexColor("#e6e9dd"), stroke=None)
        sh.poly([(x0, 0), (x1, 0), (x1, T_2X), (x0, T_2X)], fill=HexColor("#b9c4a0"), stroke=INK, w=0.7)
        sh.poly([(x0, KNEE_TOTAL-T_2X), (x1, KNEE_TOTAL-T_2X), (x1, KNEE_TOTAL), (x0, KNEE_TOTAL)],
                fill=HexColor("#b9c4a0"), stroke=INK, w=0.7)
        # joist band
        sh.poly([(x0, JOIST_BOT), (x1, JOIST_BOT), (x1, JOIST_TOP), (x0, JOIST_TOP)],
                fill=HexColor("#cdb98f"), stroke=INK, w=0.8)
        sh.poly([(x0, JOIST_TOP), (x1, JOIST_TOP), (x1, DECK_TOP), (x0, DECK_TOP)],
                fill=HexColor("#e0d3b2"), stroke=INK, w=0.6)
        # studs @16 O.C.
        ns = max(2, int(L // KNEE_OC) + 1)
        for kk in range(ns):
            sx = x0 + (L - W_2X4) * (kk/(ns-1) if ns > 1 else 0)
            sh.poly([(sx, T_2X), (sx+W_2X4, T_2X), (sx+W_2X4, KNEE_TOTAL-T_2X), (sx, KNEE_TOTAL-T_2X)],
                    fill=HexColor("#cfd8bd"), stroke=INK, w=0.5)
        sh.txt(((x0+x1)/2, POST_TOP+16), lbl, 7.2, ACCENT, "c", True)
        sh.txt(((x0+x1)/2, POST_TOP+8), f'face {frac(L)}', 6.0, THIN, "c")
        sh.dim((x0, 0), (x1, 0), -22, frac(L))

    # --- guards: vertical balusters on every face ---------------------
    import geometry as _G
    for i, (a, b, L, lbl) in enumerate(FACES):
        x0 = _face_x0(i); info = _G.GUARD_INFO[(a, b)]
        ax = x0 + POST/2 + 0.5; clear = info["clear"]; nb = info["n"]; gap = info["gap"]
        sh.poly([(ax, DECK_TOP), (ax+clear, DECK_TOP), (ax+clear, DECK_TOP+TOE_H), (ax, DECK_TOP+TOE_H)],
                fill=HexColor("#a5804f"), stroke=INK, w=0.9)
        sh.poly([(ax, POST_TOP-RAIL_T), (ax+clear, POST_TOP-RAIL_T), (ax+clear, POST_TOP), (ax, POST_TOP)],
                fill=HexColor("#a5804f"), stroke=INK, w=0.9)
        for k in range(nb):
            bx = ax + gap*(k+1) + BAL_S*k
            sh.poly([(bx, BAL_BOT), (bx+BAL_S, BAL_BOT), (bx+BAL_S, BAL_TOP), (bx, BAL_TOP)],
                    fill=HexColor("#c8a468"), stroke=INK, w=0.7)
        if info["kind"] == "GATE":
            for sx in (ax, ax+clear-W_2X4):
                sh.poly([(sx, DECK_TOP), (sx+W_2X4, DECK_TOP), (sx+W_2X4, POST_TOP), (sx, POST_TOP)],
                        fill=HexColor("#8a6a44"), stroke=INK, w=0.9)
            sh.arc_seg((ax+W_2X4, DECK_TOP+GUARD_H/2), clear-W_2X4, -18, 18, THIN, 0.6)
        if info["kind"] == "REMOVABLE PANEL":
            sh.poly([(ax-1, DECK_TOP-1), (ax+clear+1, DECK_TOP-1), (ax+clear+1, POST_TOP+1), (ax-1, POST_TOP+1)],
                    fill=None, stroke=RED, w=1.2, dash=(4,2))
        sh.dim((ax+gap+BAL_S, BAL_TOP+1), (ax+2*gap+BAL_S, BAL_TOP+1), 7, f'{gap:.2f}"')
    x0 = _face_x0(0)
    sh.leader((x0+HEX_H/2, POST_TOP-6), (-16, 40),
              'REMOVABLE PANEL — 8 screws, unscrew to add the bridge', 6.0, anchor="r")
    x0 = _face_x0(1)
    sh.leader((x0+HEX_T*0.5, POST_TOP-4), (18, 34),
              '2x2 BALUSTERS — max 3-3/8" clear. CPSC torso probe is 3.5".', 6.0)
    sh.leader((x0+HEX_T*0.15, DECK_TOP+TOE_H/2), (-30, -40),
              '2x4 TOE BOARD on edge — no gap at deck level, stops kicked toys', 6.0, anchor="r")
    x0 = _face_x0(3)
    sh.leader((x0+HEX_H*0.55, POST_TOP-3), (22, 50),
              'SELF-CLOSING GATE — swings IN. Spring hinges + gravity latch. No lock.', 6.0)

    # --- face 3: rope net + hobbit door
    x0 = _face_x0(2); x1 = x0 + HEX_T
    # hobbit door
    dc = (x0+x1)/2
    ro0, ro1 = dc-HDOOR_RO_W/2, dc+HDOOR_RO_W/2
    sh.poly([(ro0, T_2X), (ro1, T_2X), (ro1, T_2X+HDOOR_RO_H), (ro0, T_2X+HDOOR_RO_H)],
            fill=HexColor("#fbfaf6"), stroke=RED, w=1.2, dash=(3,2))
    for s in (-1, 1):
        jx = dc + s*(HDOOR_RO_W/2) + (0 if s < 0 else 0)
        px = ro0-W_2X4 if s < 0 else ro1
        sh.poly([(px, T_2X), (px+W_2X4, T_2X), (px+W_2X4, T_2X+HDOOR_RO_H), (px, T_2X+HDOOR_RO_H)],
                fill=HexColor("#c2cdaa"), stroke=INK, w=0.7)
        px2 = ro0-W_2X4*2 if s < 0 else ro1+W_2X4
        sh.poly([(px2, T_2X), (px2+W_2X4, T_2X), (px2+W_2X4, KNEE_TOTAL-T_2X), (px2, KNEE_TOTAL-T_2X)],
                fill=HexColor("#b4c199"), stroke=INK, w=0.7)
    hz = T_2X+HDOOR_RO_H
    sh.poly([(ro0-W_2X4, hz), (ro1+W_2X4, hz), (ro1+W_2X4, hz+HDOOR_HDR), (ro0-W_2X4, hz+HDOOR_HDR)],
            fill=HexColor("#a9b88c"), stroke=INK, w=0.8)
    for s in (-1, 0, 1):
        cx = dc + s*HDOOR_RO_W*0.33
        sh.poly([(cx-W_2X4/2, hz+HDOOR_HDR), (cx+W_2X4/2, hz+HDOOR_HDR),
                 (cx+W_2X4/2, hz+HDOOR_HDR+HDOOR_CRIPPLE), (cx-W_2X4/2, hz+HDOOR_HDR+HDOOR_CRIPPLE)],
                fill=HexColor("#c2cdaa"), stroke=INK, w=0.6)
    # door slab w/ arch
    sdz = HDOOR_SLAB_H - HDOOR_ARCH_R
    sh.poly([(dc-HDOOR_SLAB_W/2, T_2X), (dc+HDOOR_SLAB_W/2, T_2X),
             (dc+HDOOR_SLAB_W/2, T_2X+sdz), (dc-HDOOR_SLAB_W/2, T_2X+sdz)],
            fill=HexColor("#3a5a3c"), stroke=INK, w=1.0)
    sh.arc_seg((dc, T_2X+sdz), HDOOR_ARCH_R, 0, 180, INK, 1.0)
    pts = [(dc+HDOOR_ARCH_R*math.cos(math.radians(t*7.5)), T_2X+sdz+HDOOR_ARCH_R*math.sin(math.radians(t*7.5))) for t in range(25)]
    sh.poly([(dc-HDOOR_ARCH_R, T_2X+sdz)]+pts[::-1], fill=HexColor("#3a5a3c"), stroke=INK, w=1.0)
    for s in (-1, 1):
        sh.poly([(dc-HDOOR_SLAB_W/2+1, T_2X+sdz/2+s*sdz*0.3),
                 (dc+HDOOR_SLAB_W/2*0.72, T_2X+sdz/2+s*sdz*0.3),
                 (dc+HDOOR_SLAB_W/2*0.72, T_2X+sdz/2+s*sdz*0.3+1.5),
                 (dc-HDOOR_SLAB_W/2+1, T_2X+sdz/2+s*sdz*0.3+1.5)], fill=INK, stroke=None)
    sh.circle((dc+HDOOR_SLAB_W/2-3.5, T_2X+sdz*0.62), 1.3, fill=HexColor("#4a3career".replace("career","0")[:7]) if False else HexColor("#4a3520"), stroke=INK, w=0.6)
    sh.dim((ro0, T_2X), (ro1, T_2X), -8, f'R.O. {frac(HDOOR_RO_W)}')
    sh.dim((ro1+0.5, T_2X), (ro1+0.5, T_2X+HDOOR_RO_H), 7, f'R.O. {frac(HDOOR_RO_H)}')
    sh.leader((dc-HDOOR_ARCH_R*0.7, T_2X+sdz+HDOOR_ARCH_R*0.7), (-52, 26),
              f'SEMICIRCULAR HEAD  R = {frac(HDOOR_ARCH_R)}  —  full template on A4', 6.0, anchor="r")
    # porthole on face 2
    px0 = _face_x0(1)
    sh.circle((px0+HEX_T*0.22, PORTHOLE_Z), PORTHOLE_D/2, fill=HexColor("#cfe0e2"), stroke=INK, w=1.0)
    sh.circle((px0+HEX_T*0.22, PORTHOLE_Z), PORTHOLE_D/2+0.9, fill=None, stroke=INK, w=1.4)
    sh.leader((px0+HEX_T*0.22, PORTHOLE_Z), (-40, -36),
              f'{frac(PORTHOLE_D)} ACRYLIC PORTHOLE — no glass', 6.0, anchor="r")

    # --- face 4: ladder
    sh.dim((-5.5, 0), (-5.5, DECK_TOP), 22, frac(DECK_TOP), flip=True)
    sh.dim((-5.5, DECK_TOP), (-5.5, POST_TOP), 22, frac(GUARD_H), flip=True)
    sh.dim((DEV_W+3, 0), (DEV_W+3, KNEE_TOTAL), 30, f'{frac(KNEE_TOTAL)} wall')
    sh.dim((DEV_W+3, JOIST_BOT), (DEV_W+3, DECK_TOP), 48, f'2x6 + 3/4" ply')

    c = sh.c
    c.setFont("Helvetica-Oblique", 8); c.setFillColor(THIN)
    c.drawString(66, 80, "DEVELOPED ELEVATION — the four open faces of the loft unrolled into one flat strip. "
                          "Angles between faces are shown in plan on A2.")

def kneewall_and_door(sh):
    # left: knee wall section.  right: full-size arch template grid.
    sh.view(62, 116, (sh.W-410)*0.52, sh.H-236, -16, -12, LOFT_SIZE+16, KNEE_TOTAL+30)
    sh.line((-14, 0), (LOFT_SIZE+14, 0), INK, 1.6)
    sh.poly([(0,0),(LOFT_SIZE,0),(LOFT_SIZE,T_2X),(0,T_2X)], fill=HexColor("#b9c4a0"), stroke=INK, w=0.9)
    sh.poly([(0,KNEE_TOTAL-T_2X),(LOFT_SIZE,KNEE_TOTAL-T_2X),(LOFT_SIZE,KNEE_TOTAL),(0,KNEE_TOTAL)],
            fill=HexColor("#b9c4a0"), stroke=INK, w=0.9)
    n = 0
    while n*KNEE_OC <= LOFT_SIZE-W_2X4:
        sx = n*KNEE_OC
        sh.poly([(sx,T_2X),(sx+W_2X4,T_2X),(sx+W_2X4,KNEE_TOTAL-T_2X),(sx,KNEE_TOTAL-T_2X)],
                fill=HexColor("#cfd8bd"), stroke=INK, w=0.6)
        if n: sh.dim((sx-KNEE_OC, KNEE_TOTAL+3), (sx, KNEE_TOTAL+3), 6, '16"')
        n += 1
    sh.poly([(LOFT_SIZE-W_2X4,T_2X),(LOFT_SIZE,T_2X),(LOFT_SIZE,KNEE_TOTAL-T_2X),(LOFT_SIZE-W_2X4,KNEE_TOTAL-T_2X)],
            fill=HexColor("#cfd8bd"), stroke=INK, w=0.6)
    sh.poly([(0,JOIST_BOT),(LOFT_SIZE,JOIST_BOT),(LOFT_SIZE,JOIST_TOP),(0,JOIST_TOP)],
            fill=HexColor("#cdb98f"), stroke=INK, w=0.9)
    sh.poly([(0,JOIST_TOP),(LOFT_SIZE,JOIST_TOP),(LOFT_SIZE,DECK_TOP),(0,DECK_TOP)],
            fill=HexColor("#e0d3b2"), stroke=INK, w=0.7)
    sh.dim((-6, 0), (-6, T_2X), 12, '1-1/2"', flip=True)
    sh.dim((-6, T_2X), (-6, KNEE_TOTAL-T_2X), 12, frac(KNEE_STUD), flip=True)
    sh.dim((-6, KNEE_TOTAL-T_2X), (-6, KNEE_TOTAL), 12, '1-1/2"', flip=True)
    sh.dim((LOFT_SIZE+6, 0), (LOFT_SIZE+6, KNEE_TOTAL), 14, frac(KNEE_TOTAL))
    sh.dim((LOFT_SIZE+6, 0), (LOFT_SIZE+6, DECK_TOP), 46, frac(DECK_TOP))
    sh.txt((LOFT_SIZE/2, KNEE_TOTAL+30), "KNEE WALL SECTION — typical", 9, INK, "c", True)
    sh.leader((LOFT_SIZE*0.5, KNEE_STUD/2), (14, -44),
              f'STUD LENGTH {frac(KNEE_STUD)} — the brief said 40-42". It cannot be.', 6.4, RED)

    # ---- arch template ----
    tw = HDOOR_SLAB_W + 8
    sh.view(62+(sh.W-410)*0.54, 116, (sh.W-410)*0.44, sh.H-236, -5, -8, tw, HDOOR_SLAB_H+14)
    for gx in range(0, int(tw)+1, 2):
        sh.line((gx, 0), (gx, HDOOR_SLAB_H+2), GRID, 0.4)
    for gy in range(0, int(HDOOR_SLAB_H)+3, 2):
        sh.line((0, gy), (tw, gy), GRID, 0.4)
    for gx in range(0, int(tw)+1, 6):
        sh.line((gx, 0), (gx, HDOOR_SLAB_H+2), HexColor("#c9c3b4"), 0.7)
        sh.txt((gx, -4), f'{gx}"', 5.2, THIN, "c")
    for gy in range(0, int(HDOOR_SLAB_H)+3, 6):
        sh.line((0, gy), (tw, gy), HexColor("#c9c3b4"), 0.7)
        sh.txt((-1.5, gy-1), f'{gy}"', 5.2, THIN, "r")
    dc = tw/2; sdz = HDOOR_SLAB_H - HDOOR_ARCH_R
    pts = [(dc-HDOOR_SLAB_W/2, 0), (dc+HDOOR_SLAB_W/2, 0), (dc+HDOOR_SLAB_W/2, sdz)]
    pts += [(dc+HDOOR_ARCH_R*math.cos(math.radians(t*3.75)), sdz+HDOOR_ARCH_R*math.sin(math.radians(t*3.75)))
            for t in range(49)]
    pts += [(dc-HDOOR_SLAB_W/2, sdz)]
    sh.poly(pts, fill=HexColor("#e7eadf"), stroke=INK, w=1.8)
    # plank lines
    for pk in range(1, 5):
        px = dc - HDOOR_SLAB_W/2 + HDOOR_SLAB_W*pk/5
        sh.line((px, 0.4), (px, sdz+math.sqrt(max(HDOOR_ARCH_R**2-(px-dc)**2, 0))-0.4), HexColor("#9aa48c"), 0.8)
    sh.circle((dc, sdz), 0.6, fill=RED, stroke=None)
    sh.line((dc, sdz), (dc+HDOOR_ARCH_R, sdz), RED, 0.7, (3,2))
    sh.txt((dc+HDOOR_ARCH_R/2, sdz+1.4), f'R {frac(HDOOR_ARCH_R)}', 6.4, RED, "c", True)
    sh.dim((dc-HDOOR_SLAB_W/2, -1), (dc+HDOOR_SLAB_W/2, -1), -12, frac(HDOOR_SLAB_W))
    sh.dim((dc+HDOOR_SLAB_W/2+1, 0), (dc+HDOOR_SLAB_W/2+1, HDOOR_SLAB_H), 14, frac(HDOOR_SLAB_H))
    sh.dim((dc+HDOOR_SLAB_W/2+1, 0), (dc+HDOOR_SLAB_W/2+1, sdz), 40, f'spring line {frac(sdz)}')
    for s in (-1, 1):
        sh.poly([(dc-HDOOR_SLAB_W/2+0.8, sdz/2+s*sdz*0.30), (dc+HDOOR_SLAB_W/2*0.7, sdz/2+s*sdz*0.30),
                 (dc+HDOOR_SLAB_W/2*0.7, sdz/2+s*sdz*0.30+1.6), (dc-HDOOR_SLAB_W/2+0.8, sdz/2+s*sdz*0.30+1.6)],
                fill=INK, stroke=None)
    sh.circle((dc+HDOOR_SLAB_W/2-3.5, sdz*0.60), 1.4, fill=HexColor("#4a3520"), stroke=INK, w=0.7)
    sh.txt((dc, HDOOR_SLAB_H+10), "HOBBIT DOOR — FULL TEMPLATE", 9, INK, "c", True)
    sh.txt((dc, HDOOR_SLAB_H+4), '2" grid — scale off the grid, not the paper', 6.2, THIN, "c")

    c = sh.c
    block(c, sh.W-330, sh.H-118, 276, [
        '· Slab: two layers of 3/4" ply, glued and screwed,',
        '  grain crossed, cut to the template above = 1-1/2" thick.',
        '· Face with 1x4 tongue-and-groove pine, vertical,',
        '  ripped to the arch with a jigsaw.',
        '· Hinges: 12" black strap hinges, 2 per door, through-bolted',
        '  with 1/4" carriage bolts — screws alone will sag.',
        '· Jamb: 3/4" ply, 3 sides, glued and screwed into the',
        '  king/jack studs. No sill — remove the bottom plate',
        '  inside the R.O. after the wall is standing.',
        '· Knob: 2-3/4" round wood knob, 1/4" lag from the back.',
        '· Magnetic catch, not a latch. A kid must be able to push',
        '  the door open from the inside with no hardware.',
        '· NO lock of any kind, inside or out.',
        '· Paint: deep green (see A9). Two coats, sand between.'],
        y_min=92, size=8.0, lead=12.0, title="DOOR BUILD-UP")
