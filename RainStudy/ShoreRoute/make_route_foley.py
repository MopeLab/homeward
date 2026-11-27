"""Rebuild the ten temporary, original shore sounds for the route playtest."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT.parent / "Audio"))
import make_foley as f

f.ASSETS = ROOT / "audio"


def strike(notes, damping, duration=1.8):
    t = f.seconds(duration)
    attack = (1 - np.exp(-t / .0018))
    signal = sum(np.sin(2*np.pi*hz*t)*np.exp(-t/(damping/(1+i*.28)))/(1+i*.6)
                 for i,hz in enumerate(notes))
    return attack * (signal + .23*f.band_noise(len(t), 700, 5100)*np.exp(-t/.009))


def main():
    chain = strike([934,1286,2500],.075)
    slat = strike([156,281,511,694],.12)
    lid = strike([248,671,983],.050)
    bell = strike([899,1857,2437,3272],.57,2.65)
    keys = strike([1828,2679,3486],.108)
    latch = strike([422,993,1473],.049)
    steam_t = f.seconds(1.8)
    steam = f.band_noise(len(steam_t), 460, 3900)*(1-np.exp(-steam_t/.16))*np.exp(-steam_t/.52)
    rows = [
        ("s03a","卷门链条",[(.10+i*.115,chain,.45+i*.06) for i in range(7)]),
        ("s03b","卷门顿住",[(.08+i*.083,slat,.28+i*.038) for i in range(9)]+[(.86,slat,1.65),(.98,chain,.36)]),
        ("s04a","竹盖轻碰",[(.16,lid,1),(.34,lid,.45),(.90,lid,.68)]),
        ("s04b","蒸汽呼出",[(.12,lid,.42),(.27,steam,.72)]),
        ("s05a","两下车铃",[(.10,bell,.93),(.38,bell,.87)]),
        ("s05b","车铃尾音",[(.15,bell,1),(.47,bell,.10)]),
        ("s06a","钥匙试齿",[(.09,keys,.40),(.17,keys,.66),(.53,keys,.82),(.98,latch,.32)]),
        ("s06b","锁舌转开",[(.12,keys,.26),(.69,latch,1),(.77,lid,.64),(.95,slat,.18)])]
    for key,title,layers in rows:
        track = np.zeros_like(f.seconds(2.8))
        for at, sample, volume in layers:
            f.layer(track,sample,at,volume)
        f.save("audio-route-"+key,title,"03 原创程序拟音；04 正式声画待替换。",track,.73)
    for key,title,low,high in [("market","晨市街底",215,1850),("dusk","暮路晚风",90,980)]:
        t = f.seconds(12)
        bed = f.band_noise(len(t),low,high)*(.7+.14*np.cos(t*2*np.pi/6))
        if key == "market":
            for i in range(5):
                f.layer(bed,lid,1.5+i*1.85,.46)
        f.save("audio-route-"+key,title,"03 原创循环环境占位。",bed,.23)


if __name__ == "__main__":
    main()
