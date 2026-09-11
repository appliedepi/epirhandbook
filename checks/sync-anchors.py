#!/usr/bin/env python3
"""Give every heading of a translated chapter the English heading's anchor id.

For each declared chapter and language, headings are paired by position (the heading
sequences are already identical). Where the English heading carries {#id} and the translated
heading carries a different id or none, the translated heading gets the English id and keeps
its own classes. Every link in any translated file that targeted the old id is rewritten to
the English id. Prints one line per change and a before-and-after count of links, in the
translated files, that target an English id the translation does not carry.

The landing page, content/<lang>/index.qmd, is outside the chapter set. Each language writes
its own landing page, so its headings are not a copy of the English headings.

Deterministic. No model, no network. Usage: python3 checks/sync-anchors.py [--dry-run]
"""
import re, glob, sys

USAGE = __doc__.strip().split('Usage: ')[1].strip()
unknown = [a for a in sys.argv[1:] if a != '--dry-run']
if unknown:
    print('unknown argument %s\nUsage: %s' % (unknown[0], USAGE), file=sys.stderr)
    sys.exit(2)
dry = '--dry-run' in sys.argv
LANGS = re.findall(r'^\s*-\s*code:\s*([A-Za-z0-9_]+)', open('languages.yml').read(), re.M)
MAIN = re.search(r'^main:\s*([A-Za-z0-9_]+)', open('languages.yml').read(), re.M).group(1)
LANGS = [l for l in LANGS if l != MAIN]
LANDING = 'index'
decl = re.findall(r'^\s*-\s*([A-Za-z0-9_]+)\.qmd',
                  open('content/%s/_quarto.yaml' % MAIN).read(), re.M)
decl = [s for s in decl if s != LANDING]
HEAD = re.compile(r'^(#{1,6}\s+.*?)(\s*\{[^}]*\})?\s*$')


def chapter(stem, lang):
    """The path of one chapter file: content/<lang>/<stem>.qmd."""
    return 'content/%s/%s.qmd' % (lang, stem)


def language(path):
    """The language of a chapter file: the folder that holds it."""
    return path.split('/')[1]


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


def cross_link(stem, ident):
    """The pattern for a link to <stem>.qmd#<ident> from another file of the same language.

    The lookbehind holds the match to a whole file name. Without it the stem matches the tail
    of a longer name, so a link to ggplot_basics.qmd reads as a link to basics.qmd.
    """
    return r'(?<![A-Za-z0-9_])%s\.qmd#%s\)' % (re.escape(stem), re.escape(ident))


texts = {f: open(f, encoding='utf-8').read() for f in glob.glob('content/*/*.qmd')}


def dead_links():
    n = 0
    for st in decl:
        el = texts[chapter(st, MAIN)].split('\n'); eh = headings(el)
        for lang in LANGS:
            f = chapter(st, lang); tl = texts[f].split('\n'); th = headings(tl)
            ids = {anchor(HEAD.match(tl[i]).group(2)) for i in th} - {None}
            for i in eh:
                xe = anchor(HEAD.match(el[i]).group(2))
                if xe and xe not in ids:
                    n += len(re.findall(r'\(#%s\)' % re.escape(xe), texts[f]))
                    n += sum(len(re.findall(cross_link(st, xe), t))
                             for g, t in texts.items() if g != f and language(g) == lang)
    return n


print('dead English-id links before:', dead_links())
changed, relinked = 0, 0
for st in decl:
    el = texts[chapter(st, MAIN)].split('\n'); eh = headings(el)
    for lang in LANGS:
        f = chapter(st, lang); tl = texts[f].split('\n'); th = headings(tl)
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
                old_in = r'\(#%s\)' % re.escape(xt)
                old_cross = cross_link(st, xt)
                for g in list(texts):
                    if g == f or language(g) != lang:
                        continue
                    n = len(re.findall(old_cross, texts[g]))
                    if n: texts[g] = re.sub(old_cross, '%s.qmd#%s)' % (st, xe), texts[g]); relinked += n
                joined = '\n'.join(tl); n = len(re.findall(old_in, joined))
                if n: tl = re.sub(old_in, '(#%s)' % xe, joined).split('\n'); relinked += n
        texts[f] = '\n'.join(tl)
print('headings changed %d, links rewritten %d' % (changed, relinked))
print('dead English-id links after:', dead_links())
if not dry:
    for f, t in texts.items():
        if open(f, encoding='utf-8').read() != t: open(f, 'w', encoding='utf-8', newline='').write(t)
