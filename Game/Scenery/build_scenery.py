"""Run with Blender --background --factory-startup --python build_scenery.py."""
from pathlib import Path
from math import cos, sin, pi
import random
import sys
import bpy
import bmesh
from mathutils import Vector

OUT = Path(__file__).resolve().parent
OUT.joinpath("models").mkdir(exist_ok=True)
OUT.joinpath("textures").mkdir(exist_ok=True)
rng = random.Random(1123)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
requested = set(sys.argv[sys.argv.index("--")+1:]) if "--" in sys.argv else set()
scene.cycles.samples = 256
scene.cycles.use_adaptive_sampling = False
scene.cycles.sample_clamp_indirect = 2.0
prefs = bpy.context.preferences.addons["cycles"].preferences
for backend in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = backend
        prefs.refresh_devices()
    except (TypeError, RuntimeError):
        continue
    devices = [device for device in prefs.devices if device.type == backend]
    if devices:
        for device in prefs.devices:
            device.use = device in devices
        scene.cycles.device = 'GPU'
        print("Baking with", backend, devices[0].name, flush=True)
        break
scene.cycles.max_bounces = 5
scene.cycles.diffuse_bounces = 3
scene.world = bpy.data.worlds.new("Rain-sky")
scene.world.use_nodes = True
sky = scene.world.node_tree.nodes.get("Background")
sky.inputs["Color"].default_value = (0.26, 0.38, 0.51, 1)
sky.inputs["Strength"].default_value = 0.47

# Coordinates in this script are written as (Unity x, Unity z, height).
def point(x, z, h):
    return Vector((-x, -z, h))

def mat(name, color, rough=0.7, metal=0.0, grain=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if grain:
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = grain
        n.inputs["Detail"].default_value = 2.2
        tex = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tex.outputs["Object"], n.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*(v*0.92 for v in color),1)
        ramp.color_ramp.elements[1].color = (*(min(v*1.08,1) for v in color),1)
        nt.links.new(n.outputs["Fac"], ramp.inputs[0])
        nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    return m

plaster = mat("Mineral wash",(.49,.55,.54),grain=5)
paint = mat("Rain-dark teal",(.084,.19,.205),grain=9)
metal = mat("Galvanized corrugation",(.32,.40,.41),.37,0.09,14)
graphite = mat("Soot and wet steel",(.07,.105,.12),.43,0.12)
chalk = mat("Worn ivory",(.71,.71,.59),grain=22)
wood = mat("Oiled timber",(.26,.136,.071),grain=5)
deepwood = mat("Beam end grain",(.13,.075,.044),grain=9)
clay = mat("Old ceramic",(.145,.184,.181),grain=10)
paper = mat("Cream stationery",(.82,.72,.55))
blue = mat("Cobalt enamel",(.025,.12,.29),.22,.2)
enamel = mat("Washbasin interior",(.72,.79,.70),.22,.13)
water = mat("Standing rain",(.13,.29,.31),.15,.34)
russet = mat("Stamp lacquer",(.43,.09,.05),.42)
lamp = mat("Fluorescent diffuser",(.64,.80,.78))
amber = mat("Oiled window paper",(.88,.50,.22))
pavers = [mat("Flagstone-%d"%i,(.235+i*.018,.27+i*.017,.276+i*.015),grain=20) for i in range(4)]
groups = {}
name = ""

def mesh(label, vertices, faces, m):
    me = bpy.data.meshes.new(label)
    me.from_pydata(vertices, [], faces)
    me.update()
    ob = bpy.data.objects.new(label, me)
    scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    groups.setdefault(name, []).append(ob)
    return ob

def box(label, x,z,h, w,d,t,m):
    vs=[point(x+u*w/2,z+v*d/2,h+a*t/2) for a in (-1,1) for v in (-1,1) for u in (-1,1)]
    return mesh(label,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)

def rod(label, a,b,r,m, sides=10):
    start,end=point(*a),point(*b)
    axis=(end-start).normalized()
    side=axis.cross(Vector((0,0,1)))
    if side.length<0.01: side=Vector((1,0,0))
    side.normalize()
    up=axis.cross(side)
    vs=[where+r*(side*cos(i*2*pi/sides)+up*sin(i*2*pi/sides)) for where in (start,end) for i in range(sides)]
    faces=[(i,(i+1)%sides,sides+(i+1)%sides,sides+i) for i in range(sides)]+[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]
    return mesh(label,vs,faces,m)

def lathe(label,x,z,profile,m,steps=48):
    vs=[point(x+radius*cos(i*2*pi/steps),z+radius*sin(i*2*pi/steps),height) for radius,height in profile for i in range(steps)]
    faces=[(j*steps+i,j*steps+(i+1)%steps,(j+1)*steps+(i+1)%steps,(j+1)*steps+i) for j in range(len(profile)-1) for i in range(steps)]
    return mesh(label,vs,faces,m)

def strip(label,x0,x1,z0,z1,h0,h1,amp,period,m):
    # The nearest edge exposes the scalloped profile of pressed sheet or clay.
    n=round((z1-z0)/period)*6
    vs=[]
    for i in range(n+1):
        z=z0+(z1-z0)*i/n
        wave=amp*cos(2*pi*(z-z0)/period)
        for x,h in ((x0,h0),(x1,h1)):
            vs.extend((point(x,z,h+wave),point(x,z,h+wave-.028)))
    fs=[]
    for i in range(n):
        a=i*4
        fs.extend([(a,a+2,a+6,a+4),(a+1,a+5,a+7,a+3),(a,a+4,a+5,a+1),(a+2,a+3,a+7,a+6)])
    fs.extend([(0,1,3,2),(4*n,4*n+2,4*n+3,4*n+1)])
    return mesh(label,vs,fs,m)

name="walkway"
box("Bed joint",0,4,-.151,5.8,14,.254,graphite)
for row in range(20):
    near=-3+row*.7
    n=6 if near<4 else 5
    # Half-bond joints at alternate courses, with two properly cut end stones.
    w=5.8/n
    seams=[-2.9]+[-2.9+w*(i+(0.5 if row%2 else 1)) for i in range(n) if w*(i+(0.5 if row%2 else 1))<5.79]+[2.9]
    for left,right in zip(seams,seams[1:]):
        box("Paver",(left+right)/2,near+.35,-.0205,right-left-.016,.685,.04,rng.choice(pavers))
for zz in (-2,0,2,4,6,8,10):
    box("Drain recess",2.65,zz,-.0005,.24,.91,.012,graphite)
    for j in range(8): box("Drain bar",2.65,zz-.4+j*.11,.007,.235,.028,.018,metal)

name="campus"
box("School wall",-2.51,1,1.53,.25,6,3.06,plaster)
box("School tide line",-2.373,1,.43,.028,6,.86,paint)
for zz in (-.62,1.22,3.05):
    box("Window recess",-2.365,zz,1.9,.035,1.48,1.08,graphite)
    for k in (-.42,0,.42):
        box("Glazed light",-2.337,zz+k,1.86,.035,.37,.68,paint if zz>2 else lamp)
    box("Transom",-2.336,zz,2.30,.038,1.25,.13,metal)
    box("Drip sill",-2.29,zz,1.32,.21,1.6,.07,chalk)
for zz in (-1.82,1.1,3.97):
    box("Steel flange",.88,zz,.056,.32,.32,.11,metal)
    box("School column",.88,zz,1.46,.145,.15,2.92,paint)
    rod("Knee bracket",(.88,zz,2.46),(.28,zz,3.04),.035,metal)
    box("Rafter",-.68,zz,3.02,3.4,.09,.12,graphite)
box("Outer rail",.88,1,2.95,.12,6,.16,paint)
strip("Corrugated rain sheet",-2.53,1.18,-2,4,3.51,3.105,.033,.155,metal)
sheet = groups[name][-1]
sheet.vertex_groups.new(name="SheetOnly").add(range(len(sheet.data.vertices)),1,'REPLACE')
rod("Gutter",(1.14,-2,3.065),(1.14,4,3.065),.063,graphite)
for zz in (-1.73,2.92):
    rod("Rain pipe",(-2.22,zz,0),(-2.22,zz,2.99),.055,metal)
for zz in (-.8,1.1):
    box("Fluorescent case",-1.85,zz,2.84,.22,.98,.1,graphite)
    box("Diffuser",-1.85,zz,2.775,.175,.90,.04,lamp)
for zz in (-.8,-.2,.4):
    for offset in (-.21,.21): rod("Cycle stand",(-1.6,zz+offset,0),(-1.6,zz+offset,.56),.026,metal)
    rod("Cycle stand arch",(-1.6,zz-.21,.56),(-1.6,zz+.21,.56),.026,metal)

name="old-eaves"
box("Limewashed old wall",-2.51,7.5,1.46,.27,7,2.92,chalk)
for i in range(22):
    box("Tongue and groove",-2.36,4.16+i*.316,.49,.06,.298,.98,deepwood if i%3==0 else wood)
for zz in (4.08,7.25,10.85):
    box("Old stone shoe",.88,zz,.14,.31,.31,.28,pavers[2])
    box("Mortised upright",.88,zz,1.54,.185,.2,2.64,wood)
    rod("Timber corbel",(.88,zz,2.47),(.38,zz,2.95),.058,deepwood,6)
    box("Purlin bearer",-.70,zz,2.96,3.48,.17,.17,deepwood)
for i in range(25):
    zz=4.04+i*.286
    rod("Eave rafter",(-2.46,zz,3.53),(1.12,zz,2.99),.05,wood,8)
box("Lintel",.88,7.5,2.81,.19,7,.21,wood)
strip("Old tile courses",-2.64,1.19,4.012,11,3.64,3.065,.048,.282,clay)
for zz in (5.38,8.25,10.04):
    box("Wood reveal",-2.33,zz,1.79,.135,1.50,1.29,deepwood)
    box("Window paper",-2.249,zz,1.80,.035,1.33,1.095,amber)
    for delta in (-.50,-.25,0,.25,.5):
        box("Window mullion",-2.222,zz+delta,1.80,.038,.035,1.08,wood)
    for h in (1.47,1.91,2.21): box("Lattice rail",-2.219,zz,h,.049,1.32,.044,deepwood)
    box("Wood sill",-2.21,zz,1.12,.31,1.67,.085,wood)
rod("Lamp cord",(-1.85,7.60,3.25),(-1.85,7.60,2.70),.012,graphite)
lathe("Copper shade",-1.85,7.60,[(.025,2.7),(.13,2.63),(.205,2.55),(.209,2.535)],deepwood)
lathe("Amber glass",-1.85,7.60,[(.05,2.6),(.075,2.54),(.058,2.49),(.015,2.47)],amber)

name="desk"
for xx in (-1.87,-.53):
    for zz in (7.67,8.33): box("Tapered leg",xx,zz,.39,.08,.08,.78,deepwood)
for xx in (-1.86,-.54): box("Apron",xx,8,.708,.075,.74,.16,wood)
for zz in (7.67,8.33): box("Apron",-1.2,zz,.708,1.40,.075,.16,wood)
for zz in (7.72,8,8.28): box("Desk boards",-1.20,zz,.804,1.55,.273,.068,wood)
box("Three-cell card",-1.13,8.01,.846,.43,.245,.012,paper)
for xx in (-1.264,-1.13,-.996):
    box("Ink cell",xx,8.035,.853,.112,.117,.006,paint)
    box("Writing line",xx,7.95,.853,.079,.007,.006,graphite)
box("Stamp pad",-1.61,8.10,.866,.17,.13,.047,russet)
lathe("Date seal",-1.59,7.89,[(.054,.837),(.054,.875),(.025,.885),(.022,.95),(.037,.962),(.035,.989),(.014,1)],deepwood,24)
for cx,cz in ((-.78,7.22),(-1.84,8.61)):
    box("Stool seat",cx,cz,.43,.32,.34,.065,wood)
    for dx in (-.11,.11):
        for dz in (-.11,.11): rod("Stool leg",(cx+dx*1.3,cz+dz*1.3,.006),(cx+dx,cz+dz,.406),.023,deepwood,8)

name="basin"
x,z=1.42,5.5
lathe("Enamel bowl",x,z,[(.02,.016),(.19,.016),(.215,.038),(.291,.19),(.342,.278),(.362,.286),(.354,.306),(.333,.287),(.28,.197),(.19,.046),(.01,.046)],enamel)
lathe("Rolled blue rim",x,z,[(.353,.283),(.369,.288),(.371,.30),(.364,.31),(.349,.308),(.344,.298)],blue)
lathe("Rain surface",x,z,[(.001,.218),(.289,.218)],water)
for radius in (.07,.125,.182):
    lathe("BasinRipple",x,z,[(radius-.004,.219),(radius,.223),(radius+.004,.219)],enamel,48)

def area(label, pos, target, power, color, size):
    data = bpy.data.lights.new(label,'AREA')
    data.energy, data.color, data.shape, data.size = power,color,'DISK',size
    ob = bpy.data.objects.new(label,data)
    scene.collection.objects.link(ob)
    ob.location=point(*pos)
    ob.rotation_euler=(point(*target)-ob.location).to_track_quat('-Z','Y').to_euler()

area("Overcast skylight",(4.4,4,7.5),(0,4,0),760,(.68,.83,1),9)
area("Fluorescent",(-1.85,1.10,2.76),(-.45,1.7,.1),98,(.70,.88,1),1.05)
area("Cold spill",(-1.85,-.8,2.76),(-.50,-.7,.2),74,(.75,.91,1),.95)
area("Eaves pendant",(-1.85,7.6,2.48),(-1.08,7.9,.84),85,(1,.58,.29),.50)
area("Window spill",(-2.13,5.38,1.82),(1.42,5.5,.20),64,(1,.65,.39),1.05)
area("Far window",(-2.10,10.04,1.8),(0,10.1,.18),50,(1,.64,.37),.95)

def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]

origins={"walkway":(0,4,-.28),"campus":(-.79,1,0),"old-eaves":(-.79,7.5,0),"basin":(x,z,0),"desk":(-1.2,8,0)}
for key, objects in groups.items():
    if key=="basin":
        items = [ob for ob in objects if ob.name.startswith("BasinRipple")]
        select(items)
        bpy.ops.object.join()
        bpy.context.object.name="BasinRipple"
        groups[key]=[ob for ob in scene.objects if ob.type=="MESH" and ob.name in ("Enamel bowl","Rolled blue rim","Rain surface","BasinRipple")]
        continue
    select(objects)
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name=key+"-baked"
    groups[key]=[obj]
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.05, island_margin=.003)
    bpy.ops.object.mode_set(mode="OBJECT")
    if key == "walkway":
        # The platform currently delivers a 1024px atlas. Give the walking
        # surface two continuous strips; reserve the last band for the trim.
        mesh_data = obj.data
        uv = mesh_data.uv_layers.active.data
        for face in mesh_data.polygons:
            material = obj.data.materials[face.material_index]
            top = material.name.startswith("Flagstone-") and face.normal.z > .99
            near = -3 if -face.center.y < 4 else 4
            band = .006 if near == -3 else .472
            for index in face.loop_indices:
                if top:
                    v = mesh_data.vertices[mesh_data.loops[index].vertex_index].co
                    uv[index].uv = (.007 + (-v.y-near)*.986/7, band+(-v.x+2.9)*.45/5.8)
                else:
                    u, v = uv[index].uv
                    uv[index].uv = (.005 + .99*u, .936 + .058*v)

# Editable layout with original colors, objects, lights and occluders.
scene.render.bake.use_selected_to_active=False
scene.render.bake.margin_type='EXTEND'
scene.render.bake.margin=12
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"rain-master.blend"))
images={}
for key in ("walkway","campus","old-eaves","desk"):
    if requested and key not in requested: continue
    obj=groups[key][0]
    select([obj])
    size=2048 if key!="desk" else 1024
    target=bpy.data.images.new(key+"-GI",width=size,height=size,alpha=False)
    for m in obj.data.materials:
        nt=m.node_tree
        node=nt.nodes.new("ShaderNodeTexImage")
        node.image=target
        nt.nodes.active=node
    bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR','DIRECT','INDIRECT'})
    target.filepath_raw=str(OUT/"textures"/(key+".png"))
    target.file_format="PNG"
    target.save()
    images[key]=target
    print("Baked",key,flush=True)

for key,objects in groups.items():
    if requested and key not in requested: continue
    if key in images:
        obj=objects[0]
        baked=mat("GI-"+key,(1,1,1))
        nt=baked.node_tree
        tex=nt.nodes.new("ShaderNodeTexImage")
        tex.image=images[key]
        nt.links.new(tex.outputs["Color"],nt.nodes.get("Principled BSDF").inputs["Base Color"])
        obj.data.materials.clear()
        obj.data.materials.append(baked)
        for f in obj.data.polygons: f.material_index=0
        if key == "campus":
            # Share the same baked atlas, but animate only the sheet in the runtime.
            sheet_group = obj.vertex_groups["SheetOnly"].index
            for face in obj.data.polygons: face.select = False
            for edge in obj.data.edges: edge.select = False
            for v in obj.data.vertices:
                v.select = any(g.group == sheet_group for g in v.groups)
            select([obj])
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(type="VERT")
            bpy.ops.mesh.separate(type="SELECTED")
            bpy.ops.object.mode_set(mode="OBJECT")
            roof = next(part for part in bpy.context.selected_objects if part != obj)
            roof.name, obj.name = "RoofSkin", "CampusStructure"
            objects = [obj, roof]
    center=point(*origins[key])
    # Vertex positions become model-local. Scene bake uses the original layout.
    for ob in objects:
        inv=ob.matrix_world.inverted()
        for vertex in ob.data.vertices: vertex.co=inv@(ob.matrix_world@vertex.co-center)
    select(objects)
    bpy.ops.export_scene.gltf(filepath=str(OUT/"models"/(key+".glb")),use_selection=True,export_format='GLB',export_yup=True)
    print("Exported",key,flush=True)
