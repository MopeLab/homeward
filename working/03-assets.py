from route_cli import *
from shutil import copy2

receipt=WORK/"03-visual-uris.json"
uris=json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
def archive(key,kind):
    out=run("authoring","resource","archive",key,"--kind",kind,"--prefab",PREFAB,workspace=True)
    if out["status"]!="completed": raise RuntimeError(str(out))
    uris[key]=out["uri"]
    save(receipt,uris)
    print(key,flush=True)

def skill(name,argv):
    return run("authoring","skill","run",name,"--workspace",str(WS),"--argv",json.dumps(argv,ensure_ascii=False))

if "map" in sys.argv:
    key="map-shore-water"
    if key not in uris:
        target=PF/"assets/maps"/key
        if not target.exists():
            skill("initialize-map",["--config",json.dumps(dict(prefabId=PREFAB,resourceId=key,displayName="两岸暗水",summary="与校园水面接合的三段河水",bounds=[90,100],seed=1124),ensure_ascii=False)])
        copy2(ROUTE/"Harbor/scene.scad",target/"source/scene.scad")
        archive(key,"map")
    if not (PF/".tmp/scene-execute/shore-water.js").exists():
        conf=dict(prefabId=PREFAB,resourceId=key,bindings=[])
        skill("generate-map-assembly",["--config",json.dumps(conf),"--output","wprefabs/homeward-rain/.tmp/scene-execute/shore-water.js"])
if "steam" in sys.argv:
    key="effect-shore-steam"
    if not (PF/"assets/effects"/key).exists():
        print(skill("effect-template",["--prefab-id",PREFAB,"--resource-id",key,"--template-id","props-campfire"]))
if "models" in sys.argv:
    for folder in ("Harbor","Banks","Backdrop"):
        for src in sorted((ROUTE/folder).rglob("*.glb")):
            key="model-"+src.stem
            if key in uris: continue
            target=PF/"assets/models"/key
            if not target.exists():
                run("authoring","resource","model","import",key,"--prefab",PREFAB,"--glb",str(src),workspace=True)
            elif (target/"topology/model.glb").read_bytes()!=src.read_bytes():
                copy2(src,target/"topology/model.glb")
            out=run("authoring","resource","model","check",key,"--prefab",PREFAB,workspace=True)
            save(WORK/(key+".check.json"),out)
            archive(key,"model")
