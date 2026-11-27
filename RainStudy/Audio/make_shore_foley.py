"""Build the shore sound library and postcard foley. Uses Python 3 and NumPy."""
import numpy as np

import make_foley as f


def resonator(notes, decay, length=.7, noise=.16):
    t = f.seconds(length)
    resonances = sum(np.sin(2 * np.pi * hz * t) * np.exp(-t * (1 + i * .42) / decay)
                     / (1 + i * .6) for i, hz in enumerate(notes))
    transient = f.band_noise(len(t), 580, 6700) * np.exp(-t / .018)
    return (resonances + noise * transient) * (1 - np.exp(-t / .0016))


def friction(duration, low, high, texture=0):
    t = f.seconds(duration)
    air = f.band_noise(len(t), low, high)
    if texture:
        air *= .72 + .28 * np.sin(2 * np.pi * texture * t)
    return air * np.sin(np.pi * t / duration) ** 1.8


def cut(resource, title, description, duration, layers, peak=.71):
    track = np.zeros(len(f.seconds(duration)))
    for at, sound, gain in layers:
        f.layer(track, sound, at, gain)
    f.save(resource, title, description, track, peak)


def main():
    chain = resonator([951, 1573, 2739, 4073], .048)
    slat = resonator([181, 378, 727, 1378], .09)
    bamboo = resonator([249, 593, 1055], .037, noise=.37)
    bell = resonator([1093, 2180, 2829, 4114], .41, 2.45, .06)
    bell_tail = resonator([1069, 2169, 2795, 4083], .53, 2.85, .03)
    key = resonator([1490, 1981, 2954, 4267], .081, noise=.28)
    latch = resonator([315, 573, 1311, 2378], .053, noise=.62)
    floor = resonator([169, 257, 359], .055, noise=.2)
    cut("audio-shutter-chain", "链条绷紧", "链节逐渐加速，摩擦声衔接门帘起步。", 2.6,
        [(t, chain, amp) for t, amp in [(.16,.44),(.39,.6),(.56,.53),(.69,.62),(.81,.52),(.91,.83)]]
        + [(.55, friction(.72, 430, 3500, 29), .21), (.94, slat, .32)])
    cut("audio-shutter-stop", "卷门顿住", "短促的密集门片声，撞停后只留两下回颤。", 2.7,
        [(.1 + i * .075, slat, .16 + i * .045) for i in range(8)] +
        [(.12, friction(.66, 290, 2900, 41), .17), (.79, slat, 1.04),
         (.91, slat, .29), (1.03, chain, .18)])
    cut("audio-steamer-lid", "竹盖轻碰", "竹片短摩擦和两次干燥的盖沿碰撞。", 2.35,
        [(.13, bamboo, .88), (.22, friction(.38, 470, 2500, 34), .18), (.52, bamboo, .57)])
    cut("audio-steamer-steam", "蒸汽呼出", "盖沿一响，蒸汽逐渐透出并散去。", 2.75,
        [(.11, bamboo, .41), (.19, friction(1.72, 670, 5300, 5), .31),
         (.24, friction(1.01, 300, 1020), .085)], .61)
    cut("audio-bell-double", "两下车铃", "两次拨铃，铃舌短且分明。", 2.5,
        [(.13, bell, .85), (.44, bell, .95)])
    cut("audio-bell-tail", "铃声渐远", "一次稍远的碰击接完整尾音。", 3.1,
        [(.13, bell_tail, 1), (.29, bell_tail, .085), (.39, bell_tail, .045)], .61)
    cut("audio-lock-keys", "钥匙相碰", "散乱钥匙互碰，末尾为一次试齿。", 2.55,
        [(.15, key, .62), (.25, key, .38), (.46, key, .84), (.51, key, .43),
         (.83, friction(.29, 770, 5300, 51), .095), (.98, latch, .19)])
    cut("audio-lock-open", "钥匙转开", "试探后锁舌咔哒，木门微开停住。", 2.65,
        [(.14, key, .23), (.55, friction(.31, 450, 3700, 38), .11), (.72, latch, 1),
         (.81, friction(.76, 170, 1800, 21), .15), (1.1, floor, .31)], .8)

    t = f.seconds(24)
    market = f.band_noise(len(t), 180, 1680) * (.38 + .10 * np.sin(t * np.pi / 6))
    dusk = f.band_noise(len(t), 95, 760) * (.34 + .14 * np.sin(t * np.pi / 6))
    dusk += f.band_noise(len(t), 600, 2900) * (.14 + .08 * np.cos(t * np.pi / 4))
    for at, gain in [(2.3,.19),(2.62,.15),(6.8,.12),(12.9,.23),(17.3,.12),(17.9,.16),(21.9,.13)]:
        f.layer(market, bamboo, at, gain)
    for at, gain in [(7.7,.1),(8.12,.08),(14.9,.18),(15.38,.14),(15.95,.11)]:
        f.layer(dusk, floor, at, gain)
    f.save("audio-market-bed", "清晨市巷", "24 秒循环，窄巷远处杂响和摊面木声。", market, .25)
    f.save("audio-dusk-bed", "傍晚坡道", "24 秒循环，空地穿堂风和远处鞋底轻响。", dusk, .24)
    cut("audio-postmark", "邮戳", "木柄压在纸卡上，随后是很轻的纸擦声。", .36,
        [(.025, floor, .85), (.052, latch, .14), (.117, friction(.19, 750, 4100, 26), .07)], .48)


if __name__ == "__main__":
    main()
