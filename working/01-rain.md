# 01 雨棚工作笔记

**最新状态（2026-11-24）**　用户确认首版手机交互正常。回信桌和雨棚已经重烘焙，试听动画和静态碰撞已分开。最终主场景根为 -1185704754，重开并保存后无未保存变更。02 可接草稿，04 可接内容，03 仍待陌生玩家的手机外放听感。手机点按时偶发只剩天空尚待新版真机复测。以[手机反馈修订记录](./01-mobile-revision.md)和[当前版本与证据](../RainStudy/Evidence/README.md)为准。下方为首次交付过程日志。

本聊天 01a206d9-117b-7490-9034-e359be2a1d76，负责 01。正式交接更新根目录 Homeward.modelWorks.md。02–06 均未认领。用户已选高品质模式，允许素材占位。本轮没有星光服务。

## 恢复现场

- 真实项目为 `%APPDATA%\AI World Creator\projects\project-268b3d7f-1770-4720-8617-933ab1a1fe14`，文件 `scene.data`，作者目录为其下 `ai-sessions/workspace_7y98mqge/wprefabs/homeward-rain`。
- 初次后台实例 awc-8138e295-436e-439a-a990-c599f69ca0b0 已退出。续作实例为 awc-38b1de62-179f-4463-aecb-1d7bba81aad8。先运行 instance status 核验。原进程已经退出时仅重启同一项目。CLI 的 project locate 不接受 workspace-id。资源修改也可能推进 WPrefab revision。
- 主 WPrefab 由本聊天装配。n1 RainStudy 是 Runtime Host，n6 盆锚点、n7 桌、n9 后续航线。主场景的基础夜景已保存，回执 homeward-night-save-01 为 committed，dirty=false。
- 已在项目 Runtime 实测，模板出生世界坐标为 (119.742,77.905,88.641)，摄像机面向 +Z，前方 12 米地形表面高 77.903。计划样段导入位置为 (119.74,78.85,88.64)，根的局部 +Z 沿玩家前进方向。局部 z=4 跨柱，TIN、BASIN、DESK 与 VOICE 的位置见 RainStudy/Runtime/foundation.js。当前项目默认出生运行已停止。
- 脚本登记为 RainHost.lua（5ef17e0b-a118-4c30-ac36-1a2e7563b0c5）、Postcard.lua（09f664cf-75c7-4064-8ef5-576b619e1875）。保留 SDK 身份行。RainStudy/Runtime/sync-scripts.ps1 可按 Card 或 Host 同步。
- 共用音频的八项 URI 和真实本地 WAV 在 RainStudy/Audio。位置与雨声拼成一个 RainHost。声音位置采用样段世界 Transform，跨柱计算用局部 Z。开场及室友声音是中文合成占位。
- UI 初版已附在 n10，正式第二版末段 URI 为 xffusbt754fr9moj.glb，横竖屏 51 节点；待以 Runtime/bind-postcard.js 在事务内替换原 UI 并绑定两个脚本。Card/verify_card.lua 的模拟控件回归已通过；尚待游戏 Runtime。
- 场景已导出五个模型，四张静态颜色图含 Blender 直接及间接光，SCAD 地图 check 包括 5 个槽和 6 个碰撞盒。雨线模板效果放在盆中心局部高度 0.224 米。场景分支正归档最终 walkway，生成真实装配脚本。其间暂缓其它作者目录写入，避免 revision 冲突。

## 当前恢复点

1. 等场景分支交出 generate-map-assembly 的操作文件，在核对 revision 后提交地图，不重复装配。
2. 重同步最终 Card 与 Host 正文（Audio/RainHost.lua + Runtime/locations.lua），执行 bind-postcard，绑定雨线效果、烘焙材质适配及可动水纹。
3. validate → build → result archive → scene import → runtime start。保留归档、wrapper root 和 runtimeId，真实桌面点击、移动、回放及截图通过后停预览、保存、重开回读，再结束自己的实例。
4. 手机点按和陌生玩家跨柱听感需要实际设备及反馈。记录事实后再开放 02/03；04 可先接已绑定的样本。

## 装配完成后的实际恢复点（取代前段待办）

主 WPrefab 已装配，共用 UI 为 n48，地图为 n11，环境 n12，盆 n35，水纹 n36。八条 AudioClip 已绑定，四个正式 Lua 已登记且预览成功加载。初版归档 yn6ecidoz659ft9f.wprefab，导入回执 homeward-rain-import-1，场景 wrapper 883234484。首轮画面 Evidence/first-pass.png。实际 W 键移动后进入铁皮听区，日志读到了同时播放的雨底、滴声及开场声音；盆雨效果返回 ready。旧显示适配只按 GLB 源模型名筛选，运行时被重命名为 campus/Model 等，匹配 0/4。现在已按运行树修改 BakedColors.lua，待重新同步、构建、归档并实测。不要重做地图和 UI 资源。旧实例可能已因空闲退出，应先核对 scene.data 中对应实例是否已保存。

## 单人实装验收

最终显示适配版 py92tigrndimq4na.wprefab，作者 revision 34edd773ecc381e0fed13989a64a5ce22b8936b8cf8378e88df834647f4907e2。已删除上一轮自己的 wrapper，正式场景唯一新根 354582227，homeward-rain-save-2 已 committed 且无残留修改。运行 9bf5675e-0f15-4e8a-81de-ac6d161357a4 的四个烘焙表面全部命中，4/0。
用 W 键依次走到铁皮、盆、桌，原始输入和屏幕状态已写入 RainStudy/Evidence/input-9bf5675e-0f15-4e8a-81de-ac6d161357a4.jsonl。铁皮两拍、重复采集不占格、两格试听、跳过、盆两拍、满卡先试听再替换、交换首尾、到桌盖章均通过。按邮戳重听的 S02A/S02B/S01A 实际 clip ID 分别为 -9390/-9392/-9386，与各格的音轨、图案、字幕一致（Evidence/replay-*.json）。已实测单格试听、设置音量/环境/字幕以及再写一封。待完成另一种顺序、停预览保存、重开和清理本轮实例。真机/陌生玩家仍待。
