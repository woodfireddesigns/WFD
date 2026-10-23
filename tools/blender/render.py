import bpy, sys, math, mathutils, json, os
def smoothstep_(x, a, b):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
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
    HAIR = []; SKIN_HEAD = []
    # sculpted head: skin regions of the face and skull from the body-surface model
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=args['skin'])
    NO = ['carotid', 'muscular triangle', 'supraclavicular', 'eyelash', 'cilia', 'cross section', 'eyebrow hair', 'hairs of eyebrow', 'pubic', 'axilla']
    if not (args.get('hair') or args.get('buzz')): NO.append('hair')
    if not args.get('neck'): NO += ['neck', 'sternocleidomastoid']
    zmin_keep = args.get('skin_zmin', 1.475)
    for o in [o for o in bpy.context.scene.objects if o not in before]:
        if o.type != 'MESH': continue
        n = o.name.lower(); ws = [o.matrix_world @ mathutils.Vector(v) for v in o.bound_box]
        is_neck = any(x in n for x in ['neck', 'sternocleidomastoid'])
        if n.endswith('.j') or n.endswith('.i') or any(x in n for x in NO) or (min(w.z for w in ws) < zmin_keep and not is_neck):
            o.hide_render = True; continue
        keep.append(o)
        SKIN_HEAD.append(o)
        if n.startswith('hairs of head'): HAIR.append(o)
        if n.startswith('orbital region'):
            # sculpted eyeball behind each eye opening
            cx = sum(w.x for w in ws) / 8; fy = min(w.y for w in ws); r = 0.0125
            bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=r, location=(cx * 0.93, fy + r * args.get('eye_back', 2.2), args.get('eye_z', 1.5915)))
            bpy.ops.object.shade_smooth(); keep.append(bpy.context.active_object); SKIN_HEAD.append(bpy.context.active_object)
print('KEEP', len(keep), 'of', len(meshes))
# clay material
mat = bpy.data.materials.new('clay'); mat.use_nodes = True
b = mat.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = tuple(args.get('clay', [0.11, 0.105, 0.10])) + (1,)
b.inputs['Roughness'].default_value = 0.55
if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.35
if args.get('scanhead') and args.get('head_z'):
    # realistic male head scan (Lee Perry-Smith, Infinite Realities, CC BY 3.0) replaces the atlas head
    import bmesh
    before = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=args['scanhead'])
    scan = [o for o in sc.objects if o not in before and o.type == 'MESH'][0]
    for o in [o for o in sc.objects if o not in before and o is not scan]: o.hide_render = True
    DROP = args.get('head_drop', 0.0)   # lower the head to shorten the neck
    bm = bmesh.new(); bm.from_mesh(scan.data); bmesh.ops.transform(bm, matrix=scan.matrix_world, verts=bm.verts)
    top = max(v.co.z for v in bm.verts)
    chin = min(v.co.z for v in bm.verts if abs(v.co.x) < 0.4 and v.co.y < -1.0)
    nose_y = min(v.co.y for v in bm.verts)
    H = args.get('scan_top', 1.712) - args.get('scan_chin', 1.488)
    k = H / (top - chin)
    for v in bm.verts:
        c = v.co
        v.co = mathutils.Vector((c.x * k, args.get('scan_nose_y', -0.118) + (c.y - nose_y) * k, args.get('scan_top', 1.712) - (top - c.z) * k - DROP))
    # weld the scan's split seams first, then add resolution so the neck edge can be shaped smoothly
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=args.get('scan_weld', 0.0004))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=args.get('scan_cuts', 2), use_grid_fill=True, smooth=0.5)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    band = [v.co for v in bm.verts if 1.445 < v.co.z < 1.465 and abs(v.co.x) < 0.05]
    ncy = (min(c.y for c in band) + max(c.y for c in band)) / 2 if band else 0.0
    print('NECK centre y', round(ncy, 4), 'depth', round(max(c.y for c in band) - min(c.y for c in band), 4) if band else None)
    rx0, ry0 = args.get('neck_rx', 0.062), args.get('neck_ry', 0.07)
    flare = args.get('neck_flare', 0.35)
    def radii(z):   # neck widens toward its base so the edge tucks under collarbones and traps
        f = 1 + flare * max(0.0, min(1.0, (1.47 - z) / 0.08)); return rx0 * f, ry0 * f
    def outside_neck(c):
        if c.z >= args.get('neck_top', 1.535): return False
        rx, ry = radii(c.z)
        if c.z > args.get('jaw_keep_z', 1.478) and abs(c.x) < rx0 * args.get('jaw_keep_x', 1.2) and c.y < ncy - 0.01: return False   # jaw and under-chin
        if c.y > ncy: ry *= args.get('neck_back_k', 1.15)
        # back of the neck ends where the trimmed traps start, so they tuck underneath
        if c.y > ncy + args.get('back_dy', 0.01) and c.z < args.get('back_cut', 1.465): return True
        return ((c.x / rx) ** 2 + ((c.y - ncy) / ry) ** 2) > 1
    if args.get('neck_squeeze', True):
        # squeeze (don't cut) the neck into the column so it stays a closed tube; only the bottom is cut
        top = args.get('neck_top', 1.535) - DROP
        for v in bm.verts:
            c = v.co
            if c.z >= top: continue
            rx, ry = radii(c.z)
            if c.y > ncy: ry *= args.get('neck_back_k', 1.15)
            e = math.sqrt((c.x / rx) ** 2 + ((c.y - ncy) / ry) ** 2)
            if e <= 1: continue
            w = smoothstep_(c.z, top, top - 0.035)
            if c.z > 1.478 - DROP and c.y < ncy - 0.01 and abs(c.x) < rx0: w *= 0.0          # leave the jaw alone
            cen = mathutils.Vector((0, ncy, c.z))
            v.co = c.lerp(cen + (c - cen) / e, w)
        dead = [v for v in bm.verts if v.co.z < args.get('scan_cut', 1.40) or
                (v.co.y > ncy + args.get('back_dy', 0.01) and v.co.z < args.get('back_cut', 1.465))]
        bmesh.ops.delete(bm, geom=dead, context='VERTS')
    else:
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < args.get('scan_cut', 1.40) or outside_neck(v.co)], context='VERTS')
    # tidy the cut: drop stray islands, then relax the open edge so it's a smooth line, not a zigzag
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(e.is_boundary for e in f.edges)], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    for _ in range(args.get('neck_relax', 12)):
        edge = [v for v in bm.verts if v.is_boundary]
        new = {}
        for v in edge:
            ns = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if ns: new[v] = v.co.lerp(sum((n.co for n in ns), mathutils.Vector()) / len(ns), 0.5)
        for v, c in new.items(): v.co = c
    for f in bm.faces: f.smooth = True
    head = bpy.data.objects.new('scan_head', bpy.data.meshes.new('scan_head')); sc.collection.objects.link(head)
    bm.to_mesh(head.data); bm.free()
    sol = head.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = args.get('scan_thick', 0.004); sol.offset = -1
    # muscles that would stick up out of the neck column end cleanly underneath it
    tz = args.get('trim_z', 1.475); tx = args.get('trim_x', 0.09)
    TRAPS = [o for o in keep if o.type == 'MESH' and o.name in MUSCLE_NAMES and group_of(o.name) in ('traps', 'upperback') and 'trapezius' in o.name.lower()]
    for o in [o for o in keep if o.type == 'MESH' and (o.name in MUSCLE_NAMES or o in SKEL) and (args.get('trim_traps', True) or o not in TRAPS)]:
        mw = o.matrix_world
        if max((mw @ mathutils.Vector(c)).z for c in o.bound_box) < tz: continue
        tb = bmesh.new(); tb.from_mesh(o.data)
        dead = [v for v in tb.verts if (lambda w: w.z > tz and abs(w.x) < tx)(mw @ v.co)]
        if dead:
            if o.data.users > 1: o.data = o.data.copy()
            bmesh.ops.delete(tb, geom=dead, context='VERTS'); tb.to_mesh(o.data)
        tb.free()
    if args.get('flush', True):
        from mathutils.bvhtree import BVHTree
        tv, tp = [], []
        for o in [o for o in keep if o.type == 'MESH' and o.name in MUSCLE_NAMES and 'trapezius' in o.name.lower()]:
            off = len(tv); tv += [o.matrix_world @ v.co for v in o.data.vertices]
            tp += [[off + i for i in p.vertices] for p in o.data.polygons]
        if tv:
            tt = BVHTree.FromPolygons(tv, tp)
            lo_z = args.get('back_cut', 1.465); band = args.get('flush_band', 0.035)
            for v in head.data.vertices:
                c = v.co
                if c.y <= ncy or c.z > lo_z + band: continue
                hit = tt.find_nearest(c)
                if hit[0] is None or hit[3] > args.get('flush_reach', 0.08): continue
                w = 1 - max(0.0, min(1.0, (c.z - lo_z) / band)); w = w * w * (3 - 2 * w)
                target = hit[0] + (c - hit[0]).normalized() * 0.0012 if (c - hit[0]).length > 1e-6 else hit[0]
                v.co = c.lerp(target, w)
    scan.hide_render = True
    for o in SKIN_HEAD: o.hide_render = True
    core.hide_render = True
    keep = [o for o in keep if o not in SKIN_HEAD and o is not core]
    # atlas pieces that sit up inside/behind the scanned head would poke through it
    hz = args.get('scan_hide_z', 1.50)
    for o in list(keep):
        ws = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
        cz = sum(w.z for w in ws) / 8; cx = sum(w.x for w in ws) / 8
        ungrouped_neck = o.name in MUSCLE_NAMES and group_of(o.name) is None and cz > 1.40 and abs(cx) < 0.09
        if cz > hz or ungrouped_neck: o.hide_render = True; keep.remove(o)
    keep.append(head)
    print('SCANHEAD scale', round(k, 4), 'chin', round(chin, 3), 'top', round(top, 3))
if args.get('mannequin') and args.get('head_z'):
    # blank mannequin head: smooth shell shrink-wrapped to the skull/jaw, features smoothed away
    import bmesh
    EAR = ['auric', 'helix', 'lobule', 'tragus', 'concha', 'scapha', 'fossa', 'incisure', 'eminentia', 'crus', 'hair', 'eyebrow']
    src = [o for o in SKIN_HEAD if o.type == 'MESH' and not any(k in o.name.lower() for k in EAR) and not o.name.lower().startswith('sphere')]
    bm = bmesh.new()
    for o in src:
        t = bmesh.new(); t.from_mesh(o.data); bmesh.ops.transform(t, matrix=o.matrix_world, verts=t.verts)
        tmp = bpy.data.meshes.new('tmp'); t.to_mesh(tmp); t.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    tgt = bpy.data.objects.new('head_target', bpy.data.meshes.new('head_target')); sc.collection.objects.link(tgt)
    bm.to_mesh(tgt.data); bm.free(); tgt.hide_render = True
    ws = [v.co for v in tgt.data.vertices]
    hlo = mathutils.Vector((min(w.x for w in ws), min(w.y for w in ws), min(w.z for w in ws)))
    hhi = mathutils.Vector((max(w.x for w in ws), max(w.y for w in ws), max(w.z for w in ws)))
    hc = (hlo + hhi) / 2
    from mathutils.bvhtree import BVHTree
    tree = BVHTree.FromObject(tgt, bpy.context.evaluated_depsgraph_get())
    # radial projection of a dense sphere onto the outermost skin; rays that slip through eye
    # openings are filled from their neighbours, then the face is smoothed blank
    rings, segs = args.get('mq_rings', 140), args.get('mq_segs', 180)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    hc2 = mathutils.Vector((0, hc.y + 0.008, hc.z + 0.01))
    miss = set(); radii = []
    for v in bm.verts:
        d = v.co.normalized()
        hit = tree.ray_cast(hc2 + d * 0.4, -d, 0.4)[0]
        if hit is None or (hit - hc2).length < 0.05: miss.add(v); v.co = hc2 + d * 0.09
        else: v.co = hit; radii.append((hit - hc2).length)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < args.get('mq_cut', 1.49)], context='VERTS')
    miss = {v for v in miss if v.is_valid}
    cy0 = hc.y
    def wface(co):
        f = smoothstep_(co.y, cy0 - 0.03, cy0 - 0.08) * (1 - smoothstep_(co.z, 1.645, 1.675)) * smoothstep_(co.z, 1.485, 1.505)
        return 0.05 + 0.8 * f
    nbr = {v: [e.other_vert(v) for e in v.link_edges] for v in bm.verts}
    wts = {v: (1.0 if v in miss else wface(v.co)) for v in bm.verts}
    for it in range(args.get('mq_iter', 120)):
        new = {}
        for v, ns in nbr.items():
            if not ns or v.is_boundary: continue
            avg = sum((n.co for n in ns), mathutils.Vector()) / len(ns)
            new[v] = v.co.lerp(avg, wts[v])
        for v, c in new.items(): v.co = c
    head = bpy.data.objects.new('mannequin_head', bpy.data.meshes.new('mannequin_head')); sc.collection.objects.link(head)
    bm.to_mesh(head.data); bm.free()
    for p in head.data.polygons: p.use_smooth = True
    bpy.context.view_layer.objects.active = head; head.select_set(True)
    for o in SKIN_HEAD: o.hide_render = True
    core.hide_render = True
    keep = [o for o in keep if o not in SKIN_HEAD and o is not core]
    keep.append(head)
    print('MANNEQUIN from', len(src), 'pieces')
BUZZ = []
if args.get('buzz') and args.get('head_z'):
    scalp_keys = ['frontal region', 'parietal region', 'occipital region', 'temporal region', 'mastoid region', 'auricular region']
    parts = [o for o in keep if any(o.name.lower().startswith(k) for k in scalp_keys)]
    import bmesh
    bm = bmesh.new()
    for o in parts:   # merge scalp pieces in world space (FBX pieces are positioned via parents)
        t = bmesh.new(); t.from_mesh(o.data); bmesh.ops.transform(t, matrix=o.matrix_world, verts=t.verts)
        tmp = bpy.data.meshes.new('tmp'); t.to_mesh(tmp); t.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    cap = bpy.data.objects.new('buzz_cap', bpy.data.meshes.new('buzz_cap')); sc.collection.objects.link(cap)
    bm.to_mesh(cap.data); bm.free()
    # footprint of the original hair, so the buzz cut keeps a natural hairline
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for h in HAIR:
        e = h.evaluated_get(dg); me = e.to_mesh(); off = len(verts)
        verts += [h.matrix_world @ v.co for v in me.vertices]
        polys += [[off + i for i in p.vertices] for p in me.polygons]
        e.to_mesh_clear(); h.hide_render = True
    tree = BVHTree.FromPolygons(verts, polys)
    bm = bmesh.new(); bm.from_mesh(cap.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=args.get('buzz_merge', 0.0025))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=args.get('buzz_cuts', 2), use_grid_fill=True, smooth=0.6)
    bm.normal_update()
    reach = args.get('buzz_reach', 0.06); front_z = args.get('hairline_z', 1.68)
    cy = sum(v.co.y for v in bm.verts) / max(1, len(bm.verts))
    hc = mathutils.Vector((0, cy, (lo.z + hi.z) / 2 + 0.03))   # rough head centre
    def covered(v):
        if v.co.y < cy - 0.02 and v.co.z < front_z: return False          # forehead stays clear
        if abs(v.co.x) < 0.012 and v.co.z > front_z - 0.01: return True    # hair parting gaps on the midline
        out = (v.co - hc).normalized()
        hit = tree.ray_cast(v.co + out * 0.0005, out, reach)[0]
        if hit is None: return False
        return not (v.co.y < cy - 0.02 and v.co.z < front_z)   # keep the forehead clear
    gone = [v for v in bm.verts if not covered(v)]
    print('BUZZ verts', len(bm.verts), 'trimmed', len(gone))
    bmesh.ops.delete(bm, geom=gone, context='VERTS')
    bm.normal_update()
    # soften the hairline: relax boundary vertices a few times
    for _ in range(args.get('buzz_relax', 6)):
        edge = [v for v in bm.verts if v.is_boundary]
        new = {v: sum((e.other_vert(v).co for e in v.link_edges if e.is_boundary), mathutils.Vector()) / max(1, sum(1 for e in v.link_edges if e.is_boundary)) for v in edge}
        for v, c in new.items(): v.co = v.co.lerp(c, 0.5)
    lift = args.get('buzz_offset', 0.0025)
    for v in bm.verts: v.co += (v.co - hc).normalized() * lift
    bm.to_mesh(cap.data); bm.free()
    for p in cap.data.polygons: p.use_smooth = True
    keep = [o for o in keep if o not in HAIR]
    keep.append(cap); BUZZ.append(cap)
    # skin fully under the hair takes the stubble colour too, so seams in the cap never show skin
    BUZZ += [o for o in parts if o.name.lower().startswith(('parietal region', 'occipital region'))]
# masculine sculpt: thicker neck, wider square jaw, stronger chin and brow, lower dome
def smooth(z, a, b):   # 0 at a, 1 at b (smoothstep); works for a > b too
    t = max(0.0, min(1.0, (z - a) / (b - a))); return t * t * (3 - 2 * t)
def bump(z, lo, peak, hi):
    return smooth(z, lo, peak) if z <= peak else 1 - smooth(z, peak, hi)
M = args.get('masc')
def warp(w):
    x, y, z = w.x, w.y, w.z
    if z < 1.38: return w
    neck = bump(z, 1.40, 1.48, 1.56) * M.get('neck', 0.22)
    jaw = bump(z, 1.465, M.get('jaw_z', 1.515), 1.59) * M.get('jaw', 0.14)
    sx = 1 + neck + jaw
    sy = 1 + neck * 0.8
    ny = y * sy
    face = smooth(y, -0.02, -0.07)                      # how far toward the face (front is -y)
    chin = bump(z, 1.47, 1.50, 1.55) * face * M.get('chin', 0.007)
    brow = bump(z, 1.605, 1.625, 1.645) * face * M.get('brow', 0.005)
    nose = bump(z, 1.545, 1.575, 1.61) * smooth(abs(x), 0.022, 0.0) * face * M.get('nose', 0.0)
    cheek = bump(z, 1.54, 1.575, 1.61) * smooth(abs(x), 0.02, 0.05) * face * M.get('cheekbone', 0.0)
    ny -= chin + brow + nose + cheek
    nz = z
    if z > 1.63: nz = 1.63 + (z - 1.63) * M.get('dome', 0.9)
    if z > 1.60 and y > 0: ny = y * sy * (1 - smooth(z, 1.60, 1.70) * M.get('back', 0.0))   # less bulge at the back of the skull
    sx *= 1 + smooth(z, 1.58, 1.66) * M.get('skull_w', 0.04)
    return mathutils.Vector((x * sx, ny, nz))
if M:
    head_objs = [o for o in keep if o.type == 'MESH' and max((o.matrix_world @ mathutils.Vector(c)).z for c in o.bound_box) > 1.38]
    for o in head_objs:
        mw = o.matrix_world; inv = mw.inverted()
        me = o.data
        if me.users > 1: o.data = me = me.copy()
        for v in me.vertices: v.co = inv @ warp(mw @ v.co)
    print('MASC warped', len(head_objs))
FEM = args.get('fem')
BREASTS = []
if FEM is not None:
    def sm(x, a, b):
        t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
    def bp(z, lo, pk, hi): return sm(z, lo, pk) if z <= pk else 1 - sm(z, pk, hi)
    def fwarp(w):
        x, y, z = w.x, w.y, w.z
        ax = abs(x)
        kx = 1.0; ky = 1.0; dy = 0.0
        kx -= FEM.get('shoulders', 0.10) * bp(z, 1.10, 1.36, 1.50) * sm(ax, 0.04, 0.16)
        kx -= FEM.get('waist', 0.10) * bp(z, 0.96, 1.10, 1.26) * (1 - sm(ax, 0.17, 0.24))
        ky -= FEM.get('waist', 0.10) * 0.7 * bp(z, 0.96, 1.10, 1.26) * (1 - sm(ax, 0.17, 0.24))
        kx += FEM.get('hips', 0.11) * bp(z, 0.66, 0.89, 1.06) * (1 - sm(ax, 0.22, 0.30))
        kx += FEM.get('thighs', 0.05) * bp(z, 0.45, 0.78, 0.92) * (1 - sm(ax, 0.22, 0.30))
        if y > 0: dy += FEM.get('glutes', 0.018) * bp(z, 0.76, 0.88, 0.98) * (1 - sm(ax, 0.16, 0.22))
        ky -= FEM.get('arms', 0.10) * sm(ax, 0.20, 0.26) * bp(z, 0.70, 1.15, 1.42)
        kx -= FEM.get('neck', 0.12) * bp(z, 1.40, 1.47, 1.55)
        ky -= FEM.get('neck', 0.12) * bp(z, 1.40, 1.47, 1.55)
        k = FEM.get('scale', 0.94)
        return mathutils.Vector((x * kx * k, (y * ky + dy) * k, z * k))
    for o in [o for o in keep if o.type == 'MESH']:
        mw = o.matrix_world; inv = mw.inverted(); me = o.data
        if me.users > 1: o.data = me = me.copy()
        for v in me.vertices: v.co = inv @ fwarp(mw @ v.co)
    # chest: two soft volumes over the pectorals, part of the chest group for the recovery glow
    pecs = [o for o in keep if o.name in MUSCLE_NAMES and 'sternocostal head of pectoralis major' in o.name.lower()]
    for o in pecs:
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
        cx = sum(w.x for w in ws) / len(ws); cz = sum(w.z for w in ws) / len(ws); fy = min(w.y for w in ws)
        r = FEM.get('bust', 0.052)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=48, radius=r,
            location=(cx * 0.9, fy + r * FEM.get('bust_in', 0.62), cz - r * 0.6))
        bo = bpy.context.active_object; bo.scale = (1.05, FEM.get('bust_depth', 0.72), 0.9); bo.name = 'bust.' + o.name[-1]
        bpy.ops.object.shade_smooth(); keep.append(bo); BREASTS.append(bo)
    print('FEM warped', len(keep), 'bust', len(BREASTS))
MODE = args.get('mode', 'beauty')
def flat(name, v):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (v, v, v, 1); e.inputs['Strength'].default_value = 1
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], out.inputs[0]); return m
buzz = bpy.data.materials.new('buzz'); buzz.use_nodes = True
bn = buzz.node_tree.nodes; bb = bn['Principled BSDF']
bb.inputs['Base Color'].default_value = tuple(args.get('buzz_color', [0.022, 0.02, 0.019])) + (1,)
bb.inputs['Roughness'].default_value = 0.92
noise = bn.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 900; noise.inputs['Detail'].default_value = 2
bump = bn.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35
buzz.node_tree.links.new(noise.outputs['Fac'], bump.inputs['Height']); buzz.node_tree.links.new(bump.outputs['Normal'], bb.inputs['Normal'])
idmats = {g: flat('id_' + g, (i + 1) * 16 / 255) for i, g in enumerate(GROUPS)}
idnone = flat('id_none', 0.0)
counts = {}
for o in keep:
    o.data.materials.clear()
    if MODE == 'id':
        g = 'chest' if o in BREASTS else (group_of(o.name) if o.name in MUSCLE_NAMES else None)
        counts[g] = counts.get(g, 0) + 1
        o.data.materials.append(idmats[g] if g else idnone)
    else:
        if args.get('debug_scan') and o.name.startswith('scan_head'):
            dm = bpy.data.materials.get('dbg') or bpy.data.materials.new('dbg'); dm.use_nodes = True
            dm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.6, 0.02, 0.02, 1)
            o.data.materials.append(dm)
        else:
            o.data.materials.append(buzz if o in BUZZ else mat)
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
