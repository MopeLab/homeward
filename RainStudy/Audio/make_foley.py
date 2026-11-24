"""Build mono PCM foley for the rain-study resources. Uses Python 3 and NumPy."""
import json
import wave
from pathlib import Path

import numpy as np


ASSETS = Path(__file__).parent / "assets"
RATE = 32000
RNG = np.random.default_rng(1812)


def seconds(t):
    return np.arange(round(t * RATE)) / RATE


def band_noise(n, low, high):
    # Periodic, gently filtered noise without an abrupt frequency cutoff.
    freq = np.fft.rfftfreq(n, 1 / RATE)
    transfer = (1 - np.exp(-(freq / low) ** 2)) * np.exp(-(freq / high) ** 2)
    raw = np.fft.rfft(RNG.normal(size=n))
    noise = np.fft.irfft(raw * transfer, n)
    return noise / max(1e-12, np.std(noise))


def layer(track, sound, at, gain=1.0):
    offset = round(at * RATE)
    available = min(len(sound), len(track) - offset)
    track[offset:offset + available] += gain * sound[:available]


def impact(material, pitch=1.0):
    t = seconds(1.1)
    if material == "tin":
        frequencies = [296, 433, 711, 1029, 1810, 2432, 3109]
        amplitudes = [.29, .26, .16, .23, .11, .08, .05]
        decays = [.12, .13, .09, .08, .05, .034, .029]
        attack = .22 * band_noise(len(t), 600, 7600) * np.exp(-t / .013)
    else:
        frequencies = [581, 1192, 2037, 2864]
        amplitudes = [.22, .11, .04, .025]
        decays = [.27, .18, .11, .078]
        # A bubble rises rapidly in pitch while the curved enamel bowl keeps ringing.
        phase = 2 * np.pi * pitch * (1120 * t - 18 * (1 - np.exp(-t / .026)))
        attack = .70 * np.sin(phase) * np.exp(-t / .056)
        attack += .10 * band_noise(len(t), 600, 5100) * np.exp(-t / .016)
    sound = attack
    for hz, amp, decay in zip(frequencies, amplitudes, decays):
        sound += amp * np.sin(2 * np.pi * hz * pitch * t) * np.exp(-t / decay)
    return sound * (1 - np.exp(-t / .0014))


def drops(duration, material, pattern):
    track = np.zeros(round(RATE * duration))
    for stamp, gain, pitch in pattern:
        layer(track, impact(material, pitch), stamp, gain)
    return track


def steps():
    track = np.zeros(len(seconds(3.0)))
    for i, stamp in enumerate([.14, .54, 1.00, 1.44, 1.93, 2.36]):
        t = seconds(.42)
        slip = band_noise(len(t), 470, 2100) * np.exp(-t / .043)
        sole = np.sin(2 * np.pi * (133 * t + .75 * (1 - np.exp(-t / .022))))
        contact = (sole * np.exp(-t / .048) + .32 * slip) * (1 - np.exp(-t / .007))
        layer(track, contact, stamp, .80 ** i)
        layer(track, contact, stamp + .083, .14 * .80 ** i)
    return track


def rain():
    period = 24
    t = seconds(period)
    # Every modulator completes whole cycles. The filtered noise is also circular.
    motion = .67 + .08 * np.sin(t * np.pi / 6) + .06 * np.sin(t * np.pi / 4)
    bed = (band_noise(len(t), 260, 7200) * .15
           + band_noise(len(t), 650, 2100) * .11) * motion
    for stamp in np.arange(.075, period - .16, .13):
        pulse = seconds(.13)
        spray = band_noise(len(pulse), 700, 5400)
        spray *= np.exp(-pulse / .025) * (1 - np.exp(-pulse / .002))
        layer(bed, spray, stamp + RNG.uniform(-.045, .045), RNG.uniform(.01, .08))
    return bed


def save(resource, name, description, track=None, peak=.78):
    folder = ASSETS / resource
    folder.mkdir(parents=True, exist_ok=True)
    meta = dict(schemaVersion=4, resourceId=resource, displayName=name, summary=description)
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    if track is None:
        return
    normalized = track / max(abs(track)) * peak
    with wave.open(str(folder / "audio.wav"), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(np.round(normalized * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    save("audio-tin-scatter", "铁皮碎雨", "小雨洒在薄铁皮上，轻响短促而疏密不一。",
         drops(2.45, "tin", [(.10, .70, 1), (.23, .30, 1.12), (.43, .47, .94),
                              (.89, .58, 1.03), (1.25, .30, 1.09), (1.64, .42, .96)]))
    save("audio-tin-strike", "铁皮重滴", "两下细响之后，慢半拍的重滴带起一阵板面颤响。",
         drops(2.65, "tin", [(.08, .20, 1.06), (.39, .29, 1), (1.13, 1.00, .86)]))
    save("audio-basin-double", "两圈水纹", "两滴水贴近落下，盆边的余音和第二圈水纹相叠。",
         drops(2.4, "basin", [(.16, .84, 1.04), (.40, 1, .88)]))
    save("audio-basin-late", "迟来一滴", "一丝轻响后留出空拍，一滴圆润的水声落在盆心。",
         drops(2.9, "basin", [(.09, .16, 1.12), (1.22, 1.0, .96)]))
    save("audio-window-steps", "楼梯脚步", "鞋跟在楼梯上响了六下，脚步渐远。", steps())
    save("audio-rain-bed", "檐外的雨", "首尾循环的雨夜底声，跨柱时持续。",
         rain(), peak=.50)
    save("audio-family-voice", "家人的语音·临时", "离线合成普通话占位，待换家人原声。")
    save("audio-window-call", "走啦，吃饭去·临时", "离线合成普通话占位，待换室友原声。")
