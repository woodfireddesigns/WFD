"""Export iPhone-viewable formats from the master .blend.
USDZ  -> opens natively in Files / Messages / Safari via AR Quick Look (real-world scale AR)
GLB   -> for Android and web viewers
"""
import bpy, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(HERE, "exports")
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "playroom_build.blend"))

# Drop the room shell so the structures read on their own on a phone screen,
# and so AR Quick Look places the build in your ACTUAL room instead of a fake one.
for ob in list(bpy.data.objects):
    if any(p in ob.name for p in ("Wall_", "Ceiling", "Floor")):
        bpy.data.objects.remove(ob, do_unlink=True)

bpy.ops.object.select_all(action='SELECT')
print("objects:", len([o for o in bpy.data.objects if o.type in ('MESH','CURVE')]))

usdz = os.path.join(OUT, "playroom_build.usdz")
try:
    bpy.ops.wm.usd_export(filepath=usdz, export_materials=True,
                          export_textures=False, evaluation_mode='RENDER')
    print("USDZ OK", os.path.getsize(usdz))
except Exception as e:
    print("USDZ FAIL:", e)

glb = os.path.join(OUT, "playroom_build_mobile.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', export_apply=True)
print("GLB OK", os.path.getsize(glb))
