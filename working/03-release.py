from route_cli import *
from hashlib import sha256
from zipfile import ZipFile

def sync(name, sources):
    path=PF/"scripts"/name
    lines=path.read_text(encoding="utf-8-sig").splitlines()
    if not lines[0].startswith("---@id ") or lines[1]!="---@referenceName "+name: raise ValueError(name)
    path.write_text("\n".join(lines[:2]+[p.read_text(encoding="utf-8") for p in sources]),encoding="utf-8")

def receipt(name):
    return json.loads((WORK/name).read_text(encoding="utf-8"))

version=sys.argv[1]
def step(tag,*args,workspace=False):
    path=WORK/f"03-{version}-{tag}.json"
    if path.exists():return receipt(path.name)
    data=run(*args,workspace=workspace)
    save(path,data)
    print(tag,str(data)[:200],flush=True)
    return data

if "sync" in sys.argv:
    rain=ROOT/"RainStudy"
    sync("Postcard.lua",[rain/"Card/RainCard.lua"])
    sync("RainHost.lua",[rain/"Audio/RainHost.lua",rain/"Runtime/locations.lua"])
    sync("BakedColors.lua",[rain/"Scenery/BakedColors.lua"])
    sync("ShoreSteam.lua",[ROUTE/"Steam/ShoreSteam.lua"])
if "bind" in sys.argv:
    keys={**{k.lower():k for k in [f"S0{s}{beat}" for s in range(3,7) for beat in "AB"]},"market":"MarketBed","dusk":"DuskBed"}
    binds=json.loads((ROOT/"RainStudy/Audio/bindings.json").read_text(encoding="utf-8"))
    for name,uri in receipt("03-resource-uris.json").items():binds[keys[name.removeprefix("audio-route-")]]={"uri":uri}
    a=receipt("03-shore-assembly.json")["result"]
    uri=json.loads((PF/"assets/effects/effect-shore-steam/package/resource.json").read_text(encoding="utf-8-sig"))["uri"]
    body="await scene.scripts.setParams({bindings:['n48:s:5ef17e0b-a118-4c30-ac36-1a2e7563b0c5'],values:"+json.dumps(binds)+"});\n"
    body+="return await scene.scripts.bind("+json.dumps(dict(nodes=["n48"],script=a["steam"]["handle"],params={"Steam":{"uri":uri}}))+");"
    filename=WORK/"03-bind-shores.js"
    filename.write_text(body,encoding="utf-8")
    rev=run("authoring","prefab","read",PREFAB,"context.capabilities",workspace=True)["revision"]
    step("bound","authoring","prefab","execute",PREFAB,"--file",str(filename),"--request-id","03-"+version+"-bindings","--revision",rev,workspace=True)
if "build" in sys.argv:
    v=step("validate","authoring","prefab","validate",PREFAB,workspace=True)
    b=step("build","authoring","prefab","build",PREFAB,workspace=True)
    out=step("archive","authoring","result","archive",PREFAB,"--name","听见来处两岸航线",workspace=True)
if "export" in sys.argv:
    step("export","authoring","prefab","export",PREFAB,"--out",str(ROOT/"RainStudy/Homeward-shores.wprefab"),workspace=True)
if "deploy" in sys.argv:
    old=sys.argv[sys.argv.index("deploy")+1]
    # The first test replaces the shared 02 root; its saved scene and editable package are backed up.
    if old=="1978400842":
        snapshot=WORK/"03-before-shores.scene.data"
        assert sha256(snapshot.read_bytes()).digest()==sha256((PROJECT/"scene.data").read_bytes()).digest()
    archive=receipt("03-"+version+"-archive.json")
    uri=archive.get("uri") or archive["results"][0]["uri"]
    step("import","scene","import","--uri",uri,"--position","119.74,78.85,88.64","--request-id","03-"+version+"-import")
    step("remove","scene","remove",old,"--request-id","03-"+version+"-remove")
    if "save" in sys.argv:
        saved=step("save","scene","save","--request-id","03-"+version+"-save")
        if saved.get("hasUnsavedChanges") is True:
            saved=step("save-clean","scene","save","--request-id","03-"+version+"-save-clean")
        assert saved["status"]=="committed" and saved.get("hasUnsavedChanges") is False,saved
    else:
        started=step("runtime","runtime","start","--wait","60")
        print(started["runtimeId"])
