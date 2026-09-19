import sys, os, math, bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from params import *
IN = 0.0254
OUT = os.path.join(HERE, "exports", "renders")
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "exports", "playroom_build.blend"))
sc = bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=64
sc.cycles.use_denoising=True; sc.cycles.max_bounces=6
sc.render.image_settings.file_format='PNG'
w = bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value=(0.55,0.58,0.62,1); bg.inputs[1].default_value=0.9
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
for nm, loc, e, sz, rot in (("k",(ROOM_W*0.6,-40,150),1800,120,(math.radians(34),0,math.radians(26))),
                            ("f",(-60,-60,120),800,160,(math.radians(48),0,math.radians(-34))),
                            ("t",(ROOM_W/2,ROOM_D/2,260),900,200,(0,0,0))):
    d=bpy.data.lights.new(nm,'AREA'); d.energy=e; d.size=sz*IN
    o=bpy.data.objects.new(nm,d); sc.collection.objects.link(o)
    o.location=Vector(loc)*IN; o.rotation_euler=rot
def cam(n, loc, tgt, ortho):
    c=bpy.data.cameras.new(n); c.type='ORTHO'; c.ortho_scale=ortho*IN
    o=bpy.data.objects.new(n,c); sc.collection.objects.link(o); o.location=Vector(loc)*IN
    o.rotation_euler=(Vector(tgt)*IN-o.location).to_track_quat('-Z','Y').to_euler(); return o
def shoot(c,f,w,h,hide):
    sc.camera=c; sc.render.resolution_x=w; sc.render.resolution_y=h
    hid=[]
    for pat in hide:
        for ob in bpy.data.objects:
            if pat in ob.name and not ob.hide_render: ob.hide_render=True; hid.append(ob)
    sc.render.filepath=os.path.join(OUT,f); bpy.ops.render.render(write_still=True)
    for ob in hid: ob.hide_render=False
    print("WROTE",f)
CX,CY = ROOM_W/2, ROOM_D/2
# T1: keep the floor so the plan reads
shoot(cam("o1",(CX,CY,420),(CX,CY,0),176), "T1_plan.png", 1700,1700, ("Wall_","Ceiling"))
# T4 replacement: playhouse framing only, from inside the room
shoot(cam("o4b",(PH_X0-260,PH_Y0-260,200),(PH_X0+24,PH_Y0+24,44),112),
      "T5_playhouse_frame.png", 1500,1400,
      ("Wall_","Ceiling","Floor","PH skin","Roof plane","gable","slab","arch","hinge","knob","window","ring","LoftDeck","Skin","Net ","Bridge","Post wrap","Loft","Ladder","Rung","Shelf","Stringer","Porthole","Hobbit"))
print("FIX DONE")
