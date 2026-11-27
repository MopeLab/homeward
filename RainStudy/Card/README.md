# 雨夜明信片

线程 04 已补齐卷帘门、蒸笼、车铃、门锁四张速写。和 01 的铁皮、雨盆、宿舍窗一起接入横竖屏三格卡，每格可显示七张图之一。四图来自同一份 [岸上图集](./shore-sketch-atlas.png)，可通过 `shore-atlas-arguments.json` 和 `shore-atlas-supply.json` 重制。成品 [封面](../Cover/Homeward-cover.jpg) 使用同场雨的冷暖两侧、蓝边盆和末班船，标题用霞鹜文楷，副题用 Noto Sans SC。

雨棚样段复用同一张明信片处理收声、满卡替换、调整顺序、盖章与回放。起步时只显示一小条采集栏。到暖窗旁的回信桌后，三格收满就能盖章。回放结束后点纸面空白可唤回操作栏，点邮戳重听，点格子单听。

## 02 的单人草稿接口

作者 WPrefab 为 `homeward-rain`，UI 资源为 `ui-homeward-card`。维护 `RainCard.lua`，同步到该 UI 宿主已经登记的 `Postcard.lua`，保留编辑器生成的脚本身份行。同一宿主的 `RainHost.lua` 提供接近区域、播放、停止和混音。

`GetDraft()` 返回两个值。第一个是按格序复制的数组，每格形如 `{source="S02", beat="B"}`；第二个是本局是否已经盖章。02 可读取副本并独立保存合写状态。正式与他人合写的入口和同步仍归 02 制作。

## 01 提供给 04 的内容样本

| 编号 | 蓄势 A | 落点 B | 卡面图片 |
| --- | --- | --- | --- |
| S01 铁皮 | 棚上碎雨 | 铁皮重滴 | `tinSketch.png` |
| S02 搪瓷盆 | 盆中双响 | 迟来一滴 | `basinSketch.png` |
| S07 宿舍窗 | 走啦，吃饭去 | 远去的脚步 | `windowSketch.png` |

以 S02B 为例，`RainCard.lua` 的 `catalogue.S02.B` 给出短标题和字幕。播放器接收 `PlayBeat("S02","B")` 并返回片长。音频引用在 `../Audio/bindings.json` 的 `S02B`，动作入口在 `../Runtime/locations.lua` 的 `HostBeat`。任一格选择 S02 时，显示该格的 `slot1Basin`、`slot2Basin` 或 `slot3Basin`。三格使用相同构图，顺序随玩家草稿。

图像来自本次生成的铁皮、盆、窗三幅钢笔淡彩速写，统一深蓝墨色和留白。原图集是 `sketch-atlas.png`，正式 UI 使用 `ui-homeward-card/images/` 中造世界切出的三幅透明 PNG。04 更换同名图后可沿用控件路径。新增岸上物件时，将新图片加入 `build_layout.py` 的三格图层，并在 Lua 的 `catalogue` 和 `artNames` 加相应条目。运行 `python RainStudy/Card/build_layout.py` 更新横竖屏 HTML，然后在原作者资源 check、archive，并更新已有实例。

三幅并排的纸卡及收声 HUD 使用自写 HTML，两种方向共享控件名。归档时横竖屏检查均完成，51 个控件节点、9 个图片节点。`verify_card.lua` 用模拟按钮和播放器执行实际 Lua 的状态回归，包含两种按序回放、满卡确认与取消路径中的草稿保护、空白纸面、未就绪宿主和监听清理。真机外放与点按记录见项目交接表。
