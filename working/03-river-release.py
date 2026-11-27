from route_cli import *
from hashlib import sha256
from zipfile import ZipFile

version = os.environ.get("RIVER_VERSION", "river1")
scene = PROJECT / "scene.data"
ripples=version.startswith("ripples")
export = ROOT / ("RainStudy/Homeward-ripples.wprefab" if ripples else "RainStudy/Homeward-river.wprefab")
def receipt(name):
    return json.loads((WORK / name).read_text(encoding="utf-8-sig"))
def step(name,*args,workspace=False):
    path = WORK / f"03-{version}-{name}.json"
    if path.exists(): return receipt(path.name)
    out = run(*args,workspace=workspace)
    save(path,out)
    print(name,str(out)[:210],flush=True)
    return out

def sync(name,*sources):
    dest=PF/"scripts"/name
    lines=dest.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].startswith("---@id ") and lines[1]=="---@referenceName "+name
    dest.write_text("\n".join(lines[:2]+[(ROOT/"RainStudy"/p).read_text(encoding="utf-8") for p in sources]),encoding="utf-8")

if "assemble" in sys.argv:
    boat=receipt("03-river-uri-harbor-boat.json")["uri"]
    water=receipt("03-river-uri-river-surface.json")["uri"]
    assert boat!=receipt("03-visual-uris.json")["model-harbor-boat"]
    js=WORK/"03-river-assembly.js"
    js.write_text("const boatUri="+json.dumps(boat)+", waterUri="+json.dumps(water)+";\n"+(ROUTE/"River/install-river.js").read_text(encoding="utf-8"),encoding="utf-8")
    rev=run("authoring","prefab","read",PREFAB,"context.capabilities",workspace=True)["revision"]
    step("assembly","authoring","prefab","execute",PREFAB,"--file",str(js),"--request-id","homeward03-river-assembly-v1","--revision",rev,workspace=True)
if "build" in sys.argv:
    sync("RainHost.lua","Audio/RainHost.lua","Runtime/locations.lua")
    sync("BakedColors.lua","Scenery/BakedColors.lua","ShoreRoute/River/river-display.lua")
    validate=step("validate","authoring","prefab","validate",PREFAB,workspace=True)
    assert not validate["result"]["items"] and not validate["warnings"],validate
    step("build","authoring","prefab","build",PREFAB,workspace=True)
    step("archive","authoring","result","archive",PREFAB,"--name","听见来处 · 修订水岸",workspace=True)
    step("export","authoring","prefab","export",PREFAB,"--out",str(export),workspace=True)
    with ZipFile(export) as z: assert z.testzip() is None
if "install" in sys.argv:
    base=receipt("03-river-disk.json" if ripples else "04-sfx-disk.json")
    assert sha256(scene.read_bytes()).hexdigest()==base["sceneSha256"]
    assert run("runtime","status")["status"]=="not_started"
    imported=step("import","scene","import","--uri",receipt("03-"+version+"-archive.json")["uri"],"--position","119.74,78.85,88.64","--request-id","03-"+version+"-import")
    assert imported["status"]=="committed" and len(imported["rootIDs"])==1
    old=sys.argv[sys.argv.index("install")+1]
    removed=step("remove","scene","remove",old,"--request-id","03-"+version+"-remove")
    assert removed["status"]=="committed"
if "test" in sys.argv:
    print(step("runtime","runtime","start","--wait","60")["runtimeId"])
if "save" in sys.argv:
    status=run("runtime","status")
    if status["status"]=="running":
        runtime=("--runtime-id",status["runtimeId"])
        step("hooks","runtime","verifyNoTempHooks",*runtime)
        step("stop","runtime","stop",*runtime)
    backup="03-before-ripples.scene.data" if ripples else "03-before-river-04.scene.data"
    assert sha256(scene.read_bytes()).digest()==sha256((WORK/backup).read_bytes()).digest()
    r=step("save","scene","save","--request-id","03-"+version+"-save")
    if r.get("hasUnsavedChanges"): r=step("save-clean","scene","save","--request-id","03-"+version+"-save-clean")
    assert r["status"]=="committed" and r["hasUnsavedChanges"] is False
    root=receipt("03-"+version+"-import.json")["rootIDs"][0]
    with ZipFile(scene) as z:
        tree=z.read("SerializePcgData.json")
        previous=receipt("03-river-disk.json")["root"] if ripples else "1472798171"
        assert z.testzip() is None and root.encode() in tree and previous.encode() not in tree
    save(WORK/("03-ripples-disk.json" if ripples else "03-river-disk.json"),dict(root=root,sceneSha256=sha256(scene.read_bytes()).hexdigest(),exportSha256=sha256(export.read_bytes()).hexdigest()))
