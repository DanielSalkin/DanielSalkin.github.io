#!/usr/bin/env python3
"""Indent the portfolio HTML without rewriting attributes or inline markup."""
from pathlib import Path
import re
import textwrap

TOKEN = re.compile(r'<!--.*?-->|<![^>]*>|</?[A-Za-z][^>]*>|[^<]+', re.S)
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
INLINE = {'a', 'abbr', 'b', 'br', 'code', 'em', 'i', 'small', 'span', 'strong', 'sub', 'sup', 'time'}
LEAF = INLINE | {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'figcaption', 'button', 'caption', 'th', 'td'}


def format_html(source):
    tokens = TOKEN.findall(source)
    output = []
    depth = 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        match = re.match(r'<(/?)([\w:-]+)', token)
        if not match:
            if token.strip():
                output.append('  ' * depth + token.strip())
            i += 1
            continue
        closing, name = match.groups()
        name = name.lower()
        if closing:
            depth -= 1
            if depth < 0:
                raise ValueError('Unbalanced HTML')
            output.append('  ' * depth + token.strip())
            i += 1
            continue
        if name in LEAF and name not in VOID:
            # Keep inline punctuation, spaces, and LaTeX intact within text blocks.
            j = i + 1
            balance = 1
            inline_only = True
            while j < len(tokens):
                nested = re.match(r'<(/?)([\w:-]+)', tokens[j])
                if nested:
                    end, child = nested.groups()
                    child = child.lower()
                    if child == name:
                        balance += -1 if end else 1
                        if balance == 0:
                            break
                    if child not in INLINE:
                        inline_only = False
                j += 1
            if j < len(tokens) and inline_only:
                content = ''.join(tokens[i + 1:j]).strip()
                if '<' not in content:
                    content = ' '.join(content.split())
                if '<' not in content and len(token + content + tokens[j]) + depth * 2 > 110:
                    output.append('  ' * depth + token)
                    output.extend(textwrap.wrap(content, width=110, initial_indent='  ' * (depth + 1), subsequent_indent='  ' * (depth + 1), break_long_words=False, break_on_hyphens=False))
                    output.append('  ' * depth + tokens[j])
                else:
                    output.append('  ' * depth + token + content + tokens[j])
                i = j + 1
                continue
        if name in {'section', 'article'}:
            section_id = re.search(r'\bid="([^"]+)"', token)
            label = section_id[1] if section_id else re.search(r'\bclass="([^"]+)"', token)
            label = label if isinstance(label, str) else label[1] if label else name
            comment = '<!-- ' + label.replace('-', ' ').title() + ' -->'
            if not output or output[-1].strip() != comment:
                output.append('')
                output.append('  ' * depth + comment)
        output.append('  ' * depth + token.strip())
        if name not in VOID and not token.endswith('/>'):
            depth += 1
        i += 1
    if depth:
        raise ValueError(f'Unbalanced HTML: {depth}')
    return '\n'.join(output) + '\n'


if __name__ == '__main__':
    for page in Path(__file__).resolve().parents[1].glob('*.html'):
        page.write_text(format_html(page.read_text()))
        print(f'Formatted {page.name}')
