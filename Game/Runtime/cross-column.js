const U=CS.UnityEngine;
const actor=CS.DouyinActorService.GetLocalActor();
const start=actor.position;
const channel=name=>U.GameObject.Find("Homeward_"+name).GetComponent(puer.$typeof(U.AudioSource));
const rain=channel("Rain"), tin=channel("Tin"), basin=channel("Basin");
const samples=[];
actor.MoveContinuously(new U.Vector2(0,1));
try {
  for(let i=0;i<48;i++) {
    await awaitFrames(2);
    const z=actor.position.z-start.z;
    samples.push({z,bedPlaying:rain.isPlaying,bedTime:rain.time,bedClip:rain.clip && rain.clip.GetInstanceID(),tinVolume:tin.isPlaying?tin.volume:0,basinVolume:basin.isPlaying?basin.volume:0});
    if(z>=5.3) break;
  }
} finally {actor.StopMove();}
return samples;
