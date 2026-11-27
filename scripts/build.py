#!/usr/bin/env python3
"""Build a dependency-free static magazine for Pages or a future custom domain."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,urlunsplit
from xml.sax.saxutils import escape
import argparse,re,shutil
from editions import available_editions
ROOT=Path(__file__).resolve().parents[1]
OLD_ORIGIN='https://bornot-b2b-concept-2026.wry-calf-7403.chatgpt.site'
p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--output',default='_site');args=p.parse_args()
base=args.base_url.rstrip('/');parts=urlsplit(base)
if parts.scheme not in ('http','https') or not parts.netloc or parts.query or parts.fragment:raise SystemExit('base-url must be an absolute HTTP(S) URL without query/fragment')
prefix=parts.path.rstrip('/')
out=(ROOT/args.output).resolve()
if out==ROOT or ROOT not in out.parents or out==ROOT/'site':raise SystemExit('Output must be a separate directory within the repository')
if out.exists():shutil.rmtree(out)
shutil.copytree(ROOT/'site',out)
latest = available_editions(out)[-1]
def transform(url):
 if url.startswith(OLD_ORIGIN):return base+url[len(OLD_ORIGIN):]
 if url.startswith('/') and not url.startswith('//'):return prefix+url
 return url
for path in out.rglob('*.html'):
 text=path.read_text()
 text=re.sub(r'\b(href|src|content)=("|\')(.*?)\2',lambda m:m[1]+'='+m[2]+transform(m[3])+m[2],text)
 text=re.sub(r'(url=)(/[^"\']+)',lambda m:m[1]+prefix+m[2],text)
 # Legacy issue redirect uses a JavaScript URL, in addition to its meta refresh.
 text=text.replace("location.replace('/issue-01/'", "location.replace('"+prefix+"/issue-01/'")
 text=text.replace('location.replace("/issue-01/"', 'location.replace("'+prefix+'/issue-01/"')
 path.write_text(text)
# Homepages are independent journal pages; numbered editions keep their own URLs.
class Canonical(HTMLParser):
 def __init__(self,text):super().__init__();self.url=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='link' and 'canonical' in d.get('rel','').split():self.url=d.get('href')
# Discover canonical reader URLs, regardless of attribute order or quote style.
urls=set()
for path in out.rglob('*.html'):
 text=path.read_text()
 if 'noindex' in text or path.parent.name=='issue-00':continue
 canonical=Canonical(text).url
 if canonical:urls.add(canonical)
(out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+escape(u)+'</loc></url>\n' for u in sorted(urls))+'</urlset>\n')
(out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'/sitemap.xml\n')
(out/'.nojekyll').touch()
print('Built',out,'for',base,'with independent homepages and latest edition',latest)
