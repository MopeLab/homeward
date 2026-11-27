
const root="n113";
const old=(await scene.nodes.query({subtree:root},{fields:["handle","name"]})).items;
if(old.length!==1 || old[0].name!=="RiverSurface")throw new Error("Water root changed");
const props=(await scene.components.get({nodes:[root],type:"physicsColliderData"})).items[0].values;
const replacement=await scene.assets.replaceModel({root,name:"RiverSurface",replacement:"hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/zwvjkye4fvgggbtz.glb"});
const query=(await scene.nodes.query({subtree:replacement.root},{fields:["name","componentTypes"]})).items;
const input={nodes:[replacement.root],type:"physicsColliderData",values:props};
if(query[0].componentTypes.includes(input.type))await scene.components.set(input);else await scene.components.add(input);
return replacement;
