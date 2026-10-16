#!/usr/bin/env python3
"""Package only site pages and their referenced local assets for GitHub Pages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse, re, shutil
ROOT = Path(__file__).resolve().parents[1]
class References(HTMLParser):
    def __init__(self):
        super().__init__(); self.paths = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('src', 'href'):
            if key in attrs:
                self.paths.append(attrs[key])
def collect():
    files = {Path('styles.css'), Path('script.js'), Path('.nojekyll')}
    for page in ROOT.glob('*.html'):
        files.add(page.relative_to(ROOT))
        parser = References(); parser.feed(page.read_text())
        for ref in parser.paths:
            url = urlsplit(ref)
            if not url.scheme and not url.netloc and url.path:
                files.add(Path(unquote(url.path)))
    for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)', (ROOT/'styles.css').read_text()):
        url = urlsplit(ref)
        if not url.scheme and not url.netloc and url.path:
            files.add(Path(unquote(url.path)))
    files.update(p.relative_to(ROOT) for p in (ROOT/'licenses').rglob('*') if p.is_file())
    for rel in files:
        source = (ROOT/rel).resolve()
        if not source.is_relative_to(ROOT) or not source.is_file():
            raise ValueError(f'Missing or invalid site file: {rel}')
    return sorted(files)
def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
    output = Path(parser.parse_args().output).resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise ValueError('Output must not contain the source directory')
    files = collect()
    output.mkdir(parents=True, exist_ok=True)
    for rel in files:
        target = output/rel; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/rel, target)
    print(f'Packaged {len(files)} files into {output}')
if __name__ == '__main__': main()
