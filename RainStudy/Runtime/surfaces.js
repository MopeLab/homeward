const U=CS.UnityEngine;
const map=U.GameObject.Find("map-rainwalk");
const list=map.GetComponentsInChildren(puer.$typeof(U.Renderer),true);
const surfaces=[];
for(let i=0;i<list.Length;i++) {
  const r=list.get_Item(i), m=r.sharedMaterial;
  let t=r.transform,p=[];
  while(t && t.name!=="map-rainwalk"){p.unshift(t.name);t=t.parent;}
  surfaces.push({path:p.join("/"),shader:m&&m.shader.name,name:m&&m.name,texture:m&&m.mainTexture&&m.mainTexture.name});
}
return surfaces;
