"""Renders orthographic plan/elevations + perspective views. Run: python3 blender/render_views.py [samples] [res]"""
import sys, os, math, bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from params import *

IN = 0.0254
SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 48
RES     = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
OUT     = os.path.join(HERE, "exports", "renders")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "exports", "playroom_build.blend"))
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'

# world
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.40, 0.44, 0.50, 1); bg.inputs[1].default_value = 0.25
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = 0.2

def light(name, loc, energy, size=40.0, color=(1, 0.95, 0.88)):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.size = size*IN; d.color = color
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
    o.location = Vector(loc)*IN
    o.rotation_euler = (0, 0, 0)
    return o

# --- lighting: everything lives INSIDE the room ---
k = light("Key", (ROOM_W*0.62, 26, 88), 900, 70, (1.0, 0.90, 0.74))
k.rotation_euler = (math.radians(46), 0, math.radians(38))
f = light("Fill", (ROOM_W*0.40, ROOM_D*0.40, 90), 420, 150, (0.86, 0.90, 1.0))
f2 = light("Bounce", (12, 30, 34), 170, 90, (1.0, 0.94, 0.86))
f2.rotation_euler = (math.radians(-64), 0, math.radians(-30))
r = light("Rim", (ROOM_W-16, ROOM_D-14, 82), 430, 40, (1.0, 0.84, 0.62))
r.rotation_euler = (math.radians(58), 0, math.radians(-150))
for loc, e, col in (((26, ROOM_D-26, 18), 65, (1.0,0.66,0.32)),
                    ((PH_X0+24, PH_Y0+26, 46), 95, (1.0,0.72,0.38)),
                    ((LOFT_SIZE*0.5, ROOM_D-30, 58), 48, (1.0,0.78,0.48))):
    pl = bpy.data.lights.new("prac", 'POINT'); pl.energy = e; pl.color = col; pl.shadow_soft_size = 5*IN
    o = bpy.data.objects.new("prac", pl); sc.collection.objects.link(o); o.location = Vector(loc)*IN

def cam(name, loc, target, ortho=None, lens=30.0):
    c = bpy.data.cameras.new(name); c.lens = lens
    if ortho: c.type = 'ORTHO'; c.ortho_scale = ortho*IN
    o = bpy.data.objects.new(name, c); sc.collection.objects.link(o)
    o.location = Vector(loc)*IN
    d = Vector(target)*IN - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

def shoot(camobj, fname, w=RES, h=None, transparent=False, hide=()):
    sc.camera = camobj
    sc.render.resolution_x = w; sc.render.resolution_y = h or int(w*0.72)
    sc.render.film_transparent = transparent
    hidden = []
    for pat in hide:
        for ob in bpy.data.objects:
            if pat in ob.name and not ob.hide_render:
                ob.hide_render = True; hidden.append(ob)
    sc.render.filepath = os.path.join(OUT, fname)
    bpy.ops.render.render(write_still=True)
    for ob in hidden: ob.hide_render = False
    print("WROTE", fname)

CX, CY = ROOM_W/2, ROOM_D/2
S, E, Wl, Ce = "Wall_S", "Wall_E", "Wall_W", "Ceiling"
VIEWS = [
  ("01_hero_iso",       cam("c1", (154, 10, 74), (58, ROOM_D-26, 40), lens=17),            dict(w=1800, h=1150, hide=(S, E, Ce))),
  ("02_loft_three_qtr", cam("c2", (104, 46, 56), (22, ROOM_D-26, 34), lens=22),            dict(w=1500, h=1200, hide=(S, E, Ce))),
  ("03_playhouse_front",cam("c3", (78, 8, 52),  (PH_X0+24, PH_Y0+10, 44), lens=32),        dict(w=1400, h=1250, hide=(S, Wl, Ce))),
  ("04_bridge_along",   cam("c4", (CX, 46, 58),  (CX+4, ROOM_D-8, 54), lens=24),           dict(w=1600, h=1100, hide=(S, Ce))),
  ("05_hobbit_door",    cam("c5", (54, 66, 24),  (26, ROOM_D-54, 16), lens=32),            dict(w=1400, h=1200, hide=(S, Ce))),
  ("06_from_doorway",   cam("c6", (ROOM_DOOR_X+16, 14, 58), (ROOM_W*0.44, ROOM_D*0.9, 36), lens=14), dict(w=1900, h=1080, hide=(S, Ce))),
]
SHELL = ("Wall_", "Ceiling", "Floor")
ORTHO = [
  ("T1_plan",       cam("o1", (CX, CY, 420), (CX, CY, 0), ortho=190), dict(w=1700, h=1700, hide=SHELL)),
  ("T2_elev_north", cam("o2", (CX, -500, 46), (CX, CY, 46), ortho=190), dict(w=1900, h=1150, hide=(S, Ce))),
  ("T3_elev_west",  cam("o3", (700, CY, 46), (CX, CY, 46), ortho=190), dict(w=1900, h=1150, hide=(E, Ce))),
  ("T4_loft_frame", cam("o4", (-300, -300, 240), (30, ROOM_D-30, 30), ortho=126),
                    dict(w=1600, h=1400, hide=SHELL+("Skin","LoftDeck","slab","arch","Roof","PH ","Net ","Bridge","wrap","hinge","knob","Porthole","window"))),
]
for nm, c, kw in VIEWS + ORTHO:
    shoot(c, nm + ".png", **kw)
print("RENDER DONE")
