#!/usr/bin/env python3
"""Validate reader routes, citations, assets and publish exclusions."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import argparse,re,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--directory',default='_site');p.add_argument('--base-url',required=True);a=p.parse_args()
root=ROOT/a.directory;base=urlsplit(a.base_url);prefix=base.path.rstrip('/')
class Doc(HTMLParser):
 def __init__(self,text):super().__init__();self.ids=[];self.refs=[];self.images=[];self.h1=0;self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  for k in ('src','href'):
   if d.get(k):self.refs.append(d[k])
  if tag=='h1':self.h1+=1
  if tag=='img':self.images.append(d)
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
 if p.is_file() and p.suffix in ('.html','.js','.css') and 'bornot-b2b-concept-2026.wry-calf-7403.chatgpt.site' in p.read_text():errors.append(f'{p}: old origin')
assert (root/'index.html').read_bytes()==(root/'issue-01/index.html').read_bytes(),'Homepage and latest issue differ'
assert len(list(root.glob('read/*/index.html')))==4,'Expected four long reads'
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(docs)} reader pages, {count} local references, no raw books or internal editorial content.')
