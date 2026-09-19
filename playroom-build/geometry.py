"""
Builds the complete member list for both structures + bridge.
Every member is a rectangular prism defined by a start point, end point,
cross-section, and an 'up' vector. Blender builds boxes from this list;
the PDF plan generator builds the cut list and drawings from the same list.
Coordinates: room frame, inches. X = west->east, Y = south->north, Z = up.
"""
import math
from params import *

V = lambda *a: tuple(float(x) for x in a)

def _norm(v):
    m = math.sqrt(sum(c*c for c in v)) or 1.0
    return tuple(c/m for c in v)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

MEMBERS = []

def M(group, label, p0, p1, w, h, up=(0,0,1), mat="oak", stock=None, ends=(90.0,90.0), note=""):
    """w = width across the 'side' axis, h = depth along 'up'."""
    L = math.dist(p0, p1)
    ax = _norm(tuple(b-a for a, b in zip(p0, p1)))
    if abs(_cross(ax, up)[0]) + abs(_cross(ax, up)[1]) + abs(_cross(ax, up)[2]) < 1e-6:
        up = (0, 1, 0)
    side = _norm(_cross(up, ax)); up2 = _norm(_cross(ax, side))
    m = dict(group=group, label=label, p0=V(*p0), p1=V(*p1), L=L, w=w, h=h,
             axis=ax, side=side, up=up2, mat=mat,
             stock=stock or f"{w}x{h}", ends=ends, note=note)
    MEMBERS.append(m)
    return m

PTS = {n: (u, v) for n, u, v in LOFT_POLY}
RM  = {n: local_to_room(u, v) for n, (u, v) in PTS.items()}
ORDER = [n for n, _, _ in LOFT_POLY]

def edge(a, b):
    (x0, y0), (x1, y1) = RM[a], RM[b]
    L = math.hypot(x1-x0, y1-y0)
    return (x0, y0), (x1, y1), L, ((x1-x0)/L, (y1-y0)/L)

def inward(a, b):
    """Unit vector pointing from edge a-b toward the deck interior."""
    (x0, y0), (x1, y1), L, d = edge(a, b)
    n1 = (-d[1], d[0])
    cx = sum(RM[k][0] for k in ORDER)/6.0
    cy = sum(RM[k][1] for k in ORDER)/6.0
    mx, my = (x0+x1)/2, (y0+y1)/2
    return n1 if ((cx-mx)*n1[0] + (cy-my)*n1[1]) > 0 else (-n1[0], -n1[1])

# ======================================================================
# 1. LOFT
# ======================================================================
def build_loft():
    # --- 4x4 posts -----------------------------------------------------
    for n in ORDER:
        x, y = RM[n]
        tall = n in LOFT_TALL_POSTS
        top  = POST_LEN_TALL if tall else POST_LEN_CORNER
        # pull the post inboard so its outer faces sit on the deck outline
        iu = (0.0, 0.0)
        for a, b in zip(ORDER, ORDER[1:]+ORDER[:1]):
            if n in (a, b):
                w = inward(a, b)
                iu = (iu[0]+w[0], iu[1]+w[1])
        iu = _norm((iu[0], iu[1], 0.0))
        off = POST/2.0 * math.sqrt(2) if n == "D" else POST/2.0 * math.sqrt(2)
        px, py = x + iu[0]*off, y + iu[1]*off
        rot = 45.0 if n == "D" else 0.0
        up_ax = (0, 0, 1)
        m = M("Loft / Posts", f"Post {n}", (px, py, 0), (px, py, top), POST, POST,
              up=(0, 1, 0), mat="walnut", stock="4x4 PT",
              note=("bridge post" if n == "B" else "ladder post" if n == "Bp"
                    else "room-corner stub" if n == "A" else ""))
        m["zrot"] = rot
        m["anchor"] = (px, py)

    anchors = {m["label"].split()[1]: m["anchor"] for m in MEMBERS if m["group"] == "Loft / Posts"}

    # --- ledgers (load path) -------------------------------------------
    zc = JOIST_TOP - JOIST_D/2.0
    M("Loft / Ledgers", "Ledger N (north wall)", (0, ROOM_D-T_2X/2, zc), (LOFT_SIZE, ROOM_D-T_2X/2, zc),
      T_2X, W_2X6, mat="honey", stock="2x6 PT", note="lag to studs @16 O.C., 3/8 x 4 lag + washer")
    M("Loft / Ledgers", "Ledger W (west wall)", (T_2X/2, ROOM_D-LOFT_SIZE, zc), (T_2X/2, ROOM_D-T_2X, zc),
      T_2X, W_2X6, mat="honey", stock="2x6 PT", note="lag to studs @16 O.C.")

    # --- rim joists around the hexagon ---------------------------------
    for a, b in [("B","C"), ("C","D"), ("D","Cp"), ("Cp","Bp")]:
        (x0, y0), (x1, y1), L, d = edge(a, b)
        n_in = inward(a, b)
        ox, oy = n_in[0]*T_2X/2, n_in[1]*T_2X/2
        ang = {("B","C"):(90.0,78.75), ("C","D"):(78.75,67.5),
               ("D","Cp"):(67.5,78.75), ("Cp","Bp"):(78.75,90.0)}[(a,b)]
        M("Loft / Rim", f"Rim {a}-{b}", (x0+ox, y0+oy, zc), (x1+ox, y1+oy, zc),
          T_2X, W_2X6, mat="honey", stock="2x6",
          ends=ang, note=f"outside face length {L:.3f}\"")

    # --- field joists: run E-W, hung off the west-wall ledger -----------
    def east_edge(v):
        """u at the hexagon boundary for a given local v."""
        if v <= HEX_H: return LOFT_SIZE
        if v <= PTS["D"][1]:
            s = (v - HEX_H) / math.cos(math.radians(22.5))
            return LOFT_SIZE - math.sin(math.radians(22.5))*s
        u = (v - PTS["D"][1]) / math.sin(math.radians(22.5))
        return PTS["D"][0] - math.cos(math.radians(22.5))*u

    joists = []
    v = JOIST_OC
    while v < LOFT_SIZE - 1.0:
        u_end = east_edge(v)
        joists.append((v, u_end))
        v += JOIST_OC
    for i, (v, u_end) in enumerate(joists, 1):
        y = ROOM_D - v
        skew = v > HEX_H
        M("Loft / Joists", f"Joist J{i}", (T_2X, y, zc), (u_end - T_2X, y, zc),
          W_2X6, T_2X, up=(0, 1, 0), mat="honey", stock="2x6",
          ends=(90.0, 67.5 if v > PTS["D"][1] else (78.75 if skew else 90.0)),
          note=("skew-cut; Simpson LSU26 skewable hanger" if skew else "LUS26 hanger both ends"))
    # blocking behind the D corner
    M("Loft / Joists", "Blocking BLK1",
      (PTS["D"][0]-14, ROOM_D-PTS["D"][1]-2, zc), (PTS["D"][0]-2, ROOM_D-PTS["D"][1]-14, zc),
      W_2X6, T_2X, up=(0,1,0), mat="honey", stock="2x6", ends=(45.0,45.0),
      note="decking support at 135-deg corner")

    # --- knee wall -----------------------------------------------------
    for a, b in [("B","C"), ("C","D"), ("D","Cp"), ("Cp","Bp")]:
        (x0, y0), (x1, y1), L, d = edge(a, b)
        n_in = inward(a, b)
        ox, oy = n_in[0]*(W_2X4/2), n_in[1]*(W_2X4/2)
        for z, nm, st in ((T_2X/2, "bott plate", "2x4 PT"), (KNEE_TOTAL-T_2X/2, "top plate", "2x4")):
            M("Loft / Knee wall", f"{a}-{b} {nm}", (x0+ox, y0+oy, z), (x1+ox, y1+oy, z),
              W_2X4, T_2X, mat="moss", stock=st, note=f"{L:.2f}\" face length")
        nstud = max(2, int(L // KNEE_OC) + 1)
        for k in range(nstud):
            t = 0.0 if nstud == 1 else k/(nstud-1)
            sx = x0 + (x1-x0)*t + ox; sy = y0 + (y1-y0)*t + oy
            M("Loft / Knee wall", f"{a}-{b} stud {k+1}", (sx, sy, T_2X), (sx, sy, KNEE_TOTAL-T_2X),
              W_2X4, W_2X4, up=(0,1,0), mat="moss", stock="2x4",
              note=f"{KNEE_STUD:.2f}\" - NOT 40-42\"")

    # --- hobbit door opening in the D-Cp face --------------------------
    a, b = HDOOR_FACE
    (x0, y0), (x1, y1), L, d = edge(a, b)
    n_in = inward(a, b)
    mid = ((x0+x1)/2 + n_in[0]*W_2X4/2, (y0+y1)/2 + n_in[1]*W_2X4/2)
    half = HDOOR_RO_W/2
    for s in (-1, 1):
        jx, jy = mid[0]+d[0]*s*(half+W_2X4/2), mid[1]+d[1]*s*(half+W_2X4/2)
        M("Loft / Hobbit door", f"Jack stud {'L' if s<0 else 'R'}", (jx, jy, T_2X), (jx, jy, T_2X+HDOOR_RO_H),
          W_2X4, W_2X4, up=(0,1,0), mat="moss", stock="2x4", note=f"{HDOOR_RO_H:.2f}\" jack")
        kx, ky = mid[0]+d[0]*s*(half+W_2X4*1.5), mid[1]+d[1]*s*(half+W_2X4*1.5)
        M("Loft / Hobbit door", f"King stud {'L' if s<0 else 'R'}", (kx, ky, T_2X), (kx, ky, KNEE_TOTAL-T_2X),
          W_2X4, W_2X4, up=(0,1,0), mat="moss", stock="2x4", note=f"{KNEE_STUD:.2f}\" king")
    hz = T_2X + HDOOR_RO_H + HDOOR_HDR/2
    M("Loft / Hobbit door", "Header (2x4 flat)",
      (mid[0]-d[0]*(half+W_2X4), mid[1]-d[1]*(half+W_2X4), hz),
      (mid[0]+d[0]*(half+W_2X4), mid[1]+d[1]*(half+W_2X4), hz),
      W_2X4, HDOOR_HDR, mat="moss", stock="2x4", note="flat - deck load bypasses this wall")
    cz = T_2X + HDOOR_RO_H + HDOOR_HDR
    for s in (-1, 0, 1):
        cx, cy = mid[0]+d[0]*s*half*0.9, mid[1]+d[1]*s*half*0.9
        M("Loft / Hobbit door", f"Cripple {s+2}", (cx, cy, cz), (cx, cy, cz+HDOOR_CRIPPLE),
          W_2X4, W_2X4, up=(0,1,0), mat="moss", stock="2x4", note=f"{HDOOR_CRIPPLE:.2f}\"")
    return anchors, mid, d, n_in, east_edge

ANCHORS, HDOOR_MID, HDOOR_DIR, HDOOR_NRM, east_edge = build_loft()

# ======================================================================
# 2. LADDER  -  REMOVABLE.  This is the 18-month barrier, not the gate.
# ======================================================================
def build_ladder():
    a, b = FACE_LADDER
    (x0, y0), (x1, y1), L, d = edge(a, b)
    n_in = inward(a, b); out = (-n_in[0], -n_in[1])
    cx, cy = (x0+x1)/2, (y0+y1)/2
    top = (cx, cy, DECK_TOP)
    bot = (cx + out[0]*LADDER_RUN, cy + out[1]*LADDER_RUN, 0.0)
    # hanger rail on the deck rim - the ladder hooks over this and lifts off
    M("Ladder", "Hanger rail 2x6",
      (x0+d[0]*3+n_in[0]*T_2X*1.6, y0+d[1]*3+n_in[1]*T_2X*1.6, DECK_TOP-2.75),
      (x1-d[0]*3+n_in[0]*T_2X*1.6, y1-d[1]*3+n_in[1]*T_2X*1.6, DECK_TOP-2.75),
      T_2X, W_2X6, mat="honey", stock="2x6",
      note="lag to rim + both posts; ladder hooks over this, 3/8 pin locks it")
    for s_ in (-1, 1):
        ox, oy = d[0]*s_*(LADDER_W/2 - T_2X/2), d[1]*s_*(LADDER_W/2 - T_2X/2)
        M("Ladder", f"Stringer {'L' if s_<0 else 'R'}",
          (bot[0]+ox, bot[1]+oy, bot[2]), (top[0]+ox, top[1]+oy, top[2]),
          T_2X, W_2X4, up=(0,0,1), mat="walnut", stock="2x4", ends=(65.0, 65.0),
          note=f"{LADDER_LEN:.2f}\" o/a; notch top to hook the hanger rail, 25 deg cut both ends")
        # rigid grab rail - replaces the rope handrails (no slack rope near a toddler)
        gx, gy = d[0]*s_*(LADDER_W/2 + 3.0), d[1]*s_*(LADDER_W/2 + 3.0)
        M("Ladder", f"Grab rail {'L' if s_<0 else 'R'} 2x2",
          (bot[0]+gx, bot[1]+gy, bot[2]+16), (top[0]+gx, top[1]+gy, top[2]+8),
          BAL_S, BAL_S, up=(0,0,1), mat="walnut", stock="2x2",
          note="1/2\" roundover, sand 180. RIGID - sagging rope is a strangulation risk under 3")
        for k in (0.35, 0.8):
            sx = bot[0]+(top[0]-bot[0])*k; sy = bot[1]+(top[1]-bot[1])*k
            M("Ladder", f"Grab standoff {'L' if s_<0 else 'R'}{int(k*100)}",
              (sx+ox, sy+oy, k*LADDER_RISE+2), (sx+gx, sy+gy, k*LADDER_RISE+2),
              BAL_S, BAL_S, mat="walnut", stock="2x2", note="grab-rail standoff block")
    for k in range(1, LADDER_RUNGS+1):
        t = (k*LADDER_RISER)/LADDER_RISE
        rz = k*LADDER_RISER
        rx = bot[0] + (top[0]-bot[0])*t; ry = bot[1] + (top[1]-bot[1])*t
        M("Ladder", f"Rung {k}",
          (rx-d[0]*(LADDER_W/2-T_2X), ry-d[1]*(LADDER_W/2-T_2X), rz),
          (rx+d[0]*(LADDER_W/2-T_2X), ry+d[1]*(LADDER_W/2-T_2X), rz),
          W_2X4, T_2X, mat="honey", stock="2x4",
          note=f"riser {LADDER_RISER:.2f}\"; dado 3/4\" into stringers + 2 screws/end")
    return bot, top, d, out
LADDER_BOT, LADDER_TOP, LADDER_DIR, LADDER_OUT = build_ladder()

# ======================================================================
# 3. GUARDS  -  vertical balusters, CPSC 3.5" torso rule
#    (replaces the rope net AND the bookshelf: shelves in a guard are a ladder)
# ======================================================================
GUARD_INFO = {}
def build_guards():
    for a, b in [("B","C"), ("C","D"), ("D","Cp"), ("Cp","Bp")]:
        (x0, y0), (x1, y1), L, d = edge(a, b)
        n_in = inward(a, b)
        ins = POST/2 + 0.5
        ax, ay = x0 + d[0]*ins, y0 + d[1]*ins
        clear = L - 2*ins
        kind = ("GATE" if (a, b) == GATE_FACE else
                "REMOVABLE PANEL" if (a, b) == PANEL_FACE else "FIXED")
        nb = 3
        while True:
            gap = (clear - nb*BAL_S) / (nb + 1)
            if gap <= BAL_MAX_GAP or nb > 20: break
            nb += 1
        GUARD_INFO[(a, b)] = dict(kind=kind, clear=clear, n=nb, gap=gap)
        note = {"FIXED": "fixed guard",
                "GATE": "SELF-CLOSING GATE leaf - hinged at Cp, swings IN over the deck",
                "REMOVABLE PANEL": "REMOVABLE - 8 screws. Take it off to add the bridge later."}[kind]
        ox, oy = n_in[0]*(BAL_S/2), n_in[1]*(BAL_S/2)
        M("Loft / Guards", f"{a}-{b} top rail",
          (ax+ox, ay+oy, POST_TOP-RAIL_T/2), (ax+d[0]*clear+ox, ay+d[1]*clear+oy, POST_TOP-RAIL_T/2),
          W_2X4, RAIL_T, mat="walnut", stock="2x4",
          note=f"{note}; top of rail = {POST_TOP:.0f}\" = {GUARD_H:.0f}\" above deck")
        M("Loft / Guards", f"{a}-{b} toe board",
          (ax+ox, ay+oy, DECK_TOP+TOE_H/2), (ax+d[0]*clear+ox, ay+d[1]*clear+oy, DECK_TOP+TOE_H/2),
          T_2X, TOE_H, mat="walnut", stock="2x4",
          note="on edge at deck level; closes the bottom gap, stops kicked toys")
        for k in range(nb):
            t = (gap*(k+1) + BAL_S*k + BAL_S/2) / clear
            bx, by = ax + d[0]*clear*t + ox, ay + d[1]*clear*t + oy
            M("Loft / Guards", f"{a}-{b} baluster {k+1}",
              (bx, by, BAL_BOT), (bx, by, BAL_TOP), BAL_S, BAL_S, up=(0,0,1),
              mat="walnut", stock="2x2",
              note=f"{gap:.3f}\" clear gap - CPSC limit is 3.5\"; 1/4\" roundover")
        if kind == "GATE":
            for s_, nm in ((0.0, "hinge stile"), (1.0, "latch stile")):
                sx, sy = ax + d[0]*clear*s_ + ox, ay + d[1]*clear*s_ + oy
                M("Loft / Guards", f"Gate {nm}", (sx, sy, DECK_TOP), (sx, sy, POST_TOP),
                  W_2X4, T_2X, up=(0,0,1), mat="walnut", stock="2x4",
                  note="self-closing spring hinges (pr) / gravity latch + magnetic catch. NO lock.")
build_guards()

# ======================================================================
# 3b. GROUND-LEVEL DEN SHELF  (apothecary relocated out of the guardrail)
# ======================================================================
def build_den_shelf():
    a, b = DEN_SHELF_FACE
    (x0, y0), (x1, y1), L, d = edge(a, b)
    n_in = inward(a, b)
    ins = POST/2 + 1.5
    clear = L - 2*ins
    for z in DEN_SHELF_Z:
        M("Loft / Den shelf", f'Shelf @ {z:.0f}"',
          (x0+d[0]*ins+n_in[0]*(DEN_SHELF_D/2+W_2X4), y0+d[1]*ins+n_in[1]*(DEN_SHELF_D/2+W_2X4), z),
          (x0+d[0]*(ins+clear)+n_in[0]*(DEN_SHELF_D/2+W_2X4), y0+d[1]*(ins+clear)+n_in[1]*(DEN_SHELF_D/2+W_2X4), z),
          DEN_SHELF_D, PLY, mat="honey", stock='3/4" ply',
          note=f'{clear:.1f}" x {DEN_SHELF_D}"; screw to studs, 1/4" roundover, 2" lip')
        lipo = W_2X4 + DEN_SHELF_D - 0.4
        M("Loft / Den shelf", f'Shelf lip @ {z:.0f}"',
          (x0+d[0]*ins+n_in[0]*lipo, y0+d[1]*ins+n_in[1]*lipo, z+1.4),
          (x0+d[0]*(ins+clear)+n_in[0]*lipo, y0+d[1]*(ins+clear)+n_in[1]*lipo, z+1.4),
          0.75, 2.0, mat="walnut", stock="1x3", note="book lip, rounded")
    return clear
DEN_SHELF_CLEAR = build_den_shelf()

# ======================================================================
# 4. PLAYHOUSE
# ======================================================================
PH_POSTS = {
    "SW": (PH_X0 + POST/2,            PH_Y0 + POST/2),
    "WM": (PH_X0 + POST/2,            ROOM_D - PH_BRIDGE_BAY - POST/2),
    "NW": (PH_X0 + POST/2,            ROOM_D - POST/2),
    "SE": (ROOM_W - POST/2,           PH_Y0 + POST/2),
}
def build_playhouse():
    for n, (x, y) in PH_POSTS.items():
        M("Playhouse / Posts", f"Post {n}", (x, y, 0), (x, y, PH_POST_LEN), POST, POST,
          up=(0,1,0), mat="walnut", stock="4x4 PT",
          note={"SW":"exposed room corner","WM":"bridge bay post","NW":"lag to N wall studs",
                "SE":"lag to E wall studs"}[n])
    z = PH_WALL_H + T_2X/2
    runs = [("Plate W", (PH_X0+POST/2, PH_Y0, z), (PH_X0+POST/2, ROOM_D, z)),
            ("Plate S", (PH_X0, PH_Y0+POST/2, z), (ROOM_W, PH_Y0+POST/2, z)),
            ("Plate N", (PH_X0, ROOM_D-T_2X/2, z), (ROOM_W, ROOM_D-T_2X/2, z)),
            ("Plate E", (ROOM_W-T_2X/2, PH_Y0, z), (ROOM_W-T_2X/2, ROOM_D, z))]
    for nm, p0, p1 in runs:
        M("Playhouse / Plates", nm, p0, p1, W_2X4, T_2X, mat="honey", stock="2x4",
          note="top plate @ 84\" - anchors roof + trim")
    # gable roof, ridge N-S at x = center
    ridge_x = PH_X0 + PH_SIZE/2
    M("Playhouse / Roof", "Ridge board", (ridge_x, PH_Y0-2, PH_RIDGE-2.75), (ridge_x, ROOM_D, PH_RIDGE-2.75),
      T_2X, W_2X6, mat="walnut", stock="2x6", note="1x6 or 2x6 ridge, 1\" below ceiling")
    rise = (PH_RIDGE - 2.75) - (PH_WALL_H + T_2X)
    run  = PH_SIZE/2
    pitch = rise/run*12
    ny = 4
    for i in range(ny):
        y = PH_Y0 - 2 + (ROOM_D - (PH_Y0-2)) * i/(ny-1)
        for s, xe in ((-1, PH_X0-2.0), (1, ROOM_W+2.0)):
            M("Playhouse / Roof", f"Rafter {'W' if s<0 else 'E'}{i+1}",
              (ridge_x, y, PH_RIDGE-2.75), (xe, y, PH_WALL_H+T_2X - 2.0*rise/run),
              T_2X, W_2X4, mat="walnut", stock="2x4",
              ends=(round(math.degrees(math.atan2(run, rise)),2),)*2,
              note=f"{pitch:.2f}:12 pitch, 2\" overhang")
    # south gable infill + door framing
    z2 = PH_WALL_H
    for s in (-1, 1):
        jx = PH_X0 + PH_SIZE/2 + s*(PH_DOOR_RO_W/2 + W_2X4/2)
        M("Playhouse / Door", f"Jack {'L' if s<0 else 'R'}", (jx, PH_Y0+W_2X4/2, 0), (jx, PH_Y0+W_2X4/2, PH_DOOR_RO_H),
          W_2X4, W_2X4, up=(0,1,0), mat="moss", stock="2x4", note=f"{PH_DOOR_RO_H:.0f}\" jack")
        kx = PH_X0 + PH_SIZE/2 + s*(PH_DOOR_RO_W/2 + W_2X4*1.5)
        M("Playhouse / Door", f"King {'L' if s<0 else 'R'}", (kx, PH_Y0+W_2X4/2, 0), (kx, PH_Y0+W_2X4/2, PH_WALL_H),
          W_2X4, W_2X4, up=(0,1,0), mat="moss", stock="2x4", note=f'{PH_WALL_H:.0f}" king')
    M("Playhouse / Door", "Header (2) 2x6",
      (PH_X0+PH_SIZE/2-PH_DOOR_RO_W/2-W_2X4, PH_Y0+W_2X4/2, PH_DOOR_RO_H+W_2X6/2),
      (PH_X0+PH_SIZE/2+PH_DOOR_RO_W/2+W_2X4, PH_Y0+W_2X4/2, PH_DOOR_RO_H+W_2X6/2),
      3.0, W_2X6, mat="moss", stock="2x6", note="double 2x6 header over 26\" R.O.")
build_playhouse()

# ======================================================================
# 5. BRIDGE PROVISIONS ONLY  -  the bridge itself is NOT built in phase 1
# ======================================================================
def build_bridge():
    yc = ROOM_D - PH_BRIDGE_BAY/2 - T_2X
    y0, y1 = yc - BRIDGE_W/2, yc + BRIDGE_W/2
    for nm, x0, x1 in (("Future bridge ledger - loft side", LOFT_SIZE-20, LOFT_SIZE+1.5),
                       ("Future bridge ledger - playhouse side", PH_X0-1.5, PH_X0+20)):
        M("Bridge / Future provisions", nm,
          (x0, ROOM_D-T_2X/2, DECK_TOP-W_2X6/2), (x1, ROOM_D-T_2X/2, DECK_TOP-W_2X6/2),
          T_2X, W_2X6, mat="honey", stock="2x6 PT",
          note="INSTALL NOW. Lag 3/8x4 into 2 studs min. Eye bolts get added later.")
    for nm, x in (("Future net header - loft", LOFT_SIZE-T_2X/2),
                  ("Future net header - playhouse", PH_X0+T_2X/2)):
        M("Bridge / Future provisions", nm, (x, y0, DECK_TOP-W_2X6/2), (x, y1, DECK_TOP-W_2X6/2),
          T_2X, W_2X6, mat="honey", stock="2x6",
          note="INSTALL NOW as blocking. Drill for 4x 3/8 eye bolts when the bridge goes in.")
    return y0, y1, yc
BR_Y0, BR_Y1, BR_YC = build_bridge()

# ======================================================================
# CUT LIST
# ======================================================================
def cutlist():
    from collections import defaultdict
    rows = defaultdict(lambda: defaultdict(int))
    for m in MEMBERS:
        key = (m["group"], m["stock"], round(m["L"], 2), m["ends"], m["note"])
        rows[m["group"]][key] += 1
    out = []
    for g in dict.fromkeys(m["group"] for m in MEMBERS):
        for (grp, stock, L, ends, note), qty in rows[g].items():
            out.append(dict(group=grp, stock=stock, length=L, qty=qty, ends=ends, note=note))
    return out

if __name__ == "__main__":
    import json, collections
    print(f"{len(MEMBERS)} members")
    c = collections.Counter(m["group"] for m in MEMBERS)
    for k, v in c.items(): print(f"  {k:28s} {v}")
    tot = collections.defaultdict(float)
    for m in MEMBERS: tot[m["stock"]] += m["L"]
    print("\nlinear feet by stock:")
    for k, v in sorted(tot.items()): print(f"  {k:12s} {v/12:8.1f} lf")
