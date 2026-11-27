const uri="hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/aaof8149n9vms475.glb";

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
