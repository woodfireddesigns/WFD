"""LEGO-manual style step renders.
Parts installed THIS step render in amber; everything already built goes pale grey.
Isometric camera, flat lighting, white background, black outlines via Freestyle.
"""
import sys, os, math, bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from params import *
import geometry as G
from assembly import STEPS

IN = 0.0254
W   = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
SMP = int(sys.argv[2]) if len(sys.argv) > 2 else 24
OUT = os.path.join(HERE, "exports", "steps")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "exports", "playroom_build.blend"))
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = SMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.render.film_transparent = True   # white page shows through
sc.view_settings.view_transform = 'Standard'

# flat white world
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.55

# black outlines - this is what makes it read as an instruction manual
sc.render.use_freestyle = True
vl = sc.view_layers[0]; vl.use_freestyle = True
fs = vl.freestyle_settings
fs.as_render_pass = False
if not fs.linesets:
    fs.linesets.new("outline")
lset = fs.linesets[0]
lset.select_silhouette = True; lset.select_border = True
lset.select_crease = True; lset.select_edge_mark = False
if lset.linestyle is None:
    lset.linestyle = bpy.data.linestyles.new("OutlineStyle")
lset.linestyle.thickness = 2.4
lset.linestyle.color = (0.05, 0.05, 0.05)

def mat(name, rgb, rough=0.62):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    return m

M_NEW  = mat("STEP_NEW",  (0.88, 0.52, 0.09), 0.92)   # amber - installed this step
M_OLD  = mat("STEP_OLD",  (0.60, 0.60, 0.58), 0.92)   # pale grey - already built
M_WALL = mat("STEP_WALL", (0.88, 0.88, 0.86), 0.95)

# lighting: one soft key plus fill, no drama
for loc, e, sz, rot in (((200, -60, 220), 620, 220, (math.radians(38), 0, math.radians(62))),
                        ((60, -200, 150), 340, 220, (math.radians(52), 0, math.radians(8))),
                        ((30, ROOM_D-30, 300), 260, 320, (0, 0, 0))):
    d = bpy.data.lights.new("k", 'AREA'); d.energy = e; d.size = sz*IN
    o = bpy.data.objects.new("k", d); sc.collection.objects.link(o)
    o.location = Vector(loc)*IN; o.rotation_euler = rot

MESHES = [o for o in bpy.data.objects if o.type in ('MESH', 'CURVE')]
ROOM   = [o for o in MESHES if any(p in o.name for p in ("Wall_", "Ceiling", "Floor"))]
BUILD  = [o for o in MESHES if o not in ROOM]
for o in ROOM:                      # the real room shell blocks every useful angle
    bpy.data.objects.remove(o, do_unlink=True)

# two small panels + a floor pad, just enough to read as "the corner of your room"
import bmesh
def panel(name, cen, sx, sy, sz):
    me = bpy.data.meshes.new(name); ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    from mathutils import Matrix
    ob.matrix_world = (Matrix.Translation(Vector(cen)*IN)
                       @ Matrix.Diagonal((sx*IN, sy*IN, sz*IN, 1.0)))
    return ob
PAD = 4.0
SHELL = [
    panel("RoomWallN", (LOFT_SIZE/2, ROOM_D + 1.5, 44), LOFT_SIZE + PAD*2, 3, 88),
    panel("RoomWallW", (-1.5, ROOM_D - LOFT_SIZE/2, 44), 3, LOFT_SIZE + PAD*2, 88),
    panel("RoomFloor", (LOFT_SIZE/2 - 2, ROOM_D - LOFT_SIZE/2 + 2, -1.0),
          LOFT_SIZE + PAD*4, LOFT_SIZE + PAD*4, 2),
]

def group_of(ob):
    for c in ob.users_collection:
        return c.name
    return ""

GROUP_MAP = {}
for m in G.MEMBERS:
    GROUP_MAP.setdefault(m["group"], set()).add(m["label"])

def objects_for(step):
    sel = set()
    for g in step["groups"]:
        for nm in GROUP_MAP.get(g, ()):
            for o in BUILD:
                if o.name == nm or o.name.startswith(nm + "."):
                    sel.add(o)
    for pat in step["objects"]:
        for o in BUILD:
            if pat in o.name:
                sel.add(o)
    return sel

def paint(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m)

# isometric camera, auto-fitted to the bounding box of everything buildable
pts = []
for o in BUILD + SHELL:
    for corner in o.bound_box:
        pts.append(o.matrix_world @ Vector(corner))
ctr = sum(pts, Vector((0, 0, 0))) / len(pts)
c = bpy.data.cameras.new("iso"); c.type = 'ORTHO'
cam = bpy.data.objects.new("iso", c); sc.collection.objects.link(cam)
_d = Vector((1.0, -1.05, 0.72)); _d.normalize()
cam.location = ctr + _d * (400*IN)
cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam
AR = 0.95
sc.render.resolution_x = W; sc.render.resolution_y = int(W*AR)
# project the bbox onto the camera axes to size the frame exactly
R = cam.matrix_world.to_3x3()
right, up = R.col[0], R.col[1]
hw = max(abs((p - ctr).dot(right)) for p in pts)
hh = max(abs((p - ctr).dot(up)) for p in pts)
c.ortho_scale = max(hw * 2, hh * 2 / AR) * 1.10
print(f"fit: half-w {hw/IN:.1f}in  half-h {hh/IN:.1f}in  ortho {c.ortho_scale/IN:.1f}in")

ONLY = os.environ.get("ONLY_STEP")
cumulative = set()
for step in STEPS:
    new = objects_for(step)
    for o in BUILD:
        o.hide_render = o not in (cumulative | new)
    for o in SHELL:
        o.hide_render = False
        paint(o, M_WALL)
    for o in cumulative - new:
        paint(o, M_OLD)
    for o in new:
        paint(o, M_NEW)
    if ONLY and str(step["n"]) != ONLY:
        cumulative |= new; continue
    sc.render.filepath = os.path.join(OUT, f"step_{step['n']:02d}.png")
    bpy.ops.render.render(write_still=True)
    print("WROTE", f"step_{step['n']:02d}.png", f"({len(new)} new)")
    cumulative |= new

if ONLY:
    print("STEPS DONE"); raise SystemExit
# one finished hero, everything amber-free
for o in BUILD: o.hide_render = False
for o in BUILD: paint(o, M_OLD)
sc.render.filepath = os.path.join(OUT, "step_99_complete.png")
bpy.ops.render.render(write_still=True)
print("WROTE step_99_complete.png")
print("STEPS DONE")
