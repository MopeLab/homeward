const boatUri="hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/5doq88hqo2ipc08e.glb", waterUri="hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/awgsfimqcncis061.glb";
// The caller supplies the two archived model URIs.
const inspect = async root => (await scene.nodes.query({subtree:root},{
  fields:["name","handle","componentTypes"],limit:100
})).items;
async function physics(node, values) {
  const input={nodes:[node.handle],type:"physicsColliderData",values};
  if(node.componentTypes.includes(input.type)) await scene.components.set(input);
  else await scene.components.add(input);
}
const solid=(await scene.components.get({nodes:["n50"],type:"physicsColliderData"})).items[0].values;
const hulls={};
for(const [root,name] of [["n65","CentralBoat"],["n69","MarketBoat"],["n73","DuskBoat"]]) {
  const old=await inspect(root);
  if(old.length!==4 || old[0].name!==name) throw new Error(name+" changed");
  const replacement=await scene.assets.replaceModel({root,replacement:boatUri,name});
  const parts=await inspect(replacement.root);
  if(!["FerryTimber","BowGlass","SternGlass"].every(n=>parts.some(p=>p.name===n))) throw new Error(name+" incomplete");
  for(const p of parts) await physics(p, p.name.endsWith("Glass")?{enableCollision:false,enableRigidBody:false}:solid);
  hulls[name]=parts;
}
const oldCampus=await inspect("n13"), oldRiver=await inspect("n56");
if(oldCampus.length!==2 || oldCampus[0].name!=="volume" || oldRiver[0].name!=="map-shore-water") throw new Error("Water layout changed");
await scene.nodes.remove({nodes:["n13","n56"]});
const water=await scene.assets.instantiateModel({name:"RiverSurface",parent:"n9",resource:waterUri});
await scene.transforms.set({nodes:[water.root],space:"local",value:{position:{x:0,y:0,z:0},scale:{x:1,y:1,z:1}}});
const parts=await inspect(water.root);
for(const p of parts) await physics(p,solid);
return {hulls,river:parts,solid,oldCampus,oldRiver};
