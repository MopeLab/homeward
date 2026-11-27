// Start at the normal spawn in the saved 02 scene and walk toward its route marker.
const U = CS.UnityEngine;
const actor = CS.DouyinActorService.GetLocalActor();
const marker = U.GameObject.Find("ShoreRoute").transform;
const frame = marker.parent;
const local = () => frame.InverseTransformPoint(actor.position);
const v = p => [p.x, p.y, p.z];
const channel = name => U.GameObject.Find("Homeward_" + name).GetComponent(puer.$typeof(U.AudioSource));
const bed = channel("Rain"), tin = channel("Tin"), basin = channel("Basin");
const samples = [];
const target = marker.localPosition;
function sample() {
  samples.push({p:v(local()), frame:U.Time.frameCount, bed:bed.isPlaying && bed.clip.GetInstanceID(),
    bedTime:bed.time, tin:tin.isPlaying ? tin.volume : 0, basin:basin.isPlaying ? basin.volume : 0});
}
sample();
actor.MoveContinuously(new U.Vector2(0,1));
try {
  for (let i=0; i<120 && local().z<target.z-.30; i++) {
    await awaitFrames(2);
    sample();
  }
} finally { actor.StopMove(); }
await awaitFrames(5);
sample();
return {marker:v(target),samples};
