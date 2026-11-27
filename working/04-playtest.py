"""Thread 04 desktop audio, subtitle, artwork and postcard acceptance."""
import json
import runpy
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


here = Path(__file__).resolve().parent
release = runpy.run_path(str(here / "04-release.py"))
test = runpy.run_path(str(here / "03-playtest.py"))
NAMES, PORTS = test["NAMES"], test["PORTS"]
PARTS = ("RoofSkin", "BasinRipple", "ShutterEdge", "SteamerLid", "BellCap", "DoorLeaf", None)
BEATS = (
    ((2.45, "细雨敲在铁皮上"), (2.65, "把棚边敲颤")),
    ((2.40, "水纹叠在一起"), (2.90, "盆心又响一声")),
    ((2.60, "卷门的链条绷紧"), (2.70, "顿住时轻颤")),
    ((2.35, "竹盖轻碰笼沿"), (2.75, "白汽越过灯光")),
    ((2.50, "车铃轻轻碰响两下"), (3.10, "尾声沿坡散开")),
    ((2.55, "停在锁齿上"), (2.65, "锁舌咔哒")),
    ((1.802449, "走啦，吃饭去"), (3.0, "脚步渐渐远去")),
)
TITLES = ("铁皮重滴", "钥匙转开", "走啦，吃饭去")
ART = ["Tin", "Lock", "Window"]


class ContentTest(test["VoyageTest"]):
    def __init__(self, runtime):
        super().__init__(runtime)
        self.output = here / f"04-playtest-{runtime}"
        self.output.mkdir(exist_ok=True)
        self.probe = (here / "04-observe-audio.js").read_text(encoding="utf-8")
        self.controls_js = self.controls_js.replace('"paperWakeBtn"]',
                                                    '"paperWakeBtn","rainBtn","quieterBtn"]')
        self.ids = {}
        self.report = {}

    def observe(self, seconds=0, part=None):
        return self.js(self.probe.replace("SECONDS", str(seconds)).replace("PART", json.dumps(part)),
                       timeout=22000)

    def save(self, name, data):
        test["save"](self.output / (name + ".json"), data)

    def check_bed(self, name):
        audio = self.observe(.55)[-1]["channels"][name]
        assert audio["playing"] and audio["loop"] and audio["cursor"] > 0, audio
        self.report[name] = audio

    def beats(self, source, keep=None):
        source_id = f"S{source:02}"
        self.stage = source_id
        state = self.at(NAMES[source_id])
        base = self.observe(part=PARTS[source - 1])[0]
        self.tap("listenBtn", state=state)
        if keep == "A":
            self.tap_point(state["coords"]["keepBtn"], "收下 " + source_id + keep)
            assert self.observe()[0]["channels"]["Card"]["playing"]
            self.tap("listenBtn")
        rows = self.observe(5.45, PARTS[source - 1])
        self.save(source_id, [base] + rows)
        for beat, (length, caption) in zip("AB", BEATS[source - 1]):
            matched = [r for r in rows if r["channels"]["Card"]["playing"]
                       and abs(r["channels"]["Card"]["length"] - length) < .02
                       and caption in r["caption"]]
            assert len(matched) >= 2, (source_id, beat, [(r["channels"]["Card"], r["caption"]) for r in rows])
            cursors = [r["channels"]["Card"]["cursor"] for r in matched]
            assert max(cursors) > min(cursors), (source_id, beat, cursors)
            self.ids[source_id + beat] = matched[-1]["channels"]["Card"]["clip"]
            bed = next(n for n in ("Rain", "Market", "Dusk") if base["channels"][n]["playing"])
            assert min(r["channels"][bed]["gain"] for r in matched) < base["channels"][bed]["gain"] * .55
            if PARTS[source - 1]:
                assert any(r["part"] != base["part"] for r in matched), (source_id, beat, base["part"])
            if source == 4 and beat == "B":
                assert any(r["particleCount"] > 0 for r in matched), matched
            self.report[source_id + beat] = {
                "clip": matched[-1]["channels"]["Card"]["name"], "duration": length,
                "caption": matched[0]["caption"], "cursorRange": [min(cursors), max(cursors)],
                "movement": PARTS[source - 1], "ambient": bed,
            }
        assert self.ids[source_id + "A"] != self.ids[source_id + "B"]
        if keep == "B":
            self.tap("keepBtn", "收下落点")
        self.save("逐项试听", self.report)
        print("通过", source_id, flush=True)

    def card_replay(self, tag, postmark):
        if postmark:
            state = self.view("盖章前")
            with ThreadPoolExecutor(max_workers=1) as pool:
                capture = pool.submit(self.observe, 11.3)
                time.sleep(.55)
                self.tap("stampBtn", "盖章寄出", state)
                rows = capture.result()
        else:
            rows = self.observe(10.2)
        self.save(tag, rows)
        if postmark:
            assert any(r["channels"]["Card"]["playing"] and abs(r["channels"]["Card"]["length"] - .36) < .02
                       for r in rows), rows[:4]
        for i, (key, title) in enumerate(zip(("S01B", "S06B", "S07A"), TITLES), 1):
            assert any(r["channels"]["Card"]["playing"] and r["channels"]["Card"]["clip"] == self.ids[key]
                       and f"第 {i} 格" in r["caption"] and title in r["caption"]
                       and r["images"] == [[name] if j < i else [] for j, name in enumerate(ART)]
                       for r in rows), (tag, i, title)
        last = self.view(tag)
        assert "paperWakeBtn" in last["controls"] and "stampBtn" not in last["controls"]
        self.shot(tag)

    def muted_letter(self):
        self.stage = "静音"
        self.tap("paperWakeBtn")
        self.tap("soundBtn")
        self.tap("rainBtn")
        for _ in range(5):
            self.tap("quieterBtn")
        self.tap("closeBtn")
        self.tap("stampBtn", "再写一封")
        self.walk([(0,5.5)], NAMES["S02"])
        self.collect_silent("盆中双响")
        self.walk([(0,2.3)], NAMES["S01"])
        self.collect_silent("棚上碎雨")
        self.walk([(0,8),(.35,8.8)], NAMES["S07"])
        self.collect_silent("走啦，吃饭去")
        self.walk([(0,8)], PORTS["desk"])
        self.tap("cardEntryBtn", "坐到回信桌")
        self.tap("stampBtn", "盖章寄出")
        rows = self.observe(10.1)
        assert all(not a["playing"] and a["gain"] == 0 for r in rows
                   for a in r["channels"].values() if a["clip"] is not None)
        assert all(any(title in r["caption"] for r in rows)
                   for title in ("盆中双响", "棚上碎雨", "走啦，吃饭去"))
        self.save("静音卡", rows)
        self.shot("静音卡")

    def collect_silent(self, title):
        state = self.view("静音试听")
        self.tap("listenBtn", state=state)
        self.tap_point(state["coords"]["keepBtn"], "静音收下 " + title)
        result = self.observe()[0]
        assert not result["channels"]["Card"]["playing"] and title in result["caption"], result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    t = ContentTest(sys.argv[1])
    t.check_bed("Rain")
    t.walk([(0,2.3)], NAMES["S01"]); t.beats(1, "B")
    t.walk([(0,5.5)], NAMES["S02"]); t.beats(2)
    t.walk([(0,10.5),(0,15)], PORTS["bow"])
    t.audition("listenBtn","← 听早市","market"); t.confirm("market")
    t.check_bed("Market")
    t.walk([(-11,25.4)], NAMES["S03"]); t.beats(3)
    t.walk([(-11,30.5)], NAMES["S04"]); t.beats(4)
    t.walk([(-11,20.5)], PORTS["market"])
    t.audition("listenBtn","听暮路","dusk"); t.confirm("dusk")
    t.check_bed("Dusk")
    t.walk([(11,25.4)], NAMES["S05"]); t.beats(5)
    t.walk([(11,30.5)], NAMES["S06"]); t.beats(6, "B")
    t.walk([(11,20.5)], PORTS["dusk"]); t.home()
    t.walk([(.35,8.8)], NAMES["S07"]); t.beats(7, "A")
    t.walk([(0,8)], PORTS["desk"])
    t.tap("cardEntryBtn","坐到回信桌")
    t.card_replay("七组版盖章卡", True)
    t.tap("postmarkBtn")
    t.card_replay("邮戳重听", False)
    t.muted_letter()
    print("完成十四拍、三底声、三格回放、邮戳重听及静音成卡", flush=True)
