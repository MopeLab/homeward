from route_cli import *
from hashlib import sha256
from shutil import copy2

base=json.loads((WORK/"03-river-disk.json").read_text(encoding="utf-8"))
disk=PROJECT/"scene.data"
assert sha256(disk.read_bytes()).hexdigest()==base["sceneSha256"]
backup=WORK/"03-before-ripples.scene.data"
if not backup.exists(): copy2(disk,backup)
key="model-water-capillary"
src=ROUTE/"River/river-surface.glb"
dest=PF/"assets/models"/key/"topology/model.glb"
if not dest.exists():
    run("authoring","resource","model","import",key,"--prefab",PREFAB,"--glb",str(src),workspace=True)
assert sha256(src.read_bytes()).digest()==sha256(dest.read_bytes()).digest()
check=run("authoring","resource","model","check",key,"--prefab",PREFAB,workspace=True)
save(WORK/"03-ripples-model-check.json",check)
res=run("authoring","resource","archive",key,"--kind","model","--prefab",PREFAB,"--request-id","03-capillary-model-1",workspace=True)
assert res["status"]=="completed"
save(WORK/"03-ripples-model.json",res)
rev=run("authoring","prefab","read",PREFAB,"context.capabilities",workspace=True)["revision"]
srcjs=WORK/"03-ripples-replace.js"
srcjs.write_text("""
const root="n113";
const old=(await scene.nodes.query({subtree:root},{fields:["handle","name"]})).items;
if(old.length!==1 || old[0].name!=="RiverSurface")throw new Error("Water root changed");
const props=(await scene.components.get({nodes:[root],type:"physicsColliderData"})).items[0].values;
const replacement=await scene.assets.replaceModel({root,name:"RiverSurface",replacement:URI});
const query=(await scene.nodes.query({subtree:replacement.root},{fields:["name","componentTypes"]})).items;
const input={nodes:[replacement.root],type:"physicsColliderData",values:props};
if(query[0].componentTypes.includes(input.type))await scene.components.set(input);else await scene.components.add(input);
return replacement;
""".replace("URI",json.dumps(res["uri"])),encoding="utf-8")
out=run("authoring","prefab","execute",PREFAB,"--file",str(srcjs),"--revision",rev,"--request-id","03-water-ripple-assembly-v1",workspace=True)
save(WORK/"03-ripples-assembly.json",out)
