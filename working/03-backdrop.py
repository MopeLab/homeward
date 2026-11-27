from route_cli import *

uris=json.loads((WORK/"03-visual-uris.json").read_text(encoding="utf-8"))
path=WORK/"03-add-backdrop.js"
path.write_text("const uri="+json.dumps(uris["model-far-roofline"])+";\n"+"""
const matches=await scene.nodes.query({subtree:"n9"},{fields:["name","handle"],limit:100});
if(matches.items.some(row=>row.name==="FarShore")) throw new Error("FarShore already exists");
const model=await scene.assets.instantiateModel({parent:"n9",name:"FarShore",resource:uri});
await scene.transforms.set({nodes:[model.root],space:"local",value:{position:{x:0,y:0,z:31.2},scale:{x:1,y:1,z:1}}});
const rows=(await scene.nodes.query({subtree:model.root},{fields:["handle","componentTypes"]})).items;
for(const row of rows){
  const input={nodes:[row.handle],type:"physicsColliderData",values:{enableCollision:false,enableRigidBody:false}};
  if(row.componentTypes.includes("physicsColliderData")) await scene.components.set(input);
  else await scene.components.add(input);
}
return model;
""",encoding="utf-8")
rev=run("authoring","prefab","read",PREFAB,"context.capabilities",workspace=True)["revision"]
d=run("authoring","prefab","execute",PREFAB,"--revision",rev,"--file",str(path),"--request-id","03-v2-far-shore",workspace=True)
save(WORK/"03-backdrop-assembly.json",d)
print(d["result"])
