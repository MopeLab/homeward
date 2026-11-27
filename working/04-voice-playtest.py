"""Retest both supplied clips in the native desktop preview."""
import runpy
import sys
import time
from pathlib import Path


here = Path(__file__).resolve().parent
release = runpy.run_path(str(here / "04-voice-release.py"))
prior = runpy.run_path(str(here / "04-playtest.py"))
cli, read, step = release["cli"], release["read"], release["step"]
cli.ID = read(here / "04-voice-instance.json")["data"]["instanceId"]
NAMES, PORTS = prior["NAMES"], prior["PORTS"]
FAMILY, ROOMMATE = 3.317551, 1.802449
LINE = "刚把窗关上"
CALL = "走啦，吃饭去"


def card_audio(row):
    return row["channels"]["Card"]


def samples(rows, duration, caption):
    matched = [r for r in rows if card_audio(r)["playing"]
               and abs(card_audio(r)["length"] - duration) < .018]
    assert len(matched) >= 2 and all(caption in r["caption"] for r in matched), matched
    cursors = [card_audio(r)["cursor"] for r in matched]
    assert max(cursors) > min(cursors), cursors
    return matched


def started(row):
    clip = card_audio(row)
    return row["t"] - clip["cursor"] / clip["rate"]


def check_gap(first, second, duration, gap):
    elapsed = started(second[0]) - started(first[0])
    expected = duration + gap
    assert abs(elapsed - expected) < .30, (elapsed, expected, first[0], second[0])
    return elapsed


def collect(t, title):
    state = t.view("收下 " + title)
    t.tap("listenBtn", state=state)
    t.tap_point(state["coords"]["keepBtn"], title)
    row = t.observe()[0]
    assert title in row["caption"] and card_audio(row)["playing"], row
    return row


def check_replay(t, tag, voice):
    rows = t.observe(9.7)
    t.save(tag, rows)
    a = samples(rows, ROOMMATE, "第 1 格")
    b = samples(rows, 2.4, "第 2 格")
    c = samples(rows, 2.45, "第 3 格")
    assert [r["images"] for r in (a[0], b[0], c[0])] == [
        [["Window"], [], []], [["Window"], ["Basin"], []], [["Window"], ["Basin"], ["Tin"]]]
    assert all(card_audio(r)["clip"] == voice and CALL in r["caption"] for r in a)
    elapsed = check_gap(a, b, ROOMMATE, .32)
    assert "paperWakeBtn" in t.view(tag)["controls"]
    return elapsed


class VoiceTest(prior["ContentTest"]):
    def __init__(self, runtime):
        super().__init__(runtime)
        self.output = here / f"04-voice-test-{runtime}"
        self.output.mkdir(exist_ok=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--existing" in sys.argv:
        runtime = cli.run("runtime", "status")["runtimeId"]
    else:
        runtime = step("runtime", "runtime", "start", "--wait", "60")["runtimeId"]
    t = VoiceTest(runtime)
    rows = t.observe(5.1)
    t.save("开场", rows)
    family = samples(rows, FAMILY, LINE)
    clear = next(r for r in rows if r["t"] > family[-1]["t"] and LINE not in r["caption"])
    visible_for = clear["t"] - started(family[0])
    assert abs(visible_for - FAMILY) < .28, (visible_for, clear)
    print(f"开场字幕退场 {visible_for:.3f} 秒", flush=True)

    t.walk([(0,5.5),(0,8),(.35,8.8)], NAMES["S07"])
    t.tap("listenBtn")
    rows = t.observe(5.1)
    t.save("室友两拍", rows)
    call = samples(rows, ROOMMATE, CALL)
    steps = samples(rows, 3.0, "脚步渐渐远去")
    a_to_b = check_gap(call, steps, ROOMMATE, .20)
    assert card_audio(call[0])["clip"] != card_audio(steps[0])["clip"]
    voice = card_audio(call[0])["clip"]
    collected = collect(t, CALL)
    assert card_audio(collected)["clip"] == voice
    print(f"室友 A 到 B 开始间隔 {a_to_b:.3f} 秒，已收下 A", flush=True)

    t.walk([(0,5.5)], NAMES["S02"]); collect(t, "盆中双响")
    t.walk([(0,2.3)], NAMES["S01"]); collect(t, "棚上碎雨")
    t.walk([(0,8)], PORTS["desk"]); t.tap("cardEntryBtn", "坐到回信桌")
    t.tap("stampBtn", "盖章寄出")
    sealed = check_replay(t, "盖章", voice)
    t.tap("postmarkBtn")
    replayed = check_replay(t, "邮戳重听", voice)
    t.shot("三格原声卡")
    release["record"]("test", {"passed": True, "runtime": runtime, "familyClip": card_audio(family[0])["clip"],
                              "familyCaptionSeconds": visible_for, "roommateClip": voice,
                              "roommateAToBSeconds": a_to_b, "sealFirstToSecondSeconds": sealed,
                              "replayFirstToSecondSeconds": replayed})
    print("开场、选拍、收下、盖章和邮戳重听通过", flush=True)
