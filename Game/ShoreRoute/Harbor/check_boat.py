"""Check the exported, single-sided glTF hull including UV seams and end caps."""
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parent
blob = (root / "harbor-boat.glb").read_bytes()
length = struct.unpack_from("<I", blob, 12)[0]
model = json.loads(blob[20:20+length])
binary = memoryview(blob)[28+length:]

def values(accessor):
    a = model["accessors"][accessor]
    view = model["bufferViews"][a["bufferView"]]
    dtype = np.dtype({5123:"<u2",5125:"<u4",5126:"<f4"}[a["componentType"]])
    size = {"SCALAR":1,"VEC2":2,"VEC3":3}[a["type"]]
    return np.ndarray((a["count"],size),dtype,binary,
                      a.get("byteOffset",0)+view.get("byteOffset",0),
                      (view.get("byteStride",size*dtype.itemsize),dtype.itemsize))

nodes = {n["name"]:n for n in model["nodes"]}
assert set(nodes) == {"FerryTimber","BowGlass","SternGlass"}
prim = model["meshes"][nodes["FerryTimber"]["mesh"]]["primitives"][0]
tri = values(prim["indices"]).reshape(-1,3)
xyz = values(prim["attributes"]["POSITION"])
uv = values(prim["attributes"]["TEXCOORD_0"])
assert np.isfinite(uv).all() and uv.min()>=0 and uv.max()<=1
image = model["bufferViews"][model["images"][0]["bufferView"]]
png = binary[image.get("byteOffset",0):][:image["byteLength"]]
assert bytes(png)==(root/"FerryTimber-GI.png").read_bytes()

# The shell is the edge-connected component containing the broad under-deck
# face. Weld position duplicates introduced by normal and UV discontinuities.
vertices, weld = np.unique(np.round(xyz,5),axis=0,return_inverse=True)
triangles = weld[tri]
by_edge = {}
def edges(face):
    return [tuple(sorted((face[i],face[(i+1)%3]))) for i in range(3)]
for index, face in enumerate(triangles):
    for edge in edges(face):
        by_edge.setdefault(edge,[]).append(index)
points = xyz[tri]
seed = np.flatnonzero((np.abs(points[:,:,1]+.012).max(axis=1)<1e-5)
                      & (np.ptp(points[:,:,0],axis=1)>1.0))[0]
todo, component = [seed], set()
while todo:
    item = todo.pop()
    if item in component: continue
    component.add(item)
    for edge in edges(triangles[item]):
        todo.extend(n for n in by_edge[edge] if n not in component)
idx = sorted(component)
frequency = Counter(edge for i in idx for edge in edges(triangles[i]))
assert set(frequency.values())=={2}, "non-manifold seam or hole in the shell"
f = points[idx]
normal = np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0])
centers = f.mean(axis=1)
orientation = np.einsum("ij,ij->i",centers-[0,-.25,0],normal)
assert (orientation>0).all(), "an exterior surface is back-facing"
assert len(idx)==252
uvf=uv[tri[idx]]
d1,d2=uvf[:,1]-uvf[:,0],uvf[:,2]-uvf[:,0]
assert (np.abs(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])>1e-9).all()
groups = dict(port=(normal[:,0]<-1e-6),starboard=(normal[:,0]>1e-6),
              bow=(np.abs(f[:,:,2]-2.12).max(axis=1)<1e-5),
              stern=(np.abs(f[:,:,2]+2.12).max(axis=1)<1e-5))
result = {"sha256":hashlib.sha256(blob).hexdigest(), "shellTriangles":len(idx),
          "shellEdgesWithTwoFaces":len(frequency), "frontFacingTriangles":int((orientation>0).sum()),
          "frontFacingBySide":{s:int(np.sum(mask & (orientation>0))) for s,mask in groups.items()},
          "uvTrianglesWithArea":len(idx), "embeddedAtlasSha256":hashlib.sha256(png).hexdigest()}
print(json.dumps(result,indent=2))
