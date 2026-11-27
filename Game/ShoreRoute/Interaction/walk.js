// The caller supplies RainStudy-local [x,z] waypoints on the walking surface.
const U = CS.UnityEngine, me = CS.DouyinActorService.GetLocalActor();
const frame = U.GameObject.Find("ShoreRoute").transform.parent;
const local = () => frame.InverseTransformPoint(me.position);
const samples = [];
const sample = p => samples.push({frame:U.Time.frameCount, x:p.x, y:p.y, z:p.z});
const targets = WAYPOINTS;
sample(local());
try {
  for (const [x,z] of targets) {
    for (let i=0; i<90; i++) {
      const p = local();
      const dx=x-p.x, dz=z-p.z, length=Math.hypot(dx,dz);
      if (length<0.27) break;
      if (i===89) return {ok:false, goal:[x,z], samples};
      const dir = frame.TransformDirection(new U.Vector3(dx/length,0,dz/length));
      me.MoveContinuously(new U.Vector2(dir.x,dir.z));
      await awaitFrames(2);
      if (i%3===0) sample(local());
    }
  }
} finally { me.StopMove(); }
await awaitFrames(5);
sample(local());
return {ok:true,samples};
