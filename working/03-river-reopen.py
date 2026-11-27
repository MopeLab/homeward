import runpy
from route_cli import *

rid=json.loads((WORK/"03-river-reopen-runtime.json").read_text(encoding="utf-8"))["runtimeId"]
t=runpy.run_path(str(WORK/"03-water-playtest.py"))["WaterRun"](rid,False)
t.go(0,5.5)
t.tap("listenBtn", "听一听")
duration=t.js('const U=CS.UnityEngine;return U.GameObject.Find("Homeward_Card").GetComponent(puer.$typeof(U.AudioSource)).clip.length;')
assert abs(duration-19.09)<.03,duration
t.go(0,10.3)
scene=t.js("""
const U=CS.UnityEngine,s=U.GameObject.Find("ShoreRoute").transform;
const info=name=>{
 const tr=s.Find(name),r=tr.GetComponentInChildren(puer.$typeof(U.Renderer));
 const m=r.sharedMaterial,tex=m.GetTexture("_BaseTex");
 return {texture:tex.name,width:tex.width,display:m.GetFloat("_EmissionPower"),pieces:tr.childCount};
};
return {water:info("RiverSurface"),boats:["CentralBoat","MarketBoat","DuskBoat"].map(n=>info(n+"/FerryTimber")),
 old:!!s.Find("map-shore-water"),campusWater:!!s.parent.Find("map-rainwalk/Environment/volume/Node-2")};
""")
assert not scene["old"] and not scene["campusWater"] and all(s["width"]>1 for s in [scene["water"],*scene["boats"]]),scene
view=t.position_view(323,-65)
assert view["camera"][1]>-.30 and view["pitch"]>=-4.2,view
t.shot("重开-船侧最低视角")
t.position_view(2,14)
t.shot("重开-两岸全景")
save(WORK/"03-river-reopen-check.json",dict(runtime=rid,assets=scene,duration=duration,lowestRequested=view))
hooks=run("runtime","verifyNoTempHooks","--runtime-id",rid)
save(WORK/"03-river-reopen-hooks.json",hooks)
assert hooks["ok"]
run("runtime","stop","--runtime-id",rid)
save(WORK/"03-river-reopen-instance-stop.json",run("instance","stop"))
print(scene,view["pitch"],duration,flush=True)
