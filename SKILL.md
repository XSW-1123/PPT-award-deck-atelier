---
name: PPT-award-deck-atelier
description: 获奖级演示文稿设计工坊。当用户要求做 PPT / 幻灯片 / 演示文稿，且诉求包含「惊艳、高级、拿奖、第一名、不要 AI 味、朦胧背景、丝滑转场、旋转到每个主题、圆盘、去模板味、逐页目检、可核验内容」等任一信号时，应使用本技能。技能先从用户描述自主推导风格与样式，再产出「仪式母题 + 内容母题 + 三色配色 + 字体体系 + Morph 转场」的完整方案，并驱动手写 SVG → 原生可编辑 PPTX → 逐页渲染目检 → 交付校验的全链路。也适用于已有 PPT 的去 AI 味改造、转场重做、内容获奖概率审核。
agent_created: true
license: MIT
---

# 获奖级演示文稿设计工坊

## 目的

把一套经过 10 轮真实迭代、被用户逐轮否决又逐轮重做的演示设计方法固化为可复用能力。核心不是「生成一套好看模板」，而是：

1. **根据用户描述自主选风格**，而不是把同一套模板套给所有任务；
2. **让「惊艳」来自结构与信息密度**，而不是堆装饰；
3. **让转场真的连贯**，而不是每页淡入淡出；
4. **让视觉不像 AI 生成**，让内容经得起评委追问；
5. **交付的正式文件名确实是最新版**。

底层能力依赖已安装的 `ppt-master` 技能（手写 SVG → 原生可编辑 PPTX）。本技能是它之上的**设计决策层与工程质量层**，不重复实现转换器。

## 何时使用

在下列任一情形加载本技能：

- 新建竞赛答辩 / 生涯规划 / 金奖级展示 PPT；
- 用户说「惊艳」「高级」「拿第一」「遥遥领先」「不像 AI 做的」「别像模板」；
- 用户点名圆形遮罩、镂空蒙版、花瓣放射、剪影、朦胧背景、卡片微上浮、平滑切换、旋转圆盘；
- 用户抱怨「每页之间转换生硬」「目录页出现得突兀」「内容页一般」「配色很 AI」「全是蓝底」；
- 需要审核一份参赛 PPT 的内容是否真能提高获奖概率；
- 需要在交付前扫 AI 水印 / 生成器痕迹 / 元数据。

用户只问「怎么启动某项目」「解释某个文件」时不加载。

## 七条铁律

1. **仪式符号只用一次体系，不复用成灾。** 圆盘是章节仪式，只出现在目录页 + 章节页（+ 结尾收束）；内容页必须换另一套几何语言。把同一个圆盘搬到 8 张内容页 = 立刻廉价（真实否决案例）。
2. **统一线索贯穿全书，但每页版式不重复。** 靠固定底图、页脚、书脊、进度轨、顶栏保持连贯；靠八种互不相同的主件保持新鲜。「同一模板套八次」和「八个互不相干的海报」都会被否。
3. **一页一个 hero moment。** 每页有且只有一个占版面 40% 以上的主视觉，其余是注脚。
4. **主色 ≤ 3、字体 ≤ 2 类、留白 ≥ 30%。** 第 3 类只允许是用于数字的衬线体。
5. **真实 > 生成。** 贴题的真实摄影、真实截图、真实文档优先；禁用蓝紫渐层、整片 corporate blue、每页一枚几何徽标。
6. **内容只留能加分的部分。** 具体事实替代形容词；删无关奖项、来源不明的伪数据、自曝评分点的话术、未核实的校训口号。
7. **交付后必须验证「用户默认双击的那个文件名」是最新版。** 曾被独占锁挡住一次覆盖，导致用户打开旧版并连续两轮投诉「改进没生效」。

## 五阶段工作流

### S0 · 需求解码（先问清，别猜）

从用户描述抽取五个维度，缺失项按 `references/style-router.md` 的默认值补齐并在回复里标明假设：

| 维度 | 要抽取的内容 |
|---|---|
| 场合 | 竞赛答辩 / 学术汇报 / 商业路演 / 产品发布 / 教学 / 企业汇报 |
| 情绪 | 惊艳、高级、克制、温暖、沉稳、科技感、活泼 |
| 结构 | 章节数、总页数、是否有数据证据、是否为成长 / 路径叙事 |
| 硬约束 | 必须旋转、必须丝滑、必须去 AI 味、必须深 / 浅色、字数页数上限 |
| 素材 | 有无真实摄影、有无品牌色、有无官方规范（页数 / 字数 / 文件大小） |

**有官方材料规范时先读规范再动手**，把硬约束写进 `spec_lock.md`，在生成脚本里用 `assert` 自检。

### S1 · 风格路由（本技能的核心动作）

阅读 `references/style-router.md`，把 S0 的五个维度映射成一张**明确的选型决策**：

- 1 个仪式母题 + 1 个内容母题（不得相同）；
- 1 套三色配色（含精确 hex）；
- 1 套字体体系（标题 / 正文 / 数字）；
- 1 套转场方案；
- 页数骨架与每页主件清单。

阅读 `references/style-presets.md` 取对应预设的参数。选型结果**先在回复里用一张表说明「为什么选它、排除了哪几个」**，再开始写码。用户明确否定过某母题时，把它加入本次禁用列表，绝不再用。

### S2 · 视觉与内容设计

- 技法参数查 `references/visual-techniques.md`；
- 配色与字号角色带查 `references/typography-and-color.md`；
- 内容逐条过 `references/content-scoring.md` 的审核表；
- 去 AI 味自查过 `references/anti-ai-checklist.md`。

**顺序不可反**：先定内容与证据链，再选主件，最后才铺装饰。装饰不承载信息时一律不画。

### S3 · 工程构建

阅读 `references/svg-contract.md` 与 `references/morph-engineering.md`，再按 `references/build-pipeline.md` 执行。要点：

- 每个语义单元一个直接 root `<g id data-pptx-bounds="x y w h">`，id 唯一、bounds 不重叠；
- 背景 / 导航 / 页码标 `data-pptx-role="decoration"`，且**可见 root 组仍须显式写 bounds**；
- 背景图全书同 id、同位置、同尺寸锁死；
- Morph 至少三个强制配对对象（舞台 / 旋转体 / 进度轨），`!!` 名称不写进 key；
- 「旋转到每个主题」必须输出真正的组级 `rot`，不是把角度烘焙进子图元；
- 渐变蒙版、圆形遮罩、镂空、花瓣、剪影一律**预烘焙成带 alpha 的 PNG**，不要在 SVG 里写 `clip-path` / `<mask>`；
- 用 `scripts/` 下的通用脚本生成素材、动画 sidecar、spec_lock 字号声明，不要每次重写。

### S4 · 目检 → 交付闭环

1. 渲染全页 PNG 与总览 JPG，**逐页目视**，不只跑自动门禁；
2. 按 `references/anti-ai-checklist.md` 的目检清单修缺陷（贴边半截字、白雾、过曝白斑、深色页浅字、脏点小色块）；
3. 用 `scripts/audit_deck.py` 扫结构 / 水印 / 元数据；
4. 覆盖正式交付文件后**重新读取文件大小与页数确认覆盖成功**；若被独占锁挡住，明确告知用户并给出备用名，锁释放后立刻补覆盖正式名；
5. 追加工作记录，清理本次暂存目录。

## 硬性门禁（任一失败即不得交付）

- `svg_quality_checker.py --canonical-authoring --stage final --json` → 0 error；
- 字号 recurrence 已在 `spec_lock.md` 的 `## typography` 声明（用 `scripts/sync_spec_lock.py` 自动反推）；
- `animations.json` 的 `order` 全为正整数，`morph.from` 指向紧邻前一页；
- 导出 `svg_to_pptx.py` **不传 `-t` / `-a`**，否则覆盖动画 sidecar；
- PPTX 内 `!!Stage` / `!!DialRotor` / `!!Rail` 计数 = 页数；Morph 转场数 = 页数 - 1；
- 旋转体角度序列逐页单调递增；
- AI 水印关键词命中 = 0，`dc:creator` / `lastModifiedBy` 为空；
- 全部页渲染成功，逐页目检通过；
- 官方字数 / 图表 / 文件大小上限用脚本 `assert` 通过。

## 资源索引

| 文件 | 何时读 |
|---|---|
| `references/style-router.md` | S1 必读：描述 → 风格决策表、默认假设、禁用组合 |
| `references/style-presets.md` | S1 必读：8 套母题的参数、骨架、适用与反面案例 |
| `references/visual-techniques.md` | S2：圆盘 / 信息图 / 编辑式大版面 / 朦胧背景 / 遮罩 / 镂空 / 花瓣 / 剪影 |
| `references/typography-and-color.md` | S2：三套配色 hex、字体体系、字号角色带、对比度 |
| `references/morph-engineering.md` | S3 必读：丝滑转场、真旋转罗盘、三对象配对、全部踩坑 |
| `references/svg-contract.md` | S3 必读：SVG 页面契约、质量门禁、animations.json schema |
| `references/content-scoring.md` | S2：评分结构、证据链、遣词造句、删改清单 |
| `references/anti-ai-checklist.md` | S2 / S4：去 AI 味自查、水印体检、逐页目检清单 |
| `references/build-pipeline.md` | S3 / S4：命令、环境、导出、Word→PDF、文件锁、暂存清理 |
| `references/lessons-learned.md` | 动手前快速扫：v18–v27 全部被否方案与负面案例 |
| `scripts/make_atmosphere.py` | 真实摄影 → 朦胧背景 + 圆形遮罩 / 镂空 / 花瓣 / 剪影 PNG |
| `scripts/make_animations.py` | 生成 Morph 三对象 + 入场动画的 `animations.json` |
| `scripts/sync_spec_lock.py` | 扫 SVG 字号，自动补齐 `spec_lock.md` 声明 |
| `scripts/scaffold_project.py` | 初始化 ppt-master 项目骨架与页面名册 |
| `scripts/audit_deck.py` | PPTX 结构 / 转场 / 配对 / 水印 / 元数据体检 |
| `assets/example_brief.md` | 脱敏示例：一段用户描述 → 完整风格路由输出 |

## 快速命令

在工作目录为 ppt-master 项目根时执行（路径用本机实际值替换 `<...>`）：

```bash
python <ppt-master>/scripts/svg_quality_checker.py svg_output --canonical-authoring --stage final --json
python scripts/sync_spec_lock.py --svg-dir svg_output --spec spec_lock.md
python <ppt-master>/scripts/svg_to_pptx.py . -o deck.pptx
python scripts/audit_deck.py --pptx deck.pptx
```

静态 PDF / JPG **看不到 Morph 动效**；须在 PowerPoint 2019/365 或 WPS「平滑」中放映，旧版自动降级为淡入。交付时明确告知用户这一点。
