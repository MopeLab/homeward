const root = await scene.nodes.create({name:"RainStudy", parent:null});
const anchors = {};
for (const [name,x,y,z] of [
  ["ColdLamp",-1.85,2.8,1.1], ["EaveLamp",-1.85,2.55,7.6],
  ["Tin",-1.25,0,2.3], ["Column",0.88,0,4], ["Basin",1.42,0,5.5],
  ["ReplyDesk",-1.2,0,8], ["Voice",1.4,0,8.8], ["ShoreRoute",0,0,10.8]
]) {
  const handle = await scene.nodes.create({name,parent:root});
  await scene.transforms.set({nodes:[handle],space:"local",value:{position:{x,y,z}}});
  anchors[name] = handle;
}
for (const [key,r,g,b,intensity,range] of [
  ["ColdLamp",0.70,0.86,1,1.6,5.5], ["EaveLamp",1,0.68,0.39,1.7,5]
]) {
  await scene.components.add({nodes:[anchors[key]],type:"lightData",values:{
    type:2,color:{r,g,b,a:1},intensity,range,innerSpotAngle:20,outerSpotAngle:45
  }});
}
const host = await scene.scripts.create({path:"RainHost.lua"});
const card = await scene.scripts.create({path:"Postcard.lua"});
return {root,anchors,host,card};
