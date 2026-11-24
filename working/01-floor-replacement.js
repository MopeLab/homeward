const old="n54";
const metadata=(await scene.components.get({nodes:[old],type:"editorOnlyData"})).items[0].values;
const physics=(await scene.components.get({nodes:[old],type:"physicsColliderData"})).items[0].values;
const {root}=await scene.assets.replaceModel({root:old,replacement:"hamlet-ugc/aigc_editor/dev/unity/MS4wLjABAAAAoKzFbzyuPWSZhiJM1kV60rEwa67IzF6emT_e2vT36FsxPNHcX7DnWL7PMIZW7bCd/9783kkmcoo8uxxqq.glb"});
for(const [type,values] of [["editorOnlyData",metadata],["physicsColliderData",physics]]) {
  const current=(await scene.components.get({nodes:[root],type})).items[0];
  if(current?.values) await scene.components.set({nodes:[root],type,values});
  else await scene.components.add({nodes:[root],type,values});
}
return root;
