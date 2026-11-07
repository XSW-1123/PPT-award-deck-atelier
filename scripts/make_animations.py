# -*- coding: utf-8 -*-

"""生成 ppt-master 的 animations.json：全书 Morph + 三个强制配对 + 入场动画。

规则（见 references/morph-engineering.md / svg-contract.md）：
  * 首页 fade，其余全部 morph；morph.from 必须指向**紧邻前一页**的 stem；
  * pairs 的 key 不带 !! 前缀，值 {from, to} 是 SVG 组 id；
  * groups 的 key 必须是直接 root 组 id；
  * effects[].order 必须是正整数，0 会被拒绝。

用法：
  python make_animations.py --names-file names.txt --out animations.json
  python make_animations.py --names-file names.txt --out animations.json \
      --pairs Stage:stage DialRotor:dial-rotor Rail:rail --groups groups.json
  python make_animations.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

DEFAULT_PAIRS = {
    'Stage': {'from': 'stage', 'to': 'stage'},
    'DialRotor': {'from': 'dial-rotor', 'to': 'dial-rotor'},
    'Rail': {'from': 'rail', 'to': 'rail'},
}
DEFAULT_NAMES = [
    '01_cover', '02_toc', '03_sec1', '04_self', '05_sec2', '06_job', '07_goal',
    '08_sec3', '09_academic', '10_project', '11_ability', '12_sec4',
    '13_fix', '14_plan', '15_end',
]


def fx(effect: str, order: int, duration: float = 0.45) -> dict:
    if order < 1:
        raise ValueError('order must be a positive integer, got %r' % order)
    return {'effects': [{'effect': effect, 'order': order, 'duration': duration}]}


def parse_pairs(items) -> dict:
    pairs = {}
    for raw in items or []:
        if ':' not in raw:
            raise ValueError('pair must be KEY:svg_group_id, got %r' % raw)
        key, gid = raw.split(':', 1)
        key, gid = key.strip(), gid.strip()
        if key.startswith('!!'):
            raise ValueError('pair key must NOT start with !!, got %_r' % key)
        pairs[key] = {'from': gid, 'to': gid}
    return pairs or dict(DEFAULT_PAIRS)


def build(names: list[str], pairs: dict, groups: dict,
          morph_duration: float, fade_duration: float) -> dict:
    if len(names) < 2:
        raise ValueError('at least two slides are required')
    if len(set(names)) != len(names):
        raise ValueError('slide names must be unique')
    trans = {}
    for i, nm in enumerate(names):
        if i == 0:
            cfg = {'transition': {'effect': 'fade', 'duration': fade_duration}}
        else:
            cfg = {
                'transition': {'effect': 'morph', 'duration': morph_duration},
                'morph': {'from': names[i - 1], 'pairs': pairs},
            }
        if nm in groups:
            cfg['groups'] = groups[nm]
        trans[nm] = cfg
    return {'version': 1, 'slides': trans}


def validate(doc: dict, names: list[str]) -> list[str]:
    errs = []
    slides = doc.get('slides', {})
    for i, nm in enumerate(names):
        cfg = slides.get(nm)
        if not cfg:
            errs.append('missing slide: ' + nm)
            continue
        tr = cfg.get('transition', {})
        if i == 0:
            if tr.get('effect') != 'fade':
                errs.append('%s: first slide should use fade' % nm)
        else:
            if tr.get('effect') != 'morph':
                errs.append('%s: expected morph' % nm)
            m = cfg.get('morph', {})
            if m.get('from') != names[i - 1]:
                errs.append('%s: morph.from must be %s' % (nm, names[i - 1]))
            if not m.get('pairs'):
                errs.append('%s: morph.pairs is empty' % nm)
            for k in m.get('pairs', {}):
                if k.startswith('!!'):
                    errs.append('%s: pair key must not start with !!' % nm)
        for gid, spec in cfg.get('groups', {}).items():
            for e in spec.get('effects', []):
                o = e.get('order')
                if not isinstance(o, int) or isinstance(o, bool) or o < 1:
                    errs.append('%s/%s: order must be positive int, got %r' % (nm, gid, o))
    return errs


def load_names(path: str | None) -> list[str]:
    if not path:
        return list(DEFAULT_NAMES)
    with open(path, encoding='utf-8') as fh:
        out = []
        for line in fh:
            line = line.strip()
            if line and not line.startswith('#'):
                out.append(re.sub(r'\.(svg|pptx)$', '', line))
    return out or list(DEFAULT_NAMES)


def self_test() -> int:
    groups = {
        '01_cover': {'cv-title': fx('entrance_faded_zoom', 1, 0.8)},
        '02_toc': {('tc-%d' % k): fx('entrance_rise_up', k, 0.45) for k in range(1, 5)},
    }
    doc = build(DEFAULT_NAMES, dict(DEFAULT_PAIRS), groups, 0.9, 0.55)
    errs = validate(doc, DEFAULT_NAMES)
    assert len(doc['slides']) == 15
    assert sum(1 for c in doc['slides'].values() if c['transition']['effect'] == 'morph') == 14
    if errs:
        print('SELFTEST FAIL:', errs)
        return 1
    print('SELFTEST OK: 15 slides, 14 morph, 3 forced pairs, orders positive')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--names-file', help='每行一个 slide stem；省略则用内置 15 页名册')
    ap.add_argument('--out', help='输出 animations.json 路径')
    ap.add_argument('--pairs', nargs='*', help='KEY:group_id，可多次；省略用默认三对象')
    ap.add_argument('--groups', help='JSON：{slide_stem: {group_id: {"effects": [...]}}}')
    ap.add_argument('--morph-duration', type=float, default=0.9)
    ap.add_argument('--fade-duration', type=float, default=0.55)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()
    names = load_names(a.names_file)
    pairs = parse_pairs(a.pairs)
    groups = {}
    if a.groups:
        with open(a.groups, encoding='utf-8') as fh:
            groups = json.load(fh)
    doc = build(names, pairs, groups, a.morph_duration, a.fade_duration)
    errs = validate(doc, names)
    if errs:
        for e in errs:
            print('ERROR ' + e)
        return 1
    if a.dry_run:
        print(json.dumps(doc, ensure_ascii=False, indent=2)[:2000])
        return 0
    if not a.out:
        ap.error('--out is required unless --dry-run / --self-test')
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print('OK %s | slides=%d morph=%d pairs=%s' %
          (a.out, len(names), len(names) - 1, ','.join(pairs)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
