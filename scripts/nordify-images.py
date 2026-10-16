#!/usr/bin/env python3
"""Make non-destructive, self-contained SVG image variants with a Nord color grade.
No image generation, external service, or raster editing is involved.
Run from any directory: python3 scripts/nordify-images.py
"""
from pathlib import Path
import base64, struct, json, html, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/nordified'
def dimensions(data,suffix):
 if suffix=='.png':return struct.unpack('>II',data[16:24])
 if suffix=='.svg':
  s=data.decode();v=re.search(r'viewBox=[\'"]([^\'"]+)',s)
  if v:
   n=[float(x) for x in v[1].replace(',',' ').split()];return n[2],n[3]
  return 800,800
 i=2;orientation=1
 while i<len(data):
  if data[i]!=255:i+=1;continue
  marker=data[i+1];i+=2
  if marker in [216,217]:continue
  length=int.from_bytes(data[i:i+2],'big');segment=data[i+2:i+length]
  if marker==225 and segment.startswith(b'Exif\0\0'):
   try:
    t=segment[6:];order='little' if t[:2]==b'II' else 'big';off=int.from_bytes(t[4:8],order);count=int.from_bytes(t[off:off+2],order)
    for j in range(count):
     ent=t[off+2+j*12:off+14+j*12]
     if int.from_bytes(ent[:2],order)==274:orientation=int.from_bytes(ent[8:10],order)
   except (ValueError,IndexError):pass
  if marker in [192,193,194,195,197,198,199,201,202,203,205,206,207]:
   h,w=struct.unpack('>HH',segment[1:5]);return (h,w) if orientation in [5,6,7,8] else (w,h)
  i+=length
 raise ValueError('Unknown image dimensions')
sources=[p for p in (ROOT/'documentation').rglob('*') if p.suffix.lower() in ['.jpg','.jpeg','.png','.svg'] and 'Portfolio Photos' not in p.parts]
sources+=list((ROOT/'documentation/Portfolio Photos/Logos').glob('*.svg'))+list((ROOT/'documentation/Portfolio Photos/Logos').glob('*.png'))+[ROOT/'assets/iem-mark.svg']
manifest={}
for src in sorted(sources):
 rel=src.relative_to(ROOT);target=OUT/rel.parent/(rel.name+'.svg');target.parent.mkdir(parents=True,exist_ok=True)
 data=src.read_bytes();suffix=src.suffix.lower();w,h=dimensions(data,suffix)
 mime={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'}[suffix]
 # 55% source color + 45% luminance mapped from Polar Night to Snow Storm.
 # This cools and desaturates images without changing geometric information.
 matrix='0.505 0.302 0.043 0 0.081 0.090 0.747 0.030 0 0.092 0.092 0.308 0.580 0 0.113 0 0 0 1 0'
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="0 0 {w:g} {h:g}"><title>{html.escape(src.stem)} — Nord tone</title><defs><filter id="nord" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{matrix}"/></filter></defs><image width="100%" height="100%" preserveAspectRatio="xMidYMid meet" filter="url(#nord)" href="data:{mime};base64,{base64.b64encode(data).decode()}"/></svg>'''
 target.write_text(svg);manifest[rel.as_posix()]=target.relative_to(ROOT).as_posix()
OUT.mkdir(parents=True,exist_ok=True);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'Created {len(manifest)} Nord-toned SVG variants in {OUT}')
