#!/usr/bin/env python3
"""Validate packaged pages, intrinsic image dimensions, and responsive image URLs."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


def check(root, optimized=False):
    count = 0
    class Audit(HTMLParser):
        def handle_starttag(self, tag, attrs):
            nonlocal count
            attrs = dict(attrs)
            refs = [attrs[key] for key in ('src', 'href') if attrs.get(key)]
            refs += [candidate.strip().split()[0] for candidate in attrs.get('srcset', '').split(',') if candidate.strip()]
            for ref in refs:
                url = urlsplit(ref)
                if not url.scheme and not url.netloc and url.path:
                    target = (root / unquote(url.path)).resolve()
                    if not target.is_relative_to(root) or not target.is_file():
                        raise ValueError(f'{page.name}: broken local reference {ref}')
            if tag == 'img' and attrs.get('src'):
                count += 1
                if int(attrs.get('width', 0)) <= 0 or int(attrs.get('height', 0)) <= 0:
                    raise ValueError(f'{page.name}: image dimensions missing: {attrs["src"]}')
                if optimized and attrs['src'].startswith('documentation/') and '/Logos/' not in attrs['src'] and not attrs['src'].endswith('.svg'):
                    raise ValueError(f'{page.name}: unoptimized image: {attrs["src"]}')
    for page in root.glob('*.html'):
        Audit().feed(page.read_text())
    print(f'Checked all local page references and dimensions for {count} images')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', required=True)
    parser.add_argument('--require-optimized', action='store_true')
    args = parser.parse_args()
    check(Path(args.site).resolve(), args.require_optimized)
