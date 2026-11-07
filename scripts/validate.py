#!/usr/bin/env python3
"""Validate reader routes, citations, assets and publish exclusions."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import argparse,re,sys
from editions import available_editions
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--directory',default='_site');p.add_argument('--base-url',required=True);a=p.parse_args()
root=ROOT/a.directory;base=urlsplit(a.base_url);prefix=base.path.rstrip('/')
class Doc(HTMLParser):
 def __init__(self,text):super().__init__();self.ids=[];self.refs=[];self.images=[];self.covers=[];self.h1=0;self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='html':self.lang=d.get('lang')
  if tag in ('link','meta') and d.get('rel')=='canonical':self.canonical=d.get('href')
  if 'id' in d:self.ids.append(d['id'])
  for k in ('src','href'):
   if d.get(k):self.refs.append(d[k])
  if tag=='h1':self.h1+=1
  if tag=='img':self.images.append(d)
  if tag=='a' and 'archive-cover' in d.get('class','').split():self.covers.append(d.get('href'))
docs={p:Doc(p.read_text()) for p in root.rglob('*.html')};errors=[];count=0
for p,d in docs.items():
 if len(d.ids)!=len(set(d.ids)):errors.append(f'{p}: duplicate ids')
 if 'issue-00' not in p.parts and d.h1!=1:errors.append(f'{p}: expected one h1')
 for u in d.refs:
  q=urlsplit(u)
  if q.scheme and (q.scheme not in ('http','https') or q.netloc!=base.netloc):continue
  if u.startswith('//'):continue
  path=unquote(q.path)
  if path.startswith('/'):
   if prefix and not (path==prefix or path.startswith(prefix+'/')):errors.append(f'{p}: escapes project prefix: {u}');continue
   path=path[len(prefix):] if prefix else path;target=root/path.lstrip('/')
  elif path:target=p.parent/path
  else:target=p
  if target.is_dir():target/='index.html'
  if not target.exists():errors.append(f'{p}: missing {u}');continue
  if q.fragment and target.suffix=='.html' and q.fragment not in docs[target].ids:errors.append(f'{p}: missing fragment {u}')
  count+=1
 for img in d.images:
  if not all(k in img for k in ('alt','width','height')):errors.append(f'{p}: incomplete image attributes')
for p in root.rglob('*'):
 if p.is_file() and p.suffix.lower() == '.webp':
  b=p.read_bytes()
  if len(b)<12 or b[:4]!=b'RIFF' or b[8:12]!=b'WEBP' or int.from_bytes(b[4:8], 'little')+8!=len(b):errors.append(f'{p}: invalid WebP asset')
 if p.suffix.lower() in ('.pdf','.epub','.env') or 'editorial' in p.relative_to(root).parts:errors.append(f'Excluded content: {p}')
 if base.netloc!='bornot-b2b-concept-2026.wry-calf-7403.chatgpt.site' and p.is_file() and p.suffix in ('.html','.js','.css') and 'bornot-b2b-concept-2026.wry-calf-7403.chatgpt.site' in p.read_text():errors.append(f'{p}: old origin')
editions = available_editions(root)
latest = editions[-1]
for locale in ('', 'ru/'):
 locale_root = root / locale
 assert (locale_root / 'index.html').read_bytes() == (locale_root / latest / 'index.html').read_bytes(), f'{locale} homepage must match {latest}'
 archive = docs[locale_root / 'archive/index.html']
 assert Counter(archive.covers) == Counter(f'{prefix}/{locale}{issue}/' for issue in editions), f'{locale} archive must have one cover per issue'
english_readers = {p.parent.name for p in root.glob('read/*/index.html')}
russian_readers = {p.parent.name for p in root.glob('ru/read/*/index.html')}
assert english_readers == russian_readers, 'Missing counterpart for a reader page'
assert {'deal-system', 'jolt-effect', 'partnership-economy', 'warehouse-contract'} <= english_readers, 'Issue 01 reader pages must be preserved'
for p,d in docs.items():
 if 'issue-00' in p.parts:continue
 text=p.read_text();is_ru='ru' in p.relative_to(root).parts
 if d.lang!=('ru' if is_ru else 'en'):errors.append(f'{p}: incorrect document language')
 if not is_ru and re.search('[А-Яа-яЁё]',re.sub('<[^>]*>',' ',text)):errors.append(f'{p}: untranslated Cyrillic reader text')
 for language in ('en','ru'):
  if f'hreflang="{language}"' not in text:errors.append(f'{p}: missing {language} alternate')
for slug,total in [('partnership-economy',6),('jolt-effect',7)]:
 text=(root/'read'/slug/'index.html').read_text()
 if text.count('class="book-idea"')!=total:errors.append(f'{slug}: expected {total} book ideas')
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(docs)} reader pages, {count} local references, no raw books or internal editorial content.')
