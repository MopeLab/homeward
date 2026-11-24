# 雨棚样段声音交接

01 样段使用 8 个已归档的单声道 WAV。六段可采，另有开场语音和一条连续雨底。每个可采片段由声源号和拍号唯一确定。A 是蓄势，B 是落点。三格卡按玩家选定的顺序存这两个字段，回放沿用相同的片段、图案和字幕。

## 编号与动作

| 声源号 | 物件及卡图 | A 的动作 / 音轨 | B 的动作 / 音轨 | 01 素材 |
| --- | --- | --- | --- | --- |
| S01 | 波纹铁皮 | 散滴，细小颤动 / audio-tin-scatter，2.45 秒 | 重滴，棚顶抖一下 / audio-tin-strike，2.65 秒 | 两段 |
| S02 | 蓝边搪瓷盆 | 两滴紧挨，两圈水纹相叠 / audio-basin-double，2.40 秒 | 隔一拍落在盆心 / audio-basin-late，2.90 秒 | 两段 |
| S03 | 半开店门 | 链条绷紧，门沿开始上移 | 卷门顿住，门沿轻颤 | 留给 04 |
| S04 | 两层竹笼 | 竹盖轻碰，盖沿翘起 | 蒸汽呼出，白汽掠过灯光 | 留给 04 |
| S05 | 车把与铃 | 铃舌连击两下 | 铃声渐远，铃帽复位 | 留给 04 |
| S06 | 钥匙和门缝 | 钥匙相碰、试齿 | 锁舌转开，门缝亮起 | 留给 04 |
| S07 | 开着的窗 | 楼下招呼 / audio-window-call，2.449 秒 | 脚步走远 / audio-window-steps，3.00 秒 | 合成语音、拟音 |

雨棚内可制作对照样卡。依次收下 S01B「铁皮重滴」、S02A「两圈水纹」、S07A「走啦，吃饭去」，在桌上交换首末两格后盖章，应先听见招呼，随后盆声，最后铁皮。完整策划中的例卡顺序是 S01B、S06B、S07A，等待 04 提供门锁片段。

## 音频来源与替换

| 音频 | 来源与版本 | 使用情况 |
| --- | --- | --- |
| S01A、S01B、S02A、S02B、S07B、RainBed | 01 以噪声、非谐振模态、气泡扫频和步声包络合成，版本 v1。可用 Python 3、NumPy 执行本目录 `make_foley.py` 重建。RainBed 的资源名为 audio-rain-bed，24 秒循环。 | 项目原创样音，可剪辑、替换与调音。雨声待普通手机外放盲听。 |
| FamilyVoice、S07A | Windows 离线普通话 Microsoft Huihui Desktop 合成，v1。FamilyVoice 对应 audio-family-voice，约 4.618 秒。台词分别为“你那边也下雨了？我刚把窗关上。”和“走啦，吃饭去！” | 开发测试占位。参赛录制前换成获授权的人声，补录制者、允许用途、剪辑许可与署名。 |

作者输入按 `assets/<resource-id>/audio.wav` 和 `meta.json` 成对保存。八份归档回执返回 completed，归档的 contentHash 已与仓库 WAV 的 SHA256 逐项对齐。[绑定表](./bindings.json) 可直接传给 `scene.scripts.setParams({bindings:[bindingHandle], values: bindings})`，第一次绑定也可作为 `scripts.bind` 的 params。替换音频需重新归档目标资源并更新该键的 URI。每个键另有独立的 Volume 和 MaxDistance 字段。

[RainHost.lua](./RainHost.lua) 提供 PlayBeat、StopBeat、SetMix、UpdateRain。主线程在其后拼接 HostStart、HostUpdate、HostBeat 和 GetStudyFrame 并保留作者脚本身份。雨底、铁皮和盆的音源跟随样段坐标系，卡片试听跟随玩家摄像机。给 04 扩写时沿用 S03A 至 S06B，补入图案、标题、字幕和实际片长，再用主场景做归档后试听。
