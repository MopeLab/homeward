// Map slots are already located at each Blender model's export origin.
const models = ["n35","n49","n52","n53","n55"];
for (const model of models) {
  await scene.transforms.set({nodes:[model],space:"local",scope:"subtree",
    value:{position:{x:0,y:0,z:0},scale:{x:1,y:1,z:1}}});
}
return models;
