"""Thread 05 acceptance using the saved project's native desktop preview."""
import argparse
import json
import runpy
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import route_cli as cli

voyage = runpy.run_path(str(HERE / "03-playtest.py"))
NAMES, PORTS = voyage["NAMES"], voyage["PORTS"]
TITLES = dict(voyage["TITLES"], S01A="棚上碎雨", S02A="碗中雨滴", S03B="卷门顿住")
ART = dict(zip(NAMES, ["Tin", "Basin", "Shutter", "Steamer", "Bell", "Lock", "Window"]))
SOURCES = {f"S{i:02}{beat}" for i in range(1, 8) for beat in "AB"}


class Acceptance(voyage["VoyageTest"]):
    def __init__(self, runtime):
        self.runtime = runtime
        self.output = Path(__file__).resolve().parent / "runs" / runtime
        self.output.mkdir(parents=True, exist_ok=True)
        self.progress_path = self.output / "progress.json"
        self.progress = (json.loads(self.progress_path.read_text(encoding="utf-8"))
                         if self.progress_path.exists() else {})
        self.controls_js = (voyage["INTERACTION"] / "controls.js").read_text(encoding="utf-8").replace(
            '"paperWakeBtn"]', '"paperWakeBtn","quieterBtn","rainBtn","playBtn"]')
        self.stage = "bindings"
        keys = sorted(SOURCES | {"FamilyVoice", "BasinAccent", "RainBed", "DuskBed", "MarketBed", "Postmark"})
        expr = "return {" + ",".join(k + "={" + k + ":GetInstanceID()," + k + ".length}" for k in keys) + "}"
        self.assets = self.runtime_call("lua", "eval", expr, "--script", "RainHost.lua")["result"]
        cli.save(self.output / "bindings.json", self.assets)
        assert len(set(row[0] for row in self.assets.values())) == len(keys)
        assert abs(self.assets["S02A"][1] - 19.09) < .02
        assert abs(self.assets["FamilyVoice"][1] - 3.317551) < .02
        assert abs(self.assets["S07A"][1] - 1.802449) < .02

    def clock(self, event):
        self.progress[event] = time.time()
        cli.save(self.progress_path, self.progress)

    def labels(self, **expected):
        actual = self.view("核对界面")["labels"]
        assert all(actual.get(k) == v for k, v in expected.items()), (expected, actual)

    def collect(self, key, *, full=False, muted=False):
        state = self.at(NAMES[key[:3]])
        self.tap("listenBtn", state=state)
        if key.endswith("B"):
            if key == "S02B":
                self.tap("listenBtn", "听落点")
            else:
                time.sleep(self.assets[key[:3] + "A"][1] + .24)
            self.tap("keepBtn", "收下落点")
        else:
            self.tap_point(state["coords"]["keepBtn"], "收下 " + key)
        state = self.view("已采 " + key)
        line = "feedbackLine" if full else "walkCaption"
        assert TITLES[key] in state["labels"][line], state
        if not muted:
            assert state["channels"]["Card"]["clip"] == self.assets[key][0], state
        else:
            self.quiet(state)

    def quiet(self, state):
        assert all(not c["playing"] or c["gain"] == 0 for c in state["channels"].values()), state

    def mix(self, clicks, mute=False):
        self.tap("cardEntryBtn")
        self.tap("soundBtn")
        if mute:
            self.tap("rainBtn")
        for _ in range(clicks):
            self.tap("quieterBtn")
        self.labels(feedbackLine="音量 " + ("0%" if mute else "20%"))
        self.tap("closeBtn")
        self.tap("closeBtn")

    def playback(self, tag, keys, *, muted=False, final=True):
        # Read the real source, captions and artwork throughout the sequence.
        probe = (voyage["INTERACTION"] / "replay.js").read_text(encoding="utf-8")
        probe = probe.replace("for(let frame=0;frame<500;frame++)",
                              "const deadline=U.Time.realtimeSinceStartup+36; while(U.Time.realtimeSinceStartup<deadline)")
        if not final:
            probe = probe.replace("if(!feedback.gameObject", 'if(feedback.text==="这一封，听完了。") break;\n  if(!feedback.gameObject')
        rows = self.js(probe, 45000)
        cli.save(self.output / (tag + ".json"), rows)
        for i, key in enumerate(keys, 1):
            expected = [[ART[k[:3]]] if j < i else [] for j, k in enumerate(keys)]
            expected += [[] for _ in range(3-len(expected))]
            assert any(r["clip"] == (None if muted else self.assets[key][0])
                       and f"第 {i} 格 · {TITLES[key]}" in r["title"] and r["artwork"] == expected
                       for r in rows), (tag, key, rows)
        if final:
            assert "paperWakeBtn" in self.view(tag)["controls"]
            self.shot(tag)

    def dock(self, bank):
        self.walk([((-11 if bank == "market" else 11),20.5)], PORTS[bank])


def solo(t):
    t.clock("start")
    t.mix(3)
    t.walk([(0,2.3)], NAMES["S01"])
    t.collect("S01A")
    t.clock("first")
    t.collect("S01B")
    t.tap("cardEntryBtn")
    t.tap("playBtn")
    t.playback("两格连播", ["S01A","S01B"], final=False)
    t.clock("two")
    t.tap("closeBtn")
    t.walk([(0,10.5),(0,15)], PORTS["bow"])
    t.audition("keepBtn", "听暮路 →", "dusk")
    t.audition("listenBtn", "← 听早市", "market")
    t.confirm("market")
    t.walk([(-11,25.4)], NAMES["S03"])
    t.tap("listenBtn")
    t.dock("market")
    t.audition("listenBtn","听暮路","dusk")
    t.confirm("dusk")
    t.home()
    t.walk([(0,8)], PORTS["desk"])
    t.tap("cardEntryBtn", "坐到回信桌")
    t.tap("stampBtn")
    t.labels(feedbackLine="还差 1 格。收起明信片，再去听听。")
    t.tap("closeBtn")
    t.tap("keepBtn", "再去听听")
    t.arrive("bow")
    t.audition("keepBtn","听暮路 →","dusk")
    t.confirm("dusk")
    t.walk([(11,30.5)], NAMES["S06"])
    t.collect("S06B")
    t.dock("dusk")
    t.home()
    t.walk([(.35,8.8)], NAMES["S07"])
    t.collect("S07A", full=True)
    t.tap("slot1")
    state = t.view("替换预听")
    assert state["channels"]["Card"]["clip"] == t.assets["S07A"][0]
    assert "棚上碎雨" == state["labels"]["slot1Title"]
    t.tap("stampBtn","确认替换")
    t.tap("swapBtn","交换两格")
    t.tap("slot1")
    t.tap("slot3")
    keys = ["S06B","S01B","S07A"]
    t.labels(**{f"slot{i}Title":TITLES[k] for i,k in enumerate(keys,1)})
    t.tap("closeBtn")
    t.walk([(0,8)], PORTS["desk"])
    t.tap("cardEntryBtn")
    t.tap("stampBtn","盖章寄出")
    t.playback("低音量盖章",keys)
    t.clock("finish")
    t.tap("postmarkBtn")
    t.tap("closeBtn")
    skipped = t.view("跳到卡面")
    assert "paperWakeBtn" in skipped["controls"] and not skipped["channels"]["Card"]["playing"]
    t.tap("postmarkBtn")
    t.playback("邮戳重播",keys)
    t.tap("slot3")
    single = t.view("室友单格重听")
    assert single["channels"]["Card"]["clip"] == t.assets["S07A"][0] and "室友" in single["labels"]["feedbackLine"]
    t.tap("stampBtn","再写一封")


def silent(t):
    # Called immediately after the low-volume letter; the mix is still 20%.
    t.mix(2, mute=True)
    t.walk([(0,2.3)], NAMES["S01"])
    t.collect("S01B", muted=True)
    t.walk([(0,10.5),(0,15)], PORTS["bow"])
    t.tap("listenBtn","← 听早市")
    t.tap("cardEntryBtn","靠岸 · 早市")
    time.sleep(1.7)
    t.quiet(t.at(PORTS["market"]))
    t.walk([(-11,25.4)], NAMES["S03"])
    t.collect("S03B", muted=True)
    t.dock("market")
    t.tap("listenBtn","听暮路")
    t.tap("cardEntryBtn","靠岸 · 放学路")
    time.sleep(1.7)
    t.quiet(t.at(PORTS["dusk"]))
    t.walk([(11,30.5)], NAMES["S06"])
    t.collect("S06B", muted=True)
    t.dock("dusk")
    t.home()
    t.walk([(0,8)], PORTS["desk"])
    t.tap("cardEntryBtn")
    t.tap("stampBtn","盖章寄出")
    t.playback("静音两岸旧声卡", ["S01B","S03B","S06B"], muted=True)


def pair(t):
    t.walk([(0,2.3)], NAMES["S01"])
    t.collect("S01A")
    t.collect("S01B")
    t.walk([(0,8)],PORTS["desk"])
    t.tap("listenBtn","合写一封")
    t.tap("slot2")
    t.tap("closeBtn")
    t.labels(slot1Title="棚上碎雨", slot2Title="铁皮重滴")
    t.tap("closeBtn")
    t.tap("listenBtn","合写一封")
    t.tap("slot2")
    t.tap("stampBtn","选好，递给乙")
    t.labels(cardEntryBtnLabel="乙的声音 · 0/3")
    t.walk([(0,5.5)], NAMES["S02"])
    t.collect("S02B")
    t.walk([(0,8)],PORTS["desk"])
    t.tap("cardEntryBtn","乙的声音 · 1/3")
    t.tap("slot1")
    t.tap("stampBtn","放入第二格")
    t.tap("swapBtn","换甲来提议")
    t.tap("slot1")
    t.tap("stampBtn","提议这拍")
    state=t.view("乙确认甲的提议")
    assert state["labels"]["postmarkLabel"] == "等乙按章"
    t.tap("swapBtn","按章合寄",state)
    t.tap_point(state["controls"]["swapBtn"], "原位重复按章")
    keys=["S01B","S02B","S01A"]
    t.playback("双章合写",keys)
    t.labels(mailHeading="我们合寄的一封信",slot1Title="◇ 铁皮重滴",slot2Title="○ 迟来一滴",slot3Title="◇ 棚上碎雨")
    t.tap("postmarkBtn")
    t.playback("合写邮戳重听",keys)
    t.tap("paperWakeBtn")
    t.tap("stampBtn","回到个人草稿")
    t.labels(slot1Title="棚上碎雨",slot2Title="铁皮重滴",slot3Title="待收一声")
    t.tap("closeBtn")
    t.tap("keepBtn","上封合写")
    t.labels(slot2Title="○ 迟来一滴")
    t.tap("closeBtn")
    t.tap("closeBtn")
    t.tap("listenBtn","合写一封")
    t.tap("slot1")
    t.tap("stampBtn","选好，递给乙")
    t.tap("cardEntryBtn","乙的声音 · 0/3")
    t.labels(slot1Title="待收一声")
    t.tap("closeBtn")
    t.labels(slot2Title="铁皮重滴")


def tour(t):
    """Audition both beats of all seven objects and compare two arrangements at the desk."""
    observed = {}
    source_probe = (HERE / "04-observe-audio.js").read_text(encoding="utf-8")
    source_probe = source_probe.replace('["Card", "Rain", "Market", "Dusk", "ShoreCue"]', '["Card"]')
    source_probe = source_probe.replace("nextSample = t + .145", "nextSample = t + .22")
    parts = ["RoofSkin", "BasinRipple", "ShutterEdge", "SteamerLid", "BellCap", "DoorLeaf", None]
    captions = [("细雨敲在铁皮上", "把棚边敲颤"), ("落进搪瓷碗", "盆心又响一声"),
                ("卷门的链条绷紧", "顿住时轻颤"), ("竹盖轻碰笼沿", "白汽越过灯光"),
                ("车铃轻轻碰响两下", "尾声沿坡散开"), ("停在锁齿上", "锁舌咔哒"),
                ("走啦，吃饭去", "脚步渐渐远去")]

    def station(source, points):
        t.walk(points, NAMES[source])
        idx = int(source[1:]) - 1
        part = json.dumps(parts[idx])
        js = source_probe.replace("PART",part)
        baseline = t.js(js.replace("SECONDS","0"))[0]["part"]
        t.tap("listenBtn")
        seconds = sum(t.assets[source + b][1] for b in "AB") + .6
        rows = t.js(js.replace("SECONDS",str(seconds)),40000)
        cli.save(t.output / (source + ".json"), rows)
        for beat, subtitle in zip("AB", captions[idx]):
            key = source + beat
            matches = [r for r in rows if r["channels"]["Card"]["playing"]
                       and r["channels"]["Card"]["clip"] == t.assets[key][0] and subtitle in r["caption"]]
            cursors = [r["channels"]["Card"]["cursor"] for r in matches]
            assert len(cursors) >= 2 and max(cursors) > min(cursors), (key,cursors)
            if parts[idx]:
                assert any(r["part"] != baseline for r in matches), key
            if key == "S04B":
                assert any(r["particleCount"] > 0 for r in matches)
            observed[key] = {"samples":len(matches),"caption":matches[0]["caption"],
                             "part":parts[idx],"length":t.assets[key][1]}
        cli.save(t.output / "十四拍.json", observed)
        print("已听完",source,flush=True)

    t.clock("tour-start")
    station("S01",[(0,2.3)])
    t.collect("S01B")
    station("S02",[(0,5.5)])
    t.collect("S02A")
    t.tap("cardEntryBtn")
    t.tap("playBtn")
    t.playback("碗声两格",["S01B","S02A"],final=False)
    t.tap("closeBtn")
    t.walk([(0,10.5),(0,15)],PORTS["bow"])
    for button,label,bank in [("keepBtn","听暮路 →","dusk"),("listenBtn","← 听早市","market")]:
        t.audition(button,label,bank)
        time.sleep(3)
    t.confirm("market")
    station("S03",[(-11,25.4)])
    station("S04",[(-11,30.5)])
    t.collect("S04B")
    t.dock("market")
    t.audition("listenBtn","听暮路","dusk")
    t.confirm("dusk")
    station("S05",[(11,25.4)])
    station("S06",[(11,30.5)])
    t.collect("S06B",full=True)
    t.tap("slot3")
    t.tap("stampBtn","确认替换")
    t.tap("playBtn")
    t.playback("暮路草稿",["S01B","S02A","S06B"],final=False)
    t.tap("closeBtn")
    t.dock("dusk")
    t.home()
    station("S07",[(.35,8.8)])
    t.collect("S07A",full=True)
    t.tap("slot1")
    t.tap("stampBtn","确认替换")
    t.tap("swapBtn","交换两格")
    t.tap("slot1")
    t.tap("slot3")
    keys=["S06B","S02A","S07A"]
    t.tap("playBtn")
    t.playback("窗边草稿",keys,final=False)
    t.tap("closeBtn")
    t.walk([(0,8)],PORTS["desk"])
    t.tap("cardEntryBtn")
    t.tap("stampBtn","盖章寄出")
    t.playback("全航程盖章",keys)
    t.clock("tour-sealed")
    t.tap("postmarkBtn")
    t.playback("全航程邮戳",keys)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("instance")
    parser.add_argument("runtime")
    parser.add_argument("stages", nargs="+", choices=["solo","silent","pair","tour"])
    args=parser.parse_args()
    cli.ID=args.instance
    t=Acceptance(args.runtime)
    for stage in args.stages:
        t.stage=stage
        print("开始",stage,flush=True)
        try:
            {"solo":solo,"silent":silent,"pair":pair,"tour":tour}[stage](t)
        except Exception:
            t.shot("中断-"+stage)
            raise
        t.clock("passed-"+stage)
        print("通过",stage,flush=True)
