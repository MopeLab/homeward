"""Use the installed public CLI without cmd.exe reinterpreting JSON arguments."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "working"
ROUTE = ROOT / "RainStudy/ShoreRoute"
EDITOR = Path(os.environ["LOCALAPPDATA"]) / "Programs/造世界编辑器"
PROJECT = Path(os.environ["APPDATA"]) / "AI World Creator/projects/project-268b3d7f-1770-4720-8617-933ab1a1fe14"
WSID = "workspace_7y98mqge"
WS = PROJECT / "ai-sessions" / WSID
PREFAB = "homeward-rain"
PF = WS / "wprefabs" / PREFAB
ID = (WORK / "03-instance.txt").read_text(encoding="utf-8-sig").strip()


def save(path, data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def run(*args, workspace=False):
    cmd = [EDITOR/"造世界编辑器.exe",EDITOR/"resources/addon/awc-cli/bin/douyin-world.mjs","--instance",ID]
    if workspace:
        cmd.extend(["--workspace-id",WSID])
    p = subprocess.run([*cmd,*args,"--json"], env={**os.environ,"ELECTRON_RUN_AS_NODE":"1"},
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",errors="replace")
    if p.returncode:
        raise RuntimeError(f"{args}: {p.stdout[-2000:]} {p.stderr[-1200:]}")
    msg=json.loads(p.stdout)
    if msg.get("ok") is False:
        raise RuntimeError(str(msg))
    return msg.get("data",msg)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(run(*sys.argv[1:]),ensure_ascii=False,indent=2))
