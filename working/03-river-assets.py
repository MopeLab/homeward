from hashlib import sha256
from shutil import copy2
from route_cli import *

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

for model, folder, expected in [
    ("harbor-boat", "Harbor", "149034d66abd361707ff3bd44d9285123fc5ca55d65e73a73db27e7d04b051bf"),
    ("river-surface", "River", "7332f7079635bf76815b5c016cd7686c6b323896beaa0db9b2172186a6223a50"),
]:
    key = "model-" + model
    src = ROUTE / folder / (model + ".glb")
    dest = PF / "assets/models" / key / "topology/model.glb"
    assert digest(src) == expected
    if not dest.exists():
        run("authoring", "resource", "model", "import", key, "--prefab", PREFAB, "--glb", str(src), workspace=True)
    elif digest(dest) != expected:
        assert key == "model-harbor-boat" and digest(dest) == "35cd7af6b96bc72df9502d1cf4139946023394500c74a7f4cae02e46dc19f31a"
        copy2(src, dest)
    assert digest(dest) == expected
    check = run("authoring","resource","model","check",key,"--prefab",PREFAB,workspace=True)
    save(WORK / ("03-river-check-"+model+".json"),check)
    archive = run("authoring","resource","archive",key,"--kind","model","--prefab",PREFAB,"--request-id","03-river-final-"+model,workspace=True)
    assert archive["status"] == "completed", archive
    save(WORK / ("03-river-uri-"+model+".json"),archive)
    print(key, archive["uri"],flush=True)
