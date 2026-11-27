"""Release supplied recordings against thread 04's saved scene."""
import json
import runpy
import shutil
import sys
from hashlib import sha256
from zipfile import ZipFile

import route_cli as cli


ROOT, WORK, PF, PROJECT = cli.ROOT, cli.WORK, cli.PF, cli.PROJECT
RAIN = ROOT / "RainStudy"
ASSETS = RAIN / "Audio/assets"
PREFAB = cli.PREFAB
EXPORT = RAIN / "Homeward-content-voice.wprefab"
TAKES = {"FamilyVoice": "audio-family-voice-recorded", "S07A": "audio-window-call-recorded"}
BASE = "1626286737"
PROFILE = "voice"
BASE_RECEIPT = "04-disk.json"
LABEL = "听见来处原声版"
REQUEST = "homeward04-recorded"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def record(name, data):
    cli.save(WORK / f"04-{PROFILE}-{name}.json", data)


def step(name, *args, workspace=False):
    out = cli.run(*args, workspace=workspace)
    record(name, out)
    print(name, out.get("status", ""), flush=True)
    return out


def archive_audio(resource):
    dest = PF / "assets/audio" / resource
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("meta.json", "audio.wav"):
        shutil.copy2(ASSETS / resource / name, dest / name)
    out = step(resource, "authoring", "resource", "archive", resource, "--kind", "audio",
               "--prefab", PREFAB, "--request-id", f"{REQUEST}-{resource}", workspace=True)
    meta = read(dest / "package/resource.json")
    assert out["status"] == "completed" and meta["uri"] == out["uri"]
    assert meta["contentHash"] == sha256((dest / "audio.wav").read_bytes()).hexdigest()
    return {"uri": out["uri"]}


def sync_scripts():
    previous = cli.ID
    sync = runpy.run_path(str(WORK / "04-release.py"))["sync_script"]
    cli.ID = previous
    sync("RainHost.lua", RAIN / "Audio/RainHost.lua", RAIN / "Runtime/locations.lua")
    sync("Postcard.lua", RAIN / "Card/RainCard.lua")


def install(old_root, attempt):
    author = ("authoring", "prefab")
    validation = step("validate", *author, "validate", PREFAB, workspace=True)
    assert not validation["result"]["items"] and not validation["warnings"], validation
    step("build", *author, "build", PREFAB, workspace=True)
    archive = step("archive", "authoring", "result", "archive", PREFAB,
                   "--name", LABEL, workspace=True)
    step("export", *author, "export", PREFAB, "--out", str(EXPORT), workspace=True)
    result = step("import", "scene", "import", "--uri", archive["uri"], "--position",
                  "119.74,78.85,88.64", "--request-id", f"{REQUEST}-import-{attempt}")
    assert result["status"] == "committed" and len(result["rootIDs"]) == 1, result
    removed = step("remove", "scene", "remove", old_root,
                   "--request-id", f"{REQUEST}-remove-{attempt}")
    assert removed["status"] == "committed", removed


def deploy():
    scene = PROJECT / "scene.data"
    assert sha256(scene.read_bytes()).hexdigest() == read(WORK / BASE_RECEIPT)["sceneSha256"]
    with ZipFile(scene) as saved:
        assert BASE.encode() in saved.read("SerializePcgData.json")
    status = step("base-runtime", "runtime", "status")
    assert status["status"] == "not_started", status
    located = step("locate", "project", "locate", PREFAB)
    assert any(m["workspaceId"] == cli.WSID and m["prefabRoot"] == str(PF) for m in located["matches"])
    shutil.copy2(scene, WORK / f"04-{PROFILE}-before.scene.data")
    takes = {key: archive_audio(resource) for key, resource in TAKES.items()}
    sync_scripts()
    author = ("authoring", "prefab")
    rev = step("revision", *author, "read", PREFAB, "context.capabilities", workspace=True)["revision"]
    edit = WORK / f"04-{PROFILE}-bind.js"
    edit.write_text("return await scene.scripts.setParams({"
                    "bindings:['n48:s:5ef17e0b-a118-4c30-ac36-1a2e7563b0c5'],values:"
                    + json.dumps(takes) + "});\n", encoding="utf-8")
    step("bound", *author, "execute", PREFAB, "--file", str(edit), "--revision", rev,
         "--request-id", f"{REQUEST}-bind", workspace=True)
    record("bindings", takes)
    install(BASE, "first")


def refresh():
    status = cli.run("runtime", "status")
    if status["status"] == "running":
        step("runtime-before-fix", "runtime", "stop", "--runtime-id", status["runtimeId"])
    old_root = read(WORK / f"04-{PROFILE}-import.json")["rootIDs"][0]
    sync_scripts()
    install(old_root, sys.argv[2])


def save():
    assert read(WORK / f"04-{PROFILE}-test.json")["passed"]
    status = cli.run("runtime", "status")
    assert status["status"] == "running", status
    runtime = ("--runtime-id", status["runtimeId"])
    step("hooks", "runtime", "verifyNoTempHooks", *runtime)
    step("runtime-stop", "runtime", "stop", *runtime)
    out = step("save", "scene", "save", "--request-id", f"{REQUEST}-save")
    if out.get("hasUnsavedChanges"):
        out = step("save-clean", "scene", "save", "--request-id", f"{REQUEST}-save-clean")
    assert out["status"] == "committed" and not out["hasUnsavedChanges"], out
    root = read(WORK / f"04-{PROFILE}-import.json")["rootIDs"][0]
    scene = PROJECT / "scene.data"
    with ZipFile(scene) as saved:
        tree = saved.read("SerializePcgData.json")
        assert saved.testzip() is None and root.encode() in tree and BASE.encode() not in tree
    with ZipFile(EXPORT) as package:
        assert package.testzip() is None
    record("disk", {"root": root, "sceneSha256": sha256(scene.read_bytes()).hexdigest(),
                    "exportSha256": sha256(EXPORT.read_bytes()).hexdigest()})
    bindings = RAIN / "Audio/bindings.json"
    cli.save(bindings, {**read(bindings), **read(WORK / f"04-{PROFILE}-bindings.json")})
    step("instance-stop", "instance", "stop")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--sfx" in sys.argv:
        PROFILE = "sfx"
        BASE_RECEIPT = "04-voice-disk.json"
        BASE = read(WORK / BASE_RECEIPT)["root"]
        LABEL = "听见来处声画更新"
        REQUEST = "homeward04-sfx"
        EXPORT = RAIN / "Homeward-content-sfx.wprefab"
        TAKES = {key: value[0] for key, value in runpy.run_path(str(WORK / "04-sfx-prep.py"))["TAKES"].items()}
    cli.ID = read(WORK / f"04-{PROFILE}-instance.json")["data"]["instanceId"]
    {"deploy": deploy, "refresh": refresh, "save": save}[sys.argv[1]]()
