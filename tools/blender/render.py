import bpy, sys, math, mathutils, json, os
sys.path.insert(0, os.path.dirname(__file__))
from groups import group_of, GROUPS
args = json.loads(sys.argv[-1])
FBX = args['fbx']; OUT = args['out']; RES = args.get('res', [400, 800]); SAMPLES = args.get('samples', 32)
EXCLUDE = ['fascia', 'bursa', 'septum', 'aponeuros', 'retinacul', 'sheath', 'ligament', 'membrane', 'capsule', 'tendinous', 'raphe', 'arch']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
MUSCLE_NAMES = {o.name for o in bpy.context.scene.objects}
SKEL = set()
if args.get('skel'):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=args['skel'])
    SKEL = {o for o in bpy.context.scene.objects if o not in before}
sc = bpy.context.scene
meshes = [o for o in sc.objects if o.type == 'MESH']
keep = []
for o in meshes:
    n = o.name.lower()
    d = sorted(o.dimensions)
    # skip connective tissue, and label leader lines (long, paper-thin meshes)
    label = n.endswith('.i') or n.endswith('.j') or 'cross section' in n or len(o.data.vertices) <= 24
    if any(x in n for x in EXCLUDE) or label or (d[0] < 0.003 and d[1] < 0.003): o.hide_render = True; continue
    keep.append(o)
# replace the anatomical head with a smooth mannequin head
HEAD_Z = args.get('head_z')
if HEAD_Z:
    head_objs = []
    for o in keep:
        ws = [o.matrix_world @ mathutils.Vector(v) for v in o.bound_box]
        cz = sum(w.z for w in ws) / 8
        if cz > HEAD_Z: head_objs.append((o, ws))
    lo = mathutils.Vector((min(w.x for _, ws in head_objs for w in ws), min(w.y for _, ws in head_objs for w in ws), min(w.z for _, ws in head_objs for w in ws)))
    hi = mathutils.Vector((max(w.x for _, ws in head_objs for w in ws), max(w.y for _, ws in head_objs for w in ws), max(w.z for _, ws in head_objs for w in ws)))
    print('HEAD', len(head_objs), tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))
    for o, _ in head_objs: o.hide_render = True
    keep = [o for o in keep if not o.hide_render]
    # solid core so eye/brow openings in the skin read as clay, not holes
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=48)
    core = bpy.context.active_object; c = (lo + hi) / 2
    core.location = (0, c.y + args.get('core_dy', 0.0), c.z + 0.02)
    core.scale = ((hi.x - lo.x) / 2 * args.get("core_s", 0.86), (hi.y - lo.y) / 2 * args.get("core_sy", 0.8), (hi.z - lo.z) / 2 * args.get("core_s", 0.86))
    keep.append(core)
    # sculpted head: skin regions of the face and skull from the body-surface model
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=args['skin'])
    NO = ['neck', 'carotid', 'sternocleidomastoid', 'muscular triangle', 'supraclavicular', 'hair', 'eyelash', 'cilia', 'cross section']
    for o in [o for o in bpy.context.scene.objects if o not in before]:
        if o.type != 'MESH': continue
        n = o.name.lower(); ws = [o.matrix_world @ mathutils.Vector(v) for v in o.bound_box]
        if n.endswith('.j') or n.endswith('.i') or any(x in n for x in NO) or min(w.z for w in ws) < 1.475:
            o.hide_render = True; continue
        keep.append(o)
        if n.startswith('orbital region'):
            # sculpted eyeball behind each eye opening
            cx = sum(w.x for w in ws) / 8; fy = min(w.y for w in ws); r = 0.0125
            bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=r, location=(cx * 0.93, fy + r * args.get('eye_back', 2.2), args.get('eye_z', 1.5915)))
            bpy.ops.object.shade_smooth(); keep.append(bpy.context.active_object)
print('KEEP', len(keep), 'of', len(meshes))
# clay material
mat = bpy.data.materials.new('clay'); mat.use_nodes = True
b = mat.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = tuple(args.get('clay', [0.11, 0.105, 0.10])) + (1,)
b.inputs['Roughness'].default_value = 0.55
if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.35
MODE = args.get('mode', 'beauty')
def flat(name, v):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (v, v, v, 1); e.inputs['Strength'].default_value = 1
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], out.inputs[0]); return m
idmats = {g: flat('id_' + g, (i + 1) * 16 / 255) for i, g in enumerate(GROUPS)}
idnone = flat('id_none', 0.0)
counts = {}
for o in keep:
    o.data.materials.clear()
    if MODE == 'id':
        g = group_of(o.name) if o.name in MUSCLE_NAMES else None
        counts[g] = counts.get(g, 0) + 1
        o.data.materials.append(idmats[g] if g else idnone)
    else:
        o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
if MODE == 'id': print('IDCOUNTS', counts)
# world: black, transparent film
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.01, 0.01, 0.012, 1)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.film_transparent = True
if args.get('mode') == 'id':
    sc.cycles.samples = 1; sc.cycles.use_denoising = False
    sc.cycles.filter_width = 0.01; sc.cycles.max_bounces = 0
    sc.render.dither_intensity = 0
    sc.render.film_transparent = False
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0, 0, 0, 1)
sc.render.resolution_x, sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Raw' if args.get('mode') == 'id' else 'AgX' if 'AgX' in [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
# camera: orthographic, figure centred
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.95
def light(name, kind, loc, energy, color, size=1.0):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, kind)); sc.collection.objects.link(l)
    l.location = loc; l.data.energy = energy; l.data.color = color
    if kind == 'AREA': l.data.size = size
    d = mathutils.Vector((0, 0, 0.95)) - mathutils.Vector(loc); l.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return l
for view in args['views']:
    s = -1 if view == 'front' else 1          # camera on -Y for front (verified by test)
    cam.location = (0, s * 6, 0.86); cam.rotation_euler = (math.radians(90), 0, 0 if s < 0 else math.pi)
    for l in [o for o in sc.objects if o.type == 'LIGHT']: bpy.data.objects.remove(l)
    k = args.get('light', 1.0)
    light('key', 'AREA', (1.6, s * 3.2, 3.2), 900 * k, (1, 0.97, 0.93), 2.5)
    light('fill', 'AREA', (-2.5, s * 2.5, 1.2), 160 * k, (0.75, 0.8, 1.0), 3)
    light('rimL', 'AREA', (-2.2, -s * 2.4, 1.8), 900 * k, (1.0, 0.6, 0.38), 1.2)
    light('rimR', 'AREA', (2.2, -s * 2.4, 1.4), 700 * k, (0.85, 0.9, 1.0), 1.2)
    if args.get('crop'):
        cam.data.ortho_scale = args['crop'][0]; cam.location.z = args['crop'][1]
    sc.render.filepath = os.path.join(OUT, f'{view}.png')
    bpy.ops.render.render(write_still=True)
    print('WROTE', sc.render.filepath)
