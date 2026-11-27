from route_cli import *
def read(name):
    return json.loads((WORK/name).read_text(encoding="utf-8"))
def execute(js,tag,revision):
    path=WORK/("03-"+tag+".js")
    path.write_text(js,encoding="utf-8")
    result=run("authoring","prefab","execute",PREFAB,"--file",str(path),"--revision",revision,"--request-id","homeward03-"+tag,workspace=True)
    save(WORK/("03-"+tag+".json"),result)
    return result
if __name__=="__main__":
    rev=run("authoring","prefab","read",PREFAB,"context.capabilities",workspace=True)["revision"]
    src=(ROUTE/"install-shores.js").read_text(encoding="utf-8")
    water=read("03-water-assembly.json")["result"]["root"]
    # Confirm the saved target still contains the water and no boats.
    existing=run("authoring","prefab","read",PREFAB,"nodes.query","--args",json.dumps([{"subtree":"n9"},{"fields":["name"],"limit":100}]),workspace=True)
    if any(item["name"]=="CentralBoat" for item in existing["result"]["items"]):
        raise RuntimeError("Boat is already installed; inspect receipts before further edits.")
    r=execute("const waterRoot="+json.dumps(water)+";\nconst uris="+json.dumps(read("03-visual-uris.json"))+";\n"+src,"shore-assembly",rev)
    print(r["summary"],r["result"]["steam"])
