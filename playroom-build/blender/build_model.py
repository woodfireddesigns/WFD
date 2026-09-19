"""Builds the full Blender scene from geometry.MEMBERS. Run: python3 blender/build_model.py"""
import sys, os, math, bpy, bmesh
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *
import geometry as G

IN = 0.0254  # inches -> metres

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'IMPERIAL'
    sc.unit_settings.length_unit = 'INCHES'

def mat(name, rgb, rough=0.72, spec=0.25):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    try: b.inputs["Specular IOR Level"].default_value = spec
    except KeyError: pass
    return m

def box(name, cen, sx, sy, sz, basis=None, material=None, coll=None):
    me = bpy.data.meshes.new(name); ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    S = Matrix.Diagonal((sx*IN, sy*IN, sz*IN, 1.0))
    R = basis or Matrix.Identity(4)
    ob.matrix_world = Matrix.Translation(Vector(cen)*IN) @ R @ S
    if material: ob.data.materials.append(material)
    return ob

def basis_from(ax, side, up):
    m = Matrix.Identity(4)
    for i, v in enumerate((ax, side, up)):
        m[0][i], m[1][i], m[2][i] = v
    return m

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def build():
    reset()
    MATS = {k: mat(k, v) for k, v in PALETTE.items()}
    MATS["glass"] = mat("acrylic", (0.72, 0.84, 0.86), 0.08, 0.6)

    root = coll("PLAYROOM")
    cgrp = {}

    # ---- room shell -------------------------------------------------
    rc = coll("00_Room", root)
    box("Floor", (ROOM_W/2, ROOM_D/2, -1.5), ROOM_W+8, ROOM_D+8, 3, material=MATS["floor"], coll=rc)
    box("Wall_N", (ROOM_W/2, ROOM_D+2.5, CEILING/2), ROOM_W+8, 5, CEILING, material=MATS["wall"], coll=rc)
    box("Wall_W", (-2.5, ROOM_D/2, CEILING/2), 5, ROOM_D+8, CEILING, material=MATS["wall"], coll=rc)
    box("Wall_E", (ROOM_W+2.5, ROOM_D/2, CEILING/2), 5, ROOM_D+8, CEILING, material=MATS["wall"], coll=rc)
    for x0, x1 in ((0, ROOM_DOOR_X), (ROOM_DOOR_X+ROOM_DOOR_W, ROOM_W)):
        box(f"Wall_S_{x0:.0f}", ((x0+x1)/2, -2.5, CEILING/2), x1-x0, 5, CEILING, material=MATS["wall"], coll=rc)
    box("Ceiling", (ROOM_W/2, ROOM_D/2, CEILING+1.5), ROOM_W+8, ROOM_D+8, 3, material=MATS["wall"], coll=rc)

    # ---- framing members --------------------------------------------
    for i, m in enumerate(G.MEMBERS):
        g = m["group"]
        if g not in cgrp:
            cgrp[g] = coll(f"{len(cgrp)+1:02d}_{g.replace(' / ','_').replace(' ','')}", root)
        ax, side, up = m["axis"], m["side"], m["up"]
        if m.get("zrot"):
            a = math.radians(m["zrot"]); ca, sa = math.cos(a), math.sin(a)
            side = (side[0]*ca - side[1]*sa, side[0]*sa + side[1]*ca, side[2])
            up   = (up[0]*ca - up[1]*sa,     up[0]*sa + up[1]*ca,     up[2])
        cen = tuple((a+b)/2 for a, b in zip(m["p0"], m["p1"]))
        ob = box(f"{m['label']}", cen, m["L"], m["w"], m["h"],
                 basis_from(ax, side, up), MATS.get(m["mat"], MATS["oak"]), cgrp[g])
        ob["stock"] = m["stock"]; ob["cut_length_in"] = round(m["L"], 3)
        ob["end_cuts"] = str(m["ends"]); ob["note"] = m["note"]

    # ---- loft deck (hexagon, 3/4 ply) -------------------------------
    dc = coll("20_Decking", root)
    me = bpy.data.meshes.new("LoftDeck"); ob = bpy.data.objects.new("LoftDeck", me); dc.objects.link(ob)
    bm = bmesh.new()
    vs = [bm.verts.new((x*IN, y*IN, (DECK_TOP-PLY)*IN)) for x, y in (G.RM[n] for n in G.ORDER)]
    bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=PLY*IN)
    bm.to_mesh(me); bm.free()
    ob.data.materials.append(MATS["honey"])
    ob["stock"] = '3/4" plywood'; ob["note"] = f"{21.75:.2f} sq ft - cut from 1 sheet"

    # ---- knee-wall skin, hobbit door, porthole ----------------------
    sk = coll("21_Skin", root)
    for a, b in [("B","C"), ("C","D"), ("D","Cp"), ("Cp","Bp")]:
        (x0,y0),(x1,y1),L,d = G.edge(a,b); n = G.inward(a,b)
        cx, cy = (x0+x1)/2 - n[0]*0.4, (y0+y1)/2 - n[1]*0.4
        ang = math.atan2(d[1], d[0])
        R = Matrix.Rotation(ang, 4, 'Z')
        ob = box(f"Skin {a}-{b}", (cx, cy, KNEE_TOTAL/2), L, 0.75, KNEE_TOTAL, R, MATS["moss"], sk)
        ob["stock"] = '3/4" ext ply / T1-11'
        # guard skirt above deck on the netless faces is handled by rope
    # hobbit door slab
    mid, d, n = G.HDOOR_MID, G.HDOOR_DIR, G.HDOOR_NRM
    ang = math.atan2(d[1], d[0]); R = Matrix.Rotation(ang, 4, 'Z')
    dz = HDOOR_SLAB_H - HDOOR_ARCH_R
    dx, dy = mid[0]-n[0]*1.2, mid[1]-n[1]*1.2
    door = coll("22_Doors", root)
    box("Hobbit door slab (loft)", (dx, dy, T_2X + dz/2), HDOOR_SLAB_W, 1.25, dz, R, MATS["moss"], door)
    me = bpy.data.meshes.new("LoftDoorArch"); ah = bpy.data.objects.new("Hobbit door arch (loft)", me); door.objects.link(ah)
    bm = bmesh.new()
    prof = [(0,0)] + [(HDOOR_ARCH_R*math.cos(math.pi*t/24), HDOOR_ARCH_R*math.sin(math.pi*t/24)) for t in range(25)]
    vs = [bm.verts.new((p[0]*IN, 0, p[1]*IN)) for p in prof]
    bm.faces.new(vs); bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=1.25*IN)
    bm.to_mesh(me); bm.free(); me.materials.append(MATS["moss"])
    ah.matrix_world = Matrix.Translation(Vector((dx, dy, T_2X+dz))*IN) @ R
    # strap hinges + knob
    for s in (-1, 1):
        box(f"Strap hinge {'T' if s>0 else 'B'} (loft)",
            (dx-n[0]*0.9, dy-n[1]*0.9, T_2X + dz/2 + s*dz*0.32),
            HDOOR_SLAB_W*0.8, 0.35, 1.75, R, MATS["iron"], door)
    kx = dx + d[0]*(HDOOR_SLAB_W/2-3.0); ky = dy + d[1]*(HDOOR_SLAB_W/2-3.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.4*IN, location=Vector((kx-n[0]*2.0, ky-n[1]*2.0, T_2X+dz*0.55))*IN)
    kn = bpy.context.object; kn.name = "Door knob (loft)"; kn.data.materials.append(MATS["walnut"])
    for c in kn.users_collection: c.objects.unlink(kn)
    door.objects.link(kn)
    # porthole
    a, b = PORTHOLE_FACE
    (x0,y0),(x1,y1),L,dd = G.edge(a,b); nn = G.inward(a,b)
    px, py = (x0+x1)/2 - nn[0]*0.9, (y0+y1)/2 - nn[1]*0.9
    bpy.ops.mesh.primitive_cylinder_add(radius=PORTHOLE_D/2*IN, depth=1.0*IN,
        location=Vector((px, py, PORTHOLE_Z))*IN, rotation=(math.pi/2, 0, math.atan2(dd[1], dd[0])))
    ph = bpy.context.object; ph.name = f'Porthole {PORTHOLE_D:.0f}" acrylic'
    ph.data.materials.append(MATS["glass"])
    for c in ph.users_collection: c.objects.unlink(c and ph)
    door.objects.link(ph)

    # ---- playhouse skin, roof deck, door, window --------------------
    ps = coll("30_PlayhouseSkin", root)
    box("PH skin W (lower)", (PH_X0+0.4, (PH_Y0+ROOM_D)/2, PH_WALL_H/2), 0.75, PH_SIZE, PH_WALL_H,
        None, MATS["oak"], ps)["stock"] = '3/4" ply'
    for x0, x1 in ((PH_X0, PH_X0+PH_SIZE/2-PH_DOOR_RO_W/2-W_2X4),
                   (PH_X0+PH_SIZE/2+PH_DOOR_RO_W/2+W_2X4, ROOM_W)):
        box(f"PH skin S {x0:.0f}", ((x0+x1)/2, PH_Y0+0.4, PH_WALL_H/2), x1-x0, 0.75, PH_WALL_H,
            None, MATS["oak"], ps)
    box("PH skin S (over door)", (PH_X0+PH_SIZE/2, PH_Y0+0.4, (PH_DOOR_RO_H+W_2X6+PH_WALL_H)/2),
        PH_DOOR_RO_W+W_2X4*2, 0.75, PH_WALL_H-PH_DOOR_RO_H-W_2X6, None, MATS["oak"], ps)
    # gable + roof planes
    rise = (PH_RIDGE-2.75) - (PH_WALL_H+T_2X)
    for s in (-1, 1):
        slope = math.atan2(rise, PH_SIZE/2)
        cxr = PH_X0 + PH_SIZE/2 + s*PH_SIZE/4
        czr = (PH_RIDGE-2.75 + PH_WALL_H+T_2X)/2
        Rr = Matrix.Rotation(-s*slope, 4, 'Y')
        box(f"Roof plane {'E' if s>0 else 'W'}", (cxr, (PH_Y0+ROOM_D)/2 - 1, czr),
            math.hypot(PH_SIZE/2, rise)+2, PH_SIZE+4, 0.75, Rr, MATS["walnut"], ps)
    me = bpy.data.meshes.new("PHGable"); gb = bpy.data.objects.new("PH gable (south)", me); ps.objects.link(gb)
    bm = bmesh.new()
    for p in [(PH_X0, PH_WALL_H), (ROOM_W, PH_WALL_H), (PH_X0+PH_SIZE/2, PH_RIDGE-2.75)]:
        bm.verts.new((p[0]*IN, PH_Y0*IN, p[1]*IN))
    bm.faces.new(bm.verts); bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.75*IN)
    bm.to_mesh(me); bm.free(); me.materials.append(MATS["oak"])
    # playhouse door
    pdz = PH_DOOR_SLAB_H - PH_DOOR_RO_W/2
    pdx = PH_X0 + PH_SIZE/2
    box("Hobbit door slab (playhouse)", (pdx, PH_Y0-0.8, pdz/2), PH_DOOR_SLAB_W, 1.25, pdz, None, MATS["moss"], door)
    me = bpy.data.meshes.new("PHArch"); pa = bpy.data.objects.new("Hobbit door arch (playhouse)", me); door.objects.link(pa)
    bm = bmesh.new(); r = PH_DOOR_SLAB_W/2
    prof = [(0,0)] + [(r*math.cos(math.pi*t/24), r*math.sin(math.pi*t/24)) for t in range(25)]
    vs = [bm.verts.new((p[0]*IN, 0, p[1]*IN)) for p in prof]
    bm.faces.new(vs); bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=1.25*IN)
    bm.to_mesh(me); bm.free(); me.materials.append(MATS["moss"])
    pa.matrix_world = Matrix.Translation(Vector((pdx, PH_Y0-0.8, pdz))*IN)
    for s in (-1, 1):
        box(f"PH strap hinge {'T' if s>0 else 'B'}", (pdx, PH_Y0-1.5, pdz/2 + s*pdz*0.33),
            PH_DOOR_SLAB_W*0.8, 0.35, 1.75, None, MATS["iron"], door)
    bpy.ops.mesh.primitive_cylinder_add(radius=PH_WINDOW_D/2*IN, depth=1.2*IN,
        location=Vector((pdx, PH_Y0+0.4, PH_WINDOW_Z))*IN, rotation=(math.pi/2, 0, 0))
    w = bpy.context.object; w.name = 'PH round window 12" acrylic'; w.data.materials.append(MATS["glass"])
    for c in w.users_collection: c.objects.unlink(w)
    ps.objects.link(w)
    bpy.ops.mesh.primitive_torus_add(major_radius=(PH_WINDOW_D/2+1.0)*IN, minor_radius=0.7*IN,
        location=Vector((pdx, PH_Y0+0.2, PH_WINDOW_Z))*IN, rotation=(math.pi/2, 0, 0))
    t = bpy.context.object; t.name = "PH window iron ring"; t.data.materials.append(MATS["iron"])
    for c in t.users_collection: c.objects.unlink(t)
    ps.objects.link(t)
    return root, MATS

def add_ropes(root, MATS):
    rc = coll("40_Rope", root)
    def rope(name, pts, r=NET_ROPE_D*0.95, m="rope"):
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
        cu.bevel_depth = r*IN; cu.bevel_resolution = 3; cu.resolution_u = 6
        sp = cu.splines.new('POLY'); sp.points.add(len(pts)-1)
        for i, p in enumerate(pts): sp.points[i].co = (p[0]*IN, p[1]*IN, p[2]*IN, 1)
        ob = bpy.data.objects.new(name, cu); rc.objects.link(ob); cu.materials.append(MATS[m])
        return ob
    def catenary(p0, p1, sag, n=20):
        return [tuple(a+(b-a)*i/n for a, b in zip(p0, p1)[:0]) for i in []] or [
            (p0[0]+(p1[0]-p0[0])*i/n, p0[1]+(p1[1]-p0[1])*i/n,
             p0[2]+(p1[2]-p0[2])*i/n - sag*math.sin(math.pi*i/n)) for i in range(n+1)]

    # --- loft rope-net guard on the D-Cp face ---
    a, b = FACE_NET
    (x0,y0),(x1,y1),L,d = G.edge(a,b); nn = G.inward(a,b)
    ins = POST/2 + 0.5
    ax, ay = x0+d[0]*ins, y0+d[1]*ins
    clear = L - 2*ins
    for k in range(4):
        z = DECK_TOP + 2 + k*(GUARD_H-4)/3
        rope(f"Net rail {k+1}", catenary((ax, ay, z), (ax+d[0]*clear, ay+d[1]*clear, z), 0.5*(k<3)), 0.42)
    nv = 7
    for k in range(nv+1):
        t = k/nv
        px, py = ax+d[0]*clear*t, ay+d[1]*clear*t
        rope(f"Net vert {k+1}", [(px, py, DECK_TOP+2), (px, py, DECK_TOP+GUARD_H-2)], NET_ROPE_D*0.8)
    # --- rope across the ladder gate (Cp-Bp) and bridge gate (B-C) ---
    for (a, b), nm in ((FACE_LADDER, "Ladder gate"), (FACE_BRIDGE, "Bridge gate")):
        (x0,y0),(x1,y1),L,d = G.edge(a,b)
        ax, ay = x0+d[0]*ins, y0+d[1]*ins; clear = L-2*ins
        for z in (DECK_TOP+18, DECK_TOP+GUARD_H-2):
            rope(f"{nm} rope z{z:.0f}", catenary((ax,ay,z), (ax+d[0]*clear, ay+d[1]*clear, z), 0.4))
    # --- ladder rope handrails ---
    lb, lt, ld, lo = G.LADDER_BOT, G.LADDER_TOP, G.LADDER_DIR, G.LADDER_OUT
    for s in (-1, 1):
        ox, oy = ld[0]*s*(LADDER_W/2+1.0), ld[1]*s*(LADDER_W/2+1.0)
        rope(f"Ladder handrail {'L' if s<0 else 'R'}",
             catenary((lb[0]+ox, lb[1]+oy, 30), (lt[0]+ox, lt[1]+oy, DECK_TOP+GUARD_H-4), 1.5), 0.46)
    # --- BRIDGE: cargo net deck + side net panels + top ropes ---
    y0b, y1b, yc = G.BR_Y0, G.BR_Y1, G.BR_YC
    x0b, x1b = BRIDGE_X0, BRIDGE_X1
    for y in (y0b, y1b):
        rope(f"Bridge deck edge y{y:.0f}", catenary((x0b, y, DECK_TOP), (x1b, y, DECK_TOP), BRIDGE_SAG), 0.42)
        rope(f"Bridge top rope y{y:.0f}", catenary((x0b, y, BRIDGE_TOP_Z), (x1b, y, BRIDGE_TOP_Z), 1.2), 0.42)
        rope(f"Bridge mid rope y{y:.0f}", catenary((x0b, y, DECK_TOP+18), (x1b, y, DECK_TOP+18), BRIDGE_SAG*0.7), 0.36)
    nx = 10
    for k in range(nx+1):
        t = k/nx; x = x0b + (x1b-x0b)*t
        sg = BRIDGE_SAG*math.sin(math.pi*t)
        rope(f"Bridge slat {k+1}", [(x, y0b, DECK_TOP-sg), (x, y1b, DECK_TOP-sg)], 0.42)
        sg2 = 1.2*math.sin(math.pi*t)
        for y in (y0b, y1b):
            rope(f"Bridge side {k+1}", [(x, y, DECK_TOP-sg), (x, y, BRIDGE_TOP_Z-sg2)], 0.34)
    for k in range(5):
        t = (k+0.5)/5; x = x0b+(x1b-x0b)*t
        pass
    # rope wrap on the playhouse SW corner post
    sx, sy = G.PH_POSTS["SW"]
    for k in range(26):
        z = 6 + k*2.6
        rope(f"Post wrap {k}", [(sx-2.6, sy, z), (sx, sy-2.6, z+0.6), (sx+2.6, sy, z+1.2),
                                (sx, sy+2.6, z+1.8), (sx-2.6, sy, z+2.4)], 0.40)

def main():
    root, MATS = build()
    add_ropes(root, MATS)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "playroom_build.blend"))
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "playroom_build.glb"), export_format='GLB')
    n = len([o for o in bpy.data.objects if o.type in ('MESH','CURVE')])
    print(f"SCENE OK: {n} objects")
main()
