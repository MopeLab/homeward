from route_cli import *
import runpy

phase=sys.argv[1]
runtime=run("runtime","status")
if runtime["status"]!="running": runtime=run("runtime","start","--wait","60")
rid=runtime["runtimeId"]
t=runpy.run_path(str(WORK/"03-water-playtest.py"))["WaterRun"](rid,False)
t.output=WORK/("03-ripples-"+phase)
t.output.mkdir(exist_ok=True)
save(t.output/"runtime.json",runtime)
t.go(0,15)
t.audition("keepBtn","听暮路 →","dusk")
t.confirm("dusk")
t.go(11,19.65)
view=t.position_view(99,76)
t.shot("暮路俯视")
save(t.output/"view.json",view)
if phase!="before":
    t.shot("暮路俯视第二帧")
    script="""
const U=CS.UnityEngine,s=U.GameObject.Find("RiverSurface");
const m=s.GetComponentInChildren(puer.$typeof(U.Renderer)).sharedMaterial;
const host=U.GameObject.Find("RiverRipples"),lines=host.GetComponentsInChildren(puer.$typeof(U.LineRenderer),true);
const sample=()=>{const e=m.GetTextureOffset("_EmissionTex"),b=m.GetTextureOffset("_BaseTex"),rs=[];
for(let i=0;i<lines.Length;i++){const l=lines.get_Item(i);if(l.enabled)rs.push([i,l.transform.localScale.x,l.startColor.a]);}
return {emission:[e.x,e.y],base:[b.x,b.y],rings:rs};};
const samples=[];for(let j=0;j<5;j++){samples.push(sample());await awaitFrames(4);}
const tex=m.GetTexture("_BaseTex");
return {width:tex.width,format:tex.format,mips:tex.mipmapCount,name:tex.name,wrap:tex.wrapMode,samples};
"""
    water=t.js(script)
    save(t.output/"animation.json",water)
    assert water["name"]=="River fine colour" and water["format"]==3 and water["mips"]==10,water
    assert water["samples"][0]["emission"]!=water["samples"][-1]["emission"]
    assert any(s["rings"] for s in water["samples"])
    t.edge("暮路船",11,19.68,11.87)
    count=t.runtime_call("lua","eval","return GetRiverContactCount()","--script","RainHost.lua")["result"]
    assert count in (1,[1]),count
    t.go(11,20.5)
    t.audition("listenBtn","听早市","market")
    t.confirm("market")
    t.position_view(85,15)
    t.shot("早市水线")
    save(t.output/"passed.json",dict(runtime=rid,contact=count,view=view))
hooks=run("runtime","verifyNoTempHooks","--runtime-id",rid)
assert hooks["ok"]
run("runtime","stop","--runtime-id",rid)
