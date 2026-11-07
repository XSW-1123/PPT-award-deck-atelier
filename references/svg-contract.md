# SVG 页面契约、质量门禁与动画 Schema

> 底层转换器为 `ppt-master` 的 `svg_to_pptx.py`。本文件只记录**踩过坑**的契约细节，
> 完整 SVG 语法以 `ppt-master/references/semantic-svg.md` 为准。

## 1. 页面契约

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"
     width="1280" height="720" data-pptx-page-role="content"
     font-family="Microsoft YaHei" lang="zh-CN">
  <defs>...</defs>
  <rect id="bg" data-pptx-role="decoration" .../>
  <image id="bg-art" data-pptx-role="decoration" href="../images/haze_01.jpg" .../>
  <g id="stage" data-pptx-role="decoration" data-pptx-bounds="0 0 1280 720">...</g>
  <g id="hero" data-pptx-bounds="64 214 1152 400">...</g>
  <g id="notes" data-pptx-bounds="64 630 1152 44">...</g>
</svg>
```

### 硬规则

| 规则 | 说明 |
|---|---|
| 每个语义单元一个**直接 root** `<g id data-pptx-bounds>` | 嵌套组不能作为语义单元 |
| `data-pptx-bounds="x y w h"` | 四数空格分隔；相邻 sibling bounds 重叠 > 1 px 即 error |
| id 全书 / 全页唯一 | 重复 id 会被判冲突 |
| 背景 / 导航 / 页码 | 标 `data-pptx-role="decoration"` |
| **可见 root 组即使标了 decoration 也必须显式写 bounds** | `final` 门禁实测：漏写直接判 Failed |
| 跨多组的横线 / 网格 / 台账 | 必须放进一个 `decoration` 组，否则 bounds 跨组触发重叠 error |
| 巨型文字估算框不能超 viewBox | 200 px 字在 y=652 会下探到 722，改 y=632 + bounds 调整 |

### 转换器明确不支持

- `clip-path`、`<mask>` → 圆形遮罩 / 镂空 / 花瓣 / 剪影一律预烘焙成带 alpha 的 PNG；
- `<polyline>` → 用 `<path d="M… L…">`；
- `stroke-dasharray` → 拆成短 `<line>`；
- `<pattern>` → 手画重复线段；
- `<path d="A..."` 圆弧 → 用离散点 `<polygon>`（`arc_poly()`）。

### 图片引用

- 相对路径 `../images/<name>`，从 `svg_output/` 目录看；
- `preserveAspectRatio="none"` + 显式 width/height；
- 底图全本同 id / 同位置 / 同尺寸锁死（Morph 前提）。

## 2. 质量门禁

从 **ppt-master 项目根**执行，不能从 svg 目录执行：

```bash
python <ppt-master>/scripts/svg_quality_checker.py svg_output \
       --canonical-authoring --stage final --json
python <ppt-master>/scripts/svg_to_pptx.py . -o deck.pptx
```

- `--json` 会刷新 `validation/svg_quality_report.json`；
  **导出前必须重跑**，否则报 `default release export requires a passing final SVG quality report`；
- `--stage final` 会检查字号 recurrence：任何 `font-size` 出现 > 2 次，
  必须在 `spec_lock.md` 的 `## typography` 中声明对应角色：
  ```markdown
  ## typography
  - dial_core: 100
  - gauge_value: 56
  - ghost_cn: 200
  ```
  用 `scripts/sync_spec_lock.py` 扫 15 张 SVG 自动反推补齐，不要手填；
- `animation_config.py` 不能单独直接跑（相对导入 / `hyperlink_contract` 路径），
  以 `svg_to_pptx.py` 内部校验为准；
- 导出**不传 `-t` / `-a`**，否则覆盖 `animations.json`。

## 3. `animations.json` Schema

```json
{
  "version": 1,
  "slides": {
    "01_cover": {
      "transition": {"effect": "fade", "duration": 0.55},
      "groups": {
        "cv-title": {"effects": [{"effect": "entrance_faded_zoom", "order": 1, "duration": 0.8}]}
      }
    },
    "02_toc": {
      "transition": {"effect": "morph", "duration": 0.9},
      "morph": {
        "from": "01_cover",
        "pairs": {
          "Stage":     {"from": "stage",      "to": "stage"},
          "DialRotor": {"from": "dial-rotor", "to": "dial-rotor"},
          "Rail":      {"from": "rail",       "to": "rail"}
        }
      },
      "groups": {
        "tc-1": {"effects": [{"effect": "entrance_rise_up", "order": 1, "duration": 0.45}]}
      }
    }
  }
}
```

| 字段 | 约束 |
|---|---|
| `transition.effect` | `fade` / `morph` / 其他预设名 |
| `morph.from` | 紧邻前一页的 stem（不带扩展名） |
| `morph.pairs` | 非空；key 不带 `!!`；值 `{from, to}` 为 SVG 组 id |
| `groups` | key 必须是**直接 root 组** id；嵌套组不生效 |
| `groups[gid].effects[].order` | **正整数**，0 会被拒绝 |
| `effects[].duration` | 0.4–0.9 s 为宜 |

### `!!` 配对机制

`animation_config.py` 的 `MorphPair.shape_name` 返回 `f'!!{self.key}'`。
`scan_svg_targets()` 允许 `data-pptx-role="decoration"` 的 root 组被显式 sidecar 配对，
但**不能是 structural group**。因此 Stage / Rail 虽是 decoration，仍可被配对。

## 4. `spec_lock.md`

项目级设计约束文件，至少包含：

```markdown
## typography
- <角色名>: <字号>

## constraints
- visual_style_behavior: 每页版式不重复
- 主色 ≤ 3，字体 ≤ 2 类，留白 ≥ 30%
- <官方硬约束：字数 / 图表 / 文件大小 / 页数>
```

把官方材料规范写进这里，并在生成脚本里用 `assert` 自检。

## 5. 构建脚本的工程习惯

- 用 `patch_vNN.py` 从上一版生成 `build_vNN.py`，**每次替换都 `assert s.count(old) == 1`**，
  避免 f-string 行尾多一个空格就静默失配；
- 按注释锚点 `replace_section()` 替换页面段，别用脆弱的行号；
- 重写页面时容易漏 `P0X = p` 与 `</svg>` 闭合 → 用正则批量补齐后逐页 XML 解析验证；
- 模块级常量覆盖是换色最省事的做法：在文件末尾重新赋值 `DEEP/PAPER/GOLD…`，
  所有沿用旧常量的页面代码自动换色，不必逐页改；
- 生成 15 张 SVG 后立即写 `animations.json`，再跑门禁；
- 每条构建命令都要确认「实际执行了」，不要假设成功（GPU / 文件锁 / 路径都会导致静默跳过）。

## 6. 页数名册参考

```
01_cover 02_toc 03_sec1 04_self 05_sec2 06_job 07_goal 08_sec3
09_academic 10_project 11_ability 12_sec4 13_fix 14_plan 15_end
```

四章八字对仗标题示例：`壹 知己知彼，审视自我 / 贰 洞察岗位，锚定方向 /
叁 笃行不怠，蓄力成长 / 肆 复盘迭代，行稳致远`。
