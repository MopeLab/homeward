const U=CS.UnityEngine;
const main=U.Camera.main, actor=CS.DouyinActorService.GetLocalActor();
const v=p=>[p.x,p.y,p.z].map(n=>Math.round(n*1000)/1000);
const obj=U.GameObject.Find("map-rainwalk");
const materials=obj.GetComponentsInChildren(puer.$typeof(U.Renderer),false);
const visible=[];
for(let i=0;i<materials.Length;i++){
  const r=materials.get_Item(i);
  if(r.enabled && r.isVisible) visible.push(r.transform.parent.name+"/"+r.name);
}
const root=U.GameObject.Find("BasinRipple");
const physical=root.GetComponentsInChildren(puer.$typeof(U.Collider),true);
const solids=[];
for(let i=0;i<physical.Length;i++){
  const c=physical.get_Item(i);
  solids.push({name:c.name,enabled:c.enabled,trigger:c.isTrigger,size:v(c.bounds.size)});
}
return {pos:v(actor.position),camera:v(main.transform.position),forward:v(main.transform.forward),near:main.nearClipPlane,mask:main.cullingMask,visible,solids};
