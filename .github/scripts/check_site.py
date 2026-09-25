#!/usr/bin/env python3
"""網站靜態檢查：HTML 結構、站內連結與錨點、證據標籤、版型規範。

用法：
  python3 .github/scripts/check_site.py             # 站內檢查（PR 與部署前必跑）
  python3 .github/scripts/check_site.py --external  # 另外檢查外部連結（僅 404/410 視為失效）

只用標準函式庫，無相依套件。
"""
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CSS = os.path.join(ROOT, 'assets', 'css', 'main.css')
VOID = {'meta', 'link', 'br', 'hr', 'img', 'input', 'col', 'area', 'base',
        'source', 'wbr', 'track', 'embed', 'param'}
IMPLIED_END = {'p', 'li', 'td', 'th', 'tr', 'dd', 'dt'}
EV_CLASSES = {'ev-verified', 'ev-vendor', 'ev-third', 'ev-unverified'}
# 由 JS 動態加上的 class，不會出現在 HTML 原始碼
JS_CLASSES = {'active', 'open', 'code-wrap', 'copy-btn'}

errors = []


def error(path, line, msg):
    errors.append(f'{path}:{line}: {msg}')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.ids = {}
        self.links = []
        self.classes = set()
        self.metas = {}
        self.has_title = False
        self.lang = None
        self.ev_open = None
        self.ev_text = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'title':
            self.has_title = True
        if tag == 'meta' and a.get('name'):
            self.metas[a['name']] = a.get('content', '')
        if 'id' in a:
            if a['id'] in self.ids:
                error(self.path, line, f'重複的 id="{a["id"]}"（先前在第 {self.ids[a["id"]]} 行）')
            self.ids[a['id']] = line
        if tag == 'a' and 'href' in a:
            self.links.append((a['href'], line))
        if 'style' in a:
            error(self.path, line, '不可使用 inline style，請改用 main.css 的 class')
        if tag == 'style':
            error(self.path, line, '不可使用 <style> 區塊，請寫進 main.css')
        if tag == 'script' and 'src' not in a:
            error(self.path, line, '不可使用 inline <script>（CSP 只允許外部 script）')
        cls = (a.get('class') or '').split()
        self.classes.update(cls)
        if 'ev' in cls:
            kinds = [c for c in cls if c.startswith('ev-')]
            if len(kinds) != 1 or kinds[0] not in EV_CLASSES:
                error(self.path, line, f'證據標籤 class 不正確：{a.get("class")}')
            self.ev_open = line
            self.ev_text = ''
        if tag not in VOID:
            self.stack.append((tag, line))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == 'span' and self.ev_open is not None:
            if '【' in self.ev_text or '】' in self.ev_text:
                error(self.path, self.ev_open, f'證據標籤不加【】括號：{self.ev_text.strip()}')
            self.ev_open = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, l in self.stack[i + 1:]:
                    if t not in IMPLIED_END:
                        error(self.path, l, f'<{t}> 未關閉（被第 {self.getpos()[0]} 行的 </{tag}> 截斷）')
                del self.stack[i:]
                return
        error(self.path, self.getpos()[0], f'多餘的 </{tag}>')

    def handle_data(self, data):
        if self.ev_open is not None:
            self.ev_text += data


def main():
    check_external = '--external' in sys.argv
    files = sorted(f for f in os.listdir(ROOT) if f.endswith('.html'))
    pages = {}
    for f in files:
        p = Page(f)
        with open(os.path.join(ROOT, f), encoding='utf-8') as fh:
            p.feed(fh.read())
        p.close()
        for t, l in p.stack:
            if t not in IMPLIED_END | {'html', 'body'}:
                error(f, l, f'<{t}> 未關閉')
        if p.lang != 'zh-Hant':
            error(f, 1, '<html> 須設 lang="zh-Hant"')
        if not p.has_title:
            error(f, 1, '缺少 <title>')
        if 'noindex' not in p.metas.get('robots', ''):
            error(f, 1, '缺少 <meta name="robots" content="noindex, nofollow">')
        if f != '404.html' and not p.metas.get('description'):
            error(f, 1, '缺少 <meta name="description">')
        pages[f] = p

    # 站內連結與錨點
    external = set()
    for f, p in pages.items():
        for href, line in p.links:
            if href.startswith(('http://', 'https://')):
                external.add(href)
                continue
            if href.startswith(('mailto:', 'tel:')):
                continue
            target, _, frag = href.partition('#')
            target = target or f
            if target not in pages:
                if not os.path.exists(os.path.join(ROOT, target)):
                    error(f, line, f'連到不存在的檔案：{href}')
                continue
            if frag and frag not in pages[target].ids:
                error(f, line, f'連到不存在的錨點：{href}')

    # HTML 用到的 class 必須在 main.css 定義
    with open(CSS, encoding='utf-8') as fh:
        css_classes = set(re.findall(r'\.([A-Za-z_][\w-]*)', re.sub(r'url\([^)]*\)', '', fh.read())))
    for f, p in pages.items():
        for c in sorted(p.classes - css_classes - JS_CLASSES):
            error(f, 1, f'class "{c}" 未在 assets/css/main.css 定義')

    if check_external:
        check_links(sorted(external))

    for e in errors:
        print(f'::error::{e}' if os.environ.get('GITHUB_ACTIONS') else e)
    print(f'檢查 {len(files)} 個頁面，{len(errors)} 個問題'
          + (f'；外部連結 {len(external)} 條' if check_external else ''))
    return 1 if errors else 0


def check_links(urls):
    """只把 404/410 視為失效；403、逾時多半是網站擋自動請求，不列為錯誤。"""
    def probe(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (link-check)'})
        try:
            with urllib.request.urlopen(req, timeout=30):
                return url, 200
        except urllib.error.HTTPError as e:
            return url, e.code
        except Exception:
            return url, None

    with ThreadPoolExecutor(max_workers=12) as pool:
        for url, code in pool.map(probe, urls):
            if code in (404, 410):
                error('appendix.html', 1, f'外部連結失效（HTTP {code}）：{url}')


if __name__ == '__main__':
    sys.exit(main())
