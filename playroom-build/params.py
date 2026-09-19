"""
Kids' Playroom Build - single source of truth for all dimensions.
Every number in the Blender model, the PDF plans, and the cut list
is derived from this file. Units: INCHES throughout.
"""
import math

# ----------------------------------------------------------------------
# ROOM
# ----------------------------------------------------------------------
ROOM_W        = 162.0        # 13'-6"  (X axis, west->east). Loft & playhouse both on this wall.
ROOM_D        = 161.0        # 13'-5"  (Y axis, south->north)
CEILING       = 96.0
STUD_OC       = 16.0
DOOR_WALL     = "south"      # y = 0
ROOM_DOOR_W   = 32.0
ROOM_DOOR_X   = 65.0         # left edge of room door opening on south wall

# Nominal -> actual lumber
T_2X          = 1.5
W_2X4         = 3.5
W_2X6         = 5.5
POST          = 3.5          # 4x4 actual
PLY           = 0.75

# ----------------------------------------------------------------------
# STRUCTURE 1 - CORNER LOFT  (northwest corner: walls at x=0 and y=ROOM_D)
# Local frame: origin at room corner, +u = room +x, +v = room -y (into room)
# ----------------------------------------------------------------------
LOFT_SIZE     = 60.0         # 60" x 60" footprint envelope
DECK_TOP      = 44.0         # finished platform height off floor
JOIST_D       = W_2X6
DECK_PLY      = PLY
JOIST_TOP     = DECK_TOP - DECK_PLY      # 43.25
JOIST_BOT     = JOIST_TOP - JOIST_D      # 37.75
JOIST_OC      = 16.0

GUARD_H       = 36.0                     # guard height above deck (top of 32-36" range)
POST_TOP      = DECK_TOP + GUARD_H       # 80.0
POST_LEN_TALL = POST_TOP                 # 4x4 cut length for the 5 perimeter posts
POST_LEN_CORNER = JOIST_BOT              # stub post in the room corner (37.75)

# Hexagon: symmetric about the 45-deg diagonal.
# Interior angles: 90 (corner A), 90 (B), 157.5 (C), 135 (D), 157.5 (C'), 90 (B')
# -> miters are 11.25 deg (22.5 joint) and 22.5 deg (45 joint). Both are saw detents.
HEX_H         = 24.0         # short faces B-C and C'-B'. 24 so a FUTURE bridge can be 24" wide, not 18".
_A22          = math.radians(22.5)
_RUN_PER_LEN  = math.sin(_A22) + math.cos(_A22)   # 1.3065630
HEX_T         = (LOFT_SIZE - HEX_H) / _RUN_PER_LEN  # length of each angled face
_DX           = math.sin(_A22) * HEX_T
_DY           = math.cos(_A22) * HEX_T

# Loft deck outline in LOCAL (u,v) inches
LOFT_POLY = [
    ("A",  0.0,                0.0),               # room corner (wall/wall)
    ("B",  LOFT_SIZE,          0.0),               # north wall, outer end  -> BRIDGE post
    ("C",  LOFT_SIZE,          HEX_H),             # 22.5 deg joint
    ("D",  LOFT_SIZE - _DX,    HEX_H + _DY),       # 45 deg joint, on the diagonal
    ("Cp", HEX_H,              LOFT_SIZE),         # 22.5 deg joint
    ("Bp", 0.0,                LOFT_SIZE),         # west wall, outer end   -> LADDER post
]
LOFT_TALL_POSTS = ["B", "C", "D", "Cp", "Bp"]      # 5 tall + 1 corner stub = 6 posts

# Face assignments
FACE_BRIDGE   = ("B",  "C")    # 20" - bridge gate
FACE_SHELF    = ("C",  "D")    # angled - integrated bookshelf guard
FACE_NET      = ("D",  "Cp")   # angled - rope net guard
FACE_LADDER   = ("Cp", "Bp")   # 20" - ladder entry

# --- enclosed knee wall under the loft -------------------------------
KNEE_TOTAL    = JOIST_BOT                # 37.75 floor to underside of joists
KNEE_STUD     = KNEE_TOTAL - 2 * T_2X    # 34.75  (NOT the 40-42" in the brief)
KNEE_OC       = 16.0

# Hobbit door in the knee wall (loft ground level)
HDOOR_RO_W    = 26.0
HDOOR_RO_H    = 32.0                     # capped by KNEE_TOTAL, not the 36-38" in the brief
HDOOR_HDR     = T_2X                     # single 2x4 laid flat
HDOOR_CRIPPLE = KNEE_TOTAL - HDOOR_RO_H - HDOOR_HDR - T_2X   # 2.75
HDOOR_SLAB_W  = 24.0
HDOOR_SLAB_H  = 30.75
HDOOR_ARCH_R  = HDOOR_SLAB_W / 2.0       # true semicircular head, r = 12
HDOOR_FACE    = FACE_NET                 # centered on the D-C' angled face

PORTHOLE_D    = 8.0                      # acrylic disc
PORTHOLE_Z    = 24.0                     # center height off floor
PORTHOLE_FACE = FACE_SHELF

# --- age staging ------------------------------------------------------
# 18 mo - 3 yr : ground den + playhouse only. Ladder stored off the structure.
# 3 yr +       : ladder hung, loft in use, gate self-closing.
# 5 yr +       : unscrew the bridge panel, add the bridge.
AGE_MIN_LOFT  = 36           # months, and only once they climb it unassisted

# --- ladder ----------------------------------------------------------
LADDER_ANGLE  = 65.0                     # degrees from horizontal
LADDER_RISE   = DECK_TOP
LADDER_RUN    = LADDER_RISE / math.tan(math.radians(LADDER_ANGLE))
LADDER_LEN    = LADDER_RISE / math.sin(math.radians(LADDER_ANGLE))
LADDER_W      = 18.0                     # outside of stringers
LADDER_REMOVABLE = True                  # lifts off its hanger rail - this is the toddler barrier
LADDER_RUNGS  = 5                        # 5 rungs -> 7.33" riser, short legs
LADDER_RISER  = LADDER_RISE / (LADDER_RUNGS + 1)   # 8.8"

# --- GUARDS -----------------------------------------------------------
# CPSC 3.5" torso rule: no opening in a guard may pass a 3.5" probe.
# That rules out the 4-6" rope net originally specced - it sits square in the
# 3.5"-9" head-entrapment window. Vertical balusters instead. Rope stays as a
# tight decorative wrap only: no slack, no loops (strangulation risk under 3).
BAL_S         = 1.5          # 2x2 actual
BAL_MAX_GAP   = 3.375        # 1/8" under the 3.5" limit
TOE_H         = 3.5          # 2x4 on edge at deck level - closes the bottom gap AND stops kicked toys
RAIL_T        = T_2X         # 2x4 laid flat as the top rail
BAL_BOT       = DECK_TOP + TOE_H
BAL_TOP       = POST_TOP - RAIL_T
BAL_LEN       = BAL_TOP - BAL_BOT

GATE_FACE     = ("Cp", "Bp")   # ladder entry - self-closing swing gate
PANEL_FACE    = ("B",  "C")    # future bridge gate - REMOVABLE baluster panel

# --- ground-level den shelf (the apothecary moved down here) -----------
# Shelves in a guardrail are a climbing aid. At floor level they are just shelves.
DEN_SHELF_FACE  = ("B", "C")
DEN_SHELF_D     = 7.25
DEN_SHELF_Z     = (9.0, 19.0)

# ----------------------------------------------------------------------
# STRUCTURE 2 - PLAYHOUSE (northeast corner)
# ----------------------------------------------------------------------
PH_SIZE       = 48.0
PH_X0         = ROOM_W - PH_SIZE         # 114
PH_Y0         = ROOM_D - PH_SIZE         # 113
PH_WALL_H     = 84.0                     # top of wall / top plate bottom
PH_PLATE_TOP  = PH_WALL_H + T_2X         # 85.5
PH_RIDGE      = 95.0                     # 1" below ceiling
PH_POST_LEN   = PH_WALL_H                # 4x4 cut length
PH_BRIDGE_BAY = 18.0                     # bay on the west face that matches the loft gate

PH_DOOR_RO_W  = 26.0
PH_DOOR_RO_H  = 48.0                     # no headroom limit here
PH_DOOR_SLAB_W= 24.0
PH_DOOR_SLAB_H= 46.75
PH_WINDOW_D   = 12.0                     # round window above the door
PH_WINDOW_Z   = 62.0

# ----------------------------------------------------------------------
# CONNECTOR - ROPE BRIDGE  ***NOT BUILT IN PHASE 1***
# Provisions only: wall ledgers, the playhouse bay post, and a removable
# baluster panel at the loft gate. Adding the bridge later = unscrew the
# panel, drill 4 holes, bolt 4 eye bolts. No opening up of finished work.
# ----------------------------------------------------------------------
BRIDGE_BUILD  = False
BRIDGE_X0     = LOFT_SIZE                # 60  - loft east rim
BRIDGE_X1     = PH_X0                    # 114 - playhouse west face
BRIDGE_SPAN   = BRIDGE_X1 - BRIDGE_X0    # 54  (brief said ~42 - see plan note 3)
BRIDGE_W      = HEX_H                    # 24" - was 18", too narrow to walk
BRIDGE_DECK_Z = DECK_TOP
BRIDGE_TOP_Z  = DECK_TOP + GUARD_H       # 80
BRIDGE_SAG    = 7.0                      # expected free-hang sag at this span
NET_ROPE_D    = 0.5                      # 1/2" poly, exceeds the 3/8" minimum

# ----------------------------------------------------------------------
# PALETTE (Blender materials + Higgsfield prompt language)
# ----------------------------------------------------------------------
PALETTE = {
    "moss":    (0.129, 0.208, 0.145),
    "walnut":  (0.227, 0.141, 0.086),
    "honey":   (0.639, 0.427, 0.196),
    "oak":     (0.545, 0.408, 0.251),
    "iron":    (0.055, 0.055, 0.059),
    "rope":    (0.706, 0.612, 0.435),
    "wall":    (0.898, 0.878, 0.827),
    "floor":   (0.482, 0.365, 0.243),
}

def local_to_room(u, v):
    """Loft local (u,v) -> room (x,y). Loft sits in the NW corner."""
    return (u, ROOM_D - v)
