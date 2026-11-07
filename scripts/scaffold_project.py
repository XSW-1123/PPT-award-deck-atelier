# -*- coding: utf-8 -*-

"""初始化 ppt-master 项目骨架：页面名册、目录、spec_lock、最小 SVG 模板。

默认 15 页 / 4 章：封面 1 + 目录 1 + (章节页 + 2 内容页) × N + 结尾 1。
不覆盖已有文件，除非 --force。

用法：
  python scaffold_project.py --root my_deck
  python scaffold_project.py --root my_deck --chapters 3 --title "项目汇报"
  python scaffold_project.py --self-test
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

CONTENT_TOKENS = [
    'self', 'job', 'goal', 'academic', 'project',
    'ability', 'fix', 'plan', 'risk', 'result', 'method', 'evidence',
]
CHAPTER_CN = ['壹', '贰', '叁', '肆', '伍', '陆']


def roster(chapters: int) -> list[str]:
    """封面 + 目录 + (章节页 + 2 内容页) × N + 结尾。"""
    names = ['01_cover', '02_toc']
    idx = 3
    for c in range(1, chapters + 1):
        names.append('%02d_sec%d' % (idx, c)); idx += 1
        for k in range(2):
            tok = CONTENT_TOKENS[(c - 1) * 2 + k] if (c - 1) * 2 + k < len(CONTENT_TOKENS) else 'topic%d' % (k + 1)
            names.append('%02d_%s' % (idx, tok)); idx += 1
    names.append('%02d_end' % idx)
    return names


def spec_lock(title: str, chapters: int) -> str:
    return f"""# {title} · 设计约束

## typography
- cover_title: 166
- section_cn: 100
- page_title: 44
- hero_number: 96
- body: 17
- caption: 12

## constraints
- canvas: 1280x720 (16:9)
- visual_style_behavior: 每页版式不重复
- 主色 <= 3；字体 <= 2 类（数字可用第三个衬线体）；留白 >= 30%
- 一页一个 hero moment（主视觉占版面 >= 40%）
- 仪式母题只出现在目录页 + {chapters} 张章节页（+ 结尾收束）
- 背景图全书同 id / 同位置 / 同尺寸锁死
- Morph 强制配对：!!Stage / !!DialRotor / !!Rail
- 禁止：clip-path / <mask> / <polyline> / stroke-dasharray / <pattern> / <path d="A...">
- 禁止：蓝紫渐层、corporate blue + flat grey、深色底上盖浅色渐变
- 禁止：页面上写「对应评分项」「本页得分」等自曝话术

## official_limits
- 按当届官方文件填写：字数 / 图表数 / 文件大小 / 页数上限
- 生成脚本中用 assert 自检，不靠估算
"""


def minimal_svg(pg: int, role: str, chapter_no: int = 0) -> str:
    cn = CHAPTER_CN[chapter_no - 1] if chapter_no else ''
    label = 'SECTION ' + cn if role == 'section' else role.upper()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"
     width="1280" height="720" data-pptx-page-role="{role}"
     font-family="Microsoft YaHei" lang="zh-CN">
  <rect id="bg" data-pptx-role="decoration" x="0" y="0" width="1280" height="720" fill="#F3EFE6"/>
  <g id="stage" data-pptx-role="decoration" data-pptx-bounds="0 0 1280 720">
    <rect x="0" y="0" width="1280" height="720" fill="#33302A" fill-opacity="0.10"/>
    <text x="0" y="360" font-size="10" fill="#C3A36E" fill-opacity="0.001">·</text>
  </g>
  <g id="dial-rotor" data-pptx-bounds="1024 14 64 64" transform="rotate({(pg - 1) * 22.5:.1f} 1056 46)">
    <circle cx="1056" cy="46" r="30" fill="none" stroke="#9C7746" stroke-width="1.2"/>
    <line x1="1056" y1="16" x2="1056" y2="46" stroke="#9C7746" stroke-width="2"/>
    <text x="1056" y="20" font-size="10" fill="#9C7746" fill-opacity="0.001">·</text>
  </g>
  <g id="rail" data-pptx-role="decoration" data-pptx-bounds="64 688 {1152.0 * pg / 15 + 14:.1f} 20">
    <rect x="64" y="700" width="{1152.0 * pg / 15:.1f}" height="2" fill="#C3A36E"/>
    <text x="64" y="702" font-size="10" fill="#C3A36E" fill-opacity="0.001">·</text>
  </g>
  <g id="hero" data-pptx-bounds="64 214 1152 400">
    <text x="88" y="330" font-size="44" fill="#2C2A26">{label} · P{pg:02d}</text>
    <text x="88" y="380" font-size="17" fill="#615D55">在此写入本页唯一的主视觉与结论句</text>
  </g>
  <g id="notes" data-pptx-bounds="64 630 1152 44">
    <rect x="64" y="630" width="48" height="3" fill="#9C7746"/>
    <text x="90" y="660" font-size="17" fill="#F0E6CE">一句承上启下的过渡句</text>
  </g>
</svg>
"""


def build(root: str, chapters: int, title: str, force: bool) -> list[str]:
    os.makedirs(os.path.join(root, 'svg_output'), exist_ok=True)
    os.makedirs(os.path.join(root, 'images'), exist_ok=True)
    names = roster(chapters)
    made = []

    def put(path: str, content: str):
        if os.path.exists(path) and not force:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
        made.append(path)

    put(os.path.join(root, 'names.txt'), '\n'.join(names) + '\n')
    put(os.path.join(root, 'spec_lock.md'), spec_lock(title, chapters))
    put(os.path.join(root, 'README.md'),
        '# %s\n\n由 PPT-award-deck-atelier 初始化。\n\n'
        '1. 在 spec_lock.md 填入当届官方硬约束；\n'
        '2. 用 make_atmosphere.py 生成朦胧背景与透明素材；\n'
        '3. 改写 svg_output/*.svg，每页一个 hero 主件；\n'
        '4. make_animations.py 写 sidecar；sync_spec_lock.py 补字号；\n'
        '5. svg_quality_checker.py --stage final --json → svg_to_pptx.py；\n'
        '6. 渲染逐页目检 → audit_deck.py → 覆盖交付。\n' % title)
    for i, nm in enumerate(names, 1):
        role = 'cover' if i == 1 else ('toc' if i == 2 else
               ('end' if i == len(names) else
               ('section' if nm.split('_', 1)[1].startswith('sec') else 'content')))
        put(os.path.join(root, 'svg_output', nm + '.svg'),
            minimal_svg(i, role, chapter_no=0))
    return made


def self_test() -> int:
    tmp = tempfile.mkdtemp(prefix='atelier_scaffold_')
    made = build(os.path.join(tmp, 'deck'), 4, 'TEST', False)
    assert os.path.isfile(os.path.join(tmp, 'deck', 'names.txt'))
    assert len(open(os.path.join(tmp, 'deck', 'names.txt'), encoding='utf-8').read().strip().split('\n')) == 15
    assert len([f for f in os.listdir(os.path.join(tmp, 'deck', 'svg_output')) if f.endswith('.svg')]) == 15
    with open(os.path.join(tmp, 'deck', 'svg_output', '01_cover.svg'), encoding='utf-8') as fh:
        s = fh.read()
    assert 'data-pptx-bounds' in s and '!!' not in s
    assert 'transform="rotate(' in s
    print('SELFTEST OK: 15 pages, stage/dial-rotor/rail groups present')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root')
    ap.add_argument('--chapters', type=int, default=4)
    ap.add_argument('--title', default='演示文稿')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.root:
        ap.error('--root is required unless --self-test')
    made = build(a.root, a.chapters, a.title, a.force)
    print('OK scaffold %s | %d files | %d pages' %
          (a.root, len(made), len(roster(a.chapters))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
