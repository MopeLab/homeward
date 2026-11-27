"""Blender background script. All construction inputs are (Unity X, forward Z, Y) relative to (0,0,42)."""
from pathlib import Path
import math
import random
import bpy
import bmesh
from mathutils import Vector

out=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=48
scene.cycles.max_bounces=5
scene.cycles.diffuse_bounces=3
scene.cycles.sample_clamp_indirect=2
prefs=bpy.context.preferences.addons['cycles'].preferences
for kind in ('OPTIX','CUDA'):
    try:
        prefs.compute_device_type=kind
        prefs.refresh_devices()
    except (TypeError,RuntimeError):
        continue
    enabled=[d for d in prefs.devices if d.type==kind]
    if enabled:
        for d in prefs.devices:d.use=d in enabled
        scene.cycles.device='GPU'
        break
scene.world=bpy.data.worlds.new('Far shore twilight')
scene.world.use_nodes=True
sky=scene.world.node_tree.nodes['Background']
sky.inputs[0].default_value=(.28,.41,.60,1)
sky.inputs[1].default_value=.65


def point(x,z,h):
    return Vector((-x,-z,h))


def mat(name,color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    return m


walls=[mat('Distant plaster '+str(i),c) for i,c in enumerate(((.20,.255,.28),(.245,.28,.295),(.16,.22,.246),(.245,.255,.24)))]
roofm=[mat('Clay roof '+str(i),c) for i,c in enumerate(((.11,.145,.165),(.12,.155,.16),(.15,.155,.145)))]
wood=mat('Lattices and sills',(.085,.12,.13))
dark=mat('Dark glazing',(.086,.13,.155))
ashlar=mat('Shadowed quay',(.14,.185,.20))
warm=mat('Window paper',(.89,.55,.21))
light=mat('Lamp paper',(.96,.70,.35))
gleam=mat('Fragmented lamplight',(.38,.32,.20))

verts=[]; faces=[]; material_ids=[]; materials=[]
rng=random.Random(52641)


def shape(points,polys,m):
    n=len(verts)
    verts.extend(point(*p) for p in points)
    if m not in materials:materials.append(m)
    idx=materials.index(m)
    for poly in polys:
        faces.append(tuple(n+j for j in poly)); material_ids.append(idx)


def box(x,z,h,w,d,y,m):
    shape([(x+i*w/2,z+j*d/2,h+k*y/2) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
          [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)


def lamp(name,pos,to,power,diameter,color):
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.color=color;l.size=diameter
    inst=bpy.data.objects.new(name,l);scene.collection.objects.link(inst)
    inst.location=point(*pos)
    inst.rotation_euler=(point(*to)-inst.location).to_track_quat('-Z','Y').to_euler()


def home(x,z,w,d,h,rise,front_gable,lit):
    wall=walls[rng.randrange(len(walls))]; tile=roofm[rng.randrange(len(roofm))]
    box(x,z,(h-.12)/2,w,d,h+.12,wall)
    front=z-d/2
    box(x,front-.033,.25,w,.076,.39,ashlar)
    # Gable masonry and hip or pitched overhang, including fascia and ridge caps.
    def roof_pt(u,v,y):
        return (x+v,z+u,y) if front_gable else (x+u,z+v,y)
    length,width=(d,w) if front_gable else (w,d)
    gable=[roof_pt(u,v,y) for u in (-length/2,length/2) for v,y in ((-width/2,h),(width/2,h),(0,h+rise))]
    shape(gable,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],wall)
    half=length/2+.29; span=width/2+.30
    for side in (-1,1):
        pts=[roof_pt(-half,side*span,h-.10),roof_pt(half,side*span,h-.10),roof_pt(half,0,h+rise+.085),roof_pt(-half,0,h+rise+.085)]
        shape(pts+[(xx,zz,yy-.075) for xx,zz,yy in pts],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],tile)
    box(x,z,h+rise+.11,.13 if front_gable else length+.72,length+.72 if front_gable else .13,.14,tile)
    count=max(2,round(w/1.9))
    for i in range(count):
        px=x+(i+.5-count/2)*w/count
        wh=.65 if h<3 else .84
        wy=h-.86
        box(px,front-.066,wy,.85,.11,wh+.13,wood)
        glowing=i==lit
        box(px,front-.128,wy,.73,.023,wh,warm if glowing else dark)
        box(px,front-.147,wy,.035,.026,wh,wood)
        box(px,front-.148,wy+.09,.73,.026,.033,wood)
        if glowing:
            lamp('Window wash',(px,front-.72,wy+.16),(px,front,wy),12,.73,(1,.67,.32))
    dx=x+w*.25
    box(dx,front-.066,.88,.84,.12,1.76,wood)
    box(dx,front-.14,.91,.70,.04,1.63,dark)
    if rng.random()>.45:
        box(x-w*.22,z+.4,h+rise*.76,.28,.34,rise+.28,wall)
        box(x-w*.22,z+.4,h+rise*1.26+.16,.36,.42,.10,tile)


# Layering the edges behind the two foreground quays leaves an open bend in the centre.
for x,z,w,d,h,r,g,lit in [
    (-19.0,4.0,5.9,3.8,2.9,.85,False,0),(-14.0,1.9,4.1,3.3,3.3,.94,True,1),
    (-9.5,3.0,4.3,3.25,2.65,.82,False,1),(-5.95,5.25,3.0,3.5,3.6,.98,True,-1),
    (-4.0,8.45,3.7,3.0,2.3,.88,False,0),(-11.3,8.2,5.4,4.0,4.10,1.0,False,-1),
    (3.75,10.8,3.8,3.2,2.65,.76,False,1),(6.75,7.45,3.1,3.2,3.65,1.03,True,0),
    (10.75,4.15,4.3,3.7,2.85,.74,False,-1),(15.1,3.05,4.0,3.7,3.15,1.05,True,1),
    (19.9,4.75,5.6,4.2,2.60,.89,False,1),(12.1,8.65,5.8,3.7,4.25,.90,False,-1)]:
    home(x,z,w,d,h,r,g,lit)

for x,z,w in [(-18,2.40,9.8),(-10.75,2.0,6.4),(-6.1,4.05,4.2),(-3.8,7.25,4.0),
              (3.85,9.85,4.4),(6.8,6.15,3.6),(10.75,3,4.75),(16.8,1.80,8)]:
    waterface=z-1.9
    box(x,z,-.32,w,3.8,.77,ashlar)
    box(x,waterface-.015,.06,w+.07,.22,.12,walls[1])
    for i in range(round(w/2)):
        px=x+(i+.5-round(w/2)/2)*1.88
        box(px,waterface-.02,.25,.18,.22,.32,ashlar)

# Short, irregular broken reflections, 3 cm above water, under just three lit groups.
for x,z in ((-8.9,.05),(-3.9,5.29),(6.05,4.06)):
    for i in range(5):
        width=.37*(1-.095*i); depth=.035+.007*i
        xx=x+rng.uniform(-.12,.12);zz=z-.25-.31*i
        shape([(xx-width,zz,-.666),(xx+.23*width,zz+.6*depth,-.666),
               (xx+width,zz,-.666),(xx-.31*width,zz-depth,-.666)],[(0,1,2,3)],gleam)

lamp('Blue-hour fill',(-5,-8,12),(0,4,.8),420,(11),(.60,.76,1))
lamp('Warm far side',(-17,1,9),(-11,5,1),250,8,(1,.71,.50))
mesh=bpy.data.meshes.new('Far quay and staggered roofs')
mesh.from_pydata(verts,[],faces)
for m in materials:mesh.materials.append(m)
for f,idx in zip(mesh.polygons,material_ids):f.material_index=idx
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
ob=bpy.data.objects.new('FarRoofline',mesh);scene.collection.objects.link(ob)
ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.03,island_margin=.0035)
bpy.ops.object.mode_set(mode='OBJECT')
scene.render.bake.margin=6
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'backdrop-master.blend'))
img=bpy.data.images.new('Far shore baked diffuse',1024,1024,alpha=False)
for m in materials:
    t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=img;m.node_tree.nodes.active=t
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR','DIRECT','INDIRECT'})
img.filepath_raw=str(out/'far-roofline-GI.png');img.file_format='PNG';img.save()
target=mat('GI-FarRoofline',(1,1,1))
t=target.node_tree.nodes.new('ShaderNodeTexImage');t.image=img
target.node_tree.links.new(t.outputs['Color'],target.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
ob.data.materials.clear();ob.data.materials.append(target)
for poly in ob.data.polygons:poly.material_index=0
bpy.ops.export_scene.gltf(filepath=str(out/'far-roofline.glb'),use_selection=True,export_format='GLB',export_yup=True)
