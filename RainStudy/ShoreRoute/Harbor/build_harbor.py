"""Create the ferry and boarding pier with Cycles diffuse GI, then export GLBs.

Run with Blender 5.3 --background --factory-startup --python build_harbor.py.
Authoring coordinates below are Unity x, z, elevation in metres.
"""
from collections import defaultdict
from math import cos, sin, pi
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector

OUT = Path(__file__).resolve().parent
boat_only = "--" in sys.argv and "boat" in sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 96
scene.cycles.max_bounces = 5
scene.cycles.diffuse_bounces = 3
scene.cycles.sample_clamp_indirect = 2
prefs = bpy.context.preferences.addons["cycles"].preferences
for backend in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = backend
        prefs.refresh_devices()
    except (TypeError, RuntimeError):
        continue
    devices = [d for d in prefs.devices if d.type == backend]
    if devices:
        for device in prefs.devices:
            device.use = device in devices
        scene.cycles.device = "GPU"
        print("Baking with", devices[0].name, flush=True)
        break
scene.world = bpy.data.worlds.new("Rain over the river")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (.34,.47,.59,1)
bg.inputs["Strength"].default_value = .51
scene.render.bake.margin = 8
scene.render.bake.margin_type = "EXTEND"
scene.render.bake.use_selected_to_active = False
bpy.context.preferences.filepaths.save_version = 0

def vector(x,z,h):
    return Vector((-x,-z,h))

def material(name,color,rough=.7,metallic=0,texture=False):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    nt=mat.node_tree
    p=nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metallic
    if texture:
        tc=nt.nodes.new("ShaderNodeTexCoord")
        vec=nt.nodes.new("ShaderNodeVectorMath")
        vec.operation="MULTIPLY"
        vec.inputs[1].default_value=(12,2,10)
        nt.links.new(tc.outputs["Object"],vec.inputs[0])
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=3
        nt.links.new(vec.outputs[0],noise.inputs[0])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        for idx,factor in enumerate((.78,1.22)):
            ramp.color_ramp.elements[idx].color=(*(min(1,v*factor) for v in color),1)
        nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"],p.inputs["Base Color"])
    return mat

timber=[material("Oiled camphor %d"%i,(.266+.027*i,.141+.024*i,.072+.016*i),texture=True) for i in range(4)]
teal=material("River green paint",(.055,.174,.17),texture=True)
coal=material("Wet keel",(.048,.074,.073),.5)
cream=material("Ivory rubbing strake",(.64,.57,.39),texture=True)
copper=material("Oxidized brass",(.35,.225,.095),.44)
rope=material("Tarred hemp",(.31,.23,.139),texture=True)
stone=material("Wet quarried stone",(.26,.291,.277),texture=True)
sheet=material("Blank card",(.8,.70,.49))
ink=material("Faded cyan ink",(.18,.29,.27))
amber=material("Amber oiled diffuser",(.92,.52,.161),.37)
reed=material("Ochre rub rail",(.52,.32,.15),texture=True)
groups=defaultdict(list)
part=""
origin_z=0

def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name)
    data.from_pydata([vector(x,z+origin_z,h) for x,z,h in verts],[],faces)
    data.update()
    ob=bpy.data.objects.new(name,data)
    scene.collection.objects.link(ob)
    data.materials.append(mat)
    groups[part].append(ob)
    return ob

def box(name,x,z,h,w,d,t,mat):
    vs=[(x+a*w/2,z+b*d/2,h+c*t/2) for c in (-1,1) for b in (-1,1) for a in (-1,1)]
    return mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)

def rod(name,a,b,r,mat,n=10):
    start,end=Vector(a),Vector(b)
    axis=(end-start).normalized()
    t=axis.cross(Vector((0,0,1)))
    if t.length<.001:
        t=Vector((1,0,0))
    t.normalize()
    u=axis.cross(t)
    verts=[p+r*(t*cos(i*2*pi/n)+u*sin(i*2*pi/n)) for p in (start,end) for i in range(n)]
    faces=[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]+[tuple(reversed(range(n))),tuple(range(n,n*2))]
    return mesh(name,verts,faces,mat)

def curve(name,points,r,mat,n=8):
    for a,b in zip(points,points[1:]):
        rod(name,a,b,r,mat,n)

def lathe(name,x,z,profile,mat,n=16):
    verts=[(x+r*cos(i*2*pi/n),z+r*sin(i*2*pi/n),h) for r,h in profile for i in range(n)]
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
    return mesh(name,verts,faces,mat)

def lamp(x,z,h,glass):
    rod("Lamp mounting tenon",(x,z,-.07),(x,z,h-.06),.047,teal,12)
    lathe("Lamp seat",x,z,[(.076,h-.095),(.092,h-.06),(.092,h-.032),(.065,h)],copper)
    lathe("Lamp crown",x,z,[(.118,h+.24),(.12,h+.258),(.075,h+.283),(.04,h+.31),(.003,h+.32)],coal)
    global part
    prev=part
    part=glass
    lathe(glass,x,z,[(.004,h),(.064,h),(.087,h+.065),(.079,h+.23),(.06,h+.24),(.005,h+.24)],amber)
    part=prev
    for i in range(4):
        ang=2*pi*i/4
        dx,dz=.085*cos(ang),.085*sin(ang)
        rod("Lens guard",(x+.7*dx,z+.7*dz,h),(x+dx,z+dz,h+.245),.0065,copper,6)

part="PierTimber"
for x in (-.78,.78):
    box("Underbeam",x,.85,-.156,.14,2.25,.206,teal)
for i in range(10):
    # First plank overlaps the original stone by 18 cm and is 8 mm proud.
    z=-.18+(i+.5)*.204
    box("Pier plank",0,z,-.046,1.86,.198,.106,timber[(2*i+1)%4])
    for x in (-.75,.75):
        rod("Iron nail",(x,z,.007),(x,z,.010),.016,coal,8)
for x in (-.94,.94):
    for z in (.34,1.50):
        lathe("Oak pile",x,z,[(.10,-1.04),(.12,-.5),(.105,.24),(.101,.27)],timber[0],12)
        lathe("Pile band",x,z,[(.117,.076),(.117,.11)],coal)
    curve("Low mooring rope",[(x,.34,.235),(x,.73,.17),(x,1.11,.17),(x,1.5,.235)],.025,rope)
for z in (.27,1.55):
    box("Stone fixing shoe",-.92,z,-.46,.38,.34,.22,stone)

part="FerryTimber"
origin_z=3.72
# Longitudinal stations: pointed prow, narrow transom, a broad low step-through deck.
stations=[(-2.12,.71,.54),(-1.88,.823,.60),(-1.36,.99,.65),(-.65,1.035,.66),
          (.44,1.025,.64),(1.14,.936,.58),(1.63,.79,.49),(1.97,.64,.39),(2.12,.54,.34)]
def halfwidth(z):
    for (za,wa,_),(zb,wb,_) in zip(stations,stations[1:]):
        if z<=zb:
            return wa+(wb-wa)*(z-za)/(zb-za)
    return stations[-1][1]

def closed_hull():
    # One cross-section ring per station. Its five painted strakes, rim,
    # deck backing and bottom share vertices all the way to the end caps.
    depths = (0, .11, .17, .64, .86, 1)
    vertices, faces, colors = [], [], []
    for z, width, draft in stations:
        section = [(width, z, -.012)]
        for depth in depths:
            section.append((width * (1 - .43 * depth), z, -.085 - depth * draft))
        vertices.extend(section + [(-x, z, h) for x, z, h in reversed(section)])
    # Right rim to keel, underneath to port, then up to the closed deck.
    strakes = [timber[0], teal, cream, teal, timber[1], coal]
    surface = strakes + [coal] + list(reversed(strakes)) + [timber[0]]
    ring_size = len(surface)
    for station in range(len(stations)-1):
        for j, mat in enumerate(surface):
            near = station*ring_size
            far = near+ring_size
            next_j = (j+1)%ring_size
            faces.append((near+j,near+next_j,far+next_j,far+j))
            colors.append(mat)
    for station in (0,len(stations)-1):
        # Adjacent painted side bands are collinear in end view. Close
        # them with a centre fan to avoid degenerate exported triangles.
        ring = station*ring_size
        z, _, draft = stations[station]
        hub = len(vertices)
        vertices.append((0,z,-.08-draft*.48))
        for j in range(ring_size):
            a,b = ring+j,ring+(j+1)%ring_size
            faces.append((hub,b,a) if station==0 else (hub,a,b))
            colors.append(teal)
    obj = mesh("Watertight hull",vertices,faces,teal)
    palette = list(dict.fromkeys(colors))
    obj.data.materials.clear()
    for mat in palette: obj.data.materials.append(mat)
    for face,mat in zip(obj.data.polygons,colors):
        face.material_index = palette.index(mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if not all(edge.is_manifold and edge.is_contiguous for edge in bm.edges) or bm.calc_volume(signed=True)<=0:
        raise RuntimeError("The ferry hull must be a closed outward-facing shell")
    bm.to_mesh(obj.data)
    bm.free()

closed_hull()
for side in (-1,1):
    for i in range(len(stations)-1):
        za,wa,da=stations[i]
        zb,wb,db=stations[i+1]
        # Solid side sill protects rope pilot and makes a recognizable silhouette.
        lip=[(side*wa,za,.036),(side*wb,zb,.036)]
        rod("Sheer rail",*lip,.044,timber[1],10)
        rod("Rub rail",(side*wa*.953,za,-.16),(side*wb*.953,zb,-.16),.026,reed,8)
        rod("Keel seam",(side*.57*wa,za,-.085-da),(side*.57*wb,zb,-.085-db),.028,coal,8)
for i in range(28):
    za=-2.12+i*4.24/28+.002
    zb=-2.12+(i+1)*4.24/28-.002
    wa,wb=halfwidth(za)-.026,halfwidth(zb)-.026
    verts=[(s*w,z,h) for h in (-.086,0) for z,w in ((za,wa),(zb,wb)) for s in (-1,1)]
    mesh("Deck board",verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],timber[(i*7+i//5)%4])
    if i%2==0:
        for s in (-1,1):
            x=s*(wa-.065)
            rod("Deck fixing",(x,(za+zb)/2,-.001),(x,(za+zb)/2,.002),.011,coal,6)
for s in (-1,1):
    for z in (-1.06,-.26,.55):
        x=s*(halfwidth(z)-.07)
        rod("Light rail stanchion",(x,z,.017),(x,z,.59),.030,teal)
        lathe("Cast socket",x,z,[(.055,.008),(.052,.042),(.038,.052)],copper,12)
    curve("Hand rail",[(s*(halfwidth(z)-.07),z,.58) for z in (-1.06,-.26,.55)],.032,timber[2])
    curve("Safety line",[(s*(halfwidth(z)-.07),z,.28-.07*(i%2)) for i,z in enumerate((-1.06,-.66,-.26,.145,.55))],.012,rope)
# A seat alongside the rail leaves the passage between boat and pier clear.
for z in (-.74,-.20):
    box("Seat bearer",-.73,z,.197,.24,.055,.394,teal)
for x in (-.81,-.65):
    box("Stern seat",x,-.49,.41,.149,.89,.052,timber[3])
for z in (-.61,-.43):
    box("Card frame",-.704,z,.438,.189,.006,.004,ink)
box("Unwritten postcard",-.71,-.522,.442,.206,.143,.005,sheet)
for x in (-.776,-.714,-.652):
    box("Postcard cell",x,-.518,.446,.044,.056,.003,ink)
for i in range(3):
    pts=[]
    for j in range(33):
        theta=2*pi*j/32
        pts.append((.55+(.116+.019*i)*cos(theta),-.99+(.176+.019*i)*sin(theta),.022+.009*i))
    curve("Coiled painter",pts,.0105,rope,6)
lamp(.65,-1.30,.82,"SternGlass")
lamp(-.65,1.27,.54,"BowGlass")

def area(name,loc,target,watts,color,size):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=watts
    data.color=color
    data.shape="DISK"
    data.size=size
    ob=bpy.data.objects.new(name,data)
    scene.collection.objects.link(ob)
    ob.location=vector(*loc)
    ob.rotation_euler=(vector(*target)-ob.location).to_track_quat("-Z","Y").to_euler()
area("Broad cloudy sky",(-2,1,6),(0,2,0),630,(.70,.83,1),7)
area("Window light beside pier",(-2,-.5,2),(0,.5,0),72,(1,.65,.36),1.4)
area("Stern oil light",(.64,2.42,.96),(.1,2.18,0),19,(1,.55,.23),.33)
area("Bow oil light",(-.65,4.99,.7),(-.12,4.85,0),11,(1,.66,.36),.26)

def select(items):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in items:
        ob.select_set(True)
    bpy.context.view_layer.objects.active=items[0]
def join_part(name):
    objects=groups[name]
    select(objects)
    if len(objects)>1:
        bpy.ops.object.join()
    ob=bpy.context.object
    ob.name=name
    bm=bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob
objects={key:join_part(key) for key in list(groups)}
for key in ("PierTimber","FerryTimber"):
    select([objects[key]])
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.02,island_margin=.003)
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"harbor-master.blend"))
for name,size in (("PierTimber",768),("FerryTimber",1024)):
    if boat_only and name=="PierTimber": continue
    # The reusable ferry rests at three berths. Baking the central jetty
    # into its stern would leave solid black contact shapes at both shores.
    objects["PierTimber"].hide_render = name=="FerryTimber"
    ob=objects[name]
    select([ob])
    image=bpy.data.images.new(name+" GI",width=size,height=size,alpha=False)
    for m in set(ob.data.materials):
        tree=m.node_tree
        target=tree.nodes.new("ShaderNodeTexImage")
        target.image=image
        tree.nodes.active=target
    bpy.ops.object.bake(type="DIFFUSE",pass_filter={"COLOR","DIRECT","INDIRECT"})
    image.filepath_raw=str(OUT/(name+"-GI.png"))
    image.file_format="PNG"
    image.save()
    baked=material("GI-"+name,(1,1,1))
    tree=baked.node_tree
    tex=tree.nodes.new("ShaderNodeTexImage")
    tex.image=image
    tree.links.new(tex.outputs["Color"],tree.nodes["Principled BSDF"].inputs["Base Color"])
    ob.data.materials.clear()
    ob.data.materials.append(baked)
    for polygon in ob.data.polygons:
        polygon.material_index=0
objects["PierTimber"].hide_render = False
for name,parts,offset in (("harbor-boat",["FerryTimber","BowGlass","SternGlass"],3.72),("harbor-pier",["PierTimber"],0)):
    if boat_only and name=="harbor-pier": continue
    selected=[objects[k] for k in parts]
    for ob in selected:
        for v in ob.data.vertices:
            v.co-=vector(0,offset,0)
    select(selected)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+".glb")),use_selection=True,export_format="GLB",export_yup=True)
    print("Exported",name,flush=True)
