const waterRoot="n56";
const uris={"map-shore-water": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/4gw7taftidumhxb4.glb", "model-harbor-boat": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/ot6vsav68nlspzcv.glb", "model-harbor-pier": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/4m9fdd2j1ei8nsgp.glb", "model-bicycle": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/iyz52mz1f7wi6cz4.glb", "model-door": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/x6roiy53oszh2qpx.glb", "model-dusk-bank": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/i0l4pznna6harnlr.glb", "model-market-bank": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/avbn3vxwx9lm12qq.glb", "model-shutter": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/e0gursh6gx3f2hwv.glb", "model-steamer": "hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/70qdk5eikizt3fy7.glb"};
// The caller provides the fixed URIs and the map assembly's actual root.
const route = "n9";
await scene.nodes.reparent({nodes:[waterRoot],parent:route,preserve:"local"});
const sources = [
  ["HarborPier","harbor-pier",0,0,0], ["CentralBoat","harbor-boat",0,0,3.72],
  ["MarketBoat","harbor-boat",-11,.015,7.55], ["DuskBoat","harbor-boat",11,.015,7.55],
  ["MarketBank","market-bank",-11,0,11.2], ["DuskBank","dusk-bank",11,0,11.2],
  ["MarketShutter","shutter",-12.8,0,14.6], ["MarketSteamer","steamer",-9.2,0,19.7],
  ["DuskBicycle","bicycle",9.2,.14,14.6], ["DuskDoor","door",12.8,.65,19.7]
];
const moving = ["ShutterEdge","SteamerLid","BellCap","DoorLeaf","BowGlass","SternGlass"];
const staticPhysics=(await scene.components.get({nodes:["n50"],type:"physicsColliderData"})).items[0].values;
const records = {};
for(const [name,asset,x,y,z] of sources) {
  const model = await scene.assets.instantiateModel({name,parent:route,resource:uris["model-"+asset]});
  await scene.transforms.set({nodes:[model.root],space:"local",value:{position:{x,y,z},scale:{x:1,y:1,z:1}}});
  const meshes = (await scene.nodes.query({subtree:model.root},{fields:["handle","name","componentTypes"],limit:100})).items;
  for(const mesh of meshes) {
    if (!mesh.componentTypes.includes("glbSliceData") && meshes.length>1 && mesh.handle===model.root) continue;
    const has=mesh.componentTypes.includes("physicsColliderData");
    const values=moving.includes(mesh.name)?{enableCollision:false,enableRigidBody:false}:staticPhysics;
    const input={nodes:[mesh.handle],type:"physicsColliderData",values};
    if(has) await scene.components.set(input);
    else await scene.components.add(input);
  }
  records[name]=meshes;
}
for(const [name,x,y,z,r,g,b,intensity,range] of [
  ["HarborBowLamp",-.65,.66,4.99,1,.82,.48,1.7,4.6],
  ["MarketBerthLamp",-11.65,.675,8.82,1,.76,.41,2.1,5.2],
  ["DuskBerthLamp",10.35,.675,8.82,.69,.80,1,2.1,5.2],
  ["ReturnLamp",.65,.94,2.42,1,.54,.22,2.1,4.8],
  ["MarketSternLamp",-10.35,.955,6.25,1,.54,.22,1.65,4.0],
  ["DuskSternLamp",11.65,.955,6.25,1,.54,.22,1.65,4.0],
  ["SteamLamp",-9.3,2.65,19.55,1,.81,.60,1.9,4],
  ["DoorLamp",13.1,2.32,19.72,1,.61,.24,1.65,3.3]
]) {
  const n=await scene.nodes.create({name,parent:route});
  await scene.transforms.set({nodes:[n],space:"local",value:{position:{x,y,z}}});
  await scene.components.add({nodes:[n],type:"lightData",values:{type:2,color:{r,g,b,a:1},intensity,range,innerSpotAngle:20,outerSpotAngle:45}});
}
const spout=await scene.nodes.create({name:"SteamSpout",parent:route});
await scene.transforms.set({nodes:[spout],space:"local",value:{position:{x:-9.44,y:1.32,z:19.7}}});
const steam=await scene.scripts.create({path:"ShoreSteam.lua"});
const baked=await scene.scripts.bind({nodes:[route],script:"adf88912-b803-4df4-9604-aefdce797cdc"});
return {records,spout,steam,baked};
