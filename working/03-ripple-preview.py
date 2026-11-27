from route_cli import *
from PIL import Image
import runpy

rid=run("runtime","start","--wait","60")["runtimeId"]
t=runpy.run_path(str(WORK/"03-water-playtest.py"))["WaterRun"](rid,False)
t.output=WORK/"03-ripples-reopen"
t.output.mkdir(exist_ok=True)
t.go(0,15)
t.audition("keepBtn","听暮路 →","dusk")
t.confirm("dusk")
# Walk to the open end of the boat and look down from the quay side.
t.go(11,17.12)
t.js("CS.DouyinCameraService.SetDistance(5.0);return true;")
view=t.position_view(67,63)
t.shot("暮路船头俯拍")
info=t.js("""
const U=CS.UnityEngine, m=U.GameObject.Find("RiverSurface").GetComponent(puer.$typeof(U.Renderer)).sharedMaterial;
const tex=m.GetTexture("_EmissionTex");
return {name:tex.name,format:tex.format,levels:tex.mipmapCount,ringPool:U.GameObject.Find("RiverRipples").transform.childCount};
""")
assert info["name"]=="River fine colour" and info["format"]==3 and info["ringPool"]==12,info
# Capture public runtime screenshots in slowed simulation and play them at the
# measured in-game interval. Restore the prior clock before stopping this test.
old=t.js("const T=CS.UnityEngine.Time,v=T.timeScale;T.timeScale=.10;return v;")
frames=[]
times=[]
try:
    for i in range(22):
        times.append(t.js("return CS.UnityEngine.Time.time;"))
        path=t.output/f"wave-{i:02d}.png"
        t.runtime_call("screenshot","--out",str(path))
        with Image.open(path) as shot:
            frame=shot.convert("RGB")
            frame.thumbnail((1060,620),Image.Resampling.LANCZOS)
            frames.append(frame)
finally:
    t.js(f"CS.UnityEngine.Time.timeScale={float(old)};return true;")
dur=[max(25,round((b-a)*1000)) for a,b in zip(times,times[1:])]
out=ROOT/"RainStudy/Evidence/03-river-waves.webp"
frames[0].save(out,format="WEBP",save_all=True,append_images=frames[1:],duration=dur+[dur[-1]],loop=0,quality=88)
with Image.open(out) as image: assert image.n_frames==len(frames)
save(t.output/"check.json",dict(runtime=rid,render=info,view=view,times=times,frames=len(frames)))
hooks=run("runtime","verifyNoTempHooks","--runtime-id",rid)
assert hooks["ok"]
run("runtime","stop","--runtime-id",rid)
save(t.output/"instance-stop.json",run("instance","stop"))
print(info,"frames",len(frames),"seconds",times[-1]-times[0],flush=True)
