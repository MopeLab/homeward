# 雨棚样段声音交接

线程 04 的当前制作版包含 14 段独立卡片音轨、雨夜 / 晨市 / 暮路三段 24 秒循环底声、碗边短滴、开场语音和盖章提示声。[当前绑定表](./bindings.json) 列出全部 20 个音频引用，[七组声画内容](../Evidence/04-content.md) 记录现行片段和验证。

### 当前音轨与来源

| 键 | 文件夹位于 `assets/` | 秒 | 版本与使用说明 |
| --- | --- | ---: | --- |
| S01A | audio-tin-scatter | 2.45 | 01 原创拟音 v1 |
| S01B | audio-tin-strike | 2.65 | 01 原创拟音 v1 |
| S02A | audio-basin-drips-recorded | 19.090 | 交付的 `SFX/S02A.wav`，连续雨滴落在搪瓷碗 |
| S02B | audio-basin-late | 2.90 | 01 原创拟音 v1 |
| S03A | audio-shutter-chain | 2.60 | 04 原创拟音 v1 |
| S03B | audio-shutter-stop-recorded | 3.242 | 交付的 `SFX/S03B.wav` |
| S04A | audio-steamer-lid | 2.35 | 04 原创拟音 v1 |
| S04B | audio-steamer-steam | 2.75 | 04 原创拟音 v1 |
| S05A | audio-bell-double-recorded | 1.624 | 交付的 `SFX/S05A.wav` |
| S05B | audio-bell-tail | 3.10 | 04 原创拟音 v1 |
| S06A | audio-lock-keys | 2.55 | 04 原创拟音 v1 |
| S06B | audio-lock-open-recorded | 2.138 | 交付的 `SFX/S06B.wav` |
| S07A | audio-window-call-recorded | 1.802 | 制作方提供的 `Voice/S07A_01.wav` |
| S07B | audio-window-steps | 3.00 | 01 原创拟音 v1 |
| RainBed | audio-rain-bed | 24.00 | 01 原创循环底声 v1 |
| MarketBed | audio-market-bed | 24.00 | 04 原创循环底声 v1 |
| DuskBed | audio-dusk-bed | 24.00 | 04 原创循环底声 v1 |
| BasinAccent | audio-basin-accent-recorded | 2.800 | 从 S02A 取前三次滴声，用于碗边背景近声 |
| FamilyVoice | audio-family-voice-recorded | 3.318 | 制作方提供的 `Voice/FamilyVoice_01.wav` |
| Postmark | audio-postmark | 0.36 | 04 原创拟音 v1 |

原创程序拟音由 Homeward 制作组生成，可用于本作品、剪辑和参赛演示，可署名 Homeward 制作组。01 和 04 的拟音分别由 `make_foley.py` 与 `make_shore_foley.py` 重建。两句现用对白来自用户指定的 WAV，保留完整片长，从 44.1 kHz 单声道浮点转成单声道 16 位 PCM 归档，沿用 `FamilyVoice` 和 `S07A` 绑定键。

### 交付音效的来源与处理

四条可采音效沿用交付 WAV 的起止采样，转单声道 16 位 PCM 入包。按同批 `SFX` 目录里的原文件名登记来源。考虑到 19.09 秒的 A 拍用于主动试听和卡片，盆边环境位另用前 2.8 秒，加短尾部淡出。

| 音轨 | 来源及署名 |
| --- | --- |
| S02A、BasinAccent | TRP 的金属器皿滴水录音，Freesound CC0。[原条目](https://freesound.org/people/TRP/sounds/567941/) |
| S03B | ZapSplat 卷帘门录音，原下载文件编号 43838。项目署名写「Sound effects from ZapSplat」。[署名说明](https://www.zapsplat.com/how-to-credit-us/) |
| S05A | manofham 的双响车铃，Freesound CC0。[原条目](https://freesound.org/people/manofham/sounds/701038/) |
| S06B | fuzzpapi 的开锁声，Freesound CC0。[原条目](https://freesound.org/people/fuzzpapi/sounds/147347/) |

## 01 样段原始交接

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
