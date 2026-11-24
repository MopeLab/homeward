await scene.nodes.reparent({nodes:["n11"],parent:"n1",preserve:"local"});
const rain = await scene.scripts.create({path:"GutterRain.lua"});
const display = await scene.scripts.create({path:"BakedColors.lua"});
return {rain,display};
