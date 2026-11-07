# GitHub 上传清单

本文件说明**哪些内容上传、哪些明确不上传及原因**。仓库为公开仓库，按最小必要原则处理。

## 上传（21 个文本/代码文件）

| 路径 | 类别 | 说明 |
|---|---|---|
| `SKILL.md` | 必需 | 技能入口：frontmatter、七条铁律、五阶段工作流、硬性门禁、资源索引 |
| `README.md` | 仓库 | 项目说明、安装、目录结构、自检、边界、许可 |
| `LICENSE` | 仓库 | MIT |
| `.gitignore` | 仓库 | 排除二进制产物与本地生成物 |
| `UPLOAD_MANIFEST.md` | 仓库 | 本文件 |
| `references/style-router.md` | 方法论 | 描述 → 风格决策表、默认假设、组合禁忌、迭代路由 |
| `references/style-presets.md` | 方法论 | 8 套母题精确参数、骨架、反面案例 |
| `references/visual-techniques.md` | 方法论 | 罗盘 / 信息图 / 朦胧背景 / 遮罩 / 镂空 / 花瓣 / 剪影 |
| `references/typography-and-color.md` | 方法论 | 三套配色 hex、字体体系、字号角色带、对比度 |
| `references/morph-engineering.md` | 工程 | 丝滑转场、真旋转罗盘、三对象配对、全部踩坑 |
| `references/svg-contract.md` | 工程 | SVG 页面契约、质量门禁、animations.json schema |
| `references/content-scoring.md` | 内容 | 评分结构、证据链、遣词造句、删改清单 |
| `references/anti-ai-checklist.md` | 质检 | 去 AI 味自查、水印体检、逐页目检清单 |
| `references/build-pipeline.md` | 工程 | 命令、环境、Word→PDF、文件锁、暂存清理 |
| `references/lessons-learned.md` | 经验 | 全部被否方案与工程踩坑 |
| `scripts/make_atmosphere.py` | 脚本 | 摄影 → 朦胧背景 + 透明素材 PNG |
| `scripts/make_animations.py` | 脚本 | 生成 Morph 三对象 + 入场动画 sidecar |
| `scripts/sync_spec_lock.py` | 脚本 | 扫 SVG 字号，自动补齐 spec_lock |
| `scripts/scaffold_project.py` | 脚本 | 初始化项目骨架与页名册 |
| `scripts/audit_deck.py` | 脚本 | PPTX 结构 / 转场 / 配对 / 水印 / 元数据体检 |
| `assets/example_brief.md` | 示例 | 脱敏需求 → 完整风格路由输出 → 配置 → 命令 |

## 明确不上传

| 类别 | 原因 |
|---|---|
| 真实姓名、学校、班级、成绩数据、证书、奖项名称 | 个人隐私；与方法论无关 |
| 个人照片、校园照片、证书扫描件、合影 | 隐私 + 肖像权 |
| 从图库下载的原图、烘焙后的朦胧背景 JPG、圆形遮罩 PNG | 版权 / 许可不明，且体积大；脚本可复现 |
| 参赛 PPTX / PDF / 全页预览 JPG / 报告 DOCX | 个人参赛材料，非技能内容；含真实信息 |
| 本机绝对路径、本机用户名、邮箱、私有项目路径 | 环境特定，且泄露本机目录结构 |
| `.workbuddy/memory/` 工作日志 | 项目私有记录，含迭代过程与个人数据 |
| `build_v18.py` ~ `build_v27.py` 等历史构建脚本 | 含个人内容与硬编码路径，且是叠层历史代码，不可复用 |
| `animations.json` / `spec_lock.md` / `svg_output/` / `validation/` | 项目运行时产物，由脚本生成 |
| `atelier_selftest_out/` 等自检产物 | 临时文件 |

## 脱敏检查项

上传前逐项确认（脚本扫描结果应为 0 命中）：

```
真实姓名 / 学校 / 班级 / 具体分数 / 排名
邮箱、QQ 号、手机号
Windows 用户目录下的绝对路径、桌面路径
个人文件名（含姓名的交付文件名）
图库来源标识、带姓名的图片文件名
生成器水印与 AI 署名
```

## 许可与署名

- 代码与文档：MIT（见 `LICENSE`）；
- 参考的第三方设计趋势结论仅在文档中作为方法论引用，不含原文转载；
- 使用者自备图片，须自行遵守图片来源许可；
- 赛事规则（分值、字数、图表数、格式）随届次变化，文档只给方法，不写死具体数值。
