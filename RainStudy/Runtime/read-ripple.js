const U=CS.UnityEngine;
const ring=U.GameObject.Find("BasinRipple").transform;
const drops=U.GameObject.Find("Homeward_Basin").GetComponent(puer.$typeof(U.AudioSource));
const out=[];
for(let i=0;i<25;i++) {
  const s=ring.localScale;
  out.push([U.Time.time,s.x,s.z,drops.isPlaying?drops.volume:0]);
  await awaitFrames(2);
}
return out;
