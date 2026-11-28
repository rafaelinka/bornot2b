#!/usr/bin/env python3
"""Export the current edition as one offline, bilingual review document.

The export reads reader HTML directly, so editorial corrections remain the
source of truth. It does not publish, alter routes, or include raw book files.
"""
from pathlib import Path
from html import escape
from PIL import Image
import argparse, base64, json, re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
parser = argparse.ArgumentParser()
parser.add_argument('--edition', default='issue-05')
parser.add_argument('--output', required=True)
args = parser.parse_args()
if not re.fullmatch(r'issue-\d{2}', args.edition):
    raise SystemExit('Expected a numbered issue, such as issue-05')
edition = args.edition
files = [SITE / 'index.html', SITE / 'ru/index.html',
         SITE / 'archive/index.html', SITE / 'ru/archive/index.html',
         SITE / edition / 'index.html', SITE / 'ru' / edition / 'index.html']
for locale in ('', 'ru/'):
    files += sorted(p for p in (SITE / locale / 'read').glob('*/index.html')
                    if f'/assets/{edition}/' in p.read_text())
routes = {'/' + str(p.relative_to(SITE)).removesuffix('index.html'): p for p in files}
assets, sections, symbols = {}, [], []

def key(route):
    return 'review-' + route.strip('/').replace('/', '-') if route != '/' else 'review-home-en'

def href(value, route):
    if value.startswith('#'):
        return '#' + key(route) + '--' + value[1:]
    if value.startswith('/') and not value.startswith('//'):
        path, _, anchor = value.partition('#')
        if path in routes:
            return '#' + key(path) + ('--' + anchor if anchor else '')
        return 'https://bornot2b.com' + value
    return value

for route, path in routes.items():
    source = path.read_text()
    body = re.search(r'<body[^>]*>(.*?)</body>', source, re.S).group(1)
    body = re.sub(r'<script\b.*?</script>', '', body, flags=re.S)
    body = re.sub(r'\bhref="([^"]*)"', lambda m: 'href="' + href(m[1], route) + '"', body)
    body = re.sub(r'\bid="([^"]*)"', lambda m: 'id="' + key(route) + '--' + m[1] + '"', body)
    body = '<div id="' + key(route) + '--top"></div>' + body

    def embed_image(match):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', match[0]))
        src = attrs.get('src', '')
        if not src.startswith('/assets/'):
            return match[0]
        file = SITE / src.lstrip('/')
        if not file.is_file():
            raise FileNotFoundError(file)
        if src not in assets:
            asset_id = 'review-image-' + str(len(assets))
            assets[src] = asset_id
            with Image.open(file) as image:
                width, height = image.size
            mime = 'image/webp' if file.suffix == '.webp' else 'image/png'
            uri = 'data:' + mime + ';base64,' + base64.b64encode(file.read_bytes()).decode()
            symbols.append(f'<symbol id="{asset_id}" viewBox="0 0 {width} {height}">'
                           f'<image width="{width}" height="{height}" href="{uri}"/></symbol>')
        width, height = attrs.get('width', '1536'), attrs.get('height', '1024')
        label = attrs.get('alt', '')
        classes = 'review-image ' + attrs.get('class', '')
        return (f'<svg class="{classes}" width="{width}" height="{height}" '
                f'viewBox="0 0 {width} {height}" role="img" aria-label="{label}">'
                f'<use href="#{assets[src]}"/></svg>')

    body = re.sub(r'<img\b[^>]*>', embed_image, body)
    lang = 'ru' if route.startswith('/ru/') else 'en'
    sections.append(f'<section class="review-page" id="{key(route)}" lang="{lang}">{body}</section>')

css = '\n'.join((SITE / p).read_text() for p in [
    'assets/editorial.css', 'assets/glossy.css', 'assets/archive-covers.css',
    f'assets/{edition}/issue05.css'])
css = re.sub(r'(?<![-\w])img(?![-\w])', ':is(img,svg.review-image)', css)
css += '''
.review-image{display:block;max-width:100%;height:auto}
.review-banner{background:#19231e;color:#fff;padding:10px 20px;font:12px/1.6 Arial,sans-serif;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
.review-banner a{color:#fff}.review-banner b{color:#ffca25}.archive-main{padding-top:35px}
.review-page{display:none}.review-page:target,.review-page:has(:target){display:block}
'''
default_id = key('/ru/' + edition + '/')
css += f'#{default_id}{{display:block}}body:has(.review-page:target,.review-page :target) #{default_id}:not(:target):not(:has(:target)){{display:none}}'
number = edition[-2:]
html = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        f'<title>B(ornot)2B №{number} — предпросмотр / review copy</title><style>{css}</style></head>'
        '<body class="issue-five"><div class="review-banner"><span>'
        f'<b>ПРЕДПРОСМОТР / REVIEW COPY</b> · №{number} · Не опубликовано / Unpublished</span><span>'
        f'<a href="#{default_id}">RU</a> · <a href="#{key("/" + edition + "/")}">EN</a> · '
        f'<a href="#{key("/ru/")}">Главная / Home</a></span></div>'
        '<svg aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden"><defs>'
        + ''.join(symbols) + '</defs></svg>' + ''.join(sections) + '</body></html>')
out = Path(args.output).resolve()
if SITE == out or SITE in out.parents:
    raise SystemExit('Review copies must be exported outside the public source directory')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html)
print(json.dumps({'file': str(out), 'bytes': out.stat().st_size,
                  'pages': len(routes), 'images': len(assets)}))
