# -*- coding: utf-8 -*-

"""扫全部 SVG 的 font-size，自动补齐 spec_lock.md 的 ## typography 声明。

`--stage final` 门禁规则：任何字号出现 > 2 次，必须在 spec_lock.md 的
`## typography` 里有 `- role: size` 声明，否则直接判 error。
手填极易漏项，所以由脚本反推。

用法：
  python sync_spec_lock.py --svg-dir svg_output --spec spec_lock.md
  python sync_spec_lock.py --svg-dir svg_output --spec spec_lock.md --dry-run
  python sync_spec_lock.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from collections import Counter

FONT_RE = re.compile(r'font-size="([0-9.]+)"')
DECL_RE = re.compile(r'^\s*-\s*[\w\-]+:\s*([0-9.]+)\s*$', re.M)


def scan(svg_dir: str) -> Counter:
    cnt = Counter()
    for name in sorted(os.listdir(svg_dir)):
        if not name.lower().endswith('.svg'):
            continue
        with open(os.path.join(svg_dir, name), encoding='utf-8') as fh:
            for m in FONT_RE.finditer(fh.read()):
                cnt[m.group(1)] += 1
    return cnt


def declared(text: str) -> set[str]:
    head = text.find('## typography')
    if head < 0:
        return set()
    nxt = text.find('\n## ', head + 5)
    section = text[head:nxt if nxt > 0 else len(text)]
    return set(DECL_RE.findall(section))


def sync(cnt: Counter, text: str, min_count: int = 2,
         prefix: str = 'auto') -> tuple[str, list[str]]:
    have = declared(text)
    missing = sorted((v for v, c in cnt.items() if c > min_count and v not in have),
                     key=lambda x: float(x))
    if not missing:
        return text, []
    head = text.find('## typography')
    if head < 0:
        text = text.rstrip('\n') + '\n\n## typography\n'
        head = text.find('## typography')
        nxt = len(text)
    else:
        nxt = text.find('\n## ', head + 5)
        if nxt < 0:
            nxt = len(text)
    add = ''.join('- %s_%s: %s\n' % (prefix, v.replace('.', 'p'), v) for v in missing)
    return text[:nxt].rstrip('\n') + '\n' + add + text[nxt:], missing


def self_test() -> int:
    tmp = tempfile.mkdtemp(prefix='atelier_spec_')
    for i in range(3):
        with open(os.path.join(tmp, 'p%02d.svg' % i), 'w', encoding='utf-8') as fh:
            fh.write('<svg><text font-size="100">x</text><text font-size="16">y</text></svg>')
    cnt = scan(tmp)
    assert cnt['100'] == 3 and cnt['16'] == 3
    base = '# spec\n\n## typography\n- dial_core: 100\n\n## constraints\n- ok\n'
    out, missing = sync(cnt, base)
    assert missing == ['16'], missing
    assert '- auto_16: 16' in out
    assert '## constraints' in out
    out2, missing2 = sync(cnt, out)
    assert missing2 == []
    print('SELFTEST OK: detected 100/16, declared only 16, idempotent')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--svg-dir')
    ap.add_argument('--spec')
    ap.add_argument('--min-count', type=int, default=2,
                    help='出现次数 > N 才需声明（门禁为 > 2，故默认 2）')
    ap.add_argument('--prefix', default='auto')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()
    if not (a.svg_dir and a.spec):
        ap.error('--svg-dir / --spec are required unless --self-test')
    cnt = scan(a.svg_dir)
    if not cnt:
        print('WARN no font-size found in ' + a.svg_dir)
        return 0
    with open(a.spec, encoding='utf-8-sig') as fh:
        text = fh.read()
    out, missing = sync(cnt, text, a.min_count, a.prefix)
    if not missing:
        print('OK spec_lock typography already complete (%d distinct sizes)' % len(cnt))
        return 0
    if a.dry_run:
        print('WOULD ADD: ' + ', '.join(missing))
        return 0
    with open(a.spec, 'w', encoding='utf-8') as fh:
        fh.write(out)
    print('OK auto-declared font sizes: ' + ', '.join(missing))
    return 0


if __name__ == '__main__':
    sys.exit(main())
