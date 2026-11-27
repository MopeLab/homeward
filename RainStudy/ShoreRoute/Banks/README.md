# 晨市与暮路模型

米制尺寸，Unity 的 Y 轴向上。泊位内朝 +Z 上岸。每个模型以其摆放点为原点，位置应用一次，安装时保留 1 倍比例。两岸地面分别覆盖本地 X −3.2 至 3.2 米，Z −1.8 至 11.5 米。暮路高程在 Z 为 2 至 9 米的区间由 0 爬至 0.7 米。

| 文件 | RainStudy 根下 Unity 位置 (x, y, z) | 固定材质 | 可动节点及动作 |
| --- | --- | --- | --- |
| market-bank.glb | (−11, 0, 22) | GI-MarketMasonry | 半开的卷门店面、横棚、灶摊和石铺地 |
| dusk-bank.glb | (11, 0, 22) | GI-DuskMasonry | 水泥坡、护栏、错落住宅与下垂电线 |
| shutter.glb | (−12.8, 0, 25.4) | GI-ShutterFrame | ShutterEdge 整片短距离上移、顿住 |
| steamer.glb | (−9.2, 0, 30.5) | GI-SteamerHearth | SteamerLid 枢轴在远侧盖沿，可沿本地 Z 轴掀开 |
| bicycle.glb | (9.2, 0.14, 25.4) | GI-BicycleFrame | BellCap 枢轴在车把铃帽底，短暂摇摆 |
| door.glb | (12.8, 0.65, 30.5) | GI-DoorFrame | DoorLeaf 枢轴在铰链侧，沿本地 Y 轴向屋内开一指宽 |

每份 GLB 含一张烘焙 PNG。两岸环境各 1536 × 1536，四件道具的静态主体各 512 × 512。六个固定接收者同场计算，保留四个可动部件的原材质供实时受光。场景以创作参考设计了清晨暖主光、蒸摊灯、暮色面光和门内灯，环境填光近似夜水上方的漫射天空。Cycles 采用 48 个采样、最多 5 次反弹，其中漫反射最多 3 次，Diffuse 烘焙包含 COLOR、DIRECT、INDIRECT。生产日志见 [bake.log](./bake.log)。

[build_banks.py](./build_banks.py) 可在 Blender 5.3 后台执行，保存着色前后分离的母版与各 GLB，模型源坐标顺序沿用 01 的 (Unity x, z, height)。可用 [banks-master.blend](./banks-master.blend) 修改原材质、灯与遮挡。[preview_banks.py](./preview_banks.py) 将导出的真实 GLB 重新导入 Blender，按固定光照显示六张烘焙图并拍摄泊位视角。两份预览为[晨市](./market-baked-preview.png)和[暮路](./dusk-baked-preview.png)。编辑器与手机显示情况由整图运行记录说明。
