# 暮路船头的动态水纹

11 月 28 日从水岸修订版继续。主场景保存根为 766109963，归档 ffynlcjxtl9fa75t。[可导入版本](../Homeward-ripples.wprefab) · [磁盘及导出校验](../../working/03-ripples-disk.json)

旧材质把河面各处画在一张图上，运行时还使用 DXT1 块压缩。新版每 4.8 米使用一张 512 像素宽的无缝细纹，近处每米约 107 个纹理像素。运行时实测底色与发光层共用一份 RGB24 纹理，附十级渐远细节，两层的方向和速度不同。雨滴在水面生出扩散、消退的细圈，踏出船岸时触水位置会出现一大一小两圈。

在相同泊位、相同镜头方向和 70° 俯角下，分别拍摄了[旧版原图](../../working/03-ripples-before/暮路俯视.png)与[新版原图](../../working/03-ripples-final/暮路俯视.png)。保持角色静止，连续采样确认水纹偏移、雨圈大小与透明度都在变化。从暮路船实际走出船侧触发一次触水并回到甲板，随后顺利换至早市。[运行数据](../../working/03-ripples-final/animation.json) · [步行与换岸结果](../../working/03-ripples-final/passed.json)

从磁盘重开后，船头俯拍确认实际使用 RGB24 水纹、十级渐远细节和 12 个复用的涟漪对象。动图由同一固定机位的 22 张桌面运行画面按游戏时间间隔合成。手机端本轮未测。[重开动图](./03-river-waves.webp) · [原尺寸船头截图](../../working/03-ripples-reopen/暮路船头俯拍.png) · [重开检查](../../working/03-ripples-reopen/check.json)
