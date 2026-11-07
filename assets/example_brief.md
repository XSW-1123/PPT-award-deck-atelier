# 示例：一段需求描述 → 完整风格路由

> 完全脱敏的示例，用来演示「根据用户描述自主选风格」这一步该输出什么。
> 不含任何真实姓名、学校、成绩、照片或私有路径。

## 输入（用户原话，示例）

> 帮我做一份竞赛答辩的 15 页 PPT，四个章节。目录和主题页要那种旋转到每个主题的效果，
> 翻页要很丝滑。别做得像 AI 模板，配色别全是蓝的，最好有朦胧背景，
> 而且背景要贴每一页的内容选。内容页也要惊艳，别每页都长一样。

## S0 · 需求解码

| 维度 | 抽取结果 |
|---|---|
| 场合 | 竞赛答辩（有官方材料规范，需先复核字数 / 图表 / 文件大小上限） |
| 情绪 | 惊艳、高级、不要 AI 味 |
| 结构 | 15 页、4 章、成长 / 路径叙事、有数据证据 |
| 硬约束 | 必须旋转到每个主题、必须丝滑、必须去 AI 味、朦胧背景按页选图、每页版式不重复 |
| 素材 | 可用真实摄影（需用户自备或合法图库），无品牌色 |

默认假设（用户未说）：16:9 1280×720；主色 ≤ 3；字体 ≤ 2 类 + 数字衬线体；
封面 / 目录 / 4 章节 / 结尾为深色仪式页，8 张内容页浅底；Morph 0.9 s。

## S1 · 风格路由输出

```
选用预设    → S1 warm-editorial-compass
排除        → S2（corporate blue，2026 已过时且与「别全是蓝」冲突）
              S3（图纸模板套八次，与「每页别一样」冲突）
              S4（圆盘复用，与「旋转只给主题页」冲突）
              S7（克制路线与「惊艳」冲突）
仪式母题    → 固定外圈 + 固定 12 刻度环 + 唯一真旋转转子
              仅 P02 / P03 / P05 / P08 / P12 出现大罗盘；P01 隐形指针；P15 收束罗盘
内容母题    → 编辑式证据大版面，八页八种主件，互不重复
配色        → #F3EFE6 暖象牙 / #2C2A26 暖炭墨 / #9C7746 铜褐
              辅助 #6B4E28 #C3A36E #F0E6CE #A8A399；自检偏蓝 hex = 0
字体        → STXingkai 标题 / Microsoft YaHei 正文 / Georgia 数字
转场        → 首页 fade 0.55s + 14 页 Morph 0.9s
              !!Stage / !!DialRotor / !!Rail 三对象强制配对
页数骨架    → 01_cover 02_toc 03_sec1 04_self 05_sec2 06_job 07_goal
              08_sec3 09_academic 10_project 11_ability 12_sec4
              13_fix 14_plan 15_end；深色页 7 页
每页主件    → P04 巨数证据 + 刻度尺 / P06 四列职责卡 / P07 六行缺口对照
              P09 分数柱 / P10 时间 ribbon / P11 证据链来源表
              P13 左右复盘对照 / P14 主干阶梯 + 分支风险
```

**给用户的解释要点**：选它是因为同时满足「旋转仪式 + 丝滑 + 去 AI 味 + 每页不同」；
排除 S2 因为蓝相是用户明确否定的，排除 S3/S4 因为它们会把同一母题重复铺满内容页。

## S2 · 内容与视觉顺序

1. 先按 `content-scoring.md` 定八页的证据链（每个数字写清来源与算法）；
2. 再定每页唯一主件；
3. 最后铺统一线索（锁死底图 / 顶栏 / 书脊 / 页脚 / 进度轨）与极淡装饰。

## S3 · 素材配置 `atmosphere.json`

放到项目目录，源摄影放 `images/source/`，输出放 `images/`：

```json
{
  "canvas": [1280, 720],
  "warm": [243, 238, 228],
  "ink": [40, 36, 32],
  "dark_pages": [1, 2, 3, 5, 8, 12, 15],
  "pages": {
    "1":  {"src": "cover_valley.jpg", "veil": ["R", 0.05, 0.84, 1.4]},
    "2":  {"src": "office.jpg",       "veil": ["L", 0.05, 0.84, 1.4]},
    "3":  {"src": "fog_pine.jpg",     "veil": ["L", 0.05, 0.80, 1.4]},
    "4":  {"src": "code_desk.jpg",    "veil": ["V", 0.04, 0.50, 1.0]},
    "5":  {"src": "server.jpg",       "veil": ["L", 0.05, 0.84, 1.4]},
    "6":  {"src": "circuit.jpg",      "veil": ["V", 0.04, 0.64, 1.0]},
    "7":  {"src": "code_close.jpg",   "veil": ["V", 0.04, 0.64, 1.0]},
    "8":  {"src": "team.jpg",         "veil": ["L", 0.05, 0.82, 1.4]},
    "9":  {"src": "campus.jpg",       "veil": ["V", 0.04, 0.48, 1.0]},
    "10": {"src": "code_screen.jpg",  "veil": ["V", 0.04, 0.60, 1.0]},
    "11": {"src": "paper.jpg",        "veil": ["V", 0.04, 0.50, 1.0]},
    "12": {"src": "sunrise.jpg",      "veil": ["L", 0.05, 0.90, 1.4]},
    "13": {"src": "night.jpg",        "veil": ["V", 0.04, 0.62, 1.0]},
    "14": {"src": "ridge_road.jpg",   "veil": ["V", 0.04, 0.58, 1.0]},
    "15": {"src": "cover_valley.jpg", "veil": ["R", 0.05, 0.84, 1.4]}
  },
  "masks": {
    "circles": [
      {"src": "campus.jpg", "out": "circle_campus.png", "size": 620,
       "tint": [243, 238, 228], "hi_compress": 0.20},
      {"src": "code_desk.jpg", "out": "circle_desk.png", "size": 520,
       "bright": 1.10, "crop": [0.20, 0.28, 0.78, 0.86]}
    ],
    "knockout": {"out": "knockout.png"},
    "petals":   {"out": "petal_radial.png", "size": 680, "n": 12},
    "ridge":    {"out": "ridge.png"}
  }
}
```

方向语义：`R` 左深右浅（文字在左）、`L` 左浅右深（文字在右）、`V` 上浅下深（内容页）。

## 命令序列

```bash
python scripts/scaffold_project.py --root my_deck --chapters 4
python scripts/make_atmosphere.py --images my_deck/images/source \
       --out my_deck/images --config atmosphere.json
# 改写 my_deck/svg_output/*.svg（每页一个 hero 主件）
python scripts/make_animations.py --names-file my_deck/names.txt \
       --out my_deck/animations.json --pairs Stage:stage DialRotor:dial-rotor Rail:rail
python scripts/sync_spec_lock.py --svg-dir my_deck/svg_output --spec my_deck/spec_lock.md
python <PPT_MASTER>/scripts/svg_quality_checker.py my_deck/svg_output \
       --canonical-authoring --stage final --json
python <PPT_MASTER>/scripts/svg_to_pptx.py my_deck -o my_deck/deck.pptx
python scripts/audit_deck.py --pptx my_deck/deck.pptx --expect-slides 15
```

## S4 · 交付前必须做的三件人工事

1. 渲染 15 页 PNG + `all15.jpg`，逐页目视（白雾 / 过曝 / 半截字 / 脏点）；
2. 确认静态 PDF 看不到 Morph，主动告知用户需在 PowerPoint 2019/365 或 WPS「平滑」放映；
3. 覆盖正式文件名后复读大小与页数；若有备用名，同步覆盖并核对 `IDENTICAL`。
