from pathlib import Path
import bpy
from mathutils import Vector
from sys import argv
root=Path(argv[-1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES'; s.cycles.samples=8
s.world=bpy.data.worlds.new('Dawn blue');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.21,.26,.38,1)
s.view_settings.view_transform='Standard'
s.render.resolution_x=880;s.render.resolution_y=630;s.render.resolution_percentage=100
for f,p in [('market-bank',(-11,22,0)),('dusk-bank',(11,22,0)),('shutter',(-12.8,25.4,0)),('steamer',(-9.2,30.5,0)),('bicycle',(9.2,25.4,.14)),('door',(12.8,30.5,.65))]:
    bpy.ops.import_scene.gltf(filepath=str(root/(f+'.glb')))
    for o in bpy.context.selected_objects:
        if o.parent is None: o.location+=Vector((-p[0],-p[1],p[2]))
for m in bpy.data.materials:
    if not m.name.startswith('GI-'):continue
    nt=m.node_tree; tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs[0],em.inputs[0]);nt.links.new(em.outputs[0],out.inputs[0])
bpy.ops.object.camera_add()
cam=bpy.context.object; cam.data.lens=22;s.camera=cam
for name,src,dst in [('market',(-10.7,20.6,1.58),(-11.5,28,1.58)),('dusk',(10.7,20.6,1.58),(11.5,28,1.72))]:
    cam.location=(-src[0],-src[1],src[2]);target=Vector((-dst[0],-dst[1],dst[2]))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(root/(name+'-baked-preview.png'))
    bpy.ops.render.render(write_still=True)
