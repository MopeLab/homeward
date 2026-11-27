// Native preview probe. Read state only; the driver's physical tap advances the game.
const U=CS.UnityEngine;
const spout=U.GameObject.Find("SteamSpout").transform;
const lid=U.GameObject.Find("SteamerLid").transform;
const track=U.GameObject.Find("Homeward_Card").GetComponent(puer.$typeof(U.AudioSource));
const renderer=lid.GetComponent(puer.$typeof(U.Renderer));
const pos=v=>[v.x,v.y,v.z].map(x=>+x.toFixed(4));
const numberOfFrames=FRAME_COUNT;
const samples=[];
for(let i=0;i<numberOfFrames;i++) {
  const systems=spout.GetComponentsInChildren(puer.$typeof(U.ParticleSystem),true);
  let particles=0;
  for(let j=0;j<systems.Length;j++) particles+=systems.get_Item(j).particleCount;
  samples.push({frame:U.Time.frameCount, particles, systems:systems.Length, lid:pos(lid.localPosition),
    angles:pos(lid.localEulerAngles), visible:renderer && renderer.isVisible,
    clip:track.isPlaying && track.clip ? track.clip.GetInstanceID() : null});
  if(i+1<numberOfFrames) await awaitFrames(1);
}
return samples;
