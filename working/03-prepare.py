from route_cli import *
from shutil import copy2, copytree

receipt=WORK/"03-resource-uris.json"
uris=json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
for src in sorted((ROUTE/"audio").iterdir()):
    name=src.name
    if name in uris:
        continue
    target=PF/"assets/audio"/name
    if not target.exists():
        copytree(src,target)
    for filename in ("meta.json","audio.wav"):
        if (src/filename).read_bytes() != (target/filename).read_bytes():
            raise ValueError(f"conflicting source {target/filename}")
    data=run("authoring","resource","archive",name,"--kind","audio","--prefab",PREFAB,workspace=True)
    if data["status"]!="completed": raise RuntimeError(str(data))
    uris[name]=data["uri"]
    save(receipt,uris)
    print(name,flush=True)
