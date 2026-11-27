# 蒸笼白汽

2026-11-26。已从 props-campfire 的 Smoke02 制成单发、单层白汽，沿盖边上升并向巷口偏移。原作者目录为 homeward-rain/assets/effects/effect-shore-steam。检查结果 valid，单效果根、单粒子系统。[检查](./03-steam-check.json) · [归档回执](./03-steam-archive.json)

ShoreSteam.lua 与 RainHost.lua 同挂 n48，通过 GetShoreBeat 订阅 S04B。n9 直接子节点 SteamSpout 相对 n9 取 (-9.44, 1.32, 19.7)。从该锚点一次发射约 0.62 秒，最后一批粒子在最多 1.22 秒后淡出。使用普通 Prefab 参数 Steam 绑定归档 URI。

用 Neovim 无界面 Lua 跑过选拍测试，覆盖 A 拍不播放、B 拍一次、同动作帧去重、未就绪重试、过期动作丢弃。正式场景粒子数量与视线中的效果跟随主线程的运行验收。[触发测试](./03-steam-test.lua)
