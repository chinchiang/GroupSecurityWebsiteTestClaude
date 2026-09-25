#!/usr/bin/env python3
"""把 Noto Sans TC／Noto Serif TC 子集化為本站實際用到的字元，輸出到 assets/fonts/。

字型改由本站提供，不再連 Google Fonts：中國大陸無法存取 fonts.googleapis.com，
且可避免把瀏覽紀錄交給第三方；CSP 也因此只需允許 'self'。

用法（僅在內文新增字元、check_site.py 回報「字型子集缺字」時執行）：
  python3 -m venv .venv && .venv/bin/pip install fonttools brotli
  # 從 https://github.com/google/fonts 下載 ofl/notosanstc/NotoSansTC[wght].ttf
  #                                   與 ofl/notoseriftc/NotoSerifTC[wght].ttf
  .venv/bin/python .github/scripts/build_fonts.py NotoSansTC[wght].ttf NotoSerifTC[wght].ttf

輸出：
  assets/fonts/noto-sans-tc.woff2    可變字重 400–700
  assets/fonts/noto-serif-tc.woff2   可變字重 600–700
  assets/fonts/charset.txt           子集包含的字元（check_site.py 據此檢查缺字）
"""
import glob
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'fonts')
# (來源檔, 輸出檔, 保留的字重範圍)
TARGETS = [('noto-sans-tc.woff2', (400, 700)), ('noto-serif-tc.woff2', (600, 700))]


def site_chars():
    """HTML、JS（動態插入的按鈕文字）、CSS（content）用到的字元，加上完整 ASCII。"""
    chars = {chr(c) for c in range(0x20, 0x7f)}
    files = glob.glob(os.path.join(ROOT, '*.html')) + [
        os.path.join(ROOT, 'assets', 'js', 'main.js'),
        os.path.join(ROOT, 'assets', 'css', 'main.css')]
    for f in files:
        with open(f, encoding='utf-8') as fh:
            chars.update(fh.read())
    return ''.join(sorted(c for c in chars if not c.isspace()))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    text = site_chars()
    os.makedirs(OUT, exist_ok=True)
    for src, (out, (lo, hi)) in zip(sys.argv[1:], TARGETS):
        # 先子集化再縮小字重範圍：順序相反時 fontTools 會在 gvar 上出錯，也較慢
        font = TTFont(src, lazy=False)
        opts = subset.Options()
        opts.layout_features = ['*']
        opts.name_IDs = ['*']
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(text=text)
        sub.subset(font)
        font = instancer.instantiateVariableFont(font, {'wght': (lo, hi)})
        path = os.path.join(OUT, out)
        font.flavor = 'woff2'
        font.save(path)
        print(f'{out}: {os.path.getsize(path) / 1024:.0f} KB')
    with open(os.path.join(OUT, 'charset.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text + '\n')
    print(f'charset.txt: {len(text)} 字元')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
