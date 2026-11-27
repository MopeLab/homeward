"""Set the title and question on the 16:9 cover illustration with local fonts."""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


folder = Path(__file__).resolve().parent
fonts = Path(os.environ["WINDIR"]) / "Fonts"
image = ImageOps.fit(Image.open(folder / "rain-crossing.png").convert("RGB"), (1600, 900),
                     Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(image)
title = ImageFont.truetype(str(fonts / "LXGWWenKai-Medium.ttf"), 106)
question = ImageFont.truetype(str(fonts / "Noto Sans SC (TrueType).otf"), 27)
draw.text((179, 85), "听见来处", font=title, fill="#fff3db", stroke_width=1, stroke_fill="#fff3db")
draw.text((187, 219), "如果只能寄三种声音回家，你会选哪三种？", font=question, fill="#f1e4d4")
image.save(folder / "Homeward-cover.jpg", quality=94, subsampling=0, optimize=True)
