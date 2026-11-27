"""Render the exported boat from four low viewpoints with backface culling.

Run from Blender in background. The four PNGs are local visual proof inputs.
"""
from pathlib import Path
import bpy
from mathutils import Vector

root = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(root/"harbor-boat.glb"))
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    tree = mat.node_tree
    tex = next((n for n in tree.nodes if n.type=="TEX_IMAGE"), None)
    emission = tree.nodes.new("ShaderNodeEmission")
    if tex:
        tree.links.new(tex.outputs[0],emission.inputs[0])
    else:
        emission.inputs[0].default_value = (1,.59,.23,1)
    mix = tree.nodes.new("ShaderNodeMixShader")
    tree.links.new(tree.nodes.new("ShaderNodeNewGeometry").outputs["Backfacing"],mix.inputs[0])
    tree.links.new(emission.outputs[0],mix.inputs[1])
    tree.links.new(tree.nodes.new("ShaderNodeBsdfTransparent").outputs[0],mix.inputs[2])
    tree.links.new(mix.outputs[0],tree.nodes.get("Material Output").inputs[0])
scene.world = bpy.data.worlds.new("River gray")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.145,.176,.205,1)
camera = bpy.data.cameras.new("Hull inspection")
cam = bpy.data.objects.new("Hull inspection",camera)
scene.collection.objects.link(cam)
scene.camera = cam
camera.type = "ORTHO"
scene.render.engine = "CYCLES"
scene.cycles.samples = 4
scene.view_settings.view_transform = "Standard"
scene.render.resolution_x,scene.render.resolution_y = 620,320
scene.render.resolution_percentage = 100
for name,position,scale in (("port",(5.6,.12,.16),4.9),("starboard",(-5.6,-.12,.16),4.9),
                            ("bow",(.12,-6,.11),3.95),("stern",(-.12,6,.11),3.95)):
    cam.location = position
    cam.rotation_euler = (Vector((0,0,.12))-cam.location).to_track_quat("-Z","Y").to_euler()
    camera.ortho_scale = scale
    scene.render.filepath = str(root/("boat-review-"+name+".png"))
    bpy.ops.render.render(write_still=True)
