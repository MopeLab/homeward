"""Tailor the editor's ambient-rain template to the leak above the enamel basin."""
import json
import sys
from pathlib import Path

source = Path(sys.argv[1])
effect = json.loads(source.read_text(encoding="utf-8-sig"))
root, drops, splashes, glow = effect["nodeTransformDatas"]
root["basic"]["nodeName"] = "漏檐的细雨"
glow["basic"]["isActive"] = False

def limits(curve, low, high):
    curve["min"], curve["max"] = low, high

for node, count, radius, color in (
        (drops, 14, .105, [.60,.75,.79,.72]),
        (splashes, 7, .105, [.53,.70,.72,.62])):
    p = node["effects"]["particleSystemData"]
    p["shape"]["radius"] = radius
    limits(p["emission"]["rateOverTime"],count,count)
    p["main"]["maxParticles"] = 24
    for field in ("minColor","maxColor"):
        p["main"]["startColor"][field] = color

d = drops["effects"]["particleSystemData"]
d["shape"]["position"] = [0,0,-2.70]
limits(d["main"]["startSpeed"],4.50,4.90)
limits(d["main"]["startLifetime"],.54,.58)
limits(d["main"]["startSizeX"],.025,.048)
limits(d["main"]["startSizeY"],.08,.13)
s = splashes["effects"]["particleSystemData"]
limits(s["main"]["startLifetime"],.21,.34)
for axis in ("X","Y","Z"):
    limits(s["main"]["startSize"+axis],.04,.10)
source.write_text(json.dumps(effect,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
