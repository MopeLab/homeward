// Read only. All points are in metres relative to the shared RainStudy root.
const U=CS.UnityEngine;
const route=U.GameObject.Find("ShoreRoute").transform;
const frame=route.parent;
const all=route.GetComponentsInChildren(puer.$typeof(U.Renderer),true);
const renderers=[];
const vec=p=>[p.x,p.y,p.z].map(x=>Number(x.toFixed(3)));
for(let i=0;i<all.Length;i++){
  const r=all.get_Item(i), t=r.transform, m=r.sharedMaterial;
  const c=t.GetComponent(puer.$typeof(U.Collider));
  renderers.push({name:t.name,parent:t.parent.name,position:vec(frame.InverseTransformPoint(t.position)),
    bounds:vec(r.bounds.size),center:vec(frame.InverseTransformPoint(r.bounds.center)),collision:!!c&&c.enabled,
    material:m&&m.name,emission:m&&m.HasProperty("_EmissionPower")&&m.GetFloat("_EmissionPower")});
}
const lights=route.GetComponentsInChildren(puer.$typeof(U.Light),true);
const lamps=[];
for(let i=0;i<lights.Length;i++){const l=lights.get_Item(i);lamps.push([l.name,l.enabled,l.intensity]);}
return {renderers,lamps};
