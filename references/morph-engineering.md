# 丝滑转场与真旋转罗盘：工程规范

> 目标：让「每一页之间的转换很丝滑」「目录和主题页是旋转到每一个主题的」。
> 只设一个 `morph` 转场是不够的。以下是实测有效的全部条件。

## 1. Morph 只做什么

- 微软官方：Morph 只对**两页共有对象**的 X/Y、宽高、旋转、填充色差值做插值；
- 找不到同名对象 → 退化成 crossfade（用户感知就是「硬切 / 淡入淡出」）；
- `!!Name` 强制配对：连续页对象名称唯一、1:1 对应；
- 转换器 `pptx_transitions.py` 中 `morph` = prefix `p159`、element `morph`、`option=byObject`，
  并自动写 `mc:AlternateContent` + `mc:Fallback → <p:fade/>`，旧版 PowerPoint 降级为淡入而非硬切。

## 2. 「不丝滑」的四个真实根因

| 根因 | 症状 | 对策 |
|---|---|---|
| 每页用不同底图 | 整页晃动 | 全书底图同 id / 同位置 / 同尺寸锁死 |
| 唯一配对对象是小指针 | 带不动整页，其余全淡入淡出 | 至少三个大幅面强制配对对象 |
| 配对对象 bounds 没变 | PPT 认为它没动，不插值 | Stage / Rail 的 `data-pptx-bounds` 必须逐页变化 |
| 复杂 freeform / 未扁平矢量 | Morph 中途跳形 | 主舞台组内**只用原生 `<rect>`** |

## 3. 三个强制配对对象（最小可用集）

```python
PAIRS = {
    'Stage':     {'from': 'stage',      'to': 'stage'},
    'DialRotor': {'from': 'dial-rotor', 'to': 'dial-rotor'},
    'Rail':      {'from': 'rail',       'to': 'rail'},
}
```

- key **不带 `!!` 前缀**，转换器自动生成 `!!{key}` shape name；
- `animations.json` 中 `morph` 块只接受 `{from, pairs}`；
- `transition.effect` 必须是 `morph`；`morph.from` 必须指向**紧邻前一页**的 stem；
- 首页用 `fade`，其余全用 `morph` 0.9 s（默认 2 s 太拖）；
- `order` 必须是**正整数**，`order: 0` 会被 `animation_config.py validate` 拒绝。

### `!!Stage`：镜头推进

```python
s += f'  <g id="stage" data-pptx-role="decoration" data-pptx-bounds="{x0} {y0} {bw} {bh}">\n'
s += f'    <rect x="{x0}" y="{y0}" width="{bw}" height="{bh}" fill="{SMOKE}" fill-opacity="0.12"/>\n'
s += f'    <rect x="{x0}" y="{y0}" width="{bw}" height="3" fill="{GOLD}" fill-opacity="0.62"/>\n'
s += f'    <text x="{x0}" y="{y0+bh/2:.0f}" font-size="10" fill="{GOLD_L}" fill-opacity="0.001">·</text>\n'
s += '  </g>\n'
```

- bounds 逐页变化（仪式页整幅 0,0,1280,720；内容页按主件位置收缩到半幅），
  实测 P01 宽 12,196,762 EMU → P04 宽 5,872,162 EMU，Morph 真的做镜头推进；
- 近透明 `<text>` 是确保导出成组的必要手段；
- **组内只用 `<rect>`**，不要用 `<polygon>` / `<path>` freeform。

### `!!DialRotor`：真旋转

这是最容易踩空的一环。`converter.py` 的 `supports_full_project_transform()`
在顶层 `<g>` 的子元素**全部**是 rect/circle/ellipse/line/path/polygon/polyline/image 时返回 `True`，
会把旋转烘焙进子图元，输出组 `rot=0` → **Morph 不转**。

解法（三条同时满足）：

1. **在转子组里放一个 `<text>` 子元素**（哪怕是 `·`），迫使返回 `False`，走 `rotate_pivot` fallback；
2. 只用**纯 `transform="rotate(angle cx cy)"`**，带 translate / scale 会让 `rotate_pivot=None`；
3. **pivot 必须等于组 bbox 中心**，否则 `a:off` 补偿会带来位移。

```python
s += f'  <g id="dial-rotor" data-pptx-bounds="160 136 480 480" '
s += f'      transform="rotate({angle} 400 376)">\n'
s += f'    <text x="400" y="258" font-size="12" fill="{GOLD_L}" text-anchor="middle">·</text>\n'
# ... 其余扇区 / 底盘用原生图元 ...
s += '  </g>\n'
```

- 输出应为 `rot="{angle*60000}"`；第 3 页 `rot=0` 时转换器省略属性，属正常；
- `svg_quality_checker.py` 不解析 transform，仍按未旋转子图元算 bounds，
  所以 `data-pptx-bounds` 保持**原值**即可；
- 导出后必须实测 PPTX XML 里的角度序列是逐页单调递增，确认真 rot 而非烘焙几何。

### `!!Rail`：进度轨拉长

```python
w = 1152.0 * pg / TOTAL
s += f'  <g id="rail" data-pptx-role="decoration" data-pptx-bounds="64 688 {w+14:.1f} 20">\n'
s += f'    <rect x="64" y="700" width="{w:.1f}" height="2" fill="{GOLD_L}" fill-opacity="0.95"/>\n'
s += f'    <polygon points="{64+w-5:.1f},690 {64+w+5:.1f},690 {64+w:.1f},696" fill="{GOLD_L}"/>\n'
s += f'    <text x="64" y="702" font-size="10" fill="{GOLD_L}" fill-opacity="0.001">·</text>\n'
s += '  </g>\n'
```

灰底轨 + 16 个刻度是**锁死的独立装饰，不进配对组**，否则会拖住插值。
实测组宽 783,907 → 11,025,187 EMU，Morph 真的把它拉长。

## 4. 电影感转场语言

- 同一大幅面对象跨页**缩放 / 平移**（zoom & pan），而不是每页换底图；
- `!!Name` 可做贯穿全书的 traveling element；
- 时长 0.8–1.0 s；统一转场语言，不要混用 curtains / cube / flip / origami 等杂技效果；
- 删掉 `entrance_wheel` / `entrance_grow_and_turn` / `entrance_unfold` / `page_curl` /
  `doors` / `push` / `drape` 等，只保留文字轻淡入；
- 真实转盘要「前快后慢」，匀速硬转显假（PowerPoint Morph 缓动已自带，别再叠自定义缓动）。

## 5. `animations.json` 生成骨架

```python
TRANS = {}
for i, nm in enumerate(names, 1):
    if i == 1:
        cfg = {'transition': {'effect': 'fade', 'duration': 0.55}}
    else:
        cfg = {
            'transition': {'effect': 'morph', 'duration': 0.9},
            'morph': {'from': names[i-2], 'pairs': PAIRS},
        }
    TRANS[nm] = cfg
TRANS['01_cover']['groups'] = {
    'cv-title': fx('entrance_faded_zoom', 1, 0.8),
    'cv-job':   fx('entrance_fade', 2, 0.5),
}
json.dump({'version': 1, 'slides': TRANS}, fh, ensure_ascii=False, indent=2)
```

`fx(effect, order, duration)` = `{'effects': [{'effect':..., 'order':..., 'duration':...}]}`。

**致命坑**：导出 `svg_to_pptx.py` 时**不能传 `-t` / `-a`**，否则会覆盖这个 sidecar，
所有 Morph 与入场动画全部丢失。

## 6. 验证清单

导出 PPTX 后逐项核对（可用 `scripts/audit_deck.py`）：

```
slides = 15
morph 转场 = 14（首页 fade = 1）
!!Stage / !!DialRotor / !!Rail 各 = 15
rotor angles = [-90, -45, 0, 45, 90, 112.5, ..., 337.5]  单调递增
Stage bounds 逐页有差值
Rail bounds 逐页递增
animations.json effects[].order 全为正整数
```

**静态 PDF / JPG 看不到 Morph**；须在 PowerPoint 2019/365 或 WPS「平滑」中放映。
交付时必须主动告诉用户这一点，否则用户会以为转场没做。
