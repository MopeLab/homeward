"""Stage and release the thread 04 content through the installed public CLI."""
import json
import shutil
import sys
from hashlib import sha256

import route_cli as cli


ROOT, WORK, PF, WS, PROJECT = cli.ROOT, cli.WORK, cli.PF, cli.WS, cli.PROJECT
PREFAB = cli.PREFAB
RAIN = ROOT / "Game"
UI = PF / "assets/uis/ui-homeward-card"
CARD = RAIN / "Card/ui-homeward-card"
SOUNDS = {
    "S03A": "audio-shutter-chain", "S03B": "audio-shutter-stop",
    "S04A": "audio-steamer-lid", "S04B": "audio-steamer-steam",
    "S05A": "audio-bell-double", "S05B": "audio-bell-tail",
    "S06A": "audio-lock-keys", "S06B": "audio-lock-open",
    "MarketBed": "audio-market-bed", "DuskBed": "audio-dusk-bed",
    "Postmark": "audio-postmark",
}
SKETCHES = ("shutterSketch", "steamerSketch", "bellSketch", "lockSketch")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


cli.ID = read(WORK / "04-instance-start.json")["data"]["instanceId"]


def step(name, *args, workspace=False):
    data = cli.run(*args, workspace=workspace)
    print(name, data.get("status", data.get("revision", "")), flush=True)
    cli.save(WORK / f"04-{name}.json", data)
    return data


def sync_script(name, *files):
    target = PF / "scripts" / name
    lines = target.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].startswith("---@id ") and lines[1] == "---@referenceName " + name
    target.write_text("\n".join(lines[:2] + [path.read_text(encoding="utf-8") for path in files]),
                      encoding="utf-8")


def stage():
    snapshot = WORK / "04-before-content.scene.data"
    assert sha256((PROJECT / "scene.data").read_bytes()).hexdigest() == (
        "25672a75349d7238bc8f1c6229f2fc62142d6bcef1ede6b928cf4b7783b864f3"
    )
    shutil.copy2(PROJECT / "scene.data", snapshot)
    request = read(WORK / "04-atlas-request.json")["data"]["imageRequirements"][0]
    assert (request["expected"]["width"], request["expected"]["height"]) == (640, 640)
    png = WS / "homeward04-shore-atlas.png"
    manifest = WS / "homeward04-shore-supply.json"
    shutil.copy2(WORK / "04-shore-supply.png", png)
    cli.save(manifest, {"version": 1, "images": [{"fingerprint": request["fingerprint"],
                                                  "pngPath": png.name}]})
    cli.save(RAIN / "Card/shore-atlas-supply.json",
             {"version": 1, "images": [{"fingerprint": request["fingerprint"],
                                        "pngPath": "shore-sketch-atlas-640.png"}]})
    shutil.copy2(png, RAIN / "Card/shore-sketch-atlas-640.png")
    step("atlas", "authoring", "skill", "run", "generate-ui-png-atlas",
         "--workspace", str(WS), "--argv-file", str(RAIN / "Card/shore-atlas-arguments.json"),
         "--image-supply", manifest.name)
    for name in SKETCHES:
        shutil.copy2(UI / "images" / (name + ".png"), CARD / "images" / (name + ".png"))
    for path in (CARD / "html").glob("*.html"):
        shutil.copy2(path, UI / "html" / path.name)
    for resource in SOUNDS.values():
        source = RAIN / "Audio/assets" / resource
        target = PF / "assets/audio" / resource
        target.mkdir(parents=True, exist_ok=True)
        for name in ("meta.json", "audio.wav"):
            shutil.copy2(source / name, target / name)
    sync_script("Postcard.lua", RAIN / "Card/RainCard.lua")
    sync_script("RainHost.lua", RAIN / "Audio/RainHost.lua", RAIN / "Runtime/locations.lua")


def archive_resources():
    step("ui-check", "authoring", "resource", "ui", "check", "ui-homeward-card",
         "--prefab", PREFAB, workspace=True)
    archive_resource("ui-homeward-card", "ui")
    for resource in SOUNDS.values():
        archive_resource(resource, "audio")


def archive_resource(resource, kind):
    receipt = WORK / f"04-{resource}.json"
    if receipt.exists() and read(receipt).get("status") == "completed":
        data = read(receipt)
    else:
        data = step(resource, "authoring", "resource", "archive", resource, "--kind", kind,
                    "--prefab", PREFAB, "--request-id", f"homeward04-{resource}", workspace=True)
    assert data["status"] == "completed" and data["uri"], data
    if kind == "audio":
        archived = read(PF / "assets/audio" / resource / "package/resource.json")
        assert archived["uri"] == data["uri"], archived
        assert archived["contentHash"] == sha256(
            (RAIN / "Audio/assets" / resource / "audio.wav").read_bytes()).hexdigest(), archived


def bind():
    for name in ("components.set", "scripts.setParams"):
        step(name, "authoring", "prefab", "read", PREFAB, "context.describe", "--args",
             json.dumps([name]), workspace=True)
    result = step("ui-current", "authoring", "prefab", "read", PREFAB, "nodes.query",
                  "--args", '[{"subtree":"n48"},{"fields":["name"],"limit":2}]', workspace=True)
    assert any(n["name"] == "ui-homeward-card" for n in result["result"]["items"]), result
    bindings = read(RAIN / "Audio/bindings.json")
    bindings.update({key: {"uri": read(WORK / f"04-{value}.json")["uri"]}
                     for key, value in SOUNDS.items()})
    ui_uri = read(WORK / "04-ui-homeward-card.json")["uri"]
    edit = WORK / "04-bind.js"
    edit.write_text(
        "await scene.components.set({nodes:['n48'],type:'aigcModelData',values:"
        + json.dumps({"meshRefId": ui_uri}) + "});\n"
        + "await scene.scripts.setParams({bindings:['n48:s:5ef17e0b-a118-4c30-ac36-1a2e7563b0c5'],values:"
        + json.dumps(bindings) + "});\n"
        + "return await scene.document.validate();\n", encoding="utf-8")
    revision = step("revision", "authoring", "prefab", "read", PREFAB, "context.capabilities",
                    workspace=True)["revision"]
    step("bound", "authoring", "prefab", "execute", PREFAB, "--revision", str(revision),
         "--file", str(edit), "--request-id", "homeward04-content-binding", workspace=True)
    cli.save(RAIN / "Audio/bindings.json", bindings)


def package():
    step("validate", "authoring", "prefab", "validate", PREFAB, workspace=True)
    step("build", "authoring", "prefab", "build", PREFAB, workspace=True)
    step("archive", "authoring", "result", "archive", PREFAB, "--name", "听见来处七组声画",
         workspace=True)
    step("export", "authoring", "prefab", "export", PREFAB, "--out",
         str(RAIN / "Homeward-content.wprefab"), workspace=True)


def deploy():
    from zipfile import ZipFile

    scene_file = PROJECT / "scene.data"
    assert scene_file.read_bytes() == (WORK / "04-before-content.scene.data").read_bytes()
    with ZipFile(scene_file) as archive:
        assert b"-1615574970" in archive.read("SerializePcgData.json")
    archived = read(WORK / "04-archive.json")
    uri = archived.get("uri") or archived["results"][0]["uri"]
    data = step("import", "scene", "import", "--uri", uri, "--position", "119.74,78.85,88.64",
                "--request-id", "homeward04-content-import")
    assert data["status"] == "committed" and len(data["rootIDs"]) == 1, data
    data = step("remove", "scene", "remove", "-1615574970", "--request-id", "homeward04-remove-v3")
    assert data["status"] == "committed", data
    step("runtime", "runtime", "start", "--wait", "60")


def finish():
    from zipfile import ZipFile

    runtime = step("runtime-current", "runtime", "status")
    assert runtime["status"] == "running", runtime
    step("hooks", "runtime", "verifyNoTempHooks", "--runtime-id", runtime["runtimeId"])
    step("runtime-stop", "runtime", "stop", "--runtime-id", runtime["runtimeId"])
    saved = step("save", "scene", "save", "--request-id", "homeward04-content-save")
    if saved.get("hasUnsavedChanges"):
        saved = step("save-clean", "scene", "save", "--request-id", "homeward04-content-save-clean")
    assert saved["status"] == "committed" and not saved["hasUnsavedChanges"], saved
    root = read(WORK / "04-import.json")["rootIDs"][0]
    current = PROJECT / "scene.data"
    with ZipFile(current) as archive:
        assert archive.testzip() is None
        tree = archive.read("SerializePcgData.json")
        assert root.encode() in tree and b"-1615574970" not in tree
    export = RAIN / "Homeward-content.wprefab"
    with ZipFile(export) as archive:
        assert archive.testzip() is None
    cli.save(WORK / "04-disk.json", {
        "root": root, "sceneSha256": sha256(current.read_bytes()).hexdigest(),
        "exportSha256": sha256(export.read_bytes()).hexdigest(),
    })
    step("cover", "project", "cover", str(RAIN / "Cover/Homeward-cover.jpg"))


def reopen():
    cli.ID = read(WORK / "04-reopen-instance.json")["data"]["instanceId"]
    try:
        started = step("reopened", "runtime", "start", "--wait", "60")
        runtime = ("--runtime-id", started["runtimeId"])
        script = (WORK / "04-reopen.js").read_text(encoding="utf-8")
        result = step("opening", "runtime", "js", "eval", script, "--timeout-ms", "14000", *runtime)
        sampled = result["result"]
        assert len(sampled["artworks"]) == 21 and all(art[1] for art in sampled["artworks"]), sampled
        voice = [s["cursor"] for s in sampled["samples"] if s["playing"] and abs(s["length"] - 4.618) < .02
                 and "刚把窗关上" in s["subtitle"]]
        assert len(voice) > 1 and max(voice) > min(voice), sampled
        step("reopened-hooks", "runtime", "verifyNoTempHooks", *runtime)
    finally:
        state = cli.run("runtime", "status")
        if state["status"] == "running":
            step("reopened-stop", "runtime", "stop", "--runtime-id", state["runtimeId"])
        step("reopened-instance-stop", "instance", "stop")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for action in sys.argv[1:]:
        {"stage": stage, "resources": archive_resources, "bind": bind, "package": package,
         "deploy": deploy, "finish": finish, "reopen": reopen}[action]()
