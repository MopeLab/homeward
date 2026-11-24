const targets = [
  {
    "slot": "campus",
    "root": "n41",
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/ju4g9rz7hlr6detj.glb"
  },
  {
    "slot": "desk",
    "root": "n43",
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/ovhfrs3o5umwc4n3.glb"
  },
  {
    "slot": "old-eaves",
    "root": "n45",
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/1fc1tgxxqofrfk4x.glb"
  },
  {
    "slot": "walkway",
    "root": "n47",
    "uri": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/9783kkmcoo8uxxqq.glb"
  }
];
const replacements = {};
async function configure(node,type,values) {
  const entry = (await scene.components.get({nodes:[node],type})).items[0];
  if(entry && entry.values) await scene.components.set({nodes:[node],type,values});
  else await scene.components.add({nodes:[node],type,values});
}
for (const item of targets) {
  const metadata=(await scene.components.get({nodes:[item.root],type:"editorOnlyData"})).items[0].values;
  const oldPhysics=(await scene.components.get({nodes:[item.root],type:"physicsColliderData"})).items[0].values;
  const model=await scene.assets.replaceModel({root:item.root,replacement:item.uri});
  await configure(model.root,"editorOnlyData",metadata);
  const meshes=await scene.nodes.query({subtree:model.root},{fields:["handle","name","depth"]});
  if(item.slot==="campus") {
    const roof=meshes.items.find(node=>node.name==="RoofSkin");
    const structure=meshes.items.find(node=>node.name==="CampusStructure");
    if(!roof || !structure) throw new Error("Missing independent roof or walls");
    await configure(structure.handle,"physicsColliderData",oldPhysics);
    await configure(roof.handle,"physicsColliderData",{enableCollision:false});
  } else {
    await configure(model.root,"physicsColliderData",oldPhysics);
  }
  replacements[item.slot]=meshes.items;
}
for(const node of ["n36","n38"]) await configure(node,"physicsColliderData",{enableCollision:false});
return replacements;
