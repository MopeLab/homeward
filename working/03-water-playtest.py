"""Replay the same ordinary movement and SDK camera pitch on the 04 baseline and water fix."""
import argparse
import json
from pathlib import Path
import runpy
import time

from route_cli import WORK, save

game=runpy.run_path(str(WORK/"03-playtest.py"))
PORTS=game["PORTS"]
base=game["VoyageTest"]


class WaterRun(base):
    def __init__(self,rid,before):
        super().__init__(rid)
        self.before=before
        self.output=WORK/(("03-water-before-" if before else "03-water-after-")+rid)
        self.output.mkdir(exist_ok=True)

    def position_view(self,yaw,pitch):
        return self.js(f"""
const api=CS.DouyinCameraService, U=CS.UnityEngine;
api.SetYaw({yaw}); api.SetPitch({pitch});
await awaitFrames(12);
const c=api.GetCamera(), a=CS.DouyinActorService.GetLocalActor();
const f=U.GameObject.Find("ShoreRoute").transform.parent;
const v=p=>[p.x,p.y,p.z];
return {{yaw:api.GetYaw(),pitch:api.GetPitch(),camera:v(f.InverseTransformPoint(c.transform.position)),
    direction:v(c.transform.forward),actor:v(f.InverseTransformPoint(a.position)),near:c.nearClipPlane}};""")

    def fixed_shot(self,tag):
        view=self.position_view(270,-32)
        self.shot(tag)
        self.journal(tag,view)
        return view

    def go(self,x,z):
        source=(game["INTERACTION"]/"walk.js").read_text(encoding="utf-8")
        raw=self.js(source.replace("WAYPOINTS",json.dumps([[x,z]])),60000)
        self.journal("步行",raw)
        assert raw["ok"],raw

    def count(self):
        if self.before: return 0
        data=self.runtime_call("lua","eval","return GetWaterRecoveryCount()","--script","RainHost.lua")
        return int(data["result"][0] if isinstance(data["result"],list) else data["result"])

    def edge(self,tag,x,z,max_x):
        self.go(x,z)
        if not self.before:
            yaw = 326 if tag=="中央船" else (87 if tag=="早市船" else (273 if tag=="暮路船" else 0))
            self.position_view(yaw,16)
            self.shot(tag+"-水面与船舷")
        view=self.fixed_shot(tag+"-边缘低机位")
        prior=self.count()
        track=self.js("""
const U=CS.UnityEngine, f=U.GameObject.Find("ShoreRoute").transform.parent;
const a=CS.DouyinActorService.GetLocalActor(), c=CS.DouyinCameraService.GetCamera();
const dir=f.TransformDirection(new U.Vector3(1,0,0)), pts=[];
const read=()=>{const p=f.InverseTransformPoint(a.position), eye=f.InverseTransformPoint(c.transform.position);
    pts.push({frame:U.Time.frameCount,x:p.x,y:p.y,z:p.z,eyeY:eye.y});};
read();
a.MoveContinuously(new U.Vector2(dir.x,dir.z));
try {
    for(let i=0;i<70;i++) {
        await awaitFrames(1); read();
        const last=pts[pts.length-1], prev=pts[pts.length-2];
        if(last.x<prev.x-.4 || last.x>LIMIT) break;
    }
} finally {a.StopMove();}
await awaitFrames(8);read();return pts;""".replace("LIMIT",str(max_x+1.45)))
        save(self.output/(tag+"-轨迹.json"),track)
        end=track[-1]
        after=self.count()
        self.shot(tag+"-侧步后")
        self.journal("边缘结果",{"tag":tag,"start":view,"end":end,"before":prior,"after":after})
        print(tag,f"最大 x {max(r['x'] for r in track):.3f}，结束 x {end['x']:.3f}，y {end['y']:.3f}，恢复 {prior}→{after}",flush=True)
        if self.before:
            # Baseline has no recovery: reset the fixture only AFTER saving ordinary movement evidence.
            self.js(f"""
const f=CS.UnityEngine.GameObject.Find("ShoreRoute").transform.parent;
const a=CS.DouyinActorService.GetLocalActor();
a.Teleport(f.TransformPoint(new CS.UnityEngine.Vector3({x},.15,{z})),a.rotation);
await awaitFrames(8);return true;""")
        else:
            assert after==prior+1 and end["x"]<max_x+.12 and end["y"]>-.18,(tag,prior,after,end)
            assert min(p["eyeY"] for p in track)>-.30, (tag,"camera crossed water",track)

    def actual_jump(self):
        prior=self.count()
        self.runtime_call("input","keys","press:Space")
        heights=self.js("""
const U=CS.UnityEngine, a=CS.DouyinActorService.GetLocalActor(), f=U.GameObject.Find("ShoreRoute").transform.parent;
const h=[];for(let i=0;i<32;i++){h.push(f.InverseTransformPoint(a.position).y);await awaitFrames(1);}return h;""")
        self.journal("正常跳跃",heights)
        assert max(heights)-min(heights)>.09 and self.count()==prior, (heights,prior)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("runtime");p.add_argument("--before",action="store_true")
    p.add_argument("--stage",choices=["campus","boat","market","dusk"],default="campus")
    args=p.parse_args()
    t=WaterRun(args.runtime,args.before)
    orig=t.js("return [CS.DouyinCameraService.GetYaw(),CS.DouyinCameraService.GetPitch()];")
    stages=["campus","boat","market","dusk"]
    try:
        for action in stages[stages.index(args.stage):]:
            t.stage=action
            print(action,flush=True)
            if action=="campus":
                t.edge("校园侧面",0,2.3,2.9)
                if not args.before: t.actual_jump()
            elif action=="boat":
                t.edge("中央船",0,15.75,.91)
                t.go(0,15);t.audition("listenBtn","← 听早市","market");t.confirm("market")
            elif action=="market":
                t.edge("早市船",-11,19.68,-10.13)
                t.go(-11,20.5);t.audition("listenBtn","听暮路","dusk");t.confirm("dusk")
            else:
                t.edge("暮路船",11,19.68,11.87)
                prior=t.count()
                t.go(11,30.5)
                assert t.count()==prior
                t.fixed_shot("放学路坡面")
    finally:
        t.position_view(orig[0],orig[1])

if __name__=="__main__": main()
