"""Capture stills from the saved Homeward project with the public Creator CLI."""
import argparse
import runpy
import sys
import time
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK))
import route_cli as cli

voyage = runpy.run_path(str(WORK / "03-playtest.py"))
water = runpy.run_path(str(WORK / "03-water-playtest.py"))
NAMES, PORTS = voyage["NAMES"], voyage["PORTS"]
water["game"]["TITLES"].update(S01A="棚上碎雨", S03B="卷门顿住")


class Capture(water["WaterRun"]):
    def __init__(self, runtime):
        self.runtime = runtime
        self.output = Path(__file__).resolve().parent / "stills"
        self.output.mkdir(exist_ok=True)
        self.progress = {"clips": {}}
        self.progress_path = self.output / f"{runtime}-clips.json"
        self.stage = "submission-stills"
        self.controls_js = (voyage["INTERACTION"] / "controls.js").read_text(encoding="utf-8")

    def photo(self, name, yaw=None, pitch=None):
        if yaw is not None:
            self.journal(name, self.position_view(yaw, pitch))
        self.shot(name)
        print(name, flush=True)


def solo(t):
    t.walk([(0, 2.3)], NAMES["S01"])
    t.photo("01-campus")
    t.listen("S01B")
    t.walk([(0, 5.5)], NAMES["S02"])
    t.photo("02-eaves")
    t.walk([(0, 10.5), (0, 15)], PORTS["bow"])
    t.audition("listenBtn", "← 听早市", "market")
    t.photo("03-bow")
    t.confirm("market")
    t.photo("04-market-water", 85, 15)
    t.walk([(-11, 25.4)], NAMES["S03"])
    t.listen("S03B")
    t.photo("05-market-shutter", 0, 12)
    t.walk([(-11, 30.5)], NAMES["S04"])
    t.photo("06-market-stall", 0, 14)
    t.walk([(-11, 20.5)], PORTS["market"])
    t.audition("listenBtn", "听暮路", "dusk")
    t.confirm("dusk")
    t.go(11, 17.12)
    t.js("CS.DouyinCameraService.SetDistance(5.0);return true;")
    t.photo("07-dusk-water", 67, 63)
    t.walk([(11, 25.4)], NAMES["S05"])
    t.photo("08-dusk-bicycle", 0, 14)
    t.walk([(11, 30.5)], NAMES["S06"])
    t.listen("S06B")
    t.photo("09-dusk-door", 0, 14)
    t.walk([(11, 20.5)], PORTS["dusk"])
    t.home()
    t.walk([(.35, 8.8)], NAMES["S07"])
    state = t.at(NAMES["S07"])
    t.tap("listenBtn", state=state)
    t.tap_point(state["coords"]["keepBtn"], "室友招呼")
    t.tap("slot2")
    feedback = t.view("确认换声前")
    t.progress["clips"]["S07A"] = feedback["channels"]["Card"]["clip"]
    t.tap("stampBtn", "确认替换")
    t.tap("swapBtn", "交换两格")
    t.tap("slot2")
    t.tap("slot3")
    t.tap("closeBtn")
    t.walk([(0, 8)], PORTS["desk"])
    t.seal("10-solo-postcard", ["S01B", "S06B", "S07A"])
    print("10-solo-postcard", flush=True)


def pair(t):
    t.walk([(0, 2.3)], NAMES["S01"])
    t.listen("S01A")
    t.listen("S01B")
    t.walk([(0, 8)], PORTS["desk"])
    t.tap("listenBtn", "合写一封")
    t.tap("slot2")
    t.tap("stampBtn", "选好，递给乙")
    t.walk([(0, 5.5)], NAMES["S02"])
    state = t.at(NAMES["S02"])
    t.tap("listenBtn", state=state)
    t.tap("listenBtn", "听落点")
    t.tap("keepBtn", "收下落点")
    t.progress["clips"]["S02B"] = t.view("收下乙的声音")["channels"]["Card"]["clip"]
    t.walk([(0, 8)], PORTS["desk"])
    t.tap("cardEntryBtn", "乙的声音 · 1/3")
    t.tap("slot1")
    t.tap("stampBtn", "放入第二格")
    t.tap("swapBtn", "换甲来提议")
    t.tap("slot1")
    t.tap("stampBtn", "提议这拍")
    t.photo("11-pair-before-stamp")
    t.tap("swapBtn", "按章合寄")
    t.replay("12-pair-postcard", ["S01B", "S02B", "S01A"])
    print("12-pair-postcard", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance")
    parser.add_argument("runtime")
    args = parser.parse_args()
    cli.ID = args.instance
    cli.run("runtime", "stop", "--runtime-id", args.runtime)
    runtime = cli.run("runtime", "start", "--wait", "55")["runtimeId"]
    print(f"solo runtime {runtime}", flush=True)
    for shoot in (solo, pair):
        try:
            shoot(Capture(runtime))
        finally:
            check = cli.run("runtime", "verifyNoTempHooks", "--runtime-id", runtime)
            cli.save(WORK / "06" / "stills" / f"{runtime}-hooks.json", check)
        if shoot is solo:
            cli.run("runtime", "stop", "--runtime-id", runtime)
            runtime = cli.run("runtime", "start", "--wait", "55")["runtimeId"]
            print(f"pair runtime {runtime}", flush=True)
