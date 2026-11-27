# 03 两岸与返航

2026-11-24，已认领。01 的桌面采样证明跨柱底雨连续，手机反馈已确认点按；分工表和 01 验收记录都仍缺陌生玩家外放听感。02 最新保存根 1978400842；后续装配从此版或更新的共有版继续。

本轮先交付 04 可直接据以制作的七处局部坐标、朝向、声画落点和分岸参考，检查走道与泊位的衔接、听区和返航路线。编辑目标为 n9 ShoreRoute，原点位于 RainStudy 局部 (0,0,10.8)。共用 UI、草稿和声轨沿用 01/02。

用户已选高品质；在入口本地测试后明确授权「本轮先完成两岸实装和桌面测试，手机听感留到之后补测」。03 持有本轮主场景装配。02 版入口试玩 14c283b7-cb86-414a-be9f-a2b5fc5d2215：从 (0,0,0) 走到 z=10.99，实测底雨 ID -5588 保持，铁皮和盆边先后发声。[采样](./03-walk-to-route.json) · [玩家视角](./03-route-entry.png)。已停止此测试实例。装配专用实例 awc-ddbc5324-307d-485b-a8c1-b53f06b9975b。两岸与船分别制作烘焙资产，航线脚本在现有 Host/Card 接入。四处新声源的坐标见[交接](../RainStudy/ShoreRoute/README.md)。

## 11 月 26 日 · 作者工程

新离屏实例见 03-instance.txt。02 原主场景备份 03-before-shores.scene.data，sha256 c9a323f2cb320730538dc2fa5b88b79a98528c804684d0422c009a229a4de97c。已归档八份 GLB、水面、十个原创占位音轨和蒸笼白汽，实际 URI 见 03-visual-uris、03-resource-uris、03-steam-archive 三份 JSON。水面 n56 已装配到 n9。航线新增三艘船、一段跳板、两岸、四件可采物件、八盏灯与出汽点；节点在 03-shore-assembly.json。Host、Postcard、BakedColors 与 ShoreSteam.lua 已同步；声音与效果参数绑定在 n48。v1 校验无诊断。后续查 03-v1-*.json、03-playtest-* 的阶段记录；先确认当前预览与主场景，再决定续跑哪一步。

## 11 月 27 日 · 已保存 v2

v1 真实输入六段全部通过，见 03-playtest-a9d762f9-989a-40ac-944c-f6f1d77c0ff7/progress.json，含早返再出发、旧声卡、含室友的卡及乙跨岸采集的同机合写。v2 新增远岸屋脊 n100、船头可转向的投射光和可随选择提亮的玻璃灯罩。已重新校验、构建、归档、导出及保存。磁盘主场景只有当前新版根 -1615574970；归档 voe53ae13koo3pbf.wprefab，导出 RainStudy/Homeward-shores.wprefab SHA256 bec2ba6d06ad67697b3f57ea813bb891b4c5b978e48c1f0fb49143c2d2cd47fb；03-v2-save 已 committed/clean。原场景与导出包 CRC 检查通过。下一步只检查磁盘重开后的船灯/天际线、蒸汽动作时序、以 S07A 为末格的卡，完成后停本轮实例、写 05 交接及更新状态表。

已完成重开复验并释放装配。d2db2a8d-e23a-409f-be9a-b931b79b9e1a 实测双向船灯、蒸汽 0→14→0、笼盖升起 0.11 米、换岸、替换与换序、盖章及邮戳重播。最终卡的 S07A 在末格。03-v2-final-hooks 无残留，03-v2-instance-stop 已停止。04、05 从[正式交接](../RainStudy/Evidence/03-shore-route.md)续做；后续只需按新材料替换及手机真人反馈复测。
