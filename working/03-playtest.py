"""Desktop voyage acceptance. Run python working/03-playtest.py --help for stages."""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
from route_cli import WORK, ROUTE, run, save

INTERACTION = ROUTE / "Interaction"
NAMES = {"S01":"雨棚铁皮", "S02":"檐下接雨盆", "S03":"早市卷帘门", "S04":"摊前蒸笼",
         "S05":"路边单车", "S06":"楼道门锁", "S07":"宿舍亮窗"}
TITLES = {"S01B":"铁皮重滴", "S02B":"迟来一滴", "S03A":"链条绷紧", "S04A":"竹盖轻碰",
          "S04B":"蒸汽呼出", "S05A":"两下车铃", "S05B":"铃声渐远", "S06B":"钥匙转开", "S07A":"走啦，吃饭去"}
PORTS = {"market":"早市 · 泊位", "dusk":"放学路 · 泊位", "bow":"末班船 · 船头", "desk":"窗边回信桌"}


class VoyageTest:
    def __init__(self, runtime):
        self.runtime = runtime
        self.output = WORK / ("03-playtest-" + runtime)
        self.output.mkdir(exist_ok=True)
        self.stage = "start"
        self.progress_path = self.output / "progress.json"
        if self.progress_path.exists():
            self.progress = json.loads(self.progress_path.read_text(encoding="utf-8"))
        else:
            self.progress = {"done":[], "clips":{}}
        self.controls_js = (INTERACTION / "controls.js").read_text(encoding="utf-8")

    def runtime_call(self,*args):
        return run("runtime",*args,"--runtime-id",self.runtime)

    def journal(self,event,data):
        with (self.output / "input.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps({"stage":self.stage,"event":event,"data":data},ensure_ascii=False)+"\n")

    def js(self,source,timeout=30000):
        result = self.runtime_call("js","eval",source,"--timeout-ms",str(timeout))
        if result.get("status") not in (None,"completed") or "result" not in result:
            raise RuntimeError(result)
        return result["result"]

    def view(self,event):
        state = self.js(self.controls_js)
        self.journal(event,state)
        return state

    def tap_point(self,point,event):
        x,y=point
        assert 0<x<1 and 0<y<1, (event,point)
        self.runtime_call("input","mouse",f"click:{x:.5f},{y:.5f}")
        self.journal("点按 "+event,point)

    def tap(self,button,label=None,state=None):
        state = state or self.view("按钮 "+button)
        if label:
            assert state["labels"].get(button+"Label")==label, (button,label,state["labels"])
        assert button in state["controls"], (button,state)
        self.tap_point(state["controls"][button],button)

    def at(self,zone):
        state = self.view("核对 "+zone)
        assert state["labels"].get("sourceLabel")==zone, (zone,state["labels"],state["p"])
        return state

    def walk(self,points,zone):
        source=(INTERACTION/"walk.js").read_text(encoding="utf-8").replace("WAYPOINTS",json.dumps(points))
        walked=self.js(source,60000)
        self.journal("步行 "+zone,walked)
        assert walked["ok"], (zone,walked["goal"],walked["samples"][-5:])
        return self.at(zone)

    def shot(self,tag):
        self.runtime_call("screenshot","--out",str(self.output / (tag+".png")))

    def listen(self,key,collect=True):
        beat=key[-1]
        state=self.at(NAMES[key[:3]])
        keep=state["coords"]["keepBtn"]
        self.tap("listenBtn",state=state)
        if beat=="B":
            # Keep the second beat window open until a physical tap; re-read the real label.
            deadline=time.monotonic()+12
            while True:
                step=self.view("等待第二拍 "+key)
                if step["labels"].get("keepBtnLabel")=="收下落点": break
                if time.monotonic()>deadline: raise RuntimeError(step)
                time.sleep(.14)
        if collect:
            self.tap_point(keep,"收下 "+key)
        state=self.view(("已采 " if collect else "试听 ")+key)
        if collect:
            assert TITLES[key] in state["labels"]["walkCaption"],(key,state)
        clip=state["channels"]["Card"]["clip"]
        assert clip is not None, (key,state["channels"])
        self.progress["clips"][key]=clip
        save(self.progress_path,self.progress)

    def audition(self,button,label,bank):
        self.tap(button,label)
        state=self.view("方位试听 "+bank)
        name="早市" if bank=="market" else "放学路"
        assert state["labels"].get("cardEntryBtnLabel")=="靠岸 · "+name,state
        assert state["channels"]["ShoreCue"]["clip"] is not None,state["channels"]
        self.journal("方向音轨 "+bank,state["channels"]["ShoreCue"])
        return state

    def arrive(self,target):
        time.sleep(1.55)
        state=self.at(PORTS.get(target,NAMES["S07"]))
        if target in ("market","dusk"):
            assert state["channels"][target.capitalize()]["playing"], state["channels"]
        return state

    def confirm(self,target):
        self.tap("cardEntryBtn","靠岸 · "+("早市" if target=="market" else "放学路"))
        self.arrive(target)

    def home(self):
        self.tap("keepBtn","暖灯返航")
        self.arrive("home")

    def replay(self,tag,keys):
        source=(INTERACTION/"replay.js").read_text(encoding="utf-8")
        data=self.js(source)
        save(self.output / (tag+"-replay.json"),data)
        for i,key in enumerate(keys,1):
            expected=self.progress["clips"][key]
            assert any(row["clip"]==expected and f"第 {i} 格" in row["title"] and TITLES[key] in row["title"]
                       for row in data), (tag,i,key,expected,data)
        self.shot(tag)

    def seal(self,tag,keys):
        self.tap("cardEntryBtn","坐到回信桌"); self.tap("stampBtn","盖章寄出")
        self.replay(tag,keys)
        self.tap("postmarkBtn")
        self.replay(tag+"-邮戳",keys)


def stage_rain(t):
    t.walk([(0,2.3)],NAMES["S01"]); t.listen("S01B")
    t.walk([(0,10.5),(0,15)],PORTS["bow"]); t.shot("01-船头")
    t.audition("keepBtn","听暮路 →","dusk"); t.audition("listenBtn","← 听早市","market"); t.confirm("market")


def stage_market(t):
    t.walk([(-11,25.4)],NAMES["S03"]); t.listen("S03A"); t.shot("02-卷门")
    t.walk([(-11,30.5)],NAMES["S04"]); t.listen("S04B",collect=False); t.shot("03-蒸笼")
    t.walk([(-11,20.5)],PORTS["market"])
    t.audition("listenBtn","听暮路","dusk"); t.confirm("dusk")


def stage_early_home(t):
    t.walk([(11,25.4)],NAMES["S05"]); t.listen("S05B",collect=False); t.shot("04-单车")
    t.walk([(11,20.5)],PORTS["dusk"]); t.home()
    t.walk([(0,8)],PORTS["desk"]); t.tap("cardEntryBtn","坐到回信桌")
    state=t.view("卡未满返航")
    assert "1 格" in state["labels"].get("feedbackLine",""),state
    t.tap("closeBtn"); t.tap("keepBtn","再去听听"); t.arrive("bow")
    t.audition("keepBtn","听暮路 →","dusk"); t.confirm("dusk")


def stage_old(t):
    t.walk([(11,30.5)],NAMES["S06"]); t.listen("S06B"); t.shot("05-门锁")
    t.walk([(11,20.5)],PORTS["dusk"]); t.home(); t.walk([(0,8)],PORTS["desk"])
    t.seal("06-旧声结尾",["S01B","S03A","S06B"])


def stage_new(t):
    state=t.view("从成品回到个人草稿")
    if "paperWakeBtn" in state["controls"]:
        t.tap("paperWakeBtn",state=state)
        state=t.view("展开卡面")
    if state["labels"].get("stampBtnLabel")=="回到个人草稿":
        t.tap("stampBtn","回到个人草稿",state)
    t.tap("stampBtn","再写一封")
    state=t.view("检查桌边空卡入口")
    if state["labels"].get("keepBtnLabel")=="再去听听":
        t.tap("keepBtn","再去听听",state); t.arrive("bow")
    else:
        t.walk([(0,10.5),(0,15)],PORTS["bow"])
    t.audition("keepBtn","听暮路 →","dusk"); t.confirm("dusk")
    t.walk([(11,25.4)],NAMES["S05"]); t.listen("S05A")
    t.walk([(11,20.5)],PORTS["dusk"]); t.home()
    t.walk([(0,5.5)],NAMES["S02"]); t.listen("S02B")
    t.walk([(.35,8.8)],NAMES["S07"]); t.listen("S07A"); t.walk([(0,8)],PORTS["desk"])
    t.seal("07-宿舍招呼在末格",["S05A","S02B","S07A"])


def stage_pair(t):
    t.tap("paperWakeBtn"); t.tap("closeBtn"); t.tap("listenBtn","合写一封")
    t.tap("slot1"); t.tap("stampBtn","选好，递给乙")
    t.walk([(0,10.5),(0,15)],PORTS["bow"]); t.audition("listenBtn","← 听早市","market"); t.confirm("market")
    t.walk([(-11,30.5)],NAMES["S04"]); t.listen("S04A"); t.walk([(-11,20.5)],PORTS["market"]); t.home()
    t.walk([(0,8)],PORTS["desk"]); t.tap("cardEntryBtn"); t.tap("slot1"); t.tap("stampBtn","放入第二格")
    t.tap("swapBtn","换甲来提议"); t.tap("slot3"); t.tap("stampBtn","提议这拍"); t.tap("swapBtn","按章合寄")
    t.replay("08-合写",["S05A","S04A","S07A"])

def revised_docks(t):
    t.walk([(0,10.5),(0,15)],PORTS["bow"])
    left=t.audition("listenBtn","← 听早市","market")["lamps"]
    time.sleep(.6)
    left=t.view("左舷光束与镜片")["lamps"]
    t.audition("keepBtn","听暮路 →","dusk")
    time.sleep(.75)
    right=t.view("右舷光束与镜片")["lamps"]
    save(t.output/"v2-左右岸灯.json",{"market":left,"dusk":right})
    assert left["forward"][0] < 0 < right["forward"][0] and left["MarketBoat"]>left["DuskBoat"] and right["DuskBoat"]>right["MarketBoat"], (left,right)
    t.audition("listenBtn","← 听早市","market")
    t.shot("v2-船头")
    t.confirm("market")
    t.shot("v2-早市泊位")


def revised_steam(t):
    t.walk([(-11,30.5)],NAMES["S04"])
    # The audition plays A then B. Wait out its first plume, keep B selected,
    # then use the real collect button to trigger a fresh sound and a second plume.
    t.listen("S04B",collect=False)
    time.sleep(2.2)
    state=t.at(NAMES["S04"])
    assert state["labels"].get("keepBtnLabel")=="收下落点",state
    probe=(INTERACTION/"steam-frames.js").read_text(encoding="utf-8")
    baseline=t.js(probe.replace("FRAME_COUNT","1"))
    assert baseline[0]["particles"]==0,baseline
    with ThreadPoolExecutor(max_workers=1) as observer:
        capture=observer.submit(t.js,probe.replace("FRAME_COUNT","125"))
        time.sleep(.5)
        t.tap("keepBtn","收下落点",state)
        frames=baseline+capture.result()
    save(t.output/"v2-蒸汽与笼盖.json",frames)
    state=t.view("收下蒸汽 B")
    assert "蒸汽呼出" in state["labels"].get("walkCaption",""),state
    peak=max(row["particles"] for row in frames)
    lift=max(row["lid"][1] for row in frames) - min(row["lid"][1] for row in frames)
    swing=max(abs((row["angles"][2]-frames[0]["angles"][2]+180)%360-180) for row in frames)
    assert frames[-1]["particles"]==0 and peak>0, (peak,frames[-1])
    assert any(row["particles"]>0 and row["clip"]==t.progress["clips"]["S04B"] for row in frames), "No simultaneous steam and S04B"
    assert lift>.015 or swing>2, (lift,swing)
    print(f"蒸汽 0→{peak}→0；笼盖行程 {lift:.3f} 米 / {swing:.1f}°",flush=True)
    t.walk([(-11,20.5)],PORTS["market"])
    t.audition("listenBtn","听暮路","dusk")
    t.confirm("dusk")
    t.shot("v2-暮路泊位")


def revised_window(t):
    t.walk([(11,25.4)],NAMES["S05"]); t.listen("S05A")
    t.walk([(11,20.5)],PORTS["dusk"]); t.home()
    t.walk([(0,5.5)],NAMES["S02"]); t.listen("S02B")
    t.walk([(.35,8.8)],NAMES["S07"])
    state=t.at(NAMES["S07"]); t.tap("listenBtn",state=state)
    t.tap_point(state["coords"]["keepBtn"],"收下室友招呼 A")
    state=t.view("满卡试听新声")
    assert "卡已满" in state["labels"].get("feedbackLine",""),state
    t.progress["clips"]["S07A"]=state["channels"]["Card"]["clip"]
    assert t.progress["clips"]["S07A"] is not None
    save(t.progress_path,t.progress)
    t.tap("slot1"); t.tap("stampBtn","确认替换")
    # The three recorded items are now voice/bell/basin. Put voice in the final slot.
    for a,b in [(1,2),(2,3)]:
        t.tap("swapBtn","交换两格"); t.tap("slot"+str(a)); t.tap("slot"+str(b))
    state=t.view("室友招呼留到第三格")
    assert [state["labels"]["slot"+str(i)+"Title"] for i in (1,2,3)]==["两下车铃","迟来一滴","走啦，吃饭去"],state
    t.tap("closeBtn")
    t.walk([(0,8)],PORTS["desk"]); t.seal("v2-室友招呼在末格",["S05A","S02B","S07A"])


STAGES = { "rain":stage_rain,"market":stage_market,"early-home":stage_early_home,
           "old-card":stage_old,"window-card":stage_new,"pair":stage_pair }
REVISED={"v2-docks":revised_docks,"v2-steam":revised_steam,"v2-window":revised_window}
if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Run in order from spawn. Completed stages are skipped on the same runtime.")
    parser.add_argument("runtime",help="Exact id returned by runtime start")
    parser.add_argument("--v2",action="store_true",help="Short updated route: dock sounds, live steamer motion and ending with room-mate")
    parser.add_argument("--from",dest="first",choices=(*STAGES,*REVISED),help="Restart at this stage (requires matching in-game state)")
    parser.add_argument("--through",choices=(*STAGES,*REVISED))
    args=parser.parse_args()
    t=VoyageTest(args.runtime)
    stages=REVISED if args.v2 else STAGES
    names=list(stages)
    if args.through is None: args.through=names[-1]
    for name in names[names.index(args.first) if args.first else 0:names.index(args.through)+1]:
        if args.first is None and name in t.progress["done"]: continue
        t.stage=name
        print("开始",name,flush=True)
        try:
            stages[name](t)
        except Exception:
            t.shot("失败-"+name)
            raise
        if name not in t.progress["done"]: t.progress["done"].append(name)
        save(t.progress_path,t.progress)
        print("通过",name,flush=True)
