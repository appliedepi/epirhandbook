#!/usr/bin/env python3
"""Make every R code chunk of every translated chapter identical in code to the English chunk,
keeping the translated comments where the code line is the same.

For each chapters/<chapter>.<lang>.qmd whose chunk count equals the English chapter's, walk the
chunks in order. For each chunk, the output is the English chunk, line by line, except that a
line whose code part (the text before any # comment, right-stripped) equals the code part of a
line in the translated chunk keeps the translated line, so the translator's comment survives.
The fence line with the chunk options is taken from the English. A translated file whose
chunk count differs from the English is skipped and listed: it needs a hand alignment.

Deterministic. No model, no network. Prints one line per changed file and a summary.

Usage:
    python3 modernization/sync-chunks.py [--langs es,fr,jp,pt,ru,tr,vn] [--dry-run] [--only FILE ...]
"""
import argparse
import glob
import os
import re
import sys

FENCE = re.compile(r'^(\s*)(`{3,})\s*\{r[ ,}]')


def split(text):
    """Return a list of segments: ('prose', lines) or ('chunk', fence_line, body_lines, close_line)."""
    segs, cur, fence, i = [], [], None, 0
    lines = text.split('\n')
    prose = []
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            if prose: segs.append(('prose', prose)); prose = []
            fence = m.group(2); body = []; j = i + 1
            while j < len(lines) and not re.match(r'^\s*' + fence + r'\s*$', lines[j]):
                body.append(lines[j]); j += 1
            if j >= len(lines):
                raise ValueError('unclosed chunk at line %d' % (i + 1))
            segs.append(('chunk', lines[i], body, lines[j])); i = j + 1
        else:
            prose.append(lines[i]); i += 1
    if prose: segs.append(('prose', prose))
    return segs


def code_part(line):
    """The code before a # comment, ignoring # inside a string, right-stripped."""
    out, q = [], None
    for ch in line:
        if q:
            out.append(ch)
            if ch == q: q = None
        elif ch in '"\'':
            q = ch; out.append(ch)
        elif ch == '#':
            break
        else:
            out.append(ch)
    return ''.join(out).rstrip()


def merge(en_body, tr_body):
    """English code, translated comments where the code line matches. Returns (lines, kept, fallback)."""
    by_code = {}
    for l in tr_body:
        c = code_part(l)
        if c.strip() and '#' in l and c not in by_code: by_code[c] = l
    out, kept, fallback = [], 0, 0
    for l in en_body:
        c = code_part(l)
        if c.strip() and c in by_code and by_code[c] != l:
            out.append(by_code[c]); kept += 1
        else:
            out.append(l)
            if '#' in l and c.strip(): fallback += 1
    return out, kept, fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--langs', default='es,fr,jp,pt,ru,tr,vn')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', nargs='*', default=None)
    args = ap.parse_args()
    langs = args.langs.split(',')
    files = args.only if args.only else sorted(f for l in langs for f in glob.glob('chapters/*.%s.qmd' % l))
    changed, chunks_changed, kept_total, fallback_total, skipped = 0, 0, 0, 0, []
    for tr in files:
        en = re.sub(r'\.[a-z]{2}\.qmd$', '.qmd', tr)
        if not os.path.exists(en):
            skipped.append((tr, 'no English chapter')); continue
        te = open(en, encoding='utf-8').read(); tt = open(tr, encoding='utf-8').read()
        try:
            se, st = split(te), split(tt)
        except ValueError as e:
            skipped.append((tr, str(e))); continue
        ce = [s for s in se if s[0] == 'chunk']; ct = [s for s in st if s[0] == 'chunk']
        if len(ce) != len(ct):
            skipped.append((tr, 'chunk count %d vs English %d' % (len(ct), len(ce)))); continue
        out, k, n_changed, kept, fallback = [], 0, 0, 0, 0
        for s in st:
            if s[0] == 'prose':
                out.extend(s[1]); continue
            e = ce[k]; k += 1
            body, kk, fb = merge(e[2], s[2])
            new = [e[1]] + body + [e[3]]
            old = [s[1]] + s[2] + [s[3]]
            if new != old: n_changed += 1; kept += kk; fallback += fb
            out.extend(new)
        new_text = '\n'.join(out)
        if new_text != tt:
            changed += 1; chunks_changed += n_changed; kept_total += kept; fallback_total += fallback
            print('%-40s chunks changed %3d, translated comments kept %3d, English comments used %3d' % (tr, n_changed, kept, fallback))
            if not args.dry_run:
                open(tr, 'w', encoding='utf-8', newline='').write(new_text)
    print('files %d, changed %d, chunks changed %d, translated comments kept %d, English comments used %d%s' % (
        len(files), changed, chunks_changed, kept_total, fallback_total, ' (dry run)' if args.dry_run else ''))
    for f, why in skipped: print('SKIPPED %s: %s' % (f, why))
    return 0


if __name__ == '__main__':
    sys.exit(main())
