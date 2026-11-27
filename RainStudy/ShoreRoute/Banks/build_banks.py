"""Build both playable shore sets (metres), bake fixed surfaces and export each prop.

blender -b -noaudio -P build_banks.py
Coordinates used by the construction methods are (Unity x, forward z, height).
"""
from pathlib import Path
from math import cos, sin, pi
from collections import defaultdict
import bpy
import bmesh
from mathutils import Vector

OUT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.max_bounces = 5
scene.cycles.diffuse_bounces = 3
scene.cycles.sample_clamp_indirect = 2.0
prefs = bpy.context.preferences.addons["cycles"].preferences
for backend in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = backend
        prefs.refresh_devices()
    except (TypeError, RuntimeError):
        continue
    devices = [item for item in prefs.devices if item.type == backend]
    if devices:
        for item in prefs.devices:
            item.use = item in devices
        scene.cycles.device = 'GPU'
        print("Cycles", backend, devices[0].name, flush=True)
        break
scene.world = bpy.data.worlds.new("Night water, diffuse skylight")
scene.world.use_nodes = True
sky = scene.world.node_tree.nodes['Background']
sky.inputs[0].default_value = (.37,.47,.69,1)
sky.inputs[1].default_value = .49
scene.render.bake.margin = 6
scene.render.bake.margin_type = 'EXTEND'
bpy.context.preferences.filepaths.save_version = 0


def material(name, rgb, rough=.72, grain=0, metal=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb,1)
    mat.use_nodes = True
    tree = mat.node_tree
    shader = tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (*rgb,1)
    shader.inputs['Roughness'].default_value = rough
    shader.inputs['Metallic'].default_value = metal
    if grain:
        noise = tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = grain
        noise.inputs["Detail"].default_value = 2.5
        coord = tree.nodes.new('ShaderNodeTexCoord')
        tree.links.new(coord.outputs['Object'],noise.inputs['Vector'])
        ramp = tree.nodes.new("ShaderNodeValToRGB")
        for stop,shade in zip(ramp.color_ramp.elements,(.67,1.26)):
            stop.color=(*(min(1,v*shade) for v in rgb),1)
        tree.links.new(noise.outputs['Fac'],ramp.inputs[0])
        tree.links.new(ramp.outputs[0],shader.inputs['Base Color'])
    return mat


stone = [material("Old granite %d"%i,(.27+.03*i,.30+.023*i,.30+.015*i),grain=8) for i in range(4)]
concrete = material("Fine roughcast",(.47,.43,.40),grain=24)
tile = material("Sea green glazed tile",(.32,.48,.44),.45,12)
lime = material("Patched lime wash",(.68,.65,.56),grain=7)
timber = material("Oiled cedar",(.26,.13,.061),grain=14)
umber = material("Wet wood end",(.13,.072,.04),grain=8)
iron = material("Gunmetal",(.09,.12,.115),.39)
zinc = material("Galvanized slat",(.48,.48,.405),.42)
green = material("Green duck canvas",(.093,.29,.23),.94,15)
green2 = material("Faded duck canvas",(.145,.345,.26),.94,15)
cream = material("Pale braid",(.74,.67,.49))
ochre = material("Oiled bamboo",(.64,.345,.105),grain=15)
rattan = material("Pale split bamboo",(.78,.56,.29),grain=26)
black = material("Soft tyres",(.035,.033,.03),.91)
red = material("Red oxide",(.34,.092,.056),grain=10)
glass = material("Evening glass",(.11,.19,.24),.3)
amber = material("Door light",(.99,.67,.25))
coal = material("Deep joint",(.055,.072,.078))
terracotta = material("Weathered clay",(.36,.195,.125),grain=8)
leaf = material("Balcony greens",(.13,.23,.11))


def point(p):
    x,z,h=p
    return Vector((-x,-z,h))


# Build a mesh per renderer; mobile does not need one draw call per tile or spoke.
class Part:
    def __init__(self, name, origin, pivot=None):
        self.name=name
        self.origin=origin
        self.pivot=point(pivot or (0,0,0))
        self.verts,self.faces,self.indices,self.materials=[],[],[],[]

    def mesh(self,verts,faces,mat):
        base=len(self.verts)
        self.verts.extend(point(v)-self.pivot for v in verts)
        if mat not in self.materials:
            self.materials.append(mat)
        index=self.materials.index(mat)
        for face in faces:
            self.faces.append(tuple(base+i for i in face))
            self.indices.append(index)

    def box(self,x,z,h,w,d,t,mat):
        verts=[(x+a*w/2,z+b*d/2,h+c*t/2) for c in (-1,1) for b in (-1,1) for a in (-1,1)]
        self.mesh(verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)

    def rod(self,a,b,r,mat,n=8):
        a,b = Vector(a),Vector(b)
        axis=(b-a).normalized()
        side=axis.cross(Vector((0,0,1)))
        if side.length<.001: side=Vector((1,0,0))
        side.normalize()
        up=axis.cross(side)
        pts=[p+r*(cos(i*2*pi/n)*side+sin(i*2*pi/n)*up) for p in (a,b) for i in range(n)]
        fs=[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
        self.mesh(pts,fs+[tuple(reversed(range(n))),tuple(range(n,2*n))],mat)

    def path(self,pts,r,mat,n=8):
        for a,b in zip(pts,pts[1:]):
            self.rod(a,b,r,mat,n)

    def lathe(self,x,z,profile,mat,n=28):
        pts=[(x+r*cos(i*2*pi/n),z+r*sin(i*2*pi/n),h) for r,h in profile for i in range(n)]
        faces=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i)
               for k in range(len(profile)-1) for i in range(n)]
        self.mesh(pts,faces,mat)

    def finish(self):
        data=bpy.data.meshes.new(self.name)
        data.from_pydata(self.verts,[],self.faces)
        for mat in self.materials: data.materials.append(mat)
        for face,idx in zip(data.polygons,self.indices): face.material_index=idx
        bm=bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        bm.to_mesh(data)
        bm.free()
        ob=bpy.data.objects.new(self.name,data)
        scene.collection.objects.link(ob)
        ob.location=point(self.origin)+self.pivot
        return ob


assets=defaultdict(list)
fixed=[]


def part(asset,name,origin,pivot=None):
    p=Part(name,origin,pivot)
    assets[asset].append(p)
    if pivot is None: fixed.append(p)
    return p


def quad(part, xs, zs, floor, depth, mat):
    x0,x1=xs; z0,z1=zs
    pts=[(x,z,floor(z)+dh) for dh in (-depth,0) for z in (z0,z1) for x in (x0,x1)]
    part.mesh(pts,[(4,5,7,6),(0,2,3,1),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)


def window(p,x,z,h,width,height,glazing,frame):
    side=1 if x<0 else -1
    p.box(x,z,h,.12,width+.18,height+.18,frame)
    p.box(x+side*.071,z,h,.04,width,height,glazing)
    for dz in (-.32,0,.32): p.box(x+side*.115,z+dz*width,h,.036,.035,height,frame)
    p.box(x+side*.12,z,h+height*.18,.04,width,.047,frame)
    p.box(x+side*.045,z,h-height*.54,.28,width+.26,.082,concrete)


def stool(p,x,z,h,upside=False):
    p.box(x,z,h,.43,.35,.076,timber)
    direction=1 if upside else -1
    for a in (-1,1):
        for b in (-1,1):
            p.rod((x+a*.135,z+b*.105,h),(x+a*.20,z+b*.14,h+direction*.37),.027,umber)
        p.rod((x+a*.174,z-.13,h+direction*.24),(x+a*.174,z+.13,h+direction*.24),.017,timber)


def crate(p,x,z,h):
    for dx in (-.26,.26):
        for dz in (-.29,.29): p.box(x+dx,z+dz,h+.19,.05,.05,.38,umber)
    for y in (.065,.205,.345):
        for dx in (-.28,.28): p.box(x+dx,z,h+y,.025,.65,.09,timber)
        for dz in (-.32,.32): p.box(x,z+dz,h+y,.57,.023,.09,ochre)


def roof(p,x1,x2,z1,z2,h1,h2,mat):
    quadroof=[(x1,z1,h1),(x2,z1,h2),(x2,z2,h2),(x1,z2,h1)]
    p.mesh(quadroof+[(x,z,h-.10) for x,z,h in quadroof],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],mat)


market_origin=(-11,22,0)
market=part("market-bank","MarketMasonry",market_origin)
market.box(0,4.85,-.33,6.4,13.3,.52,concrete)
for row in range(18):
    z0=-1.8+row*13.3/18
    seams=[-3.2]+[xx for xx in [-3.2+(j+(.5 if row%2 else 1))*1.28 for j in range(5)] if xx<3.19]+[3.2]
    for col,(a,b) in enumerate(zip(seams,seams[1:])):
        market.box((a+b)/2,z0+13.3/36,-.043,b-a-.014,13.3/18-.015,.086,stone[(row+col*3)%4])
# Old masonry quays and square access bollards.
for x in (-3.05,3.05):
    for z in (-1.45,.2,10.95):
        market.box(x,z,.25,.29,.29,.5,stone[1])
        market.box(x,z,.51,.34,.34,.07,stone[3])
    market.rod((x,-1.45,.4),(x,.2,.4),.036,iron)
# Low shop with tall clerestory over the rolling grille on the left.
market.box(-2.93,3.9,1.92,.53,6.75,3.84,lime)
for z in (.77,6.95): market.box(-2.56,z,1.6,.45,.46,3.2,concrete)
market.box(-2.45,3.83,2.76,.54,6.6,.21,timber)
for z in (1.55,3.95,6.36): window(market,-2.627,z,3.28,1.6,.50,glass,umber)
roof(market,-3.40,-2.22,.24,7.47,4.08,3.83,terracotta)
# Stitched, drooping panels with a scalloped valance.
for j in range(15):
    a=.45+j*.45; b=a+.45
    c=green if j%4 else green2
    for xa,xb,ha,hb in ((-2.61,-1.73,2.97,2.77),(-1.73,-.92,2.77,2.59)):
        market.mesh([(xa,a,ha),(xb,a,hb),(xb,b,hb),(xa,b,ha)],[(0,1,2,3)],c)
    pts=[(-.91,a,2.59),(-.91,b,2.59),(-.91,b,2.45),(-.91,(a+b)/2,2.39),(-.91,a,2.45)]
    market.mesh(pts,[(0,1,2,3,4)],c)
    market.rod((-2.60,a,2.975),(-.92,a,2.595),.012,green2,5)
for z in (.52,3.1,6.96):
    market.rod((-2.56,z,2.12),(-.92,z,2.61),.024,iron)
    market.rod((-.92,z,2.61),(-2.58,z,2.97),.018,iron)
# Separate cook stall and a narrow street that ends in another row of low roofs.
market.box(2.97,8.28,1.59,.44,5.95,3.18,lime)
market.box(2.71,8.3,.39,.09,5.85,.78,tile)
roof(market,1.06,3.30,6.17,10.67,2.48,3.16,green2)
for z in (6.26,10.56):
    market.rod((1.15,z,.01),(1.15,z,2.48),.046,umber)
    market.rod((1.15,z,2.46),(2.92,z,3.05),.033,timber)
for z in (7.03,9.55): window(market,2.70,z,1.72,1.19,.88,glass,umber)
for z in (4.71,5.45): crate(market,-2.05,z,0)
crate(market,-2.05,5.45,.385)
stool(market,-1.63,6.35,.39)
for zz in (7.48,9.46):
    market.box(2.02,zz,.78,1.20,.73,.10,timber)
    for dx in (-.45,.45):
        for dz in (-.25,.25): market.box(2.02+dx,zz+dz,.38,.08,.08,.76,umber)
stool(market,2.02,9.46,.87,True)
market.box(.10,11.3,1.32,5.1,.40,2.64,lime)
roof(market,-2.65,2.81,10.94,11.78,2.92,2.58,terracotta)
market.box(.24,11.076,.91,1.06,.09,1.82,red)
for x in (-1.65,1.55): market.box(x,11.075,1.43,.81,.09,.70,glass)

shutter_origin=(-12.8,25.4,0)
shop=part("shutter","ShutterFrame",shutter_origin)
shop.box(-.43,0,1.18,.18,2.16,2.36,coal)
for z in (-1.05,1.05): shop.box(-.23,z,1.18,.15,.10,2.36,zinc)
shop.box(-.23,0,2.4,.32,2.33,.23,iron)
shop.box(-.33,0,.56,.16,1.98,.89,umber)
for z in (-.65,-.18,.42):
    shop.box(-.19,z,.70,.14,.36,.36,timber)
for j in range(14):
    z=1.12+(.014 if j%2 else -.014)
    shop.rod((-.12,z,1.91-j*.057),(-.12,1.12,1.86-j*.057),.013,iron,6)
slat=part("shutter","ShutterEdge",shutter_origin,(-.13,0,1.38))
for j in range(13):
    slat.box(-.165,0,1.34+j*.078,.074,2.03,.080,zinc)
    slat.box(-.114,0,1.318+j*.078,.044,2.035,.023,iron)
slat.box(-.145,0,1.301,.11,2.08,.059,zinc)

steam_origin=(-9.2,30.5,0)
stall=part("steamer","SteamerHearth",steam_origin)
stall.box(0,0,.41,.82,.79,.82,terracotta)
stall.box(-.421,0,.29,.032,.36,.26,coal)
stall.lathe(0,0,[(.01,.807),(.365,.807),(.40,.85),(.398,.876)],iron)
for lev in range(2):
    h=.865+lev*.215
    stall.lathe(0,0,[(.02,h),(.365,h),(.373,h+.025),(.374,h+.193),(.363,h+.207)],ochre,40)
    for hh in (h+.037,h+.168):
        stall.lathe(0,0,[(.374,hh),(.383,hh+.004),(.38,hh+.025),(.374,hh+.027)],rattan,40)
    for j in range(16):
        theta=2*pi*j/16
        stall.rod((.373*cos(theta),.373*sin(theta),h+.045),(.375*cos(theta+.055),.375*sin(theta+.055),h+.155),.007,rattan,5)
lid=part("steamer","SteamerLid",steam_origin,(.29,0,1.3))
lid.lathe(0,0,[(.01,1.282),(.38,1.282),(.388,1.306),(.373,1.337),(.29,1.369),(.05,1.427),(.01,1.427)],rattan,48)
for j in range(24):
    t=2*pi*j/24
    lid.path([(.06*cos(t),.06*sin(t),1.424),(.28*cos(t+.15),.28*sin(t+.15),1.378),(.372*cos(t+.22),.372*sin(t+.22),1.34)],.009,ochre,5)
lid.path([(-.09,0,1.414),(-.076,0,1.483),(0,0,1.508),(.076,0,1.483),(.09,0,1.414)],.019,umber)


def grade(z):
    return max(0,min(.7,(z-2)*.1))


dusk=part("dusk-bank","DuskMasonry",(11,22,0))
for a,b in ((-1.8,2),(2,9),(9,11.5)):
    quad(dusk,(-3.2,3.2),(a,b),grade,.62,stone[0])
    for edge in (-3.1,2.98):
        quad(dusk,(edge-.10,edge+.10),(a,b),lambda z: grade(z)+.065,.065,concrete)
for z in (1,2.8,4.6,6.4,8.2,10):
    dusk.box(0,z,grade(z)+.001,5.8,.018,.004,stone[0])
for z in (-.95,1.4,4.15,6.95,9.8):
    h=grade(z)
    dusk.box(-2.90,z,h+.32,.36,.35,.64,concrete)
    dusk.box(-2.90,z,h+.65,.41,.41,.065,stone[2])
for a,b in zip((-.95,1.4,4.15,6.95),(1.4,4.15,6.95,9.8)):
    dusk.rod((-2.9,a,grade(a)+.48),(-2.9,b,grade(b)+.48),.042,iron)
# Changing height and open roof terraces along the right-hand side.
for idx,(za,zb,high) in enumerate(((.25,4.15,2.85),(4.18,7.06,3.64),(7.1,10.95,4.35))):
    zz=(za+zb)/2
    low=grade(za)-.15
    dusk.box(2.94,zz,(low+high)/2,.52,zb-za,high-low,lime if idx!=1 else concrete)
    dusk.box(2.65,zz,low+.44,.07,zb-za,.88,tile)
    dusk.box(2.91,zz,high+.06,.80,zb-za+.15,.16,concrete)
    if idx<2: window(dusk,2.65,zz,grade(zz)+1.65,1.25,.95,glass,iron)
    else:
        window(dusk,2.65,zz+1.20,2.61,.78,.87,glass,iron)
        window(dusk,2.65,zz-.60,3.50,1.65,.79,glass,iron)
    for dz in (-.72,0,.72): dusk.box(2.65,zz+dz,high+.34,.25,.16,.58,lime)
    dusk.rod((2.65,za,high+.58),(2.65,zb,high+.58),.052,concrete)
for z in (1.18,6.66):
    dusk.rod((2.58,z,grade(z)+.1),(2.58,z,3.05),.047,iron)
    dusk.path([(2.58,z,.27+grade(z)),(2.42,z,.24+grade(z)),(2.35,z,.08+grade(z))],.052,iron)
for z in (1.2,9.5):
    h=grade(z)
    dusk.rod((-2.55,z,h),(-2.55,z,4.8+h),.087,timber,10)
    dusk.box(-2.55,z,h+4.54,1.18,.12,.13,umber)
    for xx in (-2.97,-2.52,-2.11): dusk.lathe(xx,z,[(.026,4.56+h),(.06,4.59+h),(.042,4.66+h),(.055,4.72+h)],cream,10)
for x in (-2.97,-2.52,-2.11):
    dusk.path([(x,1.2+8.3*t,4.74+.7*t-.63*sin(pi*t)) for t in [i/12 for i in range(13)]],.017,iron,5)
dusk.box(0,11.4,1.89,5.75,.29,2.40,concrete)
dusk.box(.63,11.20,1.86,1.05,.10,2.31,umber)
dusk.box(-1.41,11.20,2.22,.89,.10,.78,glass)
for x in (-1.72,-1.49,-1.26,-1.03): dusk.box(x,11.135,2.22,.035,.04,.79,iron)
for z in (6.5,10.25):
    dusk.lathe(2.25,z,[(.11,grade(z)),(.18,grade(z)+.27),(.21,grade(z)+.29)],terracotta)
    for j in range(7):
        theta=j*2*pi/7
        dusk.rod((2.25,z,grade(z)+.22),(2.25+.18*cos(theta),z+.18*sin(theta),grade(z)+.38+.12*(j%2)),.033,leaf,5)

bike_origin=(9.2,25.4,.14)
bike=part("bicycle","BicycleFrame",bike_origin)
# The wheel planes face the player crossing the lane.
for cz in (-.56,.56):
    for radius,tube,mat in ((.325,.032,black),(.29,.016,zinc)):
        bike.path([(0,cz+radius*cos(j*pi/16),.36+radius*sin(j*pi/16)) for j in range(33)],tube,mat,7)
    for j in range(20):
        a=j*pi/10
        bike.rod(((j%2-.5)*.066,cz,.36),(0,cz+.283*cos(a),.36+.283*sin(a)),.006,zinc,5)
    bike.rod((-.06,cz,.36),(.06,cz,.36),.036,zinc)
for pts in ([(0,-.56,.36),(0,-.18,.78),(0,.08,.33),(0,-.56,.36)],
            [(0,-.18,.78),(0,-.07,.54),(0,.25,.59),(0,.39,.89)],
            [(0,.08,.33),(0,.36,.76)],[(0,.56,.36),(0,.37,.88),(0,.38,.99)]):
    bike.path(pts,.027,iron,10)
bike.rod((0,-.18,.76),(0,-.25,.9),.026,zinc)
bike.box(0,-.26,.923,.18,.27,.053,umber)
bike.path([(-.26,.27,1.02),(-.16,.38,1.035),(0,.42,1.03),(.17,.38,1.035),(.26,.27,1.02)],.022,zinc)
for x in (-.225,.225): bike.rod((x,.246,1.015),(x,.32,1.032),.030,black)
for sz in (-.17,.17):
    bike.rod((sz*.28,.08,.33),(sz*.55,.08+sz,.33+sz*.2),.016,zinc)
    bike.box(sz*.64,.08+sz,.33+sz*.2,.111,.055,.027,black)
bike.rod((0,-.08,.35),(-.16,-.12,.008),.012,iron)
bike.box(0,-.52,.756,.19,.48,.035,timber)
for x in (-.09,.09): bike.rod((x,-.69,.75),(x,-.56,.36),.013,iron)
bell=part("bicycle","BellCap",bike_origin,(.176,.353,1.05))
bell.lathe(.176,.353,[(.01,1.035),(.052,1.045),(.051,1.059),(.044,1.083),(.016,1.098),(.001,1.098)],zinc,28)
bell.rod((.175,.353,1.052),(.125,.31,1.053),.011,iron)

door_origin=(12.8,30.5,.65)
entry=part("door","DoorFrame",door_origin)
# A shallow reveal and a warm-painted return remain visible with the door ajar.
entry.box(.48,0,1.1,.10,1.13,2.2,amber)
for z in (-.584,.584): entry.box(.20,z,1.10,.66,.12,2.20,umber)
entry.box(.20,0,2.23,.69,1.29,.12,timber)
entry.box(.15,0,.034,.67,1.23,.068,stone[2])
entry.box(.25,-.81,1.53,.28,.21,.29,iron)
entry.box(.092,-.81,1.53,.05,.14,.18,amber)
leafpart=part("door","DoorLeaf",door_origin,(.14,-.516,.08))
leafpart.box(.12,-.04,1.1,.098,.978,2.07,timber)
for z in (-.41,.32): leafpart.box(.059,z,1.11,.04,.086,1.96,umber)
for h in (.25,1.11,1.92): leafpart.box(.054,-.02,h,.048,.82,.09,umber)
leafpart.box(.045,.327,1.05,.035,.082,.19,zinc)
leafpart.rod((.011,.32,1.082),(-.064,.32,1.082),.023,zinc)
leafpart.rod((-.064,.32,1.082),(-.064,.20,1.082),.021,zinc)
for zz in (.29,.33):
    leafpart.rod((-.013,zz,1.00),(-.01,zz+.035,.891),.012,zinc,6)
    leafpart.box(-.01,zz+.026,.897,.022,.042,.018,zinc)


def area(label,pos,target,power,rgb,diameter):
    light=bpy.data.lights.new(label,'AREA')
    light.energy,light.color,light.size=power,rgb,diameter
    ob=bpy.data.objects.new(label,light)
    scene.collection.objects.link(ob)
    ob.location=point(pos)
    ob.rotation_euler=(point(target)-ob.location).to_track_quat('-Z','Y').to_euler()


area("Morning across the river",(-6,19,8),(-11,28,1),1900,(1,.77,.49),6)
area("Cool open market sky",(-13,31,7),(-11,25,.5),620,(.69,.86,1),7)
area("Cooking stall pendant",(-9.0,30.4,2.25),(-9.18,30.6,1.13),45,(1,.63,.34),.37)
area("Violet overcast",(7,26,9),(11,28,.5),1000,(.59,.67,1),9)
area("Last sky at the landing",(9,19,5),(12,30,1),510,(.95,.64,.51),6)
area("Door spill",(12.92,30.8,1.68),(11.7,30.0,1.12),65,(1,.58,.26),.45)


def select(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj


objects={p:p.finish() for parts in assets.values() for p in parts}
for p in fixed:
    ob=objects[p]
    select(ob)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.03,island_margin=.003)
    bpy.ops.object.mode_set(mode='OBJECT')
    # Reserve a continuous band for the main floor, retaining ample texels for the
    # masonry/awning atlas. Position-based UVs match on adjoining flagstones.
    if p in (market,dusk):
        uv=ob.data.uv_layers.active.data
        for f in ob.data.polygons:
            z=-f.center.y
            floor_h=grade(z) if p is dusk else 0
            floor=f.normal.z>.9 and abs(f.center.z-floor_h)<.003 and ob.data.materials[f.material_index] in stone
            for li in f.loop_indices:
                if floor:
                    v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                    uv[li].uv=(.010+(-v.y+1.8)*.98/13.3,.004+(-v.x+3.2)*.31/6.4)
                else:
                    u,v=uv[li].uv
                    uv[li].uv=(.003+.994*u,.327+.668*v)
scene.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"banks-master.blend"))

targets={}
for p in fixed:
    ob=objects[p]
    select(ob)
    resolution=1536 if p in (market,dusk) else 512
    img=bpy.data.images.new(p.name+"-GI",resolution,resolution,alpha=False)
    newnodes=[]
    for m in ob.data.materials:
        node=m.node_tree.nodes.new("ShaderNodeTexImage")
        node.image=img
        m.node_tree.nodes.active=node
        newnodes.append((m,node))
    print("Baking",p.name,resolution,flush=True)
    bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR','DIRECT','INDIRECT'})
    img.filepath_raw=str(OUT/(p.name+"-GI.png"))
    img.file_format='PNG'
    img.save()
    for m,node in newnodes: m.node_tree.nodes.remove(node)
    targets[p]=img

for p,img in targets.items():
    obj=objects[p]
    m=material("GI-"+p.name,(1,1,1))
    tex=m.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image=img
    m.node_tree.links.new(tex.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    obj.data.materials.clear()
    obj.data.materials.append(m)
    for face in obj.data.polygons: face.material_index=0

for key,parts in assets.items():
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        ob=objects[p]
        ob.location=p.pivot
        ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[parts[0]]
    bpy.ops.export_scene.gltf(filepath=str(OUT/(key+".glb")),use_selection=True,export_format='GLB',export_yup=True)
    print("Exported",key,flush=True)
