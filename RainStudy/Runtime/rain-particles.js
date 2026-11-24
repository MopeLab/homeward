const U=CS.UnityEngine;
const anchor=U.GameObject.Find("Basin");
const list=U.Object.FindObjectsOfType(puer.$typeof(U.ParticleSystem));
const layers=[];
for(let i=0;i<list.Length;i++) {
  const ps=list.get_Item(i),p=ps.transform.position;
  if (U.Vector3.Distance(p,anchor.transform.position)<5) {
    const renderer=ps.GetComponent(puer.$typeof(U.ParticleSystemRenderer));
    layers.push({name:ps.name,count:ps.particleCount,playing:ps.isPlaying,visible:renderer && renderer.enabled,world:[p.x,p.y,p.z]});
  }
}
return layers;
