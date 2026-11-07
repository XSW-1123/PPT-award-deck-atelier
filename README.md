# PPT-award-deck-atelier · 获奖级演示文稿设计工坊

一套可复用的 Agent Skill：把「惊艳、不像 AI、丝滑转场、旋转到每个主题、逐页不同、内容可核验」
这些模糊要求，转成**明确的视觉选型 + 可执行的工程规范**。

它不是又一套 PPT 模板，而是 `ppt-master` 之上的**设计决策层与工程质量层**：

- 从用户描述自主推导风格（8 套母题预设 + 决策表 + 禁忌表）；
- 给出精确色码、字体角色带、版式骨架、转场参数；
- 固化手写 SVG → 原生可编辑 PPTX → 逐页渲染目检 → 交付校验的全链路；
- 内置「去 AI 味」清单、内容获奖概率审核表、以及 10 轮真实迭代踩过的所有坑。

> 来源：一套竞赛展示材料从 v18 迭代到 v27 的完整设计记录，包含每一轮被用户否决的方案与原因。

## 安装

依赖已安装的 `ppt-master` 技能（提供 `svg_quality_checker.py` 与 `svg_to_pptx.py`）。
本仓库不重复实现转换器。

把整个仓库目录复制到用户级技能目录：

```bash
git clone https://github.com/XSW-1123/PPT-award-deck-atelier.git PPT-award-deck-atelier
cp -r PPT-award-deck-atelier ~/.workbuddy/skills/PPT-award-deck-atelier
```

Windows 下把仓库目录复制到 `%USERPROFILE%\.workbuddy\skills\PPT-award-deck-atelier`。
也可作为项目级技能放到 `<project>/.workbuddy/skills/PPT-award-deck-atelier/` 供团队共享。

## 触发方式

安装后直接用自然语言描述需求即可，例如：

> 帮我做一份 15 页竞赛答辩 PPT，四个章节，目录和主题页要旋转到每个主题，
> 翻页要丝滑，别像 AI 模板，配色别全是蓝的，朦胧背景要按每页内容选。

技能会先给出**选型表**（选了什么、排除了什么、为什么），再进入构建。

## 目录结构

```
PPT-award-deck-atelier/
├── SKILL.md                       # 入口：七条铁律 + 五阶段工作流 + 硬性门禁
├── references/
│   ├── style-router.md            # 描述 → 风格决策表（核心）
│   ├── style-presets.md           # 8 套母题的精确参数与反面案例
│   ├── visual-techniques.md       # 罗盘 / 信息图 / 朦胧背景 / 遮罩 / 镂空 / 花瓣 / 剪影
│   ├── typography-and-color.md    # 三套配色 hex、字体体系、字号角色带
│   ├── morph-engineering.md       # 丝滑转场、真旋转罗盘、三对象强制配对
│   ├── svg-contract.md            # SVG 页面契约、质量门禁、animations.json schema
│   ├── content-scoring.md         # 评分结构、证据链、遣词造句、删改清单
│   ├── anti-ai-checklist.md       # 去 AI 味自查、水印体检、逐页目检清单
│   ├── build-pipeline.md          # 命令、环境、Word→PDF、文件锁、暂存清理
│   └── lessons-learned.md         # 全部被否方案与工程踩坑
├── scripts/
│   ├── make_atmosphere.py         # 摄影 → 朦胧背景 + 透明素材 PNG（Pillow）
│   ├── make_animations.py         # 生成 Morph 三对象 + 入场动画 sidecar
│   ├── sync_spec_lock.py          # 扫 SVG 字号，自动补齐 spec_lock 声明
│   ├── scaffold_project.py         # 初始化项目骨架与 15 页名册
│   └── audit_deck.py              # PPTX 结构 / 转场 / 配对 / 水印 / 元数据体检
└── assets/
    └── example_brief.md           # 脱敏示例：需求 → 完整路由输出 → 配置 → 命令
```

## 脚本自检

全部脚本仅依赖 Python 标准库（`make_atmosphere.py` 额外需要 Pillow），可离线自检：

```bash
python scripts/make_atmosphere.py --self-test
python scripts/make_animations.py --self-test
python scripts/sync_spec_lock.py --self-test
python scripts/scaffold_project.py --self-test
python scripts/audit_deck.py --self-test
```

## 8 套母题速览

| ID | 名称 | 适用 |
|---|---|---|
| S1 | warm-editorial-compass | 竞赛 / 成长叙事 / 去 AI 味（默认推荐） |
| S2 | navy-gold-compass | 庄重仪式、明确要蓝金 |
| S3 | survey-atlas | 工程 / 技术 / 测绘图集 |
| S4 | blueprint-infographic | 一页一个信息图主件 |
| S5 | photo-editorial-haze | 朦胧摄影 / 人文柔和 |
| S6 | dark-cinematic | 科技发布 / 沉浸深色 |
| S7 | swiss-minimal | 咨询 / 商务 / 克制 |
| S8 | mixed-showstopper | 长篇多章节 / 「还要更惊艳」 |

## 隐私与素材

本仓库**不含**任何真实姓名、学校、成绩、证书、个人照片、私有路径或生成图。

- 示例中的照片文件名仅为占位符，请自备合法来源的真实摄影；
- 使用第三方图库时遵守其许可，并确认图片无水印、无叠字；
- 赛事规则（分值、字数、图表数、格式）随届次变化，务必以当届官方文件为准；
- `scripts/audit_deck.py` 会扫描 PPTX 里的生成器痕迹与图片元数据，命中为 0 时如实报告，不做无谓删除。

## 已知边界

- 静态 PDF / JPG 看不到 Morph 动效；须在 PowerPoint 2019/365 或 WPS「平滑」中放映；
- `svg_to_pptx` 不支持 `clip-path` / `<mask>` / `<polyline>` / `stroke-dasharray`，
  相关效果一律预烘焙成 PNG；
- 自动门禁只能查结构，「白雾 / 过曝 / 半截字 / 脏点」必须人工逐页目视。

## 许可

MIT，见 [LICENSE](LICENSE)。
