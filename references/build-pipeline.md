# 构建链路、环境与交付

## 1. 标准链路

```
S0/S1 需求 → 风格路由
   ↓
scripts/scaffold_project.py        初始化 ppt-master 项目骨架 / 页面名册 / spec_lock
   ↓
scripts/make_atmosphere.py         真实摄影 → 朦胧背景 JPG + 遮罩/镂空/花瓣/剪影 PNG
   ↓
build_deck.py                      手写 15 张 SVG（每个语义单元一个 root g）
   ↓ 同脚本末尾
scripts/make_animations.py         写 animations.json（Morph 三对象 + 入场）
scripts/sync_spec_lock.py          扫字号，自动补齐 spec_lock.md
   ↓
svg_quality_checker.py --stage final --json   → 0 error
   ↓
svg_to_pptx.py  （不传 -t / -a）    → 原生可编辑 PPTX
   ↓
render_preview.py                  → 15 张 PNG + all15.jpg + 放映备份 PDF
   ↓
逐页目检 → 修 → 重渲染
   ↓
scripts/audit_deck.py              → 结构 / 转场 / 配对 / 水印 / 元数据
   ↓
覆盖正式交付文件 → 复读大小与页数确认
   ↓
写工作记录 → 清理暂存目录
```

## 2. 命令（路径用占位符，运行时换成本机实际值）

```bash
# 质量门禁：必须在 ppt-master 项目根执行
python <PPT_MASTER>/scripts/svg_quality_checker.py svg_output \
       --canonical-authoring --stage final --json

# 导出：绝不传 -t / -a
python <PPT_MASTER>/scripts/svg_to_pptx.py . -o deck.pptx

# 预览（自写渲染脚本或 ppt-master 的 render 链路）
python render_preview.py deck.pptx <OUT_DIR> <TAG>

# 交付前体检
python scripts/audit_deck.py --pptx deck.pptx --images <IMAGES_DIR>
```

`--json` 会刷新 `validation/svg_quality_report.json`；**每次改完 SVG 都要重跑**，
否则 release 导出被门禁拒绝。

## 3. 环境

- Python 3.13；已验证可用：`Pillow`、`python-pptx`、`python-docx`、`win32com`、`pypdfium2`；
  通常**没有** `numpy` / `cairosvg` / `svglib` / `fitz` / `reportlab` / `comtypes`。
  → 素材处理一律用纯 Pillow + 标准库，不要引入这些依赖。
- Windows 下 Python 不认 Git Bash 的 `/c/...` 路径，脚本参数要传 `C:\...` 形式。
- Git Bash 里 `grep` / `dirname` / `find` / `du` 可能不在 PATH，且 shell state 不跨调用保留；
  每条命令自带 PATH 前缀：
  ```bash
  export PATH="<PORTABLE_GIT>/usr/bin:/c/Windows/System32:/c/Windows:$PATH"
  ```
- 用 `MSYS2_ARG_CONV_EXCL='*'` 防止 MSYS 把 `/grant` 之类的 Windows 开关转成路径。
- 查询类命令走 Bash；部分 Windows 工具在 PowerShell 下 stdout 不回显，只用于有副作用、不需读结果的动作。

## 4. 预览与备份

`render_preview.py` 输出：

```
<OUT>/png/<TAG>/p01.png … p15.png
<OUT>/png/<TAG>/all15.jpg        15 页 contact sheet
<OUT>/xsw_<TAG>.pdf              图片型放映备份
```

备用链路：`pptx_to_svg.py (flat, embed-images)` → HTML → Edge headless screenshot →
PIL 合成图片型 PDF + `all15.jpg`。

**静态 PDF / JPG 看不到 Morph 动效**，须在 PowerPoint 2019/365 或 WPS「平滑」中放映，
旧版会自动降级为 fade。交付时明确告知用户。

## 5. Word 报告 → PDF

`win32com` 的 `doc.SaveAs(pdf, FileFormat=17)` 在本机报「命令失败」；可靠写法：

```python
import win32com.client
app = win32com.client.Dispatch('Word.Application')
app.Visible = False
doc = app.Documents.Open(docx_path)
doc.ExportAsFixedFormat(OutputFileName=pdf_path, ExportFormat=17)
doc.Close(False)
app.Quit()
```

先把旧 PDF 移走再导出，避免占用。

## 6. 交付文件覆盖

常见交付集（按项目需要命名）：

```
展示-参赛版.pptx
展示-放映备份.pdf
展示-全页预览.jpg
发展报告-参赛版.docx
发展报告-参赛版.pdf
```

### 覆盖失败排查（真实案例）

正式 PPTX 曾因被其它进程独占打开而无法覆盖，症状：

- `os.replace` / `rename` 报 `WinError 32`；
- `shutil.copyfile` / `Copy-Item -Force` / `r+b` 就地写全部 `Permission denied`；
- ACL 被额外加了只读项，但修好 ACL 后仍失败 ⇒ **是句柄独占，不是权限**。

三级降级策略：

```python
def put(src, dst):
    # 1) shutil.copyfile
    # 2) 同目录临时文件 + os.replace
    # 3) 就地 r+b 截断写入
```

全部失败时：

1. 用**明确的备用文件名**落地终版（如 `...-vNN终版.pptx`），并立刻告诉用户；
2. 请用户关掉占用程序（资源管理器预览窗格 / Office / 预览面板）；
3. **锁释放后第一件事就是补覆盖正式名**，并同步覆盖备用名，让两个文件内容完全一致；
4. 复读两个文件的大小做 `IDENTICAL` 核对。

> **最重要的教训**：交付后必须确认「用户默认会双击的那个文件名」就是最新版。
> 曾经正式名留着旧版、终版在另一个文件名上，导致用户连续两轮投诉「改进没生效」，
> 白白多做了两轮设计。

## 7. 暂存目录约定

- 所有临时脚本 / 中间数据 / 下载图片放 `%TEMP%/wb-scratch/<YYYYMMDD>-<任务简称>/`；
- 禁止把临时文件直接丢在 Temp 顶层、项目根目录、桌面或用户主目录；
- 最终交付物、记忆文件、用户明确要留的东西**不在清理范围**；
- 任务收尾删除整个暂存目录并报告释放空间；
- 清理暂存目录**之外**的任何文件前，先读内容确认是本次任务创建的；时间戳不能作为归属依据。

## 8. 交付校验输出模板

```
质量门禁 0 error / 15 页
slides=15  morph=14  fade=1
!!Stage / !!DialRotor / !!Rail 各 15
rotor angles 单调递增（-90 → 337.5）
media=22  动画 31 个 effect，order 全正整数
AI 水印关键词 0 命中；creator / lastModifiedBy 为空
PPTX 1,732,318 B | PDF 15 页 1,423,216 B | JPG 220,591 B
正式名与备用名 IDENTICAL
```
