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
HEX_H         = 20.0         # length of the two short side faces B-C and C'-B'
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

# --- ladder ----------------------------------------------------------
LADDER_ANGLE  = 65.0                     # degrees from horizontal
LADDER_RISE   = DECK_TOP
LADDER_RUN    = LADDER_RISE / math.tan(math.radians(LADDER_ANGLE))
LADDER_LEN    = LADDER_RISE / math.sin(math.radians(LADDER_ANGLE))
LADDER_W      = 18.0                     # outside of stringers
LADDER_RUNGS  = 4
LADDER_RISER  = LADDER_RISE / (LADDER_RUNGS + 1)   # 8.8"

# --- bookshelf guard -------------------------------------------------
SHELF_DEPTH   = 7.25
SHELF_H       = GUARD_H
SHELF_COUNT   = 2

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
# CONNECTOR - ROPE / NET BRIDGE
# ----------------------------------------------------------------------
BRIDGE_X0     = LOFT_SIZE                # 60  - loft east rim
BRIDGE_X1     = PH_X0                    # 114 - playhouse west face
BRIDGE_SPAN   = BRIDGE_X1 - BRIDGE_X0    # 54  (brief said ~42 - see plan note 3)
BRIDGE_W      = 18.0
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
