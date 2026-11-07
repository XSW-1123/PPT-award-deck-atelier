# 惊艳技法库

> 技法按「解决什么问题」组织。每个技法给出实现要点、参数和真实踩坑。
> 所有透明素材统一用 `scripts/make_atmosphere.py` 生成。

## 1. 旋转罗盘（仪式母题）

### 结构（三层，缺一不可）

```
固定外圈  halo / 环 / 24 刻度 / 四方位箭头 / 正立罗马数字 I–IV / 固定 bezel 12 刻度
  ↓ 不参与 Morph 配对，逐页锁死 —— 指针相对它转动才「肉眼可见」
真旋转转子  dial-rotor（唯一带 rot 的组）
固定轮毂  dial-hub（核心圆 + 书法章字 + PART 副标 + 正立 N 标）
```

- 全书角度表单调递增，四章恰好落在 0 / 90 / 180 / 270，金色扇区依次对准 I(上)/II(右)/III(下)/IV(左)；
- 15 页参考角度：`-90, -45, 0, 45, 90, 112.5, 135, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5`；
- **同一个 `!!DialRotor` 出现在全部页**：目录 / 章节页是 480 px 大盘，内容页收进顶栏 48–64 px 小盘，
  封面可 `quiet=True` 隐形，结尾 `closing_dial()` 放大成收束盘。
  Morph 会自动做「大盘缩小飞入顶栏 / 展开回大盘」，圆盘不再「突然出现」。
- 用户要「最后翻页才出现」：封面删大罗盘，用隐形指针配对；结尾新增收束罗盘。

### 几何：只用原生图元

```python
def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)

def arc_poly(cx, cy, r0, r1, a0, a1, n=28):
    """环形扇区：离散点构造，避免 <path d="A..."> 的解析风险。"""
    pts = [polar(cx, cy, r1, a0 + (a1-a0)*i/n) for i in range(n+1)]
    pts += [polar(cx, cy, r0, a1 - (a1-a0)*i/n) for i in range(n+1)]
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
```

- 圆盘几何全部用 `<circle>` / `<line>` / `<polygon>`；
- 中心圆与扇区内环之间**必须补实心底圆**，否则会透出一圈背景照片（实测硬伤）；
- 目录四行卡改「无缝连排、深浅交替 + 细金分隔线」的连续面板，
  不要留 14 px 缝隙——缝隙会透出底图亮带和杂物。

### 真旋转的工程条件

见 `morph-engineering.md` §3。最关键一条：**转子组里放一个 `<text>` 子元素**，
否则转换器把旋转烘焙进子图元、组 `rot=0`，Morph 根本不转。

---

## 2. 编辑式证据大版面（内容母题）

- 超大字号（64–166 px）+ 非对称明暗分区 + 大留白 + 每页一句过渡句；
- 一页一个主件，八页八种：巨数证据 / 四列岗位卡 / 六行对照条 / 分数柱 / 时间 ribbon /
  六行刻度尺 / 左右复盘对照 / 三级阶梯；
- 明暗交替：3 页深蓝反白、5 页浅底，产生翻页节奏；
- 标题区统一用浅米纸压底（0.68），深字标题才能保证可读；
- 深色页不放巨型书法水印、不放「对应评分项」胶囊；
- 底部 `notes` 组：48×3 金条 + 一句结论，全本同位置锁死。

**内容页与仪式页的分工**：罗盘 = 仪式；内容页 = 块面 / 坐标系 / 流程 / 对照。
靠固定底图 + 顶栏 + 页脚 + 书脊 + 进度轨保持统一，不靠复用同一个图形。

---

## 3. 信息图主件（八种，见 style-presets S4）

- 圆形一律 `polar/arc_poly` 离散点；扇环填充比例用「实扇区 + 空心扇区」表达，别叠两层半透明；
- 雷达图标准画法：金色轮廓 = 基线，深色实填 = 现状（比两层半透明叠加清楚得多）；
- 刻度尺三级高度 8 / 13 / 26 px + 金色倒三角 + 两端标签，1.3 px 实基线；
  7 px 半透明浅刻度在纸白上像脏污，不可用；
- 曲线图必须有白卡 + 网格 + 实坐标轴 + 左上横排图例；标注落在两条线之间的空白带，不要压线；
- 卡片下半空白用 64 px `fill-opacity=0.075` 幽灵编号填右下，不要留真空白。

---

## 4. 朦胧背景（真实摄影 + 局部渐变蒙版）

**核心原则**：把渐变融合和局部压暗**烘焙进 JPG 本身**，SVG 里只留 0.10–0.12 极淡罩。
理由：转换器不处理 clip-path / mask / gradient rect；且深色玻璃盖上去会让背景等于没加。

```python
def veil_mask(direction, lo, hi, power=1.0):
    """L = 左浅右深；R = 左深右浅；V = 上浅下深。0 保留照片，255 压到暖墨。"""
    n = W if direction in ('L', 'R') else H
    vals = []
    for i in range(n):
        t = i / float(n - 1)
        if direction == 'R':
            t = 1.0 - t
        vals.append(int(255 * (lo + (hi - lo) * (t ** power))))
    m = Image.new('L', (n, 1) if direction in ('L', 'R') else (1, n))
    m.putdata(vals)
    return m.resize((W, H))
```

- 模糊别过头：深色页 3.5 px、浅色页 7.0 px；14 px 会把主体全抹掉；
- 统一暖调 blend：深色 0.14、浅色 0.46（0.76 会让照片几乎消失）；
- 方向按文字位置定：文字在左 `R`、在右 `L`、内容页 `V`；
- 全书底图**同 id、同位置、同尺寸锁死**，只做柔和交叉溶解，Morph 才不晃；
- 图片必须与本页内容相关（工程师岗放代码 / 工位 / 机柜），不用通用风景；
- 逐张目视确认无水印、无叠加文字、无角标署名。

---

## 5. 圆形遮罩 / 镂空蒙版 / 花瓣 / 剪影

`svg_to_pptx` 明确拒绝 `clip-path` 和 `<mask>`，因此**一律预烘焙成带 alpha 的 PNG**，
再以普通 `<image>` 插入；每个素材包一个带 `data-pptx-bounds` 的 root `<g>`。

### 圆形柔边遮罩

```python
def soft_circle_mask(size, pad=10, blur=14):
    m = Image.new('L', (size, size), 0)
    ImageDraw.Draw(m).ellipse((pad, pad, size-pad, size-pad), fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))
```

- 无 crop 时**不要**用 cover_crop 做圆形遮罩（会把亮天空放大成白斑），保持直接拉伸；
- 过曝天空用亮部 LUT 只压亮部：`i * (1 - k * (i/255)^2)`，k=0.12–0.20；
- 若必须裁切，取建筑立面 / 主体，避开天空（如 `crop=(0.20,0.28,0.78,0.86)`）。

### 镂空蒙版（合并形状「剪除」）

```python
ov = Image.new('RGBA', (w,h), tint + (150,))
m  = Image.new('L', (w,h), 255)
ImageDraw.Draw(m).ellipse(hole, fill=0)
m  = m.filter(ImageFilter.GaussianBlur(16))
edge = Image.new('L', (w,h), 0)
ImageDraw.Draw(edge).rectangle((70,70,w-70,h-70), fill=255)
edge = edge.filter(ImageFilter.GaussianBlur(46))
ov.putalpha(ImageChops.multiply(ImageChops.multiply(ov.getchannel('A'), m), edge))
```

alpha 150、四周羽化 70、blur 46 才能去掉「方块感」。

### 花瓣放射

12 片细长纺锤花瓣（19 点正向 + 19 点反向构成多边形），每片 alpha 36，
合成后 blur 3.0。**只作罗盘背后的底纹，透明度 ≤ 0.20，绝不当主视觉。**

### 远山剪影

三条正弦叠加生成山脊，底部填实、顶部透明，全本同一条、同一位置，
深色页 opacity 0.055 / 浅色页 0.105。给纸白区一点真实景物轮廓即可。

---

## 6. 卡片柔影与微上浮

- 柔化偏移阴影代替硬边框；「有填满就无外框」；
- 目录四行卡用 `entrance_rise_up` 逐个升起（order 1..4、duration 0.45）；
- 嵌套在 `hero` 内的卡片**不能**成为 direct-root 动画组（sidecar 只认 root 级），
  改用静态偏移柔影 + 第二张略高 6 px 表达同一手感，不要为凑动画破坏版式层级；
- 可用动画预设：`entrance_rise_up` / `entrance_float` / `entrance_ascend` /
  `entrance_faded_zoom` / `entrance_fade` / `entrance_grow_and_turn`。

---

## 7. 统一线索（全本锁死，不参与配对）

| 元素 | 规格 |
|---|---|
| 底图 | 1280×720，全本同 id / 同位置 / 同尺寸 |
| 顶栏 | 2 px 金线 + 64 px 小转子 + 固定 12 刻度环 |
| 书脊 | 左侧 34 px 深色 + 2 px 金线，章字 / 竖排英文 / 页码 |
| 方格 | 128 px 间距，`stroke-opacity=0.045`，矢量不用照片 |
| 页脚带 | y=618，高 76，`SMOKE` 0.68 |
| 进度轨 | 灰底轨 + 16 刻度锁死；金色进度条 + 游标单独成 `!!Rail` 组，组宽逐页增长 |
| 巨型水印 | 200 px 章字，透明度 ≤ 0.05，仅浅底页 |

> 矢量极淡方格替代雪山照片：0.09 透明度下云层在纸白区像脏水印，用户明确反感。
