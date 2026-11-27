"""Derive a single one-shot steam plume from the installed campfire's Smoke02."""
import json
import shutil
from route_cli import PF, ROUTE, save

source = PF / "assets/effects/effect-shore-steam"
out = ROUTE / "Steam"
out.mkdir(exist_ok=True)
effect = json.loads((source / "effect.json").read_text(encoding="utf-8-sig"))
root, *layers = effect["nodeTransformDatas"]
smoke = next(n for n in layers if n["basic"]["nodeName"] == "Smoke02")
particle = smoke["effects"]["particleSystemData"]
table = root["effects"]["effectData"]
mat = table["materials"][particle["renderer"]["material"]]
tex_param = mat["properties"]["base"]["texture"]
tex = table["textures"][tex_param["texture"]]
ref = next(r for r in effect["resourceRefs"] if r["id"] == tex["textureRefId"])
table.update(materials=[mat], textures=[tex])
mat["material"] = tex_param["texture"] = particle["renderer"]["material"] = 0
effect["resourceRefs"] = [ref]
root["basic"]["nodeName"] = "蒸笼白汽"
root["effects"]["particleSystemData"] = particle
effect["nodeTransformDatas"] = [root]

def curve(field, a, b=None):
    b = a if b is None else b
    field.update(mode="constant" if a == b else "twoConstants", min=a, max=b, multiplier=b)

main = particle["main"]
main.update(duration=.62, loop=False, prewarm=False, maxParticles=20)
curve(main["startLifetime"], .88, 1.22)
curve(main["startSizeX"], .40, .62)
curve(main["startSpeed"], .59, .84)
main["startColor"].update(minColor=[1,.98,.94,.88], maxColor=[1,.98,.94,.88])
particle["shape"].update(radius=.065, angle=13, rotation=[-90,0,0])
curve(particle["emission"]["rateOverTime"],25)
particle["limitVelocityOverLifetime"]["enabled"] = False
wind = particle["forceOverLifetime"]
wind["enabled"] = True
curve(wind["x"], -.38)
color = particle["colorOverLifetime"]["color"]["maxGradient"]
color["alphaKeys"] = [dict(time=t, alpha=a) for t,a in ((0,0),(.14,.96),(.49,.75),(1,0))]
particle["renderer"].update(sortingOrder=0, pivot=[0,0,0])
save(out / "effect.json",effect)
save(out / "meta.json",{"resourceId":"effect-shore-steam","displayName":"蒸笼白汽"})
texture = out / ref["pathOrUrl"]
texture.parent.mkdir(exist_ok=True)
shutil.copyfile(source / ref["pathOrUrl"], texture)
