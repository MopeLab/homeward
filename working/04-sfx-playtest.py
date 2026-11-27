"""Test the four replacement clips and the complete long postcard beat."""
import json
import runpy
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
release = runpy.run_path(str(HERE / "04-voice-release.py"))
voice_test = runpy.run_path(str(HERE / "04-voice-playtest.py"))
cli = release["cli"]
cli.ID = release["read"](HERE / "04-sfx-instance.json")["data"]["instanceId"]
NAMES, PORTS = voice_test["NAMES"], voice_test["PORTS"]
samples, card_audio = voice_test["samples"], voice_test["card_audio"]
started, check_gap = voice_test["started"], voice_test["check_gap"]
LONG, SHUTTER, BELL, LOCK = 19.09, 3.241667, 1.623787, 2.137959


def record(name, data):
    cli.save(HERE / f"04-sfx-{name}.json", data)


class SoundTest(voice_test["VoiceTest"]):
    def __init__(self, runtime):
        super().__init__(runtime)
        self.output = HERE / f"04-sfx-test-{runtime}"
        self.output.mkdir(exist_ok=True)

    def capture(self, seconds, part=None, *, basin=False):
        source = self.probe.replace("SECONDS", str(seconds)).replace("PART", json.dumps(part))
        channels = ["Card", "Rain", "Basin"] if basin else ["Card"]
        source = source.replace('["Card", "Rain", "Market", "Dusk", "ShoreCue"]', json.dumps(channels))
        if seconds > 15:
            source = source.replace("nextSample = t + .145", "nextSample = t + .24")
        return self.js(source, timeout=41000)


def peak_cursor(rows):
    return max(card_audio(row)["cursor"] / card_audio(row)["rate"] for row in rows)


def long_voyage(t):
    t.stage = "碗中雨滴"
    t.walk([(0,5.5)], NAMES["S02"])
    base = t.capture(0, "BasinRipple", basin=True)[0]["part"]
    t.tap("listenBtn", "听一听")
    t.tap("listenBtn", "听落点")
    skip = t.capture(.55)
    assert any(card_audio(r)["playing"] and abs(card_audio(r)["length"] - 2.9) < .02
               and "盆心又响一声" in r["caption"] for r in skip)
    t.save("跳到落点", skip)

    t.tap("listenBtn", "再听一遍")
    rows = t.capture(22.3, "BasinRipple", basin=True)
    t.save("搪瓷碗完整试听", rows)
    full = samples(rows, LONG, "一声接一声落进搪瓷碗")
    b = samples(rows, 2.9, "盆心又响一声")
    assert peak_cursor(full) > 18.75, peak_cursor(full)
    assert any(card_audio(r)["cursor"] / card_audio(r)["rate"] > 12 and r["part"] != base for r in full)
    ambient = [r["channels"]["Basin"] for r in rows if r["channels"]["Basin"]["playing"]]
    assert any(abs(a["length"] - 2.8) < .02 for a in ambient), ambient
    assert all(a["length"] < 3 for a in ambient), ambient
    advance = check_gap(full, b, LONG, .20)
    t.tap("listenBtn", "再听一遍")
    t.tap("keepBtn", "收下蓄势")
    check = t.capture(0)[0]
    assert "碗中雨滴" in check["caption"] and card_audio(check)["clip"] == card_audio(full[0])["clip"]
    print(f"S02A 试听至 {peak_cursor(full):.3f} 秒，{advance:.3f} 秒切到 B，主动跳拍通过", flush=True)
    return card_audio(full[0])["clip"], peak_cursor(full), advance


def shore_clip(t, name, key, length, subtitle, part, keep=False):
    t.stage = key
    state = t.at(name)
    t.tap("listenBtn", state=state)
    if key.endswith("A") and keep:
        t.tap_point(state["coords"]["keepBtn"], "收下蓄势")
    rows = t.capture(6.3 if key.endswith("B") else 1.2, part)
    t.save(key, rows)
    matched = samples(rows, length, subtitle)
    assert len({tuple(sum(r["part"], [])) for r in matched}) > 1, (name, key, matched)
    if key.endswith("B") and keep:
        t.tap("keepBtn", "收下落点")
        assert card_audio(t.capture(0)[0])["clip"] == card_audio(matched[0])["clip"]
    print(key, f"{card_audio(matched[0])['length']:.3f} 秒，字幕与动作通过", flush=True)
    return card_audio(matched[0])["clip"]


def verify_replay(rows, expected):
    first = samples(rows, LONG, "第 1 格")
    second = samples(rows, BELL, "第 2 格")
    third = samples(rows, LOCK, "第 3 格")
    assert tuple(card_audio(group[0])["clip"] for group in (first,second,third)) == expected
    assert first[0]["images"] == [["Basin"], [], []]
    assert third[0]["images"] == [["Basin"], ["Bell"], ["Lock"]]
    assert peak_cursor(first) > 18.75, peak_cursor(first)
    spacing = check_gap(first, second, LONG, .32)
    return peak_cursor(first), spacing


def verify_replay_skip(t, first_clip):
    state = t.view("回放结束")
    assert "paperWakeBtn" in state["controls"]
    t.shot("三格成品长音轨卡")
    t.tap("postmarkBtn", state=state)
    row = t.capture(0)[0]
    assert card_audio(row)["playing"] and card_audio(row)["clip"] == first_clip
    t.tap("closeBtn")
    stopped = t.capture(0)[0]
    assert not card_audio(stopped)["playing"], stopped


def replay(t, expected):
    t.stage = "长音轨明信片"
    t.tap("cardEntryBtn", "坐到回信桌")
    t.tap("stampBtn", "盖章寄出")
    rows = t.capture(25.8)
    t.save("长音轨盖章回放", rows)
    return verify_replay(rows, expected)


def finish_playtest(t, ids, audition_cursor, audition_gap, replay_cursor, replay_gap):
    verify_replay_skip(t, ids[0])
    print(f"S02A 盖章回放至 {replay_cursor:.3f} 秒，{replay_gap:.3f} 秒进入第二格", flush=True)
    record("test", {"passed": True, "runtime": t.runtime,
                    "clipIDs": dict(zip(("S02A", "S03B", "S05A", "S06B"), ids)),
                    "S02AAuditionCursorSeconds": audition_cursor, "S02AAtoBSeconds": audition_gap,
                    "S02AReplayCursorSeconds": replay_cursor, "S02AToNextSlotSeconds": replay_gap})


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    state = cli.run("runtime", "status")
    resume_bell = "--resume-bell" in sys.argv
    finish_replay = "--finish-replay" in sys.argv
    if resume_bell or finish_replay:
        assert state["status"] == "running", state
        t = SoundTest(state["runtimeId"])
        rows = release["read"](t.output / "搪瓷碗完整试听.json")
        full = samples(rows, LONG, "一声接一声落进搪瓷碗")
        basin_id, audition_cursor = card_audio(full[0])["clip"], peak_cursor(full)
        audition_gap = check_gap(full, samples(rows, 2.9, "盆心又响一声"), LONG, .20)
        shutter = samples(release["read"](t.output / "S03B.json"), SHUTTER, "顿住时轻颤")
        shutter_id = card_audio(shutter[0])["clip"]
        if resume_bell:
            assert t.at(NAMES["S05"])["labels"]["cardEntryBtnLabel"] == "明信片 · 2/3"
    else:
        if state["status"] == "running":
            cli.run("runtime", "stop", "--runtime-id", state["runtimeId"])
        data = cli.run("runtime", "start", "--wait", "60")
        record("runtime", data)
        t = SoundTest(data["runtimeId"])
        basin_id, audition_cursor, audition_gap = long_voyage(t)
        t.walk([(0,10.5),(0,15)], PORTS["bow"])
        t.audition("listenBtn", "← 听早市", "market"); t.confirm("market")
        t.walk([(-11,25.4)], NAMES["S03"])
        shutter_id = shore_clip(t, NAMES["S03"], "S03B", SHUTTER, "顿住时轻颤", "ShutterEdge")
        t.walk([(-11,20.5)], PORTS["market"])
        t.audition("listenBtn", "听暮路", "dusk"); t.confirm("dusk")
        t.walk([(11,25.4)], NAMES["S05"])
    if finish_replay:
        bell = samples(release["read"](t.output / "S05A.json"), BELL, "轻轻碰响两下")
        lock = samples(release["read"](t.output / "S06B.json"), LOCK, "锁舌咔哒")
        bell_id, lock_id = card_audio(bell[0])["clip"], card_audio(lock[0])["clip"]
        rows = release["read"](t.output / "长音轨盖章回放.json")
        replay_cursor, replay_gap = verify_replay(rows, (basin_id, bell_id, lock_id))
        finish_playtest(t, (basin_id, shutter_id, bell_id, lock_id),
                        audition_cursor, audition_gap, replay_cursor, replay_gap)
        sys.exit()
    bell_id = shore_clip(t, NAMES["S05"], "S05A", BELL, "轻轻碰响两下", "BellCap", True)
    t.walk([(11,30.5)], NAMES["S06"])
    lock_id = shore_clip(t, NAMES["S06"], "S06B", LOCK, "锁舌咔哒", "DoorLeaf", True)
    if resume_bell:
        t.tap("slot2")
        t.tap("stampBtn", "确认替换")
        t.tap("swapBtn", "交换两格")
        t.tap("slot2")
        t.tap("slot3")
        t.tap("closeBtn")
    t.walk([(11,20.5)], PORTS["dusk"]); t.home()
    t.walk([(0,8)], PORTS["desk"])
    replay_cursor, replay_gap = replay(t, (basin_id, bell_id, lock_id))
    finish_playtest(t, (basin_id, shutter_id, bell_id, lock_id),
                    audition_cursor, audition_gap, replay_cursor, replay_gap)
