"""Prepare the supplied WAVs without trimming the selectable card clips."""
import json
import subprocess
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "RainStudy/Audio/assets"
TAKES = {
    "S02A": ("audio-basin-drips-recorded", "碗中雨滴"),
    "S03B": ("audio-shutter-stop-recorded", "卷门顿住"),
    "S05A": ("audio-bell-double-recorded", "两下车铃"),
    "S06B": ("audio-lock-open-recorded", "钥匙转开"),
    "BasinAccent": ("audio-basin-accent-recorded", "碗边环境短滴"),
}


if __name__ == "__main__":
    for key, (resource, title) in TAKES.items():
        short = key == "BasinAccent"
        source = ROOT / "SFX" / ("S02A.wav" if short else key + ".wav")
        dest = ASSETS / resource
        dest.mkdir(parents=True, exist_ok=True)
        clip = dest / "audio.wav"
        extra = ["-t", "2.8", "-af", "afade=t=out:st=2.67:d=0.13"] if short else []
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), *extra, "-map_metadata",
                        "-1", "-ac", "1", "-c:a", "pcm_s16le", str(clip)], check=True)
        summary = (f"来自制作方交付的 {source.name}。"
                   + ("提取前 2.8 秒作为环境近声。" if short else "以原片长用于明信片。"))
        meta = dict(schemaVersion=4, resourceId=resource, displayName=title, summary=summary)
        (dest / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with wave.open(str(clip), "rb") as audio:
            print(f"{key} {audio.getnframes() / audio.getframerate():.6f} s", flush=True)
