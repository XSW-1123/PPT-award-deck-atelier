# -*- coding: utf-8 -*-
"""真实摄影 → 朦胧背景 + 局部渐变蒙版 + 圆形遮罩 / 镂空 / 花瓣 / 剪影。

设计原则（见 references/visual-techniques.md）：
  * 渐变融合与局部压暗必须**烘焙进 JPG 本身**，SVG 里只留 0.10~0.12 的极淡罩；
    否则深色玻璃会把背景整片盖住，朦胧背景等于没加。
  * svg_to_pptx 拒绝 clip-path / <mask>，所有透明素材预烘焙为带 alpha 的 PNG。
  * 底图全书同 id / 同位置 / 同尺寸锁死，Morph 才不会晃。

用法：
  python make_atmosphere.py --images IMG_DIR --out OUT_DIR --config config.json
  python make_atmosphere.py --self-test            # 生成合成图跑全流程，不依赖外部素材

config.json 示例见 assets/example_brief.md 末尾。
仅依赖 Pillow，不引入 numpy / cairosvg / reportlab。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
import time
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops

DEFAULT_WARM = (243, 238, 228)
DEFAULT_INK = (40, 36, 32)
DEFAULT_CANVAS = (1280, 720)


# --------------------------------------------------------------------------- 基础工具

def cover_crop(im, w: int, h: int) -> Image.Image:
    sw, sh = im.size
    sc = max(w / sw, h / sh)
    nw, nh = int(sw * sc + 0.5), int(sh * sc + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw - w) // 2, (nh - h) // 2,
                    (nw - w) // 2 + w, (nh - h) // 2 + h))


def veil_mask(w: int, h: int, direction: str, lo: float, hi: float,
              power: float = 1.0) -> Image.Image:
    """L = 左浅右深；R = 左深右浅；V = 上浅下深。

    返回 L 模式：0 处保留照片，255 处压到暖墨。
    direction 按**文字位置**选：文字在左用 R，在右用 L，内容页用 V。
    """
    if direction not in ('L', 'R', 'V'):
        raise ValueError('direction must be L / R / V')
    n = w if direction in ('L', 'R') else h
    vals = []
    for i in range(n):
        t = i / float(n - 1)
        if direction == 'R':
            t = 1.0 - t
        vals.append(int(255 * (lo + (hi - lo) * (t ** power))))
    m = Image.new('L', (n, 1) if direction in ('L', 'R') else (1, n))
    m.putdata(vals)
    return m.resize((w, h))


def make_haze(src: str, w: int, h: int, direction: str, lo: float, hi: float,
              power: float, warm, ink, dark: bool) -> Image.Image:
    im = cover_crop(Image.open(src).convert('RGB'), w, h)
    # 模糊别过头：14px 会把主体全抹掉
    im = im.filter(ImageFilter.GaussianBlur(3.5 if dark else 7.0))
    im = ImageEnhance.Color(im).enhance(0.58 if dark else 0.42)
    im = ImageEnhance.Brightness(im).enhance(0.98 if dark else 1.06)
    im = ImageEnhance.Contrast(im).enhance(0.92 if dark else 0.78)
    # 统一暖调，绝不压蓝；浅色页 0.46（0.76 会让照片几乎消失）
    im = Image.blend(im, Image.new('RGB', (w, h), warm), 0.14 if dark else 0.46)
    return Image.composite(Image.new('RGB', (w, h), ink), im,
                           veil_mask(w, h, direction, lo, hi, power))


def soft_circle_mask(size: int, pad: int = 10, blur: int = 14) -> Image.Image:
    m = Image.new('L', (size, size), 0)
    ImageDraw.Draw(m).ellipse((pad, pad, size - pad, size - pad), fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))


def compress_highlights(im: Image.Image, k: float) -> Image.Image:
    """只压亮部的 LUT：i * (1 - k * (i/255)^2)。

    用于圆形遮罩里过曝天空变白斑；不动建筑与中间调。
    """
    lut = [max(0, min(255, int(i * (1.0 - k * (i / 255.0) ** 2))))
           for i in range(256)]
    return im.point(lut * 3)


def circle_photo(src: str, out: str, size: int = 620, tint=None,
                 bright: float = 1.0, crop=None, hi_compress: float = 0.0) -> None:
    """圆形柔边遮罩的照片。

    无 crop 时保持直接拉伸 —— cover_crop 会把亮天空放大成白斑。
    若必须裁切，取主体 / 建筑立面，避开天空。
    """
    im = Image.open(src).convert('RGB')
    if crop:
        w0, h0 = im.size
        im = im.crop((int(crop[0] * w0), int(crop[1] * h0),
                      int(crop[2] * w0), int(crop[3] * h0)))
    im = im.resize((size, size), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im = ImageEnhance.Color(im).enhance(0.45)
    if hi_compress:
        im = compress_highlights(im, hi_compress)
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
        im = ImageEnhance.Contrast(im).enhance(0.82)
    if tint:
        im = Image.blend(im, Image.new('RGB', (size, size), tint), 0.26)
    out_im = im.convert('RGBA')
    out_im.putalpha(soft_circle_mask(size))
    out_im.save(out)


def knockout(out: str, w: int = 620, h: int = 620, hole=(90, 90, 530, 530),
             tint=(239, 234, 223), alpha: int = 150,
             feather: int = 70, blur: int = 46) -> None:
    """镂空蒙版：一整块半透明米色，中间被「剪除」一个圆洞，洞里透出底图。

    alpha 150 / feather 70 / blur 46 才能去掉方块感。
    """
    ov = Image.new('RGBA', (w, h), tuple(tint) + (alpha,))
    m = Image.new('L', (w, h), 255)
    ImageDraw.Draw(m).ellipse(hole, fill=0)
    m = m.filter(ImageFilter.GaussianBlur(16))
    edge = Image.new('L', (w, h), 0)
    ImageDraw.Draw(edge).rectangle((feather, feather, w - feather, h - feather), fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(blur))
    ov.putalpha(ImageChops.multiply(ImageChops.multiply(ov.getchannel('A'), m), edge))
    ov.save(out)


def petals(out: str, size: int = 680, n: int = 12,
           col=(178, 150, 108, 255), per_alpha: int = 36) -> None:
    """12 片细长纺锤花瓣，柔边。只作罗盘底纹，透明度 ≤ 0.20。"""
    base = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c = size / 2.0
    for k in range(n):
        a = 2 * math.pi * k / n
        layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pts = []
        for j in range(19):
            t = j / 18.0
            r = c * 0.20 + (c * 0.78 - c * 0.20) * t
            wd = c * 0.115 * math.sin(math.pi * t)
            pts.append((c + r * math.cos(a) - wd * math.sin(a),
                        c + r * math.sin(a) + wd * math.cos(a)))
        for j in range(18, -1, -1):
            t = j / 18.0
            r = c * 0.20 + (c * 0.78 - c * 0.20) * t
            wd = c * 0.115 * math.sin(math.pi * t)
            pts.append((c + r * math.cos(a) + wd * math.sin(a),
                        c + r * math.sin(a) - wd * math.cos(a)))
        ImageDraw.Draw(layer).polygon(pts, fill=col)
        layer.putalpha(ImageChops.multiply(layer.getchannel('A'),
                                           Image.new('L', (size, size), per_alpha)))
        base = Image.alpha_composite(base, layer)
    base.filter(ImageFilter.GaussianBlur(3.0)).save(out)


def ridge(out: str, w: int = 1280, h: int = 260, col=(44, 40, 36, 255)) -> None:
    """远山剪影：三条正弦叠加，底部填实、顶部透明。全本同一条、同一位置。"""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pts = []
    for x in range(0, w + 1, 6):
        t = x / w
        y = (h * 0.52 - 52 * math.sin(2 * math.pi * (t * 1.15 + 0.08))
             - 27 * math.sin(2 * math.pi * (t * 2.7 + 0.33))
             - 14 * math.sin(2 * math.pi * (t * 5.1 + 0.61)))
        pts.append((x, y))
    ImageDraw.Draw(im).polygon(pts + [(w, h), (0, h)], fill=tuple(col))
    im.save(out)


# --------------------------------------------------------------------------- 驱动

def run(config: dict, images: str, out: str, only: str = 'all') -> list[str]:
    os.makedirs(out, exist_ok=True)
    w, h = config.get('canvas', list(DEFAULT_CANVAS))
    warm = tuple(config.get('warm', DEFAULT_WARM))
    ink = tuple(config.get('ink', DEFAULT_INK))
    dark_pages = set(config.get('dark_pages', []))
    made: list[str] = []

    if only in ('all', 'background'):
        pages = config.get('pages', {})
        if not pages:
            raise ValueError('config.pages is empty; nothing to bake')
        for key in sorted(pages, key=lambda x: int(x)):
            pg = int(key)
            spec = pages[key]
            src = spec['src'] if os.path.isabs(spec['src']) else os.path.join(images, spec['src'])
            if not os.path.isfile(src):
                raise FileNotFoundError(src)
            direction, lo, hi, power = spec.get('veil', ['V', 0.04, 0.58, 1.0])
            dst = os.path.join(out, 'haze_%02d.jpg' % pg)
            make_haze(src, w, h, direction, lo, hi, power, warm, ink,
                      dark=pg in dark_pages).save(dst, quality=86)
            made.append(dst)
            print('  haze_%02d.jpg  <= %s  %s' % (pg, spec['src'], direction))

    if only in ('all', 'masks'):
        m = config.get('masks', {})
        for item in m.get('circles', []):
            src = item['src'] if os.path.isabs(item['src']) else os.path.join(images, item['src'])
            circle_photo(src, os.path.join(out, item['out']),
                         size=item.get('size', 620), tint=tuple(item['tint']) if item.get('tint') else None,
                         bright=item.get('bright', 1.0), crop=item.get('crop'),
                         hi_compress=item.get('hi_compress', 0.0))
            made.append(item['out'])
            print('  ' + item['out'] + '  (circle photo)')
        if 'knockout' in m:
            knockout(os.path.join(out, m['knockout'].get('out', 'knockout.png')),
                     **{k: v for k, v in m['knockout'].items() if k != 'out'})
            made.append(m['knockout'].get('out', 'knockout.png'))
        if 'petals' in m:
            pspec = {k: v for k, v in m['petals'].items() if k != 'out'}
            if 'col' in pspec:
                pspec['col'] = tuple(pspec['col'])
            petals(os.path.join(out, m['petals'].get('out', 'petal_radial.png')), **pspec)
            made.append(m['petals'].get('out', 'petal_radial.png'))
        if 'ridge' in m:
            rspec = {k: v for k, v in m['ridge'].items() if k != 'out'}
            rw = rspec.pop('w', w)
            if 'col' in rspec:
                rspec['col'] = tuple(rspec['col'])
            ridge(os.path.join(out, m['ridge'].get('out', 'ridge.png')), w=rw, **rspec)
            made.append(m['ridge'].get('out', 'ridge.png'))
        print('  transparent PNG: ' + ', '.join(x for x in made if isinstance(x, str) and x.endswith('.png')))
    return made


def self_test(out: str) -> int:
    """无外部素材的自测：合成一张测试照片，跑完整流程。"""
    tmp = tempfile.mkdtemp(prefix='atelier_selftest_')
    w, h = 640, 360
    im = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line((0, y, w, y), fill=(int(90 + 140 * t), int(110 + 110 * t), int(130 + 60 * t)))
    d.ellipse((380, 40, 560, 220), fill=(250, 246, 232))
    src = os.path.join(tmp, 'source.jpg')
    im.save(src, quality=90)

    cfg = {
        'canvas': [w, h],
        'dark_pages': [1],
        'pages': {
            '1': {'src': src, 'veil': ['R', 0.05, 0.84, 1.4]},
            '2': {'src': src, 'veil': ['V', 0.04, 0.58, 1.0]},
        },
        'masks': {
            'circles': [{'src': src, 'out': 'circle_test.png', 'size': 240,
                         'tint': [243, 238, 228], 'hi_compress': 0.18}],
            'knockout': {'out': 'knockout_test.png', 'w': 240, 'h': 240,
                         'hole': [40, 40, 200, 200], 'feather': 28, 'blur': 18},
            'petals': {'out': 'petal_test.png', 'size': 240, 'n': 12},
            'ridge': {'out': 'ridge_test.png'},
        },
    }
    files = run(cfg, tmp, out, 'all')
    for f in files:
        p = f if os.path.isfile(f) else os.path.join(out, f)
        if not os.path.isfile(p):
            print('SELFTEST FAIL missing: ' + p)
            return 1
    print('SELFTEST OK: %d outputs in %s' % (len(files), out))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--images', help='源摄影目录')
    ap.add_argument('--out', help='输出目录（svg_output 的 ../images）')
    ap.add_argument('--config', help='JSON 配置')
    ap.add_argument('--only', choices=['all', 'background', 'masks'], default='all')
    ap.add_argument('--self-test', action='store_true', help='合成图跑全流程，不依赖外部素材')
    a = ap.parse_args(argv)

    if a.self_test:
        # 自测产物统一进 %TEMP%/wb-scratch/<日期>-<任务>/，不污染当前工作区
        out = a.out or os.path.join(
            tempfile.gettempdir(), 'wb-scratch',
            time.strftime('%Y%m%d') + '-atelier-selftest')
        return self_test(out)
    if not (a.images and a.out and a.config):
        ap.error('--images / --out / --config are required unless --self-test')
    with open(a.config, encoding='utf-8') as fh:
        cfg = json.load(fh)
    files = run(cfg, a.images, a.out, a.only)
    print('done: %d outputs -> %s' % (len(files), a.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
