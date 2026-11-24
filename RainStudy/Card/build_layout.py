"""Build the two static Douyin runtime UI HTML files from one set of controls."""
from html import escape
from pathlib import Path


RESOURCE = Path(__file__).parent / "ui-homeward-card"
INK = "#243f44"
CREAM = "#fff8e8"
PAPER = "#efe6d4"
FADED = "#4d6867"
RED = "#a24c3b"
BLUE = "#375d62"
CLEAR = "rgba(0, 0, 0, 0)"


def node(name, kind, xywh, children="", *, color=CLEAR, ink=INK, size=26, align="center", attrs=""):
    x, y, w, h = xywh
    styles = (f"position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;"
              f"background-color:{color};color:{ink};font-size:{size}px;text-align:{align};")
    if kind == "image":
        return f'<img data-u-name="{name}" data-u-type="image" style="{styles}" {attrs}>'
    return f'<div data-u-name="{name}" data-u-type="{kind}" style="{styles}" {attrs}>{children}</div>'


def button(name, xywh, label, bg=BLUE, fg=CREAM, size=28):
    w, h = xywh[2:]
    return node(name, "button", xywh,
                node(name + "Label", "text", (6, 4, w - 12, h - 8), escape(label),
                     ink=fg, size=size), color=bg)


def layout(width, height):
    portrait = height > width
    left = (width - 1000) // 2
    top = 760 if portrait else 246
    hud_top = 336 if portrait else 100
    hud = node("walkHud", "div", (left, hud_top, 1000, 132),
               node("sourceLabel", "text", (16, 8, 348, 56), "雨棚", ink=CREAM, size=31, align="left") +
               button("listenBtn", (384, 6, 170, 61), "听一听") +
               button("keepBtn", (568, 6, 180, 61), "收下这拍", RED) +
               button("cardEntryBtn", (762, 6, 226, 61), "明信片 · 0/3", "#e9dfca", INK) +
               node("walkCaption", "text", (16, 74, 968, 48), "如果只能寄三种声音回家，你会选哪三种？",
                    ink=CREAM, size=28, align="left"), color="rgba(35, 56, 59, 0.90)")
    slots = []
    for i in range(1, 4):
        box = ""
        for source, asset in [("Tin", "tinSketch"), ("Basin", "basinSketch"), ("Window", "windowSketch")]:
            box += node(f"slot{i}{source}", "image", (63, 8, 152, 152),
                        attrs=f'src="../images/{asset}.png"')
        box += node(f"slot{i}Title", "text", (6, 171, 266, 47), "待收一声", size=28)
        slots.append(node(f"slot{i}", "button", (52+(i-1)*310, 126, 278, 230), box, color=CREAM))
    operations = (
        button("playBtn", (0, 0, 202, 68), "顺序试听") +
        button("swapBtn", (222, 0, 202, 68), "交换两格") +
        button("stampBtn", (444, 0, 202, 68), "盖章寄出", RED) +
        button("soundBtn", (666, 0, 208, 68), "声音设置", "#dfd2bb", INK))
    sound = (button("rainBtn", (0, 0, 220, 68), "环境声 · 开") +
             button("captionBtn", (236, 0, 216, 68), "字幕 · 开") +
             button("quieterBtn", (468, 0, 187, 68), "音量 −") +
             button("louderBtn", (671, 0, 203, 68), "音量 +"))
    card = node("cardPanelRoot", "div", (left, top, 1000, 656),
                node("paperWakeBtn", "button", (0, 0, 1000, 656)) +
                node("mailHeading", "text", (52, 28, 630, 80), "雨夜明信片", size=46, align="left") +
                button("closeBtn", (760, 34, 172, 60), "收起", "#dfd2bb", INK) +
                "".join(slots) +
                node("postmarkBtn", "button", (52, 378, 894, 64),
                     node("postmarkLabel", "text", (8, 4, 878, 54), "寄自开学后的第一个雨夜",
                          size=28, ink=RED)) +
                node("feedbackLine", "text", (52, 458, 896, 62),
                     "点一格，听听这一声。", ink=FADED, size=28) +
                node("controls", "div", (63, 544, 874, 76), operations) +
                node("settings", "div", (63, 544, 874, 76), sound),
                color=PAPER)
    return (f'<div data-u-name="ui-homeward-card" data-u-type="div" '
            f'style="position:relative;width:{width}px;height:{height}px;'
            f'background-color:{CLEAR};z-index:12;">\n{hud}\n{card}\n</div>\n')


if __name__ == "__main__":
    for width, height in [(1920, 1080), (1170, 2532)]:
        path = RESOURCE / "html" / f"{width}x{height}.html"
        path.write_text(layout(width, height), encoding="utf-8")
