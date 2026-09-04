#!/usr/bin/env python3
"""Give every heading of a translated chapter the English heading's anchor id.

For each declared chapter and language, headings are paired by position (the heading
sequences are already identical). Where the English heading carries {#id} and the translated
heading carries a different id or none, the translated heading gets the English id and keeps
its own classes. Every link in any translated file that targeted the old id is rewritten to
the English id. Prints one line per change and a before-and-after count of links, in the
translated files, that target an English id the translation does not carry.

Deterministic. No model, no network. Usage: python3 modernization/sync-anchors.py [--dry-run]
"""
import re, glob, sys
dry = '--dry-run' in sys.argv
decl = re.findall(r'^\s*-\s*chapters/([A-Za-z0-9_]+)\.qmd', open('_quarto.yml').read(), re.M)
LANGS = ['es', 'fr', 'jp', 'pt', 'ru', 'tr', 'vn']
HEAD = re.compile(r'^(#{1,6}\s+.*?)(\s*\{[^}]*\})?\s*$')


def in_prose(lines):
    """Indices of lines outside every fenced block."""
    idx, fence = [], None
    for i, l in enumerate(lines):
        m = re.match(r'^\s*(`{3,})', l)
        if fence is None and m: fence = m.group(1); continue
        if fence is not None and re.match(r'^\s*' + fence + r'\s*$', l): fence = None; continue
        if fence is None: idx.append(i)
    return idx


def headings(lines):
    return [i for i in in_prose(lines) if HEAD.match(lines[i]) and lines[i].lstrip().startswith('#')]


def anchor(attr): m = re.search(r'#([A-Za-z0-9_-]+)', attr or ''); return m.group(1) if m else None


texts = {f: open(f, encoding='utf-8').read() for f in glob.glob('chapters/*.qmd')}


def dead_links():
    n = 0
    for st in decl:
        el = texts['chapters/%s.qmd' % st].split('\n'); eh = headings(el)
        for lang in LANGS:
            f = 'chapters/%s.%s.qmd' % (st, lang); tl = texts[f].split('\n'); th = headings(tl)
            ids = {anchor(HEAD.match(tl[i]).group(2)) for i in th} - {None}
            for i in eh:
                xe = anchor(HEAD.match(el[i]).group(2))
                if xe and xe not in ids:
                    n += len(re.findall(r'\(#%s\)' % re.escape(xe), texts[f]))
                    n += sum(len(re.findall(r'\.%s\.qmd#%s\)' % (lang, re.escape(xe)), t)) for g, t in texts.items() if g != f)
    return n


print('dead English-id links before:', dead_links())
changed, relinked = 0, 0
for st in decl:
    el = texts['chapters/%s.qmd' % st].split('\n'); eh = headings(el)
    for lang in LANGS:
        f = 'chapters/%s.%s.qmd' % (st, lang); tl = texts[f].split('\n'); th = headings(tl)
        assert len(eh) == len(th), f
        for ie, it in zip(eh, th):
            me, mt = HEAD.match(el[ie]), HEAD.match(tl[it])
            xe, xt = anchor(me.group(2)), anchor(mt.group(2))
            if not xe or xe == xt: continue
            attr = (mt.group(2) or '').strip()
            classes = re.findall(r'\.[A-Za-z0-9_-]+', attr)
            new_attr = '{#%s%s}' % (xe, ''.join(' ' + c for c in classes))
            tl[it] = mt.group(1).rstrip() + ' ' + new_attr
            print('%-36s %-45s -> %s' % (f, attr or '(none)', new_attr)); changed += 1
            if xt:
                old_in = r'\(#%s\)' % re.escape(xt); old_cross = r'\.%s\.qmd#%s\)' % (lang, re.escape(xt))
                for g in list(texts):
                    if g == f:
                        continue
                    n = len(re.findall(old_cross, texts[g]))
                    if n: texts[g] = re.sub(old_cross, '.%s.qmd#%s)' % (lang, xe), texts[g]); relinked += n
                joined = '\n'.join(tl); n = len(re.findall(old_in, joined))
                if n: tl = re.sub(old_in, '(#%s)' % xe, joined).split('\n'); relinked += n
        texts[f] = '\n'.join(tl)
print('headings changed %d, links rewritten %d' % (changed, relinked))
print('dead English-id links after:', dead_links())
if not dry:
    for f, t in texts.items():
        if open(f, encoding='utf-8').read() != t: open(f, 'w', encoding='utf-8', newline='').write(t)
