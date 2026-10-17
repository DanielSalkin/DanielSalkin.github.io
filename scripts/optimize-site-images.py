#!/usr/bin/env python3
"""Optimize a packaged site in place; never modify source photographs.

Requires Pillow (see requirements-build.txt). Run after package-site.py.
"""
import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from PIL import Image, ImageOps

RASTER = {'.jpg', '.jpeg', '.png'}


def optimize(root):
    generated = root / 'assets' / 'optimized'
    generated.mkdir(parents=True, exist_ok=True)
    cache = {}
    originals = set()

    def convert(ref):
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path:
            return None
        relative = Path(unquote(url.path))
        if relative.suffix.lower() not in RASTER or 'Logos' in relative.parts or relative.parts[0] == 'assets':
            return None
        source = (root / relative).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f'Invalid image: {ref}')
        if source in cache:
            return cache[source]
        originals.add(source)
        digest = hashlib.sha256(relative.as_posix().encode()).hexdigest()[:16]
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original)
            image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
            dimensions = image.size
            widths = sorted({min(width, image.width) for width in (480, 960, 1600, 2400)})
            variants = []
            for width in widths:
                height = max(1, round(image.height * width / image.width))
                resized = image.resize((width, height), Image.Resampling.LANCZOS)
                target = generated / f'{digest}-{width}.webp'
                # Preserve fine schematic lines without JPEG-style artifacts.
                resized.save(target, 'WEBP', quality=82, method=6, lossless=relative.suffix.lower() == '.png')
                variants.append((width, target.relative_to(root).as_posix()))
        display = max((v for v in variants if v[0] <= 1600), default=variants[0])
        cache[source] = dimensions, variants, display[1]
        return cache[source]

    class Rewrite(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.output = []

        def handle_starttag(self, tag, attrs):
            data = dict(attrs)
            if tag == 'img' and data.get('src'):
                result = convert(data['src'])
                if result:
                    (width, height), variants, src = result
                    data.update(src=src, width=str(width), height=str(height),
                                srcset=', '.join(f'{path} {w}w' for w, path in variants if w <= 1600 or len(variants) == 1),
                                sizes='(max-width: 700px) calc(100vw - 48px), (max-width: 1100px) calc(100vw - 240px), 1036px')
                    # Very small originals can have only one variant above 1600.
                    if not data['srcset']:
                        data['srcset'] = f'{src} {width}w'
                data['decoding'] = 'async'
            elif tag == 'a' and data.get('href'):
                result = convert(data['href'])
                if result:
                    data['href'] = result[1][-1][1]
            self.output.append('<' + tag + ''.join(' ' + key + ('' if value is None else '="' + escape(value, quote=True) + '"') for key, value in data.items()) + '>')

        def handle_endtag(self, tag): self.output.append(f'</{tag}>')
        def handle_data(self, data): self.output.append(data)
        def handle_entityref(self, name): self.output.append(f'&{name};')
        def handle_charref(self, name): self.output.append(f'&#{name};')
        def handle_comment(self, text): self.output.append(f'<!--{text}-->')
        def handle_decl(self, decl): self.output.append(f'<!{decl}>')

    before = sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
    for page in root.glob('*.html'):
        parser = Rewrite()
        parser.feed(page.read_text())
        page.write_text(''.join(parser.output))
    # Original full-size photos are no longer needed by the generated site.
    for original in originals:
        original.unlink()
    after = sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
    print(f'Optimized {len(cache)} images; site size {before / 1e6:.1f} MB → {after / 1e6:.1f} MB')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', required=True)
    optimize(Path(parser.parse_args().site).resolve())
